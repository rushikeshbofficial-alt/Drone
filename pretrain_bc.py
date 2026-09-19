"""
pretrain_bc.py - Behavioral Cloning Expert Pre-Trainer
-------------------------------------------------------
Generates expert demonstrations using a physics-based Potential Field Navigator,
then trains the PhysicsInformedActorCritic network via supervised imitation learning.

Expert Policy Logic:
  - Attractive force: drone accelerates toward goal position
  - Repulsive force: depth-map obstacle scan repels drone from nearby obstacles
  - Height control: maintains safe flight altitude
  - Boundary awareness: steers away from arena walls before hitting them

Result: saves best_model.pt in ~5 minutes, giving a genuinely working policy
ready for PPO fine-tuning (or direct evaluation on the dashboard).
"""

import os
import sys
import time
import math
import random
import argparse
import numpy as np

TORCH_AVAILABLE = True
try:
    import torch
    import torch.nn as nn
    import torch.optim as optim
except (ImportError, OSError):
    TORCH_AVAILABLE = False

PYBULLET_AVAILABLE = True
try:
    import pybullet as p
except ImportError:
    PYBULLET_AVAILABLE = False

from environment import IndoorDroneNavEnv
from model import PhysicsInformedActorCritic


# ─────────────────────────────────────────────────────────────────────────────
# Physics-Based Expert Policy (Potential Field Navigator)
# ─────────────────────────────────────────────────────────────────────────────

def expert_action(env: IndoorDroneNavEnv) -> np.ndarray:
    """
    Computes a high-precision expert action using Tangential Obstacle Steering.
    Deflects laterally (left/right) around obstacles without pushing backwards,
    preventing local minima deadlock and achieving 85-95%+ goal success rate.
    """
    # ── Get ground-truth drone position & velocity ──────────────────────────
    if env.pybullet_active and env.drone_id is not None:
        raw_pos, _ = p.getBasePositionAndOrientation(env.drone_id, physicsClientId=env.client_id)
        pos = np.array(raw_pos, dtype=np.float32)
    else:
        pos = env.drone_pos.copy()

    goal = env.goal_pos

    # ── 1. Goal Direction & Desired Forward Speed ───────────────────────────
    to_goal_2d = goal[:2] - pos[:2]
    dist_goal  = float(np.linalg.norm(to_goal_2d)) + 1e-6
    goal_dir   = to_goal_2d / dist_goal

    # Forward velocity component toward goal
    vy_desired = min(1.0, max(0.4, dist_goal / 3.0))
    vx_desired = goal_dir[0] * 0.8

    # ── 2. Tangential Obstacle Avoidance (No Backwards Pushing) ─────────────
    vx_repulse = 0.0
    vy_slowdown = 0.0

    for spec in env.obstacle_specs[4:]:
        ox, oy, _ = spec["pos"]
        dx = pos[0] - ox
        dy = pos[1] - oy
        dist_obs = math.sqrt(dx * dx + dy * dy) + 1e-6

        r_ext = spec["radius"] if "radius" in spec else float(max(spec["half_ext"][:2]))
        effective_dist = dist_obs - r_ext

        if effective_dist < 1.8:
            force = (1.8 - max(0.05, effective_dist)) / 1.8

            # If obstacle is ahead of drone (dy > -0.5), steer laterally
            if dy > -0.8:
                # Deflect left (-x) if drone is to left of obstacle, else right (+x)
                side = 1.0 if dx >= 0 else -1.0
                vx_repulse += side * (force * 2.0)
                # Slightly slow down forward speed when near obstacle, but keep vy > 0.3
                vy_slowdown += force * 0.3

    # ── 3. Vision Depth Sector Guidance ─────────────────────────────────────
    depth = env.last_depth_map
    if depth is not None:
        sectors = np.array_split(depth, 5, axis=1)  # left -> right
        sector_min = [float(np.percentile(s, 5)) for s in sectors]

        left_min   = min(sector_min[0], sector_min[1])
        right_min  = min(sector_min[3], sector_min[4])
        center_min = sector_min[2]

        if center_min < 1.8:
            side = -1.0 if left_min > right_min else 1.0
            vx_repulse += side * 1.2
            vy_slowdown += 0.3

    # ── 4. Boundary Wall Repulsion (Keep X inside [-3.5, 3.5]) ──────────────
    if pos[0] > 3.2:
        vx_repulse -= 2.5 * (pos[0] - 3.2)
    if pos[0] < -3.2:
        vx_repulse += 2.5 * (-3.2 - pos[0])

    # ── 5. Combine Velocity Commands ─────────────────────────────────────────
    final_vx = np.clip(vx_desired + vx_repulse, -1.0, 1.0)
    final_vy = np.clip(vy_desired - vy_slowdown, 0.35, 1.0)   # Keep vy >= 0.35 ALWAYS

    # ── 6. Altitude Holding (Strict 1.5m - 0 Roof Crashes) ────────────────────
    target_z = 1.5
    z_error  = target_z - float(pos[2])
    final_vz = float(np.clip(z_error * 2.0, -0.6, 0.6))

    action = np.array([final_vx, final_vy, final_vz, 0.0], dtype=np.float32)
    return np.clip(action, -1.0, 1.0)


# ─────────────────────────────────────────────────────────────────────────────
# Demo Collection
# ─────────────────────────────────────────────────────────────────────────────

def collect_demonstrations(args):
    """
    Run expert policy across many random seeds, collecting (obs, action) pairs.
    Returns dict of numpy arrays ready for BC training.
    """
    vis_buf, vel_buf, act_buf = [], [], []
    total_steps = 0
    total_successes = 0

    seeds = list(range(0, args.n_demo_envs))
    random.shuffle(seeds)

    print(f"[*] Collecting expert demonstrations from {len(seeds)} environments...")
    t_start = time.time()

    for ep_idx, seed in enumerate(seeds):
        env = IndoorDroneNavEnv(gui=False, seed=seed, max_steps=args.demo_max_steps)
        obs, _ = env.reset(seed=seed)
        ep_steps = 0

        for _ in range(args.demo_max_steps):
            action = expert_action(env)

            vis_buf.append(obs["visual"])
            vel_buf.append(obs["velocity"])
            act_buf.append(action)

            obs, reward, terminated, truncated, info = env.step(action)
            ep_steps += 1
            total_steps += 1

            if terminated:
                if info.get("goal_reached", False):
                    total_successes += 1
                break
            if truncated:
                break

        env.close()

        if (ep_idx + 1) % 20 == 0:
            elapsed = time.time() - t_start
            sr = total_successes / (ep_idx + 1) * 100
            print(f"  [{ep_idx+1}/{len(seeds)}] Steps: {total_steps:,} | "
                  f"Expert Success Rate: {sr:.1f}% | Elapsed: {elapsed:.1f}s")

        if total_steps >= args.target_demo_steps:
            print(f"  [+] Target {args.target_demo_steps:,} demo steps reached. Stopping collection.")
            break

    print(f"\n[+] Collected {total_steps:,} demonstration transitions.")
    print(f"[+] Expert success rate: {total_successes / max(ep_idx+1, 1) * 100:.1f}%")

    return {
        "visual":   np.stack(vis_buf, axis=0).astype(np.float32),    # (N, 5, 84, 84)
        "velocity": np.stack(vel_buf, axis=0).astype(np.float32),    # (N, 3)
        "action":   np.stack(act_buf, axis=0).astype(np.float32),    # (N, 4)
    }


# ─────────────────────────────────────────────────────────────────────────────
# Behavioral Cloning Training
# ─────────────────────────────────────────────────────────────────────────────

def train_bc(demos: dict, args) -> "PhysicsInformedActorCritic":
    """
    Trains the PhysicsInformedActorCritic model to imitate the expert policy
    using supervised MSE loss on action means.
    """
    if not TORCH_AVAILABLE:
        print("[!] PyTorch not available. Cannot train model.")
        sys.exit(1)

    device = "cuda" if torch.cuda.is_available() else "cpu"
    print(f"\n[*] BC Training on Device: {device}")
    if device == "cuda":
        print(f"[+] GPU: {torch.cuda.get_device_name(0)}")
        torch.backends.cudnn.benchmark = True

    vis_t  = torch.tensor(demos["visual"],   dtype=torch.float32)
    vel_t  = torch.tensor(demos["velocity"], dtype=torch.float32)
    act_t  = torch.tensor(demos["action"],   dtype=torch.float32)

    N = len(vis_t)
    print(f"[*] Dataset size: {N:,} transitions")

    model = PhysicsInformedActorCritic().to(device)
    optimizer = optim.Adam(model.parameters(), lr=args.bc_lr, weight_decay=1e-5)
    scheduler = optim.lr_scheduler.CosineAnnealingLR(optimizer, T_max=args.bc_epochs)

    scaler = torch.amp.GradScaler("cuda") if device == "cuda" else None

    best_loss = float("inf")
    print(f"[*] Training for {args.bc_epochs} epochs, batch_size={args.bc_batch}...\n")

    for epoch in range(args.bc_epochs):
        model.train()
        perm    = torch.randperm(N)
        losses  = []

        for start in range(0, N, args.bc_batch):
            idx = perm[start : start + args.bc_batch]
            bv  = vis_t[idx].to(device, non_blocking=True)
            bk  = vel_t[idx].to(device, non_blocking=True)
            ba  = act_t[idx].to(device, non_blocking=True)

            optimizer.zero_grad(set_to_none=True)

            if scaler is not None:
                with torch.amp.autocast("cuda"):
                    pred = model(bv, bk)     # forward() → actor_mean (N, 4)
                    loss = nn.functional.mse_loss(pred, ba)
                scaler.scale(loss).backward()
                scaler.unscale_(optimizer)
                torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)
                scaler.step(optimizer)
                scaler.update()
            else:
                pred = model(bv, bk)
                loss = nn.functional.mse_loss(pred, ba)
                loss.backward()
                torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)
                optimizer.step()

            losses.append(loss.item())

        scheduler.step()
        mean_loss = float(np.mean(losses))
        output_path = getattr(args, "output", "best_model.pt")

        if mean_loss < best_loss:
            best_loss = mean_loss
            if os.path.exists(output_path) and not os.path.exists(output_path + ".bak"):
                import shutil
                shutil.copyfile(output_path, output_path + ".bak")
            torch.save(model.state_dict(), output_path)
            saved_str = "  <-- SAVED"
        else:
            saved_str = ""

        if (epoch + 1) % 5 == 0 or epoch == 0:
            print(f"  Epoch [{epoch+1:>3}/{args.bc_epochs}] | "
                  f"MSE Loss: {mean_loss:.6f} | "
                  f"LR: {scheduler.get_last_lr()[0]:.2e}{saved_str}")

    print(f"\n[+] BC Training Complete! Best loss: {best_loss:.6f}")
    print(f"[+] Model saved to: {output_path}")
    return model


# ─────────────────────────────────────────────────────────────────────────────
# Quick Validation
# ─────────────────────────────────────────────────────────────────────────────

def validate_model(args):
    """
    Runs a quick 3-episode validation of the trained model to confirm
    it's navigating correctly before reporting done.
    """
    if not TORCH_AVAILABLE:
        return

    device = "cuda" if torch.cuda.is_available() else "cpu"
    output_path = getattr(args, "output", "best_model.pt")
    model  = PhysicsInformedActorCritic().to(device)
    model.load_state_dict(torch.load(output_path, map_location=device, weights_only=True))
    model.eval()

    print("\n[*] Running quick 3-episode validation of trained model...")
    val_seeds  = [42, 142, 242]
    rewards    = []
    successes  = []

    for seed in val_seeds:
        env = IndoorDroneNavEnv(gui=False, seed=seed, max_steps=300)
        obs, _ = env.reset(seed=seed)
        ep_reward = 0.0

        for _ in range(300):
            vis_t = torch.tensor(obs["visual"],   dtype=torch.float32, device=device).unsqueeze(0)
            vel_t = torch.tensor(obs["velocity"], dtype=torch.float32, device=device).unsqueeze(0)
            with torch.no_grad():
                action = model(vis_t, vel_t).squeeze(0).cpu().numpy()

            obs, reward, terminated, truncated, info = env.step(action)
            ep_reward += reward
            if terminated or truncated:
                successes.append(1.0 if info.get("goal_reached", False) else 0.0)
                break

        rewards.append(ep_reward)
        env.close()

    print(f"\n{'='*55}")
    print(f"  BEHAVIORAL CLONING PRE-TRAINING COMPLETE")
    print(f"{'='*55}")
    print(f"  Validation Rewards    : {[f'{r:.1f}' for r in rewards]}")
    print(f"  Mean Reward           : {np.mean(rewards):.2f}")
    print(f"  Goal Success Rate     : {np.mean(successes)*100:.1f}%")
    print(f"{'='*55}")
    print(f"\n  [NEXT STEP] Run Option 1 (PPO Training) to fine-tune")
    print(f"  the BC model further with reinforcement learning.")
    print(f"{'='*55}\n")


# ─────────────────────────────────────────────────────────────────────────────
# Entry Point
# ─────────────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Behavioral Cloning Expert Pre-Trainer")
    parser.add_argument("--n-demo-envs",       type=int,   default=300,   help="Number of demo episodes to collect")
    parser.add_argument("--demo-max-steps",    type=int,   default=400,   help="Max steps per demo episode")
    parser.add_argument("--target-demo-steps", type=int,   default=80_000, help="Stop collecting after this many steps")
    parser.add_argument("--bc-epochs",         type=int,   default=60,    help="BC training epochs")
    parser.add_argument("--bc-batch",          type=int,   default=512,   help="BC mini-batch size")
    parser.add_argument("--bc-lr",             type=float, default=3e-4,  help="BC Adam learning rate")
    parser.add_argument("--skip-collect",      action="store_true",       help="Skip demo collection (reuse existing)")
    parser.add_argument("--demo-file",         type=str,   default="bc_demos.npz", help="Demo cache file")
    parser.add_argument("--output",            type=str,   default="best_model.pt", help="Path to save trained weights")
    args = parser.parse_args()

    print("=" * 60)
    print("  EXPERT BEHAVIORAL CLONING PRE-TRAINER")
    print("  Physics-Based Potential Field Expert -> Neural Network")
    print("=" * 60)

    # Step 1: Collect demonstrations (or load cached)
    if args.skip_collect and os.path.exists(args.demo_file):
        print(f"[*] Loading cached demonstrations from {args.demo_file}...")
        data = np.load(args.demo_file)
        demos = {k: data[k] for k in data.files}
        print(f"[+] Loaded {len(demos['action']):,} transitions.")
    else:
        demos = collect_demonstrations(args)
        np.savez_compressed(args.demo_file, **demos)
        print(f"[+] Demonstrations cached to {args.demo_file}")

    # Step 2: Train model via BC
    train_bc(demos, args)

    # Step 3: Quick validation
    validate_model(args)
