# Stop, Hover & Re-Route (SHR) Drone Safety Shield Benchmark Report

**Date:** 2026-10-15T22:32:41Z  
**Seeds:** `2000-2004` (5 episodes)  
**Checkpoint:** `best_model.pt`  

## Executive Summary & Comparison Table

| Metric | Baseline (OFF) | Shield ON (Oracle) | Shield ON (Camera) | Target |
|---|:---:|:---:|:---:|:---:|
| **Success Rate (95% CI)** |  40.0% [11.8%, 76.9%] (2/5) | 100.0% [56.6%, 100.0%] (5/5) |   0.0% [ 0.0%, 43.4%] (0/5) | **>= 85.0%** |
| **Total Collision Rate** |  60.0% [23.1%, 88.2%] (3/5) |   0.0% [ 0.0%, 43.4%] (0/5) |  80.0% [37.6%, 96.4%] (4/5) | **<= 2.0%** |
| Obstacle Collisions |  60.0% [23.1%, 88.2%] (3/5) |   0.0% [ 0.0%, 43.4%] (0/5) |  80.0% [37.6%, 96.4%] (4/5) | — |
| Wall OOB Collisions |   0.0% [ 0.0%, 43.4%] (0/5) |   0.0% [ 0.0%, 43.4%] (0/5) |   0.0% [ 0.0%, 43.4%] (0/5) | — |
| Timeout Rate |   0.0% [ 0.0%, 43.4%] (0/5) |   0.0% [ 0.0%, 43.4%] (0/5) |  20.0% [ 3.6%, 62.4%] (1/5) | **<= 5.0%** |
| **Mean Reward** | 67.80 +/- 153.69 | -16.48 +/- 129.99 | -631.57 +/- 907.98 | — |
| **Mean Min Clearance** | 0.16 m | 0.35 m | 0.82 m | — |
| **Mean Episode Steps** | 88.4 | 208.6 | 168.0 | — |
| **Standoff Distance** | N/A | 1.76 m | 0.51 m | **>= 0.45 m** |
| **Step Overhead (Baseline Succ)** | Baseline | 47.87% | 109.15% | **<= 15.0%** |

## Acceptance Criteria Audit

| Criterion | Target | Achieved (Oracle) | Verdict |
|---|:---:|:---:|:---:|
| Total Collisions <= 2.0% | <= 2.0% | 0.0% | **✅ PASS** |
| Success Rate >= 85.0% | >= 85.0% | 100.0% | **✅ PASS** |
| Timeout Rate <= 5.0% | <= 5.0% | 0.0% | **✅ PASS** |
| Standoff Distance >= 0.45m | >= 0.45 m | 1.76 m | **✅ PASS** |
| Step Overhead on Baseline-Success <= 15.0% | <= 15.0% | 47.9% | **❌ FAIL** |

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
- **Steps:** 500 | **Reward:** -2369.74 | **Min Clearance:** 0.301 m
- **Diagnostic Cause:** Exceeded maximum episode limit (500 steps) without reaching goal.
- **Last 5 Control Steps Telemetry:**
  ```
  Step | Pos [x, y, z]           | Vel [vx, vy, vz]        | Speed | Clr   | State    | Action Executed
  -----+-------------------------+-------------------------+-------+-------+----------+----------------
   496 | [-2.59, -1.06, 1.50]    | [-1.40,  0.00, 0.00]    |  1.40 |  0.38 | REROUTE  | [-0.47, 0.00, 0.00]
   497 | [-2.65, -1.06, 1.50]    | [-1.40,  0.00, 0.00]    |  1.40 |  0.38 | REROUTE  | [-0.47, 0.00, 0.00]
   498 | [-2.70, -1.06, 1.50]    | [-1.40,  0.00, 0.00]    |  1.40 |  0.38 | REROUTE  | [-0.47, 0.00, 0.00]
   499 | [-2.76, -1.06, 1.50]    | [-1.40,  0.00, 0.00]    |  1.40 |  0.37 | REROUTE  | [-0.47, 0.00, 0.00]
   500 | [-2.82, -1.06, 1.50]    | [-1.40,  0.00, 0.00]    |  1.40 |  0.37 | REROUTE  | [-0.47, 0.00, 0.00]
  ```

### [Seed 2001] Configuration: Shield ON (Camera) — Outcome: `OBSTACLE_COLLISION`
- **Steps:** 162 | **Reward:** -661.18 | **Min Clearance:** 0.154 m
- **Diagnostic Cause:** Obstacle collision at speed 1.40 m/s (min clearance 0.43m).
- **Last 5 Control Steps Telemetry:**
  ```
  Step | Pos [x, y, z]           | Vel [vx, vy, vz]        | Speed | Clr   | State    | Action Executed
  -----+-------------------------+-------------------------+-------+-------+----------+----------------
   158 | [-2.89, -1.14, 1.50]    | [ 1.40,  0.00, 0.00]    |  1.40 |  0.44 | REROUTE  | [0.47, 0.00, 0.00]
   159 | [-2.83, -1.14, 1.50]    | [ 1.40,  0.00, 0.00]    |  1.40 |  0.45 | REROUTE  | [0.47, 0.00, 0.00]
   160 | [-2.78, -1.11, 1.50]    | [ 1.40,  0.60, 0.00]    |  1.52 |  0.45 | REROUTE  | [0.47, 0.20, 0.00]
   161 | [-2.72, -1.11, 1.50]    | [ 1.40,  0.00, 0.00]    |  1.40 |  0.43 | REROUTE  | [0.47, 0.00, 0.00]
   162 | [-2.66, -1.11, 1.50]    | [ 1.40,  0.00, 0.00]    |  1.40 |  0.43 | REROUTE  | [0.47, 0.00, 0.00]
  ```

### [Seed 2002] Configuration: Shield ON (Camera) — Outcome: `OBSTACLE_COLLISION`
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

### [Seed 2003] Configuration: Shield ON (Camera) — Outcome: `OBSTACLE_COLLISION`
- **Steps:** 39 | **Reward:** 48.95 | **Min Clearance:** 1.469 m
- **Diagnostic Cause:** Obstacle collision at speed 2.86 m/s (min clearance 3.10m).
- **Last 5 Control Steps Telemetry:**
  ```
  Step | Pos [x, y, z]           | Vel [vx, vy, vz]        | Speed | Clr   | State    | Action Executed
  -----+-------------------------+-------------------------+-------+-------+----------+----------------
    35 | [ 0.52, -4.24, 1.50]    | [ 0.15,  2.86, 0.00]    |  2.86 |  3.57 | NOMINAL  | [0.05, 0.95, 0.00]
    36 | [ 0.52, -4.12, 1.50]    | [-0.15,  2.88, -0.01]   |  2.88 |  3.51 | NOMINAL  | [-0.05, 0.96, -0.01]
    37 | [ 0.49, -4.00, 1.50]    | [-0.56,  2.87, -0.02]   |  2.92 |  3.41 | NOMINAL  | [-0.19, 0.95, -0.01]
    38 | [ 0.47, -3.88, 1.50]    | [-0.40,  2.79, -0.02]   |  2.81 |  3.22 | NOMINAL  | [-0.14, 0.93, -0.01]
    39 | [ 0.46, -3.76, 1.50]    | [-0.28,  2.85, -0.01]   |  2.86 |  3.10 | NOMINAL  | [-0.10, 0.95, -0.00]
  ```

### [Seed 2004] Configuration: Shield ON (Camera) — Outcome: `OBSTACLE_COLLISION`
- **Steps:** 93 | **Reward:** -239.4 | **Min Clearance:** 0.101 m
- **Diagnostic Cause:** Obstacle collision at speed 1.40 m/s (min clearance 0.10m).
- **Last 5 Control Steps Telemetry:**
  ```
  Step | Pos [x, y, z]           | Vel [vx, vy, vz]        | Speed | Clr   | State    | Action Executed
  -----+-------------------------+-------------------------+-------+-------+----------+----------------
    89 | [-1.33, -1.06, 1.50]    | [-1.40,  0.00, -0.01]   |  1.40 |  0.43 | REROUTE  | [-0.47, 0.00, -0.00]
    90 | [-1.39, -1.06, 1.50]    | [-1.40,  0.00, -0.01]   |  1.40 |  0.43 | REROUTE  | [-0.47, 0.00, -0.00]
    91 | [-1.44, -1.06, 1.50]    | [-1.40,  0.00, -0.01]   |  1.40 |  0.44 | REROUTE  | [-0.47, 0.00, -0.00]
    92 | [-1.50, -1.06, 1.50]    | [-1.40,  0.00, -0.01]   |  1.40 |  0.44 | REROUTE  | [-0.47, 0.00, -0.00]
    93 | [-1.56, -1.06, 1.50]    | [-1.40,  0.00, -0.01]   |  1.40 |  0.10 | REROUTE  | [-0.47, 0.00, -0.00]
  ```
