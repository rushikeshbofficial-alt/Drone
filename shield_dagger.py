"""
shield_dagger.py - Stop, Hover & Re-Route (SHR) Policy Distillation via DAgger
-------------------------------------------------------------------------------
Tier 2 Policy Distillation Engine for Autonomous Drone Navigation.

Implements DAgger (Dataset Aggregation) to distill the safety behaviors of the
Stop, Hover & Re-Route (SHR) safety shield and privileged potential field expert
into the PhysicsInformedActorCritic neural network policy.

Key Components:
1. Rollout with Decaying Mixing Parameter Beta:
   Executes a_exec = beta * a_supervisor + (1 - beta) * a_learner in the environment
   with the SHR Safety Shield active as a protective guardian.
2. Fused Privileged Supervisor:
   At every visited state, records the learner's observation (visual 5x84x84 and velocity 3D)
   and a supervisor label:
   - When shield intervenes (info["intervened"] == True): label is shield's executed action
     (active brake, reroute deflection, or governed velocity).
   - Otherwise: label is expert_action(env) from pretrain_bc.py.
   - NEVER records the learner's unguided action.
3. Critical Recovery State Rebalancing & Dataset Aggregation:
   Tags recovery states (interventions, clearances < 1.0m, or non-nominal shield states)
   and rebalances the dataset to maintain a balanced share (~40%) of critical recovery states,
   anchored by clean expert goal-directed navigation demonstrations.
   Aggregates with original bc_demos.npz and saves bc_demos_dagger_v1.npz.
4. Behavioral Cloning Fine-Tuning:
   Supervised MSE training with Adam, Cosine Annealing, and Mixed Precision (AMP FP16).
5. Validation-Driven Model Selection on Tuning Seeds (2000-2029):
   After each round, evaluates candidate model with SHIELD OFF on tuning seeds.
   Selects checkpoint with lowest collision rate and highest success rate,
   saving to best_model_dagger_v1.pt.
6. Compute Lock Coordination:
   Enforces .compute.lock throughout simulation and training.
"""

import os
import sys
import time
import math
import random
import shutil
import argparse
import gc
from typing import Dict, List, Optional, Tuple, Any

import numpy as np

# Ensure PyTorch is available
try:
    import torch
    import torch.nn as nn
    import torch.optim as optim
    from torch.utils.data import TensorDataset, DataLoader
    TORCH_AVAILABLE = True
except (ImportError, OSError):
    TORCH_AVAILABLE = False

from environment import IndoorDroneNavEnv
from model import PhysicsInformedActorCritic
from drone_shield import StopAndRerouteShield, ShieldState
from pretrain_bc import expert_action
from eval_shield import (
    acquire_compute_lock,
    evaluate_configuration,
    format_rate_with_ci,
    wilson_score_interval,
    parse_seeds,
)


# ─────────────────────────────────────────────────────────────────────────────
# 1. Rollout Collection with Fused Supervisor & Guardian Shield
# ─────────────────────────────────────────────────────────────────────────────

def collect_dagger_rollouts(
    model: nn.Module,
    seeds: List[int],
    beta: float,
    device: str,
    max_steps: int = 500,
    shield_mode: str = "oracle",
    shield_kwargs: Optional[Dict[str, Any]] = None,
) -> Tuple[List[Dict[str, Any]], Dict[str, Any]]:
    """
    Rolls out learner policy with mixing parameter beta on procedural seeds.
    Executes mixed action a_mix = beta * a_supervisor + (1 - beta) * a_learner.
    Safety shield wraps the environment to prevent crashes and provide intervention labels.
    
    Returns:
        transitions: list of dicts with keys ('visual', 'velocity', 'action', 'is_recovery')
        stats: rollout statistics (steps, interventions, outcomes)
    """
    shield_kwargs = shield_kwargs or {}
    model.eval()

    transitions = []
    total_steps = 0
    total_interventions = 0
    recovery_count = 0
    nominal_count = 0
    outcomes = {"SUCCESS": 0, "OBSTACLE_COLLISION": 0, "WALL_OOB": 0, "TIMEOUT": 0}

    # Cap max steps per rollout episode to avoid thousands of repetitive hovering frames
    effective_max_steps = min(max_steps, 250)

    t0 = time.time()
    print(f"\n[*] Collecting DAgger Rollouts: {len(seeds)} episodes | Beta={beta:.2f} | Shield={shield_mode.upper()}")

    for idx, seed in enumerate(seeds):
        raw_env = IndoorDroneNavEnv(gui=False, seed=seed, max_steps=effective_max_steps)
        env = StopAndRerouteShield(
            raw_env,
            sensor_mode=shield_mode,
            enabled=True,
            **shield_kwargs,
        )

        obs, info = env.reset(seed=seed)
        ep_steps = 0
        ep_interventions = 0
        ep_reward = 0.0
        consecutive_recovery = 0

        for _ in range(effective_max_steps):
            vis_cur = obs["visual"]
            vel_cur = obs["velocity"]

            # Compute privileged expert action from potential field
            a_expert = expert_action(env)

            # Compute learner policy action
            if beta < 0.999:
                vis_t = torch.tensor(vis_cur, dtype=torch.float32, device=device).unsqueeze(0)
                vel_t = torch.tensor(vel_cur, dtype=torch.float32, device=device).unsqueeze(0)
                with torch.no_grad():
                    a_learner = model(vis_t, vel_t).squeeze(0).cpu().numpy()
            else:
                a_learner = a_expert.copy()

            # Mixed action for execution
            a_mix = beta * a_expert + (1.0 - beta) * a_learner
            a_mix = np.clip(a_mix, -1.0, 1.0).astype(np.float32)

            # Step in shielded environment
            next_obs, reward, terminated, truncated, info = env.step(a_mix)
            ep_steps += 1
            total_steps += 1
            ep_reward += reward

            # Fused privileged supervisor label:
            # If shield intervened, label is shield's executed action;
            # otherwise, label is expert action. NEVER learner's unguided action!
            intervened = bool(info.get("intervened", False))
            if intervened:
                supervisor_label = np.asarray(info["executed_action"], dtype=np.float32).copy()
                ep_interventions += 1
                total_interventions += 1
            else:
                supervisor_label = np.asarray(a_expert, dtype=np.float32).copy()

            # Identify critical recovery state:
            # - Shield intervened (brake, reroute, speed governor)
            # - Clearance to nearest obstacle/wall < 1.0 m
            # - FSM state is non-nominal (BRAKE, SCAN, REROUTE, RETREAT)
            # - Time-to-contact < 1.2 s
            clearance = float(info.get("clearance", 10.0))
            fsm_state = str(info.get("shield_state", "NOMINAL"))
            ttc = float(info.get("ttc", float("inf")))

            is_recovery = bool(
                intervened
                or clearance < 1.0
                or fsm_state not in ("NOMINAL", "DISABLED")
                or ttc < 1.2
            )

            if is_recovery:
                recovery_count += 1
                consecutive_recovery += 1
            else:
                nominal_count += 1
                consecutive_recovery = 0

            transitions.append({
                "visual": vis_cur,
                "velocity": vel_cur,
                "action": supervisor_label,
                "is_recovery": is_recovery,
            })

            obs = next_obs
            if terminated or truncated or consecutive_recovery > 50:
                outcome = "TIMEOUT"
                if terminated:
                    if info.get("goal_reached", False):
                        outcome = "SUCCESS"
                    elif info.get("wall_collision", False):
                        outcome = "WALL_OOB"
                    else:
                        outcome = "OBSTACLE_COLLISION"
                outcomes[outcome] += 1
                break

        env.close()

        if (idx + 1) % 5 == 0 or (idx + 1) == len(seeds):
            interv_pct = (ep_interventions / max(1, ep_steps)) * 100.0
            print(
                f"  [{idx+1:2d}/{len(seeds):2d}] Seed {seed:4d} | {outcome:18s} | "
                f"Steps: {ep_steps:3d} | Interv: {interv_pct:4.1f}% | "
                f"Recovery Transitions: {recovery_count}/{total_steps} ({(recovery_count/max(1, total_steps))*100:.1f}%)"
            )

    elapsed = time.time() - t0
    stats = {
        "episodes": len(seeds),
        "total_steps": total_steps,
        "total_interventions": total_interventions,
        "recovery_transitions": recovery_count,
        "nominal_transitions": nominal_count,
        "recovery_share_pct": (recovery_count / max(1, total_steps)) * 100.0,
        "outcomes": outcomes,
        "duration_sec": round(elapsed, 2),
    }
    print(f"[+] Rollout collection complete in {elapsed:.1f}s: {total_steps} steps collected "
          f"({recovery_count} recovery, {nominal_count} nominal | {stats['recovery_share_pct']:.1f}% recovery share)")
    return transitions, stats


# ─────────────────────────────────────────────────────────────────────────────
# 2. Critical Recovery State Rebalancing & Dataset Aggregation
# ─────────────────────────────────────────────────────────────────────────────

def balance_and_aggregate_dataset(
    collected_transitions: List[Dict[str, Any]],
    base_demo_path: str = "bc_demos.npz",
    target_recovery_share: float = 0.40,
    save_path: str = "bc_demos_dagger_v1.npz",
    anchor_samples: int = 3500,
) -> Dict[str, np.ndarray]:
    """
    Aggregates newly collected DAgger transitions with base demonstration data.
    Rebalances the dataset so critical recovery states represent a balanced share
    (default: ~40%), anchored by clean expert goal-seeking demonstrations.
    Saves the aggregated dataset to bc_demos_dagger_v1.npz.
    """
    print(f"\n[*] Rebalancing and aggregating dataset (Target recovery share: {target_recovery_share*100:.0f}%)...")

    recovery_transitions = [t for t in collected_transitions if t["is_recovery"]]
    nominal_transitions = [t for t in collected_transitions if not t["is_recovery"]]

    n_rec = len(recovery_transitions)
    n_nom = len(nominal_transitions)
    print(f"[*] Raw collected transitions: {len(collected_transitions):,} (Recovery: {n_rec:,}, Nominal: {n_nom:,})")

    # Load original base demonstrations
    base_vis, base_vel, base_act = [], [], []
    if os.path.exists(base_demo_path):
        print(f"[*] Loading original base demonstrations from '{base_demo_path}'...")
        base_data = np.load(base_demo_path)
        base_vis.append(base_data["visual"])
        base_vel.append(base_data["velocity"])
        base_act.append(base_data["action"])
        print(f"[+] Loaded {len(base_data['action']):,} transitions from '{base_demo_path}'.")

    # Also load clean goal-seeking demonstrations from bc_demos_25k.npz if present
    # to anchor forward goal navigation and prevent hover/wall-drift
    if os.path.exists("bc_demos_25k.npz") and anchor_samples > 0:
        print("[*] Loading expert forward-navigation transitions from 'bc_demos_25k.npz'...")
        d25 = np.load("bc_demos_25k.npz")
        n_sub = min(anchor_samples, len(d25["action"]))
        rng = np.random.RandomState(42)
        indices = rng.choice(len(d25["action"]), size=n_sub, replace=False)
        base_vis.append(d25["visual"][indices])
        base_vel.append(d25["velocity"][indices])
        base_act.append(d25["action"][indices])
        print(f"[+] Anchored with {n_sub:,} clean expert forward-flight transitions.")

    # Stack base transitions
    if base_vis:
        anchor_vis = np.concatenate(base_vis, axis=0)
        anchor_vel = np.concatenate(base_vel, axis=0)
        anchor_act = np.concatenate(base_act, axis=0)
    else:
        anchor_vis = np.zeros((0, 5, 84, 84), dtype=np.float32)
        anchor_vel = np.zeros((0, 3), dtype=np.float32)
        anchor_act = np.zeros((0, 4), dtype=np.float32)

    n_anchor = len(anchor_act)

    # Rebalance recovery transitions to reach target recovery share
    # Total nominal pool = n_nom + n_anchor
    total_nominal = n_nom + n_anchor
    desired_recovery = int(math.ceil((target_recovery_share / max(0.01, 1.0 - target_recovery_share)) * total_nominal))

    if n_rec > 0:
        multiplier = max(1, int(round(desired_recovery / n_rec)))
        multiplier = min(multiplier, 5)  # Cap multiplier to prevent extreme oversampling
        print(f"[*] Recovery oversampling multiplier: {multiplier}x (expanding {n_rec:,} -> {n_rec * multiplier:,})")

        rec_vis = np.stack([t["visual"] for t in recovery_transitions], axis=0)
        rec_vel = np.stack([t["velocity"] for t in recovery_transitions], axis=0)
        rec_act = np.stack([t["action"] for t in recovery_transitions], axis=0)

        # Tile recovery
        rec_vis_tiled = np.tile(rec_vis, (multiplier, 1, 1, 1))
        rec_vel_tiled = np.tile(rec_vel, (multiplier, 1))
        rec_act_tiled = np.tile(rec_act, (multiplier, 1))
    else:
        rec_vis_tiled = np.zeros((0, 5, 84, 84), dtype=np.float32)
        rec_vel_tiled = np.zeros((0, 3), dtype=np.float32)
        rec_act_tiled = np.zeros((0, 4), dtype=np.float32)

    # Nominal transitions from DAgger rollouts
    if n_nom > 0:
        nom_vis = np.stack([t["visual"] for t in nominal_transitions], axis=0)
        nom_vel = np.stack([t["velocity"] for t in nominal_transitions], axis=0)
        nom_act = np.stack([t["action"] for t in nominal_transitions], axis=0)
    else:
        nom_vis = np.zeros((0, 5, 84, 84), dtype=np.float32)
        nom_vel = np.zeros((0, 3), dtype=np.float32)
        nom_act = np.zeros((0, 4), dtype=np.float32)

    # Concatenate all components
    parts_vis = [p for p in (anchor_vis, nom_vis, rec_vis_tiled) if len(p) > 0]
    parts_vel = [p for p in (anchor_vel, nom_vel, rec_vel_tiled) if len(p) > 0]
    parts_act = [p for p in (anchor_act, nom_act, rec_act_tiled) if len(p) > 0]

    all_vis = np.concatenate(parts_vis, axis=0).astype(np.float32)
    all_vel = np.concatenate(parts_vel, axis=0).astype(np.float32)
    all_act = np.concatenate(parts_act, axis=0).astype(np.float32)

    total_transitions = len(all_act)
    actual_recovery_share = (len(rec_act_tiled) / max(1, total_transitions)) * 100.0

    print(f"[+] Final aggregated dataset size: {total_transitions:,} transitions "
          f"({len(rec_act_tiled):,} recovery [{actual_recovery_share:.1f}%], {total_nominal:,} nominal)")
    print(f"    - Visual array shape:   {all_vis.shape}")
    print(f"    - Velocity array shape: {all_vel.shape}")
    print(f"    - Action array shape:   {all_act.shape}")

    dataset_dict = {
        "visual": all_vis,
        "velocity": all_vel,
        "action": all_act,
    }

    # Save to disk
    print(f"[*] Saving compressed dataset archive to '{save_path}'...")
    np.savez_compressed(save_path, **dataset_dict)
    file_size_mb = os.path.getsize(save_path) / (1024 * 1024)
    print(f"[+] Saved '{save_path}' successfully ({file_size_mb:.2f} MB).")

    return dataset_dict


# ─────────────────────────────────────────────────────────────────────────────
# 3. Behavioral Cloning Policy Fine-Tuning
# ─────────────────────────────────────────────────────────────────────────────

def train_bc_model(
    demos: Dict[str, np.ndarray],
    init_checkpoint: str,
    device: str,
    epochs: int = 20,
    batch_size: int = 256,
    lr: float = 1.5e-4,
    weight_decay: float = 1e-5,
) -> nn.Module:
    """
    Trains / fine-tunes PhysicsInformedActorCritic model on aggregated DAgger demonstrations
    using supervised MSE loss on action predictions.
    """
    print(f"\n[*] Training Distilled Policy via Behavioral Cloning (Epochs: {epochs}, Batch: {batch_size}, LR: {lr:.2e})...")

    model = PhysicsInformedActorCritic().to(device)
    if os.path.exists(init_checkpoint):
        print(f"[*] Initializing model weights from checkpoint: '{init_checkpoint}'")
        state_dict = torch.load(init_checkpoint, map_location=device, weights_only=True)
        model.load_state_dict(state_dict)
    else:
        print(f"[*] Checkpoint '{init_checkpoint}' not found. Training from scratch.")

    if device == "cuda":
        torch.backends.cudnn.benchmark = True

    # Build PyTorch Dataset and DataLoader
    vis_tensor = torch.tensor(demos["visual"], dtype=torch.float32)
    vel_tensor = torch.tensor(demos["velocity"], dtype=torch.float32)
    act_tensor = torch.tensor(demos["action"], dtype=torch.float32)

    dataset = TensorDataset(vis_tensor, vel_tensor, act_tensor)
    loader = DataLoader(
        dataset,
        batch_size=batch_size,
        shuffle=True,
        drop_last=False,
        pin_memory=(device == "cuda"),
    )

    optimizer = optim.Adam(model.parameters(), lr=lr, weight_decay=weight_decay)
    scheduler = optim.lr_scheduler.CosineAnnealingLR(optimizer, T_max=epochs, eta_min=1e-5)
    scaler = torch.amp.GradScaler("cuda") if device == "cuda" else None

    t_start = time.time()
    for epoch in range(epochs):
        model.train()
        epoch_losses = []

        for b_vis, b_vel, b_act in loader:
            b_vis = b_vis.to(device, non_blocking=True)
            b_vel = b_vel.to(device, non_blocking=True)
            b_act = b_act.to(device, non_blocking=True)

            optimizer.zero_grad(set_to_none=True)

            if scaler is not None:
                with torch.amp.autocast("cuda"):
                    pred = model(b_vis, b_vel)
                    loss = nn.functional.mse_loss(pred, b_act)
                scaler.scale(loss).backward()
                scaler.unscale_(optimizer)
                torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)
                scaler.step(optimizer)
                scaler.update()
            else:
                pred = model(b_vis, b_vel)
                loss = nn.functional.mse_loss(pred, b_act)
                loss.backward()
                torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)
                optimizer.step()

            epoch_losses.append(loss.item())

        scheduler.step()
        mean_loss = float(np.mean(epoch_losses))

        if (epoch + 1) % 5 == 0 or epoch == 0 or (epoch + 1) == epochs:
            cur_lr = scheduler.get_last_lr()[0]
            print(f"  Epoch [{epoch+1:>2}/{epochs}] | MSE Action Loss: {mean_loss:.6f} | LR: {cur_lr:.2e}")

    elapsed = time.time() - t_start
    print(f"[+] Training completed in {elapsed:.1f}s | Final MSE Loss: {mean_loss:.6f}")
    return model


# ─────────────────────────────────────────────────────────────────────────────
# 4. Tuning Validation (Shield OFF) & Model Selection
# ─────────────────────────────────────────────────────────────────────────────

def validate_on_tuning_seeds(
    model: nn.Module,
    val_seeds: List[int],
    tmp_ckpt_path: str = "temp_candidate.pt",
) -> Dict[str, Any]:
    """
    Evaluates candidate model on tuning seeds (2000-2029) with Shield OFF.
    Returns evaluation summary dict.
    """
    torch.save(model.state_dict(), tmp_ckpt_path)
    summary = evaluate_configuration(
        seeds=val_seeds,
        checkpoint_path=tmp_ckpt_path,
        shield_enabled=False,
        config_name="Candidate Validation (Shield OFF)",
        max_steps=500,
    )
    if os.path.exists(tmp_ckpt_path):
        try:
            os.remove(tmp_ckpt_path)
        except OSError:
            pass
    return summary


# ─────────────────────────────────────────────────────────────────────────────
# 5. Master DAgger Pipeline Execution
# ─────────────────────────────────────────────────────────────────────────────

def run_dagger_pipeline(args):
    """
    Orchestrates multi-round DAgger policy distillation.
    """
    device = "cuda" if (TORCH_AVAILABLE and torch.cuda.is_available()) else "cpu"
    print("=" * 75)
    print("  STOP, HOVER & RE-ROUTE (SHR) POLICY DISTILLATION PIPELINE (DAGGER)")
    print(f"  Device: {device} | Rounds: {args.rounds} | Ep/Round: {args.episodes_per_round}")
    print(f"  Base Demo: {args.base_demos} | Output Model: {args.output_model}")
    print("=" * 75)

    if not TORCH_AVAILABLE:
        print("[!] PyTorch is not available. Cannot execute DAgger training.")
        sys.exit(1)

    # Parse seed specifications
    val_seeds = parse_seeds(args.val_seeds)
    print(f"[*] Validation Tuning Seeds: {len(val_seeds)} seeds ({val_seeds[0]}-{val_seeds[-1]})")

    # Procedural rollout seed allocations per round
    # Must be disjoint from tuning seeds (2000-2029) and held-out seeds (1000-1049)
    rollout_seed_pools = []
    base_seed = args.rollout_seed_start
    for r in range(args.rounds):
        s_start = base_seed + r * args.episodes_per_round
        s_end = s_start + args.episodes_per_round
        seeds_r = list(range(s_start, s_end))
        rollout_seed_pools.append(seeds_r)
        print(f"  Round {r+1}: Seeds {s_start}-{s_end-1} ({len(seeds_r)} episodes)")

    # Beta schedule: decaying from initial beta down to 0.0
    if args.rounds > 1:
        betas = [
            max(0.0, args.beta_start - r * (args.beta_start / (args.rounds - 1)))
            for r in range(args.rounds)
        ]
    else:
        betas = [args.beta_start]
    print(f"[*] Mixing Beta Schedule: {[round(b, 2) for b in betas]}")

    # Initialize current learner model
    current_model = PhysicsInformedActorCritic().to(device)
    if os.path.exists(args.init_model):
        print(f"[*] Loading initial model from '{args.init_model}'...")
        current_model.load_state_dict(torch.load(args.init_model, map_location=device, weights_only=True))
    else:
        print(f"[!] Warning: Initial model '{args.init_model}' not found. Starting from scratch.")

    all_transitions = []
    best_collision_rate = 100.0
    best_success_rate = 0.0
    best_reward = -float("inf")
    round_summaries = []

    with acquire_compute_lock(worker_id="a5_distillation_1"):
        # Initial baseline evaluation on tuning seeds before distillation
        print("\n" + "=" * 70)
        print("PRE-DISTILLATION BASELINE EVALUATION ON TUNING SEEDS (SHIELD OFF)")
        print("=" * 70)
        base_summary = validate_on_tuning_seeds(current_model, val_seeds, tmp_ckpt_path="temp_init.pt")
        base_tot_col = base_summary["rates"]["TOTAL_COLLISION"]["rate"]
        base_succ = base_summary["rates"]["SUCCESS"]["rate"]
        base_rew = base_summary["statistics"]["mean_reward"]
        print(f"[+] Initial Baseline: Success={base_succ:.1f}% | Total Collision={base_tot_col:.1f}% | Mean Reward={base_rew:.2f}")

        # Always copy the initial baseline model to output_model first as safety fallback
        if not os.path.exists(args.output_model) and os.path.exists(args.init_model):
            shutil.copyfile(args.init_model, args.output_model)
            print(f"[*] Seeded initial '{args.output_model}' from '{args.init_model}'")

        # Best metrics tracker initialized to baseline
        best_collision_rate = base_tot_col
        best_success_rate = base_succ
        best_reward = base_rew

        # Execute DAgger Rounds
        for round_idx in range(args.rounds):
            round_num = round_idx + 1
            beta = betas[round_idx]
            seeds_r = rollout_seed_pools[round_idx]

            print("\n" + "#" * 70)
            print(f"# DAGGER ROUND [{round_num}/{args.rounds}] | Beta = {beta:.2f} | Seeds: {seeds_r[0]}-{seeds_r[-1]}")
            print("#" * 70)

            # Step 1: Collect rollouts with current model and decaying beta
            shield_kw = {"v_reroute": args.v_reroute}
            r_transitions, r_stats = collect_dagger_rollouts(
                model=current_model,
                seeds=seeds_r,
                beta=beta,
                device=device,
                max_steps=args.max_steps,
                shield_mode=args.shield_mode,
                shield_kwargs=shield_kw,
            )
            all_transitions.extend(r_transitions)

            # Step 2: Rebalance and aggregate dataset
            dataset_dict = balance_and_aggregate_dataset(
                collected_transitions=all_transitions,
                base_demo_path=args.base_demos,
                target_recovery_share=args.recovery_share,
                save_path=args.output_demos,
                anchor_samples=args.anchor_samples,
            )

            # Free up intermediate rollout memory
            gc.collect()

            # Step 3: Train / fine-tune policy network via BC
            trained_model = train_bc_model(
                demos=dataset_dict,
                init_checkpoint=args.init_model if round_idx == 0 else args.output_model,
                device=device,
                epochs=args.bc_epochs,
                batch_size=args.bc_batch,
                lr=args.bc_lr,
            )

            # Step 4: Evaluate candidate model on tuning seeds (Shield OFF)
            print(f"\n[*] Evaluating Round {round_num} candidate policy on tuning seeds (Shield OFF)...")
            eval_summary = validate_on_tuning_seeds(
                model=trained_model,
                val_seeds=val_seeds,
                tmp_ckpt_path=f"temp_candidate_round_{round_num}.pt",
            )

            cand_col = eval_summary["rates"]["TOTAL_COLLISION"]["rate"]
            cand_succ = eval_summary["rates"]["SUCCESS"]["rate"]
            cand_rew = eval_summary["statistics"]["mean_reward"]

            print(f"\n----------------------------------------------------------------------")
            print(f"ROUND {round_num} TUNING RESULTS (SHIELD OFF):")
            print(f"  Success Rate   : {cand_succ:5.1f}% (Previous best: {best_success_rate:5.1f}%)")
            print(f"  Collision Rate : {cand_col:5.1f}% (Previous best: {best_collision_rate:5.1f}%)")
            print(f"  Mean Reward    : {cand_rew:6.2f} (Previous best: {best_reward:6.2f})")
            print(f"----------------------------------------------------------------------")

            # Strict Model Selection Rule:
            # Candidate ONLY accepted if strictly lower collision rate,
            # or equal collisions with higher success rate,
            # or equal collisions and success with significant reward improvement (+15.0).
            is_better = (cand_col < best_collision_rate) or (
                math.isclose(cand_col, best_collision_rate, abs_tol=1e-5) and (cand_succ > best_success_rate)
            ) or (
                math.isclose(cand_col, best_collision_rate, abs_tol=1e-5)
                and math.isclose(cand_succ, best_success_rate, abs_tol=1e-5)
                and (cand_rew > best_reward + 15.0)
            )

            if is_better:
                print(f"[+] >>> NEW BEST MODEL FOUND! Updating '{args.output_model}' <<<")
                torch.save(trained_model.state_dict(), args.output_model)
                best_collision_rate = cand_col
                best_success_rate = cand_succ
                best_reward = cand_rew
                current_model = trained_model
            else:
                print(f"[-] Candidate did not improve over best ({best_collision_rate:.1f}% col, {best_success_rate:.1f}% succ). Retaining current best.")
                # Reload current best model for next round rollouts
                if os.path.exists(args.output_model):
                    current_model.load_state_dict(torch.load(args.output_model, map_location=device, weights_only=True))

            round_summaries.append({
                "round": round_num,
                "beta": beta,
                "rollout_seeds": f"{seeds_r[0]}-{seeds_r[-1]}",
                "rollout_stats": r_stats,
                "tuning_metrics": {
                    "success_rate": cand_succ,
                    "collision_rate": cand_col,
                    "mean_reward": cand_rew,
                },
                "is_best": is_better,
            })

        print("\n" + "=" * 70)
        print("DAGGER DISTILLATION PIPELINE COMPLETE!")
        print(f"Best Tuning Collision Rate: {best_collision_rate:.1f}%")
        print(f"Best Tuning Success Rate:   {best_success_rate:.1f}%")
        print(f"Best Model Checkpoint:      {args.output_model}")
        print(f"Aggregated Dataset:         {args.output_demos}")
        print("=" * 70)


# ─────────────────────────────────────────────────────────────────────────────
# 6. Command Line Entry Point
# ─────────────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="Stop, Hover & Re-Route (SHR) Policy Distillation via DAgger")
    parser.add_argument("--rounds", type=int, default=4, help="Number of DAgger iterations/rounds")
    parser.add_argument("--episodes-per-round", type=int, default=30, help="Episodes per DAgger round")
    parser.add_argument("--rollout-seed-start", type=int, default=3000, help="Starting seed for DAgger rollouts")
    parser.add_argument("--beta-start", type=float, default=0.70, help="Initial mixing parameter beta")
    parser.add_argument("--shield-mode", type=str, default="oracle", choices=["oracle", "camera"],
                        help="Shield sensor mode during rollouts")
    parser.add_argument("--v-reroute", type=float, default=0.85, help="Shield lateral reroute speed (m/s) during rollouts")
    parser.add_argument("--base-demos", type=str, default="bc_demos.npz", help="Original demo dataset to aggregate")
    parser.add_argument("--anchor-samples", type=int, default=5000, help="Clean expert goal navigation transitions to anchor")
    parser.add_argument("--recovery-share", type=float, default=0.35, help="Target fraction of recovery transitions")
    parser.add_argument("--bc-epochs", type=int, default=20, help="BC training epochs per round")
    parser.add_argument("--bc-batch", type=int, default=256, help="BC mini-batch size")
    parser.add_argument("--bc-lr", type=float, default=1.0e-4, help="BC Adam learning rate")
    parser.add_argument("--max-steps", type=int, default=500, help="Max steps per rollout episode")
    parser.add_argument("--val-seeds", type=str, default="tuning", help="Tuning seeds for model validation")
    parser.add_argument("--init-model", type=str, default="best_model.pt", help="Initial checkpoint for distillation")
    parser.add_argument("--output-model", type=str, default="best_model_dagger_v1.pt", help="Path to save best distilled model")
    parser.add_argument("--output-demos", type=str, default="bc_demos_dagger_v1.npz", help="Path to save aggregated dataset")
    parser.add_argument("--smoke-test", action="store_true", default=False, help="Fast smoke test configuration")

    args = parser.parse_args()

    if args.smoke_test:
        print("[!] Running in FAST SMOKE TEST mode...")
        args.rounds = 2
        args.episodes_per_round = 3
        args.bc_epochs = 3
        args.anchor_samples = 300
        args.val_seeds = "2000-2002"

    run_dagger_pipeline(args)


if __name__ == "__main__":
    main()
