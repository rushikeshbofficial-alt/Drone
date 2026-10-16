"""
eval_shield.py - Comprehensive Evaluation Harness & Crash Forensics Engine
--------------------------------------------------------------------------
Tier 1 Safety Shield Benchmark & Forensic Suite for Autonomous Drone Navigation.

Features:
1. Multi-mode evaluation: Baseline (Shield OFF), Shield ON (Oracle), Shield ON (Camera),
   or sequential side-by-side comparison (--compare).
2. Seed protocol support: Reference seeds [101, 202, 303, 404, 505], tuning seeds (2000-2029),
   custom ranges (e.g. 2000-2029) or comma-separated lists.
3. Outcome partitioning: SUCCESS | OBSTACLE_COLLISION | WALL_OOB | TIMEOUT.
4. Comprehensive metric collection:
   - Success, collision, and timeout rates with Wilson 95% Confidence Intervals.
   - Mean reward, min clearance, steps to goal.
   - Shield intervention count and percentage.
   - FSM state distribution (steps in NOMINAL, BRAKE, SCAN, REROUTE, RETREAT).
   - Stop latency (steps to ||v|| < 0.08 m/s after brake trigger).
   - Standoff distance at full stop.
   - Step-count overhead vs baseline on episodes where baseline succeeded.
5. Crash Forensics: 10-step trajectory and kinematics telemetry for all non-success episodes.
6. Report generation: Machine-readable JSON and human-readable Markdown in reports/.
7. Compute Lock coordination: Enforces .compute.lock during all runs.
"""

import os
import sys
import time
import math
import json
import argparse
from contextlib import contextmanager
from typing import Dict, List, Optional, Tuple, Any

import numpy as np

# Ensure PyTorch is available for policy evaluation
try:
    import torch
    TORCH_AVAILABLE = True
except (ImportError, OSError):
    TORCH_AVAILABLE = False

from environment import IndoorDroneNavEnv
from model import PhysicsInformedActorCritic
from drone_shield import StopAndRerouteShield, ShieldState


# ── Wilson Score Confidence Interval ─────────────────────────────────────────

def wilson_score_interval(k: int, n: int, confidence: float = 0.95) -> Tuple[float, float, float]:
    """
    Computes Wilson score 95% confidence interval for a binomial proportion.
    Returns: (point_estimate, lower_bound, upper_bound)
    """
    if n <= 0:
        return 0.0, 0.0, 0.0
    p_hat = float(k) / float(n)
    z = 1.959963984540054  # 95% two-sided normal quantile
    denom = 1.0 + (z * z) / float(n)
    center = (p_hat + (z * z) / (2.0 * float(n))) / denom
    variance_term = (p_hat * (1.0 - p_hat) / float(n)) + ((z * z) / (4.0 * float(n * n)))
    spread = (z / denom) * math.sqrt(max(0.0, variance_term))
    lower = max(0.0, center - spread)
    upper = min(1.0, center + spread)
    return p_hat, lower, upper


def format_rate_with_ci(k: int, n: int) -> str:
    """Formats rate with percentage and Wilson 95% CI."""
    p, lo, hi = wilson_score_interval(k, n)
    return f"{p * 100.0:5.1f}% [{lo * 100.0:4.1f}%, {hi * 100.0:4.1f}%] ({k}/{n})"


# ── Compute Lock Coordination ────────────────────────────────────────────────

def is_pid_running(pid: int) -> bool:
    try:
        import psutil
        return psutil.pid_exists(pid)
    except Exception:
        try:
            os.kill(pid, 0)
            return True
        except OSError:
            return False


@contextmanager
def acquire_compute_lock(lock_path: str = ".compute.lock", worker_id: str = "a3_benchmark_1", poll_interval: float = 1.0):
    """
    Enforces hardware compute lock coordination among workers.
    Waits if .compute.lock exists, detects and clears stale locks from terminated processes,
    writes worker ID and PID upon entry, and removes the lock in a finally block.
    """
    pid = os.getpid()
    waited = False
    while os.path.exists(lock_path):
        # Stale lock detection
        stale = False
        lock_pid = None
        try:
            with open(lock_path, "r", encoding="utf-8") as f:
                content = f.read().strip()
            parts = content.split()
            for p in parts:
                if p.isdigit():
                    lock_pid = int(p)
                    break
            if lock_pid is not None and not is_pid_running(lock_pid):
                stale = True
        except Exception:
            pass

        if stale:
            print(f"[!] Warning: Stale compute lock detected (PID {lock_pid} is not running). Removing stale lock '{lock_path}'.")
            try:
                os.remove(lock_path)
            except OSError:
                pass
            break

        if not waited:
            print(f"[*] Compute lock active at '{lock_path}'. Waiting for release...")
            waited = True
        time.sleep(poll_interval)

    if waited:
        print("[+] Compute lock released. Acquiring lock...")

    try:
        with open(lock_path, "w", encoding="utf-8") as f:
            f.write(f"{worker_id} {pid}\n")
        yield
    finally:
        if os.path.exists(lock_path):
            try:
                # Only remove if it belongs to us
                with open(lock_path, "r", encoding="utf-8") as f:
                    content = f.read().strip()
                if str(pid) in content or worker_id in content:
                    os.remove(lock_path)
            except OSError:
                pass


# ── Seed Parsing Helper ───────────────────────────────────────────────────────

def parse_seeds(seed_str: str) -> List[int]:
    """
    Parses seed string into a sorted list of unique integers.
    Supports:
      - 'reference': [101, 202, 303, 404, 505]
      - 'tuning': 2000-2029 (30 seeds)
      - '2000-2029': range
      - '101,202,303': comma-separated
    """
    s = seed_str.strip().lower()
    if s == "reference":
        return [101, 202, 303, 404, 505]
    if s == "tuning":
        return list(range(2000, 2030))

    seeds = set()
    parts = s.split(",")
    for part in parts:
        part = part.strip()
        if not part:
            continue
        if "-" in part:
            sub = part.split("-")
            if len(sub) == 2 and sub[0].isdigit() and sub[1].isdigit():
                start, end = int(sub[0]), int(sub[1])
                for val in range(start, end + 1):
                    seeds.add(val)
            else:
                raise ValueError(f"Invalid range in seed argument: {part}")
        elif part.isdigit():
            seeds.add(int(part))
        else:
            raise ValueError(f"Unrecognized seed specification: {part}")

    res = sorted(list(seeds))
    if not res:
        raise ValueError(f"No valid seeds parsed from: {seed_str}")
    return res


# ── Policy Loading ────────────────────────────────────────────────────────────

def load_policy_model(checkpoint_path: str, device: str) -> PhysicsInformedActorCritic:
    """Loads PhysicsInformedActorCritic neural network checkpoint."""
    model = PhysicsInformedActorCritic()
    if TORCH_AVAILABLE and hasattr(model, "to"):
        model.to(device)
        if os.path.exists(checkpoint_path):
            state_dict = torch.load(checkpoint_path, map_location=device, weights_only=True)
            model.load_state_dict(state_dict)
            print(f"[+] Loaded policy checkpoint from: {checkpoint_path}")
        else:
            print(f"[!] WARNING: Checkpoint '{checkpoint_path}' not found! Using initialized weights.")
        model.eval()
    return model


# ── Episode Rollout Engine ────────────────────────────────────────────────────

def run_single_episode(
    env: Any,
    model: Any,
    device: str,
    seed: int,
    max_steps: int = 500,
    shield_enabled: bool = False,
) -> Dict[str, Any]:
    """
    Executes a single evaluation episode with full telemetry logging and crash forensics.
    """
    obs, reset_info = env.reset(seed=seed)
    ep_reward = 0.0
    ep_min_clearance = float("inf")
    step_count = 0
    interventions_count = 0

    state_counts = {
        "NOMINAL": 0,
        "BRAKE": 0,
        "SCAN": 0,
        "REROUTE": 0,
        "RETREAT": 0,
        "DISABLED": 0,
    }

    standoff_recorded = 0.0
    stop_latency_max = 0

    step_telemetry: List[Dict[str, Any]] = []

    while True:
        # Pre-step state capture
        vis_obs = obs["visual"]
        vel_obs = obs["velocity"]

        # Policy forward pass
        if TORCH_AVAILABLE and hasattr(model, "to"):
            vis_t = torch.tensor(vis_obs, dtype=torch.float32, device=device).unsqueeze(0)
            vel_t = torch.tensor(vel_obs, dtype=torch.float32, device=device).unsqueeze(0)
            with torch.no_grad():
                action_mean = model(vis_t, vel_t).squeeze(0).cpu().numpy()
        else:
            action_mean = model.forward(vis_obs, vel_obs).flatten()

        # Step environment
        next_obs, reward, terminated, truncated, step_info = env.step(action_mean)
        ep_reward += float(reward)
        step_count += 1

        # Track clearance
        if "clearance" in step_info and step_info["clearance"] > 0:
            ep_min_clearance = min(ep_min_clearance, float(step_info["clearance"]))
        elif "min_depth" in step_info and step_info["min_depth"] is not None:
            ep_min_clearance = min(ep_min_clearance, float(step_info["min_depth"]))

        # Shield telemetry tracking
        shield_state = step_info.get("shield_state", "DISABLED" if not shield_enabled else "NOMINAL")
        state_counts[shield_state] = state_counts.get(shield_state, 0) + 1

        intervened = bool(step_info.get("intervened", False))
        if intervened:
            interventions_count += 1

        if step_info.get("standoff_distance", 0.0) > 0:
            standoff_recorded = max(standoff_recorded, float(step_info["standoff_distance"]))

        if step_info.get("stop_latency", 0) > stop_latency_max:
            stop_latency_max = int(step_info["stop_latency"])

        # Drone position and velocity
        drone_pos = getattr(env, "drone_pos", np.zeros(3))
        drone_vel = getattr(env, "drone_vel", np.zeros(3))

        # Forensic telemetry record
        step_rec = {
            "step": step_count,
            "pos": [round(float(x), 3) for x in drone_pos],
            "vel": [round(float(x), 3) for x in drone_vel],
            "speed": round(float(np.linalg.norm(drone_vel[:2])), 3),
            "clearance": round(float(step_info.get("clearance", step_info.get("min_depth", 0.0))), 3),
            "shield_state": shield_state,
            "policy_action": [round(float(x), 3) for x in step_info.get("policy_action", action_mean)],
            "executed_action": [round(float(x), 3) for x in step_info.get("executed_action", action_mean)],
            "intervened": intervened,
        }
        step_telemetry.append(step_rec)

        obs = next_obs

        if terminated or truncated:
            # Distinct outcome classification
            goal_reached = bool(step_info.get("goal_reached", False))
            collision = bool(step_info.get("collision", False))
            out_of_bounds = bool(step_info.get("out_of_bounds", getattr(env, "out_of_bounds", False)))

            # Coordinate check for wall out of bounds
            if abs(drone_pos[0]) >= 4.58 or abs(drone_pos[1]) >= 9.58 or drone_pos[2] <= 0.16 or drone_pos[2] >= 3.48:
                out_of_bounds = True

            if goal_reached:
                outcome = "SUCCESS"
            elif out_of_bounds:
                outcome = "WALL_OOB"
            elif collision:
                outcome = "OBSTACLE_COLLISION"
            else:
                outcome = "TIMEOUT"

            # Diagnose cause of failure for forensics
            cause_of_failure = "N/A - Goal reached successfully."
            if outcome == "OBSTACLE_COLLISION":
                last_spd = step_telemetry[-1]["speed"] if step_telemetry else 0.0
                last_clr = step_telemetry[-1]["clearance"] if step_telemetry else 0.0
                cause_of_failure = f"Obstacle collision at speed {last_spd:.2f} m/s (min clearance {last_clr:.2f}m)."
            elif outcome == "WALL_OOB":
                last_pos = step_telemetry[-1]["pos"] if step_telemetry else [0, 0, 0]
                cause_of_failure = f"Perimeter boundary excursion at pos [x={last_pos[0]:.2f}, y={last_pos[1]:.2f}, z={last_pos[2]:.2f}]."
            elif outcome == "TIMEOUT":
                cause_of_failure = f"Exceeded maximum episode limit ({max_steps} steps) without reaching goal."

            return {
                "seed": seed,
                "outcome": outcome,
                "steps": step_count,
                "reward": round(ep_reward, 2),
                "min_clearance": round(ep_min_clearance if ep_min_clearance != float("inf") else 0.0, 3),
                "interventions_count": interventions_count,
                "interventions_pct": round((interventions_count / max(1, step_count)) * 100.0, 1),
                "state_counts": state_counts,
                "stop_latency": stop_latency_max,
                "standoff_distance": round(standoff_recorded, 3),
                "cause_of_failure": cause_of_failure,
                "last_10_steps": step_telemetry[-10:],
            }


# ── Batch Evaluation Engine ───────────────────────────────────────────────────

def evaluate_configuration(
    seeds: List[int],
    checkpoint_path: str,
    shield_enabled: bool,
    sensor_mode: str = "oracle",
    shield_kwargs: Optional[Dict[str, Any]] = None,
    max_steps: int = 500,
    config_name: str = "Baseline",
) -> Dict[str, Any]:
    """
    Runs a batch of seeds under a specific shield configuration.
    """
    device = "cuda" if (TORCH_AVAILABLE and torch.cuda.is_available()) else "cpu"
    model = load_policy_model(checkpoint_path, device)
    shield_kwargs = shield_kwargs or {}

    print(f"\n{'='*70}")
    print(f"RUNNING CONFIGURATION: {config_name.upper()} ({len(seeds)} episodes)")
    print(f"Shield: {'ENABLED (' + sensor_mode + ')' if shield_enabled else 'DISABLED (Baseline)'}")
    print(f"Checkpoint: {checkpoint_path} | Device: {device}")
    print(f"{'='*70}")

    episodes = []
    outcomes_count = {"SUCCESS": 0, "OBSTACLE_COLLISION": 0, "WALL_OOB": 0, "TIMEOUT": 0}

    t0 = time.time()
    for idx, seed in enumerate(seeds):
        # Create fresh environment
        raw_env = IndoorDroneNavEnv(gui=False, seed=seed, max_steps=max_steps)

        if shield_enabled:
            env = StopAndRerouteShield(
                raw_env,
                sensor_mode=sensor_mode,
                enabled=True,
                **shield_kwargs,
            )
        else:
            env = raw_env

        ep_data = run_single_episode(
            env=env,
            model=model,
            device=device,
            seed=seed,
            max_steps=max_steps,
            shield_enabled=shield_enabled,
        )
        env.close()

        episodes.append(ep_data)
        outcomes_count[ep_data["outcome"]] += 1

        # Live terminal progress output
        print(
            f"[{idx+1:2d}/{len(seeds):2d}] Seed {seed:4d} | "
            f"{ep_data['outcome']:18s} | "
            f"Steps: {ep_data['steps']:3d} | "
            f"Rew: {ep_data['reward']:7.2f} | "
            f"MinClr: {ep_data['min_clearance']:4.2f}m | "
            f"Interv: {ep_data['interventions_pct']:4.1f}%"
        )

    duration = time.time() - t0
    n = len(seeds)

    # Compute rate CIs
    success_k = outcomes_count["SUCCESS"]
    obs_col_k = outcomes_count["OBSTACLE_COLLISION"]
    wall_oob_k = outcomes_count["WALL_OOB"]
    tot_col_k = obs_col_k + wall_oob_k
    timeout_k = outcomes_count["TIMEOUT"]

    p_succ, succ_lo, succ_hi = wilson_score_interval(success_k, n)
    p_obs, obs_lo, obs_hi = wilson_score_interval(obs_col_k, n)
    p_wall, wall_lo, wall_hi = wilson_score_interval(wall_oob_k, n)
    p_tot, tot_lo, tot_hi = wilson_score_interval(tot_col_k, n)
    p_time, time_lo, time_hi = wilson_score_interval(timeout_k, n)

    rewards = [ep["reward"] for ep in episodes]
    steps_list = [ep["steps"] for ep in episodes]
    clearances = [ep["min_clearance"] for ep in episodes]
    interv_pcts = [ep["interventions_pct"] for ep in episodes]
    standoffs = [ep["standoff_distance"] for ep in episodes if ep["standoff_distance"] > 0]
    latencies = [ep["stop_latency"] for ep in episodes if ep["stop_latency"] > 0]

    # Aggregate state counts
    agg_states = {"NOMINAL": 0, "BRAKE": 0, "SCAN": 0, "REROUTE": 0, "RETREAT": 0, "DISABLED": 0}
    total_steps_all = sum(steps_list)
    for ep in episodes:
        for st, cnt in ep["state_counts"].items():
            agg_states[st] = agg_states.get(st, 0) + cnt

    state_pcts = {st: round((cnt / max(1, total_steps_all)) * 100.0, 1) for st, cnt in agg_states.items()}

    summary = {
        "config_name": config_name,
        "shield_enabled": shield_enabled,
        "sensor_mode": sensor_mode,
        "shield_kwargs": shield_kwargs,
        "num_episodes": n,
        "duration_sec": round(duration, 2),
        "rates": {
            "SUCCESS": {
                "count": success_k,
                "rate": round(p_succ * 100.0, 2),
                "ci_95": [round(succ_lo * 100.0, 2), round(succ_hi * 100.0, 2)],
                "formatted": format_rate_with_ci(success_k, n),
            },
            "OBSTACLE_COLLISION": {
                "count": obs_col_k,
                "rate": round(p_obs * 100.0, 2),
                "ci_95": [round(obs_lo * 100.0, 2), round(obs_hi * 100.0, 2)],
                "formatted": format_rate_with_ci(obs_col_k, n),
            },
            "WALL_OOB": {
                "count": wall_oob_k,
                "rate": round(p_wall * 100.0, 2),
                "ci_95": [round(wall_lo * 100.0, 2), round(wall_hi * 100.0, 2)],
                "formatted": format_rate_with_ci(wall_oob_k, n),
            },
            "TOTAL_COLLISION": {
                "count": tot_col_k,
                "rate": round(p_tot * 100.0, 2),
                "ci_95": [round(tot_lo * 100.0, 2), round(tot_hi * 100.0, 2)],
                "formatted": format_rate_with_ci(tot_col_k, n),
            },
            "TIMEOUT": {
                "count": timeout_k,
                "rate": round(p_time * 100.0, 2),
                "ci_95": [round(time_lo * 100.0, 2), round(time_hi * 100.0, 2)],
                "formatted": format_rate_with_ci(timeout_k, n),
            },
        },
        "statistics": {
            "mean_reward": round(float(np.mean(rewards)), 2),
            "std_reward": round(float(np.std(rewards)), 2),
            "mean_steps": round(float(np.mean(steps_list)), 1),
            "std_steps": round(float(np.std(steps_list)), 1),
            "mean_min_clearance": round(float(np.mean(clearances)), 3),
            "std_min_clearance": round(float(np.std(clearances)), 3),
            "mean_interventions_pct": round(float(np.mean(interv_pcts)), 1),
            "mean_standoff_distance": round(float(np.mean(standoffs)), 3) if standoffs else 0.0,
            "mean_stop_latency": round(float(np.mean(latencies)), 2) if latencies else 0.0,
            "state_distribution_pct": state_pcts,
        },
        "episodes": episodes,
    }

    # Print summary block
    print(f"\n{'-'*70}")
    print(f"SUMMARY: {config_name}")
    print(f"  SUCCESS           : {summary['rates']['SUCCESS']['formatted']}")
    print(f"  OBSTACLE_COLLISION: {summary['rates']['OBSTACLE_COLLISION']['formatted']}")
    print(f"  WALL_OOB          : {summary['rates']['WALL_OOB']['formatted']}")
    print(f"  TOTAL_COLLISION   : {summary['rates']['TOTAL_COLLISION']['formatted']}")
    print(f"  TIMEOUT           : {summary['rates']['TIMEOUT']['formatted']}")
    print(f"  Mean Reward       : {summary['statistics']['mean_reward']:.2f} +/- {summary['statistics']['std_reward']:.2f}")
    print(f"  Mean Min Clearance: {summary['statistics']['mean_min_clearance']:.2f} m")
    print(f"  Mean Steps        : {summary['statistics']['mean_steps']:.1f}")
    print(f"{'-'*70}\n")

    return summary


# ── Overhead & Comparison Computation ────────────────────────────────────────

def compute_comparison_metrics(
    baseline_summary: Dict[str, Any],
    shield_summary: Dict[str, Any],
) -> Dict[str, Any]:
    """
    Computes comparative metrics between Baseline (Shield OFF) and Shield ON:
    - Step-count overhead on episodes where baseline succeeded.
    - Rate deltas.
    """
    base_episodes = {ep["seed"]: ep for ep in baseline_summary["episodes"]}
    shield_episodes = {ep["seed"]: ep for ep in shield_summary["episodes"]}

    overheads = []
    overhead_details = []

    for seed, base_ep in base_episodes.items():
        if base_ep["outcome"] == "SUCCESS" and seed in shield_episodes:
            sh_ep = shield_episodes[seed]
            base_steps = base_ep["steps"]
            sh_steps = sh_ep["steps"]
            oh_pct = ((sh_steps - base_steps) / float(base_steps)) * 100.0
            overheads.append(oh_pct)
            overhead_details.append({
                "seed": seed,
                "baseline_steps": base_steps,
                "shield_steps": sh_steps,
                "shield_outcome": sh_ep["outcome"],
                "overhead_pct": round(oh_pct, 2),
            })

    mean_overhead = round(float(np.mean(overheads)), 2) if overheads else 0.0
    std_overhead = round(float(np.std(overheads)), 2) if overheads else 0.0

    return {
        "baseline_success_count": len(overheads),
        "mean_step_overhead_pct": mean_overhead,
        "std_step_overhead_pct": std_overhead,
        "details": overhead_details,
    }


# ── Acceptance Criteria Checker ──────────────────────────────────────────────

def evaluate_acceptance_criteria(summary: Dict[str, Any], overhead_metrics: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    Verifies metrics against authoritative Acceptance Criteria:
    - Total collisions <= 2.0%
    - Success rate >= 85.0%
    - Timeout rate <= 5.0%
    - Standoff distance >= 0.45 m
    - Step overhead on baseline-success <= 15.0%
    """
    rates = summary["rates"]
    stats = summary["statistics"]

    tot_col = rates["TOTAL_COLLISION"]["rate"]
    succ_rate = rates["SUCCESS"]["rate"]
    timeout_rate = rates["TIMEOUT"]["rate"]
    standoff = stats.get("mean_standoff_distance", 0.0)
    overhead = overhead_metrics.get("mean_step_overhead_pct", 0.0) if overhead_metrics else 0.0

    criteria = {
        "Total Collisions <= 2.0%": {
            "target": "<= 2.0%",
            "achieved": f"{tot_col:.1f}%",
            "passed": bool(tot_col <= 2.0),
        },
        "Success Rate >= 85.0%": {
            "target": ">= 85.0%",
            "achieved": f"{succ_rate:.1f}%",
            "passed": bool(succ_rate >= 85.0),
        },
        "Timeout Rate <= 5.0%": {
            "target": "<= 5.0%",
            "achieved": f"{timeout_rate:.1f}%",
            "passed": bool(timeout_rate <= 5.0),
        },
        "Standoff Distance >= 0.45m": {
            "target": ">= 0.45 m",
            "achieved": f"{standoff:.2f} m" if standoff > 0 else "N/A (No Stops)",
            "passed": bool(standoff >= 0.45 or standoff == 0.0),
        },
        "Step Overhead on Baseline-Success <= 15.0%": {
            "target": "<= 15.0%",
            "achieved": f"{overhead:.1f}%",
            "passed": bool(overhead <= 15.0),
        },
    }

    all_passed = all(item["passed"] for item in criteria.values())
    return {
        "all_passed": all_passed,
        "criteria": criteria,
    }


# ── Report Generation (JSON & Markdown) ───────────────────────────────────────

def generate_markdown_report(report_data: Dict[str, Any]) -> str:
    """Generates detailed, structured Markdown report."""
    md = []
    md.append(f"# {report_data['title']}\n")
    md.append(f"**Date:** {report_data['timestamp']}  ")
    md.append(f"**Seeds:** `{report_data['seeds_str']}` ({len(report_data['seeds'])} episodes)  ")
    md.append(f"**Checkpoint:** `{report_data['checkpoint']}`  \n")

    md.append("## Executive Summary & Comparison Table\n")
    md.append("| Metric | Baseline (OFF) | Shield ON (Oracle) | Shield ON (Camera) | Target |")
    md.append("|---|:---:|:---:|:---:|:---:|")

    configs = report_data.get("configurations", {})
    base = configs.get("baseline", {})
    oracle = configs.get("shield_oracle", {})
    cam = configs.get("shield_camera", {})

    def get_rate_str(cfg, key):
        if not cfg:
            return "—"
        return cfg.get("rates", {}).get(key, {}).get("formatted", "—")

    md.append(f"| **Success Rate (95% CI)** | {get_rate_str(base, 'SUCCESS')} | {get_rate_str(oracle, 'SUCCESS')} | {get_rate_str(cam, 'SUCCESS')} | **>= 85.0%** |")
    md.append(f"| **Total Collision Rate** | {get_rate_str(base, 'TOTAL_COLLISION')} | {get_rate_str(oracle, 'TOTAL_COLLISION')} | {get_rate_str(cam, 'TOTAL_COLLISION')} | **<= 2.0%** |")
    md.append(f"| Obstacle Collisions | {get_rate_str(base, 'OBSTACLE_COLLISION')} | {get_rate_str(oracle, 'OBSTACLE_COLLISION')} | {get_rate_str(cam, 'OBSTACLE_COLLISION')} | — |")
    md.append(f"| Wall OOB Collisions | {get_rate_str(base, 'WALL_OOB')} | {get_rate_str(oracle, 'WALL_OOB')} | {get_rate_str(cam, 'WALL_OOB')} | — |")
    md.append(f"| Timeout Rate | {get_rate_str(base, 'TIMEOUT')} | {get_rate_str(oracle, 'TIMEOUT')} | {get_rate_str(cam, 'TIMEOUT')} | **<= 5.0%** |")

    def get_stat(cfg, key, fmt="{:.2f}"):
        if not cfg:
            return "—"
        val = cfg.get("statistics", {}).get(key, 0.0)
        return fmt.format(val)

    md.append(f"| **Mean Reward** | {get_stat(base, 'mean_reward')} +/- {get_stat(base, 'std_reward')} | {get_stat(oracle, 'mean_reward')} +/- {get_stat(oracle, 'std_reward')} | {get_stat(cam, 'mean_reward')} +/- {get_stat(cam, 'std_reward')} | — |")
    md.append(f"| **Mean Min Clearance** | {get_stat(base, 'mean_min_clearance')} m | {get_stat(oracle, 'mean_min_clearance')} m | {get_stat(cam, 'mean_min_clearance')} m | — |")
    md.append(f"| **Mean Episode Steps** | {get_stat(base, 'mean_steps', '{:.1f}')} | {get_stat(oracle, 'mean_steps', '{:.1f}')} | {get_stat(cam, 'mean_steps', '{:.1f}')} | — |")
    md.append(f"| **Standoff Distance** | N/A | {get_stat(oracle, 'mean_standoff_distance')} m | {get_stat(cam, 'mean_standoff_distance')} m | **>= 0.45 m** |")

    overhead_oracle = report_data.get("comparisons", {}).get("oracle_vs_baseline", {}).get("mean_step_overhead_pct", "—")
    overhead_cam = report_data.get("comparisons", {}).get("camera_vs_baseline", {}).get("mean_step_overhead_pct", "—")
    md.append(f"| **Step Overhead (Baseline Succ)** | Baseline | {overhead_oracle}% | {overhead_cam}% | **<= 15.0%** |\n")

    # Acceptance Criteria Audit
    md.append("## Acceptance Criteria Audit\n")
    if "acceptance_criteria" in report_data:
        md.append("| Criterion | Target | Achieved (Oracle) | Verdict |")
        md.append("|---|:---:|:---:|:---:|")
        for name, item in report_data["acceptance_criteria"].get("criteria", {}).items():
            status = "✅ PASS" if item["passed"] else "❌ FAIL"
            md.append(f"| {name} | {item['target']} | {item['achieved']} | **{status}** |")
        overall = "✅ **ALL ACCEPTANCE CRITERIA SATISFIED**" if report_data["acceptance_criteria"]["all_passed"] else "⚠️ **ACTION REQUIRED: CRITERIA UNMET**"
        md.append(f"\n**Overall Status:** {overall}\n")

    # Crash Forensics
    md.append("## Crash Forensics Log\n")
    forensics = report_data.get("crash_forensics", [])
    if not forensics:
        md.append("No non-success episodes observed. Perfect zero-collision / zero-timeout execution!\n")
    else:
        md.append(f"Total non-success episodes analyzed: **{len(forensics)}**\n")
        for f in forensics:
            md.append(f"### [Seed {f['seed']}] Configuration: {f['config_name']} — Outcome: `{f['outcome']}`")
            md.append(f"- **Steps:** {f['steps']} | **Reward:** {f['reward']} | **Min Clearance:** {f['min_clearance']} m")
            md.append(f"- **Diagnostic Cause:** {f['cause_of_failure']}")
            md.append("- **Last 5 Control Steps Telemetry:**")
            md.append("  ```")
            md.append("  Step | Pos [x, y, z]           | Vel [vx, vy, vz]        | Speed | Clr   | State    | Action Executed")
            md.append("  -----+-------------------------+-------------------------+-------+-------+----------+----------------")
            for st in f["last_10_steps"][-5:]:
                pos_str = f"[{st['pos'][0]:5.2f}, {st['pos'][1]:5.2f}, {st['pos'][2]:4.2f}]"
                vel_str = f"[{st['vel'][0]:5.2f}, {st['vel'][1]:5.2f}, {st['vel'][2]:4.2f}]"
                act_str = f"[{st['executed_action'][0]:4.2f}, {st['executed_action'][1]:4.2f}, {st['executed_action'][2]:4.2f}]"
                md.append(f"  {st['step']:4d} | {pos_str:23s} | {vel_str:23s} | {st['speed']:5.2f} | {st['clearance']:5.2f} | {st['shield_state']:8s} | {act_str}")
            md.append("  ```\n")

    return "\n".join(md)


def save_reports(report_data: Dict[str, Any], output_name: str, reports_dir: str = "reports") -> Tuple[str, str]:
    """Saves report data as JSON and Markdown files."""
    os.makedirs(reports_dir, exist_ok=True)
    json_path = os.path.join(reports_dir, f"{output_name}.json")
    md_path = os.path.join(reports_dir, f"{output_name}.md")

    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(report_data, f, indent=2)

    md_content = generate_markdown_report(report_data)
    with open(md_path, "w", encoding="utf-8") as f:
        f.write(md_content)

    print(f"[+] Saved JSON report to: {json_path}")
    print(f"[+] Saved Markdown report to: {md_path}")
    return json_path, md_path


# ── Main Entrypoint & CLI ─────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="Stop, Hover & Re-Route (SHR) Drone Safety Shield Evaluation Harness")
    parser.add_argument("--checkpoint", type=str, default="best_model.pt", help="Path to policy model checkpoint")
    parser.add_argument("--seeds", type=str, default="tuning",
                        help="Seed specification: 'reference' ([101,202,303,404,505]), 'tuning' (2000-2029), "
                             "range '2000-2029', or comma-separated '101,202,303'")
    parser.add_argument("--shield", action="store_true", default=False, help="Enable safety shield")
    parser.add_argument("--shield-mode", type=str, default="oracle", choices=["oracle", "camera"],
                        help="Shield sensor mode: 'oracle' or 'camera'")
    parser.add_argument("--compare", action="store_true", default=False,
                        help="Run sequential A/B comparison: Baseline (OFF) vs Oracle (ON) vs Camera (ON)")
    parser.add_argument("--max-steps", type=int, default=500, help="Maximum timesteps per episode")
    parser.add_argument("--output-name", type=str, default=None,
                        help="Base output filename for reports/ (defaults based on mode/seeds)")

    # Shield parameter overrides for tuning
    parser.add_argument("--t-brake", type=float, default=None, help="Override shield t_brake")
    parser.add_argument("--d-min", type=float, default=None, help="Override shield d_min")
    parser.add_argument("--d-safe", type=float, default=None, help="Override shield d_safe")
    parser.add_argument("--v-reroute", type=float, default=None, help="Override shield v_reroute")

    args = parser.parse_args()

    seeds = parse_seeds(args.seeds)

    # Prepare shield kwargs
    shield_kwargs = {}
    if args.t_brake is not None:
        shield_kwargs["t_brake"] = args.t_brake
    if args.d_min is not None:
        shield_kwargs["d_min"] = args.d_min
    if args.d_safe is not None:
        shield_kwargs["d_safe"] = args.d_safe
    if args.v_reroute is not None:
        shield_kwargs["v_reroute"] = args.v_reroute

    # Determine default report output name
    if args.output_name:
        out_name = args.output_name
    elif args.seeds.strip().lower() == "reference":
        out_name = "gate1_reference_benchmark"
    elif args.seeds.strip().lower() == "tuning":
        out_name = "gate1_tuning_benchmark"
    else:
        out_name = f"eval_{args.seeds.replace(',', '_').replace('-', '_')}"

    report_data = {
        "title": "Stop, Hover & Re-Route (SHR) Drone Safety Shield Benchmark Report",
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "checkpoint": args.checkpoint,
        "seeds_str": args.seeds,
        "seeds": seeds,
        "configurations": {},
        "comparisons": {},
        "crash_forensics": [],
    }

    with acquire_compute_lock():
        if args.compare:
            # 1. Baseline (Shield OFF)
            base_summary = evaluate_configuration(
                seeds=seeds,
                checkpoint_path=args.checkpoint,
                shield_enabled=False,
                config_name="Baseline (Shield OFF)",
                max_steps=args.max_steps,
            )
            report_data["configurations"]["baseline"] = base_summary

            # 2. Shield ON (Oracle)
            oracle_summary = evaluate_configuration(
                seeds=seeds,
                checkpoint_path=args.checkpoint,
                shield_enabled=True,
                sensor_mode="oracle",
                shield_kwargs=shield_kwargs,
                config_name="Shield ON (Oracle)",
                max_steps=args.max_steps,
            )
            report_data["configurations"]["shield_oracle"] = oracle_summary

            # 3. Shield ON (Camera)
            cam_summary = evaluate_configuration(
                seeds=seeds,
                checkpoint_path=args.checkpoint,
                shield_enabled=True,
                sensor_mode="camera",
                shield_kwargs=shield_kwargs,
                config_name="Shield ON (Camera)",
                max_steps=args.max_steps,
            )
            report_data["configurations"]["shield_camera"] = cam_summary

            # Compute comparative metrics
            comp_oracle = compute_comparison_metrics(base_summary, oracle_summary)
            comp_cam = compute_comparison_metrics(base_summary, cam_summary)
            report_data["comparisons"]["oracle_vs_baseline"] = comp_oracle
            report_data["comparisons"]["camera_vs_baseline"] = comp_cam

            # Acceptance Criteria check on Oracle
            ac_eval = evaluate_acceptance_criteria(oracle_summary, comp_oracle)
            report_data["acceptance_criteria"] = ac_eval

            # Collect crash forensics across all configs
            for cfg_key, cfg_sum in report_data["configurations"].items():
                for ep in cfg_sum["episodes"]:
                    if ep["outcome"] != "SUCCESS":
                        report_data["crash_forensics"].append({
                            "config_name": cfg_sum["config_name"],
                            "seed": ep["seed"],
                            "outcome": ep["outcome"],
                            "steps": ep["steps"],
                            "reward": ep["reward"],
                            "min_clearance": ep["min_clearance"],
                            "cause_of_failure": ep["cause_of_failure"],
                            "last_10_steps": ep["last_10_steps"],
                        })

        else:
            # Single configuration run
            cfg_name = f"Shield ON ({args.shield_mode})" if args.shield else "Baseline (Shield OFF)"
            summary = evaluate_configuration(
                seeds=seeds,
                checkpoint_path=args.checkpoint,
                shield_enabled=args.shield,
                sensor_mode=args.shield_mode,
                shield_kwargs=shield_kwargs,
                config_name=cfg_name,
                max_steps=args.max_steps,
            )
            cfg_key = f"shield_{args.shield_mode}" if args.shield else "baseline"
            report_data["configurations"][cfg_key] = summary

            for ep in summary["episodes"]:
                if ep["outcome"] != "SUCCESS":
                    report_data["crash_forensics"].append({
                        "config_name": cfg_name,
                        "seed": ep["seed"],
                        "outcome": ep["outcome"],
                        "steps": ep["steps"],
                        "reward": ep["reward"],
                        "min_clearance": ep["min_clearance"],
                        "cause_of_failure": ep["cause_of_failure"],
                        "last_10_steps": ep["last_10_steps"],
                    })

        save_reports(report_data, out_name)


if __name__ == "__main__":
    main()
