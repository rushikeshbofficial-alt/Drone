"""
recon_measurements.py - Empirical measurements for Gate 0 Reconnaissance
- Measures open-loop stopping behavior (forward and lateral)
- Analyzes baseline rollouts: velocity vs FOV alignment and crash telemetry
- Evaluates 30 tuning seeds (2000-2029) with Wilson 95% CIs
"""

import math
import numpy as np
import torch
from environment import IndoorDroneNavEnv
from model import PhysicsInformedActorCritic


def wilson_score_interval(successes: int, total: int, confidence: float = 0.95):
    """Computes Wilson score 95% confidence interval for a binomial proportion."""
    if total == 0:
        return 0.0, 0.0, 0.0
    z = 1.95996  # for 95% CI
    p_hat = successes / total
    denom = 1.0 + (z**2) / total
    center = (p_hat + (z**2) / (2.0 * total)) / denom
    half_width = (z / denom) * math.sqrt((p_hat * (1.0 - p_hat) / total) + ((z**2) / (4.0 * (total**2))))
    lower = max(0.0, center - half_width)
    upper = min(1.0, center + half_width)
    return p_hat, lower, upper


def measure_stopping_dynamics():
    print("=" * 60)
    print("EMPIRICAL STOPPING BEHAVIOR MEASUREMENT (Point c & Trust Rule 5)")
    print("=" * 60)
    
    # 1. Forward stopping test
    env = IndoorDroneNavEnv(gui=False, seed=42)
    env.reset(seed=42)
    
    # Accelerate forward (world +Y) for 10 control steps with action [0, 1, 0, 0] (target_vel = [0, 3, 0])
    print("[*] Phase 1: Accelerating drone forward to target velocity 3.0 m/s...")
    for _ in range(10):
        obs, rew, term, trunc, info = env.step(np.array([0.0, 1.0, 0.0, 0.0], dtype=np.float32))
    
    v_before = env.drone_vel.copy() if not env.pybullet_active else obs["velocity"].copy()
    p_before = env.drone_pos.copy()
    print(f"    Velocity before zero-action: {v_before} m/s (speed = {np.linalg.norm(v_before):.3f} m/s)")
    print(f"    Position before zero-action: {p_before}")
    
    # Now command zero action: [0, 0, 0, 0]
    print("[*] Phase 2: Command zero-action [0, 0, 0, 0] and observe control step 1...")
    obs, rew, term, trunc, info = env.step(np.array([0.0, 0.0, 0.0, 0.0], dtype=np.float32))
    v_after_step1 = env.drone_vel.copy() if not env.pybullet_active else obs["velocity"].copy()
    p_after_step1 = env.drone_pos.copy()
    
    delta_pos = np.linalg.norm(p_after_step1 - p_before)
    print(f"    Velocity after 1 control step: {v_after_step1} m/s (speed = {np.linalg.norm(v_after_step1):.4f} m/s)")
    print(f"    Position after 1 control step: {p_after_step1}")
    print(f"    Displacement during stop step: {delta_pos:.6f} m")
    
    # 2. Substep-level inspection
    print("\n[*] Phase 3: Substep-level analysis inside physics loop:")
    # We inspect how environment.py executes substeps:
    # On substep 0, target_vel = action[:3]*3.0 = [0, 0, 0].
    # PyBullet calls p.resetBaseVelocity(self.drone_id, linearVelocity=[0, 0, 0])
    # Analytical sets self.drone_vel = [0, 0, 0], self.drone_pos += [0, 0, 0] * dt.
    # Therefore, velocity decays to 0.0 instantly on substep 0.
    
    # 3. Lateral stopping test (world +X)
    print("\n[*] Phase 4: Lateral stopping test (commanding vx = +3.0 m/s then zero)...")
    env.reset(seed=43)
    for _ in range(10):
        obs, rew, term, trunc, info = env.step(np.array([1.0, 0.0, 0.0, 0.0], dtype=np.float32))
    v_lat_before = env.drone_vel.copy() if not env.pybullet_active else obs["velocity"].copy()
    p_lat_before = env.drone_pos.copy()
    
    obs, rew, term, trunc, info = env.step(np.array([0.0, 0.0, 0.0, 0.0], dtype=np.float32))
    v_lat_after = env.drone_vel.copy() if not env.pybullet_active else obs["velocity"].copy()
    p_lat_after = env.drone_pos.copy()
    lat_disp = np.linalg.norm(p_lat_after - p_lat_before)
    print(f"    Lateral velocity before zero: {v_lat_before} m/s (speed = {np.linalg.norm(v_lat_before):.3f} m/s)")
    print(f"    Lateral velocity after zero:  {v_lat_after} m/s (speed = {np.linalg.norm(v_lat_after):.4f} m/s)")
    print(f"    Displacement during stop:    {lat_disp:.6f} m")
    env.close()


def analyze_baseline_fov_and_telemetry(checkpoint_path="best_model.pt", seeds=[101, 202, 303, 404, 505]):
    print("\n" + "=" * 60)
    print("BASELINE ROLLOUT FOV ALIGNMENT & CRASH ANALYSIS (Point b & f)")
    print("=" * 60)
    
    device = "cuda" if torch.cuda.is_available() else "cpu"
    model = PhysicsInformedActorCritic().to(device)
    model.load_state_dict(torch.load(checkpoint_path, map_location=device, weights_only=True))
    model.eval()
    
    half_fov_deg = 65.0 / 2.0  # 32.5 degrees
    
    total_steps = 0
    outside_fov_steps = 0
    episodes_data = []
    
    for seed in seeds:
        env = IndoorDroneNavEnv(gui=False, seed=seed, max_steps=500)
        obs, info = env.reset(seed=seed)
        
        ep_steps = 0
        ep_outside_fov = 0
        ep_reward = 0.0
        min_clearance = float("inf")
        step_telemetry = []
        
        while True:
            vis_t = torch.tensor(obs["visual"], dtype=torch.float32, device=device).unsqueeze(0)
            vel_t = torch.tensor(obs["velocity"], dtype=torch.float32, device=device).unsqueeze(0)
            with torch.no_grad():
                act = model(vis_t, vel_t).squeeze(0).cpu().numpy()
            
            # Record pre-step kinematics
            pos = env.drone_pos.copy()
            vel = obs["velocity"].copy()
            speed = np.linalg.norm(vel[:2])
            yaw = env.drone_orn[2] if hasattr(env, "drone_orn") else 0.0
            
            # Heading vector of camera in world XY
            cam_dir = np.array([-math.sin(yaw), math.cos(yaw)]) # When yaw=0, camera points along +Y
            # Wait, let's verify cam forward vector from environment.py:
            # In analytical mode:
            # rx = unit_rx * cos_y + unit_ry * sin_y
            # ry = -unit_rx * sin_y + unit_ry * cos_y
            # For central ray (rx_unrot=0, ry_unrot=1):
            # rx = sin(yaw), ry = cos(yaw). Wait:
            # Let's check environment.py line 256:
            # rx = self._unit_rx_unrot * cos_y + self._unit_ry_unrot * sin_y -> for central ray: rx = sin_y
            # ry = -self._unit_rx_unrot * sin_y + self._unit_ry_unrot * cos_y -> ry = cos_y
            # So forward direction is (sin(yaw), cos(yaw)).
            cam_forward = np.array([math.sin(yaw), math.cos(yaw)], dtype=np.float32)
            
            angle_deg = 0.0
            is_outside = False
            if speed > 0.1:
                vel_dir = vel[:2] / speed
                dot = np.clip(np.dot(vel_dir, cam_forward), -1.0, 1.0)
                angle_deg = math.degrees(math.acos(dot))
                if angle_deg > half_fov_deg:
                    is_outside = True
                    ep_outside_fov += 1
                    outside_fov_steps += 1
            
            total_steps += 1
            ep_steps += 1
            
            next_obs, reward, terminated, truncated, sinfo = env.step(act)
            ep_reward += reward
            if "min_depth" in sinfo:
                min_clearance = min(min_clearance, float(sinfo["min_depth"]))
            
            step_telemetry.append({
                "step": ep_steps,
                "pos": pos.tolist(),
                "vel": vel.tolist(),
                "speed": float(speed),
                "action": act.tolist(),
                "angle_to_cam_deg": float(angle_deg),
                "outside_fov": is_outside,
                "min_depth": float(sinfo.get("min_depth", 0.0)),
                "oob": env.out_of_bounds
            })
            
            obs = next_obs
            
            if terminated or truncated:
                collision = bool(sinfo.get("collision", False))
                goal_reached = bool(sinfo.get("goal_reached", False))
                oob = env.out_of_bounds
                
                status = "SUCCESS" if goal_reached else ("WALL_OOB" if oob else ("OBSTACLE_COLLISION" if collision else "TIMEOUT"))
                episodes_data.append({
                    "seed": seed,
                    "status": status,
                    "steps": ep_steps,
                    "reward": ep_reward,
                    "min_clearance": min_clearance,
                    "outside_fov_steps": ep_outside_fov,
                    "outside_fov_pct": (ep_outside_fov / max(ep_steps, 1)) * 100.0,
                    "last_steps": step_telemetry[-5:]
                })
                print(f"[Seed {seed}] Status: {status:18s} | Steps: {ep_steps:3d} | Rew: {ep_reward:7.2f} | "
                      f"MinClr: {min_clearance:.2f}m | Outside FOV: {ep_outside_fov}/{ep_steps} ({ep_outside_fov/max(ep_steps,1)*100:.1f}%)")
                env.close()
                break
                
    overall_outside_pct = (outside_fov_steps / max(total_steps, 1)) * 100.0
    print(f"\nTotal steps analyzed: {total_steps}")
    print(f"Steps where velocity angle was outside camera FOV (>{half_fov_deg:.1f}°): {outside_fov_steps} ({overall_outside_pct:.1f}%)")
    return episodes_data


def evaluate_tuning_seeds(checkpoint_path="best_model.pt", seeds=list(range(2000, 2030))):
    print("\n" + "=" * 60)
    print(f"TUNING SEEDS EVALUATION (Seeds 2000-2029: {len(seeds)} episodes)")
    print("=" * 60)
    
    device = "cuda" if torch.cuda.is_available() else "cpu"
    model = PhysicsInformedActorCritic().to(device)
    model.load_state_dict(torch.load(checkpoint_path, map_location=device, weights_only=True))
    model.eval()
    
    outcomes = {"SUCCESS": 0, "OBSTACLE_COLLISION": 0, "WALL_OOB": 0, "TIMEOUT": 0}
    rewards = []
    clearances = []
    steps_list = []
    
    for idx, seed in enumerate(seeds):
        env = IndoorDroneNavEnv(gui=False, seed=seed, max_steps=500)
        obs, info = env.reset(seed=seed)
        
        ep_reward = 0.0
        step_count = 0
        min_clearance = float("inf")
        
        while True:
            vis_t = torch.tensor(obs["visual"], dtype=torch.float32, device=device).unsqueeze(0)
            vel_t = torch.tensor(obs["velocity"], dtype=torch.float32, device=device).unsqueeze(0)
            with torch.no_grad():
                act = model(vis_t, vel_t).squeeze(0).cpu().numpy()
            
            obs, rew, term, trunc, sinfo = env.step(act)
            ep_reward += rew
            step_count += 1
            if "min_depth" in sinfo:
                min_clearance = min(min_clearance, float(sinfo["min_depth"]))
                
            if term or trunc:
                collision = bool(sinfo.get("collision", False))
                goal_reached = bool(sinfo.get("goal_reached", False))
                oob = env.out_of_bounds
                
                if goal_reached:
                    status = "SUCCESS"
                elif oob:
                    status = "WALL_OOB"
                elif collision:
                    status = "OBSTACLE_COLLISION"
                else:
                    status = "TIMEOUT"
                    
                outcomes[status] += 1
                rewards.append(ep_reward)
                clearances.append(min_clearance if min_clearance != float("inf") else 0.0)
                steps_list.append(step_count)
                
                print(f"[{idx+1:02d}/30] Seed {seed}: {status:18s} | Steps: {step_count:3d} | "
                      f"Reward: {ep_reward:7.2f} | MinClearance: {min_clearance:.2f}m")
                env.close()
                break

    n = len(seeds)
    print("\n" + "=" * 60)
    print("TUNING SEEDS SUMMARY (Seeds 2000-2029)")
    print("=" * 60)
    print(f"Total episodes: {n}")
    for cat in ["SUCCESS", "OBSTACLE_COLLISION", "WALL_OOB", "TIMEOUT"]:
        cnt = outcomes[cat]
        phat, lo, hi = wilson_score_interval(cnt, n)
        print(f"  {cat:18s}: {cnt:2d}/{n} ({phat*100.0:.1f}%) [95% CI: {lo*100:.1f}% - {hi*100:.1f}%]")
    
    combined_coll = outcomes["OBSTACLE_COLLISION"] + outcomes["WALL_OOB"]
    c_phat, c_lo, c_hi = wilson_score_interval(combined_coll, n)
    print(f"  {'TOTAL_COLLISION':18s}: {combined_coll:2d}/{n} ({c_phat*100:.1f}%) [95% CI: {c_lo*100:.1f}% - {c_hi*100:.1f}%]")
    print(f"Mean Reward: {np.mean(rewards):.2f} +/- {np.std(rewards):.2f}")
    print(f"Mean Min Clearance: {np.mean(clearances):.2f} m")
    print(f"Mean Steps: {np.mean(steps_list):.1f}")
    print("=" * 60)


if __name__ == "__main__":
    measure_stopping_dynamics()
    analyze_baseline_fov_and_telemetry()
    evaluate_tuning_seeds()
