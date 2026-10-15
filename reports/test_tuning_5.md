# Stop, Hover & Re-Route (SHR) Drone Safety Shield Benchmark Report

**Date:** 2026-10-15T22:28:37Z  
**Seeds:** `2000-2004` (5 episodes)  
**Checkpoint:** `best_model.pt`  

## Executive Summary & Comparison Table

| Metric | Baseline (OFF) | Shield ON (Oracle) | Shield ON (Camera) | Target |
|---|:---:|:---:|:---:|:---:|
| **Success Rate (95% CI)** |  40.0% [11.8%, 76.9%] (2/5) | 100.0% [56.6%, 100.0%] (5/5) |   0.0% [ 0.0%, 43.4%] (0/5) | **>= 85.0%** |
| **Total Collision Rate** |  60.0% [23.1%, 88.2%] (3/5) |   0.0% [ 0.0%, 43.4%] (0/5) |  40.0% [11.8%, 76.9%] (2/5) | **<= 2.0%** |
| Obstacle Collisions |  60.0% [23.1%, 88.2%] (3/5) |   0.0% [ 0.0%, 43.4%] (0/5) |  40.0% [11.8%, 76.9%] (2/5) | — |
| Wall OOB Collisions |   0.0% [ 0.0%, 43.4%] (0/5) |   0.0% [ 0.0%, 43.4%] (0/5) |   0.0% [ 0.0%, 43.4%] (0/5) | — |
| Timeout Rate |   0.0% [ 0.0%, 43.4%] (0/5) |   0.0% [ 0.0%, 43.4%] (0/5) |  60.0% [23.1%, 88.2%] (3/5) | **<= 5.0%** |
| **Mean Reward** | 67.80 +/- 153.69 | -30.64 +/- 114.19 | -1401.70 +/- 1190.93 | — |
| **Mean Min Clearance** | 0.16 m | 0.37 m | 0.74 m | — |
| **Mean Episode Steps** | 88.4 | 210.4 | 319.2 | — |
| **Standoff Distance** | N/A | 1.14 m | 0.58 m | **>= 0.45 m** |
| **Step Overhead (Baseline Succ)** | Baseline | 56.71% | 94.43% | **<= 15.0%** |

## Acceptance Criteria Audit

| Criterion | Target | Achieved (Oracle) | Verdict |
|---|:---:|:---:|:---:|
| Total Collisions <= 2.0% | <= 2.0% | 0.0% | **✅ PASS** |
| Success Rate >= 85.0% | >= 85.0% | 100.0% | **✅ PASS** |
| Timeout Rate <= 5.0% | <= 5.0% | 0.0% | **✅ PASS** |
| Standoff Distance >= 0.45m | >= 0.45 m | 1.14 m | **✅ PASS** |
| Step Overhead on Baseline-Success <= 15.0% | <= 15.0% | 56.7% | **❌ FAIL** |

**Overall Status:** ⚠️ **ACTION REQUIRED: CRITERIA UNMET**

## Crash Forensics Log

Total non-success episodes analyzed: **8**

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

### [Seed 2002] Configuration: Baseline (Shield OFF) — Outcome: `OBSTACLE_COLLISION`
- **Steps:** 46 | **Reward:** 63.54 | **Min Clearance:** 0.119 m
- **Diagnostic Cause:** Obstacle collision at speed 2.94 m/s (min clearance 0.16m).
- **Last 5 Control Steps Telemetry:**
  ```
  Step | Pos [x, y, z]           | Vel [vx, vy, vz]        | Speed | Clr   | State    | Action Executed
  -----+-------------------------+-------------------------+-------+-------+----------+----------------
    42 | [ 0.30, -3.04, 1.50]    | [ 0.49,  2.67, -0.00]   |  2.71 |  0.16 | DISABLED | [0.16, 0.89, -0.00]
    43 | [ 0.32, -2.93, 1.50]    | [ 0.54,  2.67, -0.00]   |  2.72 |  0.14 | DISABLED | [0.18, 0.89, -0.00]
    44 | [ 0.34, -2.82, 1.50]    | [ 0.46,  2.65, 0.00]    |  2.69 |  0.12 | DISABLED | [0.15, 0.88, 0.00]
    45 | [ 0.37, -2.71, 1.50]    | [ 0.89,  2.64, -0.02]   |  2.79 |  0.14 | DISABLED | [0.30, 0.88, -0.01]
    46 | [ 0.44, -2.60, 1.50]    | [ 1.48,  2.54, 0.01]    |  2.94 |  0.16 | DISABLED | [0.49, 0.84, 0.00]
  ```

### [Seed 2003] Configuration: Baseline (Shield OFF) — Outcome: `OBSTACLE_COLLISION`
- **Steps:** 38 | **Reward:** 57.39 | **Min Clearance:** 0.344 m
- **Diagnostic Cause:** Obstacle collision at speed 2.88 m/s (min clearance 0.34m).
- **Last 5 Control Steps Telemetry:**
  ```
  Step | Pos [x, y, z]           | Vel [vx, vy, vz]        | Speed | Clr   | State    | Action Executed
  -----+-------------------------+-------------------------+-------+-------+----------+----------------
    34 | [ 0.67, -4.10, 1.50]    | [ 0.16,  2.82, 0.00]    |  2.82 |  0.64 | DISABLED | [0.05, 0.94, 0.00]
    35 | [ 0.66, -3.98, 1.50]    | [-0.35,  2.78, -0.03]   |  2.80 |  0.57 | DISABLED | [-0.12, 0.93, -0.01]
    36 | [ 0.63, -3.87, 1.50]    | [-0.64,  2.78, -0.03]   |  2.85 |  0.48 | DISABLED | [-0.21, 0.93, -0.01]
    37 | [ 0.61, -3.75, 1.50]    | [-0.61,  2.81, 0.00]    |  2.88 |  0.41 | DISABLED | [-0.20, 0.94, 0.00]
    38 | [ 0.58, -3.63, 1.50]    | [-0.60,  2.81, 0.01]    |  2.88 |  0.34 | DISABLED | [-0.20, 0.94, 0.00]
  ```

### [Seed 2000] Configuration: Shield ON (Camera) — Outcome: `TIMEOUT`
- **Steps:** 500 | **Reward:** -2404.64 | **Min Clearance:** 0.575 m
- **Diagnostic Cause:** Exceeded maximum episode limit (500 steps) without reaching goal.
- **Last 5 Control Steps Telemetry:**
  ```
  Step | Pos [x, y, z]           | Vel [vx, vy, vz]        | Speed | Clr   | State    | Action Executed
  -----+-------------------------+-------------------------+-------+-------+----------+----------------
   496 | [-1.27, -2.24, 1.50]    | [ 1.20,  0.00, 0.00]    |  1.20 |  0.77 | REROUTE  | [0.40, 0.00, 0.00]
   497 | [-1.32, -2.24, 1.50]    | [-1.20,  0.00, 0.00]    |  1.20 |  0.78 | REROUTE  | [-0.40, 0.00, 0.00]
   498 | [-1.27, -2.24, 1.50]    | [ 1.20,  0.00, 0.00]    |  1.20 |  0.77 | REROUTE  | [0.40, 0.00, 0.00]
   499 | [-1.32, -2.24, 1.50]    | [-1.20,  0.00, 0.00]    |  1.20 |  0.78 | REROUTE  | [-0.40, 0.00, 0.00]
   500 | [-1.27, -2.24, 1.50]    | [ 1.20,  0.00, 0.00]    |  1.20 |  0.77 | REROUTE  | [0.40, 0.00, 0.00]
  ```

### [Seed 2001] Configuration: Shield ON (Camera) — Outcome: `TIMEOUT`
- **Steps:** 500 | **Reward:** -2421.68 | **Min Clearance:** 0.569 m
- **Diagnostic Cause:** Exceeded maximum episode limit (500 steps) without reaching goal.
- **Last 5 Control Steps Telemetry:**
  ```
  Step | Pos [x, y, z]           | Vel [vx, vy, vz]        | Speed | Clr   | State    | Action Executed
  -----+-------------------------+-------------------------+-------+-------+----------+----------------
   496 | [-1.22, -2.20, 1.50]    | [-1.20,  0.00, 0.00]    |  1.20 |  0.76 | REROUTE  | [-0.40, 0.00, 0.00]
   497 | [-1.17, -2.20, 1.50]    | [ 1.20,  0.00, 0.00]    |  1.20 |  0.75 | REROUTE  | [0.40, 0.00, 0.00]
   498 | [-1.22, -2.20, 1.50]    | [-1.20,  0.00, 0.00]    |  1.20 |  0.76 | REROUTE  | [-0.40, 0.00, 0.00]
   499 | [-1.17, -2.20, 1.50]    | [ 1.20,  0.00, 0.00]    |  1.20 |  0.75 | REROUTE  | [0.40, 0.00, 0.00]
   500 | [-1.22, -2.20, 1.50]    | [-1.20,  0.00, 0.00]    |  1.20 |  0.76 | REROUTE  | [-0.40, 0.00, 0.00]
  ```

### [Seed 2002] Configuration: Shield ON (Camera) — Outcome: `OBSTACLE_COLLISION`
- **Steps:** 46 | **Reward:** 63.25 | **Min Clearance:** 1.467 m
- **Diagnostic Cause:** Obstacle collision at speed 2.41 m/s (min clearance 1.47m).
- **Last 5 Control Steps Telemetry:**
  ```
  Step | Pos [x, y, z]           | Vel [vx, vy, vz]        | Speed | Clr   | State    | Action Executed
  -----+-------------------------+-------------------------+-------+-------+----------+----------------
    42 | [ 0.29, -3.04, 1.50]    | [ 0.44,  2.67, -0.01]   |  2.71 |  1.88 | NOMINAL  | [0.15, 0.89, -0.00]
    43 | [ 0.31, -2.93, 1.50]    | [ 0.49,  2.67, -0.00]   |  2.72 |  1.77 | NOMINAL  | [0.16, 0.89, -0.00]
    44 | [ 0.33, -2.82, 1.50]    | [ 0.51,  2.59, 0.00]    |  2.64 |  1.66 | NOMINAL  | [0.17, 0.86, 0.00]
    45 | [ 0.37, -2.72, 1.50]    | [ 0.83,  2.38, -0.02]   |  2.52 |  1.56 | NOMINAL  | [0.28, 0.79, -0.01]
    46 | [ 0.43, -2.65, 1.50]    | [ 1.51,  1.87, -0.02]   |  2.41 |  1.47 | NOMINAL  | [0.50, 0.62, -0.01]
  ```

### [Seed 2003] Configuration: Shield ON (Camera) — Outcome: `TIMEOUT`
- **Steps:** 500 | **Reward:** -2293.94 | **Min Clearance:** 0.561 m
- **Diagnostic Cause:** Exceeded maximum episode limit (500 steps) without reaching goal.
- **Last 5 Control Steps Telemetry:**
  ```
  Step | Pos [x, y, z]           | Vel [vx, vy, vz]        | Speed | Clr   | State    | Action Executed
  -----+-------------------------+-------------------------+-------+-------+----------+----------------
   496 | [ 1.86, -2.11, 1.50]    | [ 1.20,  0.00, -0.00]   |  1.20 |  0.76 | REROUTE  | [0.40, 0.00, -0.00]
   497 | [ 1.81, -2.11, 1.50]    | [-1.20,  0.00, -0.00]   |  1.20 |  0.76 | REROUTE  | [-0.40, 0.00, -0.00]
   498 | [ 1.86, -2.11, 1.50]    | [ 1.20,  0.00, -0.00]   |  1.20 |  0.76 | REROUTE  | [0.40, 0.00, -0.00]
   499 | [ 1.81, -2.11, 1.50]    | [-1.20,  0.00, -0.00]   |  1.20 |  0.76 | REROUTE  | [-0.40, 0.00, -0.00]
   500 | [ 1.86, -2.11, 1.50]    | [ 1.20,  0.00, -0.00]   |  1.20 |  0.76 | REROUTE  | [0.40, 0.00, -0.00]
  ```

### [Seed 2004] Configuration: Shield ON (Camera) — Outcome: `OBSTACLE_COLLISION`
- **Steps:** 50 | **Reward:** 48.51 | **Min Clearance:** 0.554 m
- **Diagnostic Cause:** Obstacle collision at speed 2.62 m/s (min clearance 2.90m).
- **Last 5 Control Steps Telemetry:**
  ```
  Step | Pos [x, y, z]           | Vel [vx, vy, vz]        | Speed | Clr   | State    | Action Executed
  -----+-------------------------+-------------------------+-------+-------+----------+----------------
    46 | [-0.30, -4.50, 1.49]    | [ 0.68,  1.90, -0.00]   |  2.02 |  3.22 | NOMINAL  | [0.23, 0.63, -0.00]
    47 | [-0.27, -4.41, 1.49]    | [ 0.68,  2.04, 0.00]    |  2.15 |  3.15 | NOMINAL  | [0.23, 0.68, 0.00]
    48 | [-0.24, -4.32, 1.49]    | [ 0.67,  2.13, -0.01]   |  2.23 |  3.07 | NOMINAL  | [0.22, 0.71, -0.00]
    49 | [-0.21, -4.23, 1.49]    | [ 0.73,  2.31, 0.01]    |  2.42 |  2.99 | NOMINAL  | [0.24, 0.77, 0.00]
    50 | [-0.18, -4.12, 1.49]    | [ 0.76,  2.51, -0.00]   |  2.62 |  2.90 | NOMINAL  | [0.25, 0.84, -0.00]
  ```
