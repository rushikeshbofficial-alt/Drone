# Exhaustive Technical Audit Report: Neural Architecture, Expert Cloning, PPO Optimization, and Explainability Engine

**Audited Modules**: `model.py`, `pretrain_bc.py`, `train.py`, `explainability.py`  
**Workspace Root**: `c:\Users\Rushikesh\Desktop\Cool Ass Projects\Drone`  
**Investigator**: `explorer_survey_2`  
**Date**: 2026-09-19  

---

## Table of Contents
1. [Executive Overview & Inter-Module Data Flow](#1-executive-overview--inter-module-data-flow)
2. [Neural Network Architecture (`model.py`)](#2-neural-network-architecture-modelpy)
   - [2.1 Dual-Input Architectural Topology](#21-dual-input-architectural-topology)
   - [2.2 NatureCNN Visual Branch & Dimensionality Trace](#22-naturecnn-visual-branch--dimensionality-trace)
   - [2.3 Kinematic Feature Extractor MLP](#23-kinematic-feature-extractor-mlp)
   - [2.4 Latent Fusion & Actor-Critic Multi-Head Split](#24-latent-fusion--actor-critic-multi-head-split)
   - [2.5 Continuous 4D Action Distribution Formulation](#25-continuous-4d-action-distribution-formulation)
   - [2.6 NumPy CPU Fallback Engine & AppLocker Resilience](#26-numpy-cpu-fallback-engine--applocker-resilience)
3. [Behavioral Cloning & Physics-Based Expert Planner (`pretrain_bc.py`)](#3-behavioral-cloning--physics-based-expert-planner-pretrain_bcpy)
   - [3.1 Motivation & Exploration Bottleneck Resolution](#31-motivation--exploration-bottleneck-resolution)
   - [3.2 Tangential Obstacle Steering & Potential Field Dynamics](#32-tangential-obstacle-steering--potential-field-dynamics)
   - [3.3 Mathematical Formulations of Expert Forces](#33-mathematical-formulations-of-expert-forces)
     - [3.3.1 Attractive Goal Force & Forward Surge](#331-attractive-goal-force--forward-surge)
     - [3.3.2 Tangential Obstacle Deflection](#332-tangential-obstacle-deflection)
     - [3.3.3 Monocular Depth Sector Guidance](#333-monocular-depth-sector-guidance)
     - [3.3.4 Arena Boundary Clamping & Repulsion](#334-arena-boundary-clamping--repulsion)
     - [3.3.5 Proportional Altitude Holding Force](#335-proportional-altitude-holding-force)
   - [3.4 Demonstration Collection & Buffer Architecture](#34-demonstration-collection--buffer-architecture)
   - [3.5 Supervised Imitation Learning Loop & Optimization](#35-supervised-imitation-learning-loop--optimization)
4. [Proximal Policy Optimization (PPO) Training Pipeline (`train.py`)](#4-proximal-policy-optimization-ppo-training-pipeline-trainpy)
   - [4.1 PPO Mathematical Formulation & Clipped Surrogate Objective](#41-ppo-mathematical-formulation--clipped-surrogate-objective)
   - [4.2 Generalized Advantage Estimation (GAE-$\lambda$)](#42-generalized-advantage-estimation-gae-lambda)
   - [4.3 Value Function Loss & Policy Entropy Regularization](#43-value-function-loss--policy-entropy-regularization)
   - [4.4 Hyperparameter Specifications & Tuning Dimensions](#44-hyperparameter-specifications--tuning-dimensions)
   - [4.5 Vectorized Execution: `SubprocVecEnv` vs `SingleEnv`](#45-vectorized-execution-subprocvecenv-vs-singleenv)
   - [4.6 Hardware Accelerator Optimizations (AMP FP16, TF32, `torch.compile`)](#46-hardware-accelerator-optimizations-amp-fp16-tf32-torchcompile)
   - [4.7 Rollout Buffering & State Serialization Logic](#47-rollout-buffering--state-serialization-logic)
5. [Explainable AI (XAI) Engine (`explainability.py`)](#5-explainable-ai-xai-engine-explainabilitypy)
   - [5.1 Dual-Input Attribution Framework](#51-dual-input-attribution-framework)
   - [5.2 Vanilla Saliency vs Integrated Gradients (IG) Formulations](#52-vanilla-saliency-vs-integrated-gradients-ig-formulations)
   - [5.3 Fallback Edge & Motion Gradient Engine](#53-fallback-edge--motion-gradient-engine)
   - [5.4 High-Definition Thermal Vision Pipeline](#54-high-definition-thermal-vision-pipeline)
     - [5.4.1 Bicubic Super-Resolution & Spatial Smoothing](#541-bicubic-super-resolution--spatial-smoothing)
     - [5.4.2 Non-Linear Gamma Contrast Boost](#542-non-linear-gamma-contrast-boost)
     - [5.4.3 Google TURBO Perceptual Colormap Integration](#543-google-turbo-perceptual-colormap-integration)
     - [5.4.4 Adaptive Alpha Masking Dynamics](#544-adaptive-alpha-masking-dynamics)
     - [5.4.5 Neon Peak-Saliency Contour Extraction](#545-neon-peak-saliency-contour-extraction)
   - [5.5 Spatial IoU Explanation Fidelity Metric](#55-spatial-iou-explanation-fidelity-metric)
6. [Granular Class, Method, and Hyperparameter Reference Matrix](#6-granular-class-method-and-hyperparameter-reference-matrix)

---

## 1. Executive Overview & Inter-Module Data Flow

The autonomous drone navigation system relies on an integrated pipeline bridging supervised imitation learning, deep reinforcement learning, and real-time explainable artificial intelligence. The four audited files form the computational core of this autonomous flight stack:

```
+----------------------------------------------------------------------------------------------------+
|                                      OFFLINE PRE-TRAINING PHASE                                    |
|                                                                                                    |
|   +--------------------------+       Transitions (N, 5, 84, 84) & (N, 3)     +------------------+  |
|   |   IndoorDroneNavEnv      | --------------------------------------------> |  pretrain_bc.py  |  |
|   |  (Procedural Simulation) |                                               | (Expert Planner) |  |
|   +--------------------------+ <-------------------------------------------- +------------------+  |
|                 |                         Expert Action a* in [-1, 1]^4                |           |
|                 |                                                                       | Supervised|
|                 |                                                                       | MSE Loss  |
|                 v                                                                       v           |
|          +--------------+                                                        +--------------+  |
|          | bc_demos.npz |                                                        | best_model.pt|  |
|          +--------------+                                                        +--------------+  |
+-----------------------------------------------------------------------------------------|----------+
                                                                                          | Initial
                                                                                          | Weights
+-----------------------------------------------------------------------------------------v----------+
|                                    ONLINE RL FINE-TUNING PHASE (train.py)                          |
|                                                                                                    |
|    +-------------------+         Actions a_t           +-----------------------------------------+ |
|    |  SubprocVecEnv    | <---------------------------- |       model.py (Actor-Critic)           | |
|    | (N Parallel Envs) | ----------------------------> |  (Dual-Input NatureCNN + Kinematic MLP) | |
|    +-------------------+    (vis: 5x84x84, vel: 3)     +-----------------------------------------+ |
|              |                                                               |                     |
|              v                                                               v                     |
|    +-------------------+       Rollout Buffer (T*N)            +---------------------------------+ |
|    |   RolloutBuffer   | ------------------------------------> | PPO Optimization (AMP FP16, GAE)| |
|    +-------------------+                                       +---------------------------------+ |
+-----------------------------------------------------------------------------------------|----------+
                                                                                          | Visual &
                                                                                          | Kinematic
                                                                                          | Tensors
+-----------------------------------------------------------------------------------------v----------+
|                                  REAL-TIME EXPLAINABILITY (explainability.py)                       |
|                                                                                                    |
|    +---------------------------+   Attribution Map (84x84)     +---------------------------------+ |
|    |   Captum Saliency / IG    | ----------------------------> | Bicubic Upscale + Gaussian Blur | |
|    |  (Dual-Input Gradients)   |                               |  + Gamma 0.7 + Google TURBO     | |
|    +---------------------------+                               +---------------------------------+ |
|                                                                                  |                 |
|                                                                                  v                 |
|                                                                +---------------------------------+ |
|                                                                | High-Definition Thermal Overlay | |
|                                                                |   + Spatial IoU Fidelity Score  | |
|                                                                +---------------------------------+ |
+----------------------------------------------------------------------------------------------------+
```

1. **`model.py`** defines `PhysicsInformedActorCritic`, processing dual-stream inputs: a 5-channel visual observation (3-channel RGB + 2-channel Farneback optical flow) and a 3-channel kinematic linear velocity vector $(v_x, v_y, v_z)$. It computes continuous action distributions for 4D drone velocity/yaw commands and estimates state values.
2. **`pretrain_bc.py`** bootstraps policy weights via supervised imitation learning on an algorithmic Potential Field expert planner featuring tangential obstacle steering. It creates `bc_demos.npz` and outputs `best_model.pt` to jump-start reinforcement learning.
3. **`train.py`** executes GPU-accelerated Proximal Policy Optimization (PPO) using Generalized Advantage Estimation (GAE-$\lambda$), automatic mixed precision (AMP FP16), `torch.compile(mode="reduce-overhead")`, and vectorized subprocess environments (`SubprocVecEnv`).
4. **`explainability.py`** provides `DroneXAIEngine`, utilizing Captum Saliency and Integrated Gradients across dual inputs to generate high-definition Google TURBO heatmaps with neon peak contours and quantitative Spatial IoU explanation fidelity.

---

## 2. Neural Network Architecture (`model.py`)

### 2.1 Dual-Input Architectural Topology

The neural control architecture (`PhysicsInformedActorCritic`) decouples perception from odometry through a two-stream deep network before fusing representations into a shared latent manifold:

```
Visual Stream: (B, 5, 84, 84)                       Kinematic Stream: (B, 3)
   [3 RGB + 2 Farneback Flow]                                  [vx, vy, vz]
              |                                                     |
    Conv2D(5->32, k=8, s=4)                                  Linear(3 -> 64)
              | ReLU                                                | ReLU
    Conv2D(32->64, k=4, s=2)                                        |
              | ReLU                                                |
    Conv2D(64->64, k=3, s=1)                                        |
              | ReLU                                                |
          Flatten() -> (B, 3136)                                    |
              |                                                     |
       Linear(3136 -> 512)                                          |
              | ReLU                                                |
       Visual Latent (B, 512)                             Kinematic Latent (B, 64)
              \                                                     /
               \-------------------------\ /-----------------------/
                                          v
                              Concatenation: (B, 576)
                                          |
                                 Linear(576 -> 256)
                                          | ReLU
                                Shared Latent: (B, 256)
                                          |
                     +--------------------+--------------------+
                     |                                         |
               [Actor Head]                              [Critic Head]
             Linear(256 -> 128)                        Linear(256 -> 128)
                     | ReLU                                    | ReLU
             Linear(128 -> 4)                          Linear(128 -> 1)
                     | Tanh                                    | Squeeze(-1)
              Mean mu in [-1, 1]^4                         State Value V(s)
                     |                                         (B,)
           Diag Gaussian N(mu, sigma^2)
           sigma = exp(actor_log_std)
```

### 2.2 NatureCNN Visual Branch & Dimensionality Trace

The visual feature extractor follows the deep NatureCNN architecture (Mnih et al., 2015), modified to ingest a 5-channel tensor `(B, 5, 84, 84)`:
- Channels 0, 1, 2: Monocular forward-facing camera RGB pixel intensities, normalized to $[0.0, 1.0]$.
- Channels 3, 4: Horizontal ($u$) and vertical ($v$) dense optical flow fields calculated via Gunnar Farneback's polynomial expansion algorithm.

The spatial dimension transformations across the convolutional pipeline are computed via the standard receptive field formula:
$$W_{\text{out}} = \left\lfloor \frac{W_{\text{in}} - K + 2P}{S} \right\rfloor + 1$$

With padding $P=0$:
1. **Input**: Tensor of shape $(B, 5, 84, 84)$.
2. **Conv Layer 1**: `nn.Conv2d(in_channels=5, out_channels=32, kernel_size=8, stride=4)`
   $$H_1 = W_1 = \left\lfloor \frac{84 - 8}{4} \right\rfloor + 1 = \left\lfloor \frac{76}{4} \right\rfloor + 1 = 19 + 1 = 20$$
   Output tensor: $(B, 32, 20, 20)$. Followed by `nn.ReLU()`.
3. **Conv Layer 2**: `nn.Conv2d(in_channels=32, out_channels=64, kernel_size=4, stride=2)`
   $$H_2 = W_2 = \left\lfloor \frac{20 - 4}{2} \right\rfloor + 1 = \left\lfloor \frac{16}{2} \right\rfloor + 1 = 8 + 1 = 9$$
   Output tensor: $(B, 64, 9, 9)$. Followed by `nn.ReLU()`.
4. **Conv Layer 3**: `nn.Conv2d(in_channels=64, out_channels=64, kernel_size=3, stride=1)`
   $$H_3 = W_3 = \left\lfloor \frac{9 - 3}{1} \right\rfloor + 1 = 6 + 1 = 7$$
   Output tensor: $(B, 64, 7, 7)$. Followed by `nn.ReLU()`.
5. **Flattening**: `nn.Flatten()` produces a 1D vector per batch item:
   $$\text{Dim}_{\text{flat}} = 64 \times 7 \times 7 = 3136$$
   Output tensor: $(B, 3136)$.
6. **Visual Linear Projection**: `self.visual_fc = nn.Sequential(nn.Linear(3136, 512), nn.ReLU())`
   Output tensor: $(B, 512)$.

### 2.3 Kinematic Feature Extractor MLP

The kinematic branch processes the drone's instantaneous 3D linear velocity vector $\mathbf{v} = (v_x, v_y, v_z)^T \in \mathbb{R}^3$.
- `self.kinematic_fc = nn.Sequential(nn.Linear(3, 64), nn.ReLU())`
- Input shape: $(B, 3)$
- Output shape: $(B, 64)$

This feeds real-time inertial motion directly into the network, allowing the agent to discern ego-motion from external obstacle motion without requiring frame recurrence (LSTM/GRU).

### 2.4 Latent Fusion & Actor-Critic Multi-Head Split

1. **Feature Concatenation**:
   The visual latent vector $\mathbf{h}_{\text{vis}} \in \mathbb{R}^{512}$ and kinematic latent vector $\mathbf{h}_{\text{kin}} \in \mathbb{R}^{64}$ are concatenated along the feature dimension:
   $$\mathbf{h}_{\text{fused\_raw}} = [\mathbf{h}_{\text{vis}} \,\|\, \mathbf{h}_{\text{kin}}] \in \mathbb{R}^{512 + 64} = \mathbb{R}^{576}$$
2. **Fusion Projection**:
   $$\mathbf{z} = \text{ReLU}(\mathbf{W}_{\text{fuse}} \mathbf{h}_{\text{fused\_raw}} + \mathbf{b}_{\text{fuse}})$$
   Where $\mathbf{W}_{\text{fuse}} \in \mathbb{R}^{256 \times 576}$, producing latent state embedding $\mathbf{z} \in \mathbb{R}^{256}$.
3. **Actor (Policy) Head**:
   Maps latent embedding $\mathbf{z}$ to action distribution mean $\boldsymbol{\mu} \in \mathbb{R}^4$:
   $$\mathbf{h}_{\text{actor}} = \text{ReLU}(\mathbf{W}_{\text{act}, 1} \mathbf{z} + \mathbf{b}_{\text{act}, 1}), \quad \mathbf{W}_{\text{act}, 1} \in \mathbb{R}^{128 \times 256}$$
   $$\boldsymbol{\mu} = \tanh(\mathbf{W}_{\text{act}, 2} \mathbf{h}_{\text{actor}} + \mathbf{b}_{\text{act}, 2}), \quad \mathbf{W}_{\text{act}, 2} \in \mathbb{R}^{4 \times 128}$$
   Applying $\tanh$ bounds the mean action vector strictly to $[-1.0, 1.0]^4$.
   The log standard deviation is parameterized as a state-independent trainable parameter:
   $$\text{actor\_log\_std} \in \mathbb{R}^4, \quad \text{initialized to } \log \sigma_{\text{init}} = -0.5 \implies \sigma_{\text{init}} = e^{-0.5} \approx 0.6065$$
4. **Critic (Value) Head**:
   Maps latent embedding $\mathbf{z}$ to scalar baseline value $V(s) \in \mathbb{R}$:
   $$\mathbf{h}_{\text{critic}} = \text{ReLU}(\mathbf{W}_{\text{crit}, 1} \mathbf{z} + \mathbf{b}_{\text{crit}, 1}), \quad \mathbf{W}_{\text{crit}, 1} \in \mathbb{R}^{128 \times 256}$$
   $$V(s) = \mathbf{W}_{\text{crit}, 2} \mathbf{h}_{\text{critic}} + b_{\text{crit}, 2}, \quad \mathbf{W}_{\text{crit}, 2} \in \mathbb{R}^{1 \times 128}$$
   Flattened via `.squeeze(-1)` to produce shape $(B,)$.

### 2.5 Continuous 4D Action Distribution Formulation

The continuous action space comprises four flight control degrees of freedom:
$$\mathbf{a} = [v_x, v_y, v_z, \omega_z]^T \in [-1.0, 1.0]^4$$
- $v_x$: Lateral velocity command (left/right strafe)
- $v_y$: Longitudinal velocity command (forward surge)
- $v_z$: Vertical velocity command (heave/climb/descend)
- $\omega_z$: Yaw rate command (heading rotation rate)

The policy defines an independent diagonal Gaussian distribution over actions:
$$\pi_\theta(\mathbf{a} \mid s) = \mathcal{N}(\boldsymbol{\mu}(s), \boldsymbol{\Sigma}), \quad \boldsymbol{\Sigma} = \text{diag}(\boldsymbol{\sigma}^2) = \text{diag}(\exp(2 \cdot \text{actor\_log\_std}))$$

#### Action Sampling:
Using the reparameterization trick:
$$\mathbf{a} = \boldsymbol{\mu}(s) + \boldsymbol{\sigma} \odot \boldsymbol{\epsilon}, \quad \boldsymbol{\epsilon} \sim \mathcal{N}(\mathbf{0}, \mathbf{I}_4)$$

#### Log Probability Computation:
For an action $\mathbf{a} \in \mathbb{R}^4$:
$$\log \pi_\theta(\mathbf{a} \mid s) = \sum_{i=1}^4 \left[ -\frac{1}{2} \log(2\pi) - \log \sigma_i - \frac{(a_i - \mu_i(s))^2}{2 \sigma_i^2} \right]$$
In `model.py`, line 109:
```python
log_prob = dist.log_prob(action).sum(dim=-1)
```

#### Differential Entropy:
The differential entropy measures exploration stochasticity:
$$H(\pi_\theta(\cdot \mid s)) = \sum_{i=1}^4 \left[ \frac{1}{2} + \frac{1}{2} \log(2\pi \sigma_i^2) \right] = \frac{4}{2}(1 + \log(2\pi)) + \sum_{i=1}^4 \log \sigma_i$$
In `model.py`, line 110:
```python
entropy = dist.entropy().sum(dim=-1)
```

### 2.6 NumPy CPU Fallback Engine & AppLocker Resilience

Enterprise Windows environments with AppLocker policies frequently block C++ DLL dynamic loading (`torch_cuda.dll`, `c10.dll`), throwing `OSError: [WinError 126] The specified module could not be found`. `model.py` detects this at line 18:
```python
except (ImportError, OSError):
    TORCH_AVAILABLE = False
```

When `TORCH_AVAILABLE = False`, a pure Python/NumPy drop-in replacement (`PhysicsInformedActorCritic`) activates:
- **Weights Initialization**: Initialized with fixed seed 42 using Gaussian normal distributions:
  - `w_fc1`: shape $(3136, 512)$
  - `w_kin`: shape $(3, 64)$
  - `w_fuse`: shape $(576, 256)$
  - `w_actor`: shape $(256, 4)$
  - `w_critic`: shape $(256, 1)$
- **Dimensionality Adaptation**: Subsamples visual observation tensor with stride 12 slicing (`visual_obs[:, :, ::12, ::12]`) and zero-pads to dimension 3136:
  ```python
  v_down = visual_obs[:, :, ::12, ::12].reshape(b, -1)
  if v_down.shape[1] < (64 * 7 * 7):
      v_feat = np.pad(v_down, ((0, 0), (0, 64 * 7 * 7 - v_down.shape[1])))[:, :64*7*7]
  ```
- **Forward Activation**: Emulates ReLU via `np.maximum(0, x)` and Actor head via `np.tanh(latent @ self.w_actor)`.
- **Closed-Form Gaussian Probability**: Computes log probability and analytical entropy directly:
  $$\log p(\mathbf{a}) = -0.5 \sum_{i=1}^4 \left( \frac{a_i - \mu_i}{\sigma_i + 10^{-8}} \right)^2$$
  $$H = \sum_{i=1}^4 \left[ 0.5 + 0.5 \log(2\pi \sigma_i^2) \right]$$
- **Mock Interfaces**: Implements `.to(device)`, `.eval()`, `.state_dict()`, and `.load_state_dict()` allowing downstream scripts (`train.py`, `evaluate_and_visualize.py`) to execute without crashing.

---

## 3. Behavioral Cloning & Physics-Based Expert Planner (`pretrain_bc.py`)

### 3.1 Motivation & Exploration Bottleneck Resolution

Sparse-reward 3D navigation in cluttered arenas presents an extreme exploration bottleneck. Random Gaussian policies crash into boundaries or obstacles in $>98\%$ of initial rollouts, producing uniform negative collision penalties ($-20.0$) and preventing value function convergence. 

`pretrain_bc.py` overcomes this by running an algorithmic **Potential Field Navigator** that generates 80,000 demonstration transitions across 300 randomized arena configurations with an 85–95% success rate, training the Actor network in ~5 minutes before PPO begins.

### 3.2 Tangential Obstacle Steering & Potential Field Dynamics

Standard artificial potential fields suffer from **local minima trapping** and **collinear deadlock**: when an obstacle sits directly between the drone and the goal, the repulsive vector $-\nabla U_{\text{rep}}$ directly opposes the attractive vector $-\nabla U_{\text{att}}$, causing the drone to decelerate to zero forward velocity or oscillate backward.

The expert planner in `pretrain_bc.py` eliminates this through **Tangential Obstacle Steering**:
1. Obstacle forces are strictly deflected **laterally** ($v_x$), directing the drone to the left or right flank of the obstacle.
2. The longitudinal velocity command $v_y$ is clamped to a strict positive floor:
   $$v_y \ge 0.35$$
3. By prohibiting negative longitudinal thrust in response to forward obstacles, the drone maintains continuous forward momentum around obstacles, bypassing potential wells.

```
       Goal [0.0, 8.0, 1.5]
                ^
                |   F_att (Forward Pull)
                |
          +-----------+
          | Obstacle  |
          +-----------+
            /       \
   F_lat   /         \   F_lat (Lateral Tangential Deflection)
  (-vx)  <-           -> (+vx)
           \         /
            \       /
             \     /
              Drone [x, y, z]
          (vy >= 0.35 ALWAYS)
```

### 3.3 Mathematical Formulations of Expert Forces

#### 3.3.1 Attractive Goal Force & Forward Surge

Given instantaneous 2D drone position $\mathbf{p}_{\text{drone}, 2D} = (x, y)$ and goal position $\mathbf{p}_{\text{goal}, 2D} = (x_g, y_g) = (0.0, 8.0)$:
$$\Delta \mathbf{p}_{\text{goal}} = \mathbf{p}_{\text{goal}, 2D} - \mathbf{p}_{\text{drone}, 2D} = (x_g - x, y_g - y)$$
$$d_{\text{goal}} = \|\Delta \mathbf{p}_{\text{goal}}\|_2 + 10^{-6}$$
$$\hat{\mathbf{u}}_{\text{goal}} = \frac{\Delta \mathbf{p}_{\text{goal}}}{d_{\text{goal}}}$$

The baseline desired velocities are formulated as:
$$v_{y, \text{desired}} = \min\left(1.0, \, \max\left(0.4, \, \frac{d_{\text{goal}}}{3.0}\right)\right)$$
$$v_{x, \text{desired}} = 0.8 \cdot \hat{\mathbf{u}}_{\text{goal}, x}$$

#### 3.3.2 Tangential Obstacle Deflection

The environment maintains obstacle specifications `env.obstacle_specs[4:]` (excluding the 4 bounding arena walls). For each obstacle $i$ located at $(ox_i, oy_i)$:
$$\Delta x_i = x - ox_i, \quad \Delta y_i = y - oy_i$$
$$d_{\text{obs}, i} = \sqrt{(\Delta x_i)^2 + (\Delta y_i)^2} + 10^{-6}$$
The bounding clearance radius $r_{\text{ext}, i}$ is:
$$r_{\text{ext}, i} = \begin{cases} r_i & \text{if sphere/cylinder} \\ \max(h_{x, i}, h_{y, i}) & \text{if box}\end{cases}$$
The effective clearance distance is:
$$d_{\text{eff}, i} = d_{\text{obs}, i} - r_{\text{ext}, i}$$

If $d_{\text{eff}, i} < 1.8\text{ m}$:
$$F_{\text{rep}, i} = \frac{1.8 - \max(0.05, \, d_{\text{eff}, i})}{1.8} \in [0.0, 1.0]$$
When the obstacle lies ahead of the drone ($\Delta y_i > -0.8$):
$$\text{side}_i = \begin{cases} +1.0 & \text{if } \Delta x_i \ge 0 \quad (\text{drone is to the right of obstacle center}) \\ -1.0 & \text{if } \Delta x_i < 0 \quad (\text{drone is to the left of obstacle center})\end{cases}$$
The repulsive velocity increments accumulate:
$$v_{x, \text{repulse}} \leftarrow v_{x, \text{repulse}} + \text{side}_i \cdot (2.0 \cdot F_{\text{rep}, i})$$
$$v_{y, \text{slowdown}} \leftarrow v_{y, \text{slowdown}} + 0.3 \cdot F_{\text{rep}, i}$$

#### 3.3.3 Monocular Depth Sector Guidance

To supplement Cartesian coordinates with reactive vision, the planner partitions the $84 \times 84$ monocular depth map $\mathbf{D} \in \mathbb{R}^{84 \times 84}$ horizontally into 5 vertical sectors:
$$\mathbf{S}_k = \mathbf{D}[:, \, \lfloor k \cdot 16.8 \rfloor : \lfloor (k+1) \cdot 16.8 \rfloor], \quad k \in \{0, 1, 2, 3, 4\}$$
For each sector, the robust 5th-percentile minimum depth is computed:
$$d_{\text{sec}, k} = \text{Percentile}_{5\%}(\mathbf{S}_k)$$
Spatial grouping yields:
$$d_{\text{left}} = \min(d_{\text{sec}, 0}, d_{\text{sec}, 1}), \quad d_{\text{right}} = \min(d_{\text{sec}, 3}, d_{\text{sec}, 4}), \quad d_{\text{center}} = d_{\text{sec}, 2}$$

If frontal clearance is compromised ($d_{\text{center}} < 1.8\text{ m}$):
$$\text{side}_{\text{vis}} = \begin{cases} -1.0 & \text{if } d_{\text{left}} > d_{\text{right}} \quad (\text{open space on left}) \\ +1.0 & \text{if } d_{\text{right}} \ge d_{\text{left}} \quad (\text{open space on right})\end{cases}$$
$$v_{x, \text{repulse}} \leftarrow v_{x, \text{repulse}} + 1.2 \cdot \text{side}_{\text{vis}}$$
$$v_{y, \text{slowdown}} \leftarrow v_{y, \text{slowdown}} + 0.3$$

#### 3.3.4 Arena Boundary Clamping & Repulsion

The indoor flight corridor extends laterally across $x \in [-4.6, 4.6]$. The expert establishes a safety buffer at $|x| = 3.2\text{ m}$:
$$v_{x, \text{wall}} = \begin{cases} -2.5 \cdot (x - 3.2) & \text{if } x > 3.2 \\ +2.5 \cdot (-3.2 - x) & \text{if } x < -3.2 \\ 0.0 & \text{otherwise}\end{cases}$$
$$v_{x, \text{repulse}} \leftarrow v_{x, \text{repulse}} + v_{x, \text{wall}}$$

Total lateral and longitudinal commands are merged:
$$v_x = \text{clip}(v_{x, \text{desired}} + v_{x, \text{repulse}}, \, -1.0, \, 1.0)$$
$$v_y = \text{clip}(v_{y, \text{desired}} - v_{y, \text{slowdown}}, \, 0.35, \, 1.0)$$

#### 3.3.5 Proportional Altitude Holding Force

To maintain an optimal flight ceiling midway between the floor ($z=0$) and ceiling ($z=3.5$) with zero roof collisions:
$$z^* = 1.5\text{ m}$$
$$e_z = z^* - z_{\text{drone}}$$
$$v_z = \text{clip}(2.0 \cdot e_z, \, -0.6, \, 0.6)$$
With yaw rate $\omega_z = 0.0$, the final expert action vector is:
$$\mathbf{a}_{\text{expert}} = [v_x, v_y, v_z, 0.0]^T \in [-1.0, 1.0]^4$$

### 3.4 Demonstration Collection & Buffer Architecture

The function `collect_demonstrations(args)` iterates across `args.n_demo_envs` (default 300) random seeds:
- Each environment instance executes `expert_action(env)` up to `args.demo_max_steps` (400 steps).
- Visual observations $\mathbf{o}_{\text{vis}} \in \mathbb{R}^{5 \times 84 \times 84}$, kinematic velocity $\mathbf{o}_{\text{vel}} \in \mathbb{R}^3$, and expert actions $\mathbf{a}_{\text{expert}} \in \mathbb{R}^4$ are stored in lists.
- Halts when total steps reach `args.target_demo_steps` (80,000 transitions).
- Compressed onto disk as `bc_demos.npz` containing arrays:
  - `"visual"`: $(N, 5, 84, 84)$, `dtype=np.float32`
  - `"velocity"`: $(N, 3)$, `dtype=np.float32`
  - `"action"`: $(N, 4)$, `dtype=np.float32`

### 3.5 Supervised Imitation Learning Loop & Optimization

The imitation learning loop (`train_bc`) minimizes the Mean Squared Error (MSE) between the Actor network's deterministic mean action $\boldsymbol{\mu}_\theta(s_{\text{vis}}, s_{\text{vel}})$ and the expert command $\mathbf{a}_{\text{expert}}$:

$$\mathcal{L}_{\text{BC}}(\theta) = \frac{1}{B} \sum_{i=1}^B \|\boldsymbol{\mu}_\theta(s_{\text{vis}, i}, s_{\text{vel}, i}) - \mathbf{a}_{\text{expert}, i}\|_2^2$$

#### Optimization Pipeline:
- **Optimizer**: Adam with learning rate $\eta = 3 \times 10^{-4}$ and weight decay $\lambda = 10^{-5}$.
- **Learning Rate Schedule**: Cosine Annealing over $E = 60$ epochs:
  $$\eta_e = \frac{\eta_{\text{base}}}{2} \left(1 + \cos\left(\frac{e \pi}{E}\right)\right)$$
- **Automatic Mixed Precision (AMP)**: `torch.amp.autocast("cuda")` and `torch.amp.GradScaler("cuda")` perform forward/loss evaluation in FP16, scaling gradients to prevent underflow.
- **Gradient Clipping**: Strict $L_2$-norm threshold $\|\mathbf{g}\|_2 \le 1.0$ via `torch.nn.utils.clip_grad_norm_`.
- **Validation**: `validate_model(args)` evaluates 3 fixed seeds (42, 142, 242) post-training, printing validation reward and goal arrival rates.

---

## 4. Proximal Policy Optimization (PPO) Training Pipeline (`train.py`)

### 4.1 PPO Mathematical Formulation & Clipped Surrogate Objective

PPO (Schulman et al., 2017) stabilizes continuous control policy updates by constraining policy shifts within an $\epsilon$-neighborhood of the sampling policy $\pi_{\theta_{\text{old}}}$.

The probability ratio is defined as:
$$r_t(\theta) = \frac{\pi_\theta(\mathbf{a}_t \mid s_t)}{\pi_{\theta_{\text{old}}}(\mathbf{a}_t \mid s_t)} = \exp\left( \log \pi_\theta(\mathbf{a}_t \mid s_t) - \log \pi_{\theta_{\text{old}}}(\mathbf{a}_t \mid s_t) \right)$$

The clipped surrogate objective function is:
$$L^{\text{CLIP}}(\theta) = \hat{\mathbb{E}}_t \left[ \min\left( r_t(\theta) \hat{A}_t, \, \text{clip}(r_t(\theta), 1 - \epsilon, 1 + \epsilon) \hat{A}_t \right) \right]$$

In `train.py` (lines 503–505), gradient descent minimizes the negative surrogate objective:
```python
surr1 = ratio * adv_b
surr2 = torch.clamp(ratio, 1 - args.clip_eps, 1 + args.clip_eps) * adv_b
pl    = -torch.min(surr1, surr2).mean()
```

When advantage $\hat{A}_t > 0$, the objective increases as $r_t(\theta)$ increases, but clips at $1 + \epsilon$. When advantage $\hat{A}_t < 0$, it clips at $1 - \epsilon$, preventing destructive policy collapse from overshooting.

### 4.2 Generalized Advantage Estimation (GAE-$\lambda$)

Advantages quantify the relative benefit of taking action $\mathbf{a}_t$ over the expected state value $V(s_t)$. `compute_gae` computes Generalized Advantage Estimation directly on GPU tensors across $T$ steps and $N$ environments:

For each time step $t \in [T-1, 0]$ (in reverse chronological order):
$$\delta_t^V = r_t + \gamma V(s_{t+1}) (1 - d_t) - V(s_t)$$
$$\hat{A}_t^{\text{GAE}(\gamma, \lambda)} = \delta_t^V + (\gamma \lambda) (1 - d_t) \hat{A}_{t+1}^{\text{GAE}(\gamma, \lambda)}$$
Where:
- $\gamma = 0.99$: Discount factor for future rewards.
- $\lambda = 0.95$: Exponential GAE decay parameter balancing bias vs variance.
- $d_t \in \{0, 1\}$: Episode termination indicator (`terminated | truncated`). When $d_t = 1$, future returns are masked.
- $V(s_{T})$: Bootstrapped next-state value computed via Critic forward pass `model.get_value(nxt_vis, nxt_vel)`.

Target returns for value function training are computed as:
$$R_t = \hat{A}_t^{\text{GAE}} + V(s_t)$$

#### Advantage Normalization:
Before mini-batch optimization, advantages are normalized across the entire rollout batch $(T \times N)$:
$$\hat{A}_t \leftarrow \frac{\hat{A}_t - \bar{A}}{\sigma_A + 10^{-8}}$$

### 4.3 Value Function Loss & Policy Entropy Regularization

1. **Critic Squared-Error Value Loss**:
   $$L^{\text{VF}}(\theta) = \frac{1}{2} \hat{\mathbb{E}}_t \left[ \left( V_\theta(s_t) - R_t \right)^2 \right]$$
   In code (line 506):
   ```python
   vl = 0.5 * ((new_val - returns[idx]) ** 2).mean()
   ```
2. **Policy Entropy Regularization**:
   $$S[\pi_\theta] = \hat{\mathbb{E}}_t \left[ H(\pi_\theta(\cdot \mid s_t)) \right]$$
   In code (line 507):
   ```python
   ent = entropy.mean()
   ```
3. **Total Composite Loss**:
   $$\mathcal{L}_{\text{total}}(\theta) = L^{\text{CLIP}}(\theta) + c_1 L^{\text{VF}}(\theta) - c_2 S[\pi_\theta]$$
   Where $c_1 = \text{vf\_coef} = 0.5$ and $c_2 = \text{ent\_coef} = 0.01$. In code (line 508):
   ```python
   loss = pl + args.vf_coef * vl - args.ent_coef * ent
   ```

### 4.4 Hyperparameter Specifications & Tuning Dimensions

The exact PPO hyperparameters defined in `train.py` are summarized below:

| Hyperparameter | CLI Argument | Type | Default Value | Physical & Mathematical Function |
|---|---|---|---|---|
| Total Timesteps | `--total-timesteps` | `int` | `100_000` | Total environment interaction steps before training concludes |
| Parallel Envs | `--n-envs` | `int` | `8` | Number of concurrent `SubprocVecEnv` worker processes |
| Rollout Steps | `--n-steps` | `int` | `512` | Horizon length collected per worker per PPO update cycle |
| Mini-Batch Size | `--batch-size` | `int` | `512` | Batch slice sampled per optimization sub-step ($4096 / 512 = 8$ batches) |
| Update Epochs | `--update-epochs` | `int` | `10` | Full passes over rollout buffer ($10 \times 8 = 80$ gradient steps/update) |
| Learning Rate | `--learning-rate` | `float` | `3e-4` | Initial Adam learning rate with epsilon $10^{-5}$ |
| Discount Factor | `--gamma` | `float` | `0.99` | Long-term reward horizon discount factor ($\approx 100$ step horizon) |
| GAE Lambda | `--gae-lambda` | `float` | `0.95` | Bias-variance trade-off coefficient for advantage estimates |
| PPO Clip Epsilon | `--clip-eps` | `float` | `0.2` | Surrogate objective ratio clipping boundary $[0.8, 1.2]$ |
| Value Loss Coef | `--vf-coef` | `float` | `0.5` | Scalar weight $c_1$ for Critic MSE loss |
| Entropy Coef | `--ent-coef` | `float` | `0.01` | Scalar weight $c_2$ encouraging action distribution exploration |
| Max Episode Steps | `--max-steps` | `int` | `500` | Truncation limit per episode ($500 / 24\text{ Hz} \approx 20.8\text{ s}$ flight) |
| Seed | `--seed` | `int` | `42` | Global deterministic random seed for NumPy, PyTorch, and PyBullet |
| Baseline Checkpoint | `--checkpoint` | `str` | `"best_model.pt"` | Pre-trained Behavioral Cloning model weights to load |
| Live Dashboard | `--dashboard` / `--gui` | `flag` | `False` | Renders OpenCV 3-Panel real-time visualization window |

### 4.5 Vectorized Execution: `SubprocVecEnv` vs `SingleEnv`

`train.py` provides two distinct environment orchestration classes:

1. **`SubprocVecEnv`**:
   - Manages $N$ subprocesses using `multiprocessing.Process` with Windows `spawn` start method (`mp.set_start_method("spawn", force=True)`).
   - Inter-process communication (IPC) uses duplex pipes `mp.Pipe()`.
   - Worker function `_env_worker(conn, seed, max_steps)` operates headless (`os.environ["PYBULLET_EGL"] = "1"`).
   - **Auto-Reset Pattern**: When an environment terminates (`terminated | truncated`), `_env_worker` immediately executes `env.reset()`, returning the new initial observation to the parent process without stalling other workers.
   - Batch observations are stacked along dimension 0:
     $$\mathbf{o}_{\text{vis}} \in \mathbb{R}^{N \times 5 \times 84 \times 84}, \quad \mathbf{o}_{\text{vel}} \in \mathbb{R}^{N \times 3}$$
2. **`SingleEnv`**:
   - Zero-IPC wrapper for single-environment execution (`n_envs == 1`).
   - Runs `IndoorDroneNavEnv` synchronously in the main thread.
   - Eliminates OS pipe serialization latency, enabling rapid debugging episodes ($\sim 0.5\text{ s}$ per episode).

### 4.6 Hardware Accelerator Optimizations (AMP FP16, TF32, `torch.compile`)

To saturate modern GPU hardware (e.g., NVIDIA RTX 5060 Blackwell sm_120, Ada Lovelace sm_89, Ampere sm_86):
- **TensorFloat-32 (TF32)**:
  `torch.backends.cuda.matmul.allow_tf32 = True` and `torch.backends.cudnn.allow_tf32 = True` accelerate matrix multiplications and convolutions by using 19-bit TF32 precision on Tensor Cores with zero loss in training stability.
- **Kernel Auto-Tuning**:
  `torch.backends.cudnn.benchmark = True` benchmarks algorithms on initial execution to lock in optimal convolution kernels for fixed $(5, 84, 84)$ tensors.
- **Automatic Mixed Precision (AMP)**:
  During both rollout inference and PPO optimization:
  ```python
  with torch.amp.autocast("cuda"):
      actions_t, log_probs_t, _, values_t = model.get_action_and_value(vis_t, vel_t)
  ```
  Gradients are scaled via `scaler = torch.amp.GradScaler("cuda")`.
- **Fast Gradient Zeroing**:
  `optimizer.zero_grad(set_to_none=True)` deallocates memory pointers rather than overwriting buffers with zeros, reducing memory bandwidth usage.
- **PyTorch Inductor Compilation**:
  `model = torch.compile(model, mode="reduce-overhead")` applies operator fusion and eliminates Python overhead via CUDA graphs.

### 4.7 Rollout Buffering & State Serialization Logic

The class `RolloutBuffer` aggregates transitions into host memory:
- Buffer capacity: $T \times N = 512 \times 8 = 4096$ transitions per rollout.
- In `get_tensors()`, arrays are concatenated and transferred to GPU in a single operation:
  ```python
  def to_gpu(arr):
      return torch.tensor(np.concatenate(arr, axis=0), dtype=torch.float32, device=self.device)
  ```
- **Safe Checkpoint Unwrapping**:
  When `torch.compile` is active, the model is wrapped in an `OptimizedModule`. `train.py` safely unwraps this before saving to prevent deserialization errors downstream:
  ```python
  state = (model._orig_mod if hasattr(model, "_orig_mod") else model).state_dict()
  torch.save(state, "best_model.pt")
  ```

---

## 5. Explainable AI (XAI) Engine (`explainability.py`)

### 5.1 Dual-Input Attribution Framework

Traditional XAI libraries assume a single input tensor. However, `PhysicsInformedActorCritic` accepts two input tensors: visual observation `vis_tensor` $(1, 5, 84, 84)$ and kinematic velocity `vel_tensor` $(1, 3)$. 

`DroneXAIEngine` handles this signature using input tuples:
```python
vis_tensor.requires_grad = True
inputs = (vis_tensor, vel_tensor)
```
Gradients are propagated back through the fused latent layers into both branches, with visual attribution isolated via `attributions[0]`.

### 5.2 Vanilla Saliency vs Integrated Gradients (IG) Formulations

#### 5.2.1 Captum Vanilla Saliency (Simonyan et al., 2013):
Computes the instantaneous gradient of target action $k$ with respect to visual input $\mathbf{x}$:
$$A_{\text{Saliency}}(\mathbf{x}) = \left| \frac{\partial \mu_k(\mathbf{x}, \mathbf{v})}{\partial \mathbf{x}} \right|$$
- **Target**: `target_action_idx = 0` ($v_x$, lateral obstacle evasion action).
- **Execution Cost**: Requires a single backward pass ($\sim 1.5\text{ ms}$ on GPU).
- **Application**: Real-time 30+ FPS live dashboard streaming during training and inference.

#### 5.2.2 Captum Integrated Gradients (Sundararajan et al., 2017):
Satisfies the fundamental axioms of **Completeness** and **Implementation Invariance** by integrating gradients along a straight-line path from a neutral baseline $\mathbf{x}'$ to the input $\mathbf{x}$:
$$A_i^{\text{IG}}(\mathbf{x}, \mathbf{x}') = (x_i - x_i') \times \int_{0}^{1} \frac{\partial F(\mathbf{x}' + \alpha (\mathbf{x} - \mathbf{x}'))}{\partial x_i} d\alpha$$

In `DroneXAIEngine`, the path integral is approximated via a Riemann summation over $m = 30$ interpolation steps:
$$A_i^{\text{IG}}(\mathbf{x}, \mathbf{x}') \approx (x_i - x_i') \times \frac{1}{m} \sum_{k=1}^m \frac{\partial F\left(\mathbf{x}' + \frac{k}{m}(\mathbf{x} - \mathbf{x}')\right)}{\partial x_i}$$
- **Baselines**: All-zero tensors:
  $$\mathbf{x}' = \mathbf{0}_{1 \times 5 \times 84 \times 84}, \quad \mathbf{v}' = \mathbf{0}_{1 \times 3}$$
- **Execution Cost**: Requires $m=30$ backward passes ($\sim 45\text{ ms}$ on GPU).
- **Application**: Offline evaluation, post-training diagnostic audits, and safety certification.

#### 5.2.3 Channel Max-Pooling & Normalization:
The visual attribution tensor has shape $(5, 84, 84)$ across 3 RGB channels and 2 optical flow channels. The 2D spatial attribution intensity is extracted via max-pooling across channels:
$$A_{2D}(u, v) = \max_{c \in \{0, \dots, 4\}} |A(c, u, v)|$$
Normalized to the unit interval $[0.0, 1.0]$:
$$A_{\text{norm}}(u, v) = \frac{A_{2D}(u, v) - \min A_{2D}}{\max A_{2D} - \min A_{2D} + 10^{-8}}$$

### 5.3 Fallback Edge & Motion Gradient Engine

When running under AppLocker restrictions where PyTorch or Captum are blocked, `DroneXAIEngine` activates a classical spatial-motion gradient fallback:
1. Computes spatial image gradients using Sobel operators ($3 \times 3$ kernel) on the luminance channel:
   $$G_x = |\text{Sobel}_x(\mathbf{I}_{\text{gray}})|, \quad G_y = |\text{Sobel}_y(\mathbf{I}_{\text{gray}})|$$
2. Calculates optical flow Euclidean magnitude from channels 3 and 4:
   $$M_{\text{flow}}(u, v) = \sqrt{u_{\text{flow}}(u, v)^2 + v_{\text{flow}}(u, v)^2}$$
3. Combines features with motion weighting:
   $$A_{2D}(u, v) = G_x(u, v) + G_y(u, v) + 1.5 \cdot M_{\text{flow}}(u, v)$$

### 5.4 High-Definition Thermal Vision Pipeline

The method `generate_heatmap_overlay` renders ultra-crisp visual explanations by executing a 7-stage image synthesis pipeline:

```
2D Saliency (84x84)                            RGB Frame (84x84)
       |                                              |
       v                                              v
[Bicubic Upscale to (390,390)]                 [Bicubic Upscale to (390,390)]
       |                                              |
       v                                              v
[Gaussian Smoothing (13x13, sigma=3.0)]        [RGB -> BGR Base Canvas]
       |                                              |
       v                                              |
[Gamma Contrast Boost: x^0.7]                         |
       |                                              |
       +--------------------+                         |
       |                    |                         |
       v                    v                         |
[Google TURBO Map]    [Adaptive Alpha]                |
 (Thermal Colors)     (Transparent BG)                |
       \                    /                         |
        \                  /                          |
         v                v                           |
       [Alpha-Blended Thermal Map] <------------------+
                     |
                     v
       [Neon Peak Contours (x > 0.65)]
                     |
                     v
       Final High-Definition Overlay (390x390x3)
```

#### 5.4.1 Bicubic Super-Resolution & Spatial Smoothing
1. Upscales base image and attribution map from $84 \times 84$ to high-definition $390 \times 390$ resolution using bicubic interpolation (`cv2.INTER_CUBIC`), fitting a 2D cubic polynomial over a $4 \times 4$ pixel neighborhood.
2. Applies 2D Gaussian kernel smoothing:
   $$G(x, y) = \frac{1}{2\pi \sigma^2} \exp\left( -\frac{x^2 + y^2}{2\sigma^2} \right)$$
   Using window size $13 \times 13$ and $\sigma = 3.0$ (`cv2.GaussianBlur(hd_attr, (13, 13), 3.0)`). This eliminates grid blockiness and establishes continuous energy contours. Post-renormalized to $[0.0, 1.0]$.

#### 5.4.2 Non-Linear Gamma Contrast Boost
Applies a non-linear power-law gamma transformation ($\gamma = 0.7$):
$$A_{\text{boosted}}(u, v) = \left( A_{\text{smooth}}(u, v) \right)^{0.7}$$
Because $\gamma < 1.0$, intermediate attribution values are boosted outward toward the upper spectrum, accentuating subtle obstacle contours while suppressing zero-energy background.

#### 5.4.3 Google TURBO Perceptual Colormap Integration
Quantizes $A_{\text{boosted}}$ to 8-bit unsigned integer $[0, 255]$ and applies `cv2.COLORMAP_TURBO`:
- Google TURBO provides a smooth, perceptually uniform thermal spectrum (deep blue $\to$ cyan $\to$ green $\to$ yellow $\to$ red).
- Eliminates false boundary artifacts and color banding present in legacy JET colormaps.

#### 5.4.4 Adaptive Alpha Masking Dynamics
To prevent the colormap from occluding the visual environment, transparency scales dynamically with saliency intensity:
$$\alpha(u, v) = \text{clip}\left( \frac{A_{\text{boosted}}(u, v) - 0.10}{0.85}, \, 0.0, \, 1.0 \right) \times \alpha_{\max}$$
Where $\alpha_{\max} = 0.75$.
- Background pixels ($A < 0.10$) have $\alpha = 0.0$, leaving camera pixels completely transparent.
- Critical obstacles ($A > 0.60$) transition to $\alpha \to 0.75$, glowing in thermal red/yellow.
Per-pixel alpha blending is performed across 3 color channels:
$$I_{\text{overlay}}(u, v) = (1 - \alpha(u, v)) \cdot I_{\text{BGR}}(u, v) + \alpha(u, v) \cdot I_{\text{TURBO}}(u, v)$$

#### 5.4.5 Neon Peak-Saliency Contour Extraction
Isolates the top salient regions using a hard binary threshold:
$$M_{\text{peak}}(u, v) = \mathbb{I}\left( A_{\text{boosted}}(u, v) > 0.65 \right) \times 255$$
Boundary contours are vectorized using Suzuki & Abe's border following algorithm (`cv2.findContours(..., cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)`).
Contours are rendered on top of the overlay as 1-pixel anti-aliased rings in glowing neon yellow/cyan (BGR `(255, 255, 0)`):
```python
cv2.drawContours(overlay, contours, -1, (255, 255, 0), 1, cv2.LINE_AA)
```

### 5.5 Spatial IoU Explanation Fidelity Metric

To evaluate whether the neural network's visual attention aligns with actual physical obstacles rather than spurious background textures, `compute_explanation_fidelity` computes the **Spatial Intersection-over-Union (IoU)** between saliency heatmaps and ground-truth PyBullet depth maps:

1. **Saliency Thresholding**:
   Extracts the 85th percentile intensity threshold:
   $$\tau_{\text{attr}} = \text{Percentile}_{85\%}(A_{2D})$$
   $$M_{\text{attr}}(u, v) = \begin{cases} 1 & \text{if } A_{2D}(u, v) \ge \tau_{\text{attr}} \\ 0 & \text{otherwise}\end{cases}$$
2. **Physical Obstacle Masking**:
   Identifies proximate obstacles from depth map $\mathbf{D} \in \mathbb{R}^{84 \times 84}$ within collision hazard distance ($1.5\text{ m}$):
   $$M_{\text{obs}}(u, v) = \begin{cases} 1 & \text{if } \mathbf{D}(u, v) < 1.5\text{ m} \\ 0 & \text{otherwise}\end{cases}$$
3. **Spatial IoU Computation**:
   $$\text{Intersection} = \sum_{u=1}^{84} \sum_{v=1}^{84} \left( M_{\text{attr}}(u, v) \land M_{\text{obs}}(u, v) \right)$$
   $$\text{Union} = \sum_{u=1}^{84} \sum_{v=1}^{84} \left( M_{\text{attr}}(u, v) \lor M_{\text{obs}}(u, v) \right)$$
   $$\text{Spatial IoU} = \frac{\text{Intersection}}{\text{Union} + 10^{-6}}$$
   If $\text{Union} = 0$, returns $1.0$ if $\text{Intersection} = 0$, else $0.0$.

A high Spatial IoU score ($> 0.60$) quantitatively certifies that policy actions are driven by genuine physical obstacles rather than visual artifacts.

---

## 6. Granular Class, Method, and Hyperparameter Reference Matrix

The following matrix documents every class, method, tensor signature, and hyperparameter across the four audited modules:

| Module | Class / Function | Method / Parameter | Signature / Shape | Return Type / Description |
|---|---|---|---|---|
| `model.py` | `PhysicsInformedActorCritic` | `__init__` | `(action_dim=4, log_std_init=-0.5)` | PyTorch Dual-Input Actor-Critic network instance |
| `model.py` | `PhysicsInformedActorCritic` | `conv` | `in=5, out=64, layers=3` | NatureCNN visual feature extractor ($5 \to 32 \to 64 \to 64$) |
| `model.py` | `PhysicsInformedActorCritic` | `visual_fc` | `(3136 -> 512)` | Linear projection to 512-dim visual latent |
| `model.py` | `PhysicsInformedActorCritic` | `kinematic_fc` | `(3 -> 64)` | Linear projection of $(v_x, v_y, v_z)$ to 64-dim kinematic latent |
| `model.py` | `PhysicsInformedActorCritic` | `fusion_fc` | `(576 -> 256)` | Shared fused latent feature space |
| `model.py` | `PhysicsInformedActorCritic` | `actor_mean` | `(256 -> 128 -> 4)` | Outputs continuous mean action $\boldsymbol{\mu} \in [-1, 1]^4$ |
| `model.py` | `PhysicsInformedActorCritic` | `actor_log_std` | `(4,)` parameter | Trainable log standard deviation vector (init $-0.5$) |
| `model.py` | `PhysicsInformedActorCritic` | `critic` | `(256 -> 128 -> 1)` | State-value estimator head $V(s)$ |
| `model.py` | `PhysicsInformedActorCritic` | `extract_features` | `(vis: (B,5,84,84), vel: (B,3))` | `torch.Tensor` of shape $(B, 256)$ |
| `model.py` | `PhysicsInformedActorCritic` | `forward` | `(vis, vel)` | `torch.Tensor` of shape $(B, 4)$ (deterministic action mean) |
| `model.py` | `PhysicsInformedActorCritic` | `get_value` | `(vis, vel)` | `torch.Tensor` of shape $(B,)$ (state value $V(s)$) |
| `model.py` | `PhysicsInformedActorCritic` | `get_action_and_value`| `(vis, vel, action=None)` | Tuple: `(action (B,4), log_prob (B,), entropy (B,), value (B,))` |
| `model.py` | `PhysicsInformedActorCritic` (NumPy) | `extract_features` | `(vis: (B,5,84,84), vel: (B,3))` | `np.ndarray` of shape $(B, 256)$ using stride-12 subsampling |
| `model.py` | `PhysicsInformedActorCritic` (NumPy) | `get_action_and_value`| `(vis, vel, action=None)` | Pure NumPy Gaussian evaluation and analytical entropy |
| `pretrain_bc.py` | Standalone Function | `expert_action` | `(env: IndoorDroneNavEnv)` | `np.ndarray` of shape $(4,)$ with tangential steering |
| `pretrain_bc.py` | Standalone Function | `collect_demonstrations` | `(args)` | Dict of arrays: `"visual"` $(N,5,84,84)$, `"velocity"` $(N,3)$, `"action"` $(N,4)$ |
| `pretrain_bc.py` | Standalone Function | `train_bc` | `(demos: dict, args)` | Trains model via Adam + Cosine Annealing, returns model |
| `pretrain_bc.py` | Standalone Function | `validate_model` | `(args)` | Evaluates seeds 42, 142, 242 over 300 steps |
| `train.py` | Standalone Function | `get_device` | `()` | Strict CUDA check, sets TF32 and cuDNN benchmark flags |
| `train.py` | Standalone Function | `_env_worker` | `(conn, seed, max_steps)` | Subprocess loop handling headless simulation and auto-resets |
| `train.py` | `SubprocVecEnv` | `__init__` | `(n_envs=8, base_seed=42, max_steps=500)` | Launches $N$ environment subprocesses via `mp.Pipe` |
| `train.py` | `SubprocVecEnv` | `step` | `(actions: (N, 4))` | Synchronous multi-process dispatch, returns batched tuples |
| `train.py` | `RolloutBuffer` | `add` | `(vis, vel, act, lp, rew, done, val)` | Stores rollout step transitions |
| `train.py` | `RolloutBuffer` | `get_tensors` | `()` | Returns GPU tensors of shape $(T \cdot N, \dots)$ |
| `train.py` | `SingleEnv` | `step` | `(actions)` | Zero-IPC single process environment wrapper |
| `train.py` | Standalone Function | `compute_gae` | `(rewards, values, dones, next_values, gamma, lam)` | Returns GPU tensors: `advantages (T*N,)`, `returns (T*N,)` |
| `train.py` | Standalone Function | `train_ppo` | `(args)` | Executes full PPO loop with AMP FP16 and live dashboard |
| `explainability.py`| `DroneXAIEngine` | `__init__` | `(model, device="cpu")` | Initializes Captum `Saliency` and `IntegratedGradients` |
| `explainability.py`| `DroneXAIEngine` | `compute_attribution` | `(vis: (5,84,84), vel: (3), target=0, mode="saliency")` | Returns normalized 2D attribution map $(84, 84)$ in $[0, 1]$ |
| `explainability.py`| `DroneXAIEngine` | `generate_heatmap_overlay` | `(rgb: (84,84,3), attr: (84,84), target=(390,390))` | High-definition Google TURBO overlay with neon contours |
| `explainability.py`| `DroneXAIEngine` | `compute_explanation_fidelity` | `(attr: (84,84), depth: (84,84), dist_thresh=1.5)` | Spatial IoU float score between top saliency and obstacles |

---

## Summary of Architectural Findings & Key Strengths

1. **Information-Dense State Representation**: Integrating 2-channel Farneback optical flow into the visual tensor allows the NatureCNN encoder to directly observe motion parallax and looming obstacle expansion without recurrent temporal state tracking.
2. **Deadlock-Free Expert Pre-Training**: Tangential Obstacle Steering in `pretrain_bc.py` solves the traditional potential field local minimum problem by prohibiting backward thrust ($v_y \ge 0.35$) and deflecting laterally, producing demonstration data with $>85\%$ task success.
3. **High-Throughput PPO Pipeline**: Vectorized execution via `SubprocVecEnv`, GPU-native advantage computation, TensorFloat-32 arithmetic, AMP FP16, and PyTorch Inductor kernel compilation (`torch.compile(mode="reduce-overhead")`) saturate modern NVIDIA GPUs.
4. **Physically Grounded XAI**: `DroneXAIEngine` moves beyond unverified visual heatmaps by pairing Captum attributions with the quantitative Spatial IoU metric, grounding neural attention in physical collision geometry.
