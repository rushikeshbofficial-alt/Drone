# Stop, Hover & Re-Route (SHR) Drone Safety Shield Benchmark Report

**Date:** 2026-10-15T22:25:11Z  
**Seeds:** `2000-2001` (2 episodes)  
**Checkpoint:** `best_model.pt`  

## Executive Summary & Comparison Table

| Metric | Baseline (OFF) | Shield ON (Oracle) | Shield ON (Camera) | Target |
|---|:---:|:---:|:---:|:---:|
| **Success Rate (95% CI)** |  50.0% [ 9.5%, 90.5%] (1/2) |  50.0% [ 9.5%, 90.5%] (1/2) |   0.0% [ 0.0%, 65.8%] (0/2) | **>= 85.0%** |
| **Total Collision Rate** |  50.0% [ 9.5%, 90.5%] (1/2) |   0.0% [ 0.0%, 65.8%] (0/2) |   0.0% [ 0.0%, 65.8%] (0/2) | **<= 2.0%** |
| Obstacle Collisions |  50.0% [ 9.5%, 90.5%] (1/2) |   0.0% [ 0.0%, 65.8%] (0/2) |   0.0% [ 0.0%, 65.8%] (0/2) | — |
| Wall OOB Collisions |   0.0% [ 0.0%, 65.8%] (0/2) |   0.0% [ 0.0%, 65.8%] (0/2) |   0.0% [ 0.0%, 65.8%] (0/2) | — |
| Timeout Rate |   0.0% [ 0.0%, 65.8%] (0/2) |  50.0% [ 9.5%, 90.5%] (1/2) | 100.0% [34.2%, 100.0%] (2/2) | **<= 5.0%** |
| **Mean Reward** | 31.99 +/- 232.34 | -408.64 +/- 425.20 | -2147.69 +/- 339.25 | — |
| **Mean Min Clearance** | 0.11 m | 0.25 m | 0.54 m | — |
| **Mean Episode Steps** | 106.0 | 417.0 | 500.0 | — |
| **Standoff Distance** | N/A | 2.14 m | 0.60 m | **>= 0.45 m** |
| **Step Overhead (Baseline Succ)** | Baseline | 136.88% | 254.61% | **<= 15.0%** |

## Acceptance Criteria Audit

| Criterion | Target | Achieved (Oracle) | Verdict |
|---|:---:|:---:|:---:|
| Total Collisions <= 2.0% | <= 2.0% | 0.0% | **✅ PASS** |
| Success Rate >= 85.0% | >= 85.0% | 50.0% | **❌ FAIL** |
| Timeout Rate <= 5.0% | <= 5.0% | 50.0% | **❌ FAIL** |
| Standoff Distance >= 0.45m | >= 0.45 m | 2.14 m | **✅ PASS** |
| Step Overhead on Baseline-Success <= 15.0% | <= 15.0% | 136.9% | **❌ FAIL** |

**Overall Status:** ⚠️ **ACTION REQUIRED: CRITERIA UNMET**

## Crash Forensics Log

Total non-success episodes analyzed: **4**

### [Seed 2001] Configuration: Baseline (Shield OFF) — Outcome: `OBSTACLE_COLLISION`
- **Steps:** 71 | **Reward:** -200.35 | **Min Clearance:** 0.105 m
- **Diagnostic Cause:** Obstacle collision at speed 2.32 m/s (min clearance 0.17m).
- **Last 5 Control Steps Telemetry:**
  ```
  Step | Pos [x, y, z]           | Vel [vx, vy, vz]        | Speed | Clr   | State    | Action Executed
  -----+-------------------------+-------------------------+-------+-------+----------+----------------
    67 | [-1.00, -1.07, 1.50]    | [ 1.00,  1.76, 0.08]    |  2.03 |  0.16 | DISABLED | [0.33, 0.59, 0.03]
    68 | [-1.08, -1.00, 1.50]    | [-1.92,  1.78, 0.02]    |  2.62 |  0.16 | DISABLED | [-0.64, 0.59, 0.01]
    69 | [-1.16, -0.93, 1.50]    | [-1.79,  1.81, 0.01]    |  2.55 |  0.17 | DISABLED | [-0.60, 0.60, 0.00]
    70 | [-1.20, -0.85, 1.50]    | [-1.00,  1.88, 0.01]    |  2.13 |  0.16 | DISABLED | [-0.33, 0.63, 0.00]
    71 | [-1.25, -0.77, 1.50]    | [-1.25,  1.95, 0.02]    |  2.32 |  0.17 | DISABLED | [-0.42, 0.65, 0.01]
  ```

### [Seed 2001] Configuration: Shield ON (Oracle) — Outcome: `TIMEOUT`
- **Steps:** 500 | **Reward:** 16.56 | **Min Clearance:** 0.22 m
- **Diagnostic Cause:** Exceeded maximum episode limit (500 steps) without reaching goal.
- **Last 5 Control Steps Telemetry:**
  ```
  Step | Pos [x, y, z]           | Vel [vx, vy, vz]        | Speed | Clr   | State    | Action Executed
  -----+-------------------------+-------------------------+-------+-------+----------+----------------
   496 | [ 0.54, -6.29, 1.50]    | [-1.20,  0.50, 0.00]    |  1.30 |  0.91 | REROUTE  | [-0.40, 0.17, 0.00]
   497 | [ 0.49, -6.27, 1.50]    | [-1.20,  0.50, 0.00]    |  1.30 |  0.89 | REROUTE  | [-0.40, 0.17, 0.00]
   498 | [ 0.44, -6.25, 1.50]    | [-1.20,  0.50, 0.00]    |  1.30 |  0.86 | REROUTE  | [-0.40, 0.17, 0.00]
   499 | [ 0.39, -6.23, 1.50]    | [-1.20,  0.50, 0.00]    |  1.30 |  0.83 | REROUTE  | [-0.40, 0.17, 0.00]
   500 | [ 0.34, -6.21, 1.50]    | [-1.20,  0.50, 0.00]    |  1.30 |  0.81 | REROUTE  | [-0.40, 0.17, 0.00]
  ```

### [Seed 2000] Configuration: Shield ON (Camera) — Outcome: `TIMEOUT`
- **Steps:** 500 | **Reward:** -1808.44 | **Min Clearance:** 0.537 m
- **Diagnostic Cause:** Exceeded maximum episode limit (500 steps) without reaching goal.
- **Last 5 Control Steps Telemetry:**
  ```
  Step | Pos [x, y, z]           | Vel [vx, vy, vz]        | Speed | Clr   | State    | Action Executed
  -----+-------------------------+-------------------------+-------+-------+----------+----------------
   496 | [-1.76, -2.16, 1.50]    | [ 0.00,  0.00, 0.00]    |  0.00 |  0.55 | SCAN     | [0.00, 0.00, 0.00]
   497 | [-1.71, -2.14, 1.50]    | [ 1.20,  0.50, 0.01]    |  1.30 |  0.55 | REROUTE  | [0.40, 0.17, 0.00]
   498 | [-1.71, -2.17, 1.50]    | [ 0.00, -0.80, 0.01]    |  0.80 |  0.54 | RETREAT  | [0.00, -0.27, 0.00]
   499 | [-1.71, -2.21, 1.50]    | [ 0.00, -0.80, 0.01]    |  0.80 |  0.57 | RETREAT  | [0.00, -0.27, 0.00]
   500 | [-1.71, -2.24, 1.50]    | [ 0.00, -0.80, 0.01]    |  0.80 |  0.61 | RETREAT  | [0.00, -0.27, 0.00]
  ```

### [Seed 2001] Configuration: Shield ON (Camera) — Outcome: `TIMEOUT`
- **Steps:** 500 | **Reward:** -2486.94 | **Min Clearance:** 0.541 m
- **Diagnostic Cause:** Exceeded maximum episode limit (500 steps) without reaching goal.
- **Last 5 Control Steps Telemetry:**
  ```
  Step | Pos [x, y, z]           | Vel [vx, vy, vz]        | Speed | Clr   | State    | Action Executed
  -----+-------------------------+-------------------------+-------+-------+----------+----------------
   496 | [-1.16, -2.36, 1.50]    | [ 0.00, -0.80, -0.00]   |  0.80 |  0.86 | RETREAT  | [0.00, -0.27, -0.00]
   497 | [-1.16, -2.39, 1.50]    | [ 0.00, -0.80, -0.00]   |  0.80 |  0.90 | SCAN     | [0.00, -0.27, -0.00]
   498 | [-1.16, -2.42, 1.50]    | [ 0.00, -0.80, -0.00]   |  0.80 |  0.93 | RETREAT  | [0.00, -0.27, -0.00]
   499 | [-1.16, -2.46, 1.50]    | [ 0.00, -0.80, -0.00]   |  0.80 |  0.96 | RETREAT  | [0.00, -0.27, -0.00]
   500 | [-1.16, -2.49, 1.50]    | [ 0.00, -0.80, -0.00]   |  0.80 |  0.99 | RETREAT  | [0.00, -0.27, -0.00]
  ```
