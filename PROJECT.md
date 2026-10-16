# Project: Stop, Hover & Re-Route (SHR) Drone Safety Shield & Policy Distillation

## Architecture & System Overview
The system provides a two-tier safety architecture for an autonomous drone trained in PyBullet + Gymnasium with PPO/BC:
1. **Tier 1: Safety Shield (`drone_shield.py`)** — A `gymnasium.Wrapper` (`StopAndRerouteShield`) that monitors the drone state, predicts time-to-contact (TTC) to obstacles and walls, governs nominal speeds smoothly, and executes a deterministic FSM (NOMINAL -> BRAKE -> SCAN -> REROUTE -> NOMINAL) to intercept collisions before they occur.
   - Sensor modes: `oracle` (privileged simulator queries: raycasts / closest points) and `camera` (central depth/flow).
2. **Tier 2: Policy Distillation (`shield_dagger.py`)** — DAgger (Dataset Aggregation) loop fine-tuning the policy network to internalize safe obstacle avoidance behaviors using a fused supervisor (shield override + potential field expert), reducing reliance on active intervention while retaining shield-OFF safety.

## Code Layout & File Ownership
Strict disjoint write ownership is enforced across the team to prevent conflicts:

| Agent / Role | Primary Files Owned | Description |
|---|---|---|
| **A0 Lead / Integrator** | `PROJECT.md`, `GATE_STATUS.md`, `DEAD_ENDS.md`, orchestrator state | Coordination, gate status, synthesis, reports |
| **A1 Recon & Accessors** | `environment.py` (read-only `@property` accessors only), `RECON.md` | Non-intrusive environment inspection & accessors, baseline measurement |
| **A2 Shield** | `drone_shield.py` | Safety wrapper implementation, FSM, braking, scanning, rerouting |
| **A3 Benchmark & Forensics** | `eval_shield.py`, `evaluate_and_visualize.py` (additive `--shield` flag only), `reports/*` | Evaluation harness, Wilson 95% CIs, crash telemetry & forensics |
| **A4 Perf Profiler** | `PERF.md` | Profiling step execution, bottlenecks, SPS across workers (read-only) |
| **A5 Distillation** | `shield_dagger.py`, `train_anchor.py` (if needed, copy of train.py) | DAgger supervisor dataset generation, policy fine-tuning |

Existing files modified:
- `environment.py`: ONLY additive read-only `@property` accessors returning copies (zero dynamics/step/reward changes).
- `evaluate_and_visualize.py`: ONLY optional `--shield` and `--shield-mode` flags (default OFF).

Protected files (NEVER overwrite):
- `best_model.pt` -> copied to `best_model_baseline.pt` at start.
- `bc_demos.npz` -> original demonstration data.

## Compute Lock Coordination
- Hardware: Laptop RTX 5060 + i7-14700HX shared among tasks.
- Exactly ONE heavy job (evaluation batch, profiling, DAgger rollout, training) runs at a time.
- All heavy operations must check for existence of `.compute.lock`. If absent, create `.compute.lock` with worker ID and PID; on finish, delete `.compute.lock`.

## Feature Inventory
| # | Feature | Description | Milestone | Source |
|---|---------|-------------|-----------|--------|
| 1 | Baseline & Stopping Characterization | Measure baseline rates on 5 reference seeds & 30 tuning seeds; quantify open-loop zero-action stopping dynamics & FOV velocity alignment | Gate 0 | ORIGINAL_REQUEST §R1 |
| 2 | Read-Only Property Accessors | Additive `@property` accessors in `environment.py` for drone pos, vel, depth, obstacle info without altering step/dynamics | Gate 0 | ORIGINAL_REQUEST §R1 |
| 3 | Profiling & Bottleneck Analysis | Time breakdown of physics, camera render, flow, obs assembly; measure SPS on 8 & 12 workers | Gate 0 | ORIGINAL_REQUEST §R1 |
| 4 | Dual-Mode Sensing Shield | Sensing with `"oracle"` (raycast batch / closest points) and `"camera"` (central depth window) | Gate 1 | ORIGINAL_REQUEST §R2 |
| 5 | TTC Trigger & Speed Governor | Time-to-contact trigger `ttc < t_brake` OR `clearance < d_min`; smooth nominal speed scaling `v_cap(d)` | Gate 1 | ORIGINAL_REQUEST §R2 |
| 6 | SHR FSM (Brake-Scan-Reroute) | Deterministic FSM: measured-dynamics active brake, clearance+goal scan, closed-loop lateral reroute, anti-deadlock | Gate 1 | ORIGINAL_REQUEST §R2 |
| 7 | Evaluation & Crash Forensics Harness | `eval_shield.py`, `--shield` CLI flag in `evaluate_and_visualize.py`, Wilson 95% CIs, crash forensics telemetry | Gate 1 | ORIGINAL_REQUEST §R2 |
| 8 | Held-Out Shield Certification | 50 held-out seeds (1000–1049) evaluation; freeze + tag `shield-v1`; verify all target thresholds | Gate 2 | ORIGINAL_REQUEST §R3 |
| 9 | DAgger Distillation Pipeline | `shield_dagger.py`: rollouts with decaying beta, fused supervisor labeling, dataset aggregation, BC fine-tuning | Gate 3 | ORIGINAL_REQUEST §R4 |
| 10 | Distilled Policy Held-Out Verification | Held-out evaluation of distilled policy (shield OFF vs shield ON) against acceptance criteria | Gate 3 | ORIGINAL_REQUEST §R4 |

## Milestones
| Gate | Name | Scope | Dependencies | Status |
|---|------|-------|-------------|--------|
| **Gate 0** | Recon & Profiling | A1 `RECON.md`, baseline reproduction, stopping dynamics, `environment.py` accessors; A4 `PERF.md` SPS profiling | None | DONE |
| **Gate 1** | Shield Implementation & Tuning | A2 `drone_shield.py`, A3 `eval_shield.py`, `--shield` flag, tuning on seeds 2000–2029, crash forensics | Gate 0 | DONE |
| **Gate 2** | Held-Out Certification | Run ONCE on held-out seeds 1000–1049, verify targets (collision <= 2%, success >= 85%, timeout <= 5%), tag `shield-v1` | Gate 1 | DONE |
| **Gate 3** | Policy Distillation | A5 `shield_dagger.py`, DAgger training, validation on tuning seeds, final held-out certification | Gate 2 | DONE |

## Seed Protocol
- Reference seeds: `[101, 202, 303, 404, 505]` — reproduction and reference check.
- Tuning seeds: `2000–2029` (30 seeds) — all parameter tuning and intermediate validation.
- Held-out seeds: `1000–1049` (50 seeds) — strictly touched ONLY at Gate 2 and Gate 3.

## Interface Contracts
### `environment.py` `@property` Accessors (Read-Only)
- `drone_pos`: returns `np.ndarray` of shape `(3,)`, float32, world frame position `(x, y, z)`. Copy, not internal reference.
- `drone_vel`: returns `np.ndarray` of shape `(3,)`, float32, world frame linear velocity `(vx, vy, vz)`. Copy.
- `drone_orientation`: returns `np.ndarray` of shape `(4,)`, float32, quaternion or euler angles.
- `last_depth_image`: returns `np.ndarray` of shape `(84, 84)`, float32, copy of latest raw camera depth.
- `obstacle_ids` / `obstacle_positions`: returns list/array of obstacle bodies for oracle queries.

### `StopAndRerouteShield` (`gymnasium.Wrapper`)
- Constructor: `__init__(self, env, sensor_mode="oracle", enabled=True, ...params)`
- `step(action)`:
  - Intercepts `action`, queries sensors, updates state machine.
  - Returns `obs, reward, terminated, truncated, info`.
  - `info` contains: `shield_state`, `policy_action`, `executed_action`, `intervened` (bool), `ttc`, `clearance`, `standoff_distance`.
  - Does NOT alter observations, reward, or termination semantics.
