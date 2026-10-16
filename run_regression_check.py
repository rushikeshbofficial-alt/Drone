import json
import numpy as np

def main():
    # Load Gate 0 v1 benchmark
    with open("reports/gate0_seeds_4000_4059_recon.json", "r") as f:
        gate0 = json.load(f)
    v1_episodes = gate0["configurations"]["shield_oracle"]["episodes"]
    v1_success_dict = {ep["seed"]: ep for ep in v1_episodes if ep["outcome"] == "SUCCESS"}

    # Load Gate 2 v2 benchmarks
    with open("reports/gate2_tuning_benchmark.json", "r") as f:
        tuning_v2 = json.load(f)["configurations"]["shield_oracle"]["episodes"]
    with open("reports/gate2_validation_benchmark.json", "r") as f:
        val_v2 = json.load(f)["configurations"]["shield_oracle"]["episodes"]

    v2_all_dict = {ep["seed"]: ep for ep in (tuning_v2 + val_v2)}

    print(f"Total v1 successes identified: {len(v1_success_dict)} (Expected: 45)")

    regressions = []
    collisions = []
    overheads = []
    details = []

    for seed, v1_ep in sorted(v1_success_dict.items()):
        v2_ep = v2_all_dict.get(seed)
        if v2_ep is None:
            raise ValueError(f"Seed {seed} missing from v2 benchmark results!")

        v1_steps = v1_ep["steps"]
        v2_steps = v2_ep["steps"]
        v2_outcome = v2_ep["outcome"]

        step_diff = v2_steps - v1_steps
        overhead_pct = (step_diff / float(v1_steps)) * 100.0
        overheads.append(overhead_pct)

        if v2_outcome != "SUCCESS":
            regressions.append((seed, v1_outcome, v2_outcome))
        if "COLLISION" in v2_outcome:
            collisions.append(seed)

        details.append({
            "seed": seed,
            "v1_steps": v1_steps,
            "v2_steps": v2_steps,
            "step_diff": step_diff,
            "overhead_pct": round(overhead_pct, 2),
            "v2_outcome": v2_outcome,
            "v1_reward": round(v1_ep["reward"], 2),
            "v2_reward": round(v2_ep["reward"], 2),
        })

    mean_overhead = float(np.mean(overheads))
    median_overhead = float(np.median(overheads))
    std_overhead = float(np.std(overheads))

    print("\n" + "=" * 80)
    print("REGRESSION CHECK REPORT: 45 V1-SUCCEEDING EPISODES EVALUATED UNDER V2")
    print("=" * 80)
    print(f"Total Evaluated        : {len(v1_success_dict)} episodes")
    print(f"Regressions            : {len(regressions)} (Target: 0)")
    print(f"Collisions             : {len(collisions)} (Target: 0)")
    print(f"Mean Step Overhead     : {mean_overhead:+.2f}% (Target: <= +15.0%)")
    print(f"Median Step Overhead   : {median_overhead:+.2f}%")
    print(f"Std Dev Step Overhead  : {std_overhead:.2f}%")
    print(f"Min / Max Overhead     : {min(overheads):+.2f}% / {max(overheads):+.2f}%")
    print("=" * 80)

    # Print breakdown
    print(f"{'Seed':5s} | {'v1 Steps':8s} | {'v2 Steps':8s} | {'Diff':5s} | {'Overhead %':10s} | {'v2 Outcome':10s} | {'Status'}")
    print("-" * 80)
    for d in details:
        status = "REGRESSION" if d["v2_outcome"] != "SUCCESS" else ("SLOWER" if d["overhead_pct"] > 0 else "FASTER/EQUAL")
        print(f"{d['seed']:5d} | {d['v1_steps']:8d} | {d['v2_steps']:8d} | {d['step_diff']:+5d} | {d['overhead_pct']:+9.2f}% | {d['v2_outcome']:10s} | {status}")

    # Save summary
    summary_data = {
        "title": "Gate 2 Regression Check (45 v1-Succeeding Episodes under v2)",
        "num_episodes": len(v1_success_dict),
        "regressions_count": len(regressions),
        "collisions_count": len(collisions),
        "mean_step_overhead_pct": round(mean_overhead, 2),
        "median_step_overhead_pct": round(median_overhead, 2),
        "std_step_overhead_pct": round(std_overhead, 2),
        "min_step_overhead_pct": round(min(overheads), 2),
        "max_step_overhead_pct": round(max(overheads), 2),
        "regressed_seeds": regressions,
        "details": details,
    }

    with open("reports/gate2_regression_check.json", "w") as f:
        json.dump(summary_data, f, indent=2)
    print("\n[+] Saved regression check summary to reports/gate2_regression_check.json")

if __name__ == "__main__":
    main()
