# Stop, Hover & Re-Route (SHR) Drone Safety Shield Benchmark Report

**Date:** 2026-10-15T22:51:04Z  
**Seeds:** `101,202` (2 episodes)  
**Checkpoint:** `best_model.pt`  

## Executive Summary & Comparison Table

| Metric | Baseline (OFF) | Shield ON (Oracle) | Shield ON (Camera) | Target |
|---|:---:|:---:|:---:|:---:|
| **Success Rate (95% CI)** | — | — |   0.0% [ 0.0%, 65.8%] (0/2) | **>= 85.0%** |
| **Total Collision Rate** | — | — |  50.0% [ 9.5%, 90.5%] (1/2) | **<= 2.0%** |
| Obstacle Collisions | — | — |  50.0% [ 9.5%, 90.5%] (1/2) | — |
| Wall OOB Collisions | — | — |   0.0% [ 0.0%, 65.8%] (0/2) | — |
| Timeout Rate | — | — |  50.0% [ 9.5%, 90.5%] (1/2) | **<= 5.0%** |
| **Mean Reward** | — +/- — | — +/- — | -1605.43 +/- 1312.38 | — |
| **Mean Min Clearance** | — m | — m | 0.28 m | — |
| **Mean Episode Steps** | — | — | 300.5 | — |
| **Standoff Distance** | N/A | — m | 0.43 m | **>= 0.45 m** |
| **Step Overhead (Baseline Succ)** | Baseline | —% | —% | **<= 15.0%** |

## Acceptance Criteria Audit

## Crash Forensics Log

Total non-success episodes analyzed: **2**

### [Seed 101] Configuration: Shield ON (camera) — Outcome: `OBSTACLE_COLLISION`
- **Steps:** 101 | **Reward:** -293.05 | **Min Clearance:** 0.286 m
- **Diagnostic Cause:** Obstacle collision at speed 1.50 m/s (min clearance 0.29m).
- **Last 5 Control Steps Telemetry:**
  ```
  Step | Pos [x, y, z]           | Vel [vx, vy, vz]        | Speed | Clr   | State    | Action Executed
  -----+-------------------------+-------------------------+-------+-------+----------+----------------
    97 | [-2.55, -0.94, 1.50]    | [-1.50,  0.00, 0.00]    |  1.50 |  0.30 | REROUTE  | [-0.50, 0.00, 0.00]
    98 | [-2.62, -0.94, 1.50]    | [-1.50,  0.00, 0.00]    |  1.50 |  0.30 | REROUTE  | [-0.50, 0.00, 0.00]
    99 | [-2.68, -0.94, 1.50]    | [-1.50,  0.00, 0.00]    |  1.50 |  0.29 | REROUTE  | [-0.50, 0.00, 0.00]
   100 | [-2.74, -0.94, 1.50]    | [-1.50,  0.00, 0.00]    |  1.50 |  0.29 | REROUTE  | [-0.50, 0.00, 0.00]
   101 | [-2.80, -0.94, 1.50]    | [-1.50,  0.00, 0.00]    |  1.50 |  0.29 | REROUTE  | [-0.50, 0.00, 0.00]
  ```

### [Seed 202] Configuration: Shield ON (camera) — Outcome: `TIMEOUT`
- **Steps:** 500 | **Reward:** -2917.81 | **Min Clearance:** 0.282 m
- **Diagnostic Cause:** Exceeded maximum episode limit (500 steps) without reaching goal.
- **Last 5 Control Steps Telemetry:**
  ```
  Step | Pos [x, y, z]           | Vel [vx, vy, vz]        | Speed | Clr   | State    | Action Executed
  -----+-------------------------+-------------------------+-------+-------+----------+----------------
   496 | [ 3.84, -0.88, 1.50]    | [ 0.00, -0.80, -0.00]   |  0.80 |  0.33 | RETREAT  | [0.00, -0.27, -0.00]
   497 | [ 3.84, -0.91, 1.50]    | [ 0.00, -0.80, -0.00]   |  0.80 |  0.36 | RETREAT  | [0.00, -0.27, -0.00]
   498 | [ 3.84, -0.94, 1.50]    | [ 0.00, -0.80, -0.00]   |  0.80 |  0.40 | RETREAT  | [0.00, -0.27, -0.00]
   499 | [ 3.84, -0.98, 1.50]    | [ 0.00, -0.80, -0.00]   |  0.80 |  0.43 | RETREAT  | [0.00, -0.27, -0.00]
   500 | [ 3.84, -1.01, 1.50]    | [ 0.00, -0.80, -0.00]   |  0.80 |  0.33 | RETREAT  | [0.00, -0.27, -0.00]
  ```
