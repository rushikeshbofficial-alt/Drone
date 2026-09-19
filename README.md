# Real-Time Explainable Autonomous Drone Navigation in Unstructured Indoor Environments using Monocular Vision and Physics-Informed Reinforcement Learning

[![Python 3.10+](https://img.shields.io/badge/python-3.10%2B-blue.svg)](https://www.python.org/)
[![PyTorch 2.5+](https://img.shields.io/badge/pytorch-2.5%2B-ee4c2c.svg)](https://pytorch.org/)
[![Gymnasium](https://img.shields.io/badge/gymnasium-0.29%2B-008080.svg)](https://gymnasium.farama.org/)
[![PyBullet](https://img.shields.io/badge/physics-pybullet-orange.svg)](https://pybullet.org/)
[![CUDA Accelerated](https://img.shields.io/badge/CUDA-12.8%20%7C%20sm__120-76b900.svg)](https://developer.nvidia.com/cuda-zone)
[![Captum XAI](https://img.shields.io/badge/XAI-Captum-blueviolet.svg)](https://captum.ai/)

An end-to-end, high-performance final-year research codebase for autonomous drone navigation in complex, unstructured 3D indoor environments. Combines **Monocular Vision (RGB + Farneback Optical Flow)**, **Bounded Time-to-Collision ($\tau^{-1}$)**, **Physics-Informed PPO Reinforcement Learning**, **Behavioral Cloning Pre-Training**, and real-time **Captum Saliency / Integrated Gradients Explainable AI (XAI)**.

---

## 🌟 Key Features & Highlights

- **Physics-Informed Gymnasium Environment (`environment.py`)**:
  - 240 Hz PyBullet physics simulation decoupled with 24 Hz Gymnasium control loop (8 substeps/step).
  - Monocular 84x84 RGB-D vision rendering with 60% central ROI Farneback Optical Flow vector field ($u, v$).
  - Bounded Inverse Time-to-Collision ($\tau^{-1}_{\text{bounded}} = \min(\max(0, \text{mean}(\nabla \cdot \mathbf{u})), \tau^{-1}_{\text{max}})$).
  - Multi-objective physics reward shaping: Goal heading velocity, optical flow expansion penalty, roll/pitch attitude stability penalty, and 1.5m visual depth proximity safety buffer.
  - Strict sub-step coordinate boundary clamping preventing wall tunneling.
  - Hardware EGL PyBullet renderer + fallback 3D Perspective Raycasting Engine for zero-dependency execution.

- **Dual-Input Neural Network Architecture (`model.py`)**:
  - **Visual Branch**: NatureCNN processing 5-channel input tensors ($3\text{ RGB} + 2\text{ Optical Flow}$).
  - **Kinematic Branch**: Multi-Layer Perceptron (MLP) processing 3D linear velocity vector $(v_x, v_y, v_z)$.
  - **Feature Fusion**: Latent concatenation (512 visual + 64 kinematic) feeding 256-dim FC layer.
  - **Actor & Critic Heads**: Continuous 4D action space $(\bar{v}_x, \bar{v}_y, \bar{v}_z, \dot{\psi}) \in [-1, 1]^4$ and scalar value function $V(s)$.

- **Behavioral Cloning Expert Pre-Trainer (`pretrain_bc.py`)**:
  - Potential Field Expert Navigator combining goal attractive forces, visual depth obstacle repulsion, arena boundary repulsion, and 1.5m altitude holding.
  - Collects 80,000 demonstration transitions across 300 randomized environment layouts.
  - Supervised MSE imitation learning (60 epochs) initializing `best_model.pt` with a ~66%+ success baseline prior to PPO fine-tuning.

- **GPU-Maximized PPO Pipeline (`train.py`)**:
  - `SubprocVecEnv` multi-process worker architecture running N parallel environments (8–16 workers).
  - Generalized Advantage Estimation (GAE-$\lambda$) with AMP FP16 mixed precision (`torch.amp.autocast`).
  - `torch.compile(mode="reduce-overhead")` kernel fusion supporting NVIDIA Blackwell RTX 50-series (`sm_120`), Ada, and Ampere GPUs.
  - Automatic TensorBoard logging (`http://localhost:6006`).

- **Explainable AI (XAI) Engine (`explainability.py`)**:
  - Dual-input tuple Captum attribution analysis: Vanilla `Saliency` for live 30+ FPS dashboard visualization and `IntegratedGradients` ($N=30$) for offline metrics.
  - HD Bicubic Super-Resolution upscaling, Gaussian spatial smoothing, and non-linear gamma contrast boost.
  - Google `COLORMAP_TURBO` scientific heat vision rendering with adaptive alpha masking.
  - Neon peak-saliency contour highlights around obstacle boundaries.
  - Quantitative **Spatial IoU Explanation Fidelity Metric** comparing visual attributions against ground-truth PyBullet depth obstacle masks (< 1.5m).

- **Unified High-Definition 3-Panel XAI Dashboard (`evaluate_and_visualize.py`)**:
  - **Panel 1**: 3rd-Person 3D Arena Top-Down Map (Drone position, heading arrow, 3D obstacles, glowing goal target).
  - **Panel 2**: 1st-Person Monocular Camera Feed + Color-Coded Dense Optical Flow Motion Vectors.
  - **Panel 3**: High-Definition Google TURBO XAI Heat Vision Overlay + Peak Saliency Contours + Spatial IoU Fidelity Badge.
  - **Live Training Stats Bar**: Step progress bar (`% done`), SPS, best reward, total episodes, policy loss, value loss, and entropy.

- **Automated Windows Launchers (`run_project.bat` & `overnight_train.bat`)**:
  - `run_project.bat`: 6-option interactive menu for BC pretraining, PPO training, evaluation, TensorBoard, dry-run, and overnight training.
  - `overnight_train.bat`: Standalone 4-hour, 4,000,000 timestep training script with auto-launching Live Dashboard + TensorBoard browser windows + 60-second Windows auto-shutdown countdown.

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
                                  | Captum XAI   | --> 3-Panel HD TURBO Dashboard
                                  | Attribution  |     & Spatial IoU Metric
                                  +--------------+
```

---

## 🛠️ Project File Structure

```
Drone/
├── environment.py              # Gymnasium indoor drone environment (physics, flow, 3D render)
├── model.py                    # Dual-input Physics-Informed Actor-Critic PyTorch model
├── explainability.py           # Captum XAI engine, TURBO heat vision, Spatial IoU metric
├── pretrain_bc.py              # Potential field expert & Behavioral Cloning pre-trainer
├── train.py                    # GPU-maximized PPO training loop (AMP, SubprocVecEnv, compile)
├── evaluate_and_visualize.py   # Unified 3-panel HD dashboard & policy evaluator
├── requirements.txt            # Python dependency manifest
├── run_project.bat             # Interactive 6-option Windows menu launcher
├── overnight_train.bat         # Standalone 4-hour 4M-step training + auto-shutdown batch script
├── best_model.pt               # Saved trained model weights checkpoint
└── README.md                   # Project documentation & research summary
```

---

## 🚀 Quick Start Guide

### 1. Prerequisites & Installation

Ensure you have Python 3.10+ installed on Windows 10/11 x64. Open a command prompt in the project folder and install dependencies:

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

Double-click **`run_project.bat`** to open the main menu:

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

### 3. Recommended Workflow

#### Step 1: Expert Pre-Training (Option `0`)
Run Behavioral Cloning pre-training. A physics-based potential field expert generates 80,000 demonstrations across 300 environments, training the neural network to achieve a ~66%+ baseline success rate in under 5 minutes:

```bash
python pretrain_bc.py --n-demo-envs 300 --target-demo-steps 80000 --bc-epochs 60
```

#### Step 2: Live PPO Training & Dashboard (Option `1`)
Fine-tune the model using PPO reinforcement learning with the live 3-panel visual dashboard running in real-time:

```bash
python train.py --total-timesteps 200000 --n-envs 8 --n-steps 512 --batch-size 512 --dashboard
```

#### Step 3: Policy Evaluation & XAI Heatmaps (Option `2`)
Run policy evaluation with the HD TURBO Heat Vision Dashboard and Spatial IoU Explanation Fidelity metrics:

```bash
python evaluate_and_visualize.py --checkpoint best_model.pt --eval-mode training --gui
```

To test generalization on brand-new, unseen obstacle layouts:
```bash
python evaluate_and_visualize.py --checkpoint best_model.pt --eval-mode unseen --gui
```

#### Step 4: TensorBoard Monitoring (Option `3`)
Monitor live training curves (Episode Reward, Goal Distance, Policy Loss, Value Loss, Entropy, SPS):

```bash
python -m tensorboard.main --logdir runs
```
Open your browser at: `http://localhost:6006`

---

## 🌙 Overnight Training & Auto-Shutdown

To run a full 4-hour, 4,000,000 timestep training session before going to sleep:

1. Double-click **`overnight_train.bat`** (or select Option `5` in `run_project.bat`).
2. The script will automatically:
   - Verify/generate pre-trained BC baseline weights.
   - Launch **TensorBoard Web Overview** at `http://localhost:6006` in your browser.
   - Launch the **Live 3-Panel OpenCV Dashboard Window**.
   - Execute 4M steps of PPO training using 16 parallel GPU workers.
   - Save the best weights to `best_model.pt`.
   - Initiate a **60-second Windows Auto-Shutdown countdown**.

> **To cancel shutdown if needed:** Open Command Prompt or press `Win + R` and type `shutdown /a`.

---

## 🔬 Mathematical Formulation

### 1. Bounded Time-to-Collision ($\tau^{-1}$)
$$\tau^{-1}_{\text{bounded}} = \min\left(\max\left(0, \frac{1}{|N_{\text{ROI}}|} \sum_{(x,y) \in \text{ROI}} \left(\frac{\partial u}{\partial x} + \frac{\partial v}{\partial y}\right)\right), \tau^{-1}_{\text{max}}\right)$$

### 2. Multi-Objective Reward Function
$$R = R_{\text{goal}} + R_{\text{TTC}} + R_{\text{attitude}} + R_{\text{proximity}} + R_{\text{terminal}}$$

$$\begin{aligned}
R_{\text{goal}} &= 2.0 \cdot (\mathbf{v}_{\text{drone}} \cdot \hat{\mathbf{d}}_{\text{goal}}) \\
R_{\text{TTC}} &= -1.5 \cdot \tau^{-1}_{\text{bounded}} \\
R_{\text{attitude}} &= -0.5 \cdot (|\phi| + |\theta|) \\
R_{\text{proximity}} &= \begin{cases} -2.0 \cdot (1.5 - d_{\text{min}}), & \text{if } d_{\text{min}} < 1.5\text{ m} \\ 0, & \text{otherwise} \end{cases} \\
R_{\text{terminal}} &= \begin{cases} +100.0, & \text{if goal reached } (d < 0.8\text{ m}) \\ -100.0, & \text{if collision or out of bounds} \end{cases}
\end{aligned}$$

### 3. Spatial IoU Explanation Fidelity Metric
$$\text{Spatial IoU} = \frac{|\mathcal{M}_{\text{attr}} \cap \mathcal{M}_{\text{obstacle}}|}{|\mathcal{M}_{\text{attr}} \cup \mathcal{M}_{\text{obstacle}}|}$$

Where $\mathcal{M}_{\text{attr}}$ is the binary mask of top 15% visual attributions and $\mathcal{M}_{\text{obstacle}}$ is the ground-truth PyBullet obstacle depth mask ($d < 1.5\text{ m}$).

---

## 📊 Citation & License

Developed for Final-Year Research on Explainable Autonomous Robotics and Physics-Informed Reinforcement Learning. Distributed under the MIT License.
