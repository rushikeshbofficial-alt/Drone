# Autonomous Drone Navigation through Random Obstacles in a Simulated Environment
## Architectural Treatise, Multi-Rate Physics Simulation, Deep Reinforcement Learning, and Granular Codebase Audit

**Author**: Principal Technical Systems Architect & Senior Flight Stack Researcher  
**Document Version**: 2.4.0 (Publication-Grade Academic Release)  
**Target Repository**: `c:\Users\Rushikesh\Desktop\Cool Ass Projects\Drone`  
**Date**: September 19, 2026  

---

## Executive Document Abstract & Metadata
- **Project Scope**: End-to-end vision-based autonomous quadrotor navigation in GPS-denied indoor procedural obstacle fields.
- **Methodologies**: PyBullet 240 Hz rigid-body dynamics decoupled with 24 Hz Gymnasium control, Gunnar Farneback dense optical flow, bounded inverse time-to-collision ($\tau^{-1}$ / TTC), Potential Field expert pre-training with Tangential Obstacle Steering, Proximal Policy Optimization (PPO) with Generalized Advantage Estimation (GAE-$\lambda$), and real-time Captum Explainable AI (XAI) with Spatial IoU fidelity.
- **Audited Codebase Scope**: `environment.py`, `model.py`, `pretrain_bc.py`, `train.py`, `explainability.py`, `evaluate_and_visualize.py`, `run_project.bat`, `overnight_train.bat`, `requirements.txt`, and `README.md`.
- **Hardware Acceleration**: NVIDIA Blackwell `sm_120` architecture, TensorFloat-32 (TF32), Automatic Mixed Precision (AMP FP16), and PyTorch Inductor kernel compilation (`torch.compile`).

---

# Chapter 1: Executive Summary

### 1.1 Research Context & Operational Motivation
Autonomous aerial navigation within unstructured, GPS-denied indoor environments represents one of the most demanding frontiers in modern robotics, embodied artificial intelligence, and cyber-physical systems control. Unlike outdoor long-range unmanned aerial systems (UAS) that leverage multi-constellation Global Navigation Satellite Systems (GNSS) such as GPS, GLONASS, and Galileo to obtain continuous sub-meter spatial positioning, indoor micro-aerial vehicles (MAVs) operate in complete sensory deprivation regarding absolute world-frame coordinates. In complex industrial warehouses, subterranean facilities, disaster ruins, and multi-compartment building interiors, electromagnetic signals are subjected to severe multi-path attenuation, total signal shadowing, and unpredictable RF interference. Furthermore, the reliance on active spatial ranging payloads such as heavy multi-beam 3D LiDAR scanners, solid-state depth arrays, or rotating laser rangefinders introduces severe structural trade-offs. Such sensors impose excessive electrical power draw, generate prohibitive thermal dissipation profiles, and dramatically elevate physical payload mass, which catastrophically reduces quadrotor battery endurance from tens of minutes down to mere minutes. Consequently, achieving high-speed, agile, collision-free autonomous flight demands lightweight, passive monocular optical perception coupled with high-frequency kinematic feedback and advanced deep learning policy representations.

Historically, classical trajectory generation and obstacle avoidance methods have relied on deterministic geometric representations, including OctoMaps, Euclidean Signed Distance Fields (ESDF), and sampling-based motion planners such as Rapidly-exploring Random Trees (RRT*) or Probabilistic Roadmaps (PRM). While mathematically rigorous under quasi-static assumptions, these classical pipelines exhibit critical bottlenecks when deployed in real-time embedded flight stacks. They require significant computational overhead for continuous volumetric voxel map updates, suffer from severe latency when re-planning through newly discovered obstacles, and are fundamentally brittle to sensor calibration drifts, depth camera dropouts, and sudden lighting transitions. Conversely, end-to-end Deep Reinforcement Learning (DRL) offers the transformative promise of directly mapping raw pixel streams and onboard IMU kinematics to continuous motor commands in sub-second inference cycles. However, standard model-free reinforcement learning applied tabula rasa to cluttered 3D navigation suffers from catastrophic exploration collapse. In environments where random exploratory trajectories result in immediate collisions within the initial meters of flight (>98% crash probability), sparse-reward agents experience vanishing policy gradients, value function divergence, and policy entrapment in uniform spin or hover failure modes.

### 1.2 High-Level Project Objectives & System Capabilities
The Autonomous Drone Navigation through Random Obstacles project addresses these fundamental bottlenecks by architecting a multi-paradigm flight stack that synthesizes physics-informed simulation mechanics, expert algorithmic imitation learning, robust policy gradient reinforcement learning, and real-time white-box explainability. The core objectives encompass:

1. **Sub-Second Reactive Flight Control**: Executing closed-loop 4D velocity and yaw-rate control at 24 Hz Gymnasium step frequency, coupled to a 240 Hz rigid-body physics integrator running inside PyBullet with exactly 8 physics substeps per control cycle.
2. **Dense Optical Flow & Looming Divergence**: Extracting real-time motion displacement vectors using the two-frame Gunnar Farneback polynomial expansion algorithm, calculating spatial flow divergence across a 60% central Region of Interest (ROI) to isolate looming expansion from peripheral parallax shear, and deriving a bounded inverse time-to-collision ($\tau^{-1}$ / TTC) metric.
3. **Algorithmic Potential Field Imitation Bootstrapping**: Resolving the RL exploration bottleneck by generating 80,000 expert demonstration transitions via a deterministic artificial potential field planner featuring Tangential Obstacle Steering (prohibiting reverse flight and deflecting laterally around obstacles to eliminate collinear local minima traps), followed by supervised Behavioral Cloning (BC) pre-training.
4. **Multi-Objective Physics-Informed Policy Optimization**: Fine-tuning the pre-trained actor-critic policy via Proximal Policy Optimization (PPO) with Generalized Advantage Estimation (GAE-$\lambda$, $\gamma=0.99, \lambda=0.95$), driven by a composite reward shaping function balancing distance progress, goal heading velocity alignment, visual looming penalties, attitude stability, and 5th-percentile depth safety margins.
5. **White-Box Explainable AI (XAI) & Spatial Fidelity**: Integrating PyTorch Captum gradient attribution (live Vanilla Saliency at 30+ FPS and offline Integrated Gradients over 30 Riemann steps), generating high-definition Google TURBO colormap heatmaps with neon peak contours, and quantitatively scoring explanation fidelity via Spatial IoU against ground-truth obstacle depth masks.
6. **Hardware Accelerator Optimizations**: Leveraging NVIDIA Blackwell `sm_120` architecture, TensorFloat-32 (TF32) tensor math, Automatic Mixed Precision (AMP FP16) gradient scaling, and PyTorch Inductor kernel compilation (`torch.compile`) to achieve high simulation throughput (SPS > 1,800).

---

# Chapter 2: System Architecture

### 2.1 High-Level Component Topology & Seven Subsystems
The system architecture is structured as a modular, high-throughput autonomous robotics pipeline that bridges physical simulation, neural representation learning, policy optimization, and real-time visualization. The seven core subsystems comprise:
1. **Perception & Simulation Engine (`environment.py`)**: Implements the Gymnasium `IndoorDroneNavEnv` class, encapsulating PyBullet physics, multi-rate 240Hz/24Hz integration, procedural obstacle generation, 3D perspective raycasting fallback, Farneback optical flow computation, and multi-objective reward evaluation.
2. **Representation & Control Policy (`model.py`)**: Implements the `PhysicsInformedActorCritic` neural network, containing a NatureCNN visual feature extractor, kinematic MLP branch, 256-dimensional latent fusion manifold, continuous 4D Actor head, and scalar Critic head, supported by a pure-NumPy CPU fallback engine.
3. **Expert Imitation Learning Planner (`pretrain_bc.py`)**: Implements algorithmic potential field navigation with Tangential Obstacle Steering, demonstration dataset collection (`bc_demos.npz`), and supervised MSE training loops with Cosine Annealing.
4. **Distributed PPO Engine (`train.py`)**: Manages multi-process `SubprocVecEnv` vectorized simulation across $N$ parallel workers, GAE-$\lambda$ advantage computation, AMP FP16 mixed-precision optimization, TensorBoard telemetry streaming, and safe model checkpoint serialization (`best_model.pt`).
5. **Explainable AI Attribution Engine (`explainability.py`)**: Encapsulates `CaptumExplainabilityEngine` / `DroneXAIEngine`, performing dual-input autograd backpropagation, channel max-pooling, 7-stage high-definition thermal rendering, and Spatial IoU explanation fidelity calculation.
6. **Telemetry & Multi-Seed Benchmarking Dashboard (`evaluate_and_visualize.py`)**: Composes a unified 3-panel HD OpenCV canvas ($1230 \times 510$ px) displaying 3D top-down tracking, first-person optical flow vectors, and TURBO heat vision overlays with automated performance benchmarking across unseen seeds.
7. **Windows Batch Automation Subsystem (`run_project.bat`, `overnight_train.bat`)**: Provides centralized menu dispatching, CUDA environment locking, multi-hour 4M-step automation, and Windows automated shutdown safety traps.

### 2.2 End-to-End System Block Diagram
```
+----------------------------------------------------------------------------------------------------+
|                                    END-TO-END AUTONOMOUS FLIGHT STACK                              |
|                                                                                                    |
|  +----------------------------------------------------------------------------------------------+  |
|  |                            PYBULLET 3D SIMULATION ENVIRONMENT (240 Hz)                       |  |
|  |                                                                                              |  |
|  |  [Drone Rigid Body (1kg)] <===> [Procedural Obstacles] <===> [Clamped Boundary Walls]       |  |
|  |            |                                                              |                  |  |
|  |            | 8 Substeps / Control Cycle                                   | GJK / EPA        |  |
|  |            v                                                              v Contacts         |  |
|  |   [Kinematic Velocity]                                           [Collision Detector]        |  |
|  |     (vx, vy, vz) in m/s                                                   |                  |  |
|  +------------|--------------------------------------------------------------|------------------+  |
|               |                                                              |                     |
|               |              +-----------------------------------------------+                     |
|               |              |                                                                     |
|               v              v                                                                     |
|  +----------------------------------------------------------------------------------------------+  |
|  |                             GYMNASIUM CONTROL INTERFACE (24 Hz)                              |  |
|  |                                                                                              |  |
|  |   +-----------------------+     +------------------------+     +--------------------------+  |  |
|  |   | Monocular RGB Camera  | --> | Farneback Optical Flow | --> | 60% Central ROI Divergence| |  |
|  |   | (84x84x3 Front-Facing)|     | (84x84x2 Motion Field) |     | Bounded tau^-1 in [0, 5] |  |  |
|  |   +-----------------------+     +------------------------+     +--------------------------+  |  |
|  |               |                             |                               |                |  |
|  |               +--------------+--------------+                               v                |  |
|  |                              v                                    [Multi-Objective Reward]   |  |
|  |                 [5-Channel Visual Tensor]                         (Progress, Goal, TTC,      |  |
|  |                   (B, 5, 84, 84) in [0, 1]                         Attitude, Safety Buffer)  |  |
|  +------------------------------|----------------------------------------------|----------------+  |
|                                 |                                              |                   |
|               +-----------------+-------------------+                          |                   |
|               |                                     |                          |                   |
|               v                                     v                          |                   |
|  +---------------------------+       +---------------------------+             |                   |
|  |    NatureCNN Conv Stack   |       |   Kinematic MLP Branch    |             |                   |
|  | (5->32->64->64 -> 512 Lat)|       |  (Linear 3 -> 64 Latent)  |             |                   |
|  +---------------------------+       +---------------------------+             |                   |
|               \                                     /                          |                   |
|                \-----------------+-----------------/                           |                   |
|                                  v                                             |                   |
|                     [Fused Latent Manifold (256)]                              |                   |
|                                  |                                             |                   |
|                 +----------------+----------------+                            |                   |
|                 v                                 v                            |                   |
|       [Actor Head (mu in [-1,1]^4)]      [Critic Head (V(s))]                  |                   |
|                 |                                 |                            |                   |
|                 v                                 v                            |                   |
|       [Continuous 4D Action]             [Baseline State Value]                |                   |
|     (vx, vy, vz, yaw_rate)                        |                            |                   |
|                 |                                 +------------+---------------+                   |
|                 v                                              |                                   |
|  +---------------------------+                                 v                                   |
|  | Motor Actuation / Physics |                 +-------------------------------+                   |
|  | resetBaseVelocity()       |                 | PPO Engine / GAE-lambda Loss  |                   |
|  +---------------------------+                 +-------------------------------+                   |
+----------------------------------------------------------------------------------------------------+
```

### 2.3 Training vs. Inference Execution Lifecycles
```
====================================================================================================
TRAINING PIPELINE (train.py): VECTORIZED ASYNCHRONOUS ACTOR-CRITIC RL
====================================================================================================

 [SubprocVecEnv] (N=8 to 16 Subprocesses via Windows spawn)
   |-- Worker 1: IndoorDroneNavEnv (Seed 42)    --> Auto-Reset on Terminate --+
   |-- Worker 2: IndoorDroneNavEnv (Seed 43)    --> Auto-Reset on Terminate --|
   |-- ...                                                                    |--> Batched Tensors
   +-- Worker N: IndoorDroneNavEnv (Seed 42+N)  --> Auto-Reset on Terminate --+    (N, 5, 84, 84) & (N, 3)
                                                                                   |
                                                                                   v
 [RolloutBuffer] <-----------------------------------------------------------------+
   Accumulates T=512 steps across N workers (Total: 4,096 to 8,192 transitions)
   Stores: vis_obs, vel_obs, actions, log_probs, rewards, dones, values
   |
   +--> compute_gae() (GPU-Native Vectorized Bellman Trace, gamma=0.99, lambda=0.95)
          Calculates Advantages A_t and Returns R_t
          Advantage Normalization: A_norm = (A - mean(A)) / (std(A) + 1e-8)
          |
          v
 [PPO Mini-Batch Optimization Loop] (10 Epochs, Mini-Batch Size: 512 to 2048)
   |-- PyTorch Inductor: torch.compile(mode="reduce-overhead")
   |-- Hardware Core: TensorFloat-32 (TF32) on NVIDIA Blackwell sm_120
   |-- Precision: Automatic Mixed Precision (AMP FP16) + GradScaler
   |-- Losses: L_total = L_CLIP + 0.5 * L_VF - 0.01 * S[pi]
   +-- Optimizer: Adam (lr=3e-4) with gradient clipping norm <= 1.0
          |
          v
 [Safe Checkpoint Serializer] --> Unwraps OptimizedModule --> Saves "best_model.pt"

====================================================================================================
INFERENCE & EVALUATION PIPELINE (evaluate_and_visualize.py): REAL-TIME XAI
====================================================================================================

 [IndoorDroneNavEnv] (Single Environment, Headless or GUI)
   |
   +--> Camera Image (84x84x3) & Optical Flow (84x84x2)
   |
   v
 [PhysicsInformedActorCritic] (Loaded from "best_model.pt", eval mode)
   |-- Forward Pass: mu = policy(vis, vel)
   +-- Action Execution: v_target = mu[:3] * 3.0 m/s, yaw_rate = mu[3] * 1.0 rad/s
   |
   v
 [DroneXAIEngine] (Captum Saliency / Integrated Gradients)
   |-- Dual-Input Backward Pass: d(mu_0) / d(vis_tensor)
   |-- Channel Max-Pool: (5, 84, 84) --> (84, 84) 2D Attribution
   |-- High-Definition Thermal Synthesis: Bicubic 390x390, Gaussian, Gamma 0.7, TURBO
   +-- Spatial IoU Fidelity Check against ground-truth depth (< 1.5 m)
   |
   v
 [Unified 3-Panel HD Canvas] (1230 x 510 px OpenCV Window at 30+ FPS)
```

### 2.4 State Space & Observation Representation
The observation space is formulated as a Gymnasium `Dict` containing two complementary sensory modalities:
1. **Visual Observation Tensor**: $\mathbf{o}_{\text{vis}} \in \mathbb{R}^{5 \times 84 \times 84}$.
   - Channels 0, 1, 2: Normalized RGB pixel intensities in $[0.0, 1.0]$.
   - Channels 3, 4: Horizontal ($u$) and vertical ($v$) dense optical flow fields calculated via the Gunnar Farneback algorithm.
2. **Kinematic Odometry Tensor**: $\mathbf{o}_{\text{vel}} \in \mathbb{R}^3$.
   - Encodes linear world-frame velocities $(v_x, v_y, v_z)$ in $\text{m/s}$, bounded within $[-10.0, 10.0]$ m/s.

### 2.5 Continuous Action Space & Kinematics Mapping
The continuous action space comprises a 4-dimensional normalized vector $\mathbf{a} = [a_x, a_y, a_z, a_\psi]^T \in [-1.0, 1.0]^4$. In `IndoorDroneNavEnv.step()`, this vector is mapped to linear velocity and yaw-rate setpoints:
$$\mathbf{v}_{\text{target}} = \begin{bmatrix} a_x \\ a_y \\ a_z \end{bmatrix} \times 3.0 \text{ m/s}, \quad \dot{\psi}_{\text{target}} = a_\psi \times 1.0 \text{ rad/s} \quad (\approx 57.3^\circ/\text{s})$$

---

# Chapter 3: Simulation Environment Mechanics

### 3.1 Multi-Rate Physics/Control Coupling
The simulation framework in `environment.py` couples rigid-body dynamics in PyBullet at $f_{\text{physics}} = 240.0$ Hz ($\Delta t = 4.167$ ms) with Gymnasium agent decision steps at $f_{\text{control}} = 24.0$ Hz ($\Delta T = 41.667$ ms), yielding exactly $N_{\text{substeps}} = 240 / 24 = 8$ physics substeps per control step.

```
Gymnasium Control Cycle (24 Hz, Delta_T = 41.667 ms)
+----------------------------------------------------------------------------------------------------+
| Step t: Receive Continuous Action a_t = [ax, ay, az, ayaw]^T in [-1, 1]^4                         |
| Target Velocity: v_target = [ax, ay, az] * 3.0 m/s,  omega_target = [0, 0, ayaw] * 1.0 rad/s      |
|                                                                                                    |
| PyBullet Substep Loop (240 Hz, Delta_t = 4.167 ms, 8 Iterations):                                 |
|   +---------------------------------------------------------------------------------------------+  |
|   | Substep k in {1, 2, 3, 4, 5, 6, 7, 8}:                                                      |  |
|   |   1. Enforce velocity command: p.resetBaseVelocity(drone_id, v_target, omega_target)        |  |
|   |   2. Advance physics integrator: p.stepSimulation(physicsClientId)                          |  |
|   |   3. Query current body position: pos = p.getBasePositionAndOrientation(drone_id)[0]        |  |
|   |   4. Anti-Tunneling Clamping Check:                                                         |  |
|   |        pos_clamped = clip(pos, [-4.6, -9.6, 0.15], [4.6, 9.6, 3.5])                         |  |
|   |        if pos_clamped != pos:                                                               |  |
|   |            latch out_of_bounds = True                                                       |  |
|   |            p.resetBasePositionAndOrientation(drone_id, pos_clamped, orn)                    |  |
|   |            p.resetBaseVelocity(drone_id, [0, 0, 0], [0, 0, 0])                              |  |
|   +---------------------------------------------------------------------------------------------+  |
|                                                                                                    |
| Post-Physics Observation & Reward Calculation:                                                     |
|   1. Render Camera: TinyRenderer / Raycaster -> RGB Frame (84x84) + Metric Depth Map D (84x84)    |
|   2. Farneback Flow: cv2.calcOpticalFlowFarneback(prev_gray, curr_gray) -> Flow (84x84x2)          |
|   3. Central ROI Looming: Sobel divergence over 60% central ROI -> tau^-1 bounded in [0, 5]        |
|   4. Collision Evaluation: p.getContactPoints() > 0 or out_of_bounds == True                       |
|   5. Compute Multi-Objective Reward: R_t = R_prog + R_goal + R_ttc + R_att + R_prox + R_term      |
|   6. Assemble Gymnasium Observation Dict: {"visual": (5, 84, 84), "velocity": (3,)}               |
+----------------------------------------------------------------------------------------------------+
```

### 3.2 Anti-Tunneling Sub-Step Boundary Clamping
In discrete-time physics integration, high-velocity bodies can penetrate or pass through collision boundaries within a single control step (tunneling). At $v_{\max} = 3.0$ m/s, the quadrotor moves $0.125$ m per control step. In `environment.py`, `_clamp_to_arena()` checks positions every $4.167$ ms against:
$$\text{ARENA\_X\_LIM} = 4.6\text{ m}, \quad \text{ARENA\_Y\_LIM} = 9.6\text{ m}, \quad \text{ARENA\_Z\_MIN} = 0.15\text{ m}, \quad \text{ARENA\_Z\_MAX} = 3.5\text{ m}$$
If coordinates breach these bounds, the drone position is clamped, velocity is nullified to $[0, 0, 0]$, `out_of_bounds` is latched to `True`, and the episode terminates with a $-100.0$ penalty.

### 3.3 Procedural Obstacle Generation & Clearance Corridors
The arena encompasses $X \in [-5.0, 5.0]$ m, $Y \in [-10.0, 10.0]$ m, and $Z \in [0.0, 4.0]$ m. The drone spawns at $\mathbf{p}_{\text{start}} = [0.0, -8.0, 1.5]$ m and navigates to $\mathbf{p}_{\text{goal}} = [0.0, 8.0, 1.5]$ m. Upon each reset, `_spawn_indoor_obstacles()` instantiates $N_{\text{obs}} \sim \mathcal{U}_{\text{discrete}}\{6, \dots, 11\}$ obstacles consisting of vertical cylinders ($r \in [0.35, 0.65]$ m, $h \in [2.5, 4.0]$ m, Coral RGB) and floating cuboids ($e_x, e_y, e_z \in [0.35, 0.65]$ m, $z \in [1.0, 2.5]$ m, Emerald RGB). Clearance corridors ensure navigability:
- Initial spawn buffer: $Y \in [-8.0, -5.0]$ m (3.0 m obstacle-free zone).
- Terminal goal buffer: $Y \in [5.0, 8.0]$ m (3.0 m obstacle-free arrival zone).
- Lateral flank channels: $X \in [3.5, 5.0]$ m and $X \in [-5.0, -3.5]$ m.

### 3.4 Camera Projection & Linear Metric Depth Recovery
The front-facing camera has field-of-view $\theta_{\text{FOV}} = 65^\circ$, near plane $z_{\text{near}} = 0.1$ m, far plane $z_{\text{far}} = 12.0$ m, and resolution $84 \times 84$. Linear metric depth $D_{\text{meters}}$ is recovered from the non-linear OpenGL buffer $d_{\text{buffer}} \in [0.0, 1.0]$ via:
$$D_{\text{meters}} = \frac{z_{\text{far}} \cdot z_{\text{near}}}{z_{\text{far}} - (z_{\text{far}} - z_{\text{near}}) \cdot d_{\text{buffer}}} = \frac{12.0 \times 0.1}{12.0 - (12.0 - 0.1) \cdot d_{\text{buffer}}} = \frac{1.2}{12.0 - 11.9 \cdot d_{\text{buffer}}}$$

### 3.5 Gunnar Farneback Optical Flow & Central ROI Divergence ($\tau^{-1}$)
Dense optical flow estimates displacement $\mathbf{d} = [u, v]^T$ across consecutive frames modeled as quadratic surfaces:
$$f_1(\mathbf{x}) = \mathbf{x}^T \mathbf{A}_1 \mathbf{x} + \mathbf{b}_1^T \mathbf{x} + c_1, \quad f_2(\mathbf{x}) = \mathbf{x}^T \mathbf{A}_2 \mathbf{x} + \mathbf{b}_2^T \mathbf{x} + c_2$$
Assuming $f_2(\mathbf{x}) = f_1(\mathbf{x} - \mathbf{d})$, coefficient comparison yields:
$$\mathbf{d}(\mathbf{x}) = -\frac{1}{2} \mathbf{A}_1^{-1} (\mathbf{b}_2 - \mathbf{b}_1)$$
Weighted over neighborhood window $w(\Delta \mathbf{x})$:
$$\mathbf{d}(\mathbf{x}) = \left( \sum w \mathbf{A}^T \mathbf{A} \right)^{-1} \sum w \mathbf{A}^T \Delta \mathbf{b}$$
Parameters: `pyr_scale=0.5`, `levels=2`, `winsize=9`, `iterations=2`, `poly_n=5`, `poly_sigma=1.1`.

Visual looming relates to flow divergence:
$$\nabla \cdot \mathbf{u} = \frac{\partial u}{\partial x} + \frac{\partial v}{\partial y} = 2 \frac{V_z}{Z} = 2 \tau^{-1}$$
Spatial derivatives are estimated with $3 \times 3$ Sobel kernels $\mathbf{K}_x, \mathbf{K}_y$. To exclude peripheral wall shear, divergence is accumulated over the 60% central ROI ($16 \le x, y < 68$, $52 \times 52$ pixels, $38.3\%$ of frame area):
$$\bar{E}_{\text{ROI}} = \frac{1}{|\mathcal{M}_{\text{ROI}}|} \sum_{(x, y) \in \mathcal{M}_{\text{ROI}}} (\nabla \cdot \mathbf{u})(x, y)$$
Bounded non-negative inverse time-to-collision:
$$\tau^{-1}_{\text{bounded}} = \min\left( \max(0.0, \, \bar{E}_{\text{ROI}}), \, 5.0 \right) \in [0.0, 5.0] \text{ s}^{-1}$$

### 3.6 Multi-Objective Physics-Informed Reward Shaping
The composite step reward is evaluated as:
$$R_t = R_{\text{progress}} + R_{\text{goal}} + R_{\text{TTC}} + R_{\text{attitude}} + R_{\text{proximity}} + R_{\text{terminal}}$$
Where:
1. $R_{\text{progress}} = 6.0 \cdot (\|\mathbf{p}_{t-1} - \mathbf{p}_{\text{goal}}\|_2 - \|\mathbf{p}_t - \mathbf{p}_{\text{goal}}\|_2)$
2. $R_{\text{goal}} = 3.0 \cdot (\mathbf{v}_{\text{drone}} \cdot \hat{\mathbf{d}}_{\text{goal}})$
3. $R_{\text{TTC}} = -2.0 \cdot \tau^{-1}_{\text{bounded}}$
4. $R_{\text{attitude}} = -0.5 \cdot (|\phi| + |\theta|)$
5. $R_{\text{proximity}} = -3.0 \cdot (1.5 - \text{Percentile}_{5\%}(D_{\text{meters}}))$ if $< 1.5$ m, else $0.0$
6. $R_{\text{terminal}} = +100.0$ if reached goal ($d < 0.8$ m); $-100.0$ on collision or out-of-bounds; $0.0$ otherwise.

### Table 1: Physical, Simulation & Timing Parameters
| Parameter Description | Variable / Constant | Numerical Value | Physical Units | Subsystem / Location |
|---|---|---|---|---|
| Physics Engine Clock Rate | $f_{\text{physics}}$ | `240.0` | Hz | PyBullet (`environment.py`) |
| Control Loop Step Rate | $f_{\text{control}}$ | `24.0` | Hz | Gymnasium (`environment.py`) |
| Substeps per Control Step | $N_{\text{substeps}}$ | `8` | integer | `step()` loop (`environment.py`) |
| Gravitational Acceleration | $\mathbf{g}$ | `[0.0, 0.0, -9.81]` | $\text{m/s}^2$ | PyBullet world gravity |
| Quadrotor Base Mass | $m_{\text{drone}}$ | `1.0` | kg | Rigid-body chassis |
| Quadrotor Collision Footprint | Half-extents | `[0.20, 0.20, 0.08]` | meters | Box footprint: $40 \times 40 \times 16$ cm |
| Arena Lateral Span (X) | $X_{\text{bounds}}$ | `[-5.0, +5.0]` | meters | Outer wall boundary |
| Arena Longitudinal Span (Y)| $Y_{\text{bounds}}$ | `[-10.0, +10.0]`| meters | Outer wall boundary |
| Arena Vertical Span (Z) | $Z_{\text{bounds}}$ | `[0.0, 4.0]` | meters | Floor to ceiling boundary |
| Hard Anti-Tunneling Clamping X | `ARENA_X_LIM` | `4.6` | meters | Substep clamping boundary |
| Hard Anti-Tunneling Clamping Y | `ARENA_Y_LIM` | `9.6` | meters | Substep clamping boundary |
| Hard Anti-Tunneling Clamping Z | `ARENA_Z_MIN, MAX`| `0.15, 3.5` | meters | Substep clamping boundary |
| Drone Initial Spawn Position | $\mathbf{p}_{\text{start}}$ | `[0.0, -8.0, 1.5]`| meters | Episode initialization |
| Target Goal Position | $\mathbf{p}_{\text{goal}}$ | `[0.0, +8.0, 1.5]`| meters | Static goal circle |
| Goal Arrival Radius | $d_{\text{goal\_thresh}}$ | `0.8` | meters | Milestone success threshold |
| Maximum Linear Velocity | $v_{\max}$ | `3.0` | m/s | Continuous action mapping |
| Maximum Yaw Rate | $\dot{\psi}_{\max}$ | `1.0` | rad/s | Continuous action mapping ($\approx 57.3^\circ$/s) |

---

# Chapter 4: Drone Navigation & Algorithmic Foundations

### 4.1 Dual-Branch NatureCNN Actor-Critic Architecture
The neural network in `model.py` maps the dual-stream observation to continuous action distributions and baseline value predictions.

```
VISUAL STREAM: (B, 5, 84, 84)                        KINEMATIC STREAM: (B, 3)
[Channels 0-2: RGB, Channels 3-4: Flow]                     [vx, vy, vz] in m/s
                |                                                     |
  nn.Conv2d(in=5, out=32, k=8, s=4)                           nn.Linear(3, 64)
                |                                                     |
             nn.ReLU()                                             nn.ReLU()
                |                                                     |
  nn.Conv2d(in=32, out=64, k=4, s=2)                                  |
                |                                                     |
             nn.ReLU()                                                |
                |                                                     |
  nn.Conv2d(in=64, out=64, k=3, s=1)                                  |
                |                                                     |
             nn.ReLU()                                                |
                |                                                     |
  nn.Flatten() -> (B, 3136)                                           |
                |                                                     |
  nn.Linear(3136, 512)                                                |
                |                                                     |
             nn.ReLU()                                                |
                |                                                     |
       Visual Latent (B, 512)                                Kinematic Latent (B, 64)
                \                                                     /
                 \-------------------------\ /-----------------------/
                                            v
                                Feature Concatenation: (B, 576)
                                            |
                                   nn.Linear(576, 256)
                                            |
                                         nn.ReLU()
                                            |
                                  Shared Latent: (B, 256)
                                            |
                       +--------------------+--------------------+
                       |                                         |
                 [Actor Head]                              [Critic Head]
              nn.Linear(256, 128)                       nn.Linear(256, 128)
                       |                                         |
                    nn.ReLU()                                 nn.ReLU()
                       |                                         |
              nn.Linear(128, 4)                         nn.Linear(128, 1)
                       |                                         |
                    nn.Tanh()                              nn.Identity()
                       |                                         |
               mu in [-1.0, 1.0]^4                              V(s)
                       |                                       (B,)
             actor_log_std (4,)
                       |
        Normal(mu, exp(actor_log_std))
```

Convolutional spatial output dimension formula:
$$W_{\text{out}} = \left\lfloor \frac{W_{\text{in}} - K + 2P}{S} \right\rfloor + 1$$
- Conv1: $\lfloor \frac{84 - 8}{4} \rfloor + 1 = 20 \implies (B, 32, 20, 20)$
- Conv2: $\lfloor \frac{20 - 4}{2} \rfloor + 1 = 9 \implies (B, 64, 9, 9)$
- Conv3: $\lfloor \frac{9 - 3}{1} \rfloor + 1 = 7 \implies (B, 64, 7, 7) \implies 64 \times 7 \times 7 = 3,136$

Stochastic policy distribution:
$$\pi_\theta(\mathbf{a} \mid s) = \mathcal{N}(\boldsymbol{\mu}(s), \boldsymbol{\Sigma}), \quad \boldsymbol{\Sigma} = \text{diag}(\exp(2 \cdot \text{actor\_log\_std}))$$
Action log-probability:
$$\log \pi_\theta(\mathbf{a} \mid s) = \sum_{i=1}^4 \left[ -\frac{1}{2} \log(2\pi) - \log \sigma_i - \frac{(a_i - \mu_i(s))^2}{2 \sigma_i^2} \right]$$
Differential policy entropy:
$$H(\pi_\theta(\cdot \mid s)) = 2(1 + \log(2\pi)) + \sum_{i=1}^4 \log \sigma_i$$

### 4.2 Potential Field Expert & Tangential Obstacle Steering
To bypass the exploration bottleneck in cluttered 3D space, `pretrain_bc.py` uses an algorithmic potential field expert featuring Tangential Obstacle Steering:

```
                                 Target Goal [0.0, 8.0, 1.5]
                                              ^
                                              |
                                              | F_att (Strong Forward Pull)
                                              |
                                    +-------------------+
                                    | Dynamic Obstacle  |
                                    | (Cylinder or Box) |
                                    +-------------------+
                                      /               \
              F_rep,lat              /                 \              F_rep,lat
         (-vx Lateral Push)         /                   \        (+vx Lateral Push)
        <--------------------------+                     +-------------------------->
                                    \                   /
                                     \                 /
                                      \               /
                                       \             /
                                      Drone [x, y, z]
                                  Forward Surge: vy >= 0.35
                                 (Collinear Deadlock ELIMINATED)
```

Mathematical formulations of expert forces:
1. Attractive Goal Force:
   $$v_{y, \text{desired}} = \min\left(1.0, \, \max\left(0.4, \, \frac{\|\mathbf{p}_{\text{goal}} - \mathbf{p}_{\text{drone}}\|_2}{3.0}\right)\right), \quad v_{x, \text{desired}} = 0.8 \cdot \frac{x_{\text{goal}} - x_{\text{drone}}}{\|\mathbf{p}_{\text{goal}} - \mathbf{p}_{\text{drone}}\|_2 + 10^{-6}}$$
2. Tangential Obstacle Repulsion ($d_{\text{eff}} < 1.8$ m):
   $$F_{\text{rep}} = \frac{1.8 - \max(0.05, d_{\text{eff}})}{1.8}, \quad v_{x, \text{repulse}} \leftarrow v_{x, \text{repulse}} + \text{sign}(x_{\text{drone}} - x_{\text{obs}}) \cdot 2.0 \cdot F_{\text{rep}}$$
   $$v_y = \text{clip}(v_{y, \text{desired}} - v_{y, \text{slowdown}}, \, 0.35, \, 1.0) \quad (\text{Guarantees } v_y \ge 0.35 \text{ m/s})$$
3. Boundary Repulsion & Altitude Hold:
   $$v_{x, \text{wall}} = \pm 2.5 \cdot (|x| - 3.2) \quad (\text{if } |x| > 3.2\text{ m}), \quad v_z = \text{clip}(2.0 \cdot (1.5 - z), \, -0.6, \, 0.6)$$
4. Supervised MSE Objective:
   $$\mathcal{L}_{\text{BC}}(\theta) = \frac{1}{B} \sum_{i=1}^B \|\boldsymbol{\mu}_\theta(s_{\text{vis}, i}, s_{\text{vel}, i}) - \mathbf{a}_{\text{expert}, i}\|_2^2$$

### 4.3 Proximal Policy Optimization (PPO) & GAE-$\lambda$
The policy is optimized using PPO with Generalized Advantage Estimation:
1. Probability Ratio:
   $$r_t(\theta) = \frac{\pi_\theta(\mathbf{a}_t \mid s_t)}{\pi_{\theta_{\text{old}}}(\mathbf{a}_t \mid s_t)} = \exp\left(\log \pi_\theta(\mathbf{a}_t \mid s_t) - \log \pi_{\theta_{\text{old}}}(\mathbf{a}_t \mid s_t)\right)$$
2. Clipped Surrogate Objective:
   $$L^{\text{CLIP}}(\theta) = \hat{\mathbb{E}}_t \left[ \min\left( r_t(\theta) \hat{A}_t, \, \text{clip}(r_t(\theta), 1 - \epsilon, 1 + \epsilon) \hat{A}_t \right) \right], \quad \epsilon = 0.2$$
3. Temporal Difference Residual & GAE-$\lambda$:
   $$\delta_t^V = r_t + \gamma V(s_{t+1}) (1 - d_t) - V(s_t)$$
   $$\hat{A}_t^{\text{GAE}(\gamma, \lambda)} = \delta_t^V + (\gamma \lambda) (1 - d_t) \hat{A}_{t+1}^{\text{GAE}(\gamma, \lambda)}, \quad \gamma = 0.99, \, \lambda = 0.95$$
4. Advantage Normalization:
   $$\hat{A}_t \leftarrow \frac{\hat{A}_t - \bar{A}}{\sigma_A + 10^{-8}}$$
5. Composite PPO Loss:
   $$\mathcal{L}_{\text{total}}(\theta) = -L^{\text{CLIP}}(\theta) + c_1 L^{\text{VF}}(\theta) - c_2 S[\pi_\theta], \quad c_1 = 0.5, \, c_2 = 0.01$$

### 4.4 Explainable AI (XAI) & Spatial IoU Fidelity
Feature attributions are generated by `explainability.py` using PyTorch Captum:
1. Vanilla Saliency:
   $$A_{\text{Saliency}}(\mathbf{x}) = \left| \frac{\partial \mu_0(\mathbf{x}, \mathbf{v})}{\partial \mathbf{x}} \right|$$
2. Integrated Gradients ($m=30$ Riemann steps):
   $$A_i^{\text{IG}}(\mathbf{x}, \mathbf{0}) \approx x_i \times \frac{1}{m} \sum_{k=1}^m \frac{\partial F\left(\frac{k}{m}\mathbf{x}\right)}{\partial x_i}$$
3. 7-Stage Thermal Vision Pipeline:
```
2D Saliency Map (84x84) in [0, 1]              RGB Camera Frame (84x84x3)
              |                                              |
              v                                              v
[Stage 1: Bicubic Upscaling]                   [Stage 1: Bicubic Upscaling]
      Resize to (390, 390)                           Resize to (390, 390)
              |                                              |
              v                                              v
[Stage 2: Gaussian Smoothing]                  [Base Canvas Preparation]
  Kernel (13x13), sigma=3.0                       RGB -> BGR Color Format
              |                                              |
              v                                              |
[Stage 3: Post-Blur Renormalize]                             |
     Strict Range [0.0, 1.0]                                 |
              |                                              |
              v                                              |
[Stage 4: Gamma Contrast Boost]                              |
      A_boosted = (A)^0.7                                    |
              |                                              |
       +------+------+                                       |
       |             |                                       |
       v             v                                       |
[Stage 5: TURBO]  [Stage 6: Adaptive Alpha]                  |
 cv2.COLORMAP_    alpha = clip((A-0.10)/0.85, 0, 1) * 0.75   |
    TURBO         (Unsalient Background = Transparent)       |
       \             /                                       |
        \           /                                        |
         v         v                                         |
   [Alpha-Blended Canvas] <----------------------------------+
             |
             v
   [Stage 7: Neon Peak Contours]
     Mask = (A_boosted > 0.65)
     cv2.findContours(RETR_EXTERNAL)
     Glowing Cyan/Gold Rings (255, 255, 0)
             |
             v
   Final High-Definition Overlay (390x390x3)
```
4. Spatial IoU Explanation Fidelity:
   $$\text{Spatial IoU} = \frac{|\mathcal{M}_{\text{attr}} \cap \mathcal{M}_{\text{obs}}|}{|\mathcal{M}_{\text{attr}} \cup \mathcal{M}_{\text{obs}}| + 10^{-6}}$$
   Where $\mathcal{M}_{\text{attr}} = (A_{\text{2D}} \ge \text{Percentile}_{85}(A_{\text{2D}}))$ and $\mathcal{M}_{\text{obs}} = (D_{\text{ground\_truth}} < 1.5\text{ m})$.

### Table 2: Perception, Optical Flow & Camera Specifications
| Parameter Description | Variable / Parameter | Specification / Value | Operational Function |
|---|---|---|---|
| Camera Field of View | $\theta_{\text{FOV}}$ | `65.0` degrees | Monocular front-facing lens |
| Camera Resolution | $W \times H$ | `84 x 84` pixels | Native visual state tensor |
| Near / Far Clipping Planes | $z_{\text{near}}, z_{\text{far}}$ | `0.1` m, `12.0` m | Depth buffer bounds |
| Camera Mounting Offset | $\Delta \mathbf{p}_{\text{cam}}$ | `[0.0, 0.20, 0.0]` m | Displaced forward from chassis center |
| Linearized Metric Depth | $D_{\text{meters}}$ | `1.2 / (12.0 - 11.9 * buf)` | Linear metric conversion |
| Farneback Pyramid Scale | `pyr_scale` | `0.5` | 50% image reduction per octave |
| Farneback Pyramid Levels | `levels` | `2` | Resolves motion at 42x42 and 84x84 |
| Farneback Averaging Window | `winsize` | `9` pixels | Neighborhood smoothing filter |
| Farneback Iterations | `iterations` | `2` | Iterative solver updates |
| Farneback Polynomial Size | `poly_n` | `5` pixels | Neighborhood for polynomial fitting |
| Farneback Gaussian Sigma | `poly_sigma` | `1.1` | Standard deviation for coefficient blur |
| Central ROI Boundary Margin | `margin_h, margin_w`| `16` pixels (20% margin)| Masks outer 20% along each axis |
| Active ROI Resolution | $W_{\text{ROI}} \times H_{\text{ROI}}$ | `52 x 52` pixels | $38.3\%$ of total frame pixels |
| Maximum Clamped Inverse TTC | $\tau^{-1}_{\max}$ | `5.0` s$^{-1}$ | Clamps looming penalty ($\tau_{\min} = 0.2$ s) |

### Table 3: Multi-Objective Reward Function Weights
| Reward Component | Mathematical Formulation | Weight / Gain | Functional Objective |
|---|---|---|---|
| Goal Distance Progress | $6.0 \cdot (d_{t-1} - d_t)$ | `+6.0` | Dense potential shaping toward target |
| Goal Velocity Alignment| $3.0 \cdot (\mathbf{v} \cdot \hat{\mathbf{d}})$ | `+3.0` | Rewards forward cruising speed along line of sight |
| Optical Flow Looming | $-2.0 \cdot \tau^{-1}_{\text{bounded}}$ | `-2.0` | Penalizes visual expansion in central ROI |
| Attitude Tilt Stability | $-0.5 \cdot (\|\phi\| + \|\theta\|)$ | `-0.5` | Stabilizes roll and pitch flight angles |
| Depth Proximity Buffer | $-3.0 \cdot (1.5 - \text{P}_{5\%}(D))$ | `-3.0` | Soft barrier penalty when obstacles $< 1.5$ m |
| Terminal Goal Reached | $d_{\text{goal}} < 0.8$ m | `+100.0` | Sparse bonus for reaching destination |
| Terminal Crash / OOB | Contact $> 0$ or OOB | `-100.0` | Catastrophic failure penalty terminating episode |

---

# Chapter 5: Granular Module & File Breakdown

### 5.1 `environment.py` — Indoor Physics Simulation & Gymnasium Interface
- **Module Metrics**: 537 Lines of Code | Dependencies: `gymnasium`, `pybullet`, `cv2`, `numpy`.
- **Operational Responsibility**: Houses the `IndoorDroneNavEnv` class which encapsulates the physical simulation world, multi-rate 240Hz/24Hz integration, procedural obstacle generation, 3D raycasting fallback, optical flow calculation, and multi-objective reward shaping.
- **Detailed Function & Method Inventory**:
  - `__init__(self, render_mode=None, use_gui=False)`: Initializes PyBullet physics client in GUI or DIRECT mode. Defines `observation_space` as Gymnasium `Dict` with `'visual'` (`Box(0.0, 1.0, (5, 84, 84))`) and `'velocity'` (`Box(-10.0, 10.0, (3,))`). Defines continuous `action_space` as `Box(-1.0, 1.0, (4,))`. Allocates internal memory buffers for `prev_gray`, `flow`, and step counters.
  - `_set_seed(self, seed=None)`: Enforces deterministic PRNG seeding across NumPy (`np.random.seed`) and Python random states.
  - `reset(self, seed=None, options=None)`: Resets PyBullet state, restores gravity vector $[0, 0, -9.81]$ m/s$^2$, spawns the quadrotor body at $[0.0, -8.0, 1.5]$ m, invokes `_spawn_indoor_obstacles()`, resets optical flow history, and returns `(observation_dict, info)`.
  - `_spawn_indoor_obstacles(self)`: Instantiates arena walls ($10\text{m} \times 20\text{m} \times 4\text{m}$) and $6-11$ procedural obstacles (Coral cylinders and Emerald cuboids). Restricts obstacle placement outside the 3m spawn corridor ($Y \in [-8, -5]$), 3m goal corridor ($Y \in [5, 8]$), and 1.5m lateral channels.
  - `_get_camera_images(self)`: Computes camera view and projection matrices ($\theta_{\text{FOV}}=65^\circ$, $z_{\text{near}}=0.1$ m, $z_{\text{far}}=12.0$ m, mounting offset $[0, 0.20, 0]$ m). Renders $84 \times 84$ RGB and depth arrays via TinyRenderer, with linear metric depth recovery $D = 1.2 / (12.0 - 11.9 \cdot d_{\text{buffer}})$. Falls back to analytical 3D Perspective Raycasting on CPU if PyBullet rendering fails.
  - `render_overhead_simulation_view(self, out_size=(380, 380))`: Renders top-down 3D arena map with gray grid lines, concentric gold goal markers, obstacle cross-sections, and drone position with red heading vector.
  - `_compute_optical_flow_and_tau(self, rgb_img)`: Computes Gunnar Farneback dense optical flow, evaluates Sobel horizontal and vertical divergence, pools mean expansion over 60% central ROI ($16 \le x, y < 68$), and bounds inverse time-to-collision $\tau^{-1} \in [0.0, 5.0]$ s$^{-1}$.
  - `_get_observation(self)`: Assembles sensory state dictionary containing `'visual'` $(5, 84, 84)$ and `'velocity'` $(3,)$.
  - `_clamp_to_arena(self)`: Substep anti-tunneling check enforcing $|x| \le 4.6$ m, $|y| \le 9.6$ m, and $z \in [0.15, 3.5]$ m. Latching `out_of_bounds = True` and zeroing velocities upon boundary violation.
  - `step(self, action)`: Advances 8 physics substeps at 240 Hz enforcing target velocities $\mathbf{v}_{\text{target}} = \mathbf{a}[:3] \times 3.0$ m/s and $\dot{\psi} = a_3 \times 1.0$ rad/s. Evaluates collisions via `p.getContactPoints()`, calculates multi-objective reward $R_t$, and checks episode termination.
  - `close(self)`: Disconnects PyBullet physics client cleanly.

### 5.2 `model.py` — Dual-Stream NatureCNN Actor-Critic Neural Policy
- **Module Metrics**: 228 Lines of Code | Dependencies: `torch`, `numpy`.
- **Operational Responsibility**: Implements the `PhysicsInformedActorCritic` neural network architecture and pure-NumPy CPU fallback engine.
- **Detailed Class & Method Inventory**:
  - `PhysicsInformedActorCritic(nn.Module)`:
    - `__init__(self, visual_shape=(5, 84, 84), vel_dim=3, action_dim=4)`: Builds NatureCNN visual conv stack (Conv1 $5 \to 32$, Conv2 $32 \to 64$, Conv3 $64 \to 64$, Linear $3136 \to 512$), kinematic MLP (Linear $3 \to 64$), latent fusion (Linear $576 \to 256$), Actor head (Linear $256 \to 128 \to 4$, tanh), Critic head (Linear $256 \to 128 \to 1$), and trainable parameter `actor_log_std` initialized to $-0.5$.
    - `extract_features(self, vis, vel)`: Forward pass through convolutional layers, flattening, kinematic projection, concatenation, and latent fusion manifold.
    - `forward(self, vis, vel)`: Returns tuple `(actor_mu, critic_val)`.
    - `get_value(self, vis, vel)`: Evaluates Critic head to return baseline scalar state value $V(s)$.
    - `get_action_and_value(self, vis, vel, action=None)`: Constructs diagonal Gaussian policy $\mathcal{N}(\boldsymbol{\mu}, \boldsymbol{\Sigma})$, samples actions, evaluates log-probabilities, differential entropy, and returns `(action, log_prob, entropy, value)`.
  - `Pure-NumPy Fallback Engine`: Standalone CPU implementation activating if PyTorch import fails. Features stride-12 visual subsampling, random matrix forward passes, analytical Gaussian sampling, closed-form entropy, and mock PyTorch serialization interfaces (`state_dict`, `load_state_dict`, `to`, `eval`).

### 5.3 `pretrain_bc.py` — Behavioral Cloning & Tangential Potential Field Expert
- **Module Metrics**: 338 Lines of Code | Dependencies: `torch`, `gymnasium`, `numpy`.
- **Operational Responsibility**: Provides the algorithmic potential field expert planner with Tangential Obstacle Steering, demonstration dataset collection, and supervised MSE imitation learning.
- **Detailed Function Inventory**:
  - `expert_action(obs, env)`: Implements artificial potential field planner: computes forward attractive goal pull ($v_{y, \text{desired}} = \min(1.0, \max(0.4, d_{\text{goal}}/3.0))$), lateral alignment, tangential obstacle repulsion deflecting strictly along $v_x$, forward momentum locking ($v_y \ge 0.35$ m/s) eliminating collinear deadlock, 5-sector depth guidance, wall repulsion at $|x| > 3.2$ m, and proportional altitude holding ($v_z = \text{clip}(2.0(1.5-z), -0.6, 0.6)$).
  - `collect_demonstrations(env, expert_fn, target_steps=80000, n_envs=300, output_path='bc_demos.npz')`: Runs expert navigation across 300 randomized environments, accumulating 80,000 transitions into `bc_demos.npz`.
  - `train_bc(model, dataset_path, epochs=60, batch_size=256, lr=3e-4, save_path='best_model.pt')`: Supervised imitation training loop using Adam optimizer, Cosine Annealing learning rate schedule over 60 epochs, AMP FP16 acceleration, and $L_2$ gradient clipping (1.0).
  - `validate_model(model, env, n_episodes=5, seeds=[42, 142, 242])`: Multi-seed evaluation suite benchmarking pre-trained policy performance before reinforcement learning.

### 5.4 `train.py` — Multi-Worker Vectorized PPO Reinforcement Learning Engine
- **Module Metrics**: 547 Lines of Code | Dependencies: `torch`, `gymnasium`, `multiprocessing`, `tensorboard`, `numpy`.
- **Operational Responsibility**: Orchestrates vectorized multi-process simulation, GAE-$\lambda$ computation, mini-batch PPO optimization, TensorBoard streaming, and hardware acceleration.
- **Detailed Class & Function Inventory**:
  - `_env_worker(remote, parent_remote, env_fn_wrapper)`: Worker subprocess target function for `SubprocVecEnv` executing environment steps and auto-resetting upon episode termination.
  - `SubprocVecEnv`: Manages $N$ parallel worker processes ($N=8$ standard, $N=16$ overnight) via multiprocessing Pipes with non-blocking IPC.
  - `SingleEnv`: Synchronous single-process wrapper for debugging.
  - `RolloutBuffer`: Pre-pinned GPU memory buffer storing $T=512$ steps across $N$ workers (4,096 to 8,192 transitions) including visual observations, velocities, actions, rewards, dones, values, and log-probs.
  - `compute_gae(rewards, values, dones, next_value, gamma=0.99, lambda=0.95)`: Vectorized Bellman residual trace computing Generalized Advantage Estimation $\hat{A}_t^{\text{GAE}}$ and advantage normalization.
  - `train_ppo(...)`: PPO optimization engine running 10 epochs per rollout, mini-batch sampling (size 512 to 2048), clipped surrogate objective ($\epsilon=0.2$), value loss ($c_1=0.5$), entropy regularization ($c_2=0.01$), and TensorBoard scalar logging.
  - Hardware Acceleration: Configures NVIDIA Blackwell `sm_120`, TensorFloat-32 (`allow_tf32=True`), cuDNN benchmark autotuning, AMP FP16 `GradScaler`, and `torch.compile(mode="reduce-overhead")` with safe checkpoint unwrapping (`_orig_mod`).

### 5.5 `explainability.py` — Real-Time Captum XAI Engine & Spatial IoU Fidelity
- **Module Metrics**: 188 Lines of Code | Dependencies: `captum`, `torch`, `cv2`, `numpy`.
- **Operational Responsibility**: Implements real-time model interpretability, feature attribution, high-definition thermal vision synthesis, and quantitative explanation fidelity evaluation.
- **Detailed Class & Method Inventory**:
  - `DroneXAIEngine / CaptumExplainabilityEngine`:
    - `__init__(self, model, method="saliency")`: Wraps `PhysicsInformedActorCritic` with dual-input autograd wrapper. Initializes Captum `Saliency` or `IntegratedGradients`.
    - `compute_attribution(self, vis_tensor, vel_tensor)`: Backpropagates autograd gradients to isolate visual attribution, max-pooling across 5 channels: $A_{\text{2D}}(u, v) = \max_{c \in [0..4]} |A(c, u, v)|$.
    - `generate_heatmap_overlay(self, rgb_img, attribution_map, ...)`: 7-stage thermal vision pipeline: (1) Bicubic upscaling to $390 \times 390$, (2) $13 \times 13$ Gaussian blur ($\sigma=3.0$), (3) $[0, 1]$ re-normalization, (4) Gamma 0.7 power-law contrast boost, (5) Google TURBO colormap synthesis, (6) Dynamic alpha blending ($\alpha \le 0.75$), (7) Neon peak contour extraction ($A > 0.65$).
    - `compute_explanation_fidelity(self, attribution_map, depth_map, ...)`: Computes Spatial IoU metric between top-15% saliency mask and ground-truth depth obstacles ($D < 1.5$ m).

### 5.6 `evaluate_and_visualize.py` — 3-Panel HD Dashboard & Telemetry Visualizer
- **Module Metrics**: 367 Lines of Code | Dependencies: `cv2`, `torch`, `gymnasium`, `numpy`.
- **Operational Responsibility**: Composes the unified 3-panel high-definition telemetry dashboard ($1230 \times 510$ px) and benchmarks trained policies across unseen procedural layouts.
- **Detailed Function Inventory**:
  - `draw_optical_flow_vectors(rgb_img, flow, target_size=(390, 390), step=16)`: Upscales flow fields to $390 \times 390$, suppresses sub-pixel noise ($\text{mag} \le 1.2$ px), and renders directional motion vectors color-coded by magnitude: Cyan (1.2-4 px), Lime Green (4-10 px), and Gold ($\ge 10$ px looming).
  - `create_unified_dashboard_canvas(topdown_img, fpv_img, xai_img, ...)`: Assembles $1230 \times 510$ px canvas with Deep Charcoal header bar, telemetry badge (Step & Goal Distance), 3 display panels (3D Arena Map, Flow Vision, TURBO Heatmap), and optional training HUD strip.
  - `evaluate_policy(policy, env, n_episodes=5, seeds=[101, 202, 303, 404, 505], render=True)`: Multi-seed benchmarking suite logging success rates, collision frequencies, episodic returns, and Spatial IoU explanation fidelity.

### 5.7 `run_project.bat` — Central Interactive Menu Dispatcher
- **Module Metrics**: 58 Lines of Script | Platform: Windows Command Prompt (`cmd.exe`).
- **Operational Responsibility**: Centralized lifecycle automation script configuring environment locks (`CUDA_VISIBLE_DEVICES=0`, `PYBULLET_EGL=1`), console styling (`COLOR 0A`), and interactive menu dispatching:
  - `[0]`: Expert Potential Field Pretraining (`pretrain_bc.py`)
  - `[1]`: PPO Policy Fine-Tuning (`train.py`)
  - `[2]`: Comprehensive Evaluation & HD Dashboard (`evaluate_and_visualize.py`)
  - `[3]`: Background TensorBoard Monitoring (`localhost:6006`)
  - `[4]`: Quick Headless Test
  - `[5]`: Overnight 4-Hour Training Automation (`overnight_train.bat`)
  - `[6]`: Clean Exit

### 5.8 `overnight_train.bat` — Unattended Long-Run Automation & Safe Shutdown
- **Module Metrics**: 65 Lines of Script | Platform: Windows Command Prompt & `shutdown.exe`.
- **Operational Responsibility**: Automates 4-hour 4,000,000-step training runs. Features pre-flight verification of `best_model.pt` (auto-runs BC pretraining if absent), launches background TensorBoard minimized, opens web browser, executes 16-worker PPO training, triggers 60-second automated shutdown (`shutdown /s /f /t 60`), and provides an interactive pause abort trap (`shutdown /a`).

### 5.9 `requirements.txt` — Dependency Manifest & Version Pinning
- **Module Metrics**: 8 Dependencies | Package Manager: `pip`.
- **Operational Responsibility**: Defines exact minimum version constraints for runtime reproducibility:
  - `gymnasium>=0.29.0`: Core reinforcement learning simulation interface.
  - `pybullet>=3.2.5`: Rigid-body multi-body physics and collision detection.
  - `torch>=2.0.0`: Deep learning autograd, AMP FP16, and Inductor compilation.
  - `captum>=0.6.0`: Model interpretability and gradient attribution.
  - `opencv-python>=4.8.0`: Computer vision, optical flow, and GUI dashboard.
  - `numpy>=1.24.0`: Tensor manipulation and fallback linear algebra.
  - `tensorboard>=2.14.0`: Experiment logging and telemetry tracking.
  - `matplotlib>=3.7.0`: Visualization colormaps and offline diagnostics.
  - `python-docx>=1.0.0`: OpenXML document generation.

### 5.10 `README.md` — Architectural Documentation & Discrepancy Reconciliation
- **Module Metrics**: 278 Lines of Markdown.
- **Operational Responsibility**: Master research documentation and user handbook detailing mathematical formulations, installation commands, quick-start workflows, and hardware benchmarks.
- **Discrepancy Reconciliation**: Reconciles conceptual README formulas with production `environment.py` implementations:
  - Addition of $6.0 \times R_{\text{progress}}$ potential shaping.
  - Scaling of $R_{\text{goal}}$ to $3.0 \times$.
  - Scaling of $R_{\text{TTC}}$ looming penalty to $-2.0 \times$.
  - Transition from strict minimum depth $d_{\min}$ to robust 5th-percentile depth proximity $P_{5\%}(D)$.

### Table 6: Complete 10-File Codebase Inventory
| # | File Name | LOC | Primary Classes / Functions | Core Dependencies | Subsystem Responsibility |
|---|---|---|---|---|---|
| 1 | `environment.py` | 537 | `IndoorDroneNavEnv` | `gymnasium`, `pybullet`, `cv2`, `numpy` | Simulation physics, 240Hz/24Hz timing, Farneback flow, reward shaping |
| 2 | `model.py` | 228 | `PhysicsInformedActorCritic` | `torch`, `numpy` | NatureCNN visual + kinematic MLP dual-branch policy, CPU fallback |
| 3 | `pretrain_bc.py` | 338 | `expert_action`, `train_bc` | `torch`, `gymnasium`, `numpy` | Potential field expert with tangential steering, supervised imitation |
| 4 | `train.py` | 547 | `SubprocVecEnv`, `train_ppo`| `torch`, `gymnasium`, `multiprocessing` | Vectorized PPO engine, GAE-$\lambda$, AMP FP16, `torch.compile` |
| 5 | `explainability.py` | 188 | `DroneXAIEngine` | `captum`, `cv2`, `torch`, `numpy` | Captum Saliency/IG, TURBO thermal synthesis, Spatial IoU fidelity |
| 6 | `evaluate_and_visualize.py` | 367 | `evaluate_policy`, HUD | `cv2`, `torch`, `gymnasium`, `numpy` | Unified 3-Panel HD Dashboard ($1230 \times 510$), multi-seed evaluation |
| 7 | `run_project.bat` | 58 | Windows Command Script | Windows Shell (`cmd.exe`) | Central interactive 6-option menu dispatcher, CUDA device locking |
| 8 | `overnight_train.bat` | 65 | Windows Command Script | Windows Shell, `shutdown.exe` | 4-hour 4M-step automation, pre-flight BC check, auto-shutdown trap |
| 9 | `requirements.txt` | 8 | Dependency Manifest | `pip` package manager | Exact minimum version bounds for 8 core runtime libraries |
| 10 | `README.md` | 278 | Markdown Documentation | GitHub / Markdown renderers | Master research overview, quick-start guide, performance benchmarks |

---

# Chapter 6: Setup, Configuration & Execution

### 6.1 Hardware & Software Prerequisites
- **Operating Systems**: Windows 10/11 x64 (PowerShell or CMD) or Ubuntu Linux 20.04/22.04 LTS.
- **Python Runtime**: Python 3.10, 3.11, or 3.12 (64-bit).
- **GPU Compute**: NVIDIA RTX 30-series, 40-series, or 50-series Blackwell `sm_120` with CUDA 12.0+.
- **Display Drivers**: NVIDIA display drivers supporting OpenGL 4.5+ or headless EGL rendering.

### 6.2 Virtual Environment Setup & Installation
```bash
# 1. Create and activate virtual environment
python -m venv venv
venv\Scripts\activate   # On Windows
# source venv/bin/activate # On Linux

# 2. Install PyTorch with CUDA support (cu128 for Blackwell sm_120)
pip install torch torchvision --index-url https://download.pytorch.org/whl/cu128

# 3. Install core dependencies
pip install -r requirements.txt
pip install python-docx
```

### 6.3 Automated Batch Execution Workflows
- **Interactive Menu (`run_project.bat`)**:
  - Run `run_project.bat` from Windows terminal.
  - Option `[0]`: Runs `pretrain_bc.py` collecting 80,000 demonstration steps and training `best_model.pt`.
  - Option `[1]`: Runs `train.py` fine-tuning the actor-critic policy via vectorized PPO.
  - Option `[2]`: Runs `evaluate_and_visualize.py` displaying the real-time 3-Panel HD Telemetry Dashboard.
  - Option `[3]`: Launches background TensorBoard server at `http://localhost:6006`.
  - Option `[4]`: Executes quick headless test.
  - Option `[5]`: Launches `overnight_train.bat` for 4M-step training with automated shutdown.
- **Unattended Long-Run Automation (`overnight_train.bat`)**:
  - Executes pre-flight verification of `best_model.pt`.
  - Launches minimized TensorBoard server.
  - Starts 16-worker PPO training for 4,000,000 timesteps.
  - Initiates 60-second automated system shutdown upon completion (`shutdown /s /f /t 60`), with interactive abort trap (`shutdown /a`).

### 6.4 Command-Line Interface (CLI) Arguments Reference
| Script | CLI Argument | Type | Default Value | Functional Description |
|---|---|---|---|---|
| `pretrain_bc.py` | `--target-demo-steps` | `int` | `80000` | Total expert transitions collected for demonstration dataset |
| `pretrain_bc.py` | `--n-demo-envs` | `int` | `300` | Number of randomized procedural obstacle environments |
| `pretrain_bc.py` | `--bc-epochs` | `int` | `60` | Supervised Behavioral Cloning training epochs |
| `pretrain_bc.py` | `--batch-size` | `int` | `256` | Mini-batch size for Adam optimization |
| `pretrain_bc.py` | `--lr` | `float` | `3e-4` | Base learning rate with Cosine Annealing decay |
| `pretrain_bc.py` | `--output` | `str` | `"bc_demos.npz"` | Filepath for saving collected demonstration dataset |
| `pretrain_bc.py` | `--save-model` | `str` | `"best_model.pt"` | Filepath for saving pre-trained model weights |
| `train.py` | `--total-timesteps` | `int` | `100000` | Total environment interaction steps across all workers |
| `train.py` | `--n-envs` | `int` | `8` | Parallel worker processes spawned in `SubprocVecEnv` |
| `train.py` | `--n-steps` | `int` | `512` | Rollout horizon per worker before PPO update (4096 total) |
| `train.py` | `--batch-size` | `int` | `512` | PPO SGD mini-batch size (8 batches per epoch) |
| `train.py` | `--update-epochs` | `int` | `10` | PPO gradient optimization epochs per rollout buffer |
| `train.py` | `--gamma` | `float` | `0.99` | Long-term reward discount factor |
| `train.py` | `--gae-lambda` | `float` | `0.95` | Generalized Advantage Estimation bias-variance coefficient |
| `train.py` | `--clip-eps` | `float` | `0.2` | PPO surrogate policy ratio clipping threshold |
| `train.py` | `--vf-coef` | `float` | `0.5` | Critic value function loss scalar coefficient |
| `train.py` | `--ent-coef` | `float` | `0.01` | Policy entropy regularization bonus coefficient |
| `train.py` | `--learning-rate` | `float` | `3e-4` | Adam optimizer learning rate |
| `train.py` | `--pretrained-model` | `str` | `"best_model.pt"` | Path to pre-trained Behavioral Cloning checkpoint |
| `evaluate_and_visualize.py` | `--model-path` | `str` | `"best_model.pt"` | Actor-critic checkpoint path for evaluation |
| `evaluate_and_visualize.py` | `--episodes` | `int` | `5` | Number of evaluation episodes per run |
| `evaluate_and_visualize.py` | `--unseen-layouts` | `flag` | `False` | Evaluates on unseen procedural obstacle seeds |
| `evaluate_and_visualize.py` | `--no-gui` | `flag` | `False` | Executes headless benchmarking without OpenCV GUI |

### 6.5 Real-Time Telemetry & TensorBoard Monitoring
Diagnostic training telemetry is logged in real-time to the `runs/` directory and visualized via TensorBoard:
```bash
tensorboard --logdir runs --port 6006
```
Open `http://localhost:6006` in any web browser. Monitored scalar metrics:
- `charts/episodic_return`: Cumulative episode reward indicating navigation efficiency.
- `charts/episodic_length`: Flight steps survived per episode.
- `losses/policy_loss`: PPO clipped surrogate objective loss.
- `losses/value_loss`: Critic mean squared error value prediction loss.
- `losses/entropy`: Differential policy exploration entropy.
- `charts/SPS`: Simulation environment interactions per second throughput.

---
*End of Technical Documentation Treatise.*
