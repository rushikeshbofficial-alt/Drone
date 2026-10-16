# Real-Time Explainable Autonomous Drone Navigation in Unstructured Indoor Environments using Monocular Vision and Physics-Informed Reinforcement Learning

[![Python 3.10+](https://img.shields.io/badge/python-3.10%2B-blue.svg)](https://www.python.org/)
[![PyTorch 2.0+](https://img.shields.io/badge/pytorch-2.0%2B-ee4c2c.svg)](https://pytorch.org/)
[![Gymnasium](https://img.shields.io/badge/gymnasium-0.29%2B-008080.svg)](https://gymnasium.farama.org/)
[![PyBullet](https://img.shields.io/badge/physics-pybullet-orange.svg)](https://pybullet.org/)
[![CUDA Accelerated](https://img.shields.io/badge/CUDA-12.8%20%7C%20sm__120-76b900.svg)](https://developer.nvidia.com/cuda-zone)
[![Captum XAI](https://img.shields.io/badge/XAI-Captum-blueviolet.svg)](https://captum.ai/)

An end-to-end, high-performance research codebase for autonomous drone navigation in complex, unstructured 3D indoor environments. Combines **Monocular Vision (84x84 RGB + Farneback Dense Optical Flow)**, **Bounded Time-to-Collision ($\tau^{-1}$)**, **Physics-Informed PPO Reinforcement Learning**, **Behavioral Cloning Pre-Training via Potential Fields**, and real-time **Captum Saliency / Integrated Gradients Explainable AI (XAI)**.

---

## 🌟 Key Features & Architecture Highlights

- **Physics-Informed Gymnasium Environment (`environment.py`)**:
  - **Decoupled Frequencies**: 240 Hz PyBullet physics simulation decoupled with a 24 Hz Gymnasium control loop (8 physics substeps per control step).
  - **Monocular Vision**: 84x84 RGB-D vision rendering ($65^\circ$ FOV, near clip 0.1m, far clip 12.0m) paired with 60% central ROI Farneback Optical Flow vector field ($u, v$).
  - **Bounded Time-to-Collision**: $\tau^{-1}_{\text{bounded}} = \min(\max(0, \text{mean}_{\text{ROI}}(\nabla \cdot \mathbf{u})), \tau^{-1}_{\text{max}})$ with $\tau^{-1}_{\text{max}} = 5.0$.
  - **Multi-Objective Physics Reward**: Progress distance reward, clearance-gated goal velocity reward, optical flow expansion penalty, roll/pitch attitude stability penalty, quadratic proximity safety barrier, and terminal goal/collision rewards.
  - **Substep Boundary Clamping**: Strict coordinate clamping every physics substep preventing wall tunneling ($X \in [-4.6, 4.6]$, $Y \in [-9.6, 9.6]$, $Z \in [0.15, 3.5]$).
  - **Dual Rendering**: Hardware EGL PyBullet renderer + fallback 3D Perspective Raycasting Engine for zero-dependency execution.

- **Dual-Input Neural Network Architecture (`model.py`)**:
  - **Visual Branch**: NatureCNN processing 5-channel input tensors ($3\text{ RGB} + 2\text{ Optical Flow}$) into a 512-dimensional latent feature vector.
  - **Kinematic Branch**: Multi-Layer Perceptron (MLP) processing 3D linear velocity vector $(v_x, v_y, v_z)$ into a 64-dimensional feature vector.
  - **Feature Fusion**: Latent concatenation ($512 + 64$) feeding a 256-dimensional fully connected layer.
  - **Actor & Critic Heads**: Continuous 4D action space $(\bar{v}_x, \bar{v}_y, \bar{v}_z, \dot{\psi}) \in [-1, 1]^4$ with learnable log-std parameter, and a scalar state-value function $V(s)$.
  - **NumPy CPU Fallback**: Pure NumPy inference backend allowing model execution on restricted Windows environments.

- **Behavioral Cloning Expert Pre-Trainer (`pretrain_bc.py`)**:
  - **Potential Field Expert**: Combines goal attractive forces, visual depth obstacle repulsion, arena boundary repulsion, and 1.5m altitude holding.
  - **Dataset Collection**: Generates transition demonstration datasets (`.npz`) across randomized environment layouts.
  - **Supervised Imitation Learning**: Supervised MSE pre-training initializing policy weights prior to PPO reinforcement learning.

- **GPU-Maximized PPO Pipeline (`train.py`)**:
  - **Shared Memory IPC**: Multi-worker `SubprocVecEnv` utilizing Python `multiprocessing.shared_memory` for zero-copy visual tensor transfers across parallel environments.
  - **GAE & Mixed Precision**: Generalized Advantage Estimation (GAE-$\lambda$, $\gamma=0.99, \lambda=0.95$) with PyTorch AMP FP16/BF16 (`torch.amp.autocast`).
  - **Fine-Tuning Stability Controls**: BC anchor regularization (`--bc-anchor-coef`) to prevent catastrophic forgetting, detached critic trunk (`--detach-critic-trunk`) to protect convolutional feature representations, and reduced exploration noise (`--log-std-mode reduced`).
  - **Metadata Logging**: Saves `.meta.json` files alongside model checkpoints with exact global steps, loss hyperparameters, and evaluation metrics.
  - **TensorBoard Integration**: Real-time diagnostic telemetry logged to `runs/` (`http://localhost:6006`).

- **Explainable AI (XAI) Suite (`explainability.py`)**:
  - **Dual-Input Attribution**: Live Captum `Saliency` for real-time 30+ FPS HUD overlays, and offline `IntegratedGradients` ($N=30$) for axiomatic attribution benchmarks.
  - **Attribution Processing**: Bicubic upscaling, Gaussian spatial smoothing ($\sigma=3$), non-linear gamma contrast boost ($\gamma=1.8$), and Google `COLORMAP_TURBO` scientific heat vision rendering.
  - **Contour Extraction**: Neon peak-saliency contour highlights around obstacle boundaries.
  - **Spatial IoU Explanation Fidelity**: Quantitative intersection-over-union metric comparing visual attributions against ground-truth PyBullet depth obstacle masks ($d < 1.5\text{ m}$).

- **Tactical C2 Console & Unified HD Dashboard (`evaluate_and_visualize.py` & `tactical_renderer.py`)**:
  - **Panel 1**: 3rd-Person 3D Arena Top-Down Map (drone position, heading arrow, 3D obstacle cylinders, glowing goal target).
  - **Panel 2**: 1st-Person Monocular Camera Feed + Color-Coded Dense Optical Flow Motion Vectors.
  - **Panel 3**: High-Definition Google TURBO XAI Heat Vision Overlay + Peak Saliency Contours + Spatial IoU Fidelity Badge.
  - **Tactical C2 Telemetry Console**: Real-time HUD showing step progress, SPS throughput, synthetic horizon attitude indicator, velocity vectors, and policy statistics.

- **Automated Regression & Test Suite (`test_drone_system.py` & `eval_baseline.py`)**:
  - Automated unit and regression test suite verifying 5-channel observation shapes, raycaster bounds, reward accounting, shared memory IPC buffer lifecycle, and atomic checkpoint serialization.

- **Automated Windows Launchers (`run_project.bat` & `overnight_train.bat`)**:
  - `run_project.bat`: 6-option interactive menu for BC pretraining, PPO training, evaluation, TensorBoard, dry-run, and overnight training.
  - `overnight_train.bat`: Standalone 4-hour, 4,000,000 timestep training batch script with auto-launching Live Dashboard + TensorBoard browser windows + 60-second Windows auto-shutdown countdown.

---

## 📐 System Architecture

```
                                  +---------------------------------------+
                                  | 3D Indoor Environment (PyBullet / 3D) |
                                  +---------------------------------------+
                                           |                      |
                            Monocular RGB-D Frame (84x84)   Velocity (vx,vy,vz)
                                           |                      |
                                  +------------------+            |
                                  | Optical Flow (u,v)            |
                                  |  (Farneback ROI) |            |
                                  +------------------+            |
                                           |                      |
                                5-Channel Visual Tensor           |
                                   (3 RGB + 2 Flow)               |
                                           \                      /
                                     +----------------------------------+
                                     |  PhysicsInformedActorCritic Net  |
                                     |  NatureCNN + Kinematic MLP Fusion|
                                     +----------------------------------+
                                           /                      \
                                    Actor Head                 Critic Head
                                         |                          |
                               Action Vector (4D)            State Value V(s)
                                         |                          |
                                  +--------------+           +--------------+
                                  |  Environment |           |  PPO + GAE   |
                                  |    Control   |           |  Optimization|
                                  +--------------+           +--------------+
                                         |
                                  +--------------+
                                  | Captum XAI   | --> 3-Panel Tactical C2 Dashboard
                                  | Attribution  |     & Spatial IoU Metric
                                  +--------------+
```

---

## 🛠️ Project File Structure

```
Drone/
├── environment.py              # Gymnasium indoor drone environment (physics, flow, 3D raycaster)
├── model.py                    # Dual-input Physics-Informed Actor-Critic PyTorch model + NumPy fallback
├── explainability.py           # Captum XAI engine (Saliency, Integrated Gradients, TURBO heatmaps, Spatial IoU)
├── tactical_renderer.py        # Military-grade Tactical C2 Console HUD and synthetic vision renderer
├── pretrain_bc.py              # Potential field expert & Behavioral Cloning demonstration pre-trainer
├── train.py                    # GPU-maximized PPO training engine (SharedMemory IPC, GAE, AMP, BC anchoring)
├── evaluate_and_visualize.py   # Unified 3-panel HD dashboard & policy evaluation runner
├── test_drone_system.py        # Automated regression test suite (observations, raycaster, rewards, shared memory)
├── eval_baseline.py            # Quantitative evaluation benchmark script for model checkpoints
├── evaluation_validation_results.json # Empirical benchmark evaluation results across seed layouts
├── requirements.txt            # Python dependency manifest
├── run_project.bat             # Interactive 6-option Windows menu launcher
├── overnight_train.bat         # Standalone 4-hour 4M-step training + auto-shutdown batch script
├── tactical_c2_console.png     # Rendered visual output from Tactical C2 Console
├── best_model.pt               # Trained neural network model weights checkpoint
├── bc_25k_clean.pt             # Pre-trained Behavioral Cloning baseline checkpoint
├── ppo_25k_postfix.pt          # Fine-tuned PPO checkpoint
├── bc_demos.npz                # Saved expert behavioral demonstration dataset
│
└── Documentation/              # Complete Project Documentation Suite
    ├── Autonomous_Drone_Navigation_Technical_Documentation.docx # Comprehensive Word manual (>6,000 words, 16 tables)
    ├── TECHNICAL_DOCUMENTATION.md                               # Complete companion Markdown treatise (>7,000 words)
    ├── Stop_and_Reroute_Collision_Avoidance_Proposal.docx       # Engineering proposal for Stop, Hover & Re-Route architecture
    ├── verify_documentation.py                                  # Automated 12-check verification harness for documentation
    ├── generate_docx.py                                         # Deterministic python-docx document compiler utility
    └── ORIGINAL_REQUEST.md                                      # Documentation specification record
```

---

## 🚀 Quick Start Guide

### 1. Prerequisites & Installation

Ensure you have Python 3.10+ installed on Windows 10/11 x64. Open a terminal in the project directory and install dependencies:

```bash
pip install -r requirements.txt
```

> **Note for NVIDIA RTX 50-Series (Blackwell `sm_120`) Users:**
> If you are using an RTX 5060/5070/5080/5090 GPU, install PyTorch Nightly with CUDA 12.8 support:
> ```bash
> pip install --pre torch torchvision torchaudio --index-url https://download.pytorch.org/whl/nightly/cu128
> ```

---

### 2. Interactive Launcher (`run_project.bat`)

Double-click **`run_project.bat`** (or execute `.\run_project.bat` in PowerShell) to access the interactive menu:

```
=========================================================================
 EXPLAINABLE AUTONOMOUS DRONE NAVIGATION IN UNSTRUCTURED INDOOR ENVIRONMENTS
=========================================================================

 [0] EXPERT PRETRAINING (BC) - Run this FIRST! Creates a working model (~5 min)
 [1] PPO Fine-Tuning + Live Dashboard (run after Option 0)
 [2] Evaluate + Live 3-Panel XAI Dashboard
 [3] Launch TensorBoard Monitor (http://localhost:6006)
 [4] Run Quick Headless Test
 [5] OVERNIGHT 4-HOUR TRAINING + AUTO SHUTDOWN (Run before sleeping)
 [6] Exit
=========================================================================
```

---

### 3. Step-by-Step Command-Line Execution

#### Step 1: Expert Behavioral Cloning Pre-Training
A potential-field expert navigates 300 randomized environments, recording 80,000 transitions. Supervised MSE imitation learning pre-trains `best_model.pt`:
```bash
python pretrain_bc.py --n-demo-envs 300 --target-demo-steps 80000 --bc-epochs 60
```

#### Step 2: High-Throughput Parallel PPO Training
Fine-tune the model using PPO reinforcement learning with SharedMemory IPC, 12 parallel environments, and the live dashboard:
```bash
python train.py --total-timesteps 500000 --n-envs 12 --n-steps 512 --batch-size 1024 --update-epochs 10 --dashboard
```

#### Step 3: Policy Evaluation & Tactical C2 Dashboard
Evaluate the trained model on training layout seeds with the HD TURBO Heat Vision Dashboard and Spatial IoU metrics:
```bash
python evaluate_and_visualize.py --checkpoint best_model.pt --eval-mode training --gui
```

To test generalization on brand-new, unseen procedural obstacle layouts:
```bash
python evaluate_and_visualize.py --checkpoint best_model.pt --eval-mode unseen --gui
```

#### Step 4: TensorBoard Monitoring
Monitor live training curves (Episodic Return, Goal Distance, Policy Loss, Value Loss, Entropy, SPS):
```bash
python -m tensorboard.main --logdir runs
```
Open your browser at `http://localhost:6006`.

#### Step 5: Regression & Unit Testing
Run the automated test suite to verify raycaster outputs, observation shapes, reward accounting, and shared memory IPC:
```bash
python -m unittest test_drone_system.py
```

#### Step 6: Documentation Verification
Validate the integrity and completeness of the documentation suite in `Documentation/`:
```bash
python Documentation/verify_documentation.py
```

---

## 🌙 Overnight Training & Auto-Shutdown

To run an unattended 4-hour, 4,000,000 timestep training session:

1. Execute **`overnight_train.bat`** (or select Option `5` in `run_project.bat`).
2. The script will automatically:
   - Check for pre-trained weights (`best_model.pt`) and generate them via BC if missing.
   - Launch **TensorBoard** at `http://localhost:6006`.
   - Launch the **Live 3-Panel OpenCV Dashboard Window**.
   - Execute 4,000,000 steps of PPO training using 12 parallel GPU workers with SharedMemory IPC.
   - Save the best weights to `best_model.pt`.
   - Initiate a **60-second Windows Auto-Shutdown countdown**.

> **To cancel shutdown if needed:** Press any key in the batch console, or open Command Prompt and type `shutdown /a`.

---

## 🔬 Mathematical Formulations

### 1. Optical Flow Divergence & Bounded Time-to-Collision ($\tau^{-1}$)
$$\nabla \cdot \mathbf{u} = \frac{\partial u}{\partial x} + \frac{\partial v}{\partial y}$$

$$\tau^{-1}_{\text{bounded}} = \min\left(\max\left(0, \frac{1}{|N_{\text{ROI}}|} \sum_{(x,y) \in \text{ROI}} \left(\frac{\partial u}{\partial x} + \frac{\partial v}{\partial y}\right)\right), \tau^{-1}_{\text{max}}\right)$$

Where $\tau^{-1}_{\text{max}} = 5.0\text{ s}^{-1}$ and ROI is the central 60% camera window ($[16:68, 16:68]$).

---

### 2. Multi-Objective Physics Reward Function
Implemented directly in [`environment.py`](environment.py):

$$R = R_{\text{progress}} + R_{\text{goal}} + R_{\text{TTC}} + R_{\text{attitude}} + R_{\text{proximity}} + R_{\text{terminal}}$$

$$\begin{aligned}
R_{\text{progress}} &= 6.0 \cdot (d_{\text{prev}} - d_{\text{curr}}) \\
R_{\text{goal}} &= 2.5 \cdot (\mathbf{v}_{\text{drone}} \cdot \hat{\mathbf{d}}_{\text{goal}}) \cdot \text{clearance\_factor} \\
R_{\text{TTC}} &= -2.0 \cdot \tau^{-1}_{\text{bounded}} \\
R_{\text{attitude}} &= -0.5 \cdot (|\phi| + |\theta|) \\
R_{\text{proximity}} &= \begin{cases} -5.0 \cdot (1.2 - d_{\min})^2, & \text{if } d_{\min} < 1.2\text{ m} \\ 0, & \text{otherwise} \end{cases} \\
R_{\text{terminal}} &= \begin{cases} +100.0, & \text{if goal reached } (d < 0.8\text{ m}) \\ -100.0, & \text{if collision or out of bounds} \end{cases}
\end{aligned}$$

Where $\text{clearance\_factor} = \text{clip}\left(\frac{d_{\min} - 0.8}{1.0}, 0.0, 1.0\right)$ prevents the agent from collecting goal velocity rewards while rushing into obstacles.

---

### 3. Spatial IoU Explanation Fidelity Metric
Implemented in [`explainability.py`](explainability.py):

$$\text{Spatial IoU} = \frac{|\mathcal{M}_{\text{attr}} \cap \mathcal{M}_{\text{obstacle}}|}{|\mathcal{M}_{\text{attr}} \cup \mathcal{M}_{\text{obstacle}}|}$$

Where $\mathcal{M}_{\text{attr}}$ is the binary mask of the top 15% visual attributions and $\mathcal{M}_{\text{obstacle}}$ is the ground-truth PyBullet depth obstacle mask ($d < 1.5\text{ m}$).

---

## 📚 Documentation Directory (`Documentation/`)

All formal treatises, engineering proposals, and verification utilities are organized in the [`Documentation/`](Documentation/) folder:

| File | Type | Description |
| :--- | :--- | :--- |
| **[`Autonomous_Drone_Navigation_Technical_Documentation.docx`](Documentation/Autonomous_Drone_Navigation_Technical_Documentation.docx)** | Word DOCX | Publication-grade systems treatise (>6,000 words, 16 formatted tables, styled callouts, and code blocks). |
| **[`TECHNICAL_DOCUMENTATION.md`](Documentation/TECHNICAL_DOCUMENTATION.md)** | Markdown | Companion technical treatise (>7,000 words, LaTeX equations, ASCII architecture diagrams). |
| **[`Stop_and_Reroute_Collision_Avoidance_Proposal.docx`](Documentation/Stop_and_Reroute_Collision_Avoidance_Proposal.docx)** | Word DOCX | Engineering specification for active looming deceleration, zero-velocity hover stabilization, and sector-based lateral escape. |
| **[`verify_documentation.py`](Documentation/verify_documentation.py)** | Python | Automated 12-check verification test harness validating word counts, OpenXML parseability, and file audits. |
| **[`generate_docx.py`](Documentation/generate_docx.py)** | Python | Deterministic compiler used to generate the styled Word document. |

---

## 🛡️ Stop, Hover & Re-Route (SHR) Safety Shield Architecture

To provide deterministic collision avoidance guarantees without altering the underlying environment physics, reward functions, or termination semantics, the system incorporates a two-tier safety architecture:

### 1. Tier 1: Deterministic Gymnasium Wrapper (`drone_shield.py`)
The `StopAndRerouteShield` wrapper sits directly between the policy and the PyBullet environment. It intercepts continuous actions and executes a deterministic Finite State Machine (FSM):

```
+------------------+   TTC < 0.28s   +------------------+
|     NOMINAL      | --------------> |      BRAKE       |
| Speed Governor   |                 | a = [0, 0, vz, 0]|
+------------------+                 +------------------+
         ▲                                     │
         │ Clear                               ▼ 1 Step
+------------------+   Argmax Score  +------------------+
|     REROUTE      | <-------------- |       SCAN       |
| Lateral Avoidance|                 | Clearance + Goal |
+------------------+                 +------------------+
```

- **Smooth Speed Governor:** Capped forward and lateral speed approaching obstacles:
  $$v_{\text{cap}}(d) = \min\left(3.0, \sqrt{2 \cdot a_{\text{dec}} \cdot \max(d - d_{\text{safe}}, 0)}\right)$$
- **Instantaneous Active Braking:** Exploits PyBullet substep velocity control (`resetBaseVelocity`) to achieve an open-loop stopping displacement of **0.000 meters** from full 3.0 m/s cruise speed.
- **Dual Sensor Modes:**
  - `oracle` (Recommended): Privileged 360-degree analytical 2D raycasting along the velocity cone, lateral quadrants, and arena walls. Achieves **0.0% collisions across all 85 tested episodes**.
  - `camera`: Passive horizontal central-ROI depth evaluation. Suffers from a 31.7% velocity-heading blindspot outside the $65^\circ$ FOV during lateral dodging maneuvers.

### 2. Tier 2: Policy Distillation Engine (`shield_dagger.py`)
Distills the protective safety actions of the shield and privileged potential field expert into the `PhysicsInformedActorCritic` neural network weights via DAgger (Dataset Aggregation) with decaying mixing parameter $\beta \in [0.70, 0.00]$ and critical recovery state rebalancing.

### 3. Running Evaluation with Safety Shield

#### Benchmarking Harness (`eval_shield.py`):
```bash
# Run A/B Comparison on Reference Seeds [101, 202, 303, 404, 505]:
python eval_shield.py --checkpoint best_model.pt --seeds reference --compare

# Evaluate 30 Tuning Seeds (2000-2029) with Oracle Shield:
python eval_shield.py --checkpoint best_model.pt --seeds tuning --shield --shield-mode oracle

# Run 50 Held-Out Certification Seeds (1000-1049):
python eval_shield.py --checkpoint best_model.pt --seeds 1000-1049 --compare
```

#### Tactical C2 Interactive Dashboard (`evaluate_and_visualize.py`):
```bash
# Launch live dashboard with Oracle Safety Shield:
python evaluate_and_visualize.py --shield --shield-mode oracle --eval-mode reference

# Launch live dashboard with Camera-based Shield:
python evaluate_and_visualize.py --shield --shield-mode camera --eval-mode reference
```

#### DAgger Policy Distillation (`shield_dagger.py`):
```bash
python shield_dagger.py --rounds 4 --episodes-per-round 30 --rollout-seed-start 3000 --val-seeds tuning
```

---

## 📊 Citation & License

Developed for Final-Year Research on Explainable Autonomous Robotics and Physics-Informed Reinforcement Learning. Distributed under the MIT License.

