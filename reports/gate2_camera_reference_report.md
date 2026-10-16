# Stop, Hover & Re-Route (SHR) Drone Safety Shield Benchmark Report

**Date:** 2026-10-16T08:03:26Z  
**Seeds:** `reference` (5 episodes)  
**Checkpoint:** `best_model_baseline.pt`  

## Executive Summary & Comparison Table

| Metric | Baseline (OFF) | Shield ON (Oracle) | Shield ON (Camera) | Target |
|---|:---:|:---:|:---:|:---:|
| **Success Rate (95% CI)** | — | — |  40.0% [11.8%, 76.9%] (2/5) | **>= 85.0%** |
| **Total Collision Rate** | — | — |  60.0% [23.1%, 88.2%] (3/5) | **<= 2.0%** |
| Obstacle Collisions | — | — |  60.0% [23.1%, 88.2%] (3/5) | — |
| Wall OOB Collisions | — | — |   0.0% [ 0.0%, 43.4%] (0/5) | — |
| Timeout Rate | — | — |   0.0% [ 0.0%, 43.4%] (0/5) | **<= 5.0%** |
| **Mean Reward** | — +/- — | — +/- — | -442.40 +/- 444.78 | — |
| **Mean Min Clearance** | — m | — m | 0.23 m | — |
| **Mean Episode Steps** | — | — | 181.6 | — |
| **Standoff Distance** | N/A | — m | 0.59 m | **>= 0.45 m** |
| **Step Overhead (Baseline Succ)** | Baseline | —% | —% | **<= 15.0%** |

## Acceptance Criteria Audit

## Crash Forensics Log

Total non-success episodes analyzed: **3**

### [Seed 101] Configuration: Shield ON (camera) — Outcome: `OBSTACLE_COLLISION`
- **Steps:** 103 | **Reward:** -310.34 | **Min Clearance:** 0.223 m
- **Diagnostic Cause:** Obstacle collision at speed 1.54 m/s (min clearance 0.28m).
- **Last 5 Control Steps Telemetry:**
  ```
  Step | Pos [x, y, z]           | Vel [vx, vy, vz]        | Speed | Clr   | State    | Action Executed
  -----+-------------------------+-------------------------+-------+-------+----------+----------------
    99 | [-2.45, -0.86, 1.50]    | [-1.50,  0.00, 0.00]    |  1.50 |  0.22 | REROUTE  | [-0.50, 0.00, 0.00]
   100 | [-2.52, -0.85, 1.50]    | [-1.50,  0.35, 0.00]    |  1.54 |  0.33 | REROUTE  | [-0.50, 0.12, 0.00]
   101 | [-2.58, -0.84, 1.50]    | [-1.50,  0.35, 0.00]    |  1.54 |  0.32 | REROUTE  | [-0.50, 0.12, 0.00]
   102 | [-2.64, -0.82, 1.50]    | [-1.50,  0.35, 0.00]    |  1.54 |  0.30 | REROUTE  | [-0.50, 0.12, 0.00]
   103 | [-2.70, -0.81, 1.50]    | [-1.50,  0.35, 0.00]    |  1.54 |  0.28 | REROUTE  | [-0.50, 0.12, 0.00]
  ```

### [Seed 202] Configuration: Shield ON (camera) — Outcome: `OBSTACLE_COLLISION`
- **Steps:** 75 | **Reward:** -170.09 | **Min Clearance:** 0.326 m
- **Diagnostic Cause:** Obstacle collision at speed 2.05 m/s (min clearance 1.42m).
- **Last 5 Control Steps Telemetry:**
  ```
  Step | Pos [x, y, z]           | Vel [vx, vy, vz]        | Speed | Clr   | State    | Action Executed
  -----+-------------------------+-------------------------+-------+-------+----------+----------------
    71 | [ 0.55, -2.21, 1.50]    | [-1.69,  1.10, -0.04]   |  2.01 |  1.60 | NOMINAL  | [-0.56, 0.37, -0.01]
    72 | [ 0.47, -2.16, 1.50]    | [-1.76,  1.12, -0.01]   |  2.08 |  1.55 | NOMINAL  | [-0.59, 0.37, -0.00]
    73 | [ 0.56, -2.11, 1.50]    | [ 2.18,  1.06, -0.02]   |  2.43 |  1.51 | NOMINAL  | [0.73, 0.35, -0.01]
    74 | [ 0.45, -2.07, 1.50]    | [-2.67,  1.03, -0.00]   |  2.87 |  1.46 | NOMINAL  | [-0.89, 0.34, -0.00]
    75 | [ 0.38, -2.03, 1.50]    | [-1.79,  1.00, 0.04]    |  2.05 |  1.42 | NOMINAL  | [-0.60, 0.33, 0.01]
  ```

### [Seed 505] Configuration: Shield ON (camera) — Outcome: `OBSTACLE_COLLISION`
- **Steps:** 62 | **Reward:** -0.87 | **Min Clearance:** 0.569 m
- **Diagnostic Cause:** Obstacle collision at speed 2.31 m/s (min clearance 1.58m).
- **Last 5 Control Steps Telemetry:**
  ```
  Step | Pos [x, y, z]           | Vel [vx, vy, vz]        | Speed | Clr   | State    | Action Executed
  -----+-------------------------+-------------------------+-------+-------+----------+----------------
    58 | [-0.94, -3.49, 1.50]    | [-0.04,  1.54, 0.01]    |  1.54 |  1.53 | NOMINAL  | [-0.01, 0.51, 0.00]
    59 | [-0.94, -3.42, 1.50]    | [-0.08,  1.65, -0.00]   |  1.65 |  1.47 | NOMINAL  | [-0.03, 0.55, -0.00]
    60 | [-0.93, -3.34, 1.50]    | [ 0.27,  1.87, -0.01]   |  1.89 |  1.40 | NOMINAL  | [0.09, 0.62, -0.00]
    61 | [-0.93, -3.26, 1.50]    | [-0.07,  2.01, 0.01]    |  2.01 |  1.66 | NOMINAL  | [-0.02, 0.67, 0.00]
    62 | [-0.96, -3.17, 1.50]    | [-0.72,  2.20, 0.04]    |  2.31 |  1.58 | NOMINAL  | [-0.24, 0.73, 0.01]
  ```
