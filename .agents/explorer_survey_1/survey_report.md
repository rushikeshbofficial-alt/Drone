# Technical Audit Report: Simulation Environment & Mathematical Formulations
**Target Module**: `environment.py` and `README.md`  
**Auditor**: `explorer_survey_1` (Principal Systems Architect & Technical Auditor)  
**Date**: 2026-09-19  
**Status**: Completed & Fully Verified  

---

## 1. Executive Summary & Audit Scope

This document provides an exhaustive, publication-grade technical audit of the simulation environment (`environment.py`) and research documentation (`README.md`) of the **Autonomous Drone Navigation through Random Obstacles in a Simulated Environment** project. 

The environment encapsulates a high-fidelity, physics-informed Gymnasium interface designed for training vision-based deep reinforcement learning agents in unstructured, GPS-denied 3D indoor arenas. The simulation couples rigid-body dynamics in PyBullet at 240 Hz with Gymnasium agent control at 24 Hz, features dual-engine rendering (PyBullet Hardware/TinyRenderer with an analytical 3D Perspective Raycasting CPU fallback), performs real-time dense Gunnar Farneback optical flow estimation across a 60% central Region of Interest (ROI), calculates bounded inverse time-to-collision ($\tau^{-1}$), executes strict sub-step coordinate boundary clamping to eliminate tunneling, and drives policy optimization via a multi-objective physics-informed reward function.

This audit cross-references all source lines of code against published equations in `README.md`, identifying exact parameter values, operational mechanics, analytical derivations, and reconciling discrepancies between high-level documentation and codebase implementations.

---

## 2. Complete Mathematical Formulations

### 2.1 Gunnar Farneback Optical Flow Formulation

The visual perception module computes dense motion displacement vectors between consecutive grayscale camera observations $I_{t-1}(\mathbf{x})$ and $I_t(\mathbf{x})$ using the two-frame Gunnar Farneback polynomial expansion algorithm.

#### 2.1.1 Local Polynomial Approximation
The local neighborhood of each pixel $\mathbf{x} = [x, y]^T$ in frame $1$ ($I_{t-1}$) and frame $2$ ($I_t$) is modeled via a continuous quadratic polynomial surface:
$$f_1(\mathbf{x}) = \mathbf{x}^T \mathbf{A}_1 \mathbf{x} + \mathbf{b}_1^T \mathbf{x} + c_1$$
$$f_2(\mathbf{x}) = \mathbf{x}^T \mathbf{A}_2 \mathbf{x} + \mathbf{b}_2^T \mathbf{x} + c_2$$

Where:
- $\mathbf{A}_i \in \mathbb{R}^{2 \times 2}$ is a symmetric matrix describing local surface curvature.
- $\mathbf{b}_i \in \mathbb{R}^2$ represents local image gradient.
- $c_i \in \mathbb{R}$ is the scalar intensity bias.

Assuming a global or local displacement vector field $\mathbf{d} = [u, v]^T$, the second frame is a shifted version of the first:
$$f_2(\mathbf{x}) = f_1(\mathbf{x} - \mathbf{d}) = (\mathbf{x} - \mathbf{d})^T \mathbf{A}_1 (\mathbf{x} - \mathbf{d}) + \mathbf{b}_1^T (\mathbf{x} - \mathbf{d}) + c_1$$
Expanding and equating corresponding polynomial terms yields:
$$\mathbf{A}_2 = \mathbf{A}_1$$
$$\mathbf{b}_2 = \mathbf{b}_1 - 2 \mathbf{A}_1 \mathbf{d}$$
$$\mathbf{d} = -\frac{1}{2} \mathbf{A}_1^{-1} (\mathbf{b}_2 - \mathbf{b}_1)$$

In practice, to enhance numerical conditioning and spatial coherence, $\mathbf{A}(\mathbf{x}) = \frac{\mathbf{A}_1(\mathbf{x}) + \mathbf{A}_2(\mathbf{x})}{2}$ and $\Delta \mathbf{b}(\mathbf{x}) = -\frac{1}{2} (\mathbf{b}_2(\mathbf{x}) - \mathbf{b}_1(\mathbf{x}))$ are weighted over a local Gaussian neighborhood $w(\Delta \mathbf{x})$:
$$\mathbf{d}(\mathbf{x}) = \left( \sum w \mathbf{A}^T \mathbf{A} \right)^{-1} \sum w \mathbf{A}^T \Delta \mathbf{b}$$

#### 2.1.2 Concrete Hyperparameters in `environment.py`
In `IndoorDroneNavEnv._compute_optical_flow_and_tau` (lines 369–380), the OpenCV implementation `cv2.calcOpticalFlowFarneback` is configured with:
- `pyr_scale = 0.5`: Classical dyadic pyramid downsampling factor (50% scale reduction per octave).
- `levels = 2`: 2-level multi-resolution image pyramid (processing at $42 \times 42$ and $84 \times 84$).
- `winsize = 9`: Spatial averaging window of $9 \times 9$ pixels for coefficient smoothing.
- `iterations = 2`: 2 displacement refinement iterations per pyramid level.
- `poly_n = 5`: Neighborhood size of $5 \times 5$ pixels used for polynomial surface fitting.
- `poly_sigma = 1.1`: Standard deviation $\sigma = 1.1$ of the Gaussian filter used for smoothing polynomial coefficients.
- `flags = 0`: Standard Farneback solver without warm-start displacement priors.

---

### 2.2 Inverse Time-to-Collision ($\tau^{-1}$) via Central ROI Looming

#### 2.2.1 Looming Dynamics & Differential Divergence
For a camera translating forward at velocity $V_z$ toward a planar obstacle at distance $Z$, the optical flow motion field radiates symmetrically from the Focus of Expansion (FOE). The radial flow velocity $\mathbf{u}(\mathbf{x}) = [u, v]^T$ at image coordinates $(x, y)$ is governed by:
$$u = \frac{x V_z}{Z} - \frac{f V_x}{Z}, \quad v = \frac{y V_z}{Z} - \frac{f V_y}{Z}$$

The 2D spatial divergence of the flow field $\nabla \cdot \mathbf{u}$ relates directly to the inverse time-to-collision $\tau^{-1} = \frac{V_z}{Z}$:
$$\nabla \cdot \mathbf{u} = \frac{\partial u}{\partial x} + \frac{\partial v}{\partial y} = \frac{V_z}{Z} + \frac{V_z}{Z} = 2 \frac{V_z}{Z} = 2 \tau^{-1}$$

Thus, the spatial divergence measures the instantaneous visual looming rate (fractional area expansion per second, $\text{s}^{-1}$).

#### 2.2.2 Discrete Sobel Differential Operators
In `environment.py` (lines 385–387), the spatial derivatives are estimated using $3 \times 3$ Sobel convolution kernels:
$$\frac{\partial u}{\partial x} \approx u * \mathbf{K}_x, \quad \frac{\partial v}{\partial y} \approx v * \mathbf{K}_y$$
Where:
$$\mathbf{K}_x = \begin{bmatrix} -1 & 0 & 1 \\ -2 & 0 & 2 \\ -1 & 0 & 1 \end{bmatrix}, \quad \mathbf{K}_y = \begin{bmatrix} -1 & -2 & -1 \\ 0 & 0 & 0 \\ 1 & 2 & 1 \end{bmatrix}$$
The continuous divergence field is computed as:
$$\text{divergence}(x, y) = \left( \frac{\partial u}{\partial x} + \frac{\partial v}{\partial y} \right)(x, y)$$

#### 2.2.3 60% Central ROI Masking
Peripheral optical flow in indoor environments is dominated by parallax shear from lateral side walls rather than frontal collision risks. Therefore, `environment.py` restricts divergence accumulation to the central 60% Region of Interest (lines 58–61, 389–391):
$$\text{margin}_h = \lfloor 84 \times 0.20 \rfloor = 16\text{ px}$$
$$\text{margin}_w = \lfloor 84 \times 0.20 \rfloor = 16\text{ px}$$
$$\mathcal{M}_{\text{ROI}}(y, x) = \begin{cases} 1, & 16 \le y < 68 \quad \text{and} \quad 16 \le x < 68 \\ 0, & \text{otherwise} \end{cases}$$

The active ROI spans $52 \times 52 = 2,704$ pixels out of 7,056 ($38.32\%$ of total frame pixels), corresponding exactly to a central $61.9\% \approx 60\%$ spatial span along each axis.

#### 2.2.4 Mean Expansion & Bounded Inverse TTC
The mean expansion across the active mask is computed as:
$$\bar{E}_{\text{ROI}} = \frac{1}{|\mathcal{M}_{\text{ROI}}|} \sum_{(x,y) \in \mathcal{M}_{\text{ROI}}} (\nabla \cdot \mathbf{u})(x, y)$$

To prevent negative penalties during retreat/backward motion and guard against numerical gradient blowup when contacting surfaces, the metric is non-negatively rectified and clamped to $\tau^{-1}_{\text{max}} = 5.0\text{ s}^{-1}$:
$$\tau^{-1}_{\text{bounded}} = \text{clip}\left( \max(0.0, \bar{E}_{\text{ROI}}), \, 0.0, \, \tau^{-1}_{\text{max}} \right) = \min\left( \max(0.0, \bar{E}_{\text{ROI}}), \, 5.0 \right)$$
At the maximum value $\tau^{-1} = 5.0\text{ s}^{-1}$, the effective theoretical time-to-collision is $\tau = 0.2\text{ s}$.

---

### 2.3 Multi-Objective Physics-Informed Reward Formulation

The reinforcement learning objective is governed by a multi-component reward shaping function evaluated at every Gymnasium step ($24\text{ Hz}$):

$$R_t = R_{\text{progress}} + R_{\text{goal}} + R_{\text{TTC}} + R_{\text{attitude}} + R_{\text{proximity}} + R_{\text{terminal}}$$

#### 2.3.1 Progress Reward ($R_{\text{progress}}$)
A potential-based shaping term rewarding monotonic reduction in Euclidean distance to the goal (lines 493–497):
$$R_{\text{progress}} = 6.0 \cdot (d_{t-1}^{\text{goal}} - d_t^{\text{goal}})$$
Where $d_t^{\text{goal}} = \|\mathbf{p}_{\text{drone}, t} - \mathbf{p}_{\text{goal}}\|_2$. At episode reset ($t=0$), $d_0^{\text{goal}} = \|\mathbf{p}_{\text{start}} - \mathbf{p}_{\text{goal}}\|_2 = \sqrt{0^2 + 16^2 + 0^2} = 16.0\text{ m}$. Traversing the full 16-meter arena provides an integrated progress return of:
$$\sum R_{\text{progress}} = 6.0 \times 16.0 = +96.0$$

#### 2.3.2 Heading Velocity Alignment Reward ($R_{\text{goal}}$)
Incentivizes the drone's instantaneous 3D velocity vector $\mathbf{v}_{\text{drone}}$ to align with the unit vector pointing toward the target $\hat{\mathbf{d}}_{\text{goal}}$ (lines 499–500):
$$\hat{\mathbf{d}}_{\text{goal}} = \frac{\mathbf{p}_{\text{goal}} - \mathbf{p}_{\text{drone}}}{\|\mathbf{p}_{\text{goal}} - \mathbf{p}_{\text{drone}}\|_2 + 10^{-6}}$$
$$R_{\text{goal}} = 3.0 \cdot (\mathbf{v}_{\text{drone}} \cdot \hat{\mathbf{d}}_{\text{goal}})$$
Given maximum forward speed $v_{\max} = 3.0\text{ m/s}$, the maximum instantaneous heading reward is $3.0 \times 3.0 = +9.0$ per step.

#### 2.3.3 Optical Flow Looming Penalty ($R_{\text{TTC}}$)
Penalizes high optical flow expansion rates within the frontal 60% central ROI (line 501):
$$R_{\text{TTC}} = -2.0 \cdot \tau^{-1}_{\text{bounded}}$$
With $\tau^{-1} \in [0.0, 5.0]$, the penalty ranges from $0.0$ to $-10.0$ per step.

#### 2.3.4 Attitude Stability Penalty ($R_{\text{attitude}}$)
Penalizes roll ($\phi$) and pitch ($\theta$) tilt angles to ensure smooth camera orientation, level flight, and stable visual perception (line 502):
$$R_{\text{attitude}} = -0.5 \cdot (|\phi| + |\theta|)$$
Angles are measured in radians from the quaternion-derived Euler orientation $[\phi, \theta, \psi]^T$.

#### 2.3.5 Visual Depth Proximity Safety Buffer ($R_{\text{proximity}}$)
Provides a soft repulsive barrier penalty when approaching any obstacle within a $1.5\text{ m}$ safety envelope (lines 505–509):
$$d_{\text{safe}} = 1.5\text{ m}$$
$$d_{\text{min}} = \text{Percentile}_{5\%}(D_{\text{meters}})$$
$$R_{\text{proximity}} = \begin{cases} -3.0 \cdot (1.5 - d_{\text{min}}), & \text{if } d_{\text{min}} < 1.5\text{ m} \\ 0.0, & \text{otherwise} \end{cases}$$
*Robustness rationale*: Utilizing the **5th percentile** of the metric depth map $D_{\text{meters}}$ rather than the strict minimum ($\min_{(x,y)} D$) prevents isolated raycast specular anomalies or single-pixel edge artifacts from corrupting the reward signal while penalizing real obstacles spanning multiple pixels.

#### 2.3.6 Terminal Rewards & Penalties ($R_{\text{terminal}}$)
Evaluated upon episode termination (lines 516–524):
$$R_{\text{terminal}} = \begin{cases} +100.0, & \text{if goal reached } (d_t^{\text{goal}} < 0.8\text{ m}) \\ -100.0, & \text{if collision or out-of-bounds detected} \\ 0.0, & \text{otherwise} \end{cases}$$

---

### 2.4 Codebase vs. README Mathematical Reconciliation

A detailed cross-audit between the mathematical formulas in `README.md` and the actual implementation in `environment.py` reveals several critical engineering enhancements:

| Parameter / Term | `README.md` Specification | `environment.py` Implementation | Architectural Rationale & Reconciliation |
| :--- | :--- | :--- | :--- |
| **Progress Reward ($R_{\text{progress}}$)** | *Omitted from README equation* | $6.0 \cdot (d_{t-1} - d_t)$ | **Dense Shaping Enhancement**: Added during RL training optimization to mitigate sparse credit assignment across 500-step episodes. |
| **Goal Velocity Gain ($w_{\text{goal}}$)** | $2.0 \cdot (\mathbf{v} \cdot \hat{\mathbf{d}})$ | $3.0 \cdot (\mathbf{v} \cdot \hat{\mathbf{d}})$ | **Dynamic Drive**: Increased by 50% to incentivize high forward cruising velocity through open corridors. |
| **TTC Looming Gain ($w_{\text{TTC}}$)** | $-1.5 \cdot \tau^{-1}_{\text{bounded}}$ | $-2.0 \cdot \tau^{-1}_{\text{bounded}}$ | **Aggressive Collision Avoidance**: Scaled up to counterbalance higher forward speed, forcing braking upon obstacle looming. |
| **Proximity Penalty Gain ($w_{\text{prox}}$)** | $-2.0 \cdot (1.5 - d_{\min})$ | $-3.0 \cdot (1.5 - d_{5\%})$ | **Safety Buffer Hardening**: Penalizes intrusion within 1.5m more severely to prevent near-miss scraping. |
| **Proximity Depth Metric** | Strict minimum $d_{\min}$ | 5th percentile $\text{P}_{5\%}(D)$ | **Sensor Noise Rejection**: 5th percentile filters single-pixel edge artifacts and camera ray noise. |
| **Maximum Inverse TTC ($\tau^{-1}_{\max}$)** | $\tau^{-1}_{\max} = 5.0$ | `self.tau_inv_max = 5.0` | **Identical**: Bound enforced at $5.0\text{ s}^{-1}$ ($\tau_{\min} = 0.2\text{ s}$). |
| **Terminal Success Reward** | $+100.0$ ($d < 0.8\text{ m}$) | $+100.0$ ($d < 0.8\text{ m}$) | **Identical**: Sparse milestone bonus for reaching target circle. |
| **Terminal Collision Penalty**| $-100.0$ (collision or OOB) | $-100.0$ (collision or OOB) | **Identical**: Severe catastrophic failure penalty terminating rollout. |

---

## 3. Complete Physical & Simulation Parameters

### 3.1 Dual-Frequency Physics/Control Architecture
The simulation implements a decoupled multi-rate timing structure:
- **PyBullet Physics Simulation Frequency**: $f_{\text{physics}} = 240.0\text{ Hz}$ ($\Delta t = \frac{1}{240} \approx 4.167\text{ ms}$).
- **Gymnasium Control Loop Frequency**: $f_{\text{control}} = 24.0\text{ Hz}$ ($\Delta T = \frac{1}{24} \approx 41.667\text{ ms}$).
- **Physics Substeps Per Control Step**:
  $$N_{\text{substeps}} = \frac{f_{\text{physics}}}{f_{\text{control}}} = \frac{240.0}{24.0} = 8\text{ substeps}$$
During each agent step call (`step(action)`), PyBullet executes 8 consecutive sub-integrations (`p.stepSimulation()`). At every single substep, boundary coordinates are evaluated and clamped.

```
+-----------------------------------------------------------------------------------+
|                        Gymnasium Control Step (24 Hz, 41.67 ms)                   |
|                                                                                   |
|  +-------------+  +-------------+  +-------------+      +-------------+           |
|  | Substep 1   |  | Substep 2   |  | Substep 3   | ...  | Substep 8   |           |
|  | (240 Hz,    |  | (240 Hz,    |  | (240 Hz,    |      | (240 Hz,    |           |
|  |  4.17 ms)   |  |  4.17 ms)   |  |  4.17 ms)   |      |  4.17 ms)   |           |
|  | +---------+ |  | +---------+ |  | +---------+ |      | +---------+ |           |
|  | |Clamp &  | |  | |Clamp &  | |  | |Clamp &  | |      | |Clamp &  | |           |
|  | |Anti-Tune| |  | |Anti-Tune| |  | |Anti-Tune| |      | |Anti-Tune| |           |
|  | +---------+ |  | +---------+ |  | +---------+ |      | +---------+ |           |
|  +-------------+  +-------------+  +-------------+      +-------------+           |
|                                                                                   |
|  --> Camera Capture (84x84) --> Farneback Optical Flow --> Multi-Objective Reward |
+-----------------------------------------------------------------------------------+
```

---

### 3.2 Coordinate Frames & Reference Systems
The environment employs a standard Right-Handed Cartesian coordinate system:
- **World Origin $(0, 0, 0)$**: Located at the center of the arena floor plane.
- **X-axis**: Lateral axis, spanning $[-5.0, +5.0]\text{ m}$ (West to East).
- **Y-axis**: Longitudinal axis, spanning $[-10.0, +10.0]\text{ m}$ (South to North). Drone navigates primarily in the $+Y$ direction.
- **Z-axis**: Vertical altitude axis, pointing upwards against gravity, spanning $[0.0, 4.0]\text{ m}$.
- **Start Position**: $\mathbf{p}_{\text{start}} = [0.0, -8.0, 1.5]^T\text{ m}$.
- **Goal Position**: $\mathbf{p}_{\text{goal}} = [0.0, +8.0, 1.5]^T\text{ m}$.
- **Total Flight Path Vector**: $\mathbf{L} = \mathbf{p}_{\text{goal}} - \mathbf{p}_{\text{start}} = [0.0, 16.0, 0.0]^T\text{ m}$ ($16.0\text{ m}$ straight-line distance).

---

### 3.3 Arena Geometry & Strict Sub-Step Boundary Clamping

#### 3.3.1 Boundary Walls
The arena is bounded by four static rectangular wall slabs (lines 140–153):
1. **North Wall**: Position $[0.0, 10.0, 2.0]$, half-extents $[5.0, 0.1, 2.0]$, full dimensions $10.0\text{ m} \times 0.2\text{ m} \times 4.0\text{ m}$.
2. **South Wall**: Position $[0.0, -10.0, 2.0]$, half-extents $[5.0, 0.1, 2.0]$, full dimensions $10.0\text{ m} \times 0.2\text{ m} \times 4.0\text{ m}$.
3. **East Wall**: Position $[5.0, 0.0, 2.0]$, half-extents $[0.1, 10.0, 2.0]$, full dimensions $0.2\text{ m} \times 20.0\text{ m} \times 4.0\text{ m}$.
4. **West Wall**: Position $[-5.0, 0.0, 2.0]$, half-extents $[0.1, 10.0, 2.0]$, full dimensions $0.2\text{ m} \times 20.0\text{ m} \times 4.0\text{ m}$.
- **Floor**: Standard PyBullet plane (`plane.urdf`) loaded at $Z = 0.0$.

#### 3.3.2 Anti-Tunneling Sub-Step Clamping Mechanics
To strictly prevent high-velocity tunneling through walls during discrete physics integration, `environment.py` defines hard spatial bounding constants:
- `ARENA_X_LIM = 4.6` (wall boundary at $5.0$, wall half-extent $0.1$, drone half-extent $0.2$, margin $0.1$)
- `ARENA_Y_LIM = 9.6` (wall boundary at $10.0$, wall half-extent $0.1$, drone half-extent $0.2$, margin $0.1$)
- `ARENA_Z_MIN = 0.15` (floor buffer above $Z=0.0$, drone half-height $0.08$)
- `ARENA_Z_MAX = 3.5` (ceiling clearance below wall top at $4.0$)

In `_clamp_to_arena(pos)` (lines 417–423):
$$x_{\text{clamped}} = \text{clip}(p_x, -4.6, 4.6)$$
$$y_{\text{clamped}} = \text{clip}(p_y, -9.6, 9.6)$$
$$z_{\text{clamped}} = \text{clip}(p_z, 0.15, 3.5)$$
$$\text{OOB} = (x_{\text{clamped}} \ne p_x) \lor (y_{\text{clamped}} \ne p_y) \lor (z_{\text{clamped}} \ne p_z)$$

When $\text{OOB} = \text{True}$ occurs during any of the 8 substeps:
1. `self.out_of_bounds = True` is latched.
2. Drone position is instantly projected to $[x_{\text{clamped}}, y_{\text{clamped}}, z_{\text{clamped}}]$.
3. Drone linear and angular velocities are zeroed out: `p.resetBaseVelocity(self.drone_id, [0, 0, 0], [0, 0, 0])`.
4. At step conclusion, `out_of_bounds` triggers `collision = True`, applying the $-100.0$ penalty and terminating the episode.

---

### 3.4 Drone Physical Constants & Rigid-Body Dynamics

The quadrotor chassis is modeled as a 6-DoF rigid body:
- **Base Mass**: $m = 1.0\text{ kg}$.
- **Collision Shape**: `p.GEOM_BOX` with half-extents $[0.20, 0.20, 0.08]\text{ m}$ (total footprint: $40\text{ cm} \times 40\text{ cm} \times 16\text{ cm}$).
- **Visual Shape**: Cyan box (`rgbaColor = [0.1, 0.7, 1.0, 1.0]`).
- **Gravity**: $\mathbf{g} = [0.0, 0.0, -9.81]^T\text{ m/s}^2$.

---

### 3.5 Action Space & Kinematics Mapping

The action space is a continuous 4D vector normalized to $\mathcal{A} \in [-1.0, +1.0]^4$:
$$\mathbf{a} = [a_x, a_y, a_z, a_{\psi}]^T$$

The action is mapped to physical target velocities via:
$$\mathbf{v}_{\text{target}} = \begin{bmatrix} a_x \\ a_y \\ a_z \end{bmatrix} \times 3.0\text{ m/s} \quad \implies \quad v_{x,y,z} \in [-3.0, +3.0]\text{ m/s}$$
$$\dot{\psi}_{\text{target}} = a_{\psi} \times 1.0\text{ rad/s} \quad \implies \quad \dot{\psi} \in [-1.0, +1.0]\text{ rad/s} \approx [-57.3^\circ/\text{s}, +57.3^\circ/\text{s}]$$

In PyBullet mode, velocity tracking is enforced via `p.resetBaseVelocity`:
$$\mathbf{v}_{\text{cmd}} = \mathbf{v}_{\text{target}}, \quad \boldsymbol{\omega}_{\text{cmd}} = [0.0, 0.0, \dot{\psi}_{\text{target}}]^T$$
In the kinematic CPU fallback mode:
$$\mathbf{p}_{t+\Delta t} = \mathbf{p}_t + \mathbf{v}_{\text{target}} \Delta t$$
$$\psi_{t+\Delta t} = \psi_t + \dot{\psi}_{\text{target}} \Delta t$$

---

### 3.6 Collision Detection Mechanics & Thresholds

Collision detection is handled through a dual-mechanism hierarchy:

#### 3.6.1 PyBullet Collision Detection
PyBullet executes Gilbert-Johnson-Keerthi (GJK) and Expanding Polytope Algorithm (EPA) contact manifold generation:
```python
contact_points = p.getContactPoints(bodyA=self.drone_id, physicsClientId=self.client_id)
collision = len(contact_points) > 0
```
Any contact point between the drone's collision bounding box ($40 \times 40 \times 16\text{ cm}$) and obstacles, walls, or the floor marks an immediate collision.

#### 3.6.2 CPU Fallback Collision Detection
In headless fallback mode, horizontal radial proximity checks are executed against all dynamic obstacles (lines 476–484):
$$\|\mathbf{p}_{\text{drone}}^{xy} - \mathbf{p}_{\text{obs}}^{xy}\|_2 < (r_{\text{obs}} + 0.25\text{ m})$$
Where $r_{\text{obs}} = \text{radius}$ for cylinders, or $r_{\text{obs}} = 0.4\text{ m}$ default for boxes. The $0.25\text{ m}$ buffer accounts for the drone's half-diagonal $\sqrt{0.2^2 + 0.2^2} \approx 0.28\text{ m}$.

#### 3.6.3 Goal Reaching Threshold
Success is declared when the Euclidean distance from drone center to goal center is strictly below $0.8\text{ m}$:
$$d_{\text{goal}} = \|\mathbf{p}_{\text{drone}} - \mathbf{p}_{\text{goal}}\|_2 < 0.8\text{ m}$$

---

## 4. Procedural Generation Algorithms & Environment Randomization

### 4.1 Obstacle Distribution & Placement Rules

Obstacles are dynamically generated during each `reset()` call via `_spawn_indoor_obstacles()` (lines 134–182).

```
  Y = +10.0 m +-------------------------------------------------------+
              |                                                       |
  Y = +8.0 m  |                     [ GOAL (0, 8, 1.5) ]              |  Clearance Buffer
              |                                                       |  (Y: +5.0 to +10.0 m)
  Y = +5.0 m  + - - - - - - - - - - - - - - - - - - - - - - - - - - - +
              |                                                       |
              |            Procedural Obstacle Field                  |
              |       (6 to 11 Cylinders & Emerald Boxes)             |
              |            X in [-3.5, 3.5], Y in [-5.0, 5.0]         |  Active Obstacle Zone
              |                                                       |
  Y = -5.0 m  + - - - - - - - - - - - - - - - - - - - - - - - - - - - +
              |                                                       |
  Y = -8.0 m  |                    [ START (0, -8, 1.5) ]             |  Clearance Buffer
              |                                                       |  (Y: -10.0 to -5.0 m)
  Y = -10.0 m +-------------------------------------------------------+
              X = -5.0 m                                              X = +5.0 m
```

#### 4.1.1 Count Distribution
The number of dynamic obstacles is sampled from a discrete uniform distribution:
$$N_{\text{obstacles}} \sim \mathcal{U}_{\text{discrete}}\{6, 7, 8, 9, 10, 11\} \quad (\text{via } \texttt{np.random.randint(6, 12)})$$

#### 4.1.2 Obstacle Types & Geometry Specifications
For each obstacle $i \in \{1, \dots, N_{\text{obstacles}}\}$, the geometric primitive type is sampled uniformly:
$$\text{Type} \sim \text{Choice}(\{\text{"cylinder"}, \text{"box"}\})$$

1. **Vertical Cylinders (Columns/Pillars)**:
   - **Radius**: $r \sim \mathcal{U}(0.35, 0.65)\text{ m}$ (diameter: $0.70$ to $1.30\text{ m}$).
   - **Height**: $h \sim \mathcal{U}(2.5, 4.0)\text{ m}$.
   - **Position**: $\mathbf{p} = [x, y, h/2.0]^T$, where $x \sim \mathcal{U}(-3.5, 3.5)\text{ m}$, $y \sim \mathcal{U}(-5.0, 5.0)\text{ m}$. Cylinders sit firmly on the floor ($Z=0$) and extend vertically.
   - **Visual Appearance**: Coral / Bright Orange RGB $(255, 100, 40)$, RGBA $[1.0, 0.4, 0.1, 1.0]$.
   - **Physics Body**: `p.GEOM_CYLINDER`, mass $m=0.0$ (static kinematic body).

2. **Floating Cuboids (Boxes/Hanging Blocks)**:
   - **Half-Extents**: $e_x, e_y, e_z \sim \mathcal{U}(0.35, 0.65)\text{ m}$ independently sampled (full dimension: $0.70$ to $1.30\text{ m}$ per side).
   - **Position**: $\mathbf{p} = [x, y, z]^T$, where $x \sim \mathcal{U}(-3.5, 3.5)\text{ m}$, $y \sim \mathcal{U}(-5.0, 5.0)\text{ m}$, $z \sim \mathcal{U}(1.0, 2.5)\text{ m}$ (floating at drone cruise altitude).
   - **Visual Appearance**: Emerald Green RGB $(40, 220, 110)$, RGBA $[0.1, 0.85, 0.4, 1.0]$.
   - **Physics Body**: `p.GEOM_BOX`, mass $m=0.0$ (static kinematic body).

---

### 4.2 Protected Clearance Zones & Corridor Geometry

The environment enforces structured clearance zones to prevent impossible spawn configurations:
1. **Initial Safe Corridor**:
   - Drone spawns at $Y = -8.0\text{ m}$.
   - Obstacles are strictly confined to $Y \in [-5.0, +5.0]\text{ m}$.
   - This creates a **$3.0\text{ m}$ longitudinal clearance zone** ($Y \in [-8.0, -5.0]$) where the drone can accelerate and stabilize attitude without immediate collision threat.
2. **Terminal Goal Approach Zone**:
   - Goal is located at $Y = +8.0\text{ m}$.
   - The obstacle field ends at $Y = +5.0\text{ m}$.
   - This provides an obstacle-free **$3.0\text{ m}$ terminal glide corridor** ($Y \in [+5.0, +8.0]$) leading directly to the target.
3. **Lateral Wall Clearance**:
   - Arena walls are located at $X = \pm 5.0\text{ m}$.
   - Obstacles are placed within $X \in [-3.5, +3.5]\text{ m}$.
   - This guarantees a minimum **$1.5\text{ m}$ outer corridor** between obstacles and side walls, ensuring that bypass paths always exist on the arena flanks.

---

## 5. Complete Perception Pipeline

### 5.1 Dual-Engine Rendering Architecture

The environment includes a dual-path rendering engine designed for zero-dependency portability:
1. **Primary Path**: PyBullet Hardware Renderer (`p.ER_TINY_RENDERER` or OpenGL GUI).
2. **Analytical Fallback**: High-contrast 3D Perspective Raycasting Engine with ambient lighting and procedural floor texturing.

---

### 5.2 Front-Facing Camera Rig & Projective Geometry

The camera is rigidly mounted to the front nose of the quadrotor:
- **Mount Offset**: $\Delta \mathbf{p}_{\text{cam}}^{\text{body}} = [0.0, 0.20, 0.0]^T\text{ m}$ (displaced $20\text{ cm}$ along the drone's local forward axis).
- **Camera Position**: $\mathbf{p}_{\text{cam}} = \mathbf{p}_{\text{drone}} + \mathbf{R}(\mathbf{q}) \cdot [0.0, 0.2, 0.0]^T$.
- **Camera Forward Vector**: $\mathbf{f}_{\text{cam}} = \mathbf{R}(\mathbf{q}) \cdot [0.0, 1.0, 0.0]^T$.
- **Camera Up Vector**: $\mathbf{u}_{\text{cam}} = \mathbf{R}(\mathbf{q}) \cdot [0.0, 0.0, 1.0]^T$.
- **Target Position**: $\mathbf{p}_{\text{target}} = \mathbf{p}_{\text{cam}} + \mathbf{f}_{\text{cam}}$.

#### 5.2.1 Camera Intrinsic & Extrinsic Parameters
- **Resolution**: $W = 84\text{ px}, H = 84\text{ px}$.
- **Field of View (FOV)**: $\theta_{\text{FOV}} = 65.0^\circ$ (symmetric vertical and horizontal).
- **Aspect Ratio**: $\text{Aspect} = \frac{W}{H} = \frac{84}{84} = 1.0$.
- **Near Clipping Plane**: $z_{\text{near}} = 0.1\text{ m}$.
- **Far Clipping Plane**: $z_{\text{far}} = 12.0\text{ m}$.
- **View Matrix**: Computed via `p.computeViewMatrix(cam_pos, target_pos, up)`.
- **Projection Matrix**: Computed via `p.computeProjectionMatrixFOV(65.0, 1.0, 0.1, 12.0)`.

---

### 5.3 Analytical Depth Buffer Linearization

PyBullet's `p.getCameraImage()` returns a non-linear normalized depth buffer $d_{\text{buffer}} \in [0.0, 1.0]$. The non-linear mapping originates from standard OpenGL perspective projection:
$$z_{\text{ndc}} = 2.0 \cdot d_{\text{buffer}} - 1.0$$
$$z_{\text{ndc}} = \frac{z_{\text{far}} + z_{\text{near}}}{z_{\text{far}} - z_{\text{near}}} - \frac{2 \cdot z_{\text{far}} \cdot z_{\text{near}}}{z \cdot (z_{\text{far}} - z_{\text{near}})}$$

Solving explicitly for linear metric depth $z_{\text{meters}}$ yields the exact formulation in `environment.py` (line 217):
$$D_{\text{meters}} = \frac{z_{\text{far}} \cdot z_{\text{near}}}{z_{\text{far}} - (z_{\text{far}} - z_{\text{near}}) \cdot d_{\text{buffer}}}$$

Substituting the environment constants $z_{\text{near}} = 0.1\text{ m}$ and $z_{\text{far}} = 12.0\text{ m}$:
$$D_{\text{meters}} = \frac{12.0 \times 0.1}{12.0 - (12.0 - 0.1) \cdot d_{\text{buffer}}} = \frac{1.2}{12.0 - 11.9 \cdot d_{\text{buffer}}}$$

---

### 5.4 Fallback 3D Perspective Raycasting Engine

When PyBullet is unavailable or executed in AppLocker-restricted environments, `IndoorDroneNavEnv._get_camera_images` executes an analytical CPU raycaster (lines 221–292):

#### 5.4.1 Ray Generation & Yaw Transformation
The effective focal length in pixels is:
$$f_{\text{px}} = \frac{W / 2}{\tan(\theta_{\text{FOV}} / 2)} = \frac{42.0}{\tan(32.5^\circ)} \approx \frac{42.0}{0.63707} \approx 65.927\text{ px}$$

For each pixel coordinate $(p_x, p_y) \in [0, 83] \times [0, 83]$:
$$\text{ray}_{dx} = \frac{p_x - 42.0}{f_{\text{px}}}, \quad \text{ray}_{dy} = 1.0, \quad \text{ray}_{dz} = -\frac{p_y - 42.0}{f_{\text{px}}}$$

Applying drone yaw angle $\psi$:
$$\begin{bmatrix} r_x \\ r_y \\ r_z \end{bmatrix} = \begin{bmatrix} \cos\psi & \sin\psi & 0 \\ -\sin\psi & \cos\psi & 0 \\ 0 & 0 & 1 \end{bmatrix} \begin{bmatrix} \text{ray}_{dx} \\ \text{ray}_{dy} \\ \text{ray}_{dz} \end{bmatrix}$$
$$\hat{\mathbf{r}} = \frac{[r_x, r_y, r_z]^T}{\sqrt{r_x^2 + r_y^2 + r_z^2}}$$

#### 5.4.2 Ray-Surface Intersections
1. **Floor Plane ($Z = 0$)**:
   For $r_z < -10^{-4}$:
   $$t_{\text{floor}} = \frac{0.0 - p_{\text{cam}, z}}{r_z} = -\frac{p_{\text{cam}, z}}{r_z}$$
   Intersection coordinates: $f_x = p_{\text{cam}, x} + r_x t_{\text{floor}}, f_y = p_{\text{cam}, y} + r_y t_{\text{floor}}$.
   Checkerboard procedural tile texture:
   $$\text{Parity} = (\lfloor f_x \rfloor + \lfloor f_y \rfloor) \pmod 2$$
   $$\text{Color} = \begin{cases} (230, 230, 230) \quad \text{(Bright White)}, & \text{if Parity} = 0 \\ (90, 90, 100) \quad \text{(Dark Slate)}, & \text{if Parity} = 1 \end{cases}$$

2. **Cylinder Primitive Intersection**:
   For cylinder centered at $(o_x, o_y)$ with radius $r$:
   $$\Delta x = p_{\text{cam}, x} - o_x, \quad \Delta y = p_{\text{cam}, y} - o_y$$
   $$a = r_x^2 + r_y^2, \quad b = 2 (\Delta x r_x + \Delta y r_y), \quad c = \Delta x^2 + \Delta y^2 - r^2$$
   $$\text{Discriminant } \Delta = b^2 - 4ac$$
   If $\Delta \ge 0$, nearest intersection parameter:
   $$t_{\text{cyl}} = \frac{-b - \sqrt{\Delta}}{2a}$$
   Valid if $0 < t_{\text{cyl}} < t_{\text{min}}$ and $0 \le (p_{\text{cam}, z} + r_z t_{\text{cyl}}) \le h_{\text{cyl}}$.

3. **Cuboid Primitive Bounding Sphere Intersection**:
   Approximates box with radius $r_{\text{approx}} = \max(e_x, e_y, e_z)$:
   $$\text{proj} = -(\Delta x r_x + \Delta y r_y)$$
   $$\text{perp} = \sqrt{\max(0, (\Delta x^2 + \Delta y^2) - \text{proj}^2)}$$
   Hit confirmed if $\text{perp} < r_{\text{approx}}$ and $0 < \text{proj} < t_{\text{min}}$.

#### 5.4.3 Ambient Shading Model
Surfaces are shaded with distance-based ambient light attenuation:
$$\text{Shade} = \max\left(0.45, \, 1.0 - 0.5 \cdot \frac{D_{\text{meters}}}{z_{\text{far}}}\right)$$
$$\text{Pixel Color} = \lfloor \mathbf{C}_{\text{hit}} \times \text{Shade} \rfloor$$

---

### 5.5 Observation Space Construction (5-Channel State)

The observation returned by `IndoorDroneNavEnv._get_observation()` (lines 396–416) is a Gymnasium `Dict` containing:
1. `"visual"`: Tensor of shape $(5, 84, 84)$ with `dtype=np.float32`.
   - **Channels 0, 1, 2**: Normalized RGB camera frame $I_{\text{rgb}} = \frac{\text{rgb}}{255.0} \in [0.0, 1.0]$.
   - **Channel 3**: Horizontal optical flow field $u(x, y) \in \mathbb{R}^{84 \times 84}$.
   - **Channel 4**: Vertical optical flow field $v(x, y) \in \mathbb{R}^{84 \times 84}$.
   - Converted to PyTorch-standard Channel-First format: $(C, H, W) = (5, 84, 84)$.
2. `"velocity"`: 3D linear velocity vector $\mathbf{v}_{\text{drone}} = [v_x, v_y, v_z]^T$ in $\text{m/s}$ with shape $(3,)$.

---

### 5.6 3rd-Person Overhead Simulation Visualizer

`IndoorDroneNavEnv.render_overhead_simulation_view` (lines 294–361) renders a real-time top-down 2D/3D map of dimensions $380 \times 380\text{ px}$:
- **World-to-Screen Transformation**:
  Maps arena coordinates $X \in [-5.0, 5.0]\text{ m}$ and $Y \in [-10.0, 10.0]\text{ m}$ onto the image frame with a $20\text{ px}$ margin:
  $$p_x = \text{int}\left( \frac{w_x + 5.0}{10.0} \cdot (380 - 40) + 20 \right) = \text{int}\left( \frac{w_x + 5.0}{10.0} \cdot 340 + 20 \right)$$
  $$p_y = \text{int}\left( \frac{10.0 - w_y}{20.0} \cdot (380 - 40) + 20 \right) = \text{int}\left( \frac{10.0 - w_y}{20.0} \cdot 340 + 20 \right)$$
- **Graphic Elements Rendered**:
  - Grid lines: Light gray grid every $2.0\text{ m}$ along X and Y.
  - Goal: Concentric gold rings ($r_1=14\text{ px}$, $r_2=18\text{ px}$, color $(0, 215, 255)$) with "GOAL" label.
  - Obstacles: Orange circles for cylinders, green rectangles for cuboids with dark borders.
  - Drone: Cyan circle ($r=10\text{ px}$), white outline ($r=12\text{ px}$), and red heading arrow ($20\text{ px}$ length, tip 0.4) oriented along drone yaw:
    $$h_x = p_x + \text{int}(20 \sin\psi), \quad h_y = p_y - \text{int}(20 \cos\psi)$$

---

## 6. Granular Code Inventory for `environment.py`

| Function / Method | Line Range | Input Arguments | Return Type | Primary Responsibility & Algorithmic Logic |
| :--- | :--- | :--- | :--- | :--- |
| `IndoorDroneNavEnv.__init__` | 28–90 | `gui: bool`, `seed: int`, `max_steps: int`, `tau_inv_max: float` | `None` | Initializes simulation hyperparameters, sets up Gymnasium action/observation spaces, connects to PyBullet engine, allocates buffers. |
| `_set_seed` | 92–94 | `seed: int` | `None` | Seeds the NumPy pseudo-random number generator for reproducible procedural layout generation. |
| `reset` | 101–132 | `seed=None`, `options=None` | `tuple (obs, info)` | Resets simulation, clears PyBullet bodies, resets gravity and timestep, re-spawns drone and obstacles, initializes observation. |
| `_spawn_indoor_obstacles` | 134–182 | `None` | `None` | Spawns 4 outer boundary walls and dynamically instantiates 6–11 random cylinders and boxes with collision and visual shapes. |
| `_get_camera_images` | 184–292 | `None` | `tuple (rgb, depth_meters)` | Computes camera view/projection matrices, renders RGB-D frames via PyBullet TinyRenderer, or invokes analytical 3D raycasting engine. |
| `render_overhead_simulation_view`| 294–361 | `out_size=(380, 380)` | `np.ndarray` | Generates a high-contrast 3rd-person top-down visualization of the arena, drone position, heading arrow, obstacles, and goal. |
| `_compute_optical_flow_and_tau`| 363–394 | `current_gray: np.ndarray` | `tuple (flow, tau_inv_bounded)` | Computes Farneback dense optical flow, Sobel gradients, flow divergence, 60% central ROI pooling, and bounded inverse TTC. |
| `_get_observation` | 396–416 | `None` | `dict` | Assembles 5-channel visual tensor ($3\text{ RGB} + 2\text{ Flow}$) and 3D velocity vector into Gymnasium observation dictionary. |
| `_clamp_to_arena` | 417–423 | `pos: array-like` | `tuple (clamped_pos, oob: bool)`| Evaluates spatial bounds against hard arena limits, clamps coordinates, and detects out-of-bounds boundary violations. |
| `step` | 425–532 | `action: np.ndarray` | `tuple (obs, reward, terminated, truncated, info)` | Clips action, maps to target velocity, integrates 8 physics substeps, evaluates collisions, computes multi-objective reward, checks termination. |
| `close` | 534–537 | `None` | `None` | Disconnects the active PyBullet physics client session cleanly. |

---

## 7. Architectural Synthesis & Recommendations for Downstream Documentation

1. **Precision in Equations**:
   The final documentation (`TECHNICAL_DOCUMENTATION.md` and `.docx`) should explicitly present both the conceptual reward formulation from `README.md` and the reinforced weights from `environment.py`, noting the addition of $R_{\text{progress}}$ ($6.0\times$) and the transition from strict $d_{\min}$ to robust 5th percentile depth $\text{P}_{5\%}(D)$.
2. **Sub-Step Mechanics Documentation**:
   Highlight that anti-tunneling coordinate clamping is evaluated **at every physics substep** ($240\text{ Hz}$), which is an essential design pattern for high-speed robotic simulations where substep penetration could otherwise corrupt contact manifolds.
3. **Perception Pipeline Verification**:
   Ensure the dual-path rendering architecture is documented as a primary resilience feature: the agent code runs identically whether accelerated by PyBullet EGL/TinyRenderer or through pure-NumPy analytical raycasting.
4. **Spatial IoU Integration**:
   Document how `environment.py`'s `last_depth_map` directly powers `explainability.py`'s Spatial IoU metric by generating ground-truth obstacle binary masks ($\text{depth} < 1.5\text{ m}$) against which XAI heatmaps are evaluated.

---
*End of Technical Audit Report (explorer_survey_1)*
