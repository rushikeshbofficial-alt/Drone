# Stop, Hover & Re-Route (SHR) Drone Safety Shield Benchmark Report

**Date:** 2026-10-15T22:43:37Z  
**Seeds:** `tuning` (30 episodes)  
**Checkpoint:** `best_model.pt`  

## Executive Summary & Comparison Table

| Metric | Baseline (OFF) | Shield ON (Oracle) | Shield ON (Camera) | Target |
|---|:---:|:---:|:---:|:---:|
| **Success Rate (95% CI)** |  40.0% [24.6%, 57.7%] (12/30) |  90.0% [74.4%, 96.5%] (27/30) |   0.0% [ 0.0%, 11.4%] (0/30) | **>= 85.0%** |
| **Total Collision Rate** |  60.0% [42.3%, 75.4%] (18/30) |   0.0% [ 0.0%, 11.4%] (0/30) |  63.3% [45.5%, 78.1%] (19/30) | **<= 2.0%** |
| Obstacle Collisions |  60.0% [42.3%, 75.4%] (18/30) |   0.0% [ 0.0%, 11.4%] (0/30) |  63.3% [45.5%, 78.1%] (19/30) | — |
| Wall OOB Collisions |   0.0% [ 0.0%, 11.4%] (0/30) |   0.0% [ 0.0%, 11.4%] (0/30) |   0.0% [ 0.0%, 11.4%] (0/30) | — |
| Timeout Rate |   0.0% [ 0.0%, 11.4%] (0/30) |  10.0% [ 3.5%, 25.6%] (3/30) |  36.7% [21.9%, 54.5%] (11/30) | **<= 5.0%** |
| **Mean Reward** | 18.99 +/- 129.17 | -324.14 +/- 557.01 | -957.24 +/- 1118.48 | — |
| **Mean Min Clearance** | 0.15 m | 0.23 m | 0.55 m | — |
| **Mean Episode Steps** | 94.9 | 254.2 | 228.5 | — |
| **Standoff Distance** | N/A | 1.47 m | 0.44 m | **>= 0.45 m** |
| **Step Overhead (Baseline Succ)** | Baseline | 56.37% | 61.33% | **<= 15.0%** |

## Acceptance Criteria Audit

| Criterion | Target | Achieved (Oracle) | Verdict |
|---|:---:|:---:|:---:|
| Total Collisions <= 2.0% | <= 2.0% | 0.0% | **✅ PASS** |
| Success Rate >= 85.0% | >= 85.0% | 90.0% | **✅ PASS** |
| Timeout Rate <= 5.0% | <= 5.0% | 10.0% | **❌ FAIL** |
| Standoff Distance >= 0.45m | >= 0.45 m | 1.47 m | **✅ PASS** |
| Step Overhead on Baseline-Success <= 15.0% | <= 15.0% | 56.4% | **❌ FAIL** |

**Overall Status:** ⚠️ **ACTION REQUIRED: CRITERIA UNMET**

## Crash Forensics Log

Total non-success episodes analyzed: **51**

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

### [Seed 2005] Configuration: Baseline (Shield OFF) — Outcome: `OBSTACLE_COLLISION`
- **Steps:** 56 | **Reward:** -71.76 | **Min Clearance:** 0.117 m
- **Diagnostic Cause:** Obstacle collision at speed 3.62 m/s (min clearance 0.14m).
- **Last 5 Control Steps Telemetry:**
  ```
  Step | Pos [x, y, z]           | Vel [vx, vy, vz]        | Speed | Clr   | State    | Action Executed
  -----+-------------------------+-------------------------+-------+-------+----------+----------------
    52 | [ 0.40, -2.06, 1.50]    | [ 1.28,  2.43, -0.00]   |  2.75 |  0.17 | DISABLED | [0.43, 0.81, -0.00]
    53 | [ 0.38, -1.96, 1.50]    | [-0.41,  2.46, 0.01]    |  2.50 |  0.14 | DISABLED | [-0.14, 0.82, 0.00]
    54 | [ 0.48, -1.86, 1.50]    | [ 2.29,  2.43, -0.01]   |  3.34 |  0.13 | DISABLED | [0.77, 0.81, -0.00]
    55 | [ 0.60, -1.77, 1.50]    | [ 2.87,  2.27, -0.04]   |  3.65 |  0.15 | DISABLED | [0.96, 0.76, -0.01]
    56 | [ 0.48, -1.68, 1.50]    | [-2.97,  2.07, 0.02]    |  3.62 |  0.14 | DISABLED | [-0.99, 0.69, 0.01]
  ```

### [Seed 2006] Configuration: Baseline (Shield OFF) — Outcome: `OBSTACLE_COLLISION`
- **Steps:** 59 | **Reward:** -70.67 | **Min Clearance:** 0.11 m
- **Diagnostic Cause:** Obstacle collision at speed 3.40 m/s (min clearance 0.15m).
- **Last 5 Control Steps Telemetry:**
  ```
  Step | Pos [x, y, z]           | Vel [vx, vy, vz]        | Speed | Clr   | State    | Action Executed
  -----+-------------------------+-------------------------+-------+-------+----------+----------------
    55 | [-1.33, -1.80, 1.51]    | [-2.84,  2.00, -0.03]   |  3.48 |  0.14 | DISABLED | [-0.95, 0.67, -0.01]
    56 | [-1.37, -1.71, 1.51]    | [-1.15,  2.12, -0.01]   |  2.42 |  0.14 | DISABLED | [-0.39, 0.71, -0.00]
    57 | [-1.30, -1.63, 1.51]    | [ 1.80,  1.90, -0.04]   |  2.62 |  0.15 | DISABLED | [0.60, 0.63, -0.01]
    58 | [-1.39, -1.55, 1.51]    | [-2.12,  1.90, 0.01]    |  2.85 |  0.15 | DISABLED | [-0.71, 0.63, 0.00]
    59 | [-1.50, -1.47, 1.51]    | [-2.81,  1.92, -0.02]   |  3.40 |  0.15 | DISABLED | [-0.94, 0.64, -0.01]
  ```

### [Seed 2009] Configuration: Baseline (Shield OFF) — Outcome: `OBSTACLE_COLLISION`
- **Steps:** 34 | **Reward:** 38.35 | **Min Clearance:** 0.418 m
- **Diagnostic Cause:** Obstacle collision at speed 0.93 m/s (min clearance 0.42m).
- **Last 5 Control Steps Telemetry:**
  ```
  Step | Pos [x, y, z]           | Vel [vx, vy, vz]        | Speed | Clr   | State    | Action Executed
  -----+-------------------------+-------------------------+-------+-------+----------+----------------
    30 | [ 0.23, -4.79, 1.49]    | [ 0.38,  1.26, 0.00]    |  1.32 |  0.56 | DISABLED | [0.13, 0.42, 0.00]
    31 | [ 0.23, -4.74, 1.49]    | [ 0.09,  1.02, -0.00]   |  1.02 |  0.53 | DISABLED | [0.03, 0.34, -0.00]
    32 | [ 0.24, -4.71, 1.49]    | [ 0.35,  0.87, -0.01]   |  0.94 |  0.49 | DISABLED | [0.12, 0.29, -0.00]
    33 | [ 0.25, -4.67, 1.49]    | [ 0.12,  1.03, -0.02]   |  1.04 |  0.45 | DISABLED | [0.04, 0.34, -0.01]
    34 | [ 0.26, -4.63, 1.49]    | [ 0.34,  0.87, -0.01]   |  0.93 |  0.42 | DISABLED | [0.11, 0.29, -0.00]
  ```

### [Seed 2010] Configuration: Baseline (Shield OFF) — Outcome: `OBSTACLE_COLLISION`
- **Steps:** 68 | **Reward:** -191.58 | **Min Clearance:** 0.111 m
- **Diagnostic Cause:** Obstacle collision at speed 2.74 m/s (min clearance 0.15m).
- **Last 5 Control Steps Telemetry:**
  ```
  Step | Pos [x, y, z]           | Vel [vx, vy, vz]        | Speed | Clr   | State    | Action Executed
  -----+-------------------------+-------------------------+-------+-------+----------+----------------
    64 | [-0.89, -1.08, 1.48]    | [-1.30,  1.88, -0.08]   |  2.28 |  0.16 | DISABLED | [-0.43, 0.63, -0.03]
    65 | [-1.00, -1.01, 1.48]    | [-2.83,  1.74, -0.01]   |  3.32 |  0.16 | DISABLED | [-0.94, 0.58, -0.00]
    66 | [-0.90, -0.94, 1.48]    | [ 2.50,  1.73, -0.04]   |  3.04 |  0.13 | DISABLED | [0.83, 0.58, -0.01]
    67 | [-0.79, -0.86, 1.48]    | [ 2.55,  1.80, 0.01]    |  3.13 |  0.16 | DISABLED | [0.85, 0.60, 0.00]
    68 | [-0.71, -0.79, 1.47]    | [ 2.00,  1.87, -0.09]   |  2.74 |  0.15 | DISABLED | [0.67, 0.62, -0.03]
  ```

### [Seed 2011] Configuration: Baseline (Shield OFF) — Outcome: `OBSTACLE_COLLISION`
- **Steps:** 62 | **Reward:** -36.1 | **Min Clearance:** 0.108 m
- **Diagnostic Cause:** Obstacle collision at speed 2.90 m/s (min clearance 0.11m).
- **Last 5 Control Steps Telemetry:**
  ```
  Step | Pos [x, y, z]           | Vel [vx, vy, vz]        | Speed | Clr   | State    | Action Executed
  -----+-------------------------+-------------------------+-------+-------+----------+----------------
    58 | [-0.37, -1.81, 1.49]    | [ 2.37,  1.47, 0.02]    |  2.79 |  0.15 | DISABLED | [0.79, 0.49, 0.01]
    59 | [-0.36, -1.76, 1.49]    | [ 0.14,  1.27, -0.01]   |  1.28 |  0.13 | DISABLED | [0.04, 0.42, -0.00]
    60 | [-0.39, -1.71, 1.49]    | [-0.59,  1.15, -0.01]   |  1.29 |  0.15 | DISABLED | [-0.20, 0.38, -0.00]
    61 | [-0.34, -1.65, 1.49]    | [ 1.19,  1.45, -0.05]   |  1.88 |  0.15 | DISABLED | [0.40, 0.48, -0.02]
    62 | [-0.23, -1.59, 1.49]    | [ 2.54,  1.40, -0.08]   |  2.90 |  0.11 | DISABLED | [0.84, 0.47, -0.03]
  ```

### [Seed 2014] Configuration: Baseline (Shield OFF) — Outcome: `OBSTACLE_COLLISION`
- **Steps:** 39 | **Reward:** 76.39 | **Min Clearance:** 0.258 m
- **Diagnostic Cause:** Obstacle collision at speed 3.52 m/s (min clearance 0.26m).
- **Last 5 Control Steps Telemetry:**
  ```
  Step | Pos [x, y, z]           | Vel [vx, vy, vz]        | Speed | Clr   | State    | Action Executed
  -----+-------------------------+-------------------------+-------+-------+----------+----------------
    35 | [ 0.54, -3.91, 1.49]    | [ 0.80,  2.71, -0.01]   |  2.83 |  0.64 | DISABLED | [0.27, 0.90, -0.00]
    36 | [ 0.60, -3.81, 1.49]    | [ 1.46,  2.60, -0.01]   |  2.98 |  0.52 | DISABLED | [0.49, 0.87, -0.00]
    37 | [ 0.67, -3.70, 1.49]    | [ 1.80,  2.53, -0.01]   |  3.10 |  0.40 | DISABLED | [0.60, 0.84, -0.00]
    38 | [ 0.78, -3.60, 1.49]    | [ 2.51,  2.42, -0.00]   |  3.49 |  0.35 | DISABLED | [0.84, 0.81, -0.00]
    39 | [ 0.88, -3.50, 1.49]    | [ 2.56,  2.42, -0.01]   |  3.52 |  0.26 | DISABLED | [0.85, 0.81, -0.00]
  ```

### [Seed 2017] Configuration: Baseline (Shield OFF) — Outcome: `OBSTACLE_COLLISION`
- **Steps:** 92 | **Reward:** -249.53 | **Min Clearance:** 0.107 m
- **Diagnostic Cause:** Obstacle collision at speed 3.44 m/s (min clearance 0.12m).
- **Last 5 Control Steps Telemetry:**
  ```
  Step | Pos [x, y, z]           | Vel [vx, vy, vz]        | Speed | Clr   | State    | Action Executed
  -----+-------------------------+-------------------------+-------+-------+----------+----------------
    88 | [-2.16,  0.42, 1.50]    | [ 2.10,  1.37, 0.03]    |  2.50 |  0.13 | DISABLED | [0.70, 0.46, 0.01]
    89 | [-2.08,  0.48, 1.50]    | [ 1.91,  1.43, -0.05]   |  2.39 |  0.15 | DISABLED | [0.64, 0.48, -0.02]
    90 | [-1.99,  0.57, 1.50]    | [ 2.21,  2.06, -0.03]   |  3.02 |  0.13 | DISABLED | [0.74, 0.69, -0.01]
    91 | [-1.89,  0.65, 1.50]    | [ 2.37,  2.07, -0.00]   |  3.15 |  0.16 | DISABLED | [0.79, 0.69, -0.00]
    92 | [-1.78,  0.75, 1.50]    | [ 2.57,  2.29, 0.04]    |  3.44 |  0.12 | DISABLED | [0.86, 0.77, 0.01]
  ```

### [Seed 2018] Configuration: Baseline (Shield OFF) — Outcome: `OBSTACLE_COLLISION`
- **Steps:** 46 | **Reward:** 27.74 | **Min Clearance:** 0.127 m
- **Diagnostic Cause:** Obstacle collision at speed 2.38 m/s (min clearance 0.15m).
- **Last 5 Control Steps Telemetry:**
  ```
  Step | Pos [x, y, z]           | Vel [vx, vy, vz]        | Speed | Clr   | State    | Action Executed
  -----+-------------------------+-------------------------+-------+-------+----------+----------------
    42 | [-0.05, -3.20, 1.51]    | [ 0.78,  2.50, -0.01]   |  2.62 |  0.18 | DISABLED | [0.26, 0.83, -0.00]
    43 | [-0.06, -3.10, 1.51]    | [-0.28,  2.47, 0.04]    |  2.49 |  0.16 | DISABLED | [-0.09, 0.82, 0.01]
    44 | [-0.12, -2.99, 1.51]    | [-1.46,  2.62, 0.02]    |  3.00 |  0.13 | DISABLED | [-0.49, 0.87, 0.01]
    45 | [-0.14, -2.89, 1.51]    | [-0.46,  2.29, 0.02]    |  2.34 |  0.16 | DISABLED | [-0.15, 0.76, 0.01]
    46 | [-0.18, -2.80, 1.51]    | [-0.95,  2.19, 0.02]    |  2.38 |  0.15 | DISABLED | [-0.32, 0.73, 0.01]
  ```

### [Seed 2019] Configuration: Baseline (Shield OFF) — Outcome: `OBSTACLE_COLLISION`
- **Steps:** 31 | **Reward:** -5.33 | **Min Clearance:** 0.212 m
- **Diagnostic Cause:** Obstacle collision at speed 3.17 m/s (min clearance 0.21m).
- **Last 5 Control Steps Telemetry:**
  ```
  Step | Pos [x, y, z]           | Vel [vx, vy, vz]        | Speed | Clr   | State    | Action Executed
  -----+-------------------------+-------------------------+-------+-------+----------+----------------
    27 | [ 0.18, -4.80, 1.48]    | [ 2.65,  2.40, 0.01]    |  3.57 |  0.49 | DISABLED | [0.88, 0.80, 0.00]
    28 | [ 0.06, -4.71, 1.48]    | [-2.92,  2.12, -0.01]   |  3.61 |  0.41 | DISABLED | [-0.97, 0.71, -0.00]
    29 | [-0.06, -4.63, 1.49]    | [-2.88,  1.92, 0.05]    |  3.46 |  0.36 | DISABLED | [-0.96, 0.64, 0.02]
    30 | [-0.15, -4.55, 1.49]    | [-2.22,  1.92, 0.01]    |  2.94 |  0.33 | DISABLED | [-0.74, 0.64, 0.00]
    31 | [-0.04, -4.48, 1.49]    | [ 2.69,  1.67, -0.04]   |  3.17 |  0.21 | DISABLED | [0.90, 0.56, -0.01]
  ```

### [Seed 2020] Configuration: Baseline (Shield OFF) — Outcome: `OBSTACLE_COLLISION`
- **Steps:** 71 | **Reward:** -137.59 | **Min Clearance:** 0.115 m
- **Diagnostic Cause:** Obstacle collision at speed 2.94 m/s (min clearance 0.15m).
- **Last 5 Control Steps Telemetry:**
  ```
  Step | Pos [x, y, z]           | Vel [vx, vy, vz]        | Speed | Clr   | State    | Action Executed
  -----+-------------------------+-------------------------+-------+-------+----------+----------------
    67 | [-0.01, -0.68, 1.47]    | [ 0.40,  2.13, -0.04]   |  2.17 |  0.14 | DISABLED | [0.13, 0.71, -0.01]
    68 | [-0.01, -0.59, 1.47]    | [-0.09,  2.26, 0.01]    |  2.26 |  0.18 | DISABLED | [-0.03, 0.75, 0.00]
    69 | [ 0.02, -0.49, 1.48]    | [ 0.77,  2.29, 0.04]    |  2.42 |  0.16 | DISABLED | [0.26, 0.76, 0.01]
    70 | [ 0.02, -0.40, 1.48]    | [ 0.09,  2.27, 0.02]    |  2.28 |  0.15 | DISABLED | [0.03, 0.76, 0.01]
    71 | [-0.06, -0.30, 1.47]    | [-1.88,  2.27, -0.04]   |  2.94 |  0.15 | DISABLED | [-0.62, 0.76, -0.01]
  ```

### [Seed 2022] Configuration: Baseline (Shield OFF) — Outcome: `OBSTACLE_COLLISION`
- **Steps:** 33 | **Reward:** -20.35 | **Min Clearance:** 0.188 m
- **Diagnostic Cause:** Obstacle collision at speed 2.50 m/s (min clearance 0.19m).
- **Last 5 Control Steps Telemetry:**
  ```
  Step | Pos [x, y, z]           | Vel [vx, vy, vz]        | Speed | Clr   | State    | Action Executed
  -----+-------------------------+-------------------------+-------+-------+----------+----------------
    29 | [ 0.05, -5.02, 1.52]    | [-1.78,  2.38, 0.02]    |  2.97 |  0.61 | DISABLED | [-0.59, 0.79, 0.01]
    30 | [-0.01, -4.92, 1.52]    | [-1.41,  2.39, 0.01]    |  2.78 |  0.51 | DISABLED | [-0.47, 0.80, 0.00]
    31 | [-0.07, -4.81, 1.52]    | [-1.34,  2.56, -0.03]   |  2.89 |  0.40 | DISABLED | [-0.45, 0.85, -0.01]
    32 | [-0.06, -4.71, 1.52]    | [ 0.15,  2.50, -0.01]   |  2.50 |  0.29 | DISABLED | [0.05, 0.83, -0.00]
    33 | [-0.06, -4.61, 1.52]    | [ 0.07,  2.50, 0.01]    |  2.50 |  0.19 | DISABLED | [0.02, 0.83, 0.01]
  ```

### [Seed 2026] Configuration: Baseline (Shield OFF) — Outcome: `OBSTACLE_COLLISION`
- **Steps:** 67 | **Reward:** -112.1 | **Min Clearance:** 0.12 m
- **Diagnostic Cause:** Obstacle collision at speed 3.28 m/s (min clearance 0.15m).
- **Last 5 Control Steps Telemetry:**
  ```
  Step | Pos [x, y, z]           | Vel [vx, vy, vz]        | Speed | Clr   | State    | Action Executed
  -----+-------------------------+-------------------------+-------+-------+----------+----------------
    63 | [ 0.48, -1.18, 1.48]    | [ 1.03,  2.01, 0.02]    |  2.26 |  0.17 | DISABLED | [0.34, 0.67, 0.01]
    64 | [ 0.47, -1.09, 1.48]    | [-0.27,  2.14, -0.07]   |  2.15 |  0.16 | DISABLED | [-0.09, 0.71, -0.02]
    65 | [ 0.41, -0.99, 1.47]    | [-1.46,  2.22, -0.11]   |  2.66 |  0.13 | DISABLED | [-0.49, 0.74, -0.04]
    66 | [ 0.31, -0.90, 1.47]    | [-2.36,  2.27, -0.01]   |  3.28 |  0.16 | DISABLED | [-0.79, 0.76, -0.00]
    67 | [ 0.41, -0.81, 1.48]    | [ 2.55,  2.07, 0.03]    |  3.28 |  0.15 | DISABLED | [0.85, 0.69, 0.01]
  ```

### [Seed 2027] Configuration: Baseline (Shield OFF) — Outcome: `OBSTACLE_COLLISION`
- **Steps:** 39 | **Reward:** 69.37 | **Min Clearance:** 0.325 m
- **Diagnostic Cause:** Obstacle collision at speed 2.62 m/s (min clearance 0.33m).
- **Last 5 Control Steps Telemetry:**
  ```
  Step | Pos [x, y, z]           | Vel [vx, vy, vz]        | Speed | Clr   | State    | Action Executed
  -----+-------------------------+-------------------------+-------+-------+----------+----------------
    35 | [-0.05, -3.88, 1.50]    | [-0.80,  2.71, 0.01]    |  2.83 |  0.58 | DISABLED | [-0.27, 0.90, 0.00]
    36 | [-0.06, -3.77, 1.50]    | [-0.28,  2.78, 0.02]    |  2.80 |  0.51 | DISABLED | [-0.10, 0.93, 0.01]
    37 | [-0.09, -3.65, 1.50]    | [-0.60,  2.77, -0.01]   |  2.84 |  0.47 | DISABLED | [-0.20, 0.93, -0.00]
    38 | [-0.05, -3.54, 1.50]    | [ 0.85,  2.71, -0.01]   |  2.84 |  0.38 | DISABLED | [0.28, 0.90, -0.00]
    39 | [-0.03, -3.43, 1.50]    | [ 0.49,  2.57, 0.04]    |  2.62 |  0.33 | DISABLED | [0.16, 0.86, 0.01]
  ```

### [Seed 2028] Configuration: Baseline (Shield OFF) — Outcome: `OBSTACLE_COLLISION`
- **Steps:** 52 | **Reward:** -60.85 | **Min Clearance:** 0.125 m
- **Diagnostic Cause:** Obstacle collision at speed 2.19 m/s (min clearance 0.15m).
- **Last 5 Control Steps Telemetry:**
  ```
  Step | Pos [x, y, z]           | Vel [vx, vy, vz]        | Speed | Clr   | State    | Action Executed
  -----+-------------------------+-------------------------+-------+-------+----------+----------------
    48 | [ 0.11, -2.70, 1.50]    | [-0.63,  2.35, -0.01]   |  2.44 |  0.12 | DISABLED | [-0.21, 0.78, -0.00]
    49 | [ 0.16, -2.61, 1.50]    | [ 1.24,  2.30, -0.01]   |  2.61 |  0.13 | DISABLED | [0.41, 0.77, -0.00]
    50 | [ 0.23, -2.51, 1.50]    | [ 1.58,  2.23, 0.05]    |  2.73 |  0.13 | DISABLED | [0.53, 0.74, 0.02]
    51 | [ 0.32, -2.43, 1.50]    | [ 2.19,  2.01, 0.03]    |  2.97 |  0.16 | DISABLED | [0.73, 0.67, 0.01]
    52 | [ 0.33, -2.34, 1.50]    | [ 0.23,  2.17, 0.04]    |  2.19 |  0.15 | DISABLED | [0.08, 0.72, 0.01]
  ```

### [Seed 2029] Configuration: Baseline (Shield OFF) — Outcome: `OBSTACLE_COLLISION`
- **Steps:** 66 | **Reward:** -101.72 | **Min Clearance:** 0.116 m
- **Diagnostic Cause:** Obstacle collision at speed 2.29 m/s (min clearance 0.16m).
- **Last 5 Control Steps Telemetry:**
  ```
  Step | Pos [x, y, z]           | Vel [vx, vy, vz]        | Speed | Clr   | State    | Action Executed
  -----+-------------------------+-------------------------+-------+-------+----------+----------------
    62 | [-0.46, -1.43, 1.49]    | [-2.92,  1.86, -0.05]   |  3.46 |  0.14 | DISABLED | [-0.97, 0.62, -0.02]
    63 | [-0.58, -1.35, 1.49]    | [-2.87,  1.92, -0.02]   |  3.45 |  0.16 | DISABLED | [-0.96, 0.64, -0.01]
    64 | [-0.52, -1.27, 1.49]    | [ 1.43,  1.91, -0.03]   |  2.38 |  0.14 | DISABLED | [0.47, 0.64, -0.01]
    65 | [-0.47, -1.19, 1.49]    | [ 1.11,  2.03, -0.05]   |  2.31 |  0.17 | DISABLED | [0.37, 0.68, -0.02]
    66 | [-0.51, -1.10, 1.49]    | [-0.95,  2.08, 0.02]    |  2.29 |  0.16 | DISABLED | [-0.32, 0.69, 0.01]
  ```

### [Seed 2007] Configuration: Shield ON (Oracle) — Outcome: `TIMEOUT`
- **Steps:** 500 | **Reward:** -1120.27 | **Min Clearance:** 0.426 m
- **Diagnostic Cause:** Exceeded maximum episode limit (500 steps) without reaching goal.
- **Last 5 Control Steps Telemetry:**
  ```
  Step | Pos [x, y, z]           | Vel [vx, vy, vz]        | Speed | Clr   | State    | Action Executed
  -----+-------------------------+-------------------------+-------+-------+----------+----------------
   496 | [-0.08,  9.06, 1.50]    | [-1.50,  0.00, 0.00]    |  1.50 |  0.68 | REROUTE  | [-0.50, 0.00, 0.00]
   497 | [-0.14,  9.06, 1.50]    | [-1.50,  0.00, 0.00]    |  1.50 |  0.68 | REROUTE  | [-0.50, 0.00, 0.00]
   498 | [-0.20,  9.06, 1.50]    | [-1.50,  0.00, 0.00]    |  1.50 |  0.68 | REROUTE  | [-0.50, 0.00, 0.00]
   499 | [-0.27,  9.06, 1.50]    | [-1.50,  0.00, 0.00]    |  1.50 |  0.68 | REROUTE  | [-0.50, 0.00, 0.00]
   500 | [-0.33,  9.06, 1.50]    | [-1.50,  0.00, 0.00]    |  1.50 |  0.68 | REROUTE  | [-0.50, 0.00, 0.00]
  ```

### [Seed 2011] Configuration: Shield ON (Oracle) — Outcome: `TIMEOUT`
- **Steps:** 500 | **Reward:** -2668.5 | **Min Clearance:** 0.179 m
- **Diagnostic Cause:** Exceeded maximum episode limit (500 steps) without reaching goal.
- **Last 5 Control Steps Telemetry:**
  ```
  Step | Pos [x, y, z]           | Vel [vx, vy, vz]        | Speed | Clr   | State    | Action Executed
  -----+-------------------------+-------------------------+-------+-------+----------+----------------
   496 | [ 2.12, -0.70, 1.50]    | [ 0.00, -0.80, -0.00]   |  0.80 |  4.56 | RETREAT  | [0.00, -0.27, -0.00]
   497 | [ 2.12, -0.74, 1.50]    | [ 0.00, -0.80, -0.00]   |  0.80 |  4.56 | RETREAT  | [0.00, -0.27, -0.00]
   498 | [ 2.12, -0.77, 1.50]    | [ 0.00, -0.80, -0.00]   |  0.80 |  4.56 | RETREAT  | [0.00, -0.27, -0.00]
   499 | [ 2.12, -0.81, 1.50]    | [ 0.00, -0.80, -0.00]   |  0.80 |  4.56 | RETREAT  | [0.00, -0.27, -0.00]
   500 | [ 2.12, -0.84, 1.50]    | [ 0.00, -0.80, -0.00]   |  0.80 |  4.56 | SCAN     | [0.00, -0.27, -0.00]
  ```

### [Seed 2019] Configuration: Shield ON (Oracle) — Outcome: `TIMEOUT`
- **Steps:** 500 | **Reward:** -1531.13 | **Min Clearance:** 0.184 m
- **Diagnostic Cause:** Exceeded maximum episode limit (500 steps) without reaching goal.
- **Last 5 Control Steps Telemetry:**
  ```
  Step | Pos [x, y, z]           | Vel [vx, vy, vz]        | Speed | Clr   | State    | Action Executed
  -----+-------------------------+-------------------------+-------+-------+----------+----------------
   496 | [-1.10,  3.10, 1.50]    | [-0.75,  0.90, 0.01]    |  1.17 |  0.55 | NOMINAL  | [-0.25, 0.30, 0.00]
   497 | [-1.11,  3.13, 1.50]    | [-0.07,  0.81, 0.02]    |  0.82 |  0.47 | NOMINAL  | [-0.02, 0.27, 0.01]
   498 | [-1.10,  3.16, 1.50]    | [ 0.06,  0.59, -0.02]   |  0.60 |  0.44 | NOMINAL  | [0.02, 0.20, -0.01]
   499 | [-1.10,  3.16, 1.50]    | [ 0.00,  0.00, 0.00]    |  0.00 |  0.40 | BRAKE    | [0.00, 0.00, 0.00]
   500 | [-1.10,  3.16, 1.50]    | [ 0.00,  0.00, 0.00]    |  0.00 |  0.41 | SCAN     | [0.00, 0.00, 0.00]
  ```

### [Seed 2000] Configuration: Shield ON (Camera) — Outcome: `TIMEOUT`
- **Steps:** 500 | **Reward:** -2361.9 | **Min Clearance:** 0.233 m
- **Diagnostic Cause:** Exceeded maximum episode limit (500 steps) without reaching goal.
- **Last 5 Control Steps Telemetry:**
  ```
  Step | Pos [x, y, z]           | Vel [vx, vy, vz]        | Speed | Clr   | State    | Action Executed
  -----+-------------------------+-------------------------+-------+-------+----------+----------------
   496 | [-3.33, -1.07, 1.50]    | [ 1.50,  0.00, -0.00]   |  1.50 |  0.35 | REROUTE  | [0.50, 0.00, -0.00]
   497 | [-3.26, -1.06, 1.50]    | [ 1.50,  0.40, -0.00]   |  1.55 |  0.35 | REROUTE  | [0.50, 0.13, -0.00]
   498 | [-3.20, -1.06, 1.50]    | [ 1.50,  0.00, -0.00]   |  1.50 |  0.34 | REROUTE  | [0.50, 0.00, -0.00]
   499 | [-3.14, -1.06, 1.50]    | [ 1.50,  0.00, -0.00]   |  1.50 |  0.34 | REROUTE  | [0.50, 0.00, -0.00]
   500 | [-3.08, -1.06, 1.50]    | [ 1.50,  0.00, -0.00]   |  1.50 |  0.35 | REROUTE  | [0.50, 0.00, -0.00]
  ```

### [Seed 2001] Configuration: Shield ON (Camera) — Outcome: `OBSTACLE_COLLISION`
- **Steps:** 170 | **Reward:** -740.85 | **Min Clearance:** 0.326 m
- **Diagnostic Cause:** Obstacle collision at speed 1.50 m/s (min clearance 0.35m).
- **Last 5 Control Steps Telemetry:**
  ```
  Step | Pos [x, y, z]           | Vel [vx, vy, vz]        | Speed | Clr   | State    | Action Executed
  -----+-------------------------+-------------------------+-------+-------+----------+----------------
   166 | [-1.08, -0.98, 1.50]    | [-1.50,  0.00, 0.00]    |  1.50 |  0.35 | REROUTE  | [-0.50, 0.00, 0.00]
   167 | [-1.14, -0.97, 1.50]    | [-1.50,  0.40, 0.00]    |  1.55 |  0.35 | REROUTE  | [-0.50, 0.13, 0.00]
   168 | [-1.21, -0.97, 1.50]    | [-1.50,  0.00, 0.00]    |  1.50 |  0.34 | REROUTE  | [-0.50, 0.00, 0.00]
   169 | [-1.27, -0.97, 1.50]    | [-1.50,  0.00, 0.00]    |  1.50 |  0.34 | REROUTE  | [-0.50, 0.00, 0.00]
   170 | [-1.33, -0.97, 1.50]    | [-1.50,  0.00, 0.00]    |  1.50 |  0.35 | REROUTE  | [-0.50, 0.00, 0.00]
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

### [Seed 2003] Configuration: Shield ON (Camera) — Outcome: `TIMEOUT`
- **Steps:** 500 | **Reward:** -2518.32 | **Min Clearance:** 0.254 m
- **Diagnostic Cause:** Exceeded maximum episode limit (500 steps) without reaching goal.
- **Last 5 Control Steps Telemetry:**
  ```
  Step | Pos [x, y, z]           | Vel [vx, vy, vz]        | Speed | Clr   | State    | Action Executed
  -----+-------------------------+-------------------------+-------+-------+----------+----------------
   496 | [ 3.52, -1.12, 1.50]    | [ 0.00, -0.80, 0.00]    |  0.80 |  0.51 | RETREAT  | [0.00, -0.27, 0.00]
   497 | [ 3.52, -1.16, 1.50]    | [ 0.00, -0.80, 0.00]    |  0.80 |  0.54 | SCAN     | [0.00, -0.27, 0.00]
   498 | [ 3.46, -1.16, 1.50]    | [-1.50,  0.00, 0.00]    |  1.50 |  0.57 | REROUTE  | [-0.50, 0.00, 0.00]
   499 | [ 3.40, -1.14, 1.50]    | [-1.50,  0.40, 0.00]    |  1.55 |  0.58 | REROUTE  | [-0.50, 0.13, 0.00]
   500 | [ 3.34, -1.12, 1.50]    | [-1.50,  0.40, 0.00]    |  1.55 |  0.56 | REROUTE  | [-0.50, 0.13, 0.00]
  ```

### [Seed 2004] Configuration: Shield ON (Camera) — Outcome: `OBSTACLE_COLLISION`
- **Steps:** 97 | **Reward:** -252.17 | **Min Clearance:** 0.064 m
- **Diagnostic Cause:** Obstacle collision at speed 1.50 m/s (min clearance 0.06m).
- **Last 5 Control Steps Telemetry:**
  ```
  Step | Pos [x, y, z]           | Vel [vx, vy, vz]        | Speed | Clr   | State    | Action Executed
  -----+-------------------------+-------------------------+-------+-------+----------+----------------
    93 | [-1.29, -0.97, 1.50]    | [-1.50,  0.00, 0.01]    |  1.50 |  0.35 | REROUTE  | [-0.50, 0.00, 0.00]
    94 | [-1.35, -0.96, 1.50]    | [-1.50,  0.40, 0.01]    |  1.55 |  0.35 | REROUTE  | [-0.50, 0.13, 0.00]
    95 | [-1.41, -0.96, 1.50]    | [-1.50,  0.00, 0.01]    |  1.50 |  0.34 | REROUTE  | [-0.50, 0.00, 0.00]
    96 | [-1.48, -0.96, 1.50]    | [-1.50,  0.00, 0.01]    |  1.50 |  0.34 | REROUTE  | [-0.50, 0.00, 0.00]
    97 | [-1.54, -0.96, 1.50]    | [-1.50,  0.00, 0.01]    |  1.50 |  0.06 | REROUTE  | [-0.50, 0.00, 0.00]
  ```

### [Seed 2005] Configuration: Shield ON (Camera) — Outcome: `OBSTACLE_COLLISION`
- **Steps:** 99 | **Reward:** -248.58 | **Min Clearance:** 0.37 m
- **Diagnostic Cause:** Obstacle collision at speed 1.55 m/s (min clearance 0.37m).
- **Last 5 Control Steps Telemetry:**
  ```
  Step | Pos [x, y, z]           | Vel [vx, vy, vz]        | Speed | Clr   | State    | Action Executed
  -----+-------------------------+-------------------------+-------+-------+----------+----------------
    95 | [ 1.55, -1.01, 1.50]    | [ 1.50,  0.40, -0.01]   |  1.55 |  0.41 | REROUTE  | [0.50, 0.13, -0.00]
    96 | [ 1.62, -0.99, 1.50]    | [ 1.50,  0.40, -0.01]   |  1.55 |  0.40 | REROUTE  | [0.50, 0.13, -0.00]
    97 | [ 1.68, -0.97, 1.50]    | [ 1.50,  0.40, -0.01]   |  1.55 |  0.39 | REROUTE  | [0.50, 0.13, -0.00]
    98 | [ 1.74, -0.96, 1.50]    | [ 1.50,  0.40, -0.01]   |  1.55 |  0.38 | REROUTE  | [0.50, 0.13, -0.00]
    99 | [ 1.80, -0.94, 1.50]    | [ 1.50,  0.40, -0.01]   |  1.55 |  0.37 | REROUTE  | [0.50, 0.13, -0.00]
  ```

### [Seed 2006] Configuration: Shield ON (Camera) — Outcome: `OBSTACLE_COLLISION`
- **Steps:** 91 | **Reward:** -296.8 | **Min Clearance:** 0.403 m
- **Diagnostic Cause:** Obstacle collision at speed 1.50 m/s (min clearance 0.65m).
- **Last 5 Control Steps Telemetry:**
  ```
  Step | Pos [x, y, z]           | Vel [vx, vy, vz]        | Speed | Clr   | State    | Action Executed
  -----+-------------------------+-------------------------+-------+-------+----------+----------------
    87 | [-1.04, -1.48, 1.48]    | [-0.45,  1.13, -0.05]   |  1.22 |  0.88 | NOMINAL  | [-0.15, 0.38, -0.02]
    88 | [-0.96, -1.44, 1.48]    | [ 1.80,  0.81, -0.05]   |  1.97 |  0.83 | NOMINAL  | [0.60, 0.27, -0.02]
    89 | [-1.03, -1.40, 1.48]    | [-1.60,  1.01, -0.01]   |  1.89 |  0.80 | NOMINAL  | [-0.53, 0.34, -0.00]
    90 | [-1.05, -1.35, 1.48]    | [-0.52,  1.20, -0.01]   |  1.31 |  0.76 | NOMINAL  | [-0.17, 0.40, -0.00]
    91 | [-1.11, -1.32, 1.48]    | [-1.30,  0.74, -0.01]   |  1.50 |  0.65 | NOMINAL  | [-0.43, 0.25, -0.00]
  ```

### [Seed 2007] Configuration: Shield ON (Camera) — Outcome: `TIMEOUT`
- **Steps:** 500 | **Reward:** -2339.84 | **Min Clearance:** 0.258 m
- **Diagnostic Cause:** Exceeded maximum episode limit (500 steps) without reaching goal.
- **Last 5 Control Steps Telemetry:**
  ```
  Step | Pos [x, y, z]           | Vel [vx, vy, vz]        | Speed | Clr   | State    | Action Executed
  -----+-------------------------+-------------------------+-------+-------+----------+----------------
   496 | [-3.85, -1.22, 1.50]    | [ 0.00, -0.80, -0.00]   |  0.80 |  0.39 | RETREAT  | [0.00, -0.27, -0.00]
   497 | [-3.85, -1.25, 1.50]    | [ 0.00, -0.80, -0.00]   |  0.80 |  0.42 | SCAN     | [0.00, -0.27, -0.00]
   498 | [-3.79, -1.25, 1.50]    | [ 1.50,  0.00, -0.00]   |  1.50 |  0.46 | REROUTE  | [0.50, 0.00, -0.00]
   499 | [-3.73, -1.24, 1.50]    | [ 1.50,  0.40, -0.00]   |  1.55 |  0.46 | REROUTE  | [0.50, 0.13, -0.00]
   500 | [-3.66, -1.22, 1.50]    | [ 1.50,  0.40, -0.00]   |  1.55 |  0.45 | REROUTE  | [0.50, 0.13, -0.00]
  ```

### [Seed 2008] Configuration: Shield ON (Camera) — Outcome: `TIMEOUT`
- **Steps:** 500 | **Reward:** -2383.22 | **Min Clearance:** 0.286 m
- **Diagnostic Cause:** Exceeded maximum episode limit (500 steps) without reaching goal.
- **Last 5 Control Steps Telemetry:**
  ```
  Step | Pos [x, y, z]           | Vel [vx, vy, vz]        | Speed | Clr   | State    | Action Executed
  -----+-------------------------+-------------------------+-------+-------+----------+----------------
   496 | [ 2.97, -0.91, 1.50]    | [ 1.50,  0.00, 0.00]    |  1.50 |  0.32 | REROUTE  | [0.50, 0.00, 0.00]
   497 | [ 3.03, -0.91, 1.50]    | [ 1.50,  0.00, 0.00]    |  1.50 |  0.32 | REROUTE  | [0.50, 0.00, 0.00]
   498 | [ 3.09, -0.91, 1.50]    | [ 1.50,  0.00, 0.00]    |  1.50 |  0.31 | REROUTE  | [0.50, 0.00, 0.00]
   499 | [ 3.16, -0.91, 1.50]    | [ 1.50,  0.00, 0.00]    |  1.50 |  0.31 | REROUTE  | [0.50, 0.00, 0.00]
   500 | [ 3.22, -0.91, 1.50]    | [ 1.50,  0.00, 0.00]    |  1.50 |  0.31 | REROUTE  | [0.50, 0.00, 0.00]
  ```

### [Seed 2009] Configuration: Shield ON (Camera) — Outcome: `OBSTACLE_COLLISION`
- **Steps:** 99 | **Reward:** -273.35 | **Min Clearance:** 0.27 m
- **Diagnostic Cause:** Obstacle collision at speed 1.50 m/s (min clearance 0.27m).
- **Last 5 Control Steps Telemetry:**
  ```
  Step | Pos [x, y, z]           | Vel [vx, vy, vz]        | Speed | Clr   | State    | Action Executed
  -----+-------------------------+-------------------------+-------+-------+----------+----------------
    95 | [ 1.43, -1.05, 1.48]    | [ 0.00,  0.00, 0.00]    |  0.00 |  0.43 | SCAN     | [0.00, 0.00, 0.00]
    96 | [ 1.49, -1.05, 1.49]    | [ 1.50,  0.00, 0.03]    |  1.50 |  0.43 | REROUTE  | [0.50, 0.00, 0.01]
    97 | [ 1.55, -1.03, 1.49]    | [ 1.50,  0.40, 0.03]    |  1.55 |  0.44 | REROUTE  | [0.50, 0.13, 0.01]
    98 | [ 1.61, -1.02, 1.49]    | [ 1.50,  0.40, 0.03]    |  1.55 |  0.43 | REROUTE  | [0.50, 0.13, 0.01]
    99 | [ 1.68, -1.02, 1.49]    | [ 1.50,  0.00, 0.03]    |  1.50 |  0.27 | REROUTE  | [0.50, 0.00, 0.01]
  ```

### [Seed 2010] Configuration: Shield ON (Camera) — Outcome: `TIMEOUT`
- **Steps:** 500 | **Reward:** -2419.1 | **Min Clearance:** 0.186 m
- **Diagnostic Cause:** Exceeded maximum episode limit (500 steps) without reaching goal.
- **Last 5 Control Steps Telemetry:**
  ```
  Step | Pos [x, y, z]           | Vel [vx, vy, vz]        | Speed | Clr   | State    | Action Executed
  -----+-------------------------+-------------------------+-------+-------+----------+----------------
   496 | [-3.33, -1.16, 1.50]    | [ 1.50,  0.00, 0.00]    |  1.50 |  0.34 | REROUTE  | [0.50, 0.00, 0.00]
   497 | [-3.27, -1.16, 1.50]    | [ 1.50,  0.00, 0.00]    |  1.50 |  0.35 | REROUTE  | [0.50, 0.00, 0.00]
   498 | [-3.20, -1.14, 1.50]    | [ 1.50,  0.40, 0.00]    |  1.55 |  0.35 | REROUTE  | [0.50, 0.13, 0.00]
   499 | [-3.14, -1.14, 1.50]    | [ 1.50,  0.00, 0.00]    |  1.50 |  0.34 | REROUTE  | [0.50, 0.00, 0.00]
   500 | [-3.08, -1.14, 1.50]    | [ 1.50,  0.00, 0.00]    |  1.50 |  0.35 | REROUTE  | [0.50, 0.00, 0.00]
  ```

### [Seed 2011] Configuration: Shield ON (Camera) — Outcome: `OBSTACLE_COLLISION`
- **Steps:** 38 | **Reward:** 87.82 | **Min Clearance:** 2.137 m
- **Diagnostic Cause:** Obstacle collision at speed 2.88 m/s (min clearance 2.14m).
- **Last 5 Control Steps Telemetry:**
  ```
  Step | Pos [x, y, z]           | Vel [vx, vy, vz]        | Speed | Clr   | State    | Action Executed
  -----+-------------------------+-------------------------+-------+-------+----------+----------------
    34 | [-0.33, -3.94, 1.49]    | [-0.34,  2.86, 0.01]    |  2.88 |  2.59 | NOMINAL  | [-0.12, 0.95, 0.00]
    35 | [-0.34, -3.82, 1.49]    | [-0.27,  2.88, -0.01]   |  2.89 |  2.48 | NOMINAL  | [-0.09, 0.96, -0.00]
    36 | [-0.38, -3.70, 1.49]    | [-0.77,  2.87, -0.03]   |  2.97 |  2.36 | NOMINAL  | [-0.26, 0.96, -0.01]
    37 | [-0.39, -3.58, 1.49]    | [-0.32,  2.83, -0.00]   |  2.85 |  2.24 | NOMINAL  | [-0.11, 0.94, -0.00]
    38 | [-0.41, -3.46, 1.49]    | [-0.47,  2.84, -0.03]   |  2.88 |  2.14 | NOMINAL  | [-0.16, 0.95, -0.01]
  ```

### [Seed 2012] Configuration: Shield ON (Camera) — Outcome: `OBSTACLE_COLLISION`
- **Steps:** 44 | **Reward:** 60.19 | **Min Clearance:** 2.361 m
- **Diagnostic Cause:** Obstacle collision at speed 2.54 m/s (min clearance 2.36m).
- **Last 5 Control Steps Telemetry:**
  ```
  Step | Pos [x, y, z]           | Vel [vx, vy, vz]        | Speed | Clr   | State    | Action Executed
  -----+-------------------------+-------------------------+-------+-------+----------+----------------
    40 | [-0.21, -3.29, 1.50]    | [-0.09,  2.77, -0.00]   |  2.77 |  2.74 | NOMINAL  | [-0.03, 0.92, -0.00]
    41 | [-0.23, -3.18, 1.50]    | [-0.51,  2.82, 0.01]    |  2.86 |  2.63 | NOMINAL  | [-0.17, 0.94, 0.01]
    42 | [-0.14, -3.10, 1.50]    | [ 2.28,  1.95, 0.05]    |  3.00 |  2.52 | NOMINAL  | [0.76, 0.65, 0.02]
    43 | [-0.21, -3.02, 1.51]    | [-1.77,  1.75, 0.14]    |  2.49 |  2.43 | NOMINAL  | [-0.59, 0.58, 0.05]
    44 | [-0.29, -2.95, 1.51]    | [-1.83,  1.75, 0.06]    |  2.54 |  2.36 | NOMINAL  | [-0.61, 0.58, 0.02]
  ```

### [Seed 2013] Configuration: Shield ON (Camera) — Outcome: `OBSTACLE_COLLISION`
- **Steps:** 51 | **Reward:** 47.34 | **Min Clearance:** 0.425 m
- **Diagnostic Cause:** Obstacle collision at speed 1.70 m/s (min clearance 2.96m).
- **Last 5 Control Steps Telemetry:**
  ```
  Step | Pos [x, y, z]           | Vel [vx, vy, vz]        | Speed | Clr   | State    | Action Executed
  -----+-------------------------+-------------------------+-------+-------+----------+----------------
    47 | [ 0.02, -3.82, 1.48]    | [ 0.11,  1.33, -0.02]   |  1.34 |  2.46 | NOMINAL  | [0.04, 0.45, -0.01]
    48 | [ 0.02, -3.76, 1.48]    | [ 0.08,  1.40, -0.02]   |  1.40 |  3.11 | NOMINAL  | [0.03, 0.47, -0.01]
    49 | [ 0.03, -3.70, 1.48]    | [ 0.04,  1.42, -0.00]   |  1.42 |  3.05 | NOMINAL  | [0.01, 0.47, -0.00]
    50 | [ 0.03, -3.64, 1.48]    | [ 0.00,  1.52, -0.02]   |  1.52 |  3.03 | NOMINAL  | [0.00, 0.51, -0.01]
    51 | [ 0.02, -3.56, 1.48]    | [-0.09,  1.69, -0.01]   |  1.70 |  2.96 | NOMINAL  | [-0.03, 0.56, -0.01]
  ```

### [Seed 2014] Configuration: Shield ON (Camera) — Outcome: `TIMEOUT`
- **Steps:** 500 | **Reward:** -2362.78 | **Min Clearance:** 0.294 m
- **Diagnostic Cause:** Exceeded maximum episode limit (500 steps) without reaching goal.
- **Last 5 Control Steps Telemetry:**
  ```
  Step | Pos [x, y, z]           | Vel [vx, vy, vz]        | Speed | Clr   | State    | Action Executed
  -----+-------------------------+-------------------------+-------+-------+----------+----------------
   496 | [ 2.83, -0.92, 1.50]    | [ 1.50,  0.00, 0.00]    |  1.50 |  0.34 | REROUTE  | [0.50, 0.00, 0.00]
   497 | [ 2.89, -0.92, 1.50]    | [ 1.50,  0.00, 0.00]    |  1.50 |  0.34 | REROUTE  | [0.50, 0.00, 0.00]
   498 | [ 2.96, -0.92, 1.50]    | [ 1.50,  0.00, 0.00]    |  1.50 |  0.33 | REROUTE  | [0.50, 0.00, 0.00]
   499 | [ 3.02, -0.92, 1.50]    | [ 1.50,  0.00, 0.00]    |  1.50 |  0.33 | REROUTE  | [0.50, 0.00, 0.00]
   500 | [ 3.08, -0.92, 1.50]    | [ 1.50,  0.00, 0.00]    |  1.50 |  0.33 | REROUTE  | [0.50, 0.00, 0.00]
  ```

### [Seed 2015] Configuration: Shield ON (Camera) — Outcome: `TIMEOUT`
- **Steps:** 500 | **Reward:** -2310.4 | **Min Clearance:** 0.275 m
- **Diagnostic Cause:** Exceeded maximum episode limit (500 steps) without reaching goal.
- **Last 5 Control Steps Telemetry:**
  ```
  Step | Pos [x, y, z]           | Vel [vx, vy, vz]        | Speed | Clr   | State    | Action Executed
  -----+-------------------------+-------------------------+-------+-------+----------+----------------
   496 | [-2.46, -0.99, 1.50]    | [-1.50,  0.00, -0.00]   |  1.50 |  0.33 | REROUTE  | [-0.50, 0.00, -0.00]
   497 | [-2.52, -0.99, 1.50]    | [-1.50,  0.00, -0.00]   |  1.50 |  0.33 | REROUTE  | [-0.50, 0.00, -0.00]
   498 | [-2.58, -0.99, 1.50]    | [-1.50,  0.00, -0.00]   |  1.50 |  0.32 | REROUTE  | [-0.50, 0.00, -0.00]
   499 | [-2.64, -0.99, 1.50]    | [-1.50,  0.00, -0.00]   |  1.50 |  0.32 | REROUTE  | [-0.50, 0.00, -0.00]
   500 | [-2.71, -0.99, 1.50]    | [-1.50,  0.00, -0.00]   |  1.50 |  0.32 | REROUTE  | [-0.50, 0.00, -0.00]
  ```

### [Seed 2016] Configuration: Shield ON (Camera) — Outcome: `OBSTACLE_COLLISION`
- **Steps:** 61 | **Reward:** -57.98 | **Min Clearance:** 0.716 m
- **Diagnostic Cause:** Obstacle collision at speed 1.69 m/s (min clearance 0.72m).
- **Last 5 Control Steps Telemetry:**
  ```
  Step | Pos [x, y, z]           | Vel [vx, vy, vz]        | Speed | Clr   | State    | Action Executed
  -----+-------------------------+-------------------------+-------+-------+----------+----------------
    57 | [-0.21, -1.99, 1.48]    | [ 1.50,  1.50, -0.03]   |  2.12 |  0.90 | NOMINAL  | [0.50, 0.50, -0.01]
    58 | [-0.28, -1.95, 1.48]    | [-1.64,  1.10, 0.00]    |  1.98 |  0.83 | NOMINAL  | [-0.55, 0.37, 0.00]
    59 | [-0.35, -1.92, 1.48]    | [-1.72,  0.75, -0.05]   |  1.88 |  0.79 | NOMINAL  | [-0.57, 0.25, -0.02]
    60 | [-0.41, -1.87, 1.48]    | [-1.47,  1.05, 0.00]    |  1.81 |  0.76 | NOMINAL  | [-0.49, 0.35, 0.00]
    61 | [-0.48, -1.85, 1.48]    | [-1.59,  0.57, -0.02]   |  1.69 |  0.72 | NOMINAL  | [-0.53, 0.19, -0.01]
  ```

### [Seed 2017] Configuration: Shield ON (Camera) — Outcome: `TIMEOUT`
- **Steps:** 500 | **Reward:** -2679.86 | **Min Clearance:** 0.235 m
- **Diagnostic Cause:** Exceeded maximum episode limit (500 steps) without reaching goal.
- **Last 5 Control Steps Telemetry:**
  ```
  Step | Pos [x, y, z]           | Vel [vx, vy, vz]        | Speed | Clr   | State    | Action Executed
  -----+-------------------------+-------------------------+-------+-------+----------+----------------
   496 | [-3.50, -1.07, 1.50]    | [ 1.50,  0.40, 0.00]    |  1.55 |  0.38 | REROUTE  | [0.50, 0.13, 0.00]
   497 | [-3.44, -1.06, 1.50]    | [ 1.50,  0.40, 0.00]    |  1.55 |  0.36 | REROUTE  | [0.50, 0.13, 0.00]
   498 | [-3.38, -1.04, 1.50]    | [ 1.50,  0.40, 0.00]    |  1.55 |  0.35 | REROUTE  | [0.50, 0.13, 0.00]
   499 | [-3.31, -1.04, 1.50]    | [ 1.50,  0.00, 0.00]    |  1.50 |  0.34 | REROUTE  | [0.50, 0.00, 0.00]
   500 | [-3.25, -1.04, 1.50]    | [ 1.50,  0.00, 0.00]    |  1.50 |  0.34 | REROUTE  | [0.50, 0.00, 0.00]
  ```

### [Seed 2018] Configuration: Shield ON (Camera) — Outcome: `OBSTACLE_COLLISION`
- **Steps:** 76 | **Reward:** -176.57 | **Min Clearance:** 0.354 m
- **Diagnostic Cause:** Obstacle collision at speed 3.00 m/s (min clearance 2.09m).
- **Last 5 Control Steps Telemetry:**
  ```
  Step | Pos [x, y, z]           | Vel [vx, vy, vz]        | Speed | Clr   | State    | Action Executed
  -----+-------------------------+-------------------------+-------+-------+----------+----------------
    72 | [-0.28, -2.95, 1.50]    | [-1.50,  0.00, 0.01]    |  1.50 |  0.39 | REROUTE  | [-0.50, 0.00, 0.00]
    73 | [-0.34, -2.88, 1.50]    | [-1.50,  1.60, 0.01]    |  2.19 |  2.11 | REROUTE  | [-0.50, 0.53, 0.00]
    74 | [-0.43, -2.82, 1.50]    | [-2.11,  1.54, -0.02]   |  2.62 |  2.22 | NOMINAL  | [-0.70, 0.52, -0.01]
    75 | [-0.32, -2.75, 1.50]    | [ 2.52,  1.62, 0.05]    |  3.00 |  2.15 | NOMINAL  | [0.84, 0.54, 0.02]
    76 | [-0.21, -2.70, 1.50]    | [ 2.71,  1.30, 0.07]    |  3.00 |  2.09 | NOMINAL  | [0.90, 0.43, 0.02]
  ```

### [Seed 2019] Configuration: Shield ON (Camera) — Outcome: `OBSTACLE_COLLISION`
- **Steps:** 42 | **Reward:** 20.57 | **Min Clearance:** 0.434 m
- **Diagnostic Cause:** Obstacle collision at speed 2.95 m/s (min clearance 3.77m).
- **Last 5 Control Steps Telemetry:**
  ```
  Step | Pos [x, y, z]           | Vel [vx, vy, vz]        | Speed | Clr   | State    | Action Executed
  -----+-------------------------+-------------------------+-------+-------+----------+----------------
    38 | [ 0.65, -4.77, 1.48]    | [ 0.76,  2.07, -0.01]   |  2.20 |  3.18 | NOMINAL  | [0.25, 0.69, -0.00]
    39 | [ 0.67, -4.67, 1.48]    | [ 0.48,  2.52, -0.01]   |  2.56 |  4.10 | NOMINAL  | [0.16, 0.84, -0.00]
    40 | [ 0.65, -4.55, 1.48]    | [-0.28,  2.75, -0.03]   |  2.76 |  4.00 | NOMINAL  | [-0.09, 0.92, -0.01]
    41 | [ 0.65, -4.43, 1.48]    | [-0.14,  2.83, 0.01]    |  2.84 |  3.88 | NOMINAL  | [-0.04, 0.94, 0.00]
    42 | [ 0.61, -4.31, 1.48]    | [-0.78,  2.85, -0.04]   |  2.95 |  3.77 | NOMINAL  | [-0.26, 0.95, -0.01]
  ```

### [Seed 2020] Configuration: Shield ON (Camera) — Outcome: `TIMEOUT`
- **Steps:** 500 | **Reward:** -2328.22 | **Min Clearance:** 0.235 m
- **Diagnostic Cause:** Exceeded maximum episode limit (500 steps) without reaching goal.
- **Last 5 Control Steps Telemetry:**
  ```
  Step | Pos [x, y, z]           | Vel [vx, vy, vz]        | Speed | Clr   | State    | Action Executed
  -----+-------------------------+-------------------------+-------+-------+----------+----------------
   496 | [-2.46, -1.07, 1.50]    | [-1.50,  0.00, 0.00]    |  1.50 |  0.34 | REROUTE  | [-0.50, 0.00, 0.00]
   497 | [-2.53, -1.07, 1.50]    | [-1.50,  0.00, 0.00]    |  1.50 |  0.34 | REROUTE  | [-0.50, 0.00, 0.00]
   498 | [-2.59, -1.07, 1.50]    | [-1.50,  0.00, 0.00]    |  1.50 |  0.33 | REROUTE  | [-0.50, 0.00, 0.00]
   499 | [-2.65, -1.07, 1.50]    | [-1.50,  0.00, 0.00]    |  1.50 |  0.33 | REROUTE  | [-0.50, 0.00, 0.00]
   500 | [-2.71, -1.07, 1.50]    | [-1.50,  0.00, 0.00]    |  1.50 |  0.32 | REROUTE  | [-0.50, 0.00, 0.00]
  ```

### [Seed 2021] Configuration: Shield ON (Camera) — Outcome: `TIMEOUT`
- **Steps:** 500 | **Reward:** -2499.04 | **Min Clearance:** 0.254 m
- **Diagnostic Cause:** Exceeded maximum episode limit (500 steps) without reaching goal.
- **Last 5 Control Steps Telemetry:**
  ```
  Step | Pos [x, y, z]           | Vel [vx, vy, vz]        | Speed | Clr   | State    | Action Executed
  -----+-------------------------+-------------------------+-------+-------+----------+----------------
   496 | [-3.55, -1.05, 1.50]    | [ 0.00, -0.80, 0.00]    |  0.80 |  0.40 | RETREAT  | [0.00, -0.27, 0.00]
   497 | [-3.55, -1.08, 1.50]    | [ 0.00, -0.80, 0.00]    |  0.80 |  0.30 | RETREAT  | [0.00, -0.27, 0.00]
   498 | [-3.55, -1.11, 1.50]    | [ 0.00, -0.80, 0.00]    |  0.80 |  0.33 | RETREAT  | [0.00, -0.27, 0.00]
   499 | [-3.55, -1.15, 1.50]    | [ 0.00, -0.80, 0.00]    |  0.80 |  0.37 | RETREAT  | [0.00, -0.27, 0.00]
   500 | [-3.55, -1.18, 1.50]    | [ 0.00, -0.80, 0.00]    |  0.80 |  0.40 | RETREAT  | [0.00, -0.27, 0.00]
  ```

### [Seed 2022] Configuration: Shield ON (Camera) — Outcome: `OBSTACLE_COLLISION`
- **Steps:** 67 | **Reward:** -127.63 | **Min Clearance:** 0.419 m
- **Diagnostic Cause:** Obstacle collision at speed 2.75 m/s (min clearance 2.91m).
- **Last 5 Control Steps Telemetry:**
  ```
  Step | Pos [x, y, z]           | Vel [vx, vy, vz]        | Speed | Clr   | State    | Action Executed
  -----+-------------------------+-------------------------+-------+-------+----------+----------------
    63 | [ 0.81, -3.96, 1.49]    | [ 0.15,  2.09, -0.03]   |  2.10 |  2.62 | NOMINAL  | [0.05, 0.70, -0.01]
    64 | [ 0.81, -3.86, 1.49]    | [ 0.00,  2.36, 0.00]    |  2.36 |  2.53 | NOMINAL  | [0.00, 0.79, 0.00]
    65 | [ 0.80, -3.75, 1.49]    | [-0.22,  2.61, 0.00]    |  2.62 |  2.44 | NOMINAL  | [-0.07, 0.87, 0.00]
    66 | [ 0.81, -3.64, 1.49]    | [ 0.34,  2.69, -0.01]   |  2.72 |  3.09 | NOMINAL  | [0.11, 0.90, -0.00]
    67 | [ 0.80, -3.53, 1.49]    | [-0.35,  2.73, -0.02]   |  2.75 |  2.91 | NOMINAL  | [-0.12, 0.91, -0.01]
  ```

### [Seed 2023] Configuration: Shield ON (Camera) — Outcome: `OBSTACLE_COLLISION`
- **Steps:** 96 | **Reward:** -214.4 | **Min Clearance:** 0.303 m
- **Diagnostic Cause:** Obstacle collision at speed 1.50 m/s (min clearance 0.30m).
- **Last 5 Control Steps Telemetry:**
  ```
  Step | Pos [x, y, z]           | Vel [vx, vy, vz]        | Speed | Clr   | State    | Action Executed
  -----+-------------------------+-------------------------+-------+-------+----------+----------------
    92 | [-1.96, -0.96, 1.50]    | [-1.50,  0.00, 0.01]    |  1.50 |  0.32 | REROUTE  | [-0.50, 0.00, 0.00]
    93 | [-2.02, -0.96, 1.50]    | [-1.50,  0.00, 0.01]    |  1.50 |  0.32 | REROUTE  | [-0.50, 0.00, 0.00]
    94 | [-2.08, -0.96, 1.50]    | [-1.50,  0.00, 0.01]    |  1.50 |  0.31 | REROUTE  | [-0.50, 0.00, 0.00]
    95 | [-2.15, -0.96, 1.50]    | [-1.50,  0.00, 0.01]    |  1.50 |  0.31 | REROUTE  | [-0.50, 0.00, 0.00]
    96 | [-2.21, -0.96, 1.50]    | [-1.50,  0.00, 0.01]    |  1.50 |  0.30 | REROUTE  | [-0.50, 0.00, 0.00]
  ```

### [Seed 2024] Configuration: Shield ON (Camera) — Outcome: `OBSTACLE_COLLISION`
- **Steps:** 64 | **Reward:** -45.36 | **Min Clearance:** 0.478 m
- **Diagnostic Cause:** Obstacle collision at speed 0.84 m/s (min clearance 0.48m).
- **Last 5 Control Steps Telemetry:**
  ```
  Step | Pos [x, y, z]           | Vel [vx, vy, vz]        | Speed | Clr   | State    | Action Executed
  -----+-------------------------+-------------------------+-------+-------+----------+----------------
    60 | [-0.82, -1.98, 1.49]    | [-1.04,  0.65, -0.04]   |  1.23 |  0.57 | NOMINAL  | [-0.35, 0.22, -0.01]
    61 | [-0.77, -1.96, 1.49]    | [ 1.04,  0.44, 0.03]    |  1.13 |  0.54 | NOMINAL  | [0.35, 0.15, 0.01]
    62 | [-0.81, -1.94, 1.48]    | [-0.94,  0.47, -0.07]   |  1.05 |  0.52 | NOMINAL  | [-0.31, 0.16, -0.02]
    63 | [-0.84, -1.91, 1.48]    | [-0.72,  0.66, -0.03]   |  0.97 |  0.51 | NOMINAL  | [-0.24, 0.22, -0.01]
    64 | [-0.84, -1.88, 1.48]    | [ 0.03,  0.84, -0.03]   |  0.84 |  0.48 | NOMINAL  | [0.01, 0.28, -0.01]
  ```

### [Seed 2025] Configuration: Shield ON (Camera) — Outcome: `OBSTACLE_COLLISION`
- **Steps:** 58 | **Reward:** -28.46 | **Min Clearance:** 1.238 m
- **Diagnostic Cause:** Obstacle collision at speed 2.75 m/s (min clearance 1.24m).
- **Last 5 Control Steps Telemetry:**
  ```
  Step | Pos [x, y, z]           | Vel [vx, vy, vz]        | Speed | Clr   | State    | Action Executed
  -----+-------------------------+-------------------------+-------+-------+----------+----------------
    54 | [-1.27, -2.06, 1.51]    | [-2.82,  1.03, 0.01]    |  3.00 |  1.45 | NOMINAL  | [-0.94, 0.34, 0.00]
    55 | [-1.35, -2.01, 1.51]    | [-1.95,  1.11, 0.01]    |  2.25 |  1.40 | NOMINAL  | [-0.65, 0.37, 0.00]
    56 | [-1.44, -1.96, 1.52]    | [-2.21,  1.21, 0.04]    |  2.52 |  1.35 | NOMINAL  | [-0.73, 0.40, 0.01]
    57 | [-1.54, -1.91, 1.52]    | [-2.36,  1.21, 0.03]    |  2.65 |  1.29 | NOMINAL  | [-0.79, 0.40, 0.01]
    58 | [-1.65, -1.86, 1.52]    | [-2.50,  1.15, 0.02]    |  2.75 |  1.24 | NOMINAL  | [-0.83, 0.38, 0.01]
  ```

### [Seed 2026] Configuration: Shield ON (Camera) — Outcome: `TIMEOUT`
- **Steps:** 500 | **Reward:** -2310.62 | **Min Clearance:** 0.259 m
- **Diagnostic Cause:** Exceeded maximum episode limit (500 steps) without reaching goal.
- **Last 5 Control Steps Telemetry:**
  ```
  Step | Pos [x, y, z]           | Vel [vx, vy, vz]        | Speed | Clr   | State    | Action Executed
  -----+-------------------------+-------------------------+-------+-------+----------+----------------
   496 | [-1.78, -1.21, 1.50]    | [-1.50,  0.40, 0.00]    |  1.55 |  0.53 | REROUTE  | [-0.50, 0.13, 0.00]
   497 | [-1.84, -1.19, 1.50]    | [-1.50,  0.40, 0.00]    |  1.55 |  0.51 | REROUTE  | [-0.50, 0.13, 0.00]
   498 | [-1.91, -1.18, 1.50]    | [-1.50,  0.40, 0.00]    |  1.55 |  0.49 | REROUTE  | [-0.50, 0.13, 0.00]
   499 | [-1.97, -1.16, 1.50]    | [-1.50,  0.40, 0.00]    |  1.55 |  0.47 | REROUTE  | [-0.50, 0.13, 0.00]
   500 | [-2.03, -1.14, 1.50]    | [-1.50,  0.40, 0.00]    |  1.55 |  0.45 | REROUTE  | [-0.50, 0.13, 0.00]
  ```

### [Seed 2027] Configuration: Shield ON (Camera) — Outcome: `OBSTACLE_COLLISION`
- **Steps:** 45 | **Reward:** 54.66 | **Min Clearance:** 0.254 m
- **Diagnostic Cause:** Obstacle collision at speed 2.60 m/s (min clearance 2.98m).
- **Last 5 Control Steps Telemetry:**
  ```
  Step | Pos [x, y, z]           | Vel [vx, vy, vz]        | Speed | Clr   | State    | Action Executed
  -----+-------------------------+-------------------------+-------+-------+----------+----------------
    41 | [-0.01, -3.88, 1.50]    | [-1.50,  0.00, 0.01]    |  1.50 |  0.25 | REROUTE  | [-0.50, 0.00, 0.00]
    42 | [-0.07, -3.81, 1.50]    | [-1.50,  1.60, 0.01]    |  2.19 |  3.20 | REROUTE  | [-0.50, 0.53, 0.00]
    43 | [-0.14, -3.73, 1.50]    | [-1.60,  1.92, -0.01]   |  2.50 |  3.13 | NOMINAL  | [-0.53, 0.64, -0.00]
    44 | [-0.06, -3.65, 1.50]    | [ 1.90,  1.89, -0.00]   |  2.68 |  3.06 | NOMINAL  | [0.63, 0.63, -0.00]
    45 | [ 0.02, -3.58, 1.49]    | [ 1.83,  1.85, -0.03]   |  2.60 |  2.98 | NOMINAL  | [0.61, 0.62, -0.01]
  ```

### [Seed 2028] Configuration: Shield ON (Camera) — Outcome: `OBSTACLE_COLLISION`
- **Steps:** 69 | **Reward:** -148.38 | **Min Clearance:** 0.401 m
- **Diagnostic Cause:** Obstacle collision at speed 1.23 m/s (min clearance 1.38m).
- **Last 5 Control Steps Telemetry:**
  ```
  Step | Pos [x, y, z]           | Vel [vx, vy, vz]        | Speed | Clr   | State    | Action Executed
  -----+-------------------------+-------------------------+-------+-------+----------+----------------
    65 | [ 0.60, -2.22, 1.49]    | [ 1.09,  1.71, 0.02]    |  2.03 |  1.63 | NOMINAL  | [0.36, 0.57, 0.01]
    66 | [ 0.57, -2.16, 1.49]    | [-0.81,  1.57, 0.02]    |  1.77 |  1.56 | NOMINAL  | [-0.27, 0.52, 0.01]
    67 | [ 0.50, -2.10, 1.49]    | [-1.58,  1.44, -0.01]   |  2.14 |  1.50 | NOMINAL  | [-0.53, 0.48, -0.00]
    68 | [ 0.51, -2.04, 1.49]    | [ 0.14,  1.49, -0.00]   |  1.50 |  1.44 | NOMINAL  | [0.05, 0.50, -0.00]
    69 | [ 0.49, -1.99, 1.50]    | [-0.54,  1.10, 0.06]    |  1.23 |  1.38 | NOMINAL  | [-0.18, 0.37, 0.02]
  ```

### [Seed 2029] Configuration: Shield ON (Camera) — Outcome: `OBSTACLE_COLLISION`
- **Steps:** 43 | **Reward:** 72.46 | **Min Clearance:** 0.791 m
- **Diagnostic Cause:** Obstacle collision at speed 3.00 m/s (min clearance 2.65m).
- **Last 5 Control Steps Telemetry:**
  ```
  Step | Pos [x, y, z]           | Vel [vx, vy, vz]        | Speed | Clr   | State    | Action Executed
  -----+-------------------------+-------------------------+-------+-------+----------+----------------
    39 | [ 0.18, -3.91, 1.49]    | [ 0.20,  2.55, 0.00]    |  2.56 |  3.03 | NOMINAL  | [0.07, 0.85, 0.00]
    40 | [ 0.19, -3.80, 1.49]    | [ 0.08,  2.54, -0.04]   |  2.54 |  2.94 | NOMINAL  | [0.03, 0.85, -0.01]
    41 | [ 0.18, -3.69, 1.49]    | [-0.19,  2.60, -0.05]   |  2.61 |  2.84 | NOMINAL  | [-0.06, 0.87, -0.02]
    42 | [ 0.20, -3.58, 1.49]    | [ 0.58,  2.67, -0.03]   |  2.73 |  2.73 | NOMINAL  | [0.19, 0.89, -0.01]
    43 | [ 0.12, -3.49, 1.49]    | [-2.05,  2.19, 0.01]    |  3.00 |  2.65 | NOMINAL  | [-0.68, 0.73, 0.00]
  ```
