"""
train.py - Proximal Policy Optimization (PPO) Training Pipeline
----------------------------------------------------------------
Maximized GPU Utilization via:
  - N Parallel Subprocess Environments (SubprocVecEnv) for batched GPU inference
  - AMP Mixed Precision (FP16) training via torch.cuda.amp
  - torch.compile() with reduce-overhead mode for kernel fusion
  - cudnn.benchmark + pinned CUDA memory for faster CPU->GPU transfers
  - Large rollout buffers and batch sizes to saturate GPU
  - Live 3-Panel XAI Dashboard auto-updates every second during training
"""

import os
os.environ["CUDA_VISIBLE_DEVICES"] = "0"
os.environ["PYBULLET_EGL"] = "1"

import argparse
import time
import multiprocessing as mp
import numpy as np
import cv2
import json
import shutil

from environment import IndoorDroneNavEnv
from model import PhysicsInformedActorCritic
from explainability import DroneXAIEngine
from evaluate_and_visualize import draw_optical_flow_vectors, create_unified_dashboard_canvas

TORCH_AVAILABLE = True
try:
    import torch
    import torch.optim as optim
    from torch.distributions.normal import Normal
    from torch.utils.tensorboard import SummaryWriter
except (ImportError, OSError):
    TORCH_AVAILABLE = False


# ─────────────────────────────────────────────────────────────────────────────
# Device Setup
# ─────────────────────────────────────────────────────────────────────────────

def get_device():
    """Returns CUDA device strictly. Raises a clear error if CUDA is unavailable."""
    if not TORCH_AVAILABLE:
        raise RuntimeError(
            "[ERROR] PyTorch is not installed. Run: "
            "pip install --pre torch --index-url https://download.pytorch.org/whl/nightly/cu128"
        )
    if not torch.cuda.is_available():
        raise RuntimeError(
            "[ERROR] No CUDA GPU detected. Training requires an NVIDIA GPU.\n"
            "        RTX 5060 (sm_120) users: install PyTorch Nightly cu128."
        )
    torch.backends.cudnn.benchmark = True         # Auto-tune kernels for fixed input sizes
    torch.backends.cuda.matmul.allow_tf32 = True  # Use TF32 for faster matmul on Ampere/Blackwell
    torch.backends.cudnn.allow_tf32 = True        # Use TF32 for cuDNN convolutions
    gpu_name = torch.cuda.get_device_name(0)
    capability = torch.cuda.get_device_capability(0)
    total_mem_gb = torch.cuda.get_device_properties(0).total_memory / 1e9
    print(f"[+] GPU: {gpu_name}  |  sm_{capability[0]}{capability[1]}  |  VRAM: {total_mem_gb:.1f} GB")
    return "cuda"


# ─────────────────────────────────────────────────────────────────────────────
# Subprocess Vectorized Environment (SubprocVecEnv)
# ─────────────────────────────────────────────────────────────────────────────

from multiprocessing import shared_memory

def _env_worker(conn, seed, max_steps, shm_name=None, env_idx=None, shape=None):
    """Worker process: owns one IndoorDroneNavEnv and responds to commands."""
    shared_vis = None
    existing_shm = None
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
        elif cmd == "get_overhead":
            frame = env.render_overhead_simulation_view((390, 390))
            conn.send(frame)
        elif cmd == "get_depth":
            conn.send(env.last_depth_map)
        elif cmd == "close":
            env.close()
            if existing_shm is not None:
                existing_shm.close()
            conn.close()
            break


class SubprocVecEnv:
    """
    Runs N environments in parallel worker processes with zero-copy SharedMemory visual obs.
    Each step sends actions to all workers simultaneously,
    then collects results — enabling fully batched GPU inference.
    """

    def __init__(self, n_envs: int, base_seed: int = 42, max_steps: int = 500):
        self.n_envs = n_envs
        self.shape = (n_envs, 5, 84, 84)
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
                target=_env_worker,
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

    def reset(self):
        for conn in self.parent_conns:
            conn.send(("reset", None))
        if self.use_shm:
            for i, conn in enumerate(self.parent_conns):
                res = conn.recv()
                self.vel_stack[i] = res["velocity"]
            return {"visual": self.shared_vis, "velocity": self.vel_stack}
        else:
            results = [conn.recv() for conn in self.parent_conns]
            self._last_obs = [r[0] for r in results]
            return self._stack_obs(self._last_obs)

    def step(self, actions):
        """Send actions to all workers simultaneously, collect results."""
        for conn, action in zip(self.parent_conns, actions):
            conn.send(("step", action))

        if self.use_shm:
            rewards = np.zeros(self.n_envs, dtype=np.float32)
            terminateds = np.zeros(self.n_envs, dtype=bool)
            truncateds = np.zeros(self.n_envs, dtype=bool)
            infos = []
            for i, conn in enumerate(self.parent_conns):
                vel, rew, term, trunc, step_info = conn.recv()
                self.vel_stack[i] = vel
                rewards[i] = rew
                terminateds[i] = term
                truncateds[i] = trunc
                infos.append(step_info)
            obs_dict = {"visual": self.shared_vis, "velocity": self.vel_stack}
            return obs_dict, rewards, terminateds, truncateds, infos
        else:
            results = [conn.recv() for conn in self.parent_conns]
            obs_list, rewards, terminateds, truncateds, infos = zip(*results)
            self._last_obs = list(obs_list)
            return (
                self._stack_obs(obs_list),
                np.array(rewards, dtype=np.float32),
                np.array(terminateds, dtype=bool),
                np.array(truncateds, dtype=bool),
                infos
            )

    def get_overhead_view(self, env_idx=0):
        self.parent_conns[env_idx].send(("get_overhead", None))
        return self.parent_conns[env_idx].recv()

    def get_depth(self, env_idx=0):
        self.parent_conns[env_idx].send(("get_depth", None))
        return self.parent_conns[env_idx].recv()

    def _stack_obs(self, obs_list):
        vis = np.stack([o["visual"] for o in obs_list], axis=0)   # (N, 5, 84, 84)
        vel = np.stack([o["velocity"] for o in obs_list], axis=0) # (N, 3)
        return {"visual": vis, "velocity": vel}

    def close(self):
        for conn in self.parent_conns:
            try:
                conn.send(("close", None))
            except Exception:
                pass
        for p in self.processes:
            p.join(timeout=3)
        if self.use_shm and self.shm is not None:
            try:
                self.shm.close()
                self.shm.unlink()
            except Exception:
                pass


# ─────────────────────────────────────────────────────────────────────────────
# Rollout Buffer (GPU-pinned memory for fast CPU→GPU transfer)
# ─────────────────────────────────────────────────────────────────────────────

class RolloutBuffer:
    def __init__(self, n_steps: int, n_envs: int, device: str):
        self.n_steps = n_steps
        self.n_envs = n_envs
        self.device = device
        self.reset()

    def reset(self):
        self.visual_obs  = []
        self.velocity_obs = []
        self.actions     = []
        self.log_probs   = []
        self.rewards     = []
        self.dones       = []
        self.values      = []

    def add(self, vis, vel, act, log_prob, reward, done, value):
        self.visual_obs.append(np.array(vis, copy=True))
        self.velocity_obs.append(np.array(vel, copy=True))
        self.actions.append(act)
        self.log_probs.append(log_prob)
        self.rewards.append(reward)
        self.dones.append(done)
        self.values.append(value)

    def get_tensors(self):
        # Stack: (n_steps, n_envs, ...) → (n_steps*n_envs, ...)
        def to_gpu(arr):
            return torch.tensor(
                np.concatenate(arr, axis=0),
                dtype=torch.float32,
                device=self.device
            )

        vis   = to_gpu(self.visual_obs)    # (T*N, 5, 84, 84)
        vel   = to_gpu(self.velocity_obs)  # (T*N, 3)
        act   = to_gpu(self.actions)       # (T*N, 4)
        lp    = to_gpu(self.log_probs)     # (T*N,)
        rew   = to_gpu(self.rewards)       # (T*N,)
        done  = to_gpu(self.dones)         # (T*N,)
        val   = to_gpu(self.values)        # (T*N,)
        return vis, vel, act, lp, rew, done, val


class SingleEnv:
    """
    Direct single-environment wrapper with zero IPC pipe overhead.
    Runs at maximum speed in the main Python process.
    Episodes finish in ~0.5s!
    """
    def __init__(self, seed: int = 42, max_steps: int = 500):
        self.n_envs = 1
        self.env = IndoorDroneNavEnv(gui=False, seed=seed, max_steps=max_steps)

    def reset(self):
        obs, _ = self.env.reset()
        vis = np.expand_dims(obs["visual"], 0)   # (1, 5, 84, 84)
        vel = np.expand_dims(obs["velocity"], 0) # (1, 3)
        return {"visual": vis, "velocity": vel}

    def step(self, actions):
        action = actions[0]
        obs, reward, terminated, truncated, info = self.env.step(action)
        if terminated or truncated:
            obs, _ = self.env.reset()
        vis = np.expand_dims(obs["visual"], 0)
        vel = np.expand_dims(obs["velocity"], 0)
        return (
            {"visual": vis, "velocity": vel},
            np.array([reward], dtype=np.float32),
            np.array([terminated], dtype=bool),
            np.array([truncated], dtype=bool),
            [info]
        )

    def get_overhead_view(self, env_idx=0):
        return self.env.render_overhead_simulation_view((390, 390))

    def get_depth(self, env_idx=0):
        return self.env.last_depth_map

    def close(self):
        self.env.close()


# ─────────────────────────────────────────────────────────────────────────────
# GAE Computation (GPU tensors)
# ─────────────────────────────────────────────────────────────────────────────

def compute_gae(rewards, values, dones, next_values, gamma=0.99, lam=0.95):
    """Compute GAE advantages on GPU tensors. rewards: (T, N), values: (T, N)."""
    T, N = rewards.shape
    advantages = torch.zeros_like(rewards)
    last_gae = torch.zeros(N, device=rewards.device)

    for t in reversed(range(T)):
        nxt = next_values if t == T - 1 else values[t + 1]
        mask = 1.0 - dones[t]
        delta = rewards[t] + gamma * nxt * mask - values[t]
        last_gae = delta + gamma * lam * mask * last_gae
        advantages[t] = last_gae

    returns = advantages + values
    return advantages.reshape(-1), returns.reshape(-1)


# ─────────────────────────────────────────────────────────────────────────────
# Behavioral Evaluation Helper
# ─────────────────────────────────────────────────────────────────────────────

def evaluate_model_internal(model, device, seeds_dict=None):
    """
    Evaluates policy across training and unseen layout seeds.
    Uses deterministic policy mode (action_mean).
    Matches evaluate_and_visualize.py protocol.
    """
    if seeds_dict is None:
        seeds_dict = {
            "training": [42, 142, 242, 342, 442],
            "unseen": [101, 202, 303, 404, 505]
        }

    was_training = model.training
    model.eval()
    eval_results = {}

    for set_name, seeds in seeds_dict.items():
        res_list = []
        all_steer = []
        all_throt = []

        for s in seeds:
            env = IndoorDroneNavEnv(gui=False, seed=s, max_steps=500)
            obs, _ = env.reset(seed=s)
            ep_rew = 0.0
            steps = 0
            min_clr = float("inf")

            while True:
                vt = torch.tensor(obs["visual"], dtype=torch.float32, device=device).unsqueeze(0)
                kt = torch.tensor(obs["velocity"], dtype=torch.float32, device=device).unsqueeze(0)
                with torch.no_grad():
                    act = model(vt, kt).squeeze(0).cpu().numpy()

                all_steer.append(float(act[0]))
                all_throt.append(float(act[1]))

                obs, rew, term, trunc, sinfo = env.step(act)
                ep_rew += rew
                steps += 1
                if "min_depth" in sinfo:
                    min_clr = min(min_clr, float(sinfo["min_depth"]))

                if term or trunc:
                    is_succ = bool(sinfo.get("goal_reached", False))
                    is_coll = bool(sinfo.get("collision", False))
                    res_list.append({
                        "seed": s,
                        "status": "SUCCESS" if is_succ else ("COLLISION" if is_coll else "TIMEOUT"),
                        "success": 1.0 if is_succ else 0.0,
                        "collision": 1.0 if is_coll else 0.0,
                        "steps": steps,
                        "reward": float(ep_rew),
                        "goal_dist": float(sinfo.get("dist_to_goal", 0.0)),
                        "min_clearance": float(min_clr) if min_clr != float("inf") else 0.0
                    })
                    env.close()
                    break

        eval_results[set_name] = {
            "success_rate": float(np.mean([r["success"] for r in res_list]) * 100),
            "collision_rate": float(np.mean([r["collision"] for r in res_list]) * 100),
            "mean_episode_length": float(np.mean([r["steps"] for r in res_list])),
            "final_goal_distance": float(np.mean([r["goal_dist"] for r in res_list])),
            "mean_reward": float(np.mean([r["reward"] for r in res_list])),
            "std_reward": float(np.std([r["reward"] for r in res_list])),
            "mean_min_clearance": float(np.mean([r["min_clearance"] for r in res_list])),
            "steering_mean": float(np.mean(all_steer)),
            "steering_std": float(np.std(all_steer)),
            "steering_abs_mean": float(np.mean(np.abs(all_steer))),
            "throttle_mean": float(np.mean(all_throt)),
            "throttle_std": float(np.std(all_throt)),
            "per_seed": res_list
        }

    if was_training:
        model.train()
    return eval_results


# ─────────────────────────────────────────────────────────────────────────────
# Main Training Loop
# ─────────────────────────────────────────────────────────────────────────────

def train_ppo(args):
    np.random.seed(args.seed)
    device = get_device()

    torch.manual_seed(args.seed)
    writer = SummaryWriter(log_dir=os.path.join("runs", f"ppo_drone_{int(time.time())}"))

    if args.n_envs == 1:
        print("[*] Single-Environment Mode Active (Zero IPC Overhead, Ultra-Fast ~0.5s Episodes)...")
        vec_env = SingleEnv(seed=args.seed, max_steps=args.max_steps)
    else:
        print(f"[*] Launching {args.n_envs} parallel environment workers...")
        vec_env = SubprocVecEnv(n_envs=args.n_envs, base_seed=args.seed, max_steps=args.max_steps)

    # Ensure save directory exists
    os.makedirs(args.save_dir, exist_ok=True)

    # Build model & load pre-trained baseline weights if available
    model = PhysicsInformedActorCritic().to(device)
    backup_path = args.checkpoint + ".bak"
    best_reward = -float("inf")

    if os.path.exists(args.checkpoint):
        try:
            print(f"[+] Loading baseline checkpoint: {args.checkpoint}")
            model.load_state_dict(torch.load(args.checkpoint, map_location=device, weights_only=True))
            print(f"[+] Baseline weights loaded successfully! Expert intuition active from Step 0.")
            if not os.path.exists(backup_path):
                shutil.copyfile(args.checkpoint, backup_path)
                print(f"[+] Safety backup created: {backup_path}")
            meta_path = args.checkpoint + ".meta.json"
            if os.path.exists(meta_path):
                try:
                    with open(meta_path, "r") as f:
                        meta = json.load(f)
                        best_reward = float(meta.get("best_reward", meta.get("reward", 0.0)))
                    print(f"[+] Checkpoint metadata loaded: previous best reward = {best_reward:.2f}")
                except Exception:
                    best_reward = 0.0
            else:
                best_reward = 0.0
        except Exception as e:
            print(f"[!] Warning: Could not load {args.checkpoint}: {e}")
    else:
        print(f"[!] Warning: Baseline checkpoint {args.checkpoint} not found. Starting from scratch.")

    # Configure fine-tuning exploration mode
    if args.log_std_mode == "reduced":
        with torch.no_grad():
            model.actor_log_std.fill_(args.reduced_log_std)
        print(f"[+] Exploration log_std mode: 'reduced' -> {args.reduced_log_std:.2f} (std={np.exp(args.reduced_log_std):.3f})")
    elif args.log_std_mode == "custom":
        with torch.no_grad():
            model.actor_log_std.fill_(args.custom_log_std)
        print(f"[+] Exploration log_std mode: 'custom' -> {args.custom_log_std:.2f} (std={np.exp(args.custom_log_std):.3f})")
    elif args.log_std_mode == "checkpoint":
        loaded_log_std = model.actor_log_std.detach().cpu().numpy()
        print(f"[+] Exploration log_std mode: 'checkpoint' -> preserved: {loaded_log_std} (std={np.exp(loaded_log_std)})")

    if args.freeze_log_std:
        model.actor_log_std.requires_grad = False
        print(f"[+] actor_log_std parameter FROZEN during fine-tuning (requires_grad=False).")

    # Step 0: Save initial BC checkpoint into save_dir (Phase 5)
    initial_ckpt_path = os.path.join(args.save_dir, "initial_bc_checkpoint.pt")
    torch.save(model.state_dict(), initial_ckpt_path)
    initial_meta = {
        "source_checkpoint": args.checkpoint,
        "global_step": 0,
        "learning_rate": args.learning_rate,
        "log_std": model.actor_log_std.detach().cpu().tolist(),
        "best_reward": best_reward,
        "timestamp": time.time(),
        "config": vars(args)
    }
    with open(initial_ckpt_path + ".meta.json", "w") as f:
        json.dump(initial_meta, f, indent=2)
    print(f"[+] Safety snapshot created at Step 0: {initial_ckpt_path}")

    # Initialize frozen BC reference model for behavioral anchor if requested (Phase 10)
    ref_model = None
    if args.bc_anchor_coef > 0:
        ref_model = PhysicsInformedActorCritic().to(device)
        ref_model.load_state_dict(model.state_dict())
        ref_model.eval()
        for p in ref_model.parameters():
            p.requires_grad = False
        print(f"[+] Frozen BC reference anchor active: bc_anchor_coef = {args.bc_anchor_coef}")

    # Step 0: Run initial baseline evaluation if requested
    if args.eval_interval > 0:
        print(f"[*] Running Step 0 Behavioral Baseline Evaluation...")
        step0_eval = evaluate_model_internal(model, device)
        for s_name, m_dict in step0_eval.items():
            print(f"    [{s_name.upper()}] Success: {m_dict['success_rate']:.1f}% | Coll: {m_dict['collision_rate']:.1f}% | "
                  f"Len: {m_dict['mean_episode_length']:.1f} | GoalDist: {m_dict['final_goal_distance']:.2f}m | "
                  f"Rew: {m_dict['mean_reward']:.2f} | Clear: {m_dict['mean_min_clearance']:.2f}m | "
                  f"Steer: {m_dict['steering_mean']:.3f} | Throt: {m_dict['throttle_mean']:.3f}")
            writer.add_scalar(f"Eval/{s_name}_SuccessRate", m_dict["success_rate"], 0)
            writer.add_scalar(f"Eval/{s_name}_CollisionRate", m_dict["collision_rate"], 0)
            writer.add_scalar(f"Eval/{s_name}_MeanReward", m_dict["mean_reward"], 0)
            writer.add_scalar(f"Eval/{s_name}_GoalDist", m_dict["final_goal_distance"], 0)
        initial_meta["eval_metrics"] = step0_eval
        with open(initial_ckpt_path + ".meta.json", "w") as f:
            json.dump(initial_meta, f, indent=2)

    # torch.compile for kernel fusion (opt-in via --compile)
    if args.compile and hasattr(torch, "compile"):
        print("[+] Compiling model with torch.compile (reduce-overhead mode)...")
        try:
            model = torch.compile(model, mode="reduce-overhead")
        except Exception as e:
            print(f"[!] Warning: torch.compile failed: {e}. Falling back to eager mode.")

    optimizer = optim.Adam(model.parameters(), lr=args.learning_rate, eps=1e-5)

    amp_dtype = torch.float32
    scaler = None
    if args.amp_dtype == "bfloat16":
        amp_dtype = torch.bfloat16
        print("[+] Native BF16 Mixed Precision Active (No GradScaler needed on RTX 5060)")
    elif args.amp_dtype == "float16":
        amp_dtype = torch.float16
        scaler = torch.amp.GradScaler("cuda")
        print("[+] FP16 Mixed Precision Active with GradScaler")

    # XAI engine (for dashboard saliency — runs on a small subset of frames)
    # Wrap the underlying compiled module for Captum compatibility
    raw_model_for_xai = PhysicsInformedActorCritic().to(device)
    if os.path.exists(args.checkpoint):
        try:
            raw_model_for_xai.load_state_dict(torch.load(args.checkpoint, map_location=device, weights_only=True))
        except Exception:
            pass
    xai_engine = DroneXAIEngine(model=raw_model_for_xai, device=device)

    buffer = RolloutBuffer(n_steps=args.n_steps, n_envs=args.n_envs, device=device)

    # Dashboard Window
    train_win = "Real-Time Autonomous Drone Training Dashboard"
    show_dashboard = args.dashboard or args.gui
    if show_dashboard:
        try:
            cv2.namedWindow(train_win, cv2.WINDOW_NORMAL)
            cv2.resizeWindow(train_win, 1280, 620)   # taller to fit stats bar
            print("[+] Live Training Dashboard Launched (refreshes every ~1s)")
        except Exception as e:
            print(f"[!] Warning: OpenCV GUI window unavailable ({e}). Continuing in terminal mode.")
            show_dashboard = False

    obs_dict = vec_env.reset()
    global_step       = 0
    ep_reward         = np.zeros(args.n_envs, dtype=np.float32)
    episode_count     = 0
    dashboard_last_update = time.time()
    dashboard_saliency   = np.zeros((84, 84), dtype=np.float32)
    dashboard_overhead   = np.zeros((390, 390, 3), dtype=np.uint8)
    dashboard_flow_view  = np.zeros((84, 84, 3), dtype=np.uint8)
    dashboard_fps        = 0.0
    dashboard_latency    = 0.0
    dashboard_fidelity   = 0.0
    dashboard_goal_dist  = 0.0
    last_policy_loss     = 0.0
    last_value_loss      = 0.0
    last_entropy         = 0.0
    last_sps             = 0.0
    next_snapshot_step   = args.snapshot_interval

    print(f"[*] Starting GPU-Maximized PPO Training | n_envs={args.n_envs} | "
          f"n_steps={args.n_steps} | batch={args.batch_size} | "
          f"total_steps={args.total_timesteps:,}")
    print("[*] Watch GPU-Z / Task Manager -> GPU should now hit 60-95% utilization!")

    while global_step < args.total_timesteps:
        buffer.reset()
        rollout_start = time.perf_counter()

        # ── Rollout Phase ────────────────────────────────────────────────────
        for step_idx in range(args.n_steps):
            vis_np  = obs_dict["visual"]    # (N, 5, 84, 84)
            vel_np  = obs_dict["velocity"]  # (N, 3)

            vis_t = torch.tensor(vis_np, dtype=torch.float32, device=device, requires_grad=False)
            vel_t = torch.tensor(vel_np, dtype=torch.float32, device=device, requires_grad=False)

            with torch.no_grad():
                with torch.amp.autocast("cuda", dtype=amp_dtype):
                    actions_t, log_probs_t, _, values_t = model.get_action_and_value(vis_t, vel_t)

            actions_np   = actions_t.float().cpu().numpy()              # (N, 4)
            log_probs_np = log_probs_t.float().cpu().numpy()            # (N,)
            values_np    = values_t.float().cpu().numpy()               # (N,)

            next_obs_dict, rewards_np, terminateds, truncateds, infos = vec_env.step(actions_np)
            dones_np = (terminateds | truncateds).astype(np.float32)
            ep_reward += rewards_np
            global_step += args.n_envs

            buffer.add(
                vis_np, vel_np,
                actions_np, log_probs_np,
                rewards_np, dones_np, values_np
            )

            # Track per-episode stats
            for i in range(args.n_envs):
                if terminateds[i] or truncateds[i]:
                    episode_count += 1
                    # Save checkpoint only when it genuinely beats the previous best reward
                    if ep_reward[i] > best_reward:
                        best_reward = float(ep_reward[i])
                        best_ckpt_path = os.path.join(args.save_dir, "best_reward_model.pt")
                        tmp_ckpt = best_ckpt_path + ".tmp"
                        raw_m = (model._orig_mod if hasattr(model, "_orig_mod") else model)
                        torch.save(raw_m.state_dict(), tmp_ckpt)
                        os.replace(tmp_ckpt, best_ckpt_path)
                        best_eval_metrics = None
                        if args.eval_interval > 0:
                            print(f"\n[*] Evaluating New Best Reward Policy at Step {global_step:,}...")
                            best_eval_metrics = evaluate_model_internal(raw_m, device)
                            for s_name, m_dict in best_eval_metrics.items():
                                print(f"    [{s_name.upper()}] Success: {m_dict['success_rate']:.1f}% | Coll: {m_dict['collision_rate']:.1f}% | "
                                      f"Rew: {m_dict['mean_reward']:.2f} | GoalDist: {m_dict['final_goal_distance']:.2f}m")

                        meta = {
                            "source_checkpoint": args.checkpoint,
                            "best_reward": best_reward,
                            "reward": best_reward,
                            "global_step": global_step,
                            "episode": episode_count,
                            "env_idx": i,
                            "learning_rate": args.learning_rate,
                            "log_std": raw_m.actor_log_std.detach().cpu().tolist(),
                            "eval_metrics": best_eval_metrics,
                            "timestamp": time.time(),
                            "config": vars(args)
                        }
                        with open(best_ckpt_path + ".meta.json", "w") as f:
                            json.dump(meta, f, indent=2)
                        print(f"[+] New Best at Step {global_step:,} | "
                              f"Env {i} Reward: {best_reward:.2f} (saved to {best_ckpt_path})\n")

                    writer.add_scalar("Episode/Reward", ep_reward[i], global_step)

                    rc = infos[i].get("reward_components", {})
                    if rc:
                        writer.add_scalar("Episode/Progress",  rc.get("ep_progress", 0.0),  global_step)
                        writer.add_scalar("Episode/GoalVel",   rc.get("ep_goal_vel", 0.0),   global_step)
                        writer.add_scalar("Episode/TTC",       rc.get("ep_ttc", 0.0),        global_step)
                        writer.add_scalar("Episode/Proximity", rc.get("ep_proximity", 0.0),  global_step)
                        writer.add_scalar("Episode/Terminal",  rc.get("ep_terminal", 0.0),   global_step)

                    ep_reward[i] = 0.0
                    dashboard_goal_dist = infos[i].get("dist_to_goal", 0.0)

            obs_dict = next_obs_dict

            # ── Dashboard Update (every 1 second, non-blocking) ───────────
            if show_dashboard and (time.time() - dashboard_last_update) >= 1.0:
                t0 = time.perf_counter()

                # Grab env 0's overhead view + flow visualization
                try:
                    dashboard_overhead = vec_env.get_overhead_view(0)
                    # Use env 0's last observation for dashboard rendering
                    rgb_raw  = (vis_np[0, :3].transpose(1, 2, 0) * 255).astype(np.uint8)
                    flow_raw = vis_np[0, 3:5].transpose(1, 2, 0)
                    dashboard_flow_view = draw_optical_flow_vectors(rgb_raw, flow_raw)

                    # Saliency (lightweight single-frame)
                    dashboard_saliency = xai_engine.compute_attribution(
                        visual_obs=vis_np[0],
                        velocity_obs=vel_np[0],
                        target_action_idx=0,
                        mode="saliency"
                    )
                    depth = vec_env.get_depth(0)
                    if depth is not None:
                        dashboard_fidelity = DroneXAIEngine.compute_explanation_fidelity(
                            dashboard_saliency, depth
                        )
                    saliency_overlay = DroneXAIEngine.generate_heatmap_overlay(
                        rgb_raw, dashboard_saliency, alpha=0.65
                    )
                except Exception:
                    saliency_overlay = np.zeros((84, 84, 3), dtype=np.uint8)

                t1 = time.perf_counter()
                dashboard_latency = (t1 - t0) * 1000.0
                dashboard_fps = args.n_envs * args.n_steps / max(time.time() - rollout_start, 1e-6)

                canvas = create_unified_dashboard_canvas(
                    sim_view=dashboard_overhead,
                    flow_view=dashboard_flow_view,
                    saliency_view=saliency_overlay,
                    fps=dashboard_fps,
                    latency_ms=dashboard_latency,
                    fidelity_iou=dashboard_fidelity,
                    goal_dist=dashboard_goal_dist,
                    step_num=global_step,
                    train_stats={
                        "global_step":    global_step,
                        "total_timesteps": args.total_timesteps,
                        "sps":            last_sps,
                        "best_reward":    best_reward,
                        "episode_count":  episode_count,
                        "policy_loss":    last_policy_loss,
                        "value_loss":     last_value_loss,
                        "entropy":        last_entropy,
                    }
                )
                try:
                    cv2.imshow(train_win, canvas)
                    cv2.waitKey(1)
                except Exception as e:
                    show_dashboard = False
                dashboard_last_update = time.time()

        # ── Optimization Phase (fully on GPU with AMP) ────────────────────
        b_vis, b_vel, b_act, b_lp, b_rew, b_done, b_val = buffer.get_tensors()

        # Compute next values for GAE
        with torch.no_grad():
            with torch.amp.autocast("cuda", dtype=amp_dtype):
                nxt_vis = torch.tensor(obs_dict["visual"],  dtype=torch.float32, device=device)
                nxt_vel = torch.tensor(obs_dict["velocity"], dtype=torch.float32, device=device)
                next_val = model.get_value(nxt_vis, nxt_vel)  # (N,)

        # Reshape for GAE
        T, N = args.n_steps, args.n_envs
        advantages, returns = compute_gae(
            b_rew.reshape(T, N), b_val.reshape(T, N), b_done.reshape(T, N),
            next_val, args.gamma, args.gae_lambda
        )
        advantages = (advantages - advantages.mean()) / (advantages.std() + 1e-8)

        dataset_size = b_vis.shape[0]
        policy_losses, value_losses, entropies = [], [], []
        approx_kls, clip_fracs = [], []

        for _ in range(args.update_epochs):
            perm = torch.randperm(dataset_size, device=device)
            early_stop = False
            for start in range(0, dataset_size, args.batch_size):
                idx = perm[start : start + args.batch_size]

                with torch.amp.autocast("cuda", dtype=amp_dtype):
                    if args.detach_critic_trunk:
                        raw_m = (model._orig_mod if hasattr(model, "_orig_mod") else model)
                        latent = raw_m.extract_features(b_vis[idx], b_vel[idx])
                        action_mean = raw_m.actor_mean(latent)
                        action_std = torch.exp(raw_m.actor_log_std)
                        dist = Normal(action_mean, action_std)
                        new_lp = dist.log_prob(b_act[idx]).sum(dim=-1)
                        entropy = dist.entropy().sum(dim=-1)
                        new_val = raw_m.critic(latent.detach()).squeeze(-1)
                    else:
                        _, new_lp, entropy, new_val = model.get_action_and_value(
                            b_vis[idx], b_vel[idx], b_act[idx]
                        )
                    logratio = new_lp - b_lp[idx]
                    ratio   = torch.exp(logratio)
                    adv_b   = advantages[idx]
                    surr1   = ratio * adv_b
                    surr2   = torch.clamp(ratio, 1 - args.clip_eps, 1 + args.clip_eps) * adv_b
                    pl      = -torch.min(surr1, surr2).mean()
                    vl      = 0.5 * ((new_val - returns[idx]) ** 2).mean()
                    ent     = entropy.mean()
                    loss    = pl + args.vf_coef * vl - args.ent_coef * ent

                    # Optional BC behavioral anchor regularizer (Phase 10)
                    if ref_model is not None and args.bc_anchor_coef > 0:
                        with torch.no_grad():
                            ref_act = ref_model(b_vis[idx], b_vel[idx])
                        cur_act = model(b_vis[idx], b_vel[idx])
                        anchor_loss = torch.mean((cur_act - ref_act) ** 2)
                        loss = loss + args.bc_anchor_coef * anchor_loss

                optimizer.zero_grad(set_to_none=True)  # faster than zero_grad()
                if scaler is not None:
                    scaler.scale(loss).backward()
                    scaler.unscale_(optimizer)
                    if args.detach_critic_trunk:
                        raw_m = (model._orig_mod if hasattr(model, "_orig_mod") else model)
                        trunk_actor_params = [p for name, p in raw_m.named_parameters() if not name.startswith("critic")]
                        critic_params = list(raw_m.critic.parameters())
                        torch.nn.utils.clip_grad_norm_(trunk_actor_params, 0.5)
                        torch.nn.utils.clip_grad_norm_(critic_params, 0.5)
                    else:
                        torch.nn.utils.clip_grad_norm_(model.parameters(), 0.5)
                    scaler.step(optimizer)
                    scaler.update()
                else:
                    loss.backward()
                    if args.detach_critic_trunk:
                        raw_m = (model._orig_mod if hasattr(model, "_orig_mod") else model)
                        trunk_actor_params = [p for name, p in raw_m.named_parameters() if not name.startswith("critic")]
                        critic_params = list(raw_m.critic.parameters())
                        torch.nn.utils.clip_grad_norm_(trunk_actor_params, 0.5)
                        torch.nn.utils.clip_grad_norm_(critic_params, 0.5)
                    else:
                        torch.nn.utils.clip_grad_norm_(model.parameters(), 0.5)
                    optimizer.step()

                with torch.no_grad():
                    approx_kl = ((ratio - 1.0) - logratio).mean().item()
                    clip_frac = ((ratio - 1.0).abs() > args.clip_eps).float().mean().item()

                policy_losses.append(pl.item())
                value_losses.append(vl.item())
                entropies.append(ent.item())
                approx_kls.append(approx_kl)
                clip_fracs.append(clip_frac)

                if args.target_kl > 0 and approx_kl > args.target_kl:
                    early_stop = True
                    break
            if early_stop:
                break

        rollout_time = time.perf_counter() - rollout_start
        last_sps         = (args.n_steps * args.n_envs) / rollout_time
        last_policy_loss = float(np.mean(policy_losses))
        last_value_loss  = float(np.mean(value_losses))
        last_entropy     = float(np.mean(entropies))
        last_kl          = float(np.mean(approx_kls))
        last_clip_frac   = float(np.mean(clip_fracs))

        print(
            f"Step {global_step:>8,}/{args.total_timesteps:,} | "
            f"SPS: {last_sps:>5.0f} | "
            f"PLoss: {last_policy_loss:+.4f} | "
            f"VLoss: {last_value_loss:8.2f} | "
            f"Entropy: {last_entropy:.4f} | "
            f"KL: {last_kl:.4f} | "
            f"Clip: {last_clip_frac:.3f} | "
            f"Ep: {episode_count:,} | "
            f"BestRew: {best_reward:.1f}"
        )
        writer.add_scalar("Train/PolicyLoss",   last_policy_loss, global_step)
        writer.add_scalar("Train/ValueLoss",    last_value_loss,  global_step)
        writer.add_scalar("Train/Entropy",      last_entropy,     global_step)
        writer.add_scalar("Train/ApproxKL",     last_kl,          global_step)
        writer.add_scalar("Train/ClipFraction", last_clip_frac,   global_step)
        writer.add_scalar("Train/SPS",          last_sps,         global_step)

        # Periodic Snapshot & Behavioral Evaluation (Phase 5 & 6)
        if global_step >= next_snapshot_step:
            raw_m = (model._orig_mod if hasattr(model, "_orig_mod") else model)
            snap_idx = int(round(global_step / 1000.0))
            snap_path = os.path.join(args.save_dir, f"ckpt_{snap_idx}k.pt")
            torch.save(raw_m.state_dict(), snap_path + ".tmp")
            os.replace(snap_path + ".tmp", snap_path)

            eval_metrics = None
            if args.eval_interval > 0:
                print(f"\n[*] Running Periodic Behavioral Evaluation at Step {global_step:,}...")
                eval_metrics = evaluate_model_internal(raw_m, device)
                for s_name, m_dict in eval_metrics.items():
                    print(f"    [{s_name.upper()}] Success: {m_dict['success_rate']:.1f}% | Coll: {m_dict['collision_rate']:.1f}% | "
                          f"Len: {m_dict['mean_episode_length']:.1f} | GoalDist: {m_dict['final_goal_distance']:.2f}m | "
                          f"Rew: {m_dict['mean_reward']:.2f} | Clear: {m_dict['mean_min_clearance']:.2f}m | "
                          f"Steer: {m_dict['steering_mean']:.3f} | Throt: {m_dict['throttle_mean']:.3f}")
                    writer.add_scalar(f"Eval/{s_name}_SuccessRate", m_dict["success_rate"], global_step)
                    writer.add_scalar(f"Eval/{s_name}_CollisionRate", m_dict["collision_rate"], global_step)
                    writer.add_scalar(f"Eval/{s_name}_MeanReward", m_dict["mean_reward"], global_step)
                    writer.add_scalar(f"Eval/{s_name}_GoalDist", m_dict["final_goal_distance"], global_step)

            snap_meta = {
                "source_checkpoint": args.checkpoint,
                "global_step": global_step,
                "learning_rate": args.learning_rate,
                "log_std": raw_m.actor_log_std.detach().cpu().tolist(),
                "reward": best_reward,
                "best_reward": best_reward,
                "eval_metrics": eval_metrics,
                "timestamp": time.time(),
                "config": vars(args)
            }
            with open(snap_path + ".meta.json", "w") as f:
                json.dump(snap_meta, f, indent=2)
            print(f"[+] Saved snapshot checkpoint: {snap_path}\n")
            next_snapshot_step += args.snapshot_interval

    if show_dashboard:
        cv2.destroyAllWindows()

    # Save Final Model and run final evaluation
    raw_m = (model._orig_mod if hasattr(model, "_orig_mod") else model)
    final_path = os.path.join(args.save_dir, "final_model.pt")
    torch.save(raw_m.state_dict(), final_path + ".tmp")
    os.replace(final_path + ".tmp", final_path)

    final_eval = None
    if args.eval_interval > 0:
        print(f"\n[*] Running Final Behavioral Evaluation at Step {global_step:,}...")
        final_eval = evaluate_model_internal(raw_m, device)
        for s_name, m_dict in final_eval.items():
            print(f"    [{s_name.upper()}] Success: {m_dict['success_rate']:.1f}% | Coll: {m_dict['collision_rate']:.1f}% | "
                  f"Len: {m_dict['mean_episode_length']:.1f} | GoalDist: {m_dict['final_goal_distance']:.2f}m | "
                  f"Rew: {m_dict['mean_reward']:.2f} | Clear: {m_dict['mean_min_clearance']:.2f}m | "
                  f"Steer: {m_dict['steering_mean']:.3f} | Throt: {m_dict['throttle_mean']:.3f}")

    final_meta = {
        "source_checkpoint": args.checkpoint,
        "global_step": global_step,
        "learning_rate": args.learning_rate,
        "log_std": raw_m.actor_log_std.detach().cpu().tolist(),
        "reward": best_reward,
        "best_reward": best_reward,
        "eval_metrics": final_eval,
        "timestamp": time.time(),
        "config": vars(args)
    }
    with open(final_path + ".meta.json", "w") as f:
        json.dump(final_meta, f, indent=2)
    print(f"[+] Saved final model checkpoint: {final_path}")

    vec_env.close()
    writer.close()
    print("[*] Training Complete!")


# ─────────────────────────────────────────────────────────────────────────────
# Entry Point
# ─────────────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    mp.set_start_method("spawn", force=True)   # Required on Windows for CUDA + multiprocessing

    parser = argparse.ArgumentParser(description="GPU-Maximized PPO Training for Drone Navigation")
    parser.add_argument("--checkpoint",          type=str,   default="bc_25k_clean.pt", help="Baseline checkpoint to load")
    parser.add_argument("--save-dir",            type=str,   default="runs/finetune_ppo", help="Directory where fine-tuning checkpoints and metadata are stored")
    parser.add_argument("--total-timesteps",     type=int,   default=50_000,   help="Total environment steps")
    parser.add_argument("--n-envs",              type=int,   default=12,       help="Number of parallel environments (optimal sweet spot: 12 on i7-14700HX)")
    parser.add_argument("--n-steps",             type=int,   default=512,      help="Rollout steps per env per update")
    parser.add_argument("--batch-size",          type=int,   default=1024,     help="PPO mini-batch size (6144 / 1024 = 6 batches)")
    parser.add_argument("--update-epochs",       type=int,   default=10,       help="PPO update epochs per rollout")
    parser.add_argument("--learning-rate",       type=float, default=5e-5,     help="Adam learning rate")
    parser.add_argument("--gamma",               type=float, default=0.99,     help="Discount factor")
    parser.add_argument("--gae-lambda",          type=float, default=0.95,     help="GAE lambda")
    parser.add_argument("--clip-eps",            type=float, default=0.2,      help="PPO clip epsilon")
    parser.add_argument("--ent-coef",            type=float, default=0.01,     help="Entropy coefficient")
    parser.add_argument("--vf-coef",             type=float, default=0.5,      help="Value function loss coefficient")
    parser.add_argument("--log-std-mode",        type=str,   default="reduced", choices=["checkpoint", "reduced", "custom"], help="Exploration mode")
    parser.add_argument("--reduced-log-std",     type=float, default=-1.6,     help="Target log_std for reduced exploration")
    parser.add_argument("--custom-log-std",      type=float, default=-1.6,     help="Target log_std for custom exploration")
    parser.add_argument("--freeze-log-std",      action="store_true",          help="Freeze actor_log_std during fine-tuning")
    parser.add_argument("--detach-critic-trunk", action="store_true",          help="Detach convolutional feature trunk from critic value loss to prevent visual representation erosion during fine-tuning")
    parser.add_argument("--snapshot-interval",   type=int,   default=25_000,   help="Steps between periodic checkpoint snapshots")
    parser.add_argument("--eval-interval",       type=int,   default=25_000,   help="Steps between behavioral evaluations (0 to disable)")
    parser.add_argument("--bc-anchor-coef",      type=float, default=0.0,      help="BC anchor regularization coefficient (Phase 10)")
    parser.add_argument("--target-kl",           type=float, default=0.0,      help="Target KL threshold for early stopping update epochs (0 to disable)")
    parser.add_argument("--max-steps",           type=int,   default=500,      help="Max steps per episode")
    parser.add_argument("--seed",                type=int,   default=42,       help="Random seed")
    parser.add_argument("--gui",                 action="store_true",          help="Enable live dashboard")
    parser.add_argument("--dashboard",           action="store_true",          help="Force launch live dashboard")
    parser.add_argument("--compile",             action="store_true",          help="Enable torch.compile (opt-in; eager is faster for batch-12 inference)")
    parser.add_argument("--amp-dtype",           type=str,   default="bfloat16", choices=["bfloat16", "float16", "float32"], help="Mixed precision data type")

    args = parser.parse_args()
    train_ppo(args)
