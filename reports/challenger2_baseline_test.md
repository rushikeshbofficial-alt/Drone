# Stop, Hover & Re-Route (SHR) Drone Safety Shield Benchmark Report

**Date:** 2026-10-15T22:51:17Z  
**Seeds:** `101,202` (2 episodes)  
**Checkpoint:** `best_model.pt`  

## Executive Summary & Comparison Table

| Metric | Baseline (OFF) | Shield ON (Oracle) | Shield ON (Camera) | Target |
|---|:---:|:---:|:---:|:---:|
| **Success Rate (95% CI)** |   0.0% [ 0.0%, 65.8%] (0/2) | — | — | **>= 85.0%** |
| **Total Collision Rate** | 100.0% [34.2%, 100.0%] (2/2) | — | — | **<= 2.0%** |
| Obstacle Collisions |  50.0% [ 9.5%, 90.5%] (1/2) | — | — | — |
| Wall OOB Collisions |  50.0% [ 9.5%, 90.5%] (1/2) | — | — | — |
| Timeout Rate |   0.0% [ 0.0%, 65.8%] (0/2) | — | — | **<= 5.0%** |
| **Mean Reward** | -247.31 +/- 52.58 | — +/- — | — +/- — | — |
| **Mean Min Clearance** | 0.08 m | — m | — m | — |
| **Mean Episode Steps** | 133.0 | — | — | — |
| **Standoff Distance** | N/A | — m | — m | **>= 0.45 m** |
| **Step Overhead (Baseline Succ)** | Baseline | —% | —% | **<= 15.0%** |

## Acceptance Criteria Audit

## Crash Forensics Log

Total non-success episodes analyzed: **2**

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
