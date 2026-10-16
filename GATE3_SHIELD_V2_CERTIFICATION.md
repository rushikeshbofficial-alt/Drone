# Stop, Hover & Re-Route (SHR) Drone Safety Shield: Gate 3 Held-Out Certification Report

**Document ID:** `GATE3_SHIELD_V2_CERTIFICATION.md`  
**Date:** October 16, 2026  
**Git Branch:** `shr-v2`  
**Git Commit / Tag:** `0c41b61` (`shield-v2`)  
**Checkpoint:** `best_model_baseline.pt` (SHA-256: `A47610D967D689AD9A517E52D6D1788239B8C0F123BE430F0494B973A6AB2715`)  
**Target Hardware:** NVIDIA GeForce RTX 5060 Laptop GPU / Intel Core i7-14700HX  
**Target Environment:** PyBullet 3.2.6 + Gymnasium 0.29.1 + PyTorch (CUDA 12.8)  
**Tuning Seeds:** `4000–4029` (30 procedural episodes)  
**Validation Seeds:** `4030–4059` (30 procedural episodes)  
**Final Held-Out Evaluation Seeds:** `5000–5049` (50 procedural episodes)  
**Mutual Exclusion Protocol:** Enforced via `.compute.lock` throughout all runs  
**Status:** Gate 3 Evaluation Complete — 4 of 5 Criteria Certified, Step Overhead Missed (Failure Analysis & Re-certification Plan Provided)

---

## 1. Executive Summary & Acceptance Criteria Scorecard

Gate 3 conducts the rigorous, definitive evaluation of the **SHR v2 Safety Shield** on the **first fully unseen held-out test set** (seeds `5000–5049`, 50 procedural episodes). 

Prior to held-out evaluation, the codebase and parameters in [`drone_shield.py`](file:///c:/Users/Rushikesh/Desktop/Cool%20Ass%20Projects/Drone/drone_shield.py) were strictly frozen under git tag `shield-v2` at commit `0c41b61`. Zero parameter adjustments or code edits were performed.

### 1.1 Acceptance Criteria Scorecard on Final Held-Out Range (`5000–5049`)

| Acceptance Criterion | Gate 3 Target | Baseline Policy (OFF) | SHR v1 (Oracle) | SHR v2 (Oracle, Privileged) | SHR v2 (Camera, Report-Only) | Gate 3 Verdict |
|---|:---:|:---:|:---:|:---:|:---:|:---:|
| **Total Collision Rate** | $\le 2.0\%$ / $0$ | 72.0% [58.3%, 82.5%] (36/50) | **0.0% [0.0%, 7.1%] (0/50)** | **0.0% [0.0%, 7.1%] (0/50)** | 46.0% [33.0%, 59.6%] (23/50) | **PASSED** |
| Obstacle Collisions | 0 | 72.0% (36/50) | 0.0% (0/50) | **0.0% (0/50)** | 46.0% (23/50) | **PASSED** |
| Wall OOB Collisions | 0 | 0.0% (0/50) | 0.0% (0/50) | **0.0% (0/50)** | 0.0% (0/50) | **PASSED** |
| **Timeout Rate** | $\le 5.0\%$ | 0.0% [0.0%, 7.1%] (0/50) | 14.0% [7.0%, 26.2%] (7/50) | **0.0% [0.0%, 7.1%] (0/50)** | 2.0% [0.4%, 10.5%] (1/50) | **PASSED** |
| **Success Rate** | $\ge 85.0\%$ | 28.0% [17.5%, 41.7%] (14/50) | 86.0% [73.8%, 93.0%] (43/50) | **100.0% [92.9%, 100.0%] (50/50)** | 52.0% [38.5%, 65.2%] (26/50) | **PASSED** |
| **Standoff Distance at Full Stop** | $\ge 0.45\text{ m}$ | N/A (No stopping) | 1.99 m | **1.84 m** | 0.57 m | **PASSED** |
| **Step Overhead vs Baseline (on Baseline Successes)** | $\le +15.0\%$ | 0.0% (151.8 mean steps) | +57.77% (241.9 mean steps) | **+45.79% (221.8 mean steps)** | +51.72% (230.3 mean steps) | **TARGET MISSED** |
| *Step Overhead vs SHR v1 (on v1 Successes)* | *N/A (Informational)* | — | 0.0% (245.8 mean steps) | **-3.46% (233.6 mean steps)** | — | *Faster than v1* |
| **Camera Mode Status** | Report-Only | — | — | — | **Report-Only (No Tuning)** | **PASSED** |

---

## 2. Protocol Adherence & Critical Methodological Disclaimers

1. **Protocol Freeze:** In accordance with Gate 3 protocol, commit `0c41b61` was tagged `shield-v2`. `git diff shield-v2 -- drone_shield.py` was verified to be strictly empty before and after benchmarking. Zero tuning or parameter adjustments were executed after observing held-out results.
2. **First Fully Unseen Test Set (`5000–5049`):** As mandated, we explicitly note that the `4030–4059` validation set was evaluated during the Gate 1 forensic diagnosis (its 7 timeout episodes directly informed the design of the remediations). Therefore, **seeds `5000–5049` constitute the first fully unseen procedural test set** that was never examined during diagnosis, parameter tuning, or remediation development.
3. **Privileged Simulator Information Label:** All SHR v2 Oracle results explicitly utilize **privileged simulator information**. Sensing relies on analytical ground-truth obstacle positions and bounding extents from the PyBullet physics engine, and the A* escalation fallback queries exact obstacle geometry for inflated 2D grid planning.
4. **Camera Mode Designation (REPORT-ONLY):** Monocular depth camera mode remains strictly report-only with zero developer effort allocated. The forward camera (65° horizontal FOV) continues to suffer blind-spots during lateral maneuvers, causing 46.0% collisions on held-out layouts.
5. **Mutual Exclusion:** Every evaluation executed with mutual hardware exclusion via `.compute.lock`.

---

## 3. Per-Fix Ablation Study on the 15 Former v1 Timeouts

During Gate 1 forensic diagnosis, 15 oracle timeout episodes were identified across diagnostic seeds `4000–4059`:
`[4000, 4015, 4018, 4020, 4021, 4023, 4024, 4026, 4036, 4048, 4049, 4052, 4053, 4055, 4056]`.

To determine the exact contribution of each remediation in [`drone_shield.py`](file:///c:/Users/Rushikesh/Desktop/Cool%20Ass%20Projects/Drone/drone_shield.py), we conducted an empirical per-fix ablation study across all 15 seeds. All experiments were executed under `.compute.lock` using [`run_gate3_ablation.py`](file:///c:/Users/Rushikesh/Desktop/Cool%20Ass%20Projects/Drone/run_gate3_ablation.py) and archived in [`reports/gate3_ablation_results.json`](file:///c:/Users/Rushikesh/Desktop/Cool%20Ass%20Projects/Drone/reports/gate3_ablation_results.json).

### 3.1 Ablation Results Table

| Configuration Tested | Remediations Enabled | Timeouts Resolved | Timeouts Remaining | Collisions | A* Planner Fallback Invocations | Empirical Behavior & Notes |
|---|---|:---:|:---:|:---:|:---:|---|
| **SHR v1 (Baseline)** | None (All 5 Fixes OFF) | **0 / 15 (0.0%)** | 15 / 15 (100.0%) | 0 / 15 | 0 / 15 | Reproduces the exact 15 Gate 1 timeout episodes. |
| **Alone: Fix 1** | `anti_amnesia` only | **1 / 15 (6.7%)** | 14 / 15 (93.3%) | 0 / 15 | 0 / 15 | Resolves Seed 4049 by retaining history penalty to alternate scan side. |
| **Alone: Fix 2** | `forward_creep` only | **2 / 15 (13.3%)** | 13 / 15 (86.7%) | 0 / 15 | 0 / 15 | Resolves Seeds 4020, 4049 by eliminating lateral shuttling forward lock ($v_y > 0$). |
| **Alone: Fix 3** | `guided_bypass` only | **1 / 15 (6.7%)** | 14 / 15 (93.3%) | 0 / 15 | 0 / 15 | Resolves Seed 4023 by holding reroute state until body passes obstacle edge. |
| **Alone: Fix 4** | `goal_proximity` only | **0 / 15 (0.0%)** | 15 / 15 (100.0%) | 0 / 15 | 0 / 15 | Ineffective alone because all 15 traps occurred in mid-corridor ($\text{dist} \ge 4.45\text{m}$). |
| **Alone: Fix 5** | `oracle_planner` only | **14 / 15 (93.3%)** | 1 / 15 (6.7%) | 0 / 15 | 15 / 15 | Resolves 14 of 15 timeouts alone via 2D A* inflated replanning. Only Seed 4018 timed out. |
| **Cumulative 1** | `+anti_amnesia` | **1 / 15 (6.7%)** | 14 / 15 (93.3%) | 0 / 15 | 0 / 15 | Resolves Seed 4049. |
| **Cumulative 2** | `+anti_amnesia` `+forward_creep` | **2 / 15 (13.3%)** | 13 / 15 (86.7%) | 0 / 15 | 0 / 15 | Resolves Seeds 4020, 4049. |
| **Cumulative 3** | `+anti_amnesia` `+forward_creep` `+guided_bypass` | **2 / 15 (13.3%)** | 13 / 15 (86.7%) | 0 / 15 | 0 / 15 | Resolves Seeds 4023, 4049 (Seed 4020 timed out at step 500 during extended bypass). |
| **Cumulative 4** | `+anti_amnesia` `+forward_creep` `+guided_bypass` `+goal_proximity` | **2 / 15 (13.3%)** | 13 / 15 (86.7%) | 0 / 15 | 0 / 15 | Resolves Seeds 4023, 4049. |
| **Cumulative 5 (Full v2)** | **All 5 Remediations Enabled** | **15 / 15 (100.0%)** | **0 / 15 (0.0%)** | **0 / 15** | **15 / 15** | **100.0% resolved. Zero timeouts, zero collisions.** |

### 3.2 Key Ablation Findings
1. **Heuristic Ceiling:** Reactive heuristic fixes (`anti_amnesia`, `forward_creep`, `guided_bypass`) resolve between 1 and 2 of the 15 traps when deployed alone or together. Reactive potential-field and raycast FSMs cannot alone navigate concave multi-obstacle pockets or wall pinches.
2. **Decisive Impact of `oracle_planner`:** The 2D A* geometric planner is the decisive escalation mechanism. When added to the cumulative stack, resolution jumps from 2/15 (13.3%) to 15/15 (100.0%).
3. **Synergy:** When heuristic guidance and the planner operate together in Full v2, all 15 traps are eliminated cleanly without a single collision.

---

## 4. A* Fallback (PLANNER State) Telemetry Audit

The A* path planner escalation triggers only when reactive rerouting encounters repeated deadlocks (`deadlock_attempts >= 2` or lateral blockage/step exhaustion).

We audited every episode across all benchmark ranges to quantify exactly how often the privileged A* planner was invoked:

| Benchmark Phase | Seed Range | Total Episodes | Episodes Invoking A* Planner | Invocations Rate (%) | Mean Steps in PLANNER State | Specific Episode Seeds Invoking A* Planner |
|---|:---:|:---:|:---:|:---:|:---:|---|
| **Gate 2 Tuning** | `4000–4029` | 30 | 10 / 30 | **33.3%** | 80.6 steps | `[4000, 4002, 4015, 4018, 4020, 4021, 4023, 4024, 4026, 4027]` |
| **Gate 2 Validation** | `4030–4059` | 30 | 8 / 30 | **26.7%** | 99.1 steps | `[4036, 4048, 4049, 4050, 4052, 4053, 4055, 4056]` |
| **Combined Diagnostic** | `4000–4059` | 60 | 18 / 60 | **30.0%** | 88.8 steps | *All 15 former timeouts + 3 narrow-corridor seeds (4002, 4027, 4050)* |
| **Gate 3 Final Held-Out** | `5000–5049` | 50 | 14 / 50 | **28.0%** | 81.3 steps | `[5010, 5012, 5013, 5014, 5016, 5018, 5024, 5026, 5028, 5030, 5033, 5039, 5048, 5049]` |

### 4.1 Resolution of Held-Out v1 Timeouts
Under SHR v1, seeds `5000–5049` produced **7 timeouts** (14.0% timeout rate): `[5005, 5013, 5014, 5018, 5024, 5026, 5039]`.  
Under SHR v2:
- **Seed 5005:** Resolved by heuristic guided bypass in 266 steps (0 steps in planner).
- **Seeds 5013, 5014, 5018, 5024, 5026, 5039 (6 seeds):** Escalated cleanly to `ShieldState.PLANNER`, successfully navigating out of deadlocks with 45–174 planner steps and completing all missions safely.
- Result: **0 timeouts remain (0.0%)**.

---

## 5. Comprehensive Held-Out Benchmark Results (`5000–5049`, 50 Episodes)

Evaluated under mutual exclusion ([`reports/gate3_heldout_v2_compare.json`](file:///c:/Users/Rushikesh/Desktop/Cool%20Ass%20Projects/Drone/reports/gate3_heldout_v2_compare.json) and [`reports/gate3_heldout_v1_oracle.json`](file:///c:/Users/Rushikesh/Desktop/Cool%20Ass%20Projects/Drone/reports/gate3_heldout_v1_oracle.json)):

```
========================================================================================================
FINAL HELD-OUT PERFORMANCE COMPARISON: SEEDS 5000-5049 (50 EPISODES)
========================================================================================================
Metric                               | Baseline (OFF)      | SHR v1 (Oracle)     | SHR v2 (Oracle, Priv) | SHR v2 (Camera, Rep)
-------------------------------------+---------------------+---------------------+-----------------------+---------------------
Success Rate (Wilson 95% CI)         |  28.0% [17.5, 41.7] |  86.0% [73.8, 93.0] | 100.0% [92.9, 100.0]  |  52.0% [38.5, 65.2] 
Total Collision Rate (95% CI)        |  72.0% [58.3, 82.5] |   0.0% [ 0.0,  7.1] |   0.0% [ 0.0,  7.1]   |  46.0% [33.0, 59.6] 
  - Obstacle Collisions              |  72.0% (36/50)      |   0.0% ( 0/50)      |   0.0% ( 0/50)        |  46.0% (23/50)      
  - Wall Out-Of-Bounds Collisions    |   0.0% ( 0/50)      |   0.0% ( 0/50)      |   0.0% ( 0/50)        |   0.0% ( 0/50)      
Timeout Rate (Wilson 95% CI)         |   0.0% [ 0.0,  7.1] |  14.0% [ 7.0, 26.2] |   0.0% [ 0.0,  7.1]   |   2.0% [ 0.4, 10.5] 
Mean Episode Reward                  |  -9.41 +/- 161.40   | -516.62 +/- 791.32  | -215.74 +/- 281.48    | -448.68 +/- 436.44  
Mean Minimum Clearance               | 0.13 m              | 0.39 m              | 0.36 m                | 0.27 m              
Mean Total Episode Steps             | 90.0 steps          | 281.4 steps         | 246.9 steps           | 208.1 steps         
Mean Standoff Distance at Full Stop  | N/A                 | 1.99 m              | 1.84 m                | 0.57 m              
Intervention Rate (% of steps active)| 0.0%                | 47.1%               | 48.5%                 | 53.7%               
A* Planner Escalation Rate           | N/A                 | N/A                 | 28.0% (14/50 eps)     | N/A                 
Step Overhead on Baseline-Successes  | 0.0% (Reference)    | +57.77%             | +45.79%               | +51.72%             
Step Overhead on v1-Successes        | —                   | 0.0% (Reference)    | -3.46% (Faster)       | —                   
========================================================================================================
```

---

## 6. Baseline-Succeeding Episodes & Step Overhead Analysis

The baseline unshielded policy succeeded on exactly **14 of 50 episodes (28.0% success rate)**.  
On these 14 episodes, the baseline drone had an unobstructed line-of-sight to the goal and accelerated at full unregulated throttle ($v_y \approx 2.5 - 3.2\text{ m/s}$), reaching the goal in a mean of **$151.8 \pm 14.6$ steps**.

### 6.1 Seed-by-Seed Audit on the 14 Baseline-Succeeding Episodes

| Seed ID | Baseline Steps | SHR v1 Steps (Overhead vs Base) | SHR v2 Steps (Overhead vs Base) | v2 Intervention Rate (%) | v2 Standoff Distance (m) | v2 Steps in FSM Avoidance States |
|:---:|:---:|:---:|:---:|:---:|:---:|---|
| **5000** | 141 | 255 (+80.9%) | 224 (+58.9%) | 37.1% | 0.56 m | 39 steps (1 BRAKE, 1 SCAN, 37 REROUTE) |
| **5005** | 160 | 500 (+212.5% timeout) | 266 (+66.2%) | 43.2% | 1.44 m | 36 steps (3 BRAKE, 3 SCAN, 30 REROUTE) |
| **5006** | 140 | 164 (+17.1%) | 175 (+25.0%) | 17.7% | 0.00 m | **0 detour steps** (All 175 steps in NOMINAL) |
| **5008** | 142 | 181 (+27.5%) | 192 (+35.2%) | 30.7% | 0.57 m | 17 steps (1 BRAKE, 1 SCAN, 15 REROUTE) |
| **5011** | 139 | 197 (+41.7%) | 208 (+49.6%) | 31.2% | 2.22 m | 20 steps (2 BRAKE, 2 SCAN, 16 REROUTE) |
| **5012** | 177 | 282 (+59.3%) | 274 (+54.8%) | 60.9% | 0.56 m | 96 steps (2 BRAKE, 2 SCAN, 44 REROUTE, 48 PLANNER) |
| **5015** | 138 | 160 (+15.9%) | 171 (+23.9%) | 26.9% | 0.00 m | **0 detour steps** (All 171 steps in NOMINAL) |
| **5017** | 176 | 322 (+83.0%) | 235 (+33.5%) | 38.7% | 0.62 m | 32 steps (2 BRAKE, 2 SCAN, 28 REROUTE) |
| **5020** | 174 | 253 (+45.4%) | 266 (+52.9%) | 25.2% | 0.76 m | 7 steps (1 BRAKE, 1 SCAN, 5 REROUTE) |
| **5022** | 161 | 196 (+21.7%) | 190 (+18.0%) | 28.9% | 7.55 m | 14 steps (2 BRAKE, 2 SCAN, 10 REROUTE) |
| **5025** | 146 | 226 (+54.8%) | 233 (+59.6%) | 37.8% | 4.12 m | 43 steps (2 BRAKE, 2 SCAN, 39 REROUTE) |
| **5035** | 138 | 193 (+39.9%) | 203 (+47.1%) | 22.7% | 0.56 m | 11 steps (1 BRAKE, 1 SCAN, 9 REROUTE) |
| **5045** | 139 | 166 (+19.4%) | 176 (+26.6%) | 13.6% | 0.00 m | **0 detour steps** (All 176 steps in NOMINAL) |
| **5048** | 154 | 292 (+89.6%) | 292 (+89.6%) | 64.7% | 4.79 m | 105 steps (4 BRAKE, 4 SCAN, 45 REROUTE, 52 PLANNER) |
| **Mean** | **151.8** | **241.9 (+57.8%)** | **221.8 (+45.8%)** | **34.3%** | **1.71 m** | — |

---

## 7. Failure Analysis for Missed Criterion: Step Overhead vs Baseline

### 7.1 The Physics & Mechanics of the +45.79% Overhead
The criterion specifies:
$$\text{Step Overhead on Baseline-Successes} \le +15.0\%$$
On the 14 baseline-succeeding held-out episodes, SHR v2 achieved **+45.79% mean overhead** (median +48.37%), failing the 15.0% target.

Our forensic investigation reveals two root causes:

1. **The Safe Speed Governor in NOMINAL Mode (Physics Constraint):**
   - In [`drone_shield.py:721–748`](file:///c:/Users/Rushikesh/Desktop/Cool%20Ass%20Projects/Drone/drone_shield.py#L721-L748), the speed governor enforces a deterministic stopping constraint:
     $$v_{\text{cap}}(d) = \min\left(3.0, \sqrt{2 a_{\text{dec}} \max(d - d_{\text{safe}}, 0)}\right)$$
   - In seeds **5006, 5015, and 5045**, the drone encountered **zero obstacles requiring avoidance** (zero BRAKE, SCAN, REROUTE, or PLANNER steps; 100% of steps were in `NOMINAL`).
   - Yet on these exact episodes, the step overhead was:
     - Seed 5006: 175 steps vs 140 baseline steps (**+25.0% overhead**)
     - Seed 5015: 171 steps vs 138 baseline steps (**+23.9% overhead**)
     - Seed 5045: 176 steps vs 139 baseline steps (**+26.6% overhead**)
   - Because the baseline policy flies recklessly at full throttle (~3.0 m/s) within 0.15m–0.35m of obstacles without braking, the shield's mandated deceleration to guarantee stopping distance inherently costs +24% to +27% steps **even without any detour**.

2. **Detour Path Length around Proximate Obstacles:**
   - In the remaining 11 baseline successes, the baseline narrowly skims obstacle boundaries at high speed (often surviving by mere millimeters; mean min clearance 0.13m).
   - The shield enforces a minimum safe clearance $d_{\text{safe}} = 0.55\text{ m}$. Whenever clearance falls below $d_{\text{min}} = 0.45\text{ m}$, the shield executes a safe lateral bypass (e.g. Seed 5000: 37 reroute steps; Seed 5048: 45 reroute steps + 52 planner steps), creating additional flight distance.

### 7.2 Discrepancy with Gate 2 Protocol Metric
In Gate 2, the report assessed step overhead against **v1 successes** (yielding **-2.22%**, certified faster).  
On held-out seeds `5000–5049`, comparing SHR v2 against SHR v1 on the 43 v1 successes yields **-3.46%** (233.6 vs 245.8 mean steps).  
SHR v2 is empirically **3.5% faster than SHR v1** and completely eliminates timeouts.  
However, when measured strictly against the **raw unprotected baseline policy** as required by the automated harness (`eval_shield.py:563`), the overhead is +45.79%.

---

## 8. Action Plan: Re-Certification Protocol for Fallback Range (`5100–5149`)

Per the explicit freeze instruction:
> *"FREEZE: tag shield-v2, no parameter or code changes after seeing the 5000-5049 results. If the targets are missed, report the numbers and the failure analysis. Do not re-tune on 5000-5049. A re-certified candidate goes to 5100-5149 and must be labelled as such."*

1. **No Re-tuning on 5000–5049:** The parameters and code of `shield-v2` remain frozen.
2. **If Proceeding to Re-Certification:**
   - Candidate modifications must balance the speed governor parameter $a_{\text{dec}}$ or $d_{\text{safe}}$ in NOMINAL mode, or the certification target must formally distinguish between overhead vs baseline (which crashes 72% of the time) versus overhead vs the certified v1 shield.
   - Any re-certified candidate must be evaluated on the certified disjoint fallback held-out seed range: **`5100–5149` (50 episodes)**.
   - The run must be explicitly labeled: `RE-CERTIFIED CANDIDATE (SEEDS 5100-5149)`.

---

## 9. Gate 3 PASTE-BACK Block

```
================================== PASTE-BACK ==================================
1. RAW CONSOLE OUTPUT OF KEY EVALUATION COMMANDS:
   [*] python eval_shield.py --checkpoint best_model_baseline.pt --seeds 5000-5049 --compare --shield-version v2 --output-name gate3_heldout_v2_compare
       SUMMARY: Baseline (Shield OFF)
         SUCCESS           :  28.0% [17.5%, 41.7%] (14/50)
         TOTAL_COLLISION   :  72.0% [58.3%, 82.5%] (36/50) (Obs: 36, Wall: 0)
         TIMEOUT           :   0.0% [ 0.0%,  7.1%] (0/50)
         Mean Reward       : -9.41 +/- 161.40 | Mean Steps: 90.0 | MinClr: 0.13m
       SUMMARY: Shield ON (Oracle, Privileged Simulator Information)
         SUCCESS           : 100.0% [92.9%, 100.0%] (50/50)
         TOTAL_COLLISION   :   0.0% [ 0.0%,  7.1%] (0/50) (Obs:  0, Wall: 0)
         TIMEOUT           :   0.0% [ 0.0%,  7.1%] (0/50)
         Mean Reward       : -215.74 +/- 281.48 | Mean Steps: 246.9 | MinClr: 0.36m
         Standoff Distance : 1.84 m | Intervention Rate: 48.5%
         A* Planner Invoked: 14/50 (28.0% of episodes)
       SUMMARY: Shield ON (Camera, REPORT-ONLY)
         SUCCESS           :  52.0% [38.5%, 65.2%] (26/50)
         TOTAL_COLLISION   :  46.0% [33.0%, 59.6%] (23/50) (Obs: 23, Wall: 0)
         TIMEOUT           :   2.0% [ 0.4%, 10.5%] (1/50)

   [*] python eval_shield.py --checkpoint best_model_baseline.pt --seeds 5000-5049 --shield --shield-mode oracle --shield-version v1 --output-name gate3_heldout_v1_oracle
       SUMMARY: Shield ON (Oracle v1)
         SUCCESS           :  86.0% [73.8%, 93.0%] (43/50)
         TOTAL_COLLISION   :   0.0% [ 0.0%,  7.1%] (0/50)
         TIMEOUT           :  14.0% [ 7.0%, 26.2%] (7/50)
         Mean Reward       : -516.62 +/- 791.32 | Mean Steps: 281.4 | MinClr: 0.39m

   [*] python run_gate3_ablation.py (Ablation on 15 Former v1 Timeouts):
       - Baseline v1 (0/5 fixes):  0/15 Resolved (15 timeouts, 0 collisions)
       - Alone Fix 1 (anti_amnesia): 1/15 Resolved (Seed 4049)
       - Alone Fix 2 (forward_creep): 2/15 Resolved (Seeds 4020, 4049)
       - Alone Fix 3 (guided_bypass): 1/15 Resolved (Seed 4023)
       - Alone Fix 4 (goal_proximity): 0/15 Resolved
       - Alone Fix 5 (oracle_planner): 14/15 Resolved (14/15 invoked planner)
       - Cumulative Stack (Full v2): 15/15 Resolved (100.0% resolved, 15/15 invoked planner)

2. RESULTS TABLE: SEEDS 5000-5049 (50 Episodes):
   +------------------------------------+---------------+---------------+-----------------------+---------------------+
   | Metric                             | Baseline OFF  | SHR v1 Oracle | SHR v2 (Oracle, Priv) | SHR v2 Camera (Rep) |
   +------------------------------------+---------------+---------------+-----------------------+---------------------+
   | Success Rate (95% CI)              | 28.0% (14/50) | 86.0% (43/50) | 100.0% (50/50)        | 52.0% (26/50)       |
   | Total Collision Rate               | 72.0% (36/50) |  0.0% ( 0/50) |   0.0% ( 0/50)        | 46.0% (23/50)       |
   | Timeout Rate                       |  0.0% ( 0/50) | 14.0% ( 7/50) |   0.0% ( 0/50)        |  2.0% ( 1/50)       |
   | Mean Min Clearance                 | 0.13 m        | 0.39 m        |   0.36 m              | 0.27 m              |
   | Standoff Distance at Full Stop     | N/A           | 1.99 m        |   1.84 m              | 0.57 m              |
   | Intervention Rate (% steps)        | 0.0%          | 47.1%         |  48.5%                | 53.7%               |
   | Mean Steps (Baseline-Successes)    | 151.8         | 241.9         |  221.8                | 230.3               |
   | Step Overhead vs Baseline Success  | Reference     | +57.77%       |  +45.79% [TARGET MISSED]| +51.72%           |
   | Step Overhead vs v1 Successes      | —             | Reference     |  -3.46% (Faster)      | —                   |
   +------------------------------------+---------------+---------------+-----------------------+---------------------+

3. ACCEPTANCE CRITERIA STATUS:
   - Total Collisions <= 2.0%: 0.0% (PASSED)
   - Timeout Rate <= 5.0%: 0.0% (PASSED)
   - Success Rate >= 85.0%: 100.0% (PASSED)
   - Standoff Distance >= 0.45m: 1.84 m (PASSED)
   - Step Overhead vs Baseline <= 15.0%: +45.79% (FAILED / TARGET MISSED)

4. FILES TOUCHED:
   - Codebase strictly frozen at tag shield-v2 (commit 0c41b61); drone_shield.py UNTOUCHED.
   - Created: GATE3_SHIELD_V2_CERTIFICATION.md, run_gate3_ablation.py, analyze_gate3_results.py.
   - Telemetry reports: reports/gate3_heldout_v2_compare.json, reports/gate3_heldout_v2_compare.md,
     reports/gate3_heldout_v1_oracle.json, reports/gate3_heldout_v1_oracle.md, reports/gate3_ablation_results.json.

5. OPEN QUESTIONS OR RISKS:
   - Overhead vs Baseline vs Overhead vs v1: Baseline succeeds only by flying straight without braking (151.8 steps, 72% crash rate). Any active safety shield with a deterministic stopping speed governor requires ~171-176 steps even on completely clear paths (+25% overhead). Deciding whether the 15% target applies to baseline or v1 is the primary policy question.
   - Privilege dependence: 28% of held-out episodes require the 2D A* planner escalation to guarantee 100% success without timeouts.

6. WHAT WILL BE DONE NEXT:
   - STOP after Gate 3. Wait for coordinator go-ahead before touching code or proceeding to re-certification on seeds 5100-5149.
================================================================================
```
