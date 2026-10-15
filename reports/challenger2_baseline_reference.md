# Stop, Hover & Re-Route (SHR) Drone Safety Shield Benchmark Report

**Date:** 2026-10-15T22:51:25Z  
**Seeds:** `reference` (5 episodes)  
**Checkpoint:** `best_model.pt`  

## Executive Summary & Comparison Table

| Metric | Baseline (OFF) | Shield ON (Oracle) | Shield ON (Camera) | Target |
|---|:---:|:---:|:---:|:---:|
| **Success Rate (95% CI)** |  20.0% [ 3.6%, 62.4%] (1/5) | — | — | **>= 85.0%** |
| **Total Collision Rate** |  80.0% [37.6%, 96.4%] (4/5) | — | — | **<= 2.0%** |
| Obstacle Collisions |  60.0% [23.1%, 88.2%] (3/5) | — | — | — |
| Wall OOB Collisions |  20.0% [ 3.6%, 62.4%] (1/5) | — | — | — |
| Timeout Rate |   0.0% [ 0.0%, 43.4%] (0/5) | — | — | **<= 5.0%** |
| **Mean Reward** | -66.81 +/- 165.29 | — +/- — | — +/- — | — |
| **Mean Min Clearance** | 0.12 m | — m | — m | — |
| **Mean Episode Steps** | 102.8 | — | — | — |
| **Standoff Distance** | N/A | — m | — m | **>= 0.45 m** |
| **Step Overhead (Baseline Succ)** | Baseline | —% | —% | **<= 15.0%** |

## Acceptance Criteria Audit

## Crash Forensics Log

Total non-success episodes analyzed: **4**

### [Seed 101] Configuration: Baseline (Shield OFF) — Outcome: `OBSTACLE_COLLISION`
- **Steps:** 81 | **Reward:** -194.73 | **Min Clearance:** 0.112 m
- **Diagnostic Cause:** Obstacle collision at speed 3.40 m/s (min clearance 0.17m).
- **Last 5 Control Steps Telemetry:**
  ```
  Step | Pos [x, y, z]           | Vel [vx, vy, vz]        | Speed | Clr   | State    | Action Executed
  -----+-------------------------+-------------------------+-------+-------+----------+----------------
    77 | [-0.92, -0.01, 1.50]    | [-1.71,  2.50, 0.04]    |  3.03 |  0.15 | DISABLED | [-0.57, 0.83, 0.01]
    78 | [-0.79,  0.09, 1.50]    | [ 2.98,  2.29, 0.08]    |  3.76 |  0.13 | DISABLED | [0.99, 0.76, 0.03]
    79 | [-0.68,  0.18, 1.50]    | [ 2.81,  2.19, 0.00]    |  3.56 |  0.16 | DISABLED | [0.94, 0.73, 0.00]
    80 | [-0.56,  0.26, 1.51]    | [ 2.72,  1.97, 0.09]    |  3.36 |  0.16 | DISABLED | [0.91, 0.66, 0.03]
    81 | [-0.44,  0.33, 1.50]    | [ 2.90,  1.77, -0.06]   |  3.40 |  0.17 | DISABLED | [0.97, 0.59, -0.02]
  ```

### [Seed 202] Configuration: Baseline (Shield OFF) — Outcome: `WALL_OOB`
- **Steps:** 185 | **Reward:** -299.88 | **Min Clearance:** 0.041 m
- **Diagnostic Cause:** Perimeter boundary excursion at pos [x=0.78, y=9.60, z=1.52].
- **Last 5 Control Steps Telemetry:**
  ```
  Step | Pos [x, y, z]           | Vel [vx, vy, vz]        | Speed | Clr   | State    | Action Executed
  -----+-------------------------+-------------------------+-------+-------+----------+----------------
   181 | [ 1.10,  9.45, 1.51]    | [ 0.75,  1.05, -0.01]   |  1.29 |  0.07 | DISABLED | [0.25, 0.35, -0.00]
   182 | [ 1.10,  9.50, 1.52]    | [-0.04,  1.08, 0.10]    |  1.08 |  0.06 | DISABLED | [-0.01, 0.36, 0.03]
   183 | [ 0.98,  9.53, 1.51]    | [-2.81,  0.67, -0.05]   |  2.89 |  0.06 | DISABLED | [-0.94, 0.22, -0.02]
   184 | [ 0.88,  9.59, 1.51]    | [-2.63,  1.43, 0.02]    |  2.99 |  0.05 | DISABLED | [-0.88, 0.48, 0.01]
   185 | [ 0.78,  9.60, 1.52]    | [ 0.00,  0.00, 0.00]    |  0.00 |  0.04 | DISABLED | [-0.80, 0.46, 0.01]
  ```

### [Seed 404] Configuration: Baseline (Shield OFF) — Outcome: `OBSTACLE_COLLISION`
- **Steps:** 59 | **Reward:** -36.43 | **Min Clearance:** 0.113 m
- **Diagnostic Cause:** Obstacle collision at speed 1.99 m/s (min clearance 0.13m).
- **Last 5 Control Steps Telemetry:**
  ```
  Step | Pos [x, y, z]           | Vel [vx, vy, vz]        | Speed | Clr   | State    | Action Executed
  -----+-------------------------+-------------------------+-------+-------+----------+----------------
    55 | [ 0.38, -2.38, 1.50]    | [-0.07,  1.88, -0.00]   |  1.88 |  0.14 | DISABLED | [-0.02, 0.63, -0.00]
    56 | [ 0.42, -2.30, 1.50]    | [ 0.97,  1.81, -0.02]   |  2.05 |  0.15 | DISABLED | [0.32, 0.60, -0.01]
    57 | [ 0.40, -2.23, 1.50]    | [-0.70,  1.71, -0.01]   |  1.84 |  0.14 | DISABLED | [-0.23, 0.57, -0.00]
    58 | [ 0.50, -2.16, 1.50]    | [ 2.44,  1.58, 0.03]    |  2.91 |  0.12 | DISABLED | [0.81, 0.53, 0.01]
    59 | [ 0.54, -2.09, 1.50]    | [ 1.06,  1.69, 0.01]    |  1.99 |  0.13 | DISABLED | [0.35, 0.56, 0.00]
  ```

### [Seed 505] Configuration: Baseline (Shield OFF) — Outcome: `OBSTACLE_COLLISION`
- **Steps:** 45 | **Reward:** 26.55 | **Min Clearance:** 0.229 m
- **Diagnostic Cause:** Obstacle collision at speed 3.31 m/s (min clearance 0.23m).
- **Last 5 Control Steps Telemetry:**
  ```
  Step | Pos [x, y, z]           | Vel [vx, vy, vz]        | Speed | Clr   | State    | Action Executed
  -----+-------------------------+-------------------------+-------+-------+----------+----------------
    41 | [-0.07, -3.72, 1.51]    | [-1.07,  1.69, 0.01]    |  2.00 |  0.37 | DISABLED | [-0.35, 0.56, 0.00]
    42 | [-0.16, -3.64, 1.51]    | [-1.96,  1.81, 0.01]    |  2.66 |  0.46 | DISABLED | [-0.65, 0.60, 0.00]
    43 | [-0.28, -3.57, 1.51]    | [-2.90,  1.79, 0.00]    |  3.40 |  0.40 | DISABLED | [-0.97, 0.60, 0.00]
    44 | [-0.16, -3.50, 1.50]    | [ 2.86,  1.60, -0.05]   |  3.27 |  0.39 | DISABLED | [0.95, 0.53, -0.02]
    45 | [-0.03, -3.44, 1.50]    | [ 2.97,  1.45, -0.02]   |  3.31 |  0.23 | DISABLED | [0.99, 0.48, -0.01]
  ```
