# Master Blueprint for `TECHNICAL_DOCUMENTATION.md`
**Document Title**: Autonomous Drone Navigation through Random Obstacles in a Simulated Environment: Architecture, Simulation Dynamics, Deep Reinforcement Learning, and Explainability  
**Target Document**: `c:\Users\Rushikesh\Desktop\Cool Ass Projects\Drone\TECHNICAL_DOCUMENTATION.md`  
**Architectural Blueprint Author**: `explorer_m1_1`  
**Date**: September 19, 2026  
**Status**: Authoritative Blueprint & Implementation Guide  

---

## 1. Blueprint Overview & Word Count Architecture

This document establishes the comprehensive structural, algorithmic, mathematical, and diagrammatic blueprint for authoring the companion technical documentation `TECHNICAL_DOCUMENTATION.md` in the workspace root.

### 1.1 Volume & Word Count Targets
To guarantee publication-grade depth and ensure the document decisively exceeds the **6,000-word threshold on its own** (as mandated by `ORIGINAL_REQUEST.md` and `verify_documentation.py`), the content budget is allocated across the 6 mandatory chapters as follows:

| Section # | Mandatory Chapter Title | Planned Word Budget | Primary Elements Included |
|---|---|---|---|
| **Chapter 1** | **Executive Summary** | ~650 words | Research background, indoor GPS-denied challenges, technical objectives, system scope, paradigm synthesis (BC + PPO + XAI). |
| **Chapter 2** | **System Architecture** | ~1,100 words | End-to-end data flow, 3 ASCII block diagrams (dataflow, execution lifecycle, threading/IPC), sync/async timings, state/action spaces. |
| **Chapter 3** | **Simulation Environment Mechanics** | ~1,650 words | 240Hz/24Hz timing, 8 substeps, clamping proof, procedural generation, camera projection math, Farneback optical flow, $\tau^{-1}$ looming, reward shaping. |
| **Chapter 4** | **Drone Navigation & Algorithmic Foundations** | ~1,950 words | NatureCNN + MLP dual-branch math, potential field tangential steering, GAE-$\lambda$, PPO clipped objective, Captum XAI, Spatial IoU fidelity. |
| **Chapter 5** | **Granular Module & File Breakdown** | ~2,400 words | All 10 project files audited line-by-line: classes, methods, signatures, interfaces, error handling, AppLocker fallback. |
| **Chapter 6** | **Setup, Configuration & Execution** | ~950 words | Prerequisites, Python 3.10+, NVIDIA Blackwell `sm_120`, batch automation, CLI tables, TensorBoard diagnostics, shutdown safety traps. |
| **TOTALS** | **Complete Technical Document** | **~8,700 words** | **6 Chapters, 10 Files, 7 ASCII Diagrams, 15 LaTeX Math Formulations, 9 Tables** |

---

## 2. Chapter-by-Chapter Structural Specification

### Chapter 1: Executive Summary
- **1.1 Research Context & Motivation**:
  - Unstructured, GPS-denied indoor aerial navigation.
  - Challenges: absence of global positioning signals, severe multi-path acoustic/RF reflections, dynamic obstacle occlusion, low payload capacity requiring lightweight monocular cameras rather than heavy LiDAR sensors.
  - Failure modes of naive reinforcement learning: uniform collision loops, credit assignment collapse in sparse-reward regimes, sim-to-real transfer gaps.
- **1.2 High-Level Project Objectives**:
  - Autonomous collision-free navigation through procedural 3D obstacle fields.
  - Sub-second closed-loop reactive control at 24 Hz Gymnasium step frequency.
  - Physics-informed reward shaping and bounded inverse time-to-collision ($\tau^{-1}$) derived from dense optical flow.
  - Bootstrapping policy optimization via algorithmic Potential Field Behavioral Cloning.
  - White-box interpretability via real-time attribution heatmaps and quantitative Spatial IoU explanation fidelity.
- **1.3 Architectural Scope & System Taxonomy**:
  - Decoupled 240 Hz rigid-body simulation in PyBullet vs. 24 Hz Gymnasium agent control.
  - Dual-input neural network: 5-channel visual tensor ($84 \times 84 \times 5$) and 3D velocity vector ($3,$).
  - Multi-process vectorized training (`SubprocVecEnv`) with TensorFloat-32, AMP FP16, and PyTorch Inductor kernel compilation (`torch.compile`).
  - Unified 3-Panel HD Telemetry Dashboard ($1230 \times 510$ px) integrating overhead tracking, first-person optical flow vectors, and Google TURBO thermal attributions.

---

### Chapter 2: System Architecture & End-to-End Data Flow
- **2.1 High-Level Component Topology**:
  - Perception & Simulation Engine (`environment.py`).
  - Representation & Neural Control Policy (`model.py`).
  - Expert Imitation Learning Planner (`pretrain_bc.py`).
  - Distributed Proximal Policy Optimization Engine (`train.py`).
  - Explainable AI Attribution Engine (`explainability.py`).
  - Visualization, Multi-Seed Evaluation & Telemetry Dashboard (`evaluate_and_visualize.py`).
  - Windows Batch Lifecycle Automation (`run_project.bat`, `overnight_train.bat`).
- **2.2 End-to-End System Block Diagram**:
  - Complete ASCII schematic tracing tensors from camera projection to motor commands.
- **2.3 State Space & Observation Representation**:
  - Visual Observation Tensor: $\mathbf{o}_{\text{vis}} \in \mathbb{R}^{5 \times 84 \times 84}$ (Channels 0–2: Normalized RGB $[0, 1]$; Channels 3–4: Farneback horizontal and vertical optical flow $u, v$).
  - Kinematic Odometry Tensor: $\mathbf{o}_{\text{vel}} \in \mathbb{R}^3$ ($(v_x, v_y, v_z)$ linear velocities in m/s).
- **2.4 Continuous Action Space & Kinematics Mapping**:
  - Continuous 4D action vector $\mathbf{a} \in [-1.0, 1.0]^4$.
  - Scaling to physical velocity commands: $\mathbf{v}_{\text{target}} = [a_x, a_y, a_z]^T \times 3.0$ m/s, $\dot{\psi} = a_\psi \times 1.0$ rad/s.
- **2.5 Training vs. Inference Execution Paths**:
  - Vectorized multiprocessing via `SubprocVecEnv` across $N$ workers with Windows `spawn` IPC and non-blocking auto-resets.
  - Synchronous inference path for real-time evaluation with live OpenCV dashboard.

---

### Chapter 3: Simulation Environment Mechanics & Perception Pipeline
- **3.1 Multi-Rate Physics/Control Coupling**:
  - PyBullet internal physics clock: $f_{\text{physics}} = 240.0$ Hz ($\Delta t = 4.167$ ms).
  - Gymnasium agent control step: $f_{\text{control}} = 24.0$ Hz ($\Delta T = 41.667$ ms).
  - Exact substep ratio: $N_{\text{substeps}} = 240 / 24 = 8$ substeps per control step.
  - Substep integration loop and velocity persistence.
- **3.2 Coordinate Frames & Arena Geometry**:
  - Right-handed Cartesian world frame centered at arena floor $(0, 0, 0)$.
  - Arena bounds: $X \in [-5.0, 5.0]$ m, $Y \in [-10.0, 10.0]$ m, $Z \in [0.0, 4.0]$ m.
  - Start position: $\mathbf{p}_{\text{start}} = [0.0, -8.0, 1.5]^T$ m; Goal position: $\mathbf{p}_{\text{goal}} = [0.0, 8.0, 1.5]^T$ m (16 m traversal distance).
- **3.3 Anti-Tunneling Sub-Step Boundary Clamping**:
  - Boundary limits: `ARENA_X_LIM = 4.6`, `ARENA_Y_LIM = 9.6`, `ARENA_Z_MIN = 0.15`, `ARENA_Z_MAX = 3.5`.
  - Sub-step clamping algorithm: evaluating position every 4.167 ms, projecting violating coordinates, nullifying linear/angular velocity, latching `out_of_bounds = True`, and enforcing immediate episode termination with $-100.0$ penalty.
- **3.4 Procedural Obstacle Generation & Clearance Corridors**:
  - Dynamic count: $N_{\text{obs}} \sim \mathcal{U}_{\text{discrete}}\{6, \dots, 11\}$.
  - Obstacle primitives: Vertical cylinders ($r \in [0.35, 0.65]$ m, $h \in [2.5, 4.0]$ m, Coral RGB) and floating cuboids ($e_x, e_y, e_z \in [0.35, 0.65]$ m, $z \in [1.0, 2.5]$ m, Emerald RGB).
  - Structured clearance buffers: 3.0 m initial spawn corridor ($Y \in [-8.0, -5.0]$), 3.0 m terminal goal corridor ($Y \in [5.0, 8.0]$), and 1.5 m lateral flank channels ($X \in [3.5, 5.0]$ and $[-5.0, -3.5]$).
- **3.5 Dual-Engine Camera Rendering Pipeline**:
  - Front-mounted camera: offset $\Delta \mathbf{p}_{\text{cam}} = [0.0, 0.20, 0.0]^T$ m, resolution $84 \times 84$, $\theta_{\text{FOV}} = 65^\circ$, $z_{\text{near}} = 0.1$ m, $z_{\text{far}} = 12.0$ m.
  - Primary path: PyBullet Hardware/TinyRenderer (`p.computeViewMatrix`, `p.computeProjectionMatrixFOV`).
  - Analytical Linear Depth Recovery: Derivation converting non-linear OpenGL $z$-buffer $d_{\text{buffer}} \in [0, 1]$ to metric distance $D_{\text{meters}} = \frac{1.2}{12.0 - 11.9 \cdot d_{\text{buffer}}}$.
  - Analytical CPU 3D Raycasting Fallback: Pin-hole ray generation, yaw rotation matrix, ray-plane floor intersection with checkerboard texturing, ray-cylinder quadratic discriminant intersection, and cuboid bounding-sphere intersection with ambient distance attenuation.
- **3.6 Gunnar Farneback Dense Optical Flow & Divergence Formulation**:
  - Continuous quadratic polynomial surface approximation $f_1(\mathbf{x})$ and $f_2(\mathbf{x})$.
  - Parameter derivation: $\mathbf{A}_i, \mathbf{b}_i, c_i$, Gaussian weighting window $w(\Delta \mathbf{x})$.
  - Concrete hyperparameters: `pyr_scale=0.5`, `levels=2`, `winsize=9`, `iterations=2`, `poly_n=5`, `poly_sigma=1.1`.
  - Sobel convolution kernels $\mathbf{K}_x, \mathbf{K}_y$ estimating $\frac{\partial u}{\partial x}$ and $\frac{\partial v}{\partial y}$.
  - 60% Central ROI masking ($16 \le x, y < 68$) isolating looming expansion from lateral wall shear.
  - Bounded inverse time-to-collision formulation: $\tau^{-1}_{\text{bounded}} = \min(\max(0, \bar{E}_{\text{ROI}}), 5.0)$ s$^{-1}$.
- **3.7 Multi-Objective Physics-Informed Reward Shaping**:
  - Composite formulation: $R_t = R_{\text{progress}} + R_{\text{goal}} + R_{\text{TTC}} + R_{\text{attitude}} + R_{\text{proximity}} + R_{\text{terminal}}$.
  - Detailed breakdown of all 6 terms.
  - Reconciliation table contrasting conceptual `README.md` formulas with optimized `environment.py` values ($R_{\text{progress}} = 6.0 \Delta d$, 5th-percentile depth $\text{P}_{5\%}(D)$).

---

### Chapter 4: Drone Navigation & Algorithmic Foundations
- **4.1 Dual-Branch Actor-Critic Neural Architecture (`model.py`)**:
  - Complete topology diagram: Visual Branch + Kinematic Branch + Fusion MLP + Actor & Critic Heads.
  - NatureCNN 3-conv layer dimension trace: $(5, 84, 84) \to (32, 20, 20) \to (64, 9, 9) \to (64, 7, 7) \to 3136 \to 512$.
  - Kinematic MLP: $(3,) \to 64$.
  - Latent fusion: Concatenation $(576,) \to \text{Linear}(576, 256) \to \text{ReLU} \to (256,)$.
  - Actor Head: $\text{Linear}(256, 128) \to \text{ReLU} \to \text{Linear}(128, 4) \to \tanh \to \boldsymbol{\mu} \in [-1, 1]^4$.
  - Trainable state-independent log standard deviation vector $\text{actor\_log\_std} \in \mathbb{R}^4$ (init $-0.5$, $\sigma = 0.6065$).
  - Critic Head: $\text{Linear}(256, 128) \to \text{ReLU} \to \text{Linear}(128, 1) \to V(s) \in \mathbb{R}$.
  - Pure-NumPy CPU Fallback Engine: Stride-12 visual subsampling, padding to 3136, closed-form Gaussian log-prob and analytical entropy, mock PyTorch interface methods.
- **4.2 Behavioral Cloning & Potential Field Expert Planner (`pretrain_bc.py`)**:
  - Resolution of RL exploration bottleneck (preventing $>98\%$ random crash loops).
  - Mathematical formulation of expert potential field forces:
    1. Attractive goal force: $v_{y, \text{desired}} = \min(1.0, \max(0.4, d_{\text{goal}}/3.0))$, $v_{x, \text{desired}} = 0.8 \hat{\mathbf{u}}_{\text{goal}, x}$.
    2. Tangential Obstacle Steering: Repulsive deflection strictly along $v_x$, continuous forward momentum with $v_y \ge 0.35$ eliminating collinear deadlock.
    3. 5-Sector Monocular Depth Guidance: Horizontal slicing into 5 sectors, 5th-percentile depth detection, reactive lateral steering away from closest obstacle.
    4. Lateral Wall Clamping: Linear repulsive ramp activating at $|x| > 3.2$ m ($v_{x, \text{wall}} = \pm 2.5 (|x| - 3.2)$).
    5. Proportional Altitude Hold: $v_z = \text{clip}(2.0 (1.5 - z), -0.6, 0.6)$.
  - Demonstration collection: 80,000 transitions across 300 environments saved to `bc_demos.npz`.
  - Supervised MSE training loop: Adam optimizer ($\eta = 3 \times 10^{-4}$), Cosine Annealing over 60 epochs, AMP FP16, $L_2$ gradient clipping ($1.0$).
- **4.3 Proximal Policy Optimization Engine (`train.py`)**:
  - Probability ratio: $r_t(\theta) = \frac{\pi_\theta(\mathbf{a}_t \mid s_t)}{\pi_{\theta_{\text{old}}}(\mathbf{a}_t \mid s_t)}$.
  - Clipped surrogate objective: $L^{\text{CLIP}}(\theta) = \hat{\mathbb{E}}_t [\min(r_t \hat{A}_t, \text{clip}(r_t, 1-\epsilon, 1+\epsilon) \hat{A}_t)]$.
  - Generalized Advantage Estimation (GAE-$\lambda$):
    $\delta_t^V = r_t + \gamma V(s_{t+1})(1-d_t) - V(s_t)$, $\hat{A}_t^{\text{GAE}} = \delta_t^V + (\gamma \lambda)(1-d_t) \hat{A}_{t+1}^{\text{GAE}}$.
  - Advantage normalization across rollout batch: $\hat{A}_t \leftarrow \frac{\hat{A}_t - \bar{A}}{\sigma_A + 10^{-8}}$.
  - Composite loss function: $\mathcal{L}_{\text{total}} = L^{\text{CLIP}} + c_1 L^{\text{VF}} - c_2 S[\pi_\theta]$, where $c_1 = 0.5, c_2 = 0.01$.
  - Hardware acceleration pipeline: NVIDIA Blackwell `sm_120`, TensorFloat-32 (`allow_tf32=True`), cuDNN benchmarking, AMP FP16 `GradScaler`, and `torch.compile(mode="reduce-overhead")`.
- **4.4 Explainable AI (XAI) Attribution Engine (`explainability.py`)**:
  - Dual-input attribution handling: passing tuple `(vis_tensor, vel_tensor)` into Captum.
  - Live Vanilla Saliency vs. Offline Integrated Gradients ($m=30$ Riemann steps).
  - Channel max-pooling: $A_{\text{2D}}(u, v) = \max_{c \in [0..4]} |A(c, u, v)|$.
  - 7-Stage High-Definition Thermal Vision Pipeline:
    1. Bicubic upscaling from $84 \times 84$ to $390 \times 390$.
    2. $13 \times 13$ Gaussian smoothing ($\sigma = 3.0$).
    3. Post-smoothing re-normalization to $[0, 1]$.
    4. Non-linear power-law contrast boost: $A_{\text{boosted}} = (A_{\text{smooth}})^{0.7}$.
    5. Google TURBO colormap synthesis (`cv2.COLORMAP_TURBO`).
    6. Adaptive alpha blending: $\alpha(u, v) = \text{clip}(\frac{A - 0.10}{0.85}, 0, 1) \times \alpha_{\max}$.
    7. Neon peak-saliency contour extraction ($A > 0.65$) via Suzuki-Abe border following.
  - Spatial IoU Explanation Fidelity metric: $\text{Spatial IoU} = \frac{|\mathcal{M}_{\text{attr}} \cap \mathcal{M}_{\text{obs}}|}{|\mathcal{M}_{\text{attr}} \cup \mathcal{M}_{\text{obs}}| + 10^{-6}}$.

---

### Chapter 5: Granular Module & File-by-File Breakdown
Exhaustive, function-by-function analysis of all 10 project files:
1. `environment.py` (537 lines):
   - `IndoorDroneNavEnv`: `__init__`, `_set_seed`, `reset`, `_spawn_indoor_obstacles`, `_get_camera_images`, `render_overhead_simulation_view`, `_compute_optical_flow_and_tau`, `_get_observation`, `_clamp_to_arena`, `step`, `close`.
2. `model.py` (228 lines):
   - `PhysicsInformedActorCritic` (PyTorch): `__init__`, `extract_features`, `forward`, `get_value`, `get_action_and_value`.
   - `PhysicsInformedActorCritic` (NumPy Fallback): random weight generation, subsampling, analytical Gaussian logic.
3. `pretrain_bc.py` (338 lines):
   - Standalone functions: `expert_action`, `collect_demonstrations`, `train_bc`, `validate_model`, `main`.
4. `train.py` (547 lines):
   - `_env_worker`, `SubprocVecEnv` (`__init__`, `step`, `reset`, `close`), `SingleEnv`, `RolloutBuffer` (`add`, `get_tensors`), `compute_gae`, `train_ppo`, `get_device`, `main`.
5. `explainability.py` (188 lines):
   - `DroneXAIEngine`: `__init__`, `compute_attribution`, `generate_heatmap_overlay`, `compute_explanation_fidelity`.
6. `evaluate_and_visualize.py` (367 lines):
   - `draw_optical_flow_vectors`, `create_unified_dashboard_canvas`, `evaluate_policy`, `main`.
7. `run_project.bat` (58 lines):
   - Environment locking (`CUDA_VISIBLE_DEVICES=0`, `PYBULLET_EGL=1`), interactive 6-option menu dispatcher, error trap.
8. `overnight_train.bat` (65 lines):
   - 4-hour 4M-step automation, pre-flight `best_model.pt` presence verification, background TensorBoard spawning, 16 parallel workers, Windows automated shutdown sequence with keyboard cancellation trap (`shutdown /a`).
9. `requirements.txt` (8 dependencies):
   - Granular package manifest: `gymnasium`, `pybullet`, `torch`, `captum`, `opencv-python`, `numpy`, `tensorboard`, `matplotlib`. Subsystem mapping and version compatibility.
10. `README.md` (278 lines):
    - Project overview, mathematical descriptions, quick start guide, benchmark performance curves, reconciliation with codebase.

---

### Chapter 6: Setup, Configuration & Execution
- **6.1 Hardware & Software Prerequisites**:
  - Supported OS: Windows 10/11 x64, Ubuntu Linux 20.04/22.04 LTS.
  - Python version: Python 3.10, 3.11, or 3.12.
  - GPU Requirements: NVIDIA GPU with CUDA 12.0+ (RTX 30-series, 40-series, 50-series Blackwell `sm_120`).
  - Headless display requirements: EGL driver or PyBullet TinyRenderer / CPU Raycaster.
- **6.2 Virtual Environment & Dependency Installation**:
  - Virtualenv creation and activation (`venv`).
  - PyTorch CUDA installation commands (including Nightly wheel `cu128` for Blackwell).
  - Core dependency installation from `requirements.txt`.
  - Installation of `python-docx` for document compilation.
- **6.3 Automated Batch Execution Workflows**:
  - Step-by-step walkthrough of `run_project.bat` menu options `[0]` through `[6]`.
  - Detailed operational instructions for `overnight_train.bat`.
- **6.4 Command-Line Interface (CLI) Arguments Reference**:
  - Comprehensive reference table documenting CLI flags across `pretrain_bc.py`, `train.py`, and `evaluate_and_visualize.py`.
- **6.5 Real-Time Telemetry & TensorBoard Monitoring**:
  - Spawning TensorBoard server on port 6006 (`http://localhost:6006`).
  - Key scalar metrics tracked: `charts/episodic_return`, `charts/episodic_length`, `losses/policy_loss`, `losses/value_loss`, `losses/entropy`, `charts/SPS`.

---

## 3. Complete LaTeX Mathematical Formulations

The authoring agent in M2 must embed these exact LaTeX mathematical equations across Chapters 2, 3, 4, and 5:

### 3.1 Gunnar Farneback Optical Flow Quadratic Expansion
Local quadratic polynomial model of image intensity across consecutive frames:
$$f_1(\mathbf{x}) = \mathbf{x}^T \mathbf{A}_1 \mathbf{x} + \mathbf{b}_1^T \mathbf{x} + c_1$$
$$f_2(\mathbf{x}) = \mathbf{x}^T \mathbf{A}_2 \mathbf{x} + \mathbf{b}_2^T \mathbf{x} + c_2$$

Assuming local displacement $\mathbf{d} = [u, v]^T$ such that $f_2(\mathbf{x}) = f_1(\mathbf{x} - \mathbf{d})$:
$$\mathbf{A}_2 = \mathbf{A}_1$$
$$\mathbf{b}_2 = \mathbf{b}_1 - 2 \mathbf{A}_1 \mathbf{d}$$
$$\mathbf{d} = -\frac{1}{2} \mathbf{A}_1^{-1} (\mathbf{b}_2 - \mathbf{b}_1)$$

Weighted Gaussian solution over neighborhood window $w(\Delta \mathbf{x})$:
$$\mathbf{d}(\mathbf{x}) = \left( \sum w \mathbf{A}^T \mathbf{A} \right)^{-1} \sum w \mathbf{A}^T \Delta \mathbf{b}$$
Where $\mathbf{A}(\mathbf{x}) = \frac{\mathbf{A}_1(\mathbf{x}) + \mathbf{A}_2(\mathbf{x})}{2}$ and $\Delta \mathbf{b}(\mathbf{x}) = -\frac{1}{2} (\mathbf{b}_2(\mathbf{x}) - \mathbf{b}_1(\mathbf{x}))$.

### 3.2 Visual Looming, Sobel Differential Operators, and Central ROI Mask
Continuous flow divergence relating to inverse time-to-collision:
$$\nabla \cdot \mathbf{u} = \frac{\partial u}{\partial x} + \frac{\partial v}{\partial y} = \frac{V_z}{Z} + \frac{V_z}{Z} = 2 \frac{V_z}{Z} = 2 \tau^{-1}$$

Sobel spatial gradient estimation:
$$\frac{\partial u}{\partial x} \approx u * \begin{bmatrix} -1 & 0 & 1 \\ -2 & 0 & 2 \\ -1 & 0 & 1 \end{bmatrix}, \quad \frac{\partial v}{\partial y} \approx v * \begin{bmatrix} -1 & -2 & -1 \\ 0 & 0 & 0 \\ 1 & 2 & 1 \end{bmatrix}$$

Central 60% Region of Interest (ROI) indicator mask:
$$\mathcal{M}_{\text{ROI}}(y, x) = \begin{cases} 1, & 16 \le y < 68 \quad \text{and} \quad 16 \le x < 68 \\ 0, & \text{otherwise} \end{cases}$$

Mean divergence across active ROI:
$$\bar{E}_{\text{ROI}} = \frac{1}{|\mathcal{M}_{\text{ROI}}|} \sum_{(x,y) \in \mathcal{M}_{\text{ROI}}} (\nabla \cdot \mathbf{u})(x, y)$$

Bounded Non-Negative Inverse Time-to-Collision:
$$\tau^{-1}_{\text{bounded}} = \min\left( \max(0.0, \, \bar{E}_{\text{ROI}}), \, 5.0 \right) \in [0.0, \, 5.0] \text{ s}^{-1}$$

### 3.3 Linear Metric Depth Inversion
Derivation from non-linear OpenGL perspective depth buffer $d_{\text{buffer}} \in [0.0, 1.0]$:
$$D_{\text{meters}} = \frac{z_{\text{far}} \cdot z_{\text{near}}}{z_{\text{far}} - (z_{\text{far}} - z_{\text{near}}) \cdot d_{\text{buffer}}} = \frac{12.0 \times 0.1}{12.0 - (12.0 - 0.1) \cdot d_{\text{buffer}}} = \frac{1.2}{12.0 - 11.9 \cdot d_{\text{buffer}}}$$

### 3.4 Multi-Objective Physics-Informed Reward Formulation
$$R_t = R_{\text{progress}} + R_{\text{goal}} + R_{\text{TTC}} + R_{\text{attitude}} + R_{\text{proximity}} + R_{\text{terminal}}$$

Component formulations:
1. Progress potential reward:
   $$R_{\text{progress}} = 6.0 \cdot (\|\mathbf{p}_{\text{drone}, t-1} - \mathbf{p}_{\text{goal}}\|_2 - \|\mathbf{p}_{\text{drone}, t} - \mathbf{p}_{\text{goal}}\|_2)$$
2. Goal heading velocity alignment:
   $$\hat{\mathbf{d}}_{\text{goal}} = \frac{\mathbf{p}_{\text{goal}} - \mathbf{p}_{\text{drone}}}{\|\mathbf{p}_{\text{goal}} - \mathbf{p}_{\text{drone}}\|_2 + 10^{-6}}, \quad R_{\text{goal}} = 3.0 \cdot (\mathbf{v}_{\text{drone}} \cdot \hat{\mathbf{d}}_{\text{goal}})$$
3. Optical flow looming penalty:
   $$R_{\text{TTC}} = -2.0 \cdot \tau^{-1}_{\text{bounded}}$$
4. Attitude stability penalty:
   $$R_{\text{attitude}} = -0.5 \cdot (|\phi| + |\theta|)$$
5. 5th-percentile visual depth proximity safety buffer:
   $$R_{\text{proximity}} = \begin{cases} -3.0 \cdot (1.5 - \text{Percentile}_{5\%}(D_{\text{meters}})), & \text{if } \text{Percentile}_{5\%}(D_{\text{meters}}) < 1.5\text{ m} \\ 0.0, & \text{otherwise} \end{cases}$$
6. Terminal sparse success / failure reward:
   $$R_{\text{terminal}} = \begin{cases} +100.0, & \text{if } \|\mathbf{p}_{\text{drone}} - \mathbf{p}_{\text{goal}}\|_2 < 0.8\text{ m} \\ -100.0, & \text{if collision or out-of-bounds} \\ 0.0, & \text{otherwise} \end{cases}$$

### 3.5 NatureCNN Convolutional Spatial Dimensions
Convolutional output spatial dimension formula:
$$W_{\text{out}} = \left\lfloor \frac{W_{\text{in}} - K + 2P}{S} \right\rfloor + 1$$
- Layer 1: $W_1 = \lfloor \frac{84 - 8}{4} \rfloor + 1 = 20 \implies (B, 32, 20, 20)$
- Layer 2: $W_2 = \lfloor \frac{20 - 4}{2} \rfloor + 1 = 9 \implies (B, 64, 9, 9)$
- Layer 3: $W_3 = \lfloor \frac{9 - 3}{1} \rfloor + 1 = 7 \implies (B, 64, 7, 7)$
- Flattened visual features: $64 \times 7 \times 7 = 3136$

### 3.6 Continuous Gaussian Policy & Entropy
Policy distribution:
$$\pi_\theta(\mathbf{a} \mid s) = \mathcal{N}(\boldsymbol{\mu}(s), \boldsymbol{\Sigma}), \quad \boldsymbol{\Sigma} = \text{diag}(\exp(2 \cdot \text{actor\_log\_std}))$$

Action log-probability:
$$\log \pi_\theta(\mathbf{a} \mid s) = \sum_{i=1}^4 \left[ -\frac{1}{2} \log(2\pi) - \log \sigma_i - \frac{(a_i - \mu_i(s))^2}{2 \sigma_i^2} \right]$$

Differential policy entropy:
$$H(\pi_\theta(\cdot \mid s)) = 2(1 + \log(2\pi)) + \sum_{i=1}^4 \log \sigma_i$$

### 3.7 Potential Field Tangential Steering & BC Loss
Attractive baseline velocity:
$$v_{y, \text{desired}} = \min\left(1.0, \, \max\left(0.4, \, \frac{\|\mathbf{p}_{\text{goal}} - \mathbf{p}_{\text{drone}}\|_2}{3.0}\right)\right)$$
$$v_{x, \text{desired}} = 0.8 \cdot \frac{x_{\text{goal}} - x_{\text{drone}}}{\|\mathbf{p}_{\text{goal}} - \mathbf{p}_{\text{drone}}\|_2 + 10^{-6}}$$

Tangential obstacle repulsion for obstacle $i$ with clearance $d_{\text{eff}, i} < 1.8$ m:
$$F_{\text{rep}, i} = \frac{1.8 - \max(0.05, \, d_{\text{eff}, i})}{1.8}$$
$$\text{side}_i = \text{sign}(x_{\text{drone}} - ox_i)$$
$$v_{x, \text{repulse}} \leftarrow v_{x, \text{repulse}} + \text{side}_i \cdot (2.0 \cdot F_{\text{rep}, i})$$
$$v_{y, \text{slowdown}} \leftarrow v_{y, \text{slowdown}} + 0.3 \cdot F_{\text{rep}, i}$$

Guaranteed forward velocity floor (deadlock elimination):
$$v_y = \text{clip}(v_{y, \text{desired}} - v_{y, \text{slowdown}}, \, 0.35, \, 1.0)$$

Supervised Behavioral Cloning MSE objective:
$$\mathcal{L}_{\text{BC}}(\theta) = \frac{1}{B} \sum_{i=1}^B \|\boldsymbol{\mu}_\theta(s_{\text{vis}, i}, s_{\text{vel}, i}) - \mathbf{a}_{\text{expert}, i}\|_2^2$$

### 3.8 Proximal Policy Optimization (PPO) & GAE-$\lambda$
Probability ratio:
$$r_t(\theta) = \frac{\pi_\theta(\mathbf{a}_t \mid s_t)}{\pi_{\theta_{\text{old}}}(\mathbf{a}_t \mid s_t)} = \exp\left(\log \pi_\theta(\mathbf{a}_t \mid s_t) - \log \pi_{\theta_{\text{old}}}(\mathbf{a}_t \mid s_t)\right)$$

Clipped surrogate objective:
$$L^{\text{CLIP}}(\theta) = \hat{\mathbb{E}}_t \left[ \min\left( r_t(\theta) \hat{A}_t, \, \text{clip}(r_t(\theta), 1 - \epsilon, 1 + \epsilon) \hat{A}_t \right) \right]$$

Temporal difference residual and GAE-$\lambda$ recurrence:
$$\delta_t^V = r_t + \gamma V(s_{t+1}) (1 - d_t) - V(s_t)$$
$$\hat{A}_t^{\text{GAE}(\gamma, \lambda)} = \delta_t^V + (\gamma \lambda) (1 - d_t) \hat{A}_{t+1}^{\text{GAE}(\gamma, \lambda)}$$

Total composite PPO loss:
$$\mathcal{L}_{\text{total}}(\theta) = -L^{\text{CLIP}}(\theta) + c_1 L^{\text{VF}}(\theta) - c_2 S[\pi_\theta]$$
Where $L^{\text{VF}}(\theta) = \frac{1}{2} \hat{\mathbb{E}}_t [(V_\theta(s_t) - R_t)^2]$, $c_1 = 0.5$, and $c_2 = 0.01$.

### 3.9 Captum Explainability & Spatial IoU Fidelity
Captum Saliency:
$$A_{\text{Saliency}}(\mathbf{x}) = \left| \frac{\partial \mu_0(\mathbf{x}, \mathbf{v})}{\partial \mathbf{x}} \right|$$

Captum Integrated Gradients (Riemann sum over $m=30$ steps from zero baseline):
$$A_i^{\text{IG}}(\mathbf{x}, \mathbf{0}) \approx x_i \times \frac{1}{m} \sum_{k=1}^m \frac{\partial F\left(\frac{k}{m}\mathbf{x}\right)}{\partial x_i}$$

Non-linear gamma contrast boost:
$$A_{\text{boosted}}(u, v) = (A_{\text{smooth}}(u, v))^{0.7}$$

Dynamic adaptive alpha transparency:
$$\alpha(u, v) = \text{clip}\left( \frac{A_{\text{boosted}}(u, v) - 0.10}{0.85}, \, 0.0, \, 1.0 \right) \times 0.75$$

Spatial IoU explanation fidelity score:
$$\text{Spatial IoU} = \frac{|\mathcal{M}_{\text{attr}} \cap \mathcal{M}_{\text{obs}}|}{|\mathcal{M}_{\text{attr}} \cup \mathcal{M}_{\text{obs}}| + 10^{-6}}$$
Where $\mathcal{M}_{\text{attr}} = (A_{\text{2D}} \ge \text{Percentile}_{85}(A_{\text{2D}}))$ and $\mathcal{M}_{\text{obs}} = (D_{\text{ground\_truth}} < 1.5\text{ m})$.

---

## 4. Complete ASCII Architectural & Data Flow Diagrams

The authoring agent must include all 7 ASCII block diagrams below directly in `TECHNICAL_DOCUMENTATION.md`:

### Diagram 1: End-to-End System Data Flow Architecture
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

### Diagram 2: Training vs. Inference Lifecycle Pipelines
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

### Diagram 3: Multi-Rate Physics/Control Simulation Loop
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

### Diagram 4: Dual-Branch Actor-Critic Neural Topology
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

### Diagram 5: Tangential Obstacle Steering Potential Field
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

### Diagram 6: 7-Stage High-Definition Thermal Vision Pipeline
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

### Diagram 7: Unified 3-Panel HD Dashboard Geometry
```
+----------------------------------------------------------------------------------------------------+
|  HEADER BAR (1230 x 80 px) - Deep Charcoal (38, 28, 48)                                            |
|  REAL-TIME EXPLAINABLE AUTONOMOUS DRONE NAVIGATION                    [STEP: 1,420 | GOAL: 4.12m]  |
|  MONOCULAR VISION | DENSE OPTICAL FLOW | PHYSICS PPO | CAPTUM XAI     Badge: Plum (50, 35, 70)     |
|----------------------------------------------------------------------------------------------------|
|  PANEL 1 (390x390)            PANEL 2 (390x390)            PANEL 3 (390x390)                       |
|  Origin: (x=20, y=100)        Origin: (x=425, y=100)       Origin: (x=830, y=100)                  |
|                                                                                                    |
|  [3D ARENA SIMULATION MAP]    [CAMERA VISION & FLOW]       [XAI SALIENCY HEATMAP]                  |
|  - 10m x 20m Arena Grid       - Bicubic 390x390 Camera     - Google TURBO Heatmap                  |
|  - Concentric Gold Goal       - Color-Coded Flow Vectors   - Adaptive Transparency                 |
|  - Coral / Emerald Obstacles  - Cyan: Steady (mag 1.2-4)   - Neon Peak Contours                    |
|  - Cyan Drone + Red Heading   - Green: Active (mag 4-10)   - Ground-Truth Overlap                  |
|  - Real-time Position Trace   - Yellow: Looming (mag >10)  - Focus on Hazard Objs                  |
|                                                                                                    |
|  Footer: Target Dist: 4.12 m  Footer: FPS: 31.4 | Lat: 31ms Footer: Spatial IoU: 0.684             |
|----------------------------------------------------------------------------------------------------|
|  [OPTIONAL TRAINING HUD STRIP] (1230 x 64 px) - Dark Slate (28, 20, 40)                           |
|  [================================== 68.4% (684,000 / 1,000,000 Steps) =========================] |
|  SPS: 1,842  |  Best Reward: +124.8  |  Episodes: 1,420  |  P-Loss: -0.012  |  V-Loss: 0.041       |
+----------------------------------------------------------------------------------------------------+
```

---

## 5. Comprehensive Parameter & Hyperparameter Tables

The authoring agent in M2 must embed the following 6 comprehensive reference tables in Chapters 3, 4, 5, and 6:

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

### Table 4: Behavioral Cloning Pre-Training Hyperparameters
| Hyperparameter Description | CLI Argument | Value | Architectural Justification |
|---|---|---|---|
| Random Demonstration Envs | `--n-demo-envs` | `300` | Ensures coverage across diverse procedural obstacle fields |
| Target Demonstration Steps | `--target-demo-steps`| `80,000` | Dataset volume preventing overfitting during supervised BC |
| Maximum Demonstration Steps | `--demo-max-steps` | `400` | Episode truncation limit during demonstration collection |
| Supervised Training Epochs | `--bc-epochs` | `60` | Full passes through demonstration dataset |
| Mini-Batch Size | `--batch-size` | `256` | Gradient descent batch slice |
| Initial Learning Rate | `--lr` | `3e-4` | Adam base learning rate |
| Learning Rate Schedule | Cosine Annealing | $E=60$ epochs | Decays learning rate smoothly to zero |
| Weight Decay | $L_2$ Regularization | `1e-5` | Prevents weight explosion |
| Gradient Clipping Norm | `clip_grad_norm_` | `1.0` | Stabilizes backpropagation through deep conv layers |
| Demonstration Output File | `--output` | `"bc_demos.npz"` | Compressed NumPy archive containing visual, vel, and actions |
| Pre-Trained Model Checkpoint| `--save-model` | `"best_model.pt"` | Checkpoint consumed by PPO training pipeline |

### Table 5: Proximal Policy Optimization (PPO) Hyperparameters
| Hyperparameter Description | CLI Argument | Default Value | Role in Reinforcement Learning |
|---|---|---|---|
| Total Training Timesteps | `--total-timesteps` | `100,000` (std) / `4,000,000` (overnight) | Total environment interactions across all parallel workers |
| Parallel Subprocess Workers | `--n-envs` | `8` (interactive) / `16` (overnight) | Number of concurrent `SubprocVecEnv` instances |
| Rollout Horizon per Worker | `--n-steps` | `512` | Steps collected per worker before PPO update ($512 \times 8 = 4096$) |
| PPO Mini-Batch Size | `--batch-size` | `512` (std) / `2048` (overnight) | Slice size for SGD updates ($4096 / 512 = 8$ batches/epoch) |
| PPO Optimization Epochs | `--update-epochs` | `10` | Full gradient passes per rollout ($10 \times 8 = 80$ updates) |
| Discount Factor | `--gamma` | `0.99` | Long-term reward horizon discount factor ($\approx 100$ steps) |
| GAE Lambda Parameter | `--gae-lambda` | `0.95` | Advantage estimation bias-variance trade-off coefficient |
| Policy Surrogate Clip | `--clip-eps` | `0.2` | Constrains policy ratio $r_t(\theta)$ to $[0.8, 1.2]$ |
| Critic Loss Coefficient | `--vf-coef` | `0.5` | Scalar weight $c_1$ for value function squared loss |
| Policy Entropy Coefficient | `--ent-coef` | `0.01` | Scalar weight $c_2$ encouraging exploration stochasticity |
| Adam Learning Rate | `--learning-rate` | `3e-4` | Learning rate with epsilon $10^{-5}$ |
| Maximum Episode Steps | `--max-steps` | `500` | Truncation horizon per episode ($500 / 24\text{ Hz} \approx 20.8$ s) |
| Floating Point Precision | Automatic Mixed Precision | `torch.float16` (FP16) | Accelerated execution on NVIDIA Tensor Cores |
| TensorFloat-32 Acceleration | `allow_tf32` | `True` | 19-bit precision for matrix multiplications and cuDNN conv |
| Inductor Kernel Compilation | `torch.compile` | `mode="reduce-overhead"`| Fuses kernels and eliminates Python overhead via CUDA graphs |

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

## 6. Verification and Validation Guidelines for Chapter Authoring

To ensure the authoring agent in M2 produces a document that passes all validation checks in `verify_documentation.py`:

1. **Chapter Heading Exactness**:
   The 6 mandatory chapter headings must be explicitly present as top-level Markdown headers (`# Chapter X: ...` or `# Section X: ...`):
   - `Chapter 1: Executive Summary`
   - `Chapter 2: System Architecture`
   - `Chapter 3: Simulation Environment Mechanics`
   - `Chapter 4: Drone Navigation & Algorithmic Foundations`
   - `Chapter 5: Granular Module & File Breakdown`
   - `Chapter 6: Setup, Configuration & Execution`

2. **File Coverage Completeness**:
   Every one of the 10 files must have its own dedicated sub-heading in Chapter 5:
   - `5.1 environment.py`
   - `5.2 model.py`
   - `5.3 pretrain_bc.py`
   - `5.4 train.py`
   - `5.5 explainability.py`
   - `5.6 evaluate_and_visualize.py`
   - `5.7 run_project.bat`
   - `5.8 overnight_train.bat`
   - `5.9 requirements.txt`
   - `5.10 README.md`

3. **Mathematical Formula Verification**:
   The verification harness checks for the presence of the 5 key mathematical formulations:
   - Inverse time-to-collision ($\tau^{-1}$) and optical flow divergence ($\nabla \cdot \mathbf{u}$)
   - Gunnar Farneback quadratic polynomial expansion ($f_1(\mathbf{x}), f_2(\mathbf{x}), \mathbf{d}$)
   - Potential field tangential obstacle steering ($v_y \ge 0.35$, lateral deflection)
   - PPO clipped surrogate objective ($L^{\text{CLIP}}$) and Generalized Advantage Estimation (GAE-$\lambda$)
   - Spatial IoU explanation fidelity ($\text{Spatial IoU} = \frac{|\mathcal{M}_{\text{attr}} \cap \mathcal{M}_{\text{obs}}|}{|\mathcal{M}_{\text{attr}} \cup \mathcal{M}_{\text{obs}}|}$)

4. **Word Count Validation**:
   The planned budget of ~8,700 words ensures that `TECHNICAL_DOCUMENTATION.md` will comfortably exceed the **6,000-word threshold on its own**, with ample margin against any word-counting tokenization discrepancies.

---
*End of Master Blueprint for TECHNICAL_DOCUMENTATION.md (explorer_m1_1)*
