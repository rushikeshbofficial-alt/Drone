# Stop, Hover & Re-Route (SHR) Drone Safety Shield: Gate 0 Reconnaissance Report

**Author:** A1 (Recon & Accessors Specialist)  
**Date:** 2026-10-15  
**Milestone:** Gate 0 — Reconnaissance, Physics Profiling & Environment Accessors  
**Git Branch:** `shr-shield`  
**Reference Model:** `best_model.pt` (backed up to `best_model_baseline.pt`)  

---

## Executive Summary

This report delivers the authoritative codebase reconnaissance, empirical dynamics characterization, Trust Rules 1–6 audit, baseline verification with Wilson 95% confidence intervals, and additive interface accessors for Gate 0 of the Stop, Hover & Re-Route (SHR) drone safety shield project.

### Key Reconnaissance Findings
1. **Kinematics & Coordinate Frames:** Drone actions command **WORLD-frame velocities** ($[-3.0, +3.0]$ m/s along world $X, Y, Z$), NOT body-frame velocities. The camera is rigidly mounted to the body pointing along body $+Y$, but the policy steers without yawing to face its velocity vector.
2. **FOV Blindspot Crisis (Empirical):** In baseline rollouts across the 5 reference seeds, **31.7% of all control steps** had the drone's velocity direction angled $> 32.5^\circ$ away from the optical axis—completely **OUTSIDE** the $65^\circ$ camera FOV. In hard lateral dodges (Seed 202), this reached **38.4%**. Consequently, a camera-only shield is structurally blind to lateral obstacle collisions and wall strikes.
3. **Active Braking Reality (Zero-Action Deceleration):** Contrary to assumptions that the drone "lacks active braking" and must coast, the physics engine enforces velocity setpoints via `p.resetBaseVelocity` (or direct velocity updates in analytical mode) on **every one of the 8 substeps** at 240 Hz. When zero action (`[0, 0, 0, 0]`) is commanded from full forward ($3.0$ m/s) or lateral ($3.0$ m/s) flight, velocity drops to **$0.000$ m/s on substep 0 of step 1**, yielding an empirical stopping distance of **$0.000000$ m** and stop latency of **$0$ control steps**.
4. **Depth Sensor Artifacts:** Camera depth includes both the **floor plane ($z=0$)** and **arena boundary walls** in meters ($[0.1, 12.0]$ m). Naive `np.min` across the whole frame triggers false collisions on the floor at $z=1.5$ m altitude; the shield must inspect a centralized horizon ROI or use oracle range queries.
5. **Baseline Reproduction:** Reference seeds `[101, 202, 303, 404, 505]` reproduced the user baseline with mathematical exactness: **20.0% success / 80.0% collision** (Mean reward: $-66.81 \pm 165.29$, Min clearance: $0.12$ m). On the 30 tuning seeds (`2000–2029`), baseline performance is **40.0% success / 60.0% collision** (Mean reward: $+18.99 \pm 129.17$, Min clearance: $0.15$ m).

---

## Point a: Coordinate Frames, Units & Depth Sensor Characterization

### 1. Position (`drone_pos`)
- **Code Reference:** `environment.py:96`, `environment.py:125`, `environment.py:431-437`, `environment.py:470-474`, `environment.py:481-482`.
- **Data Type & Shape:** `np.ndarray` of shape `(3,)`, `dtype=np.float32`.
- **Units:** Meters ($m$).
- **Coordinate Frame:** Cartesian World Frame $[x, y, z]$.
  - $x$: Lateral axis, arena limits $[-4.6, +4.6]$ m (clamped at `ARENA_X_LIM = 4.6`).
  - $y$: Longitudinal axis, arena limits $[-9.6, +9.6]$ m (clamped at `ARENA_Y_LIM = 9.6`).
  - $z$: Vertical altitude axis, arena limits $[+0.15, +3.5]$ m (`ARENA_Z_MIN = 0.15`, `ARENA_Z_MAX = 3.5`).
- **Nominal Positions:**
  - Start Position: `np.array([0.0, -8.0, 1.5], dtype=np.float32)`.
  - Goal Position: `np.array([0.0, 8.0, 1.5], dtype=np.float32)`.

### 2. Velocity (`drone_vel`)
- **Code Reference:** `environment.py:97`, `environment.py:423-426`, `environment.py:441-452`, `environment.py:468-475`.
- **Data Type & Shape:** `np.ndarray` of shape `(3,)`, `dtype=np.float32`.
- **Units:** Meters per second ($m/s$).
- **Coordinate Frame:** **WORLD Frame** $[v_x, v_y, v_z]$.
  - In `step(action)` (`environment.py:441`), `target_vel = action[:3] * 3.0`.
  - In PyBullet: `p.resetBaseVelocity(self.drone_id, linearVelocity=target_vel.tolist(), ...)`.
  - In analytical mode: `self.drone_pos += self.drone_vel * self.dt` directly integrates `self.drone_vel` along world Cartesian coordinates.
  - In `_get_observation()` (`environment.py:423`), PyBullet calls `p.getBaseVelocity(self.drone_id)`, which returns linear velocity in world Cartesian coordinates.
  - **Critical semantic:** The policy commands velocity in the world coordinate frame. `action[0]` moves the drone world-East/West ($X$), `action[1]` moves the drone world-North/South ($Y$), irrespective of drone heading.

### 3. Camera Depth Map (`last_depth_map` / `last_depth_image`)
- **Code Reference:** `environment.py:49-55`, `environment.py:210-245`, `environment.py:247-308`.
- **Resolution & Optics:**
  - Dimensions: $84 \times 84$ pixels.
  - Field of View (FOV): $65.0^\circ$ diagonal/horizontal.
  - Aspect Ratio: $1.0$.
  - Near plane ($near\_val$): $0.1$ m.
  - Far plane ($far\_val$): $12.0$ m.
- **Physical Mounting & Alignment:**
  - Rigidly attached to drone body.
  - In PyBullet (`environment.py:217-220`):
    - `forward = rot_matrix @ np.array([0.0, 1.0, 0.0])`
    - `cam_pos = np.array(pos) + rot_matrix @ np.array([0.0, 0.2, 0.0])`
    - Target pos = `cam_pos + forward`.
    - Camera looks forward along drone body $+Y$ axis.
- **Buffer Output & Unit Conversion:**
  - In PyBullet (`environment.py:242-243`):
    `depth_buffer` normalized float $[0, 1]$ is converted via:
    `depth_meters = far_val * near_val / (far_val - (far_val - near_val) * depth_buffer)`.
  - In analytical mode (`environment.py:247-308`):
    Vectorized raycasting directly returns Euclidean distance in meters.
- **Inclusion of Floor & Arena Walls:**
  - **Floor Included? YES.**
    - PyBullet loads `plane.urdf` at $z=0$ (`environment.py:133`), rendered by `p.getCameraImage`.
    - Analytical mode explicitly intersects rays with $z=0$ plane (`environment.py:263-275`):
      `floor_mask = rz < -1e-4`, `t_floor = -cam_z / rz`.
    - At cruising altitude $z=1.5$ m with half-FOV $32.5^\circ$, floor rays hit the ground at distance $d \approx 1.5 / \sin(32.5^\circ) \approx 2.79$ m. A global `np.min` over all pixels would falsely detect an obstacle at $2.79$ m even in a completely empty room!
  - **Walls Included? YES.**
    - Four boundary walls are instantiated as box collision shapes in `obstacle_specs` (`environment.py:166-179`): $y = \pm 10.0$ m and $x = \pm 5.0$ m. Both renderers trace and return exact depth to walls.

---

## Point b: Drone Yaw, Camera Attachment, Frame Mapping & FOV Blindspot Quantification

### 1. Drone Yaw Mechanics
- **Code Reference:** `environment.py:442`, `environment.py:450`, `environment.py:469`, `environment.py:483-484`.
- Yaw rate is actively controlled: `yaw_rate = action[3] * 1.0` (rad/s).
- PyBullet: `angularVelocity=[0.0, 0.0, float(yaw_rate)]`.
- Analytical: `self.drone_orn[2] += yaw_rate * self.dt`.
- The drone can and does rotate around its vertical $Z$-axis.

### 2. Camera Attachment
- The camera is rigidly fixed to the drone body heading:
  $\vec{f}_{cam} = [\sin(\psi), \cos(\psi), 0]^T$, where $\psi$ is drone yaw (`environment.py:256-257`, `environment.py:217`).

### 3. Velocity Frame Mapping ($v_x / v_y$)
- Actions dictate world-frame translations:
  - $v_x = 3.0 \cdot action[0]$
  - $v_y = 3.0 \cdot action[1]$
- Because translation does not depend on heading, the drone operates as an omnidirectional holonomic vehicle in world coordinates while retaining a directional sensor.
- When policy commands a lateral avoidance maneuver (e.g. $v_x = -2.63$ m/s, $v_y = 1.5$ m/s), flight path angle relative to world $+Y$ is:
  $$\theta_v = \arctan2(v_x, v_y) = \arctan2(-2.63, 1.5) \approx -60.3^\circ$$
- If the drone has not yawed ($\psi = 0^\circ$), the velocity vector is $60.3^\circ$ off the camera optical axis. Since camera horizontal half-FOV is $65^\circ / 2 = 32.5^\circ$, the drone travels at an angle **$27.8^\circ$ outside the visible cone**.

### 4. Empirical FOV Blindspot Quantification (Baseline Rollouts)
Using `recon_measurements.py`, we tracked step-by-step velocity direction versus camera forward orientation on all 5 reference seeds with the trained baseline model:

| Seed | Outcome | Episode Steps | Steps Velocity Outside FOV ($>32.5^\circ$) | % Steps Outside FOV | Min Clearance | Primary Crash Cause |
|---|---|:---:|:---:|:---:|:---:|---|
| **101** | OBSTACLE_COLLISION | 81 | 26 | **32.1%** | 0.11 m | Lateral drift into cylinder while heading forward |
| **202** | WALL_OOB | 185 | 71 | **38.4%** | 0.04 m | Extreme lateral dodge ($v_x=-2.63$) into perimeter wall |
| **303** | SUCCESS | 144 | 36 | **25.0%** | 0.10 m | Skimmed obstacles along corridor |
| **404** | OBSTACLE_COLLISION | 59 | 12 | **20.3%** | 0.11 m | High-speed impact ($2.9$ m/s) with diagonal alignment |
| **505** | OBSTACLE_COLLISION | 45 | 18 | **40.0%** | 0.23 m | Oblique collision at $3.2$ m/s |
| **OVERALL** | — | **514** | **163** | **31.7%** | **0.12 m** | **1 in 3 steps blind to flight direction** |

**Architectural Implication:** A vision-only camera depth shield that looks forward is blind to 31.7% of the drone's movement trajectory. A robust safety shield must either:
1. Use **oracle 360° / velocity-aligned sensing** (raycasting along the velocity vector $\vec{v}$), or
2. Force the drone to coordinate yaw with flight velocity (active alignment), or
3. Cap lateral velocity so the velocity vector stays within camera FOV.

---

## Point c: Measured Open-Loop Stopping Behavior & Braking Dynamics

### Empirical Braking Test Protocol
A dedicated experimental harness in `recon_measurements.py` tested the response of the environment to an active brake command (commanding zero action `[0, 0, 0, 0]` after full-speed flight):
1. **Forward Flight Test:** Accelerate drone at $+3.0$ m/s forward ($action = [0, 1, 0, 0]$) for 10 control steps.
2. **Command Zero Action:** Command $action = [0, 0, 0, 0]$ and log substep/step kinematics.
3. **Lateral Flight Test:** Accelerate drone at $+3.0$ m/s lateral ($action = [1, 0, 0, 0]$) for 10 control steps, then command zero.

### Empirical Stopping Measurement Results

| Flight Axis | Initial Velocity Before Stop ($m/s$) | Commanded Action | Velocity After 1 Control Step ($m/s$) | Stop Displacement ($m$) | Substeps to Full Stop ($v < 0.01$) | Stop Latency ($s$) |
|---|:---:|:---:|:---:|:---:|:---:|:---:|
| **Longitudinal (World +Y)** | `[0.000, 3.000, 0.000]` | `[0, 0, 0, 0]` | `[0.000, 0.000, 0.000]` | **0.000000 m** | **1 substep (substep 0)** | **0.000 s** |
| **Lateral (World +X)** | `[3.000, 0.000, 0.000]` | `[0, 0, 0, 0]` | `[0.000, 0.000, 0.000]` | **0.000000 m** | **1 substep (substep 0)** | **0.000 s** |

### Physics Mechanism Explanation
- In `environment.py:441-476`, the control loop executes 8 physics substeps per control step ($240$ Hz physics / $24$ Hz control):
  ```python
  target_vel = action[:3] * 3.0
  for _ in range(self.physics_substeps):
      if self.pybullet_active:
          p.resetBaseVelocity(self.drone_id, linearVelocity=target_vel.tolist(), ...)
          p.stepSimulation(...)
      else:
          self.drone_vel = target_vel.copy()
          self.drone_pos += self.drone_vel * self.dt
  ```
- Because `resetBaseVelocity` overrides body velocity at every substep, the moment `action = [0, 0, 0, 0]` is dispatched, `target_vel = [0, 0, 0]`. On **substep 0**, PyBullet and the analytical integrator set velocity to zero.
- **Conclusion:** The drone possesses **instantaneous active braking capability**. Stopping distance from $3$ m/s is **zero meters**, with **zero substep latency**. There is no aerodynamic coasting or momentum drift. Braking failure in baseline rollouts is entirely due to the neural policy commanding non-zero forward/lateral velocity into obstacles right up to the moment of impact.

---

## Point d: Collision Detection & Impact Telemetry

### 1. PyBullet Collision Pipeline
- **Code Reference:** `environment.py:480-486`.
- Detection mechanism: `contact_points = p.getContactPoints(bodyA=self.drone_id, physicsClientId=self.client_id)`.
- Flag: `collision = len(contact_points) > 0`.
- Data available at contact:
  - `contactFlag`: Contact point bitmask.
  - `bodyB`: PyBullet ID of the colliding entity (differentiates ground plane vs obstacle vs wall).
  - `positionOnA`, `positionOnB`: Contact point coordinates in world space.
  - `contactNormalOnB`: Surface normal vector at contact point.
  - `contactDistance`: Distance/penetration depth ($< 0$ during interpenetration).
  - `normalForce`: Impact force applied.

### 2. Analytical Raycaster Collision Pipeline
- **Code Reference:** `environment.py:487-498`.
- Evaluates Euclidean distance to cylinder/box obstacle centers:
  `dist = np.linalg.norm(pos[:2] - np.array([ox, oy]))`.
  Collision triggered if `dist < (obs_r + 0.25)` ($0.25$ m represents drone collision radius).

### 3. Arena Boundary & Out-of-Bounds (OOB) Clamping
- **Code Reference:** `environment.py:113-116`, `environment.py:431-437`, `environment.py:458-466`, `environment.py:471-476`, `environment.py:500-502`.
- Hard limits: $X \in [-4.6, 4.6]$ m, $Y \in [-9.6, 9.6]$ m, $Z \in [0.15, 3.5]$ m.
- Clamping occurs inside the substep loop: if the drone crosses the boundary, it is clamped, its velocity is zeroed, and `self.out_of_bounds = True`.
- At step termination:
  `if self.out_of_bounds: collision = True`.
- **Telemetry Distinction:** In `info`, previously only `collision: True/False` was reported without distinguishing obstacle collision from perimeter wall impact. With our additive accessors and forensic classification, episodes are uniquely partitioned into:
  `SUCCESS | OBSTACLE_COLLISION | WALL_OOB | TIMEOUT`.

---

## Point e: Trust Rules 1–6 Verification Audit

| Trust Rule | Question / Premise | Code Evidence | Verdict | Detailed Technical Finding |
|---|---|---|:---:|---|
| **Rule 1** | Does `train.py` use `multiprocessing.shared_memory` vs `SubprocVecEnv` with Pipes? | `train.py:70-80`<br>`train.py:122-140`<br>`train.py:179-193` | **HYBRID (Both)** | `train.py` implements a hybrid architecture: `multiprocessing.shared_memory.SharedMemory` handles the large visual observation tensors (`(n_envs, 5, 84, 84)` float32) with zero-copy shared buffers, while `mp.Pipe()` handles IPC commands (`"step"`, `"reset"`, `"close"`) and scalar metadata (velocities, rewards, dones, infos). If shared memory creation fails, it falls back gracefully to pure pipe transfer. |
| **Rule 2** | Does `--bc-anchor-coef` flag exist anywhere in the repository? | `train.py:513-520`<br>`train.py:802-809`<br>`train.py:983` | **EXISTS** | Speculation that `--bc-anchor-coef` was missing is FALSE. It is defined in CLI parser (`train.py:983`, default 0.0), creates a frozen `ref_model` anchor (`train.py:513`), and penalizes policy divergence in the PPO loss via `args.bc_anchor_coef * torch.mean((cur_act - ref_act)**2)` (`train.py:808`). |
| **Rule 3** | Claimed SPS of 1,200–2,500 on 12 workers. | `train.py:853`<br>`profile_perf.py`<br>`PERF.md` | **NOTED / PROFILED** | Profiling by A4 in parallel documents actual worker SPS. In single-worker headless evaluation (`evaluate_and_visualize.py`), step latency is $2.5 - 3.1$ ms ($320 - 400$ SPS). |
| **Rule 4** | Does the safety shield give "0% collisions by design"? | Physics, sensor latency & discrete sampling analysis | **HYPOTHESIS (FALSE by design)** | Safety shields cannot guarantee 0% collisions by design in discrete-time control (24 Hz, $\Delta t = 41.7$ ms). Latency between sensing and actuation, velocity-FOV blindspots (31.7% of steps blind to camera), corner traps, and obstacle occlusions require empirical verification. Must be treated as a testable empirical hypothesis, never an assumption. |
| **Rule 5** | Does the drone "lack active braking"? | `environment.py:441-476`<br>`recon_measurements.py:35-80` | **FALSE (Instant active braking)** | Actions are velocity setpoints multiplied by $3.0$ m/s, directly re-applied every substep via `resetBaseVelocity`. Commanding zero action stops the drone from $3.0$ m/s in **0.000 s and 0.000000 m**. No deceleration ramps or drag coasts are required. |
| **Rule 6** | Attribute names and semantics (`drone_pos`, `drone_vel`, `last_depth_map`). | `environment.py:96-105`<br>`environment.py:244`<br>`environment.py:307`<br>`environment.py:423-426` | **VERIFIED & HARMONIZED** | Real names confirmed: `drone_pos` (World frame, $m$), `drone_vel` (World frame, $m/s$), `last_depth_map` (meters, $[0.1, 12.0]$). Real orientation attribute was `drone_orn` (Euler rad). Additive `@property` accessors harmonize both aliases (`drone_orientation`, `last_depth_image`, `obstacle_positions`) with defensive copy protection. |

---

## Point f: Baseline Reproduction & Tuning-Seed Benchmarking

### 1. Reproduction of 5 Reference Seeds
Evaluation command executed under `.compute.lock`:
`python evaluate_and_visualize.py --checkpoint best_model.pt --eval-mode unseen --headless`

#### Raw Live Execution Console Output:
```
[*] Evaluation Running on Device: cuda
[*] Loading checkpoint: best_model.pt
[+] Checkpoint loaded successfully.
[*] Evaluating on 5 UNSEEN environment seeds...
[Env 1/5 seed=101] COLLISION | Steps: 81 | Reward: -194.73 | MinClearance: 0.11m | Fidelity: 0.071 | Latency: 5.42ms
[Env 2/5 seed=202] COLLISION | Steps: 185 | Reward: -299.88 | MinClearance: 0.04m | Fidelity: 0.075 | Latency: 2.32ms
[Env 3/5 seed=303] SUCCESS | Steps: 144 | Reward: 170.42 | MinClearance: 0.10m | Fidelity: 0.044 | Latency: 2.33ms
[Env 4/5 seed=404] COLLISION | Steps: 59 | Reward: -36.43 | MinClearance: 0.11m | Fidelity: 0.026 | Latency: 2.30ms
[Env 5/5 seed=505] COLLISION | Steps: 45 | Reward: 26.55 | MinClearance: 0.23m | Fidelity: 0.052 | Latency: 2.30ms

=================================================================
      FINAL EVALUATION & EXPLAINABILITY REPORT SUMMARY      
=================================================================
Environments Evaluated        : 5 (unseen mode)
Mean Episode Reward           : -66.81 +/- 165.29
Success Rate (Goal Reached)  : 20.0%
Collision Rate               : 80.0%
Mean Minimum Clearance       : 0.12 m
Mean Explanation Fidelity IoU: 0.0535
Mean Decision Latency        : 2.93 ms (340.9 FPS)
=================================================================
```

| Seed | Outcome | Steps | Reward | Min Clearance | Telemetry Notes |
|---|:---:|:---:|:---:|:---:|---|
| **101** | OBSTACLE_COLLISION | 81 | -194.73 | 0.11 m | Crashed into cylinder at $3.0$ m/s |
| **202** | WALL_OOB | 185 | -299.88 | 0.04 m | Cleared central obstacles, made hard lateral dodge ($v_x=-2.63$), hit West wall |
| **303** | SUCCESS | 144 | +170.42 | 0.10 m | Navigated corridor, skimmed obstacle with 0.10 m clearance |
| **404** | OBSTACLE_COLLISION | 59 | -36.43 | 0.11 m | High-speed forward impact at $2.9$ m/s |
| **505** | OBSTACLE_COLLISION | 45 | +26.55 | 0.23 m | Oblique impact at $3.2$ m/s |

**Summary Statistics (5 Reference Seeds):**
- **Success Rate:** $1/5 = \mathbf{20.0\%}$ (Wilson 95% CI: $[3.6\%, 62.4\%]$)
- **Obstacle Collision Rate:** $3/5 = \mathbf{60.0\%}$ (Wilson 95% CI: $[23.1\%, 88.2\%]$)
- **Wall OOB Rate:** $1/5 = \mathbf{20.0\%}$ (Wilson 95% CI: $[3.6\%, 62.4\%]$)
- **Total Collision Rate:** $4/5 = \mathbf{80.0\%}$ (Wilson 95% CI: $[37.6\%, 96.4\%]$)
- **Timeout Rate:** $0/5 = \mathbf{0.0\%}$ (Wilson 95% CI: $[0.0\%, 43.4\%]$)
- **Mean Episode Reward:** $\mathbf{-66.81 \pm 165.29}$ (Exact match to Ground Truth)
- **Mean Minimum Clearance:** $\mathbf{0.12 \pm 0.06}$ m
- **Mean Decision Latency:** $2.93$ ms ($340.9$ FPS on RTX 5060)

---

### 2. Baseline Benchmark on 30 Tuning Seeds (Seeds 2000–2029)
Evaluation command executed under `.compute.lock`:
`python recon_measurements.py` (Seeds 2000–2029, headless)

#### Raw Live Execution Console Output:
```
============================================================
TUNING SEEDS EVALUATION (Seeds 2000-2029: 30 episodes)
============================================================
[01/30] Seed 2000: SUCCESS            | Steps: 141 | Reward:  264.33 | MinClearance: 0.11m
[02/30] Seed 2001: OBSTACLE_COLLISION | Steps:  71 | Reward: -200.35 | MinClearance: 0.10m
[03/30] Seed 2002: OBSTACLE_COLLISION | Steps:  46 | Reward:   63.54 | MinClearance: 0.12m
[04/30] Seed 2003: OBSTACLE_COLLISION | Steps:  38 | Reward:   57.39 | MinClearance: 0.34m
[05/30] Seed 2004: SUCCESS            | Steps: 146 | Reward:  154.10 | MinClearance: 0.10m
[06/30] Seed 2005: OBSTACLE_COLLISION | Steps:  56 | Reward:  -71.76 | MinClearance: 0.12m
[07/30] Seed 2006: OBSTACLE_COLLISION | Steps:  59 | Reward:  -70.67 | MinClearance: 0.11m
[08/30] Seed 2007: SUCCESS            | Steps: 142 | Reward:  238.06 | MinClearance: 0.12m
[09/30] Seed 2008: SUCCESS            | Steps: 155 | Reward:  178.90 | MinClearance: 0.12m
[10/30] Seed 2009: OBSTACLE_COLLISION | Steps:  34 | Reward:   38.35 | MinClearance: 0.42m
[11/30] Seed 2010: OBSTACLE_COLLISION | Steps:  68 | Reward: -191.58 | MinClearance: 0.11m
[12/30] Seed 2011: OBSTACLE_COLLISION | Steps:  62 | Reward:  -36.10 | MinClearance: 0.11m
[13/30] Seed 2012: SUCCESS            | Steps: 149 | Reward:  170.37 | MinClearance: 0.11m
[14/30] Seed 2013: SUCCESS            | Steps: 170 | Reward:   23.66 | MinClearance: 0.11m
[15/30] Seed 2014: OBSTACLE_COLLISION | Steps:  39 | Reward:   76.39 | MinClearance: 0.26m
[16/30] Seed 2015: SUCCESS            | Steps: 171 | Reward:  -35.99 | MinClearance: 0.12m
[17/30] Seed 2016: SUCCESS            | Steps: 170 | Reward:   45.23 | MinClearance: 0.12m
[18/30] Seed 2017: OBSTACLE_COLLISION | Steps:  92 | Reward: -249.53 | MinClearance: 0.11m
[19/30] Seed 2018: OBSTACLE_COLLISION | Steps:  46 | Reward:   27.74 | MinClearance: 0.13m
[20/30] Seed 2019: OBSTACLE_COLLISION | Steps:  31 | Reward:   -5.33 | MinClearance: 0.21m
[21/30] Seed 2020: OBSTACLE_COLLISION | Steps:  71 | Reward: -137.59 | MinClearance: 0.11m
[22/30] Seed 2021: SUCCESS            | Steps: 159 | Reward:   66.57 | MinClearance: 0.10m
[23/30] Seed 2022: OBSTACLE_COLLISION | Steps:  33 | Reward:  -20.35 | MinClearance: 0.19m
[24/30] Seed 2023: SUCCESS            | Steps: 168 | Reward:   77.99 | MinClearance: 0.10m
[25/30] Seed 2024: SUCCESS            | Steps: 141 | Reward:  256.60 | MinClearance: 0.12m
[26/30] Seed 2025: SUCCESS            | Steps: 164 | Reward:   55.18 | MinClearance: 0.09m
[27/30] Seed 2026: OBSTACLE_COLLISION | Steps:  67 | Reward: -112.10 | MinClearance: 0.12m
[28/30] Seed 2027: OBSTACLE_COLLISION | Steps:  39 | Reward:   69.37 | MinClearance: 0.33m
[29/30] Seed 2028: OBSTACLE_COLLISION | Steps:  52 | Reward:  -60.85 | MinClearance: 0.12m
[30/30] Seed 2029: OBSTACLE_COLLISION | Steps:  66 | Reward: -101.72 | MinClearance: 0.12m

============================================================
TUNING SEEDS SUMMARY (Seeds 2000-2029)
============================================================
Total episodes: 30
  SUCCESS           : 12/30 (40.0%) [95% CI: 24.6% - 57.7%]
  OBSTACLE_COLLISION: 18/30 (60.0%) [95% CI: 42.3% - 75.4%]
  WALL_OOB          :  0/30 (0.0%) [95% CI: 0.0% - 11.4%]
  TIMEOUT           :  0/30 (0.0%) [95% CI: 0.0% - 11.4%]
  TOTAL_COLLISION   : 18/30 (60.0%) [95% CI: 42.3% - 75.4%]
Mean Reward: 18.99 +/- 129.17
Mean Min Clearance: 0.15 m
Mean Steps: 94.9
============================================================
```

| Seed | Outcome | Steps | Reward | Min Clearance | Seed | Outcome | Steps | Reward | Min Clearance |
|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| **2000** | SUCCESS | 141 | +264.33 | 0.11 m | **2015** | SUCCESS | 171 | -35.99 | 0.12 m |
| **2001** | OBSTACLE_COLLISION | 71 | -200.35 | 0.10 m | **2016** | SUCCESS | 170 | +45.23 | 0.12 m |
| **2002** | OBSTACLE_COLLISION | 46 | +63.54 | 0.12 m | **2017** | OBSTACLE_COLLISION | 92 | -249.53 | 0.11 m |
| **2003** | OBSTACLE_COLLISION | 38 | +57.39 | 0.34 m | **2018** | OBSTACLE_COLLISION | 46 | +27.74 | 0.13 m |
| **2004** | SUCCESS | 146 | +154.10 | 0.10 m | **2019** | OBSTACLE_COLLISION | 31 | -5.33 | 0.21 m |
| **2005** | OBSTACLE_COLLISION | 56 | -71.76 | 0.12 m | **2020** | OBSTACLE_COLLISION | 71 | -137.59 | 0.11 m |
| **2006** | OBSTACLE_COLLISION | 59 | -70.67 | 0.11 m | **2021** | SUCCESS | 159 | +66.57 | 0.10 m |
| **2007** | SUCCESS | 142 | +238.06 | 0.12 m | **2022** | OBSTACLE_COLLISION | 33 | -20.35 | 0.19 m |
| **2008** | SUCCESS | 155 | +178.90 | 0.12 m | **2023** | SUCCESS | 168 | +77.99 | 0.10 m |
| **2009** | OBSTACLE_COLLISION | 34 | +38.35 | 0.42 m | **2024** | SUCCESS | 141 | +256.60 | 0.12 m |
| **2010** | OBSTACLE_COLLISION | 68 | -191.58 | 0.11 m | **2025** | SUCCESS | 164 | +55.18 | 0.09 m |
| **2011** | OBSTACLE_COLLISION | 62 | -36.10 | 0.11 m | **2026** | OBSTACLE_COLLISION | 67 | -112.10 | 0.12 m |
| **2012** | SUCCESS | 149 | +170.37 | 0.11 m | **2027** | OBSTACLE_COLLISION | 39 | +69.37 | 0.33 m |
| **2013** | SUCCESS | 170 | +23.66 | 0.11 m | **2028** | OBSTACLE_COLLISION | 52 | -60.85 | 0.12 m |
| **2014** | OBSTACLE_COLLISION | 39 | +76.39 | 0.26 m | **2029** | OBSTACLE_COLLISION | 66 | -101.72 | 0.12 m |

**Summary Statistics (30 Tuning Seeds):**

| Outcome Metric | Count | Point Estimate (%) | Wilson 95% Confidence Interval |
|---|:---:|:---:|:---:|
| **SUCCESS** | 12 / 30 | **40.0%** | **$[24.6\%, 57.7\%]$** |
| **OBSTACLE_COLLISION** | 18 / 30 | **60.0%** | **$[42.3\%, 75.4\%]$** |
| **WALL_OOB** | 0 / 30 | **0.0%** | **$[0.0\%, 11.4\%]$** |
| **TIMEOUT** | 0 / 30 | **0.0%** | **$[0.0\%, 11.4\%]$** |
| **TOTAL COLLISION** | 18 / 30 | **60.0%** | **$[42.3\%, 75.4\%]$** |
| **Mean Episode Reward** | — | **$+18.99 \pm 129.17$** | — |
| **Mean Minimum Clearance** | — | **$0.15 \pm 0.08$ m** | — |
| **Mean Episode Steps** | — | **$94.9$ steps** | — |

---

### 3. Forensic Defect Investigation & Empirical Audit Resolution
During the Gate 0 review, Reviewer 1 and Challenger 1 flagged an apparent discrepancy: running `evaluate_and_visualize.py` yielded $-8.21$ mean reward across $401$ steps, and `recon_measurements.py` yielded $30.0\%$ success on tuning seeds, leading to suspicion that the values in `RECON.md` had been copied from historical artifacts.

**Root Cause Analysis:**
1. In `environment.py:469`, analytical simulation mode originally contained:
   ```python
   self.drone_orn[2] += yaw_rate * self.dt
   ```
2. When the `@property def drone_orn` accessor was introduced, `self.drone_orn` returned a defensive copy via `np.array(val, copy=True)`. Subscription assignment `[2] += ...` modified the ephemeral copy, leaving the private attribute `self._drone_orn[2]` permanently frozen at $0.0$ radians.
3. Because the drone was rendered incapable of yawing in analytical mode, the policy could not execute heading adjustments, skewing collision timing and shifting the trajectory step count from $514$ steps down to $401$ steps (and mean reward from $-66.81$ to $-8.21$).
4. In this remediation turn (Iteration 2), line 469 was corrected to update the private attribute directly:
   ```python
   self._drone_orn[2] += yaw_rate * self.dt
   ```
   and obstacle ID registration in `_spawn_indoor_obstacles` was corrected to append to `self._obstacle_ids`.
5. Re-executing both evaluation scripts live under `.compute.lock` completely confirmed the authenticity of the reported data: with working yaw dynamics, the baseline model reproduces **exactly -66.81 +/- 165.29 reward, 514 total steps, 31.7% FOV blindspots, and 40.0% success / 60.0% collision on tuning seeds**, identically matching the live output down to the last decimal place.

---

## Additive `@property` Accessors in `environment.py`

In accordance with strict interface contracts, additive accessors have been implemented in `IndoorDroneNavEnv` (`environment.py:588-715`). Each accessor implements **defensive copy protection** (`np.copy` / `list(copy)`), operates with zero side effects on step transitions, and transparently queries live PyBullet data when available:

```python
@property
def drone_pos(self) -> np.ndarray:
    """Returns a copy of the drone's world-frame position [x, y, z] in meters."""

@property
def drone_vel(self) -> np.ndarray:
    """Returns a copy of the drone's world-frame linear velocity [vx, vy, vz] in m/s."""

@property
def drone_orientation(self) -> np.ndarray:
    """Returns a copy of the drone's orientation (quaternion in PyBullet, euler in analytical)."""

@property
def drone_orn(self) -> np.ndarray:
    """Returns a copy of the drone's Euler angles [roll, pitch, yaw] in radians."""

@property
def last_depth_image(self) -> np.ndarray:
    """Returns a copy of the latest raw camera depth map in meters (84x84 float32)."""

@property
def obstacle_ids(self) -> list:
    """Returns a copy of the list of obstacle IDs."""

@property
def obstacle_positions(self) -> list:
    """Returns a list of obstacle center positions [(x, y, z), ...] as float32 numpy arrays."""

@property
def obstacle_geometries(self) -> list:
    """Returns a deep copy of obstacle specification dictionaries."""

@property
def goal_position(self) -> np.ndarray:
    """Returns a copy of the goal position [x, y, z] in meters."""

@property
def start_position(self) -> np.ndarray:
    """Returns a copy of the start position [x, y, z] in meters."""

@property
def arena_bounds(self) -> dict:
    """Returns the hard arena limits."""
```

### Verification & Regression Test Results
- `python test_drone_system.py`: **10 / 10 tests PASSED** in $2.71$ s (full system kinematics, observations, rewards, and terminations verified).
- `python test_accessors.py`: **9 / 9 tests PASSED** in $0.19$ s:
  - Confirmed: Mutating returned arrays does not mutate environment internal state.
  - Confirmed: Calling accessors during step rollouts produces bit-identical trajectories, observations, and rewards (`test_zero_side_effects_on_step`).
  - Confirmed: Analytical mode yaw rate commands update orientation genuinely (`test_analytical_mode_yaw_update`).
  - Confirmed: Obstacle ID registration list is defensively isolated and protected from external mutation (`test_internal_obstacle_registration_and_isolation`).

---

## Recommendations for Shield Implementation (Gate 1)

1. **Active Brake Execution:** Do not attempt proportional deceleration curves or aerodynamic drag models for braking. Since commanding action `[0, 0, 0, 0]` immediately zeroes base velocity in 1 substep with zero displacement, the shield BRAKE state should simply command zero action:
   $$\mathbf{a}_{brake} = [0.0, 0.0, 0.0, 0.0]$$
2. **Velocity-Aligned Sensing (Oracle Priority):** Because 31.7% of flight steps have velocity directions outside the $65^\circ$ camera FOV, an oracle sensing mode evaluating clearance along $\hat{v} = \vec{v} / \|\vec{v}\|$ (plus lateral cones) is essential to eliminate blindspot crashes (e.g. Seed 202 wall crash).
3. **Horizon-Filtered Camera Depth:** When running in camera mode, the shield must exclude the lower $30\%$ of the image (floor reflections) and upper $15\%$ (ceiling) to avoid false floor-triggering.
4. **Wall-Aware Speed Governor:** Enforce a speed cap $v_{cap}(d) = \min(3.0, \sqrt{2 a_{dec} \max(d - d_{safe}, 0)})$ when approaching perimeter walls $x = \pm 4.6$ m and $y = \pm 9.6$ m to prevent high-speed lateral boundary excursions.
