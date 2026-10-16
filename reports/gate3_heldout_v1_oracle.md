# Stop, Hover & Re-Route (SHR) Drone Safety Shield Benchmark Report

**Date:** 2026-10-16T11:27:52Z  
**Seeds:** `5000-5049` (50 episodes)  
**Checkpoint:** `best_model_baseline.pt`  

## Executive Summary & Comparison Table

| Metric | Baseline (OFF) | Shield ON (Oracle) | Shield ON (Camera) | Target |
|---|:---:|:---:|:---:|:---:|
| **Success Rate (95% CI)** | — |  86.0% [73.8%, 93.0%] (43/50) | — | **>= 85.0%** |
| **Total Collision Rate** | — |   0.0% [ 0.0%,  7.1%] (0/50) | — | **<= 2.0%** |
| Obstacle Collisions | — |   0.0% [ 0.0%,  7.1%] (0/50) | — | — |
| Wall OOB Collisions | — |   0.0% [ 0.0%,  7.1%] (0/50) | — | — |
| Timeout Rate | — |  14.0% [ 7.0%, 26.2%] (7/50) | — | **<= 5.0%** |
| **Mean Reward** | — +/- — | -516.62 +/- 791.32 | — +/- — | — |
| **Mean Min Clearance** | — m | 0.39 m | — m | — |
| **Mean Episode Steps** | — | 281.4 | — | — |
| **Standoff Distance** | N/A | 1.99 m | — m | **>= 0.45 m** |
| **Step Overhead (Baseline Succ)** | Baseline | —% | —% | **<= 15.0%** |

## Acceptance Criteria Audit

## Crash Forensics Log

Total non-success episodes analyzed: **7**

### [Seed 5005] Configuration: Shield ON (oracle) — Outcome: `TIMEOUT`
- **Steps:** 500 | **Reward:** -2506.35 | **Min Clearance:** 0.334 m
- **Diagnostic Cause:** Exceeded maximum episode limit (500 steps) without reaching goal.
- **Last 5 Control Steps Telemetry:**
  ```
  Step | Pos [x, y, z]           | Vel [vx, vy, vz]        | Speed | Clr   | State    | Action Executed
  -----+-------------------------+-------------------------+-------+-------+----------+----------------
   496 | [-0.17,  1.26, 1.50]    | [ 0.00, -0.80, -0.00]   |  0.80 |  0.52 | SCAN     | [0.00, -0.27, -0.00]
   497 | [-0.23,  1.28, 1.50]    | [-1.50,  0.40, -0.00]   |  1.55 |  0.64 | REROUTE  | [-0.50, 0.13, -0.00]
   498 | [-0.29,  1.30, 1.50]    | [-1.50,  0.40, -0.00]   |  1.55 |  0.59 | REROUTE  | [-0.50, 0.13, -0.00]
   499 | [-0.35,  1.31, 1.50]    | [-1.50,  0.40, -0.00]   |  1.55 |  0.59 | REROUTE  | [-0.50, 0.13, -0.00]
   500 | [-0.42,  1.33, 1.50]    | [-1.50,  0.40, -0.00]   |  1.55 |  0.64 | REROUTE  | [-0.50, 0.13, -0.00]
  ```

### [Seed 5013] Configuration: Shield ON (oracle) — Outcome: `TIMEOUT`
- **Steps:** 500 | **Reward:** -2371.42 | **Min Clearance:** 0.251 m
- **Diagnostic Cause:** Exceeded maximum episode limit (500 steps) without reaching goal.
- **Last 5 Control Steps Telemetry:**
  ```
  Step | Pos [x, y, z]           | Vel [vx, vy, vz]        | Speed | Clr   | State    | Action Executed
  -----+-------------------------+-------------------------+-------+-------+----------+----------------
   496 | [ 1.68,  1.70, 1.50]    | [ 0.00, -0.80, -0.00]   |  0.80 |  0.86 | RETREAT  | [0.00, -0.27, -0.00]
   497 | [ 1.68,  1.67, 1.50]    | [ 0.00, -0.80, -0.00]   |  0.80 |  0.70 | SCAN     | [0.00, -0.27, -0.00]
   498 | [ 1.62,  1.73, 1.50]    | [-1.50,  1.50, -0.00]   |  2.12 |  0.88 | REROUTE  | [-0.50, 0.50, -0.00]
   499 | [ 1.56,  1.80, 1.50]    | [-1.32,  1.60, -0.00]   |  2.07 |  0.62 | REROUTE  | [-0.44, 0.53, -0.00]
   500 | [ 1.52,  1.86, 1.50]    | [-0.98,  1.60, -0.00]   |  1.88 |  0.55 | REROUTE  | [-0.33, 0.53, -0.00]
  ```

### [Seed 5014] Configuration: Shield ON (oracle) — Outcome: `TIMEOUT`
- **Steps:** 500 | **Reward:** -2279.84 | **Min Clearance:** 0.446 m
- **Diagnostic Cause:** Exceeded maximum episode limit (500 steps) without reaching goal.
- **Last 5 Control Steps Telemetry:**
  ```
  Step | Pos [x, y, z]           | Vel [vx, vy, vz]        | Speed | Clr   | State    | Action Executed
  -----+-------------------------+-------------------------+-------+-------+----------+----------------
   496 | [-1.21, -1.19, 1.50]    | [ 0.00, -0.80, 0.00]    |  0.80 |  0.55 | RETREAT  | [0.00, -0.27, 0.00]
   497 | [-1.21, -1.22, 1.50]    | [ 0.00, -0.80, 0.00]    |  0.80 |  0.59 | RETREAT  | [0.00, -0.27, 0.00]
   498 | [-1.21, -1.25, 1.50]    | [ 0.00, -0.80, 0.00]    |  0.80 |  0.49 | RETREAT  | [0.00, -0.27, 0.00]
   499 | [-1.21, -1.28, 1.50]    | [ 0.00, -0.80, 0.00]    |  0.80 |  0.65 | RETREAT  | [0.00, -0.27, 0.00]
   500 | [-1.21, -1.32, 1.50]    | [ 0.00, -0.80, 0.00]    |  0.80 |  0.68 | SCAN     | [0.00, -0.27, 0.00]
  ```

### [Seed 5018] Configuration: Shield ON (oracle) — Outcome: `TIMEOUT`
- **Steps:** 500 | **Reward:** -3219.57 | **Min Clearance:** 0.324 m
- **Diagnostic Cause:** Exceeded maximum episode limit (500 steps) without reaching goal.
- **Last 5 Control Steps Telemetry:**
  ```
  Step | Pos [x, y, z]           | Vel [vx, vy, vz]        | Speed | Clr   | State    | Action Executed
  -----+-------------------------+-------------------------+-------+-------+----------+----------------
   496 | [-1.41, -0.56, 1.50]    | [-1.18,  0.00, 0.00]    |  1.18 |  0.57 | REROUTE  | [-0.39, 0.00, 0.00]
   497 | [-1.45, -0.56, 1.50]    | [-0.98,  0.00, 0.00]    |  0.98 |  0.43 | REROUTE  | [-0.33, 0.00, 0.00]
   498 | [-1.48, -0.56, 1.50]    | [-0.77,  0.00, 0.00]    |  0.77 |  0.42 | REROUTE  | [-0.26, 0.00, 0.00]
   499 | [-1.50, -0.56, 1.50]    | [-0.55,  0.00, 0.00]    |  0.55 |  0.41 | REROUTE  | [-0.18, 0.00, 0.00]
   500 | [-1.52, -0.56, 1.50]    | [-0.31,  0.00, 0.00]    |  0.31 |  0.41 | REROUTE  | [-0.10, 0.00, 0.00]
  ```

### [Seed 5024] Configuration: Shield ON (oracle) — Outcome: `TIMEOUT`
- **Steps:** 500 | **Reward:** -2695.39 | **Min Clearance:** 0.248 m
- **Diagnostic Cause:** Exceeded maximum episode limit (500 steps) without reaching goal.
- **Last 5 Control Steps Telemetry:**
  ```
  Step | Pos [x, y, z]           | Vel [vx, vy, vz]        | Speed | Clr   | State    | Action Executed
  -----+-------------------------+-------------------------+-------+-------+----------+----------------
   496 | [-0.16, -0.83, 1.50]    | [-0.33,  0.40, -0.00]   |  0.52 |  0.28 | REROUTE  | [-0.11, 0.13, -0.00]
   497 | [-0.16, -0.86, 1.50]    | [ 0.00, -0.80, -0.00]   |  0.80 |  0.27 | RETREAT  | [0.00, -0.27, -0.00]
   498 | [-0.16, -0.90, 1.50]    | [ 0.00, -0.80, -0.00]   |  0.80 |  0.29 | RETREAT  | [0.00, -0.27, -0.00]
   499 | [-0.16, -0.93, 1.50]    | [ 0.00, -0.80, -0.00]   |  0.80 |  0.40 | RETREAT  | [0.00, -0.27, -0.00]
   500 | [-0.16, -0.96, 1.50]    | [ 0.00, -0.73, -0.00]   |  0.73 |  0.35 | RETREAT  | [0.00, -0.24, -0.00]
  ```

### [Seed 5026] Configuration: Shield ON (oracle) — Outcome: `TIMEOUT`
- **Steps:** 500 | **Reward:** -1529.81 | **Min Clearance:** 0.09 m
- **Diagnostic Cause:** Exceeded maximum episode limit (500 steps) without reaching goal.
- **Last 5 Control Steps Telemetry:**
  ```
  Step | Pos [x, y, z]           | Vel [vx, vy, vz]        | Speed | Clr   | State    | Action Executed
  -----+-------------------------+-------------------------+-------+-------+----------+----------------
   496 | [-3.95,  0.72, 1.50]    | [ 0.00, -0.80, 0.00]    |  0.80 |  0.51 | RETREAT  | [0.00, -0.27, 0.00]
   497 | [-3.95,  0.69, 1.50]    | [ 0.00, -0.80, 0.00]    |  0.80 |  0.47 | SCAN     | [0.00, -0.27, 0.00]
   498 | [-3.91,  0.75, 1.50]    | [ 0.99,  1.50, 0.00]    |  1.80 |  0.50 | REROUTE  | [0.33, 0.50, 0.00]
   499 | [-3.88,  0.77, 1.50]    | [ 0.78,  0.40, 0.00]    |  0.87 |  0.49 | REROUTE  | [0.26, 0.13, 0.00]
   500 | [-3.86,  0.79, 1.50]    | [ 0.39,  0.40, 0.00]    |  0.56 |  0.47 | REROUTE  | [0.13, 0.13, 0.00]
  ```

### [Seed 5039] Configuration: Shield ON (oracle) — Outcome: `TIMEOUT`
- **Steps:** 500 | **Reward:** -1555.86 | **Min Clearance:** 0.346 m
- **Diagnostic Cause:** Exceeded maximum episode limit (500 steps) without reaching goal.
- **Last 5 Control Steps Telemetry:**
  ```
  Step | Pos [x, y, z]           | Vel [vx, vy, vz]        | Speed | Clr   | State    | Action Executed
  -----+-------------------------+-------------------------+-------+-------+----------+----------------
   496 | [-1.57, -3.20, 1.50]    | [-0.55,  1.50, 0.00]    |  1.60 |  0.74 | REROUTE  | [-0.18, 0.50, 0.00]
   497 | [-1.59, -3.14, 1.50]    | [-0.30,  1.60, 0.00]    |  1.63 |  0.60 | REROUTE  | [-0.10, 0.53, 0.00]
   498 | [-1.59, -3.17, 1.50]    | [ 0.00, -0.80, 0.00]    |  0.80 |  0.69 | RETREAT  | [0.00, -0.27, 0.00]
   499 | [-1.59, -3.20, 1.50]    | [ 0.00, -0.80, 0.00]    |  0.80 |  0.78 | RETREAT  | [0.00, -0.27, 0.00]
   500 | [-1.59, -3.24, 1.50]    | [ 0.00, -0.80, 0.00]    |  0.80 |  0.66 | RETREAT  | [0.00, -0.27, 0.00]
  ```
