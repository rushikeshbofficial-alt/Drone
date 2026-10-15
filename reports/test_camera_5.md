# Stop, Hover & Re-Route (SHR) Drone Safety Shield Benchmark Report

**Date:** 2026-10-15T22:31:17Z  
**Seeds:** `2000-2004` (5 episodes)  
**Checkpoint:** `best_model.pt`  

## Executive Summary & Comparison Table

| Metric | Baseline (OFF) | Shield ON (Oracle) | Shield ON (Camera) | Target |
|---|:---:|:---:|:---:|:---:|
| **Success Rate (95% CI)** | — | — |   0.0% [ 0.0%, 43.4%] (0/5) | **>= 85.0%** |
| **Total Collision Rate** | — | — |  80.0% [37.6%, 96.4%] (4/5) | **<= 2.0%** |
| Obstacle Collisions | — | — |  80.0% [37.6%, 96.4%] (4/5) | — |
| Wall OOB Collisions | — | — |   0.0% [ 0.0%, 43.4%] (0/5) | — |
| Timeout Rate | — | — |  20.0% [ 3.6%, 62.4%] (1/5) | **<= 5.0%** |
| **Mean Reward** | — +/- — | — +/- — | -466.97 +/- 880.47 | — |
| **Mean Min Clearance** | — m | — m | 0.98 m | — |
| **Mean Episode Steps** | — | — | 144.2 | — |
| **Standoff Distance** | N/A | — m | 0.58 m | **>= 0.45 m** |
| **Step Overhead (Baseline Succ)** | Baseline | —% | —% | **<= 15.0%** |

## Acceptance Criteria Audit

## Crash Forensics Log

Total non-success episodes analyzed: **5**

### [Seed 2000] Configuration: Shield ON (camera) — Outcome: `TIMEOUT`
- **Steps:** 500 | **Reward:** -2210.87 | **Min Clearance:** 0.379 m
- **Diagnostic Cause:** Exceeded maximum episode limit (500 steps) without reaching goal.
- **Last 5 Control Steps Telemetry:**
  ```
  Step | Pos [x, y, z]           | Vel [vx, vy, vz]        | Speed | Clr   | State    | Action Executed
  -----+-------------------------+-------------------------+-------+-------+----------+----------------
   496 | [-2.63, -1.16, 1.50]    | [-1.20,  0.00, 0.00]    |  1.20 |  0.47 | REROUTE  | [-0.40, 0.00, 0.00]
   497 | [-2.68, -1.16, 1.50]    | [-1.20,  0.00, 0.00]    |  1.20 |  0.47 | REROUTE  | [-0.40, 0.00, 0.00]
   498 | [-2.73, -1.16, 1.50]    | [-1.20,  0.00, 0.00]    |  1.20 |  0.46 | REROUTE  | [-0.40, 0.00, 0.00]
   499 | [-2.78, -1.16, 1.50]    | [-1.20,  0.00, 0.00]    |  1.20 |  0.46 | REROUTE  | [-0.40, 0.00, 0.00]
   500 | [-2.83, -1.16, 1.50]    | [-1.20,  0.00, 0.00]    |  1.20 |  0.46 | REROUTE  | [-0.40, 0.00, 0.00]
  ```

### [Seed 2001] Configuration: Shield ON (camera) — Outcome: `OBSTACLE_COLLISION`
- **Steps:** 99 | **Reward:** -266.9 | **Min Clearance:** 0.488 m
- **Diagnostic Cause:** Obstacle collision at speed 1.20 m/s (min clearance 0.49m).
- **Last 5 Control Steps Telemetry:**
  ```
  Step | Pos [x, y, z]           | Vel [vx, vy, vz]        | Speed | Clr   | State    | Action Executed
  -----+-------------------------+-------------------------+-------+-------+----------+----------------
    95 | [-1.19, -1.16, 1.51]    | [-1.20,  0.40, -0.02]   |  1.26 |  0.54 | REROUTE  | [-0.40, 0.13, -0.01]
    96 | [-1.24, -1.14, 1.51]    | [-1.20,  0.40, -0.02]   |  1.26 |  0.53 | REROUTE  | [-0.40, 0.13, -0.01]
    97 | [-1.29, -1.12, 1.51]    | [-1.20,  0.40, -0.02]   |  1.26 |  0.52 | REROUTE  | [-0.40, 0.13, -0.01]
    98 | [-1.34, -1.11, 1.51]    | [-1.20,  0.40, -0.02]   |  1.26 |  0.50 | REROUTE  | [-0.40, 0.13, -0.01]
    99 | [-1.39, -1.11, 1.51]    | [-1.20,  0.00, -0.02]   |  1.20 |  0.49 | REROUTE  | [-0.40, 0.00, -0.01]
  ```

### [Seed 2002] Configuration: Shield ON (camera) — Outcome: `OBSTACLE_COLLISION`
- **Steps:** 46 | **Reward:** 63.52 | **Min Clearance:** 2.053 m
- **Diagnostic Cause:** Obstacle collision at speed 2.95 m/s (min clearance 2.05m).
- **Last 5 Control Steps Telemetry:**
  ```
  Step | Pos [x, y, z]           | Vel [vx, vy, vz]        | Speed | Clr   | State    | Action Executed
  -----+-------------------------+-------------------------+-------+-------+----------+----------------
    42 | [ 0.29, -3.04, 1.50]    | [ 0.44,  2.67, -0.01]   |  2.71 |  2.49 | NOMINAL  | [0.15, 0.89, -0.00]
    43 | [ 0.31, -2.93, 1.50]    | [ 0.49,  2.67, -0.00]   |  2.72 |  2.38 | NOMINAL  | [0.16, 0.89, -0.00]
    44 | [ 0.33, -2.82, 1.50]    | [ 0.52,  2.65, 0.00]    |  2.70 |  2.27 | NOMINAL  | [0.17, 0.88, 0.00]
    45 | [ 0.37, -2.71, 1.50]    | [ 0.93,  2.63, -0.02]   |  2.79 |  2.16 | NOMINAL  | [0.31, 0.88, -0.01]
    46 | [ 0.43, -2.60, 1.50]    | [ 1.53,  2.52, 0.00]    |  2.95 |  2.05 | NOMINAL  | [0.51, 0.84, 0.00]
  ```

### [Seed 2003] Configuration: Shield ON (camera) — Outcome: `OBSTACLE_COLLISION`
- **Steps:** 40 | **Reward:** 45.38 | **Min Clearance:** 1.27 m
- **Diagnostic Cause:** Obstacle collision at speed 2.85 m/s (min clearance 3.08m).
- **Last 5 Control Steps Telemetry:**
  ```
  Step | Pos [x, y, z]           | Vel [vx, vy, vz]        | Speed | Clr   | State    | Action Executed
  -----+-------------------------+-------------------------+-------+-------+----------+----------------
    36 | [ 0.52, -4.21, 1.51]    | [ 0.43,  2.83, 0.01]    |  2.86 |  3.55 | NOMINAL  | [0.14, 0.94, 0.00]
    37 | [ 0.51, -4.09, 1.51]    | [-0.37,  2.86, -0.02]   |  2.88 |  3.49 | NOMINAL  | [-0.12, 0.95, -0.01]
    38 | [ 0.50, -3.98, 1.51]    | [-0.16,  2.84, -0.02]   |  2.85 |  3.32 | NOMINAL  | [-0.05, 0.95, -0.01]
    39 | [ 0.48, -3.86, 1.51]    | [-0.34,  2.87, -0.02]   |  2.88 |  3.25 | NOMINAL  | [-0.11, 0.95, -0.01]
    40 | [ 0.48, -3.74, 1.50]    | [-0.21,  2.84, -0.01]   |  2.85 |  3.08 | NOMINAL  | [-0.07, 0.95, -0.00]
  ```

### [Seed 2004] Configuration: Shield ON (camera) — Outcome: `OBSTACLE_COLLISION`
- **Steps:** 36 | **Reward:** 34.04 | **Min Clearance:** 0.703 m
- **Diagnostic Cause:** Obstacle collision at speed 2.52 m/s (min clearance 4.03m).
- **Last 5 Control Steps Telemetry:**
  ```
  Step | Pos [x, y, z]           | Vel [vx, vy, vz]        | Speed | Clr   | State    | Action Executed
  -----+-------------------------+-------------------------+-------+-------+----------+----------------
    32 | [-0.12, -4.97, 1.50]    | [ 0.34,  1.82, -0.01]   |  1.85 |  4.36 | NOMINAL  | [0.11, 0.61, -0.01]
    33 | [-0.12, -4.89, 1.50]    | [-0.01,  1.90, 0.00]    |  1.90 |  4.29 | NOMINAL  | [-0.00, 0.63, 0.00]
    34 | [-0.14, -4.81, 1.50]    | [-0.53,  1.95, -0.02]   |  2.02 |  4.21 | NOMINAL  | [-0.18, 0.65, -0.01]
    35 | [-0.13, -4.71, 1.50]    | [ 0.43,  2.35, -0.02]   |  2.39 |  4.13 | NOMINAL  | [0.14, 0.78, -0.01]
    36 | [-0.12, -4.61, 1.50]    | [ 0.25,  2.51, 0.01]    |  2.52 |  4.03 | NOMINAL  | [0.08, 0.84, 0.00]
  ```
