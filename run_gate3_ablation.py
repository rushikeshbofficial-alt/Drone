"""
run_gate3_ablation.py - Per-Fix Ablation Study on 15 Former v1 Timeouts
------------------------------------------------------------------------
Evaluates the 15 timeout seeds from 4000-4059 under:
- Alone: anti_amnesia, forward_creep, guided_bypass, goal_proximity, oracle_planner
- Cumulative: +anti_amnesia -> +forward_creep -> +guided_bypass -> +goal_proximity -> +oracle_planner (full v2)

Enforces .compute.lock coordination.
"""

import os
import sys
import time
import json
import numpy as np
import torch

from environment import IndoorDroneNavEnv
from eval_shield import load_policy_model, run_single_episode, acquire_compute_lock
from drone_shield import StopAndRerouteShield

TIMEOUT_SEEDS = [4000, 4015, 4018, 4020, 4021, 4023, 4024, 4026, 4036, 4048, 4049, 4052, 4053, 4055, 4056]
CHECKPOINT = "best_model_baseline.pt"

def run_config(seeds, model, device, config_name, shield_kwargs):
    print(f"\n--- Running: {config_name} ({len(seeds)} episodes) ---")
    results = []
    for idx, s in enumerate(seeds):
        raw_env = IndoorDroneNavEnv(gui=False, seed=s, max_steps=500)
        env = StopAndRerouteShield(
            raw_env,
            sensor_mode="oracle",
            enabled=True,
            **shield_kwargs
        )
        ep = run_single_episode(
            env=env,
            model=model,
            device=device,
            seed=s,
            max_steps=500,
            shield_enabled=True
        )
        env.close()
        planner_steps = ep["state_counts"].get("PLANNER", 0)
        results.append({
            "seed": s,
            "outcome": ep["outcome"],
            "steps": ep["steps"],
            "planner_invoked": planner_steps > 0,
            "planner_steps": planner_steps,
            "reward": ep["reward"],
            "min_clearance": ep["min_clearance"],
        })
        print(f"[{idx+1:2d}/15] Seed {s:4d} | {ep['outcome']:18s} | Steps: {ep['steps']:3d} | Planner: {planner_steps > 0} ({planner_steps} steps)")
    
    success_count = sum(1 for r in results if r["outcome"] == "SUCCESS")
    timeout_count = sum(1 for r in results if r["outcome"] == "TIMEOUT")
    collision_count = sum(1 for r in results if "COLLISION" in r["outcome"] or "OOB" in r["outcome"])
    planner_count = sum(1 for r in results if r["planner_invoked"])
    
    return {
        "config_name": config_name,
        "shield_kwargs": shield_kwargs,
        "success_count": success_count,
        "timeout_count": timeout_count,
        "collision_count": collision_count,
        "planner_count": planner_count,
        "resolved_count": success_count,  # Since original v1 had 0/15 successes
        "episodes": results
    }

def main():
    device = "cuda" if torch.cuda.is_available() else "cpu"
    model = load_policy_model(CHECKPOINT, device)

    # Base v1 kwargs (all fixes False)
    base_v1 = {
        "shield_version": "v1",
        "anti_amnesia": False,
        "forward_creep": False,
        "guided_bypass": False,
        "goal_proximity": False,
        "oracle_planner": False,
    }

    configs = {}

    with acquire_compute_lock(worker_id="gate3_ablation"):
        print("Compute lock acquired. Starting ablation study...")

        # 0. v1 Baseline
        configs["v1_baseline"] = run_config(
            TIMEOUT_SEEDS, model, device,
            "SHR v1 (All 5 Fixes OFF)",
            {**base_v1}
        )

        # 1. Alone Fixes
        configs["alone_anti_amnesia"] = run_config(
            TIMEOUT_SEEDS, model, device,
            "Alone: Fix 1 (anti_amnesia)",
            {**base_v1, "anti_amnesia": True}
        )

        configs["alone_forward_creep"] = run_config(
            TIMEOUT_SEEDS, model, device,
            "Alone: Fix 2 (forward_creep)",
            {**base_v1, "forward_creep": True}
        )

        configs["alone_guided_bypass"] = run_config(
            TIMEOUT_SEEDS, model, device,
            "Alone: Fix 3 (guided_bypass)",
            {**base_v1, "guided_bypass": True}
        )

        configs["alone_goal_proximity"] = run_config(
            TIMEOUT_SEEDS, model, device,
            "Alone: Fix 4 (goal_proximity)",
            {**base_v1, "goal_proximity": True}
        )

        configs["alone_oracle_planner"] = run_config(
            TIMEOUT_SEEDS, model, device,
            "Alone: Fix 5 (oracle_planner)",
            {**base_v1, "oracle_planner": True}
        )

        # 2. Cumulative Fixes
        configs["cumul_1_anti_amnesia"] = run_config(
            TIMEOUT_SEEDS, model, device,
            "Cumulative 1: +anti_amnesia",
            {**base_v1, "anti_amnesia": True}
        )

        configs["cumul_2_forward_creep"] = run_config(
            TIMEOUT_SEEDS, model, device,
            "Cumulative 2: +anti_amnesia +forward_creep",
            {**base_v1, "anti_amnesia": True, "forward_creep": True}
        )

        configs["cumul_3_guided_bypass"] = run_config(
            TIMEOUT_SEEDS, model, device,
            "Cumulative 3: +anti_amnesia +forward_creep +guided_bypass",
            {**base_v1, "anti_amnesia": True, "forward_creep": True, "guided_bypass": True}
        )

        configs["cumul_4_goal_proximity"] = run_config(
            TIMEOUT_SEEDS, model, device,
            "Cumulative 4: +anti_amnesia +forward_creep +guided_bypass +goal_proximity",
            {**base_v1, "anti_amnesia": True, "forward_creep": True, "guided_bypass": True, "goal_proximity": True}
        )

        configs["cumul_5_full_v2"] = run_config(
            TIMEOUT_SEEDS, model, device,
            "Cumulative 5: Full v2 (+oracle_planner)",
            {**base_v1, "anti_amnesia": True, "forward_creep": True, "guided_bypass": True, "goal_proximity": True, "oracle_planner": True}
        )

    # Save summary
    os.makedirs("reports", exist_ok=True)
    out_file = "reports/gate3_ablation_results.json"
    with open(out_file, "w", encoding="utf-8") as f:
        json.dump(configs, f, indent=2)
    print(f"\n[+] Saved ablation results to {out_file}")

    # Print summary table
    print("\n" + "="*80)
    print("PER-FIX ABLATION SUMMARY ON 15 FORMER V1 TIMEOUTS")
    print("="*80)
    print(f"{'Configuration':50s} | {'Resolved':8s} | {'Timeouts':8s} | {'Collisions':10s} | {'Planner':8s}")
    print("-"*80)
    for k, v in configs.items():
        print(f"{v['config_name']:50s} | {v['resolved_count']:2d}/15     | {v['timeout_count']:2d}/15     | {v['collision_count']:2d}/15      | {v['planner_count']:2d}/15")
    print("="*80)

if __name__ == "__main__":
    main()
