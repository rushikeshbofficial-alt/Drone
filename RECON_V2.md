# Stop, Hover & Re-Route (SHR) System Reconnaissance Report v2 (Gate 0)

**Date:** October 16, 2026  
**Git Branch:** `shr-v2` (forked from tag `shr-complete` at commit `d094001`)  
**Target Hardware:** NVIDIA GeForce RTX 5060 Laptop GPU / Intel Core i7-14700HX  
**Target Environment:** PyBullet 3.2.6 + Gymnasium 0.29.1 + PyTorch (CUDA 12.8)  

---

## 1. Reproduction of Reference Benchmarks & Diagnostics (Seeds 4000–4059)

### 1.1 Reference Seeds Benchmark ([101, 202, 303, 404, 505])
Executed via:
```powershell
python eval_shield.py --checkpoint best_model_baseline.pt --seeds reference --compare --output-name gate0_reference_recon
```

| Metric | Baseline Policy (Shield OFF) | Shield ON (Oracle Mode) | Shield ON (Camera Mode) | Prior Recorded | Target Threshold |
|---|:---:|:---:|:---:|:---:|:---:|
| **Success Rate (95% CI)** | 20.0% [3.6%, 62.4%] (1/5) | **100.0% [56.6%, 100.0%] (5/5)** | 0.0% [0.0%, 43.4%] (0/5) | 20.0% / 100.0% / 0.0% | $\ge$ 85.0% |
| **Total Collision Rate** | 80.0% [37.6%, 96.4%] (4/5) | **0.0% [0.0%, 43.4%] (0/5)** | 80.0% [37.6%, 96.4%] (4/5) | 80.0% / 0.0% / 40.0% | $\le$ 2.0% |
| Obstacle Collisions | 60.0% [23.1%, 88.2%] (3/5) | **0.0% [0.0%, 43.4%] (0/5)** | 80.0% [37.6%, 96.4%] (4/5) | 80.0% / 0.0% / 40.0% | — |
| Wall OOB Collisions | 20.0% [3.6%, 62.4%] (1/5) | **0.0% [0.0%, 43.4%] (0/5)** | 0.0% [0.0%, 43.4%] (0/5) | 0.0% / 0.0% / 0.0% | — |
| Timeout Rate | 0.0% [0.0%, 43.4%] (0/5) | 0.0% [0.0%, 43.4%] (0/5) | 20.0% [3.6%, 62.4%] (1/5) | 0.0% / 0.0% / 60.0% | $\le$ 5.0% |
| **Mean Reward** | -66.81 $\pm$ 165.29 | -170.35 $\pm$ 432.01 | -699.79 $\pm$ 856.22 | -66.81 / -164.60 | — |
| **Mean Min Clearance** | 0.12 m | **0.61 m** | 0.46 m | 0.12 m / 0.56 m | — |
| **Mean Steps** | 102.8 | 231.8 | 185.0 | 102.8 / 231.8 | — |

**Confirmation:** Baseline **20.0% Success / 80.0% Collision** on reference seeds is strictly reproduced. Oracle Shield achieves 100.0% Success / 0.0% Collision.

---

### 1.2 Diagnostic & Tuning Benchmark (Seeds 4000–4059, 60 Episodes)
Executed via:
```powershell
python eval_shield.py --checkpoint best_model_baseline.pt --seeds 4000-4059 --compare --output-name gate0_seeds_4000_4059_recon
```

| Metric | Baseline Policy (Shield OFF) | Shield ON (Oracle Mode) | Shield ON (Camera Mode) | Target Threshold |
|---|:---:|:---:|:---:|:---:|
| **Success Rate (95% CI)** | 28.3% [18.5%, 40.8%] (17/60) | **75.0% [62.8%, 84.2%] (45/60)** | 0.0% [0.0%, 6.0%] (0/60) | $\ge$ 85.0% |
| **Total Collision Rate** | 71.7% [59.2%, 81.5%] (43/60) | **0.0% [0.0%, 6.0%] (0/60)** | 53.3% [40.9%, 65.4%] (32/60) | $\le$ 2.0% |
| Obstacle Collisions | 71.7% [59.2%, 81.5%] (43/60) | **0.0% [0.0%, 6.0%] (0/60)** | 53.3% [40.9%, 65.4%] (32/60) | — |
| Wall OOB Collisions | 0.0% [0.0%, 6.0%] (0/60) | **0.0% [0.0%, 6.0%] (0/60)** | 0.0% [0.0%, 6.0%] (0/60) | — |
| **Timeout Rate (95% CI)** | 0.0% [0.0%, 6.0%] (0/60) | **25.0% [15.8%, 37.2%] (15/60)** | 46.7% [34.6%, 59.1%] (28/60) | $\le$ 5.0% |
| **Mean Reward** | -18.73 $\pm$ 164.74 | -623.99 $\pm$ 860.57 | -1246.37 $\pm$ 1192.39 | — |
| **Mean Min Clearance** | 0.14 m | 0.38 m | 0.62 m | — |
| **Mean Steps** | 89.4 | 310.2 | 275.6 | — |
| **Standoff Distance at Stop** | N/A | **2.18 m** | 0.56 m | $\ge$ 0.45 m |
| **Step Overhead (Baseline Succ)** | Baseline | 67.79% | 178.68% | $\le$ 15.0% |

**Oracle Timeout Seeds Identified (15 episodes):**
`[4000, 4015, 4018, 4020, 4021, 4023, 4024, 4026, 4036, 4048, 4049, 4052, 4053, 4055, 4056]`

---

## 2. Forensic Code Analysis of `drone_shield.py` (FSM, Governors & Timeout Causes)

File: [`drone_shield.py`](file:///c:/Users/Rushikesh/Desktop/Cool%20Ass%20Projects/Drone/drone_shield.py)

### 2.1 Trigger Logic
- **Code:** Line 780–782:
  ```python
  trigger_fired = (ttc < self.t_brake) or (clearance < self.d_min) or (telemetry.get("omni_clearance", float("inf")) < self.d_min)
  ```
- **Parameters:** Defaults are `t_brake = 0.28 s`, `d_min = 0.45 m`, `d_safe = 0.55 m` (lines 253–256).
- **Trigger Condition:** Fired when time-to-contact is below 0.28s, or forward ray clearance is below 0.45m, or omnidirectional Euclidean distance to any obstacle/wall is below 0.45m.
- **State Transition:** From `NOMINAL`, fires to `BRAKE` if `trigger_fired and self.cooldown_counter == 0` (line 792).

### 2.2 Braking & Speed Governor Logic
- **`BRAKE` State (lines 800–811):** Commands active instantaneous zero horizontal velocity setpoint `[0.0, 0.0, 0.0, 0.0]` (line 804). Stopping displacement in PyBullet is 0.000m because `p.resetBaseVelocity` overrides velocity substep-by-substep. Transitions to `SCAN` once `speed < 0.08 m/s or latency >= 1` (line 808).
- **Speed Governor (`_apply_speed_governor`, lines 582–700):**
  In `NOMINAL` state, caps commanded speed dynamically:
  $$v_{\text{cap}}(d) = \begin{cases} 0.0, & d \le d_{\text{safe}} \\ \min\left(3.0, \sqrt{2 \cdot a_{\text{dec}} \cdot (d - d_{\text{safe}})}\right), & d > d_{\text{safe}} \end{cases}$$
  with $a_{\text{dec}} = 4.5\text{ m/s}^2$ and $d_{\text{safe}} = 0.55\text{ m}$.
  Also throttles horizontal speeds approaching East/West perimeter walls ($\pm 4.6\text{m}$) and North/South perimeter walls ($\pm 9.6\text{m}$).

### 2.3 Reroute State & Exit Hysteresis
- **Direction Selection (`_evaluate_scan_direction`, lines 704–753):**
  Evaluates Left (-X) vs Right (+X) lateral options based on clearance, goal vector alignment $u_{\text{goal}}[0]$, quadratic wall proximity penalties, and anti-deadlock history penalty (lines 733–744).
- **Reroute Flight Dynamics (lines 844–874, 948–968):**
  Commands lateral speed:
  $$v_{x} = \text{sign} \cdot \min\left(v_{\text{reroute}}, \sqrt{2 \cdot a_{\text{dec}} \cdot \max(d_{\text{lat}} - d_{\text{min}}, 0)}\right)$$
  Forward speed $v_{y}$ is strictly governed:
  - If $d_{\text{fwd}} > d_{\text{safe}} + 0.20\text{ m}$ (0.75m): $v_y \le 1.6\text{ m/s}$.
  - If $d_{\text{min}} < d_{\text{fwd}} \le d_{\text{safe}} + 0.20\text{ m}$ (0.45m to 0.75m): $v_y \le 0.4\text{ m/s}$.
  - If $d_{\text{fwd}} \le d_{\text{min}}$ (0.45m): $v_y = 0.0\text{ m/s}$ (strictly zero forward velocity!).
- **Exit Condition (lines 933–939):**
  Requires `reroute_steps >= min_reroute_steps` (default 3 steps) AND:
  - If $u_{\text{goal}}[1] \ge 0$: forward corridor clearance $d_{\text{fwd}} \ge d_{\text{safe}} + 0.15\text{ m} = 0.70\text{ m}$ AND ray clearance $\ge d_{\text{safe}} = 0.55\text{ m}$.
  When met, transitions `REROUTE -> NOMINAL`, resets `deadlock_attempts = 0`, and initiates `cooldown_counter = 3` steps (lines 940–942).

### 2.4 Max-Duration, Deadlock Detection & Retreat Logic
- **Reroute Max Steps & Blockage (lines 889–896):**
  - Triggered if `reroute_steps >= max_reroute_steps` (default 40 steps) OR `effective_lat_clear < d_min` (lateral side blocked).
  - Increments `deadlock_attempts += 1`.
  - If `is_max_steps` OR (`deadlock_attempts >= 2 and rear_avail > d_min`), transitions to `RETREAT` (lines 897–903).
  - Otherwise (first lateral blockage), flips lateral direction directly (`LEFT <-> RIGHT`, line 905).
- **`RETREAT` State (lines 969–989):**
  Reverses along $-Y$ (away from goal) at speed $v_{\text{back}} \le 0.8\text{ m/s}$ for up to 6–8 steps. Upon completion, transitions back to `SCAN` (line 988).

### 2.5 Concrete Root Causes of the 25.0% - 30.0% Timeouts
Forensic step-by-step tracing of seed 4000 (`Counter({'NOMINAL': 173, 'REROUTE': 154, 'RETREAT': 122, 'SCAN': 34, 'BRAKE': 17})`) and the 15 timeout seeds revealed three primary failure modes:
1. **The Policy-Shield Ping-Pong Limit Cycle:**
   The reroute exit threshold requires only $d_{\text{fwd}} \ge 0.70\text{ m}$ ($d_{\text{safe}} + 0.15$). The unguided baseline policy has zero obstacle avoidance awareness. The moment the shield exits `REROUTE` to `NOMINAL`, the policy commands full-throttle forward cruise ($v_y \approx 2.4 - 2.8\text{ m/s}$). After exactly 3 cooldown steps, the drone has moved forward ~0.35m, placing clearance back at $\sim 0.35 - 0.45\text{ m}$. The shield immediately triggers `BRAKE` again (e.g. seed 4000 cycled through `BRAKE` 17 times!).
2. **Forward Speed Zeroing in Reroute:**
   While the drone is rerouting sideways past an obstacle whose front face is within $0.45\text{ m}$ ($d_{\text{min}}$), line 962 sets $v_y = 0.0$. If lateral flight is also slowed by proximity to an adjacent obstacle or wall, the drone hovers almost stationary, burning episode steps without making forward progress.
3. **Deadlock & Retreat Oscillation Trap:**
   When the drone attempts to reroute around an obstacle located near an arena wall ($x \approx \pm 3.9\text{ m}$), the wall penalty blocks further lateral movement ($d_{\text{wall}} < 0.45\text{ m}$). This increments `deadlock_attempts` and triggers `RETREAT`, which flies backwards 6–8 steps along $-Y$, then `SCAN`s, then re-enters `REROUTE`, hits the wall again, and repeats until the 500-step cap expires.
4. **Physical Bypass Feasibility Audit:**
   A full BFS 2D traversability analysis was executed on all 15 timeout seeds (accounting for the drone's 0.20m radius). **Result: 15/15 seeds (100.0%) possess valid, physically open horizontal bypass corridors.** There are **zero** corridor-spanning wall boxes or physically impassable layouts. All 15 timeouts are pure software control deadlocks within the shield FSM.

---

## 3. Environment Step Cap & Goal-Reached Verification

File: [`environment.py`](file:///c:/Users/Rushikesh/Desktop/Cool%20Ass%20Projects/Drone/environment.py)

- **Episode Step Cap:**
  - `self.max_steps = 500` (line 32, 38).
  - Truncation condition: `self.current_step >= self.max_steps` (lines 544–545). Truncation returns `truncated = True`, `terminated = False`.
- **Goal-Reached Condition:**
  - Goal coordinates: `self.goal_pos = np.array([0.0, 8.0, 1.5], dtype=np.float32)` (line 103).
  - Goal distance check: `dist_to_goal = float(np.linalg.norm(pos - self.goal_pos))` (line 503).
  - Goal reached condition: `goal_reached = dist_to_goal < 0.8` (line 504).
  - Terminal reward: `terminal_reward = 100.0`, `terminated = True` (lines 541–543).
  - **Speed Requirement:** **NONE.** There is zero velocity or speed constraint on reaching the goal. Termination triggers instantly the moment the drone's 3D Euclidean center is within $0.80\text{ m}$ of `goal_pos`.

---

## 4. Policy Distillation Forensics: Why `best_model_dagger_v1.pt` Weights Were Unchanged

File: [`shield_dagger.py`](file:///c:/Users/Rushikesh/Desktop/Cool%20Ass%20Projects/Drone/shield_dagger.py)

### 4.1 The Mechanism
Verification of SHA-256 hashes across checkpoints:
- `best_model.pt`: `A47610D967D689AD9A517E52D6D1788239B8C0F123BE430F0494B973A6AB2715`
- `best_model_baseline.pt`: `A47610D967D689AD9A517E52D6D1788239B8C0F123BE430F0494B973A6AB2715`
- `best_model_dagger_v1.pt`: `A47610D967D689AD9A517E52D6D1788239B8C0F123BE430F0494B973A6AB2715`

### 4.2 Exact Code Tracing
1. **Initial Seeding (lines 546–548):**
   ```python
   if not os.path.exists(args.output_model) and os.path.exists(args.init_model):
       shutil.copyfile(args.init_model, args.output_model)
   ```
   Before round 1, `args.output_model` (`best_model_dagger_v1.pt`) was created as a direct file copy of `args.init_model` (`best_model.pt`).
2. **Gradient Updates Were Performed:**
   In `train_bc_model` (lines 415–431), mini-batch updates via Adam, PyTorch AMP GradScaler, and MSE loss were genuinely executed on the candidate neural network:
   ```python
   pred = model(b_vis, b_vel)
   loss = nn.functional.mse_loss(pred, b_act)
   scaler.scale(loss).backward()
   scaler.step(optimizer)
   ```
3. **Model Selection Validation Gate (lines 601–643):**
   At the conclusion of each round, `validate_on_tuning_seeds` evaluated the candidate model with **Shield OFF** across tuning seeds (2000–2029).
   Candidate acceptance required:
   ```python
   is_better = (cand_col < best_collision_rate) or (
       math.isclose(cand_col, best_collision_rate, abs_tol=1e-5) and (cand_succ > best_success_rate)
   ) or ...
   ```
4. **Rejection & Rollback:**
   In all 4 rounds, candidate models achieved collision rates $\ge 60.0\%$ (failing to beat the baseline's 60.0% collision rate). Thus `is_better` evaluated to `False` in every round.
   Lines 639–642 executed:
   ```python
   print(f"[-] Candidate did not improve over best... Retaining current best.")
   if os.path.exists(args.output_model):
       current_model.load_state_dict(torch.load(args.output_model, map_location=device, weights_only=True))
   ```
   Because `torch.save(trained_model.state_dict(), args.output_model)` was never called to overwrite `best_model_dagger_v1.pt`, the initial file copy remained intact.

---

## 5. Behavioral Cloning Pipeline & Interface Compatibility Audit

### 5.1 Observation Space Alignment
- **Policy Network Expectation ([`model.py:26–28, 80–89`](file:///c:/Users/Rushikesh/Desktop/Cool%20Ass%20Projects/Drone/model.py#L26-L28)):**
  Dual-input architecture: `visual_obs` of shape `(5, 84, 84)` (3 RGB channels normalized in $[0, 1]$ + 2 optical flow channels $(u, v)$), and `velocity_obs` of shape `(3,)` (linear velocities $[v_x, v_y, v_z]$).
- **Evaluation Pipeline ([`evaluate_and_visualize.py:275–283`](file:///c:/Users/Rushikesh/Desktop/Cool%20Ass%20Projects/Drone/evaluate_and_visualize.py#L275-L283)):**
  Extracts `obs["visual"]` (shape `(5, 84, 84)`) and `obs["velocity"]` (shape `(3,)`) from environment and passes tensors of matching shape and type.
- **DAgger Data Pipeline ([`shield_dagger.py:125–136, 184–190`](file:///c:/Users/Rushikesh/Desktop/Cool%20Ass%20Projects/Drone/shield_dagger.py#L125-L136)):**
  Saves raw `obs["visual"]` (shape `(5, 84, 84)`) and `obs["velocity"]` (shape `(3,)`), assembling into dataset `(N, 5, 84, 84)` and `(N, 3)` (lines 338–346).
- **Verdict:** **PERFECT MATCH.** Observation formatting is completely consistent across training, DAgger rollouts, and evaluation.

### 5.2 Action Space & Action Scaling Alignment
- **Environment Action Interface ([`environment.py:87, 440–442`](file:///c:/Users/Rushikesh/Desktop/Cool%20Ass%20Projects/Drone/environment.py#L440-L442)):**
  4D continuous box in $[-1.0, 1.0]$. Actions are scaled by $3.0\text{ m/s}$ for linear velocities and $1.0\text{ rad/s}$ for yaw rate:
  $$v_{\text{target}} = \text{action}[:3] \times 3.0, \quad \dot{\psi} = \text{action}[3] \times 1.0$$
- **Policy Network Output ([`model.py:64–69`](file:///c:/Users/Rushikesh/Desktop/Cool%20Ass%20Projects/Drone/model.py#L64-L69)):**
  Actor mean output layer ends with `nn.Tanh()`, producing 4 continuous values in $[-1.0, 1.0]$.
- **Supervisor Labels in DAgger ([`shield_dagger.py:153–159`](file:///c:/Users/Rushikesh/Desktop/Cool%20Ass%20Projects/Drone/shield_dagger.py#L153-L159)):**
  - Normal navigation: `expert_action(env)` from [`pretrain_bc.py:125–126`](file:///c:/Users/Rushikesh/Desktop/Cool%20Ass%20Projects/Drone/pretrain_bc.py#L125-L126), strictly clipped to $[-1.0, 1.0]$.
  - Intervention label: `info["executed_action"]` from [`drone_shield.py:691–694, 872–873, 966–967`](file:///c:/Users/Rushikesh/Desktop/Cool%20Ass%20Projects/Drone/drone_shield.py#L691-L694), divided by $3.0$ and clipped to $[-1.0, 1.0]$.
- **Loss Computation ([`shield_dagger.py:420`](file:///c:/Users/Rushikesh/Desktop/Cool%20Ass%20Projects/Drone/shield_dagger.py#L420)):**
  MSE loss between `pred` (Tanh outputs in $[-1, 1]$) and `b_act` (supervisor labels in $[-1, 1]$).
- **Verdict:** **PERFECT MATCH.** Action space dimension (4D) and continuous scaling ($[-1.0, 1.0]$) are strictly aligned across all components.

---

## 6. Seed Protocol Audit & Overlap Detection

We analyzed all seed ranges used across the codebase:
- **`pretrain_bc.py`:** Generates demos using seeds `0` to `299` (`list(range(0, args.n_demo_envs))`, line 142).
- **`train.py`:** Initializes parallel workers with `seed = 42 + i * 100` for $i \in [0, 11]$ (seeds 42, 142, ..., 1142) and unseeded resets.
- **Prior Held-Out Seeds (v1):** `1000–1049` (Burned).
- **Prior Tuning Seeds (v1):** `2000–2029`.
- **Prior DAgger Rollouts (v1):** `shield_dagger.py` lines 502–508 and line 674 explicitly ran with `rollout-seed-start 3000`, 4 rounds $\times$ 30 episodes = **seeds `3000–3119`** to collect `bc_demos_dagger_v1.npz`.

### CRITICAL FINDING: Proposed Seed Overlap
- The prompt proposes:
  - Final Held-Out: `3000–3049` (and fallback `3100–3149`).
  - DAgger Training Layouts: `6000–6999`.
  - Diagnosis & Tuning: `4000–4059`.
- **OVERLAP DETECTED:** Seeds `3000–3049` (and `3100–3119`) were **already consumed** by the previous DAgger rollout data collection. Evaluating a newly distilled policy on seeds 3000–3049 violates the strict held-out certification guarantee because `bc_demos_dagger_v1.npz` contains rollouts on those exact layouts.
- **RECOMMENDED DISJOINT HELD-OUT RANGES:**
  - **Certified Final Held-Out:** `5000–5049` (completely untouched, 50 seeds).
  - **Held-Out Fallback / Recertification:** `5100–5149` (completely untouched, 50 seeds).
  - **DAgger Training Layouts:** `6000–6999` (as proposed).
  - **Diagnosis & Tuning Layouts:** `4000–4059` (as proposed).

---

## 7. False Premises & Codebase Inconsistencies Identified

1. **`run_project.bat` Menu Options 7–10:**
   - *Prompt Premise:* "run_project.bat (menu options 7-10)"
   - *Evidence:* [`run_project.bat`](file:///c:/Users/Rushikesh/Desktop/Cool%20Ass%20Projects/Drone/run_project.bat#L15-L33) contains only options `[0–6]` (`CHOICE` variable options 0 to 6). Options 7 to 10 are completely absent.
2. **Final Held-Out Seed Range 3000–3049:**
   - *Prompt Premise:* "FINAL HELD-OUT: 3000-3049, touched only for the final numbers of a frozen candidate."
   - *Evidence:* [`shield_dagger.py:674`](file:///c:/Users/Rushikesh/Desktop/Cool%20Ass%20Projects/Drone/shield_dagger.py#L674) defaults to `--rollout-seed-start 3000` across 4 rounds $\times$ 30 episodes (`3000–3119`). Seeds 3000–3049 are in `bc_demos_dagger_v1.npz` and are not held out.
3. **Impassable Corridors / Boxes Spanning Corridors:**
   - *Prompt Premise:* "If the analysis shows that some timeouts are caused by obstacles that left/right cannot bypass (for example boxes spanning the corridor), count and report them as their own category and leave them unfixed."
   - *Evidence:* Obstacle extents in [`environment.py:189, 200`](file:///c:/Users/Rushikesh/Desktop/Cool%20Ass%20Projects/Drone/environment.py#L189) are max half-extent 0.65m in a 9.2m corridor. Exact 2D grid pathfinding on all 15 timeout seeds confirms **15/15 seeds have valid, open horizontal paths**. No obstacles span the corridor.
