"""
profile_perf.py - Empirical Performance Profiling Suite for Drone Navigation
-----------------------------------------------------------------------------
Measures:
  1. Per-control-step time breakdown (Physics, Camera Raycast/Render, Grayscale,
     Farneback Optical Flow, Sobel/Tau_inv, Obs Assembly, Step Remainder)
  2. IPC overhead and communication latency across SubprocVecEnv with SharedMemory
  3. Policy Model GPU forward and backward pass timings across batch sizes & precisions
  4. Worker scaling curves (1, 2, 4, 8, 12 workers) for both Rollout SPS and Training SPS
  5. Empirical identification of top bottlenecks

Adheres strictly to the .compute.lock coordination protocol.
Never touches held-out seeds (1000-1049).
"""

import os
import sys
import time
import json
import argparse
import numpy as np
import cv2
import torch
import multiprocessing as mp

from environment import IndoorDroneNavEnv
from model import PhysicsInformedActorCritic
from train import SubprocVecEnv, SingleEnv, RolloutBuffer, compute_gae


class ComputeLock:
    def __init__(self, lock_file=".compute.lock", worker_id="A4_PERF"):
        self.lock_file = lock_file
        self.worker_id = worker_id
        self.acquired = False

    def acquire(self, timeout=120, poll_interval=1.0):
        start = time.time()
        while time.time() - start < timeout:
            if not os.path.exists(self.lock_file):
                try:
                    with open(self.lock_file, "x") as f:
                        f.write(f"worker_id: {self.worker_id}\npid: {os.getpid()}\ntimestamp: {time.time()}\n")
                    self.acquired = True
                    print(f"[ComputeLock] Acquired {self.lock_file} for {self.worker_id} (PID {os.getpid()})")
                    return True
                except FileExistsError:
                    pass
            print(f"[ComputeLock] Waiting for {self.lock_file} to be released...")
            time.sleep(poll_interval)
        return False

    def release(self):
        if self.acquired and os.path.exists(self.lock_file):
            try:
                os.remove(self.lock_file)
                print(f"[ComputeLock] Released {self.lock_file}")
            except Exception as e:
                print(f"[ComputeLock] Warning: failed to remove {self.lock_file}: {e}")
            self.acquired = False

    def __enter__(self):
        if not self.acquire():
            raise RuntimeError(f"Could not acquire compute lock {self.lock_file} within timeout")
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.release()


# ─────────────────────────────────────────────────────────────────────────────
# 1. Micro-Benchmark: Per-Control-Step Component Breakdown
# ─────────────────────────────────────────────────────────────────────────────

def profile_per_step_breakdown(num_steps=500, warmup=50, seed=42):
    print(f"\n{'='*70}\n1. PROFILING PER-CONTROL-STEP BREAKDOWN ({num_steps} steps, seed={seed})\n{'='*70}")
    env = IndoorDroneNavEnv(gui=False, seed=seed, max_steps=1000)
    obs, _ = env.reset(seed=seed)

    # Warmup
    for _ in range(warmup):
        action = np.random.uniform(-1.0, 1.0, size=4).astype(np.float32)
        obs, _, term, trunc, _ = env.step(action)
        if term or trunc:
            obs, _ = env.reset()

    # Metrics storage (microseconds)
    t_physics = []
    t_camera_render = []
    t_gray_convert = []
    t_optical_flow = []
    t_divergence_tau = []
    t_obs_assembly = []
    t_step_remainder = []
    t_total_instrumented = []

    for step_i in range(num_steps):
        action = np.random.uniform(-1.0, 1.0, size=4).astype(np.float32)
        action_clipped = np.clip(action, -1.0, 1.0)
        target_vel = action_clipped[:3] * 3.0
        yaw_rate = action_clipped[3] * 1.0
        env.out_of_bounds = False

        t0 = time.perf_counter_ns()

        # Phase A: Physics stepping (8 substeps)
        t_phys_start = time.perf_counter_ns()
        for _ in range(env.physics_substeps):
            if env.pybullet_active:
                import pybullet as p
                p.resetBaseVelocity(
                    env.drone_id,
                    linearVelocity=target_vel.tolist(),
                    angularVelocity=[0.0, 0.0, float(yaw_rate)],
                    physicsClientId=env.client_id
                )
                p.stepSimulation(physicsClientId=env.client_id)
                raw_pos, raw_orn = p.getBasePositionAndOrientation(env.drone_id, physicsClientId=env.client_id)
                clamped, oob = env._clamp_to_arena(raw_pos)
                if oob:
                    env.out_of_bounds = True
                    p.resetBasePositionAndOrientation(env.drone_id, clamped, raw_orn, physicsClientId=env.client_id)
                    p.resetBaseVelocity(env.drone_id, [0, 0, 0], [0, 0, 0], physicsClientId=env.client_id)
            else:
                env.drone_vel = target_vel.copy()
                env.drone_orn[2] += yaw_rate * env.dt
                env.drone_pos += env.drone_vel * env.dt
                clamped, oob = env._clamp_to_arena(env.drone_pos)
                if oob:
                    env.out_of_bounds = True
                    env.drone_pos = np.array(clamped, dtype=np.float32)
                    env.drone_vel = np.zeros(3, dtype=np.float32)
        t_phys_end = time.perf_counter_ns()

        env.current_step += 1

        # Phase B: Camera Image Rendering
        t_cam_start = time.perf_counter_ns()
        rgb, depth = env._get_camera_images()
        t_cam_end = time.perf_counter_ns()

        # Phase C: Grayscale conversion
        t_gray_start = time.perf_counter_ns()
        gray = cv2.cvtColor(rgb, cv2.COLOR_RGB2GRAY)
        t_gray_end = time.perf_counter_ns()

        # Phase D: Optical flow computation
        t_flow_start = time.perf_counter_ns()
        if env.prev_gray_frame is None:
            flow = np.zeros((env.img_height, env.img_width, 2), dtype=np.float32)
        else:
            flow = cv2.calcOpticalFlowFarneback(
                env.prev_gray_frame,
                gray,
                None,
                pyr_scale=0.5,
                levels=2,
                winsize=9,
                iterations=2,
                poly_n=5,
                poly_sigma=1.1,
                flags=0
            )
        t_flow_end = time.perf_counter_ns()

        # Phase E: Divergence & Tau^-1 calculation
        t_tau_start = time.perf_counter_ns()
        if env.prev_gray_frame is None:
            tau_inv_bounded = 0.0
        else:
            u = flow[:, :, 0]
            v = flow[:, :, 1]
            du_dx = cv2.Sobel(u, cv2.CV_32F, 1, 0, ksize=3)
            dv_dy = cv2.Sobel(v, cv2.CV_32F, 0, 1, ksize=3)
            divergence_roi = du_dx[env.roi_y_slice, env.roi_x_slice] + dv_dy[env.roi_y_slice, env.roi_x_slice]
            mean_expansion = float(np.mean(divergence_roi))
            tau_inv_bounded = float(np.clip(np.maximum(0.0, mean_expansion), 0.0, env.tau_inv_max))
        env.prev_gray_frame = gray.copy()
        t_tau_end = time.perf_counter_ns()

        # Phase F: Observation assembly
        t_obs_start = time.perf_counter_ns()
        rgb_norm = rgb.astype(np.float32) / 255.0
        flow_u = flow[:, :, 0:1]
        flow_v = flow[:, :, 1:2]
        visual_obs = np.concatenate([rgb_norm, flow_u, flow_v], axis=-1)
        visual_obs = np.transpose(visual_obs, (2, 0, 1)).astype(np.float32)
        vel_vec = env.drone_vel.copy()
        env.current_tau_inv = tau_inv_bounded
        obs = {"visual": visual_obs, "velocity": vel_vec}
        t_obs_end = time.perf_counter_ns()

        # Phase G: Step Remainder (Collision, Rewards, Done checks)
        t_rem_start = time.perf_counter_ns()
        pos = env.drone_pos.copy()
        roll, pitch, yaw = env.drone_orn[0], env.drone_orn[1], env.drone_orn[2]
        collision = False
        for spec in env.obstacle_specs:
            ox, oy, _ = spec["pos"]
            dist = np.linalg.norm(pos[:2] - np.array([ox, oy]))
            obs_r = spec.get("radius", 0.4)
            if dist < (obs_r + 0.25):
                collision = True
                break
        if env.out_of_bounds:
            collision = True

        dist_to_goal = float(np.linalg.norm(pos - env.goal_pos))
        goal_reached = dist_to_goal < 0.8
        if not hasattr(env, "prev_dist_to_goal") or env.prev_dist_to_goal is None:
            env.prev_dist_to_goal = float(np.linalg.norm(env.start_pos - env.goal_pos))

        r_progress = 6.0 * (env.prev_dist_to_goal - dist_to_goal)
        env.prev_dist_to_goal = dist_to_goal
        goal_dir = (env.goal_pos - pos) / (dist_to_goal + 1e-6)

        min_depth = env.far_val
        if env.last_depth_map is not None:
            min_depth = float(np.percentile(env.last_depth_map, 5))

        clearance_factor = float(np.clip((min_depth - 0.8) / 1.0, 0.0, 1.0))
        r_goal = 2.5 * float(np.dot(obs["velocity"], goal_dir)) * clearance_factor
        r_ttc = -2.0 * env.current_tau_inv
        r_attitude = -0.5 * (abs(roll) + abs(pitch))
        r_proximity = 0.0
        if min_depth < 1.2:
            r_proximity = -5.0 * ((1.2 - min_depth) ** 2)

        terminal_reward = 0.0
        terminated = False
        truncated = False
        if collision:
            terminal_reward = -100.0
            terminated = True
        elif goal_reached:
            terminal_reward = 100.0
            terminated = True
        elif env.current_step >= env.max_steps:
            truncated = True

        reward = r_progress + r_goal + r_ttc + r_attitude + r_proximity + terminal_reward
        info = {
            "dist_to_goal": dist_to_goal,
            "tau_inv": env.current_tau_inv,
            "collision": collision,
            "goal_reached": goal_reached,
            "min_depth": min_depth,
        }
        t_rem_end = time.perf_counter_ns()
        t_total_end = time.perf_counter_ns()

        t_physics.append((t_phys_end - t_phys_start) / 1e3)
        t_camera_render.append((t_cam_end - t_cam_start) / 1e3)
        t_gray_convert.append((t_gray_end - t_gray_start) / 1e3)
        t_optical_flow.append((t_flow_end - t_flow_start) / 1e3)
        t_divergence_tau.append((t_tau_end - t_tau_start) / 1e3)
        t_obs_assembly.append((t_obs_end - t_obs_start) / 1e3)
        t_step_remainder.append((t_rem_end - t_rem_start) / 1e3)
        t_total_instrumented.append((t_total_end - t0) / 1e3)

        if terminated or truncated:
            obs, _ = env.reset()

    # Measure uninstrumented baseline env.step(action) for verification
    t_uninstrumented = []
    env.reset(seed=seed + 1)
    for _ in range(num_steps):
        action = np.random.uniform(-1.0, 1.0, size=4).astype(np.float32)
        t0 = time.perf_counter_ns()
        _, _, term, trunc, _ = env.step(action)
        t1 = time.perf_counter_ns()
        t_uninstrumented.append((t1 - t0) / 1e3)
        if term or trunc:
            env.reset()

    env.close()

    def stats(arr):
        return {
            "mean_us": float(np.mean(arr)),
            "std_us": float(np.std(arr)),
            "mean_ms": float(np.mean(arr) / 1000.0),
            "std_ms": float(np.std(arr) / 1000.0),
            "min_ms": float(np.min(arr) / 1000.0),
            "max_ms": float(np.max(arr) / 1000.0),
            "p50_ms": float(np.median(arr) / 1000.0),
            "p95_ms": float(np.percentile(arr, 95) / 1000.0),
        }

    total_mean = float(np.mean(t_total_instrumented))
    results = {
        "engine_mode": "Analytical Kinematics + Raycast" if not env.pybullet_active else "PyBullet Physics + TinyRenderer",
        "pybullet_active": env.pybullet_active,
        "physics_stepping": stats(t_physics),
        "camera_rendering": stats(t_camera_render),
        "gray_conversion": stats(t_gray_convert),
        "optical_flow_farneback": stats(t_optical_flow),
        "divergence_and_tau": stats(t_divergence_tau),
        "obs_assembly": stats(t_obs_assembly),
        "step_remainder": stats(t_step_remainder),
        "total_step_instrumented": stats(t_total_instrumented),
        "total_step_uninstrumented": stats(t_uninstrumented),
    }

    # Add percentage of control step
    for k in [
        "physics_stepping", "camera_rendering", "gray_conversion",
        "optical_flow_farneback", "divergence_and_tau", "obs_assembly", "step_remainder"
    ]:
        results[k]["pct_of_step"] = float((results[k]["mean_us"] / total_mean) * 100.0)

    print(f"Engine mode: {results['engine_mode']}")
    print(f"{'Component':<32} | {'Mean (ms)':<10} | {'Std (ms)':<10} | {'P95 (ms)':<10} | {'Share (%)':<10}")
    print("-" * 80)
    for k in [
        "camera_rendering", "optical_flow_farneback", "divergence_and_tau",
        "obs_assembly", "physics_stepping", "gray_conversion", "step_remainder"
    ]:
        v = results[k]
        print(f"{k:<32} | {v['mean_ms']:<10.4f} | {v['std_ms']:<10.4f} | {v['p95_ms']:<10.4f} | {v['pct_of_step']:<10.2f}%")
    print("-" * 80)
    print(f"{'Total Instrumented Step':<32} | {results['total_step_instrumented']['mean_ms']:<10.4f} | {results['total_step_instrumented']['std_ms']:<10.4f} | {results['total_step_instrumented']['p95_ms']:<10.4f} | 100.00%")
    print(f"{'Total Uninstrumented Baseline':<32} | {results['total_step_uninstrumented']['mean_ms']:<10.4f} | {results['total_step_uninstrumented']['std_ms']:<10.4f} | {results['total_step_uninstrumented']['p95_ms']:<10.4f} | N/A")
    print(f"Implied Single-Environment Step Rate: {1000.0 / results['total_step_uninstrumented']['mean_ms']:.1f} steps/sec")

    return results


# ─────────────────────────────────────────────────────────────────────────────
# 2. GPU Model Forward and Backward Pass Profiling
# ─────────────────────────────────────────────────────────────────────────────

def profile_gpu_passes(device="cuda", warmup=50, iters=200):
    print(f"\n{'='*70}\n2. PROFILING GPU POLICY MODEL FORWARD & BACKWARD PASSES\n{'='*70}")
    if not torch.cuda.is_available():
        raise RuntimeError("CUDA required for GPU profiling")

    gpu_name = torch.cuda.get_device_name(0)
    print(f"Device: {gpu_name}")

    model = PhysicsInformedActorCritic(action_dim=4).to(device)
    optimizer = torch.optim.Adam(model.parameters(), lr=5e-5, eps=1e-5)

    results = {}

    # Test forward pass across batch sizes (1, 8, 12, 1024) and precisions (fp32, bfloat16)
    batch_sizes = [1, 8, 12, 1024]
    precisions = ["float32", "bfloat16"]

    results["forward_pass"] = {}
    for prec in precisions:
        amp_dtype = torch.bfloat16 if prec == "bfloat16" else torch.float32
        results["forward_pass"][prec] = {}
        for bs in batch_sizes:
            vis = torch.randn(bs, 5, 84, 84, device=device, dtype=torch.float32)
            vel = torch.randn(bs, 3, device=device, dtype=torch.float32)

            # Warmup
            for _ in range(warmup):
                with torch.no_grad():
                    with torch.amp.autocast("cuda", dtype=amp_dtype, enabled=(prec != "float32")):
                        _ = model.get_action_and_value(vis, vel)
            torch.cuda.synchronize()

            # Measure with CUDA Events
            start_event = torch.cuda.Event(enable_timing=True)
            end_event = torch.cuda.Event(enable_timing=True)
            times_ms = []

            for _ in range(iters):
                start_event.record()
                with torch.no_grad():
                    with torch.amp.autocast("cuda", dtype=amp_dtype, enabled=(prec != "float32")):
                        _ = model.get_action_and_value(vis, vel)
                end_event.record()
                torch.cuda.synchronize()
                times_ms.append(start_event.elapsed_time(end_event))

            results["forward_pass"][prec][f"batch_{bs}"] = {
                "mean_ms": float(np.mean(times_ms)),
                "std_ms": float(np.std(times_ms)),
                "p50_ms": float(np.median(times_ms)),
                "p95_ms": float(np.percentile(times_ms, 95)),
                "per_sample_us": float(np.mean(times_ms) / bs * 1000.0),
                "throughput_samples_per_sec": float(bs / (np.mean(times_ms) / 1000.0))
            }
            print(f"Forward [{prec:8s}] Batch={bs:<4} | Latency: {np.mean(times_ms):.4f} ms | Throughput: {bs / (np.mean(times_ms) / 1000.0):.1f} samples/s")

    # Host-to-Device Transfer Latency
    results["h2d_transfer"] = {}
    print("\nHost-to-Device (CPU numpy -> CUDA tensor) Latency:")
    for bs in batch_sizes:
        vis_np = np.random.randn(bs, 5, 84, 84).astype(np.float32)
        vel_np = np.random.randn(bs, 3).astype(np.float32)

        # Warmup
        for _ in range(warmup):
            vt = torch.tensor(vis_np, dtype=torch.float32, device=device)
            kt = torch.tensor(vel_np, dtype=torch.float32, device=device)
        torch.cuda.synchronize()

        times_ms = []
        for _ in range(iters):
            t0 = time.perf_counter_ns()
            vt = torch.tensor(vis_np, dtype=torch.float32, device=device)
            kt = torch.tensor(vel_np, dtype=torch.float32, device=device)
            torch.cuda.synchronize()
            t1 = time.perf_counter_ns()
            times_ms.append((t1 - t0) / 1e6)

        results["h2d_transfer"][f"batch_{bs}"] = {
            "mean_ms": float(np.mean(times_ms)),
            "std_ms": float(np.std(times_ms)),
            "data_bytes": int(vis_np.nbytes + vel_np.nbytes),
            "bandwidth_gb_per_sec": float((vis_np.nbytes + vel_np.nbytes) / (np.mean(times_ms) / 1e3) / 1e9)
        }
        print(f"H2D Transfer Batch={bs:<4} ({vis_np.nbytes/1024:.1f} KB) | Latency: {np.mean(times_ms):.4f} ms | Effective Bandwidth: {results['h2d_transfer'][f'batch_{bs}']['bandwidth_gb_per_sec']:.2f} GB/s")

    # PPO Backward pass mini-batch (batch=1024)
    print("\nPPO Training Mini-Batch (Batch=1024, Forward + Loss + Backward + Adam Step):")
    results["ppo_backward_pass"] = {}
    for prec in ["float32", "bfloat16"]:
        amp_dtype = torch.bfloat16 if prec == "bfloat16" else torch.float32
        bs = 1024
        vis = torch.randn(bs, 5, 84, 84, device=device, dtype=torch.float32)
        vel = torch.randn(bs, 3, device=device, dtype=torch.float32)
        act = torch.randn(bs, 4, device=device, dtype=torch.float32)
        old_lp = torch.randn(bs, device=device, dtype=torch.float32)
        adv = torch.randn(bs, device=device, dtype=torch.float32)
        ret = torch.randn(bs, device=device, dtype=torch.float32)

        # Warmup
        for _ in range(20):
            optimizer.zero_grad(set_to_none=True)
            with torch.amp.autocast("cuda", dtype=amp_dtype, enabled=(prec != "float32")):
                _, new_lp, ent, new_val = model.get_action_and_value(vis, vel, act)
                ratio = torch.exp(new_lp - old_lp)
                surr1 = ratio * adv
                surr2 = torch.clamp(ratio, 0.8, 1.2) * adv
                pl = -torch.min(surr1, surr2).mean()
                vl = 0.5 * ((new_val - ret) ** 2).mean()
                loss = pl + 0.5 * vl - 0.01 * ent.mean()
            loss.backward()
            torch.nn.utils.clip_grad_norm_(model.parameters(), 0.5)
            optimizer.step()
        torch.cuda.synchronize()

        times_ms = []
        for _ in range(100):
            optimizer.zero_grad(set_to_none=True)
            t0 = time.perf_counter_ns()
            with torch.amp.autocast("cuda", dtype=amp_dtype, enabled=(prec != "float32")):
                _, new_lp, ent, new_val = model.get_action_and_value(vis, vel, act)
                ratio = torch.exp(new_lp - old_lp)
                surr1 = ratio * adv
                surr2 = torch.clamp(ratio, 0.8, 1.2) * adv
                pl = -torch.min(surr1, surr2).mean()
                vl = 0.5 * ((new_val - ret) ** 2).mean()
                loss = pl + 0.5 * vl - 0.01 * ent.mean()
            loss.backward()
            torch.nn.utils.clip_grad_norm_(model.parameters(), 0.5)
            optimizer.step()
            torch.cuda.synchronize()
            t1 = time.perf_counter_ns()
            times_ms.append((t1 - t0) / 1e6)

        results["ppo_backward_pass"][prec] = {
            "mean_ms": float(np.mean(times_ms)),
            "std_ms": float(np.std(times_ms)),
            "p50_ms": float(np.median(times_ms)),
            "p95_ms": float(np.percentile(times_ms, 95)),
            "samples_per_sec": float(bs / (np.mean(times_ms) / 1000.0))
        }
        print(f"PPO Mini-Batch Update [{prec:8s}] | Latency: {np.mean(times_ms):.3f} ms | Throughput: {results['ppo_backward_pass'][prec]['samples_per_sec']:.1f} transitions/s")

    return results


# ─────────────────────────────────────────────────────────────────────────────
# 3. Vector Environment & IPC Overhead Profiling
# ─────────────────────────────────────────────────────────────────────────────

def profile_ipc_overhead(num_steps=200):
    print(f"\n{'='*70}\n3. PROFILING IPC & VECTOR ENVIRONMENT OVERHEAD ({num_steps} steps)\n{'='*70}")
    results = {}

    # A: SingleEnv (Zero IPC)
    print("[*] Testing SingleEnv (Zero IPC baseline)...")
    single_env = SingleEnv(seed=42, max_steps=1000)
    single_env.reset()
    t_single = []
    for _ in range(num_steps):
        act = np.random.uniform(-1.0, 1.0, size=(1, 4)).astype(np.float32)
        t0 = time.perf_counter_ns()
        single_env.step(act)
        t1 = time.perf_counter_ns()
        t_single.append((t1 - t0) / 1e6)
    single_env.close()

    results["single_env"] = {
        "mean_ms": float(np.mean(t_single)),
        "std_ms": float(np.std(t_single)),
        "sps": float(1000.0 / np.mean(t_single))
    }
    print(f"SingleEnv Step Time: {results['single_env']['mean_ms']:.3f} ms | SPS: {results['single_env']['sps']:.1f}")

    # B: SubprocVecEnv with 1 worker (evaluating pure IPC overhead)
    print("[*] Testing SubprocVecEnv(1) to isolate IPC pipe + SharedMemory cost...")
    vec1 = SubprocVecEnv(n_envs=1, base_seed=42, max_steps=1000)
    vec1.reset()
    t_vec1 = []
    t_send1 = []
    t_recv1 = []

    for _ in range(num_steps):
        act = np.random.uniform(-1.0, 1.0, size=(1, 4)).astype(np.float32)
        t0 = time.perf_counter_ns()

        t_s0 = time.perf_counter_ns()
        vec1.parent_conns[0].send(("step", act[0]))
        t_s1 = time.perf_counter_ns()

        t_r0 = time.perf_counter_ns()
        vel, rew, term, trunc, step_info = vec1.parent_conns[0].recv()
        vec1.vel_stack[0] = vel
        obs_dict = {"visual": vec1.shared_vis, "velocity": vec1.vel_stack}
        t_r1 = time.perf_counter_ns()

        t1 = time.perf_counter_ns()
        t_vec1.append((t1 - t0) / 1e6)
        t_send1.append((t_s1 - t_s0) / 1e6)
        t_recv1.append((t_r1 - t_r0) / 1e6)

    vec1.close()

    ipc_overhead_ms = float(np.mean(t_vec1) - np.mean(t_single))
    results["subproc_vec1"] = {
        "total_step_ms": float(np.mean(t_vec1)),
        "send_action_ms": float(np.mean(t_send1)),
        "worker_exec_plus_recv_ms": float(np.mean(t_recv1)),
        "pure_ipc_overhead_ms": ipc_overhead_ms,
        "pure_ipc_overhead_pct": float((ipc_overhead_ms / np.mean(t_vec1)) * 100.0) if ipc_overhead_ms > 0 else 0.0,
        "sps": float(1000.0 / np.mean(t_vec1))
    }
    print(f"SubprocVecEnv(1) Step Time: {results['subproc_vec1']['total_step_ms']:.3f} ms (Send: {results['subproc_vec1']['send_action_ms']:.4f} ms, Worker+Recv: {results['subproc_vec1']['worker_exec_plus_recv_ms']:.3f} ms)")
    print(f"IPC Overhead vs Local: {ipc_overhead_ms:.3f} ms ({results['subproc_vec1']['pure_ipc_overhead_pct']:.1f}%)")

    return results


# ─────────────────────────────────────────────────────────────────────────────
# 4. Worker Scaling Benchmark: SPS across 1, 2, 4, 8, 12 Workers
# ─────────────────────────────────────────────────────────────────────────────

def profile_worker_scaling(worker_counts=[1, 2, 4, 8, 12], rollout_steps=512, device="cuda"):
    print(f"\n{'='*70}\n4. MEASURING SPS ACROSS WORKER COUNTS: {worker_counts} (steps_per_env={rollout_steps})\n{'='*70}")
    model = PhysicsInformedActorCritic(action_dim=4).to(device)
    model.eval()

    results = {}

    for n_envs in worker_counts:
        print(f"\n[*] Evaluating n_envs = {n_envs}...")
        if n_envs == 1:
            vec_env = SingleEnv(seed=42, max_steps=1000)
        else:
            vec_env = SubprocVecEnv(n_envs=n_envs, base_seed=42 + n_envs * 10, max_steps=1000)

        obs_dict = vec_env.reset()

        # Warmup 10 steps
        for _ in range(10):
            dummy_act = np.zeros((n_envs, 4), dtype=np.float32)
            obs_dict, _, _, _, _ = vec_env.step(dummy_act)

        # ── Benchmark A: Rollout Only (Env Step + Batched GPU Inference in BF16) ──
        total_steps = n_envs * rollout_steps
        step_times_ms = []
        gpu_infer_times_ms = []
        env_step_times_ms = []

        rollout_t0 = time.perf_counter()
        for step_i in range(rollout_steps):
            vis_np = obs_dict["visual"]
            vel_np = obs_dict["velocity"]

            t_gpu0 = time.perf_counter_ns()
            vis_t = torch.tensor(vis_np, dtype=torch.float32, device=device)
            vel_t = torch.tensor(vel_np, dtype=torch.float32, device=device)
            with torch.no_grad():
                with torch.amp.autocast("cuda", dtype=torch.bfloat16):
                    act_t, _, _, _ = model.get_action_and_value(vis_t, vel_t)
            act_np = act_t.float().cpu().numpy()
            t_gpu1 = time.perf_counter_ns()

            t_env0 = time.perf_counter_ns()
            obs_dict, _, _, _, _ = vec_env.step(act_np)
            t_env1 = time.perf_counter_ns()

            gpu_infer_times_ms.append((t_gpu1 - t_gpu0) / 1e6)
            env_step_times_ms.append((t_env1 - t_env0) / 1e6)
            step_times_ms.append((t_env1 - t_gpu0) / 1e6)

        rollout_t1 = time.perf_counter()
        rollout_wall_sec = rollout_t1 - rollout_t0
        rollout_sps = total_steps / rollout_wall_sec

        # ── Benchmark B: End-to-End PPO (Rollout + 10 Epochs Updates, batch 1024) ──
        # Mimic exact train.py update phase
        dataset_size = n_envs * rollout_steps
        batch_size = 1024
        update_epochs = 10
        optimizer = torch.optim.Adam(model.parameters(), lr=5e-5)

        # Prepare dummy rollout buffer tensors on GPU
        b_vis = torch.randn(dataset_size, 5, 84, 84, device=device, dtype=torch.float32)
        b_vel = torch.randn(dataset_size, 3, device=device, dtype=torch.float32)
        b_act = torch.randn(dataset_size, 4, device=device, dtype=torch.float32)
        b_lp = torch.randn(dataset_size, device=device, dtype=torch.float32)
        adv = torch.randn(dataset_size, device=device, dtype=torch.float32)
        ret = torch.randn(dataset_size, device=device, dtype=torch.float32)

        update_t0 = time.perf_counter()
        for _ in range(update_epochs):
            perm = torch.randperm(dataset_size, device=device)
            for start in range(0, dataset_size, batch_size):
                idx = perm[start : start + batch_size]
                optimizer.zero_grad(set_to_none=True)
                with torch.amp.autocast("cuda", dtype=torch.bfloat16):
                    _, new_lp, ent, new_val = model.get_action_and_value(b_vis[idx], b_vel[idx], b_act[idx])
                    ratio = torch.exp(new_lp - b_lp[idx])
                    surr1 = ratio * adv[idx]
                    surr2 = torch.clamp(ratio, 0.8, 1.2) * adv[idx]
                    pl = -torch.min(surr1, surr2).mean()
                    vl = 0.5 * ((new_val - ret[idx]) ** 2).mean()
                    loss = pl + 0.5 * vl - 0.01 * ent.mean()
                loss.backward()
                torch.nn.utils.clip_grad_norm_(model.parameters(), 0.5)
                optimizer.step()
        torch.cuda.synchronize()
        update_t1 = time.perf_counter()
        update_wall_sec = update_t1 - update_t0

        total_training_wall_sec = rollout_wall_sec + update_wall_sec
        training_sps = total_steps / total_training_wall_sec

        vec_env.close()

        results[f"workers_{n_envs}"] = {
            "n_envs": n_envs,
            "total_rollout_steps": total_steps,
            "rollout_wall_sec": float(rollout_wall_sec),
            "rollout_sps": float(rollout_sps),
            "update_wall_sec": float(update_wall_sec),
            "training_sps": float(training_sps),
            "mean_step_cycle_ms": float(np.mean(step_times_ms)),
            "mean_gpu_infer_ms": float(np.mean(gpu_infer_times_ms)),
            "mean_env_step_ms": float(np.mean(env_step_times_ms)),
        }

        print(f"n_envs={n_envs:<2} | Rollout SPS: {rollout_sps:<8.1f} | Training SPS: {training_sps:<8.1f} | Env Step: {np.mean(env_step_times_ms):.2f} ms | GPU Infer: {np.mean(gpu_infer_times_ms):.2f} ms | Update Time: {update_wall_sec:.2f} s")

    # Compute scaling efficiencies relative to 1 worker SingleEnv
    baseline_sps = results["workers_1"]["rollout_sps"]
    for n_envs in worker_counts:
        curr = results[f"workers_{n_envs}"]
        ideal_sps = baseline_sps * n_envs
        actual_sps = curr["rollout_sps"]
        curr["scaling_efficiency_pct"] = float((actual_sps / ideal_sps) * 100.0)
        curr["speedup_factor"] = float(actual_sps / baseline_sps)

    print("\n" + "="*70)
    print(f"{'Workers':<8} | {'Rollout SPS':<12} | {'Training SPS':<13} | {'Speedup':<10} | {'Efficiency':<12}")
    print("-" * 70)
    for n_envs in worker_counts:
        c = results[f"workers_{n_envs}"]
        print(f"{n_envs:<8} | {c['rollout_sps']:<12.1f} | {c['training_sps']:<13.1f} | {c['speedup_factor']:<10.2f}x | {c['scaling_efficiency_pct']:<12.1f}%")
    print("="*70)

    return results


# ─────────────────────────────────────────────────────────────────────────────
# 5. A/B Optimization Benchmark: Default vs Single-Threaded Worker
# ─────────────────────────────────────────────────────────────────────────────

def _optimized_worker(conn, seed, max_steps, shm_name=None, env_idx=None, shape=None):
    import cv2
    cv2.setNumThreads(1)
    from multiprocessing import shared_memory
    existing_shm = None
    shared_vis = None
    if shm_name is not None:
        try:
            existing_shm = shared_memory.SharedMemory(name=shm_name)
            shared_vis = np.ndarray(shape, dtype=np.float32, buffer=existing_shm.buf)
        except Exception:
            shared_vis = None

    env = IndoorDroneNavEnv(gui=False, seed=seed, max_steps=max_steps)
    obs, info = env.reset(seed=seed)
    if shared_vis is not None:
        shared_vis[env_idx] = obs["visual"]
        conn.send({"velocity": obs["velocity"], "info": info})
    else:
        conn.send((obs, info))

    while True:
        cmd, data = conn.recv()
        if cmd == "step":
            obs, reward, terminated, truncated, step_info = env.step(data)
            if terminated or truncated:
                obs, _ = env.reset()
            if shared_vis is not None:
                shared_vis[env_idx] = obs["visual"]
                conn.send((obs["velocity"], reward, terminated, truncated, step_info))
            else:
                conn.send((obs, reward, terminated, truncated, step_info))
        elif cmd == "reset":
            obs, info = env.reset()
            if shared_vis is not None:
                shared_vis[env_idx] = obs["visual"]
                conn.send({"velocity": obs["velocity"], "info": info})
            else:
                conn.send((obs, info))
        elif cmd == "close":
            env.close()
            if existing_shm is not None:
                existing_shm.close()
            conn.close()
            break


class OptimizedSubprocVecEnv(SubprocVecEnv):
    def __init__(self, n_envs: int, base_seed: int = 42, max_steps: int = 500):
        self.n_envs = n_envs
        self.shape = (n_envs, 5, 84, 84)
        from multiprocessing import shared_memory
        try:
            self.shm = shared_memory.SharedMemory(create=True, size=int(np.prod(self.shape) * 4))
            self.shared_vis = np.ndarray(self.shape, dtype=np.float32, buffer=self.shm.buf)
            self.use_shm = True
        except Exception:
            self.shm = None
            self.shared_vis = None
            self.use_shm = False

        self.parent_conns, self.worker_conns = zip(*[mp.Pipe() for _ in range(n_envs)])
        self.processes = []

        for i, (wconn,) in enumerate(zip(self.worker_conns)):
            p = mp.Process(
                target=_optimized_worker,
                args=(wconn, base_seed + i * 100, max_steps, self.shm.name if self.use_shm else None, i, self.shape),
                daemon=True
            )
            p.start()
            self.processes.append(p)

        self.vel_stack = np.zeros((n_envs, 3), dtype=np.float32)
        if self.use_shm:
            for i, conn in enumerate(self.parent_conns):
                init_data = conn.recv()
                self.vel_stack[i] = init_data["velocity"]
        else:
            self._last_obs = [conn.recv() for conn in self.parent_conns]


def profile_ab_opencv_threads(worker_counts=[8, 12], rollout_steps=256, device="cuda"):
    print(f"\n{'='*70}\n5. A/B TEST: DEFAULT (28 OpenCV THREADS/WORKER) VS cv2.setNumThreads(1)\n{'='*70}")
    model = PhysicsInformedActorCritic(action_dim=4).to(device)
    model.eval()

    ab_results = {}
    for n_envs in worker_counts:
        print(f"\n[*] Testing n_envs = {n_envs}...")
        total_steps = n_envs * rollout_steps

        # Baseline: default SubprocVecEnv
        vec_default = SubprocVecEnv(n_envs=n_envs, base_seed=42 + n_envs * 10, max_steps=1000)
        obs_dict = vec_default.reset()
        for _ in range(10):
            obs_dict, _, _, _, _ = vec_default.step(np.zeros((n_envs, 4), dtype=np.float32))

        t0 = time.perf_counter()
        for _ in range(rollout_steps):
            vis_t = torch.tensor(obs_dict["visual"], dtype=torch.float32, device=device)
            vel_t = torch.tensor(obs_dict["velocity"], dtype=torch.float32, device=device)
            with torch.no_grad():
                with torch.amp.autocast("cuda", dtype=torch.bfloat16):
                    act_t, _, _, _ = model.get_action_and_value(vis_t, vel_t)
            obs_dict, _, _, _, _ = vec_default.step(act_t.float().cpu().numpy())
        t1 = time.perf_counter()
        default_sps = total_steps / (t1 - t0)
        vec_default.close()

        # Optimized: OptimizedSubprocVecEnv
        vec_opt = OptimizedSubprocVecEnv(n_envs=n_envs, base_seed=42 + n_envs * 10, max_steps=1000)
        obs_dict = vec_opt.reset()
        for _ in range(10):
            obs_dict, _, _, _, _ = vec_opt.step(np.zeros((n_envs, 4), dtype=np.float32))

        t0 = time.perf_counter()
        for _ in range(rollout_steps):
            vis_t = torch.tensor(obs_dict["visual"], dtype=torch.float32, device=device)
            vel_t = torch.tensor(obs_dict["velocity"], dtype=torch.float32, device=device)
            with torch.no_grad():
                with torch.amp.autocast("cuda", dtype=torch.bfloat16):
                    act_t, _, _, _ = model.get_action_and_value(vis_t, vel_t)
            obs_dict, _, _, _, _ = vec_opt.step(act_t.float().cpu().numpy())
        t1 = time.perf_counter()
        opt_sps = total_steps / (t1 - t0)
        vec_opt.close()

        speedup_pct = ((opt_sps - default_sps) / default_sps) * 100.0
        ab_results[f"workers_{n_envs}"] = {
            "default_sps": float(default_sps),
            "opt_sps": float(opt_sps),
            "speedup_pct": float(speedup_pct)
        }
        print(f"n_envs={n_envs:<2} | Default SPS: {default_sps:8.1f} | Optimized (setNumThreads=1) SPS: {opt_sps:8.1f} | Delta: {speedup_pct:+.1f}%")

    return ab_results



# ─────────────────────────────────────────────────────────────────────────────
# Main Orchestration
# ─────────────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="Profile drone navigation training pipeline")
    parser.add_argument("--mode", type=str, default="all", choices=["micro", "gpu", "ipc", "scaling", "ab", "all"], help="Profiling mode")
    parser.add_argument("--num-steps", type=int, default=500, help="Steps for micro benchmark")
    parser.add_argument("--rollout-steps", type=int, default=512, help="Rollout steps per env for scaling")
    parser.add_argument("--device", type=str, default="cuda", help="Torch device")
    parser.add_argument("--out-json", type=str, default="perf_benchmark_results.json", help="Output JSON path")
    args = parser.parse_args()

    # Hardware metadata
    hw_info = {
        "os": sys.platform,
        "python_version": sys.version,
        "cpu_count_logical": mp.cpu_count(),
        "torch_version": torch.__version__,
        "cuda_available": torch.cuda.is_available(),
        "cuda_device_name": torch.cuda.get_device_name(0) if torch.cuda.is_available() else "None",
        "cuda_capability": torch.cuda.get_device_capability(0) if torch.cuda.is_available() else "None",
        "timestamp": time.time(),
        "date_iso": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
    }

    # Load existing results if file exists, so individual test modes don't discard prior benchmarks
    full_results = {}
    if os.path.exists(args.out_json):
        try:
            with open(args.out_json, "r") as f:
                full_results = json.load(f)
        except Exception as e:
            print(f"[!] Warning loading existing {args.out_json}: {e}")
            full_results = {}

    full_results["hardware_info"] = hw_info
    full_results["profiling_timestamp"] = hw_info["date_iso"]

    # Acquire compute lock for heavy operations
    with ComputeLock(worker_id="A4_PERF"):
        if args.mode in ["micro", "all"]:
            full_results["micro_breakdown"] = profile_per_step_breakdown(num_steps=args.num_steps, seed=42)

        if args.mode in ["gpu", "all"]:
            full_results["gpu_passes"] = profile_gpu_passes(device=args.device, iters=200)

        if args.mode in ["ipc", "all"]:
            full_results["ipc_overhead"] = profile_ipc_overhead(num_steps=200)

        if args.mode in ["scaling", "all"]:
            full_results["worker_scaling"] = profile_worker_scaling(
                worker_counts=[1, 2, 4, 8, 12],
                rollout_steps=args.rollout_steps,
                device=args.device
            )

        if args.mode in ["ab", "all"]:
            full_results["ab_cv2_threads"] = profile_ab_opencv_threads(
                worker_counts=[8, 12],
                rollout_steps=256,
                device=args.device
            )

    # Save to JSON
    with open(args.out_json, "w") as f:
        json.dump(full_results, f, indent=2)
    print(f"\n[+] Full profiling results successfully saved to {args.out_json}")


if __name__ == "__main__":
    mp.set_start_method("spawn", force=True)
    main()
