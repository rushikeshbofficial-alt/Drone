# Stop, Hover & Re-Route (SHR) Drone Safety Shield Benchmark Report

**Date:** 2026-10-16T06:12:30Z  
**Seeds:** `4000-4059` (60 episodes)  
**Checkpoint:** `best_model_baseline.pt`  

## Executive Summary & Comparison Table

| Metric | Baseline (OFF) | Shield ON (Oracle) | Shield ON (Camera) | Target |
|---|:---:|:---:|:---:|:---:|
| **Success Rate (95% CI)** |  28.3% [18.5%, 40.8%] (17/60) |  75.0% [62.8%, 84.2%] (45/60) |   0.0% [ 0.0%,  6.0%] (0/60) | **>= 85.0%** |
| **Total Collision Rate** |  71.7% [59.2%, 81.5%] (43/60) |   0.0% [ 0.0%,  6.0%] (0/60) |  53.3% [40.9%, 65.4%] (32/60) | **<= 2.0%** |
| Obstacle Collisions |  71.7% [59.2%, 81.5%] (43/60) |   0.0% [ 0.0%,  6.0%] (0/60) |  53.3% [40.9%, 65.4%] (32/60) | — |
| Wall OOB Collisions |   0.0% [ 0.0%,  6.0%] (0/60) |   0.0% [ 0.0%,  6.0%] (0/60) |   0.0% [ 0.0%,  6.0%] (0/60) | — |
| Timeout Rate |   0.0% [ 0.0%,  6.0%] (0/60) |  25.0% [15.8%, 37.2%] (15/60) |  46.7% [34.6%, 59.1%] (28/60) | **<= 5.0%** |
| **Mean Reward** | -18.73 +/- 164.74 | -623.99 +/- 860.57 | -1246.37 +/- 1192.39 | — |
| **Mean Min Clearance** | 0.14 m | 0.38 m | 0.62 m | — |
| **Mean Episode Steps** | 89.4 | 310.2 | 275.6 | — |
| **Standoff Distance** | N/A | 2.18 m | 0.56 m | **>= 0.45 m** |
| **Step Overhead (Baseline Succ)** | Baseline | 67.79% | 178.68% | **<= 15.0%** |

## Acceptance Criteria Audit

| Criterion | Target | Achieved (Oracle) | Verdict |
|---|:---:|:---:|:---:|
| Total Collisions <= 2.0% | <= 2.0% | 0.0% | **✅ PASS** |
| Success Rate >= 85.0% | >= 85.0% | 75.0% | **❌ FAIL** |
| Timeout Rate <= 5.0% | <= 5.0% | 25.0% | **❌ FAIL** |
| Standoff Distance >= 0.45m | >= 0.45 m | 2.18 m | **✅ PASS** |
| Step Overhead on Baseline-Success <= 15.0% | <= 15.0% | 67.8% | **❌ FAIL** |

**Overall Status:** ⚠️ **ACTION REQUIRED: CRITERIA UNMET**

## Crash Forensics Log

Total non-success episodes analyzed: **118**

### [Seed 4000] Configuration: Baseline (Shield OFF) — Outcome: `OBSTACLE_COLLISION`
- **Steps:** 47 | **Reward:** 4.23 | **Min Clearance:** 0.164 m
- **Diagnostic Cause:** Obstacle collision at speed 3.67 m/s (min clearance 0.16m).
- **Last 5 Control Steps Telemetry:**
  ```
  Step | Pos [x, y, z]           | Vel [vx, vy, vz]        | Speed | Clr   | State    | Action Executed
  -----+-------------------------+-------------------------+-------+-------+----------+----------------
    43 | [ 1.15, -3.20, 1.50]    | [ 0.07,  2.24, 0.02]    |  2.24 |  0.37 | DISABLED | [0.02, 0.74, 0.01]
    44 | [ 1.16, -3.10, 1.50]    | [ 0.16,  2.48, -0.01]   |  2.49 |  0.36 | DISABLED | [0.06, 0.83, -0.01]
    45 | [ 1.10, -2.99, 1.50]    | [-1.36,  2.50, 0.03]    |  2.84 |  0.38 | DISABLED | [-0.45, 0.83, 0.01]
    46 | [ 1.15, -2.89, 1.51]    | [ 1.32,  2.55, 0.02]    |  2.88 |  0.32 | DISABLED | [0.44, 0.85, 0.01]
    47 | [ 1.27, -2.79, 1.51]    | [ 2.71,  2.47, -0.01]   |  3.67 |  0.16 | DISABLED | [0.91, 0.82, -0.00]
  ```

### [Seed 4001] Configuration: Baseline (Shield OFF) — Outcome: `OBSTACLE_COLLISION`
- **Steps:** 99 | **Reward:** -251.29 | **Min Clearance:** 0.105 m
- **Diagnostic Cause:** Obstacle collision at speed 2.50 m/s (min clearance 0.14m).
- **Last 5 Control Steps Telemetry:**
  ```
  Step | Pos [x, y, z]           | Vel [vx, vy, vz]        | Speed | Clr   | State    | Action Executed
  -----+-------------------------+-------------------------+-------+-------+----------+----------------
    95 | [-1.28,  0.46, 1.51]    | [ 2.83,  2.00, 0.05]    |  3.47 |  0.14 | DISABLED | [0.94, 0.67, 0.02]
    96 | [-1.21,  0.55, 1.51]    | [ 1.83,  2.08, -0.00]   |  2.78 |  0.13 | DISABLED | [0.61, 0.69, -0.00]
    97 | [-1.10,  0.63, 1.51]    | [ 2.48,  2.00, -0.01]   |  3.19 |  0.12 | DISABLED | [0.83, 0.67, -0.00]
    98 | [-1.10,  0.71, 1.51]    | [ 0.09,  1.88, 0.01]    |  1.88 |  0.15 | DISABLED | [0.03, 0.63, 0.00]
    99 | [-1.17,  0.78, 1.51]    | [-1.74,  1.79, -0.01]   |  2.50 |  0.14 | DISABLED | [-0.58, 0.60, -0.00]
  ```

### [Seed 4002] Configuration: Baseline (Shield OFF) — Outcome: `OBSTACLE_COLLISION`
- **Steps:** 106 | **Reward:** -362.54 | **Min Clearance:** 0.123 m
- **Diagnostic Cause:** Obstacle collision at speed 2.15 m/s (min clearance 0.14m).
- **Last 5 Control Steps Telemetry:**
  ```
  Step | Pos [x, y, z]           | Vel [vx, vy, vz]        | Speed | Clr   | State    | Action Executed
  -----+-------------------------+-------------------------+-------+-------+----------+----------------
   102 | [ 0.28,  0.08, 1.50]    | [-0.04,  2.05, -0.01]   |  2.05 |  0.15 | DISABLED | [-0.01, 0.68, -0.00]
   103 | [ 0.18,  0.16, 1.49]    | [-2.34,  2.02, -0.06]   |  3.09 |  0.15 | DISABLED | [-0.78, 0.67, -0.02]
   104 | [ 0.07,  0.24, 1.49]    | [-2.75,  1.98, 0.01]    |  3.39 |  0.14 | DISABLED | [-0.92, 0.66, 0.00]
   105 | [ 0.02,  0.32, 1.49]    | [-1.16,  1.87, -0.06]   |  2.20 |  0.15 | DISABLED | [-0.39, 0.62, -0.02]
   106 | [-0.02,  0.40, 1.49]    | [-0.94,  1.94, 0.04]    |  2.15 |  0.14 | DISABLED | [-0.31, 0.65, 0.01]
  ```

### [Seed 4004] Configuration: Baseline (Shield OFF) — Outcome: `OBSTACLE_COLLISION`
- **Steps:** 24 | **Reward:** 6.58 | **Min Clearance:** 0.271 m
- **Diagnostic Cause:** Obstacle collision at speed 2.92 m/s (min clearance 0.27m).
- **Last 5 Control Steps Telemetry:**
  ```
  Step | Pos [x, y, z]           | Vel [vx, vy, vz]        | Speed | Clr   | State    | Action Executed
  -----+-------------------------+-------------------------+-------+-------+----------+----------------
    20 | [-0.30, -5.74, 1.50]    | [-2.78,  2.29, 0.03]    |  3.61 |  0.80 | DISABLED | [-0.93, 0.77, 0.01]
    21 | [-0.40, -5.63, 1.50]    | [-2.43,  2.58, -0.00]   |  3.54 |  0.63 | DISABLED | [-0.81, 0.86, -0.00]
    22 | [-0.48, -5.52, 1.50]    | [-1.88,  2.78, -0.01]   |  3.35 |  0.48 | DISABLED | [-0.63, 0.93, -0.00]
    23 | [-0.52, -5.40, 1.50]    | [-0.84,  2.88, 0.08]    |  3.00 |  0.37 | DISABLED | [-0.28, 0.96, 0.03]
    24 | [-0.55, -5.28, 1.50]    | [-0.75,  2.82, -0.01]   |  2.92 |  0.27 | DISABLED | [-0.25, 0.94, -0.00]
  ```

### [Seed 4005] Configuration: Baseline (Shield OFF) — Outcome: `OBSTACLE_COLLISION`
- **Steps:** 42 | **Reward:** 48.96 | **Min Clearance:** 0.132 m
- **Diagnostic Cause:** Obstacle collision at speed 3.61 m/s (min clearance 0.16m).
- **Last 5 Control Steps Telemetry:**
  ```
  Step | Pos [x, y, z]           | Vel [vx, vy, vz]        | Speed | Clr   | State    | Action Executed
  -----+-------------------------+-------------------------+-------+-------+----------+----------------
    38 | [-0.06, -3.52, 1.52]    | [-0.87,  2.79, -0.01]   |  2.92 |  0.40 | DISABLED | [-0.29, 0.93, -0.00]
    39 | [-0.07, -3.41, 1.52]    | [-0.13,  2.72, 0.01]    |  2.73 |  0.31 | DISABLED | [-0.04, 0.91, 0.00]
    40 | [-0.03, -3.30, 1.52]    | [ 0.86,  2.60, -0.00]   |  2.73 |  0.23 | DISABLED | [0.29, 0.87, -0.00]
    41 | [ 0.04, -3.19, 1.52]    | [ 1.75,  2.62, -0.00]   |  3.15 |  0.13 | DISABLED | [0.58, 0.87, -0.00]
    42 | [ 0.15, -3.09, 1.52]    | [ 2.70,  2.40, -0.00]   |  3.61 |  0.16 | DISABLED | [0.90, 0.80, -0.00]
  ```

### [Seed 4008] Configuration: Baseline (Shield OFF) — Outcome: `OBSTACLE_COLLISION`
- **Steps:** 23 | **Reward:** -24.98 | **Min Clearance:** 0.266 m
- **Diagnostic Cause:** Obstacle collision at speed 3.07 m/s (min clearance 0.27m).
- **Last 5 Control Steps Telemetry:**
  ```
  Step | Pos [x, y, z]           | Vel [vx, vy, vz]        | Speed | Clr   | State    | Action Executed
  -----+-------------------------+-------------------------+-------+-------+----------+----------------
    19 | [-0.10, -5.78, 1.50]    | [ 0.05,  2.83, 0.02]    |  2.83 |  0.59 | DISABLED | [0.02, 0.94, 0.01]
    20 | [-0.10, -5.66, 1.51]    | [-0.12,  2.82, 0.03]    |  2.82 |  0.49 | DISABLED | [-0.04, 0.94, 0.01]
    21 | [-0.09, -5.54, 1.51]    | [ 0.32,  2.80, -0.01]   |  2.82 |  0.39 | DISABLED | [0.11, 0.93, -0.00]
    22 | [-0.05, -5.43, 1.51]    | [ 0.95,  2.79, 0.03]    |  2.94 |  0.27 | DISABLED | [0.32, 0.93, 0.01]
    23 | [-0.13, -5.32, 1.51]    | [-1.83,  2.47, -0.00]   |  3.07 |  0.27 | DISABLED | [-0.61, 0.82, -0.00]
  ```

### [Seed 4009] Configuration: Baseline (Shield OFF) — Outcome: `OBSTACLE_COLLISION`
- **Steps:** 82 | **Reward:** -126.47 | **Min Clearance:** 0.091 m
- **Diagnostic Cause:** Obstacle collision at speed 2.74 m/s (min clearance 0.09m).
- **Last 5 Control Steps Telemetry:**
  ```
  Step | Pos [x, y, z]           | Vel [vx, vy, vz]        | Speed | Clr   | State    | Action Executed
  -----+-------------------------+-------------------------+-------+-------+----------+----------------
    78 | [ 2.51,  0.47, 1.50]    | [ 2.00,  2.52, 0.00]    |  3.22 |  0.13 | DISABLED | [0.67, 0.84, 0.00]
    79 | [ 2.58,  0.57, 1.50]    | [ 1.80,  2.38, 0.05]    |  2.98 |  0.12 | DISABLED | [0.60, 0.79, 0.02]
    80 | [ 2.65,  0.67, 1.50]    | [ 1.57,  2.45, 0.01]    |  2.90 |  0.11 | DISABLED | [0.52, 0.82, 0.00]
    81 | [ 2.68,  0.78, 1.50]    | [ 0.70,  2.63, 0.02]    |  2.72 |  0.11 | DISABLED | [0.23, 0.88, 0.01]
    82 | [ 2.67,  0.89, 1.50]    | [-0.12,  2.74, 0.00]    |  2.74 |  0.09 | DISABLED | [-0.04, 0.91, 0.00]
  ```

### [Seed 4011] Configuration: Baseline (Shield OFF) — Outcome: `OBSTACLE_COLLISION`
- **Steps:** 60 | **Reward:** -22.56 | **Min Clearance:** 0.108 m
- **Diagnostic Cause:** Obstacle collision at speed 3.06 m/s (min clearance 0.12m).
- **Last 5 Control Steps Telemetry:**
  ```
  Step | Pos [x, y, z]           | Vel [vx, vy, vz]        | Speed | Clr   | State    | Action Executed
  -----+-------------------------+-------------------------+-------+-------+----------+----------------
    56 | [-1.03, -1.63, 1.49]    | [-0.12,  2.04, 0.01]    |  2.04 |  0.15 | DISABLED | [-0.04, 0.68, 0.01]
    57 | [-1.01, -1.54, 1.49]    | [ 0.43,  2.11, 0.03]    |  2.16 |  0.12 | DISABLED | [0.14, 0.70, 0.01]
    58 | [-1.08, -1.45, 1.50]    | [-1.78,  2.20, 0.02]    |  2.83 |  0.15 | DISABLED | [-0.59, 0.73, 0.01]
    59 | [-1.15, -1.36, 1.50]    | [-1.46,  2.27, 0.00]    |  2.70 |  0.14 | DISABLED | [-0.49, 0.76, 0.00]
    60 | [-1.23, -1.26, 1.49]    | [-2.06,  2.26, -0.01]   |  3.06 |  0.12 | DISABLED | [-0.69, 0.75, -0.00]
  ```

### [Seed 4012] Configuration: Baseline (Shield OFF) — Outcome: `OBSTACLE_COLLISION`
- **Steps:** 91 | **Reward:** -251.75 | **Min Clearance:** 0.113 m
- **Diagnostic Cause:** Obstacle collision at speed 2.08 m/s (min clearance 0.17m).
- **Last 5 Control Steps Telemetry:**
  ```
  Step | Pos [x, y, z]           | Vel [vx, vy, vz]        | Speed | Clr   | State    | Action Executed
  -----+-------------------------+-------------------------+-------+-------+----------+----------------
    87 | [-0.44,  0.20, 1.49]    | [ 1.25,  1.46, -0.04]   |  1.92 |  0.16 | DISABLED | [0.42, 0.49, -0.01]
    88 | [-0.39,  0.26, 1.49]    | [ 1.21,  1.43, -0.03]   |  1.87 |  0.16 | DISABLED | [0.40, 0.48, -0.01]
    89 | [-0.48,  0.34, 1.49]    | [-2.03,  1.83, -0.04]   |  2.74 |  0.16 | DISABLED | [-0.68, 0.61, -0.01]
    90 | [-0.45,  0.41, 1.49]    | [ 0.69,  1.70, -0.09]   |  1.83 |  0.17 | DISABLED | [0.23, 0.57, -0.03]
    91 | [-0.40,  0.48, 1.49]    | [ 1.15,  1.73, -0.02]   |  2.08 |  0.17 | DISABLED | [0.38, 0.58, -0.01]
  ```

### [Seed 4015] Configuration: Baseline (Shield OFF) — Outcome: `OBSTACLE_COLLISION`
- **Steps:** 51 | **Reward:** 26.3 | **Min Clearance:** 0.291 m
- **Diagnostic Cause:** Obstacle collision at speed 2.78 m/s (min clearance 0.29m).
- **Last 5 Control Steps Telemetry:**
  ```
  Step | Pos [x, y, z]           | Vel [vx, vy, vz]        | Speed | Clr   | State    | Action Executed
  -----+-------------------------+-------------------------+-------+-------+----------+----------------
    47 | [ 1.97, -2.68, 1.48]    | [ 0.72,  2.42, -0.03]   |  2.53 |  0.42 | DISABLED | [0.24, 0.81, -0.01]
    48 | [ 1.98, -2.57, 1.48]    | [ 0.21,  2.51, -0.01]   |  2.52 |  0.42 | DISABLED | [0.07, 0.84, -0.01]
    49 | [ 2.00, -2.46, 1.48]    | [ 0.34,  2.65, 0.00]    |  2.67 |  0.40 | DISABLED | [0.11, 0.88, 0.00]
    50 | [ 2.01, -2.35, 1.48]    | [ 0.43,  2.71, -0.01]   |  2.75 |  0.34 | DISABLED | [0.14, 0.90, -0.00]
    51 | [ 2.04, -2.24, 1.48]    | [ 0.75,  2.67, -0.01]   |  2.78 |  0.29 | DISABLED | [0.25, 0.89, -0.00]
  ```

### [Seed 4016] Configuration: Baseline (Shield OFF) — Outcome: `OBSTACLE_COLLISION`
- **Steps:** 23 | **Reward:** -9.36 | **Min Clearance:** 0.268 m
- **Diagnostic Cause:** Obstacle collision at speed 2.98 m/s (min clearance 0.27m).
- **Last 5 Control Steps Telemetry:**
  ```
  Step | Pos [x, y, z]           | Vel [vx, vy, vz]        | Speed | Clr   | State    | Action Executed
  -----+-------------------------+-------------------------+-------+-------+----------+----------------
    19 | [-0.08, -5.69, 1.50]    | [-1.02,  2.91, 0.01]    |  3.09 |  0.72 | DISABLED | [-0.34, 0.97, 0.00]
    20 | [-0.12, -5.57, 1.50]    | [-0.89,  2.88, -0.03]   |  3.02 |  0.60 | DISABLED | [-0.30, 0.96, -0.01]
    21 | [-0.15, -5.45, 1.50]    | [-0.95,  2.89, -0.01]   |  3.04 |  0.49 | DISABLED | [-0.32, 0.96, -0.00]
    22 | [-0.20, -5.33, 1.50]    | [-1.04,  2.87, -0.00]   |  3.05 |  0.38 | DISABLED | [-0.35, 0.96, -0.00]
    23 | [-0.24, -5.21, 1.50]    | [-0.97,  2.82, -0.03]   |  2.98 |  0.27 | DISABLED | [-0.32, 0.94, -0.01]
  ```

### [Seed 4017] Configuration: Baseline (Shield OFF) — Outcome: `OBSTACLE_COLLISION`
- **Steps:** 91 | **Reward:** -211.77 | **Min Clearance:** 0.094 m
- **Diagnostic Cause:** Obstacle collision at speed 3.30 m/s (min clearance 0.41m).
- **Last 5 Control Steps Telemetry:**
  ```
  Step | Pos [x, y, z]           | Vel [vx, vy, vz]        | Speed | Clr   | State    | Action Executed
  -----+-------------------------+-------------------------+-------+-------+----------+----------------
    87 | [ 2.11,  1.58, 1.52]    | [ 2.77,  2.28, 0.02]    |  3.59 |  0.13 | DISABLED | [0.92, 0.76, 0.01]
    88 | [ 2.19,  1.66, 1.52]    | [ 1.81,  2.07, -0.01]   |  2.75 |  0.26 | DISABLED | [0.60, 0.69, -0.00]
    89 | [ 2.28,  1.75, 1.52]    | [ 2.19,  2.07, 0.01]    |  3.01 |  0.40 | DISABLED | [0.73, 0.69, 0.00]
    90 | [ 2.39,  1.83, 1.52]    | [ 2.64,  1.99, -0.00]   |  3.31 |  0.45 | DISABLED | [0.88, 0.66, -0.00]
    91 | [ 2.50,  1.91, 1.51]    | [ 2.70,  1.90, -0.04]   |  3.30 |  0.41 | DISABLED | [0.90, 0.63, -0.01]
  ```

### [Seed 4020] Configuration: Baseline (Shield OFF) — Outcome: `OBSTACLE_COLLISION`
- **Steps:** 53 | **Reward:** 14.62 | **Min Clearance:** 0.123 m
- **Diagnostic Cause:** Obstacle collision at speed 2.98 m/s (min clearance 0.12m).
- **Last 5 Control Steps Telemetry:**
  ```
  Step | Pos [x, y, z]           | Vel [vx, vy, vz]        | Speed | Clr   | State    | Action Executed
  -----+-------------------------+-------------------------+-------+-------+----------+----------------
    49 | [-0.42, -2.29, 1.50]    | [-2.54,  2.29, 0.00]    |  3.42 |  0.13 | DISABLED | [-0.85, 0.76, 0.00]
    50 | [-0.52, -2.20, 1.50]    | [-2.40,  2.26, 0.03]    |  3.29 |  0.15 | DISABLED | [-0.80, 0.75, 0.01]
    51 | [-0.41, -2.11, 1.50]    | [ 2.65,  2.03, -0.03]   |  3.33 |  0.15 | DISABLED | [0.88, 0.68, -0.01]
    52 | [-0.52, -2.03, 1.50]    | [-2.56,  2.07, -0.01]   |  3.29 |  0.14 | DISABLED | [-0.85, 0.69, -0.00]
    53 | [-0.59, -1.93, 1.49]    | [-1.76,  2.41, -0.07]   |  2.98 |  0.12 | DISABLED | [-0.58, 0.81, -0.03]
  ```

### [Seed 4021] Configuration: Baseline (Shield OFF) — Outcome: `OBSTACLE_COLLISION`
- **Steps:** 62 | **Reward:** -56.78 | **Min Clearance:** 0.118 m
- **Diagnostic Cause:** Obstacle collision at speed 1.93 m/s (min clearance 0.16m).
- **Last 5 Control Steps Telemetry:**
  ```
  Step | Pos [x, y, z]           | Vel [vx, vy, vz]        | Speed | Clr   | State    | Action Executed
  -----+-------------------------+-------------------------+-------+-------+----------+----------------
    58 | [ 0.46, -1.62, 1.49]    | [-2.94,  2.04, -0.04]   |  3.58 |  0.14 | DISABLED | [-0.98, 0.68, -0.01]
    59 | [ 0.34, -1.53, 1.49]    | [-2.85,  2.13, -0.02]   |  3.56 |  0.13 | DISABLED | [-0.95, 0.71, -0.01]
    60 | [ 0.22, -1.45, 1.49]    | [-2.90,  1.97, 0.04]    |  3.50 |  0.16 | DISABLED | [-0.97, 0.66, 0.01]
    61 | [ 0.34, -1.36, 1.49]    | [ 2.88,  2.05, -0.04]   |  3.54 |  0.16 | DISABLED | [0.96, 0.68, -0.01]
    62 | [ 0.35, -1.28, 1.49]    | [ 0.19,  1.92, 0.06]    |  1.93 |  0.16 | DISABLED | [0.06, 0.64, 0.02]
  ```

### [Seed 4022] Configuration: Baseline (Shield OFF) — Outcome: `OBSTACLE_COLLISION`
- **Steps:** 60 | **Reward:** -28.75 | **Min Clearance:** 0.123 m
- **Diagnostic Cause:** Obstacle collision at speed 3.47 m/s (min clearance 0.12m).
- **Last 5 Control Steps Telemetry:**
  ```
  Step | Pos [x, y, z]           | Vel [vx, vy, vz]        | Speed | Clr   | State    | Action Executed
  -----+-------------------------+-------------------------+-------+-------+----------+----------------
    56 | [-0.37, -1.58, 1.50]    | [ 1.68,  1.98, -0.03]   |  2.60 |  0.15 | DISABLED | [0.56, 0.66, -0.01]
    57 | [-0.26, -1.50, 1.50]    | [ 2.56,  1.97, -0.02]   |  3.23 |  0.18 | DISABLED | [0.85, 0.66, -0.01]
    58 | [-0.14, -1.42, 1.50]    | [ 2.85,  1.95, -0.02]   |  3.45 |  0.14 | DISABLED | [0.95, 0.65, -0.01]
    59 | [-0.02, -1.34, 1.50]    | [ 2.98,  1.81, 0.03]    |  3.49 |  0.16 | DISABLED | [0.99, 0.60, 0.01]
    60 | [-0.14, -1.27, 1.50]    | [-2.97,  1.81, 0.04]    |  3.47 |  0.12 | DISABLED | [-0.99, 0.60, 0.01]
  ```

### [Seed 4023] Configuration: Baseline (Shield OFF) — Outcome: `OBSTACLE_COLLISION`
- **Steps:** 56 | **Reward:** 18.27 | **Min Clearance:** 0.124 m
- **Diagnostic Cause:** Obstacle collision at speed 1.97 m/s (min clearance 0.12m).
- **Last 5 Control Steps Telemetry:**
  ```
  Step | Pos [x, y, z]           | Vel [vx, vy, vz]        | Speed | Clr   | State    | Action Executed
  -----+-------------------------+-------------------------+-------+-------+----------+----------------
    52 | [-0.37, -2.07, 1.49]    | [ 1.59,  1.64, 0.02]    |  2.28 |  0.14 | DISABLED | [0.53, 0.55, 0.01]
    53 | [-0.49, -2.01, 1.49]    | [-2.86,  1.57, 0.01]    |  3.26 |  0.13 | DISABLED | [-0.95, 0.52, 0.00]
    54 | [-0.47, -1.94, 1.49]    | [ 0.47,  1.61, -0.01]   |  1.68 |  0.12 | DISABLED | [0.15, 0.54, -0.00]
    55 | [-0.56, -1.88, 1.49]    | [-2.29,  1.48, -0.03]   |  2.72 |  0.16 | DISABLED | [-0.76, 0.49, -0.01]
    56 | [-0.62, -1.82, 1.49]    | [-1.34,  1.45, -0.00]   |  1.97 |  0.12 | DISABLED | [-0.45, 0.48, -0.00]
  ```

### [Seed 4024] Configuration: Baseline (Shield OFF) — Outcome: `OBSTACLE_COLLISION`
- **Steps:** 28 | **Reward:** -0.04 | **Min Clearance:** 0.382 m
- **Diagnostic Cause:** Obstacle collision at speed 2.86 m/s (min clearance 0.38m).
- **Last 5 Control Steps Telemetry:**
  ```
  Step | Pos [x, y, z]           | Vel [vx, vy, vz]        | Speed | Clr   | State    | Action Executed
  -----+-------------------------+-------------------------+-------+-------+----------+----------------
    24 | [-0.11, -5.19, 1.50]    | [-1.17,  2.66, 0.05]    |  2.91 |  0.58 | DISABLED | [-0.39, 0.89, 0.02]
    25 | [-0.15, -5.07, 1.50]    | [-0.95,  2.73, 0.02]    |  2.89 |  0.48 | DISABLED | [-0.32, 0.91, 0.01]
    26 | [-0.15, -4.96, 1.50]    | [ 0.02,  2.76, 0.01]    |  2.76 |  0.44 | DISABLED | [0.01, 0.92, 0.00]
    27 | [-0.16, -4.84, 1.50]    | [-0.32,  2.81, -0.01]   |  2.83 |  0.40 | DISABLED | [-0.11, 0.94, -0.00]
    28 | [-0.18, -4.72, 1.50]    | [-0.50,  2.82, 0.00]    |  2.86 |  0.38 | DISABLED | [-0.17, 0.94, 0.00]
  ```

### [Seed 4025] Configuration: Baseline (Shield OFF) — Outcome: `OBSTACLE_COLLISION`
- **Steps:** 35 | **Reward:** 63.27 | **Min Clearance:** 0.209 m
- **Diagnostic Cause:** Obstacle collision at speed 3.01 m/s (min clearance 0.21m).
- **Last 5 Control Steps Telemetry:**
  ```
  Step | Pos [x, y, z]           | Vel [vx, vy, vz]        | Speed | Clr   | State    | Action Executed
  -----+-------------------------+-------------------------+-------+-------+----------+----------------
    31 | [ 0.32, -4.35, 1.49]    | [ 0.14,  2.74, -0.01]   |  2.74 |  0.63 | DISABLED | [0.05, 0.91, -0.00]
    32 | [ 0.30, -4.23, 1.49]    | [-0.51,  2.81, -0.02]   |  2.85 |  0.52 | DISABLED | [-0.17, 0.94, -0.01]
    33 | [ 0.29, -4.12, 1.49]    | [-0.23,  2.84, -0.02]   |  2.85 |  0.41 | DISABLED | [-0.08, 0.95, -0.01]
    34 | [ 0.29, -4.00, 1.49]    | [ 0.06,  2.81, -0.03]   |  2.81 |  0.33 | DISABLED | [0.02, 0.94, -0.01]
    35 | [ 0.25, -3.88, 1.49]    | [-0.96,  2.86, -0.01]   |  3.01 |  0.21 | DISABLED | [-0.32, 0.95, -0.00]
  ```

### [Seed 4026] Configuration: Baseline (Shield OFF) — Outcome: `OBSTACLE_COLLISION`
- **Steps:** 115 | **Reward:** -262.48 | **Min Clearance:** 0.068 m
- **Diagnostic Cause:** Obstacle collision at speed 2.72 m/s (min clearance 0.07m).
- **Last 5 Control Steps Telemetry:**
  ```
  Step | Pos [x, y, z]           | Vel [vx, vy, vz]        | Speed | Clr   | State    | Action Executed
  -----+-------------------------+-------------------------+-------+-------+----------+----------------
   111 | [-0.05,  4.11, 1.50]    | [ 0.97,  2.11, 0.04]    |  2.32 |  0.42 | DISABLED | [0.32, 0.70, 0.01]
   112 | [-0.01,  4.20, 1.51]    | [ 0.83,  2.10, 0.05]    |  2.26 |  0.25 | DISABLED | [0.28, 0.70, 0.01]
   113 | [-0.14,  4.27, 1.51]    | [-2.96,  1.74, 0.01]    |  3.43 |  0.45 | DISABLED | [-0.98, 0.58, 0.00]
   114 | [-0.23,  4.34, 1.51]    | [-2.18,  1.55, 0.08]    |  2.68 |  0.26 | DISABLED | [-0.73, 0.52, 0.03]
   115 | [-0.32,  4.40, 1.51]    | [-2.21,  1.58, -0.02]   |  2.72 |  0.07 | DISABLED | [-0.74, 0.53, -0.01]
  ```

### [Seed 4027] Configuration: Baseline (Shield OFF) — Outcome: `OBSTACLE_COLLISION`
- **Steps:** 36 | **Reward:** 30.16 | **Min Clearance:** 0.324 m
- **Diagnostic Cause:** Obstacle collision at speed 2.90 m/s (min clearance 0.32m).
- **Last 5 Control Steps Telemetry:**
  ```
  Step | Pos [x, y, z]           | Vel [vx, vy, vz]        | Speed | Clr   | State    | Action Executed
  -----+-------------------------+-------------------------+-------+-------+----------+----------------
    32 | [-0.98, -4.33, 1.50]    | [-1.85,  2.68, -0.01]   |  3.26 |  0.70 | DISABLED | [-0.61, 0.90, -0.00]
    33 | [-1.05, -4.22, 1.50]    | [-1.71,  2.66, -0.01]   |  3.16 |  0.58 | DISABLED | [-0.57, 0.89, -0.00]
    34 | [-1.11, -4.11, 1.50]    | [-1.49,  2.62, -0.02]   |  3.02 |  0.47 | DISABLED | [-0.50, 0.87, -0.01]
    35 | [-1.17, -4.00, 1.49]    | [-1.34,  2.58, -0.03]   |  2.90 |  0.36 | DISABLED | [-0.45, 0.86, -0.01]
    36 | [-1.23, -3.89, 1.49]    | [-1.31,  2.58, -0.02]   |  2.90 |  0.32 | DISABLED | [-0.44, 0.86, -0.01]
  ```

### [Seed 4028] Configuration: Baseline (Shield OFF) — Outcome: `OBSTACLE_COLLISION`
- **Steps:** 101 | **Reward:** -256.82 | **Min Clearance:** 0.107 m
- **Diagnostic Cause:** Obstacle collision at speed 3.07 m/s (min clearance 0.15m).
- **Last 5 Control Steps Telemetry:**
  ```
  Step | Pos [x, y, z]           | Vel [vx, vy, vz]        | Speed | Clr   | State    | Action Executed
  -----+-------------------------+-------------------------+-------+-------+----------+----------------
    97 | [ 0.82,  0.85, 1.48]    | [ 1.95,  1.78, -0.01]   |  2.64 |  0.14 | DISABLED | [0.65, 0.59, -0.00]
    98 | [ 0.93,  0.92, 1.48]    | [ 2.56,  1.52, -0.05]   |  2.98 |  0.14 | DISABLED | [0.85, 0.51, -0.02]
    99 | [ 1.03,  0.98, 1.48]    | [ 2.31,  1.49, 0.06]    |  2.75 |  0.14 | DISABLED | [0.77, 0.50, 0.02]
   100 | [ 1.10,  1.03, 1.48]    | [ 1.89,  1.32, -0.03]   |  2.31 |  0.11 | DISABLED | [0.63, 0.44, -0.01]
   101 | [ 1.22,  1.09, 1.48]    | [ 2.70,  1.46, -0.12]   |  3.07 |  0.15 | DISABLED | [0.90, 0.49, -0.04]
  ```

### [Seed 4029] Configuration: Baseline (Shield OFF) — Outcome: `OBSTACLE_COLLISION`
- **Steps:** 94 | **Reward:** -232.58 | **Min Clearance:** 0.11 m
- **Diagnostic Cause:** Obstacle collision at speed 3.06 m/s (min clearance 0.14m).
- **Last 5 Control Steps Telemetry:**
  ```
  Step | Pos [x, y, z]           | Vel [vx, vy, vz]        | Speed | Clr   | State    | Action Executed
  -----+-------------------------+-------------------------+-------+-------+----------+----------------
    90 | [-1.39,  0.73, 1.50]    | [ 1.48,  2.33, -0.00]   |  2.76 |  0.14 | DISABLED | [0.49, 0.78, -0.00]
    91 | [-1.27,  0.82, 1.50]    | [ 2.74,  2.26, 0.05]    |  3.55 |  0.13 | DISABLED | [0.91, 0.75, 0.02]
    92 | [-1.15,  0.91, 1.50]    | [ 2.80,  2.12, 0.00]    |  3.51 |  0.12 | DISABLED | [0.93, 0.71, 0.00]
    93 | [-1.20,  1.01, 1.50]    | [-1.11,  2.30, -0.06]   |  2.56 |  0.13 | DISABLED | [-0.37, 0.77, -0.02]
    94 | [-1.29,  1.10, 1.50]    | [-2.13,  2.19, -0.09]   |  3.06 |  0.14 | DISABLED | [-0.71, 0.73, -0.03]
  ```

### [Seed 4030] Configuration: Baseline (Shield OFF) — Outcome: `OBSTACLE_COLLISION`
- **Steps:** 38 | **Reward:** 51.05 | **Min Clearance:** 0.17 m
- **Diagnostic Cause:** Obstacle collision at speed 3.52 m/s (min clearance 0.17m).
- **Last 5 Control Steps Telemetry:**
  ```
  Step | Pos [x, y, z]           | Vel [vx, vy, vz]        | Speed | Clr   | State    | Action Executed
  -----+-------------------------+-------------------------+-------+-------+----------+----------------
    34 | [-1.05, -4.09, 1.50]    | [-0.88,  2.55, 0.01]    |  2.70 |  0.47 | DISABLED | [-0.29, 0.85, 0.00]
    35 | [-1.07, -3.98, 1.50]    | [-0.61,  2.61, -0.02]   |  2.68 |  0.38 | DISABLED | [-0.20, 0.87, -0.01]
    36 | [-1.11, -3.87, 1.50]    | [-0.93,  2.69, -0.02]   |  2.84 |  0.35 | DISABLED | [-0.31, 0.90, -0.01]
    37 | [-1.07, -3.76, 1.50]    | [ 1.04,  2.69, -0.03]   |  2.88 |  0.35 | DISABLED | [0.35, 0.90, -0.01]
    38 | [-0.96, -3.66, 1.50]    | [ 2.57,  2.40, -0.04]   |  3.52 |  0.17 | DISABLED | [0.86, 0.80, -0.01]
  ```

### [Seed 4036] Configuration: Baseline (Shield OFF) — Outcome: `OBSTACLE_COLLISION`
- **Steps:** 121 | **Reward:** -422.99 | **Min Clearance:** 0.11 m
- **Diagnostic Cause:** Obstacle collision at speed 1.68 m/s (min clearance 0.14m).
- **Last 5 Control Steps Telemetry:**
  ```
  Step | Pos [x, y, z]           | Vel [vx, vy, vz]        | Speed | Clr   | State    | Action Executed
  -----+-------------------------+-------------------------+-------+-------+----------+----------------
   117 | [ 0.19,  2.42, 1.45]    | [ 2.26,  1.67, -0.01]   |  2.81 |  0.15 | DISABLED | [0.75, 0.56, -0.00]
   118 | [ 0.31,  2.49, 1.45]    | [ 2.94,  1.59, -0.02]   |  3.34 |  0.15 | DISABLED | [0.98, 0.53, -0.01]
   119 | [ 0.43,  2.55, 1.45]    | [ 2.83,  1.53, -0.07]   |  3.22 |  0.11 | DISABLED | [0.94, 0.51, -0.02]
   120 | [ 0.54,  2.62, 1.45]    | [ 2.54,  1.66, -0.01]   |  3.04 |  0.14 | DISABLED | [0.85, 0.55, -0.00]
   121 | [ 0.51,  2.68, 1.45]    | [-0.70,  1.53, 0.07]    |  1.68 |  0.14 | DISABLED | [-0.23, 0.51, 0.03]
  ```

### [Seed 4037] Configuration: Baseline (Shield OFF) — Outcome: `OBSTACLE_COLLISION`
- **Steps:** 107 | **Reward:** -325.42 | **Min Clearance:** 0.11 m
- **Diagnostic Cause:** Obstacle collision at speed 2.46 m/s (min clearance 0.11m).
- **Last 5 Control Steps Telemetry:**
  ```
  Step | Pos [x, y, z]           | Vel [vx, vy, vz]        | Speed | Clr   | State    | Action Executed
  -----+-------------------------+-------------------------+-------+-------+----------+----------------
   103 | [-0.51,  2.41, 1.50]    | [ 2.54,  1.89, 0.04]    |  3.17 |  0.13 | DISABLED | [0.85, 0.63, 0.01]
   104 | [-0.49,  2.49, 1.50]    | [ 0.34,  1.90, 0.03]    |  1.93 |  0.13 | DISABLED | [0.11, 0.63, 0.01]
   105 | [-0.54,  2.57, 1.50]    | [-1.11,  1.91, -0.02]   |  2.21 |  0.15 | DISABLED | [-0.37, 0.64, -0.01]
   106 | [-0.52,  2.65, 1.50]    | [ 0.47,  1.86, -0.01]   |  1.92 |  0.15 | DISABLED | [0.16, 0.62, -0.01]
   107 | [-0.46,  2.73, 1.50]    | [ 1.36,  2.05, -0.03]   |  2.46 |  0.11 | DISABLED | [0.45, 0.68, -0.01]
  ```

### [Seed 4038] Configuration: Baseline (Shield OFF) — Outcome: `OBSTACLE_COLLISION`
- **Steps:** 29 | **Reward:** 24.33 | **Min Clearance:** 0.336 m
- **Diagnostic Cause:** Obstacle collision at speed 2.41 m/s (min clearance 0.34m).
- **Last 5 Control Steps Telemetry:**
  ```
  Step | Pos [x, y, z]           | Vel [vx, vy, vz]        | Speed | Clr   | State    | Action Executed
  -----+-------------------------+-------------------------+-------+-------+----------+----------------
    25 | [ 0.55, -5.09, 1.50]    | [-1.63,  2.67, 0.02]    |  3.13 |  0.77 | DISABLED | [-0.54, 0.89, 0.01]
    26 | [ 0.51, -4.98, 1.50]    | [-0.95,  2.63, 0.01]    |  2.79 |  0.64 | DISABLED | [-0.32, 0.88, 0.00]
    27 | [ 0.60, -4.88, 1.49]    | [ 2.16,  2.48, -0.04]   |  3.29 |  0.61 | DISABLED | [0.72, 0.83, -0.01]
    28 | [ 0.48, -4.78, 1.49]    | [-2.71,  2.43, -0.05]   |  3.65 |  0.42 | DISABLED | [-0.90, 0.81, -0.02]
    29 | [ 0.49, -4.68, 1.49]    | [ 0.14,  2.41, -0.09]   |  2.41 |  0.34 | DISABLED | [0.05, 0.80, -0.03]
  ```

### [Seed 4041] Configuration: Baseline (Shield OFF) — Outcome: `OBSTACLE_COLLISION`
- **Steps:** 68 | **Reward:** -69.04 | **Min Clearance:** 0.103 m
- **Diagnostic Cause:** Obstacle collision at speed 3.48 m/s (min clearance 0.16m).
- **Last 5 Control Steps Telemetry:**
  ```
  Step | Pos [x, y, z]           | Vel [vx, vy, vz]        | Speed | Clr   | State    | Action Executed
  -----+-------------------------+-------------------------+-------+-------+----------+----------------
    64 | [ 0.86, -1.32, 1.51]    | [-2.83,  1.98, 0.03]    |  3.45 |  0.14 | DISABLED | [-0.94, 0.66, 0.01]
    65 | [ 0.79, -1.24, 1.51]    | [-1.53,  1.96, -0.01]   |  2.49 |  0.14 | DISABLED | [-0.51, 0.66, -0.00]
    66 | [ 0.69, -1.16, 1.50]    | [-2.51,  1.96, -0.02]   |  3.18 |  0.16 | DISABLED | [-0.84, 0.65, -0.01]
    67 | [ 0.57, -1.07, 1.50]    | [-2.78,  1.98, -0.06]   |  3.41 |  0.13 | DISABLED | [-0.93, 0.66, -0.02]
    68 | [ 0.45, -1.00, 1.50]    | [-2.92,  1.89, -0.01]   |  3.48 |  0.16 | DISABLED | [-0.97, 0.63, -0.00]
  ```

### [Seed 4042] Configuration: Baseline (Shield OFF) — Outcome: `OBSTACLE_COLLISION`
- **Steps:** 47 | **Reward:** 19.71 | **Min Clearance:** 0.126 m
- **Diagnostic Cause:** Obstacle collision at speed 3.03 m/s (min clearance 0.13m).
- **Last 5 Control Steps Telemetry:**
  ```
  Step | Pos [x, y, z]           | Vel [vx, vy, vz]        | Speed | Clr   | State    | Action Executed
  -----+-------------------------+-------------------------+-------+-------+----------+----------------
    43 | [ 1.01, -3.09, 1.51]    | [ 0.21,  2.45, -0.01]   |  2.46 |  0.35 | DISABLED | [0.07, 0.82, -0.01]
    44 | [ 1.02, -2.99, 1.51]    | [ 0.30,  2.52, 0.04]    |  2.54 |  0.31 | DISABLED | [0.10, 0.84, 0.01]
    45 | [ 1.01, -2.88, 1.51]    | [-0.24,  2.50, 0.02]    |  2.51 |  0.26 | DISABLED | [-0.08, 0.83, 0.01]
    46 | [ 1.02, -2.78, 1.51]    | [ 0.22,  2.54, 0.01]    |  2.55 |  0.20 | DISABLED | [0.07, 0.85, 0.00]
    47 | [ 0.95, -2.68, 1.51]    | [-1.77,  2.46, 0.05]    |  3.03 |  0.13 | DISABLED | [-0.59, 0.82, 0.02]
  ```

### [Seed 4043] Configuration: Baseline (Shield OFF) — Outcome: `OBSTACLE_COLLISION`
- **Steps:** 65 | **Reward:** -41.36 | **Min Clearance:** 0.104 m
- **Diagnostic Cause:** Obstacle collision at speed 3.73 m/s (min clearance 0.13m).
- **Last 5 Control Steps Telemetry:**
  ```
  Step | Pos [x, y, z]           | Vel [vx, vy, vz]        | Speed | Clr   | State    | Action Executed
  -----+-------------------------+-------------------------+-------+-------+----------+----------------
    61 | [ 2.06, -1.23, 1.52]    | [ 0.96,  2.41, 0.02]    |  2.60 |  0.14 | DISABLED | [0.32, 0.80, 0.01]
    62 | [ 2.14, -1.14, 1.52]    | [ 1.74,  2.35, -0.01]   |  2.92 |  0.11 | DISABLED | [0.58, 0.78, -0.00]
    63 | [ 2.23, -1.04, 1.52]    | [ 2.23,  2.37, -0.03]   |  3.25 |  0.13 | DISABLED | [0.74, 0.79, -0.01]
    64 | [ 2.35, -0.94, 1.52]    | [ 2.87,  2.37, -0.06]   |  3.72 |  0.11 | DISABLED | [0.96, 0.79, -0.02]
    65 | [ 2.47, -0.84, 1.52]    | [ 2.95,  2.28, -0.05]   |  3.73 |  0.13 | DISABLED | [0.98, 0.76, -0.02]
  ```

### [Seed 4044] Configuration: Baseline (Shield OFF) — Outcome: `OBSTACLE_COLLISION`
- **Steps:** 70 | **Reward:** -147.51 | **Min Clearance:** 0.102 m
- **Diagnostic Cause:** Obstacle collision at speed 3.37 m/s (min clearance 0.14m).
- **Last 5 Control Steps Telemetry:**
  ```
  Step | Pos [x, y, z]           | Vel [vx, vy, vz]        | Speed | Clr   | State    | Action Executed
  -----+-------------------------+-------------------------+-------+-------+----------+----------------
    66 | [ 1.75, -1.08, 1.51]    | [ 2.85,  1.92, -0.03]   |  3.44 |  0.15 | DISABLED | [0.95, 0.64, -0.01]
    67 | [ 1.87, -0.99, 1.50]    | [ 2.89,  1.93, -0.12]   |  3.48 |  0.15 | DISABLED | [0.96, 0.64, -0.04]
    68 | [ 1.83, -0.93, 1.50]    | [-1.03,  1.65, 0.05]    |  1.94 |  0.10 | DISABLED | [-0.34, 0.55, 0.02]
    69 | [ 1.71, -0.87, 1.50]    | [-2.93,  1.44, 0.01]    |  3.27 |  0.14 | DISABLED | [-0.98, 0.48, 0.00]
    70 | [ 1.82, -0.79, 1.51]    | [ 2.83,  1.82, 0.07]    |  3.37 |  0.14 | DISABLED | [0.94, 0.61, 0.02]
  ```

### [Seed 4045] Configuration: Baseline (Shield OFF) — Outcome: `OBSTACLE_COLLISION`
- **Steps:** 82 | **Reward:** -183.82 | **Min Clearance:** 0.108 m
- **Diagnostic Cause:** Obstacle collision at speed 3.37 m/s (min clearance 0.15m).
- **Last 5 Control Steps Telemetry:**
  ```
  Step | Pos [x, y, z]           | Vel [vx, vy, vz]        | Speed | Clr   | State    | Action Executed
  -----+-------------------------+-------------------------+-------+-------+----------+----------------
    78 | [ 1.13,  0.32, 1.50]    | [ 1.74,  2.46, -0.06]   |  3.02 |  0.16 | DISABLED | [0.58, 0.82, -0.02]
    79 | [ 1.10,  0.42, 1.50]    | [-0.84,  2.41, -0.03]   |  2.55 |  0.15 | DISABLED | [-0.28, 0.80, -0.01]
    80 | [ 0.99,  0.52, 1.50]    | [-2.67,  2.39, 0.02]    |  3.58 |  0.13 | DISABLED | [-0.89, 0.80, 0.01]
    81 | [ 0.86,  0.61, 1.50]    | [-2.92,  2.17, 0.03]    |  3.63 |  0.16 | DISABLED | [-0.97, 0.72, 0.01]
    82 | [ 0.76,  0.70, 1.50]    | [-2.56,  2.20, 0.10]    |  3.37 |  0.15 | DISABLED | [-0.85, 0.73, 0.03]
  ```

### [Seed 4046] Configuration: Baseline (Shield OFF) — Outcome: `OBSTACLE_COLLISION`
- **Steps:** 92 | **Reward:** -206.4 | **Min Clearance:** 0.107 m
- **Diagnostic Cause:** Obstacle collision at speed 3.81 m/s (min clearance 0.11m).
- **Last 5 Control Steps Telemetry:**
  ```
  Step | Pos [x, y, z]           | Vel [vx, vy, vz]        | Speed | Clr   | State    | Action Executed
  -----+-------------------------+-------------------------+-------+-------+----------+----------------
    88 | [-1.62,  1.22, 1.50]    | [-0.86,  2.52, -0.08]   |  2.66 |  0.15 | DISABLED | [-0.28, 0.84, -0.03]
    89 | [-1.65,  1.32, 1.50]    | [-0.75,  2.56, -0.03]   |  2.66 |  0.14 | DISABLED | [-0.25, 0.85, -0.01]
    90 | [-1.68,  1.43, 1.50]    | [-0.82,  2.64, 0.02]    |  2.76 |  0.14 | DISABLED | [-0.27, 0.88, 0.01]
    91 | [-1.72,  1.54, 1.50]    | [-0.93,  2.63, 0.04]    |  2.79 |  0.13 | DISABLED | [-0.31, 0.88, 0.01]
    92 | [-1.61,  1.65, 1.50]    | [ 2.79,  2.60, -0.05]   |  3.81 |  0.11 | DISABLED | [0.93, 0.86, -0.02]
  ```

### [Seed 4048] Configuration: Baseline (Shield OFF) — Outcome: `OBSTACLE_COLLISION`
- **Steps:** 45 | **Reward:** 74.04 | **Min Clearance:** 0.161 m
- **Diagnostic Cause:** Obstacle collision at speed 1.70 m/s (min clearance 0.16m).
- **Last 5 Control Steps Telemetry:**
  ```
  Step | Pos [x, y, z]           | Vel [vx, vy, vz]        | Speed | Clr   | State    | Action Executed
  -----+-------------------------+-------------------------+-------+-------+----------+----------------
    41 | [ 0.03, -3.48, 1.49]    | [-0.28,  1.72, 0.04]    |  1.74 |  0.37 | DISABLED | [-0.09, 0.57, 0.01]
    42 | [ 0.03, -3.40, 1.49]    | [ 0.06,  1.87, -0.06]   |  1.87 |  0.30 | DISABLED | [0.02, 0.62, -0.02]
    43 | [ 0.03, -3.33, 1.49]    | [ 0.09,  1.85, -0.00]   |  1.85 |  0.24 | DISABLED | [0.03, 0.62, -0.00]
    44 | [-0.01, -3.25, 1.49]    | [-1.07,  1.77, 0.02]    |  2.07 |  0.18 | DISABLED | [-0.36, 0.59, 0.01]
    45 | [-0.03, -3.18, 1.49]    | [-0.49,  1.62, 0.01]    |  1.70 |  0.16 | DISABLED | [-0.17, 0.54, 0.00]
  ```

### [Seed 4049] Configuration: Baseline (Shield OFF) — Outcome: `OBSTACLE_COLLISION`
- **Steps:** 35 | **Reward:** 72.88 | **Min Clearance:** 0.215 m
- **Diagnostic Cause:** Obstacle collision at speed 3.20 m/s (min clearance 0.21m).
- **Last 5 Control Steps Telemetry:**
  ```
  Step | Pos [x, y, z]           | Vel [vx, vy, vz]        | Speed | Clr   | State    | Action Executed
  -----+-------------------------+-------------------------+-------+-------+----------+----------------
    31 | [-0.18, -4.34, 1.50]    | [ 0.23,  2.81, -0.01]   |  2.82 |  0.69 | DISABLED | [0.08, 0.94, -0.00]
    32 | [-0.18, -4.22, 1.50]    | [ 0.20,  2.88, 0.01]    |  2.88 |  0.58 | DISABLED | [0.07, 0.96, 0.00]
    33 | [-0.16, -4.10, 1.50]    | [ 0.43,  2.87, 0.01]    |  2.90 |  0.47 | DISABLED | [0.14, 0.96, 0.00]
    34 | [-0.13, -3.98, 1.50]    | [ 0.68,  2.81, 0.01]    |  2.89 |  0.35 | DISABLED | [0.23, 0.94, 0.00]
    35 | [-0.05, -3.87, 1.50]    | [ 1.82,  2.64, 0.02]    |  3.20 |  0.21 | DISABLED | [0.60, 0.88, 0.01]
  ```

### [Seed 4051] Configuration: Baseline (Shield OFF) — Outcome: `OBSTACLE_COLLISION`
- **Steps:** 45 | **Reward:** -28.3 | **Min Clearance:** 0.245 m
- **Diagnostic Cause:** Obstacle collision at speed 2.73 m/s (min clearance 0.24m).
- **Last 5 Control Steps Telemetry:**
  ```
  Step | Pos [x, y, z]           | Vel [vx, vy, vz]        | Speed | Clr   | State    | Action Executed
  -----+-------------------------+-------------------------+-------+-------+----------+----------------
    41 | [-0.98, -3.21, 1.50]    | [-0.06,  2.75, 0.04]    |  2.75 |  0.31 | DISABLED | [-0.02, 0.92, 0.01]
    42 | [-0.97, -3.10, 1.50]    | [ 0.18,  2.76, -0.00]   |  2.77 |  0.37 | DISABLED | [0.06, 0.92, -0.00]
    43 | [-0.98, -2.98, 1.50]    | [-0.33,  2.69, -0.02]   |  2.71 |  0.35 | DISABLED | [-0.11, 0.90, -0.01]
    44 | [-0.98, -2.87, 1.50]    | [-0.04,  2.71, 0.01]    |  2.71 |  0.30 | DISABLED | [-0.01, 0.91, 0.01]
    45 | [-1.01, -2.76, 1.50]    | [-0.53,  2.68, 0.06]    |  2.73 |  0.24 | DISABLED | [-0.18, 0.90, 0.02]
  ```

### [Seed 4052] Configuration: Baseline (Shield OFF) — Outcome: `OBSTACLE_COLLISION`
- **Steps:** 117 | **Reward:** -372.9 | **Min Clearance:** 0.099 m
- **Diagnostic Cause:** Obstacle collision at speed 1.85 m/s (min clearance 0.23m).
- **Last 5 Control Steps Telemetry:**
  ```
  Step | Pos [x, y, z]           | Vel [vx, vy, vz]        | Speed | Clr   | State    | Action Executed
  -----+-------------------------+-------------------------+-------+-------+----------+----------------
   113 | [ 2.38,  3.32, 1.50]    | [ 0.19,  1.49, 0.06]    |  1.50 |  0.43 | DISABLED | [0.07, 0.50, 0.02]
   114 | [ 2.37,  3.38, 1.50]    | [-0.31,  1.46, -0.00]   |  1.49 |  0.38 | DISABLED | [-0.10, 0.49, -0.00]
   115 | [ 2.35,  3.45, 1.50]    | [-0.38,  1.49, 0.00]    |  1.54 |  0.35 | DISABLED | [-0.13, 0.50, 0.00]
   116 | [ 2.34,  3.51, 1.50]    | [-0.23,  1.62, -0.00]   |  1.64 |  0.29 | DISABLED | [-0.07, 0.54, -0.00]
   117 | [ 2.33,  3.59, 1.50]    | [-0.30,  1.83, -0.01]   |  1.85 |  0.23 | DISABLED | [-0.10, 0.61, -0.01]
  ```

### [Seed 4053] Configuration: Baseline (Shield OFF) — Outcome: `OBSTACLE_COLLISION`
- **Steps:** 83 | **Reward:** -156.54 | **Min Clearance:** 0.125 m
- **Diagnostic Cause:** Obstacle collision at speed 3.67 m/s (min clearance 0.17m).
- **Last 5 Control Steps Telemetry:**
  ```
  Step | Pos [x, y, z]           | Vel [vx, vy, vz]        | Speed | Clr   | State    | Action Executed
  -----+-------------------------+-------------------------+-------+-------+----------+----------------
    79 | [-0.19,  0.03, 1.48]    | [-0.80,  2.50, -0.02]   |  2.62 |  0.17 | DISABLED | [-0.27, 0.83, -0.01]
    80 | [-0.18,  0.14, 1.49]    | [ 0.34,  2.62, 0.06]    |  2.65 |  0.14 | DISABLED | [0.11, 0.88, 0.02]
    81 | [-0.15,  0.24, 1.49]    | [ 0.76,  2.44, -0.02]   |  2.55 |  0.18 | DISABLED | [0.25, 0.81, -0.01]
    82 | [-0.21,  0.34, 1.49]    | [-1.49,  2.46, 0.01]    |  2.87 |  0.16 | DISABLED | [-0.49, 0.82, 0.00]
    83 | [-0.33,  0.44, 1.49]    | [-2.79,  2.38, -0.04]   |  3.67 |  0.17 | DISABLED | [-0.93, 0.79, -0.01]
  ```

### [Seed 4054] Configuration: Baseline (Shield OFF) — Outcome: `OBSTACLE_COLLISION`
- **Steps:** 34 | **Reward:** 26.01 | **Min Clearance:** 0.165 m
- **Diagnostic Cause:** Obstacle collision at speed 2.65 m/s (min clearance 0.17m).
- **Last 5 Control Steps Telemetry:**
  ```
  Step | Pos [x, y, z]           | Vel [vx, vy, vz]        | Speed | Clr   | State    | Action Executed
  -----+-------------------------+-------------------------+-------+-------+----------+----------------
    30 | [-0.40, -4.52, 1.49]    | [ 0.16,  2.65, 0.00]    |  2.65 |  0.57 | DISABLED | [0.05, 0.88, 0.00]
    31 | [-0.41, -4.41, 1.49]    | [-0.26,  2.64, 0.01]    |  2.65 |  0.47 | DISABLED | [-0.09, 0.88, 0.00]
    32 | [-0.42, -4.30, 1.49]    | [-0.35,  2.68, 0.02]    |  2.71 |  0.37 | DISABLED | [-0.12, 0.89, 0.01]
    33 | [-0.42, -4.19, 1.49]    | [ 0.09,  2.66, 0.01]    |  2.66 |  0.27 | DISABLED | [0.03, 0.89, 0.00]
    34 | [-0.42, -4.08, 1.49]    | [ 0.07,  2.65, 0.02]    |  2.65 |  0.17 | DISABLED | [0.02, 0.88, 0.01]
  ```

### [Seed 4055] Configuration: Baseline (Shield OFF) — Outcome: `OBSTACLE_COLLISION`
- **Steps:** 85 | **Reward:** -220.21 | **Min Clearance:** 0.123 m
- **Diagnostic Cause:** Obstacle collision at speed 1.43 m/s (min clearance 0.17m).
- **Last 5 Control Steps Telemetry:**
  ```
  Step | Pos [x, y, z]           | Vel [vx, vy, vz]        | Speed | Clr   | State    | Action Executed
  -----+-------------------------+-------------------------+-------+-------+----------+----------------
    81 | [-0.50, -0.19, 1.49]    | [-2.78,  1.45, -0.02]   |  3.13 |  0.13 | DISABLED | [-0.93, 0.48, -0.01]
    82 | [-0.39, -0.13, 1.49]    | [ 2.74,  1.58, 0.06]    |  3.16 |  0.26 | DISABLED | [0.91, 0.53, 0.02]
    83 | [-0.31, -0.06, 1.49]    | [ 1.86,  1.53, 0.00]    |  2.40 |  0.20 | DISABLED | [0.62, 0.51, 0.00]
    84 | [-0.26, -0.00, 1.49]    | [ 1.18,  1.45, 0.01]    |  1.86 |  0.15 | DISABLED | [0.39, 0.48, 0.00]
    85 | [-0.24,  0.06, 1.49]    | [ 0.33,  1.40, 0.01]    |  1.43 |  0.17 | DISABLED | [0.11, 0.47, 0.00]
  ```

### [Seed 4056] Configuration: Baseline (Shield OFF) — Outcome: `OBSTACLE_COLLISION`
- **Steps:** 52 | **Reward:** 28.21 | **Min Clearance:** 0.12 m
- **Diagnostic Cause:** Obstacle collision at speed 2.71 m/s (min clearance 0.12m).
- **Last 5 Control Steps Telemetry:**
  ```
  Step | Pos [x, y, z]           | Vel [vx, vy, vz]        | Speed | Clr   | State    | Action Executed
  -----+-------------------------+-------------------------+-------+-------+----------+----------------
    48 | [ 1.32, -2.53, 1.49]    | [-0.08,  2.64, 0.03]    |  2.64 |  0.20 | DISABLED | [-0.03, 0.88, 0.01]
    49 | [ 1.31, -2.42, 1.49]    | [-0.15,  2.65, 0.03]    |  2.65 |  0.14 | DISABLED | [-0.05, 0.88, 0.01]
    50 | [ 1.26, -2.31, 1.49]    | [-1.22,  2.60, 0.02]    |  2.87 |  0.13 | DISABLED | [-0.41, 0.87, 0.01]
    51 | [ 1.28, -2.21, 1.49]    | [ 0.40,  2.51, -0.00]   |  2.54 |  0.13 | DISABLED | [0.13, 0.84, -0.00]
    52 | [ 1.32, -2.10, 1.49]    | [ 1.14,  2.46, 0.00]    |  2.71 |  0.12 | DISABLED | [0.38, 0.82, 0.00]
  ```

### [Seed 4057] Configuration: Baseline (Shield OFF) — Outcome: `OBSTACLE_COLLISION`
- **Steps:** 71 | **Reward:** -105.73 | **Min Clearance:** 0.111 m
- **Diagnostic Cause:** Obstacle collision at speed 2.32 m/s (min clearance 0.13m).
- **Last 5 Control Steps Telemetry:**
  ```
  Step | Pos [x, y, z]           | Vel [vx, vy, vz]        | Speed | Clr   | State    | Action Executed
  -----+-------------------------+-------------------------+-------+-------+----------+----------------
    67 | [-0.56, -1.04, 1.51]    | [-1.03,  1.68, 0.01]    |  1.97 |  0.14 | DISABLED | [-0.34, 0.56, 0.01]
    68 | [-0.45, -0.97, 1.51]    | [ 2.59,  1.69, 0.01]    |  3.10 |  0.14 | DISABLED | [0.86, 0.56, 0.01]
    69 | [-0.57, -0.91, 1.51]    | [-2.87,  1.61, 0.02]    |  3.29 |  0.15 | DISABLED | [-0.96, 0.54, 0.01]
    70 | [-0.47, -0.84, 1.51]    | [ 2.33,  1.61, -0.01]   |  2.83 |  0.13 | DISABLED | [0.78, 0.54, -0.00]
    71 | [-0.40, -0.77, 1.51]    | [ 1.67,  1.61, 0.03]    |  2.32 |  0.13 | DISABLED | [0.56, 0.54, 0.01]
  ```

### [Seed 4058] Configuration: Baseline (Shield OFF) — Outcome: `OBSTACLE_COLLISION`
- **Steps:** 32 | **Reward:** -19.49 | **Min Clearance:** 0.266 m
- **Diagnostic Cause:** Obstacle collision at speed 2.86 m/s (min clearance 0.27m).
- **Last 5 Control Steps Telemetry:**
  ```
  Step | Pos [x, y, z]           | Vel [vx, vy, vz]        | Speed | Clr   | State    | Action Executed
  -----+-------------------------+-------------------------+-------+-------+----------+----------------
    28 | [ 0.64, -4.87, 1.49]    | [ 0.94,  2.85, -0.02]   |  3.00 |  0.55 | DISABLED | [0.31, 0.95, -0.01]
    29 | [ 0.65, -4.75, 1.49]    | [ 0.47,  2.88, -0.01]   |  2.91 |  0.48 | DISABLED | [0.16, 0.96, -0.00]
    30 | [ 0.64, -4.63, 1.49]    | [-0.34,  2.86, -0.04]   |  2.88 |  0.39 | DISABLED | [-0.11, 0.95, -0.01]
    31 | [ 0.63, -4.51, 1.49]    | [-0.34,  2.85, 0.01]    |  2.87 |  0.31 | DISABLED | [-0.11, 0.95, 0.00]
    32 | [ 0.63, -4.39, 1.49]    | [ 0.09,  2.86, 0.01]    |  2.86 |  0.27 | DISABLED | [0.03, 0.95, 0.00]
  ```

### [Seed 4059] Configuration: Baseline (Shield OFF) — Outcome: `OBSTACLE_COLLISION`
- **Steps:** 65 | **Reward:** -40.32 | **Min Clearance:** 0.106 m
- **Diagnostic Cause:** Obstacle collision at speed 3.18 m/s (min clearance 0.12m).
- **Last 5 Control Steps Telemetry:**
  ```
  Step | Pos [x, y, z]           | Vel [vx, vy, vz]        | Speed | Clr   | State    | Action Executed
  -----+-------------------------+-------------------------+-------+-------+----------+----------------
    61 | [-1.00, -1.42, 1.49]    | [-1.50,  1.52, -0.02]   |  2.13 |  0.14 | DISABLED | [-0.50, 0.51, -0.01]
    62 | [-1.11, -1.35, 1.49]    | [-2.71,  1.55, -0.03]   |  3.12 |  0.15 | DISABLED | [-0.90, 0.52, -0.01]
    63 | [-1.22, -1.29, 1.49]    | [-2.52,  1.60, 0.01]    |  2.99 |  0.15 | DISABLED | [-0.84, 0.54, 0.00]
    64 | [-1.34, -1.22, 1.49]    | [-2.90,  1.53, -0.03]   |  3.28 |  0.17 | DISABLED | [-0.97, 0.51, -0.01]
    65 | [-1.46, -1.17, 1.49]    | [-2.90,  1.29, -0.02]   |  3.18 |  0.12 | DISABLED | [-0.97, 0.43, -0.01]
  ```

### [Seed 4000] Configuration: Shield ON (Oracle) — Outcome: `TIMEOUT`
- **Steps:** 500 | **Reward:** -2412.99 | **Min Clearance:** 0.202 m
- **Diagnostic Cause:** Exceeded maximum episode limit (500 steps) without reaching goal.
- **Last 5 Control Steps Telemetry:**
  ```
  Step | Pos [x, y, z]           | Vel [vx, vy, vz]        | Speed | Clr   | State    | Action Executed
  -----+-------------------------+-------------------------+-------+-------+----------+----------------
   496 | [-0.99,  0.68, 1.50]    | [ 0.00,  0.00, 0.00]    |  0.00 |  0.63 | SCAN     | [0.00, 0.00, 0.00]
   497 | [-0.98,  0.74, 1.50]    | [ 0.32,  1.50, -0.00]   |  1.53 |  0.63 | REROUTE  | [0.11, 0.50, -0.00]
   498 | [-1.00,  0.80, 1.50]    | [-0.53,  1.50, -0.00]   |  1.59 |  0.60 | REROUTE  | [-0.18, 0.50, -0.00]
   499 | [-1.00,  0.77, 1.50]    | [ 0.00, -0.80, -0.00]   |  0.80 |  0.52 | RETREAT  | [0.00, -0.27, -0.00]
   500 | [-1.00,  0.74, 1.50]    | [ 0.00, -0.80, -0.00]   |  0.80 |  0.59 | RETREAT  | [0.00, -0.27, -0.00]
  ```

### [Seed 4015] Configuration: Shield ON (Oracle) — Outcome: `TIMEOUT`
- **Steps:** 500 | **Reward:** -2477.91 | **Min Clearance:** 0.327 m
- **Diagnostic Cause:** Exceeded maximum episode limit (500 steps) without reaching goal.
- **Last 5 Control Steps Telemetry:**
  ```
  Step | Pos [x, y, z]           | Vel [vx, vy, vz]        | Speed | Clr   | State    | Action Executed
  -----+-------------------------+-------------------------+-------+-------+----------+----------------
   496 | [-0.38, -1.76, 1.50]    | [ 0.00, -0.80, -0.00]   |  0.80 |  0.60 | RETREAT  | [0.00, -0.27, -0.00]
   497 | [-0.38, -1.80, 1.50]    | [ 0.00, -0.80, -0.00]   |  0.80 |  0.62 | RETREAT  | [0.00, -0.27, -0.00]
   498 | [-0.38, -1.83, 1.50]    | [ 0.00, -0.80, -0.00]   |  0.80 |  0.65 | RETREAT  | [0.00, -0.27, -0.00]
   499 | [-0.38, -1.86, 1.50]    | [ 0.00, -0.80, -0.00]   |  0.80 |  0.67 | SCAN     | [0.00, -0.27, -0.00]
   500 | [-0.32, -1.80, 1.50]    | [ 1.50,  1.50, -0.00]   |  2.12 |  0.70 | REROUTE  | [0.50, 0.50, -0.00]
  ```

### [Seed 4018] Configuration: Shield ON (Oracle) — Outcome: `TIMEOUT`
- **Steps:** 500 | **Reward:** -2371.49 | **Min Clearance:** 0.414 m
- **Diagnostic Cause:** Exceeded maximum episode limit (500 steps) without reaching goal.
- **Last 5 Control Steps Telemetry:**
  ```
  Step | Pos [x, y, z]           | Vel [vx, vy, vz]        | Speed | Clr   | State    | Action Executed
  -----+-------------------------+-------------------------+-------+-------+----------+----------------
   496 | [-0.96, -0.97, 1.50]    | [ 0.00, -0.80, 0.00]    |  0.80 |  0.65 | RETREAT  | [0.00, -0.27, 0.00]
   497 | [-0.96, -1.01, 1.50]    | [ 0.00, -0.80, 0.00]    |  0.80 |  0.52 | SCAN     | [0.00, -0.27, 0.00]
   498 | [-0.89, -0.99, 1.50]    | [ 1.50,  0.40, 0.00]    |  1.55 |  0.72 | REROUTE  | [0.50, 0.13, 0.00]
   499 | [-0.83, -0.97, 1.50]    | [ 1.50,  0.40, 0.00]    |  1.55 |  0.66 | REROUTE  | [0.50, 0.13, 0.00]
   500 | [-0.77, -0.96, 1.50]    | [ 1.50,  0.40, 0.00]    |  1.55 |  0.68 | REROUTE  | [0.50, 0.13, 0.00]
  ```

### [Seed 4020] Configuration: Shield ON (Oracle) — Outcome: `TIMEOUT`
- **Steps:** 500 | **Reward:** -1210.35 | **Min Clearance:** 0.195 m
- **Diagnostic Cause:** Exceeded maximum episode limit (500 steps) without reaching goal.
- **Last 5 Control Steps Telemetry:**
  ```
  Step | Pos [x, y, z]           | Vel [vx, vy, vz]        | Speed | Clr   | State    | Action Executed
  -----+-------------------------+-------------------------+-------+-------+----------+----------------
   496 | [-3.95,  2.50, 1.50]    | [ 0.00, -0.80, -0.00]   |  0.80 |  0.68 | RETREAT  | [0.00, -0.27, -0.00]
   497 | [-3.95,  2.47, 1.50]    | [ 0.00, -0.80, -0.00]   |  0.80 |  0.64 | RETREAT  | [0.00, -0.27, -0.00]
   498 | [-3.95,  2.44, 1.50]    | [ 0.00, -0.80, -0.00]   |  0.80 |  0.63 | RETREAT  | [0.00, -0.27, -0.00]
   499 | [-3.95,  2.40, 1.50]    | [ 0.00, -0.80, -0.00]   |  0.80 |  0.57 | RETREAT  | [0.00, -0.27, -0.00]
   500 | [-3.95,  2.37, 1.50]    | [ 0.00, -0.80, -0.00]   |  0.80 |  0.54 | RETREAT  | [0.00, -0.27, -0.00]
  ```

### [Seed 4021] Configuration: Shield ON (Oracle) — Outcome: `TIMEOUT`
- **Steps:** 500 | **Reward:** -2463.9 | **Min Clearance:** 0.198 m
- **Diagnostic Cause:** Exceeded maximum episode limit (500 steps) without reaching goal.
- **Last 5 Control Steps Telemetry:**
  ```
  Step | Pos [x, y, z]           | Vel [vx, vy, vz]        | Speed | Clr   | State    | Action Executed
  -----+-------------------------+-------------------------+-------+-------+----------+----------------
   496 | [ 3.90, -1.03, 1.50]    | [ 0.00, -0.80, -0.00]   |  0.80 |  0.57 | RETREAT  | [0.00, -0.27, -0.00]
   497 | [ 3.90, -1.06, 1.50]    | [ 0.00, -0.80, -0.00]   |  0.80 |  0.54 | RETREAT  | [0.00, -0.27, -0.00]
   498 | [ 3.90, -1.09, 1.50]    | [ 0.00, -0.80, -0.00]   |  0.80 |  0.54 | RETREAT  | [0.00, -0.27, -0.00]
   499 | [ 3.90, -1.13, 1.50]    | [ 0.00, -0.80, -0.00]   |  0.80 |  0.52 | RETREAT  | [0.00, -0.27, -0.00]
   500 | [ 3.90, -1.16, 1.50]    | [ 0.00, -0.80, -0.00]   |  0.80 |  0.55 | SCAN     | [0.00, -0.27, -0.00]
  ```

### [Seed 4023] Configuration: Shield ON (Oracle) — Outcome: `TIMEOUT`
- **Steps:** 500 | **Reward:** -995.01 | **Min Clearance:** 0.25 m
- **Diagnostic Cause:** Exceeded maximum episode limit (500 steps) without reaching goal.
- **Last 5 Control Steps Telemetry:**
  ```
  Step | Pos [x, y, z]           | Vel [vx, vy, vz]        | Speed | Clr   | State    | Action Executed
  -----+-------------------------+-------------------------+-------+-------+----------+----------------
   496 | [-0.20,  3.13, 1.50]    | [ 0.00,  0.00, 0.00]    |  0.00 |  0.55 | BRAKE    | [0.00, 0.00, 0.00]
   497 | [-0.20,  3.13, 1.50]    | [ 0.00,  0.00, 0.00]    |  0.00 |  0.47 | SCAN     | [0.00, 0.00, 0.00]
   498 | [-0.15,  3.20, 1.50]    | [ 1.05,  1.50, -0.00]   |  1.83 |  0.47 | REROUTE  | [0.35, 0.50, -0.00]
   499 | [-0.14,  3.26, 1.50]    | [ 0.27,  1.60, -0.00]   |  1.62 |  0.37 | REROUTE  | [0.09, 0.53, -0.00]
   500 | [-0.17,  3.33, 1.50]    | [-0.73,  1.50, -0.00]   |  1.67 |  0.32 | REROUTE  | [-0.24, 0.50, -0.00]
  ```

### [Seed 4024] Configuration: Shield ON (Oracle) — Outcome: `TIMEOUT`
- **Steps:** 500 | **Reward:** -218.6 | **Min Clearance:** 0.309 m
- **Diagnostic Cause:** Exceeded maximum episode limit (500 steps) without reaching goal.
- **Last 5 Control Steps Telemetry:**
  ```
  Step | Pos [x, y, z]           | Vel [vx, vy, vz]        | Speed | Clr   | State    | Action Executed
  -----+-------------------------+-------------------------+-------+-------+----------+----------------
   496 | [ 0.27, -4.95, 1.50]    | [ 0.00, -0.80, 0.00]    |  0.80 |  0.59 | RETREAT  | [0.00, -0.27, 0.00]
   497 | [ 0.27, -4.99, 1.50]    | [ 0.00, -0.80, 0.00]    |  0.80 |  0.54 | RETREAT  | [0.00, -0.27, 0.00]
   498 | [ 0.27, -5.02, 1.50]    | [ 0.00, -0.80, 0.00]    |  0.80 |  0.74 | RETREAT  | [0.00, -0.27, 0.00]
   499 | [ 0.27, -5.05, 1.50]    | [ 0.00, -0.80, 0.00]    |  0.80 |  0.53 | RETREAT  | [0.00, -0.27, 0.00]
   500 | [ 0.27, -5.09, 1.50]    | [ 0.00, -0.80, 0.00]    |  0.80 |  0.81 | RETREAT  | [0.00, -0.27, 0.00]
  ```

### [Seed 4026] Configuration: Shield ON (Oracle) — Outcome: `TIMEOUT`
- **Steps:** 500 | **Reward:** -1459.81 | **Min Clearance:** 0.392 m
- **Diagnostic Cause:** Exceeded maximum episode limit (500 steps) without reaching goal.
- **Last 5 Control Steps Telemetry:**
  ```
  Step | Pos [x, y, z]           | Vel [vx, vy, vz]        | Speed | Clr   | State    | Action Executed
  -----+-------------------------+-------------------------+-------+-------+----------+----------------
   496 | [-1.68,  3.47, 1.50]    | [ 1.50,  0.40, 0.00]    |  1.55 |  0.45 | REROUTE  | [0.50, 0.13, 0.00]
   497 | [-1.61,  3.47, 1.50]    | [ 1.50,  0.00, 0.00]    |  1.50 |  0.42 | REROUTE  | [0.50, 0.00, 0.00]
   498 | [-1.55,  3.47, 1.50]    | [ 1.50,  0.00, 0.00]    |  1.50 |  0.43 | REROUTE  | [0.50, 0.00, 0.00]
   499 | [-1.49,  3.47, 1.50]    | [ 1.50,  0.00, 0.00]    |  1.50 |  0.42 | REROUTE  | [0.50, 0.00, 0.00]
   500 | [-1.43,  3.47, 1.50]    | [ 1.50,  0.00, 0.00]    |  1.50 |  0.41 | REROUTE  | [0.50, 0.00, 0.00]
  ```

### [Seed 4036] Configuration: Shield ON (Oracle) — Outcome: `TIMEOUT`
- **Steps:** 500 | **Reward:** -1324.44 | **Min Clearance:** 0.075 m
- **Diagnostic Cause:** Exceeded maximum episode limit (500 steps) without reaching goal.
- **Last 5 Control Steps Telemetry:**
  ```
  Step | Pos [x, y, z]           | Vel [vx, vy, vz]        | Speed | Clr   | State    | Action Executed
  -----+-------------------------+-------------------------+-------+-------+----------+----------------
   496 | [ 3.92,  3.71, 1.50]    | [ 0.77,  1.60, -0.00]   |  1.78 |  0.36 | REROUTE  | [0.26, 0.53, -0.00]
   497 | [ 3.92,  3.74, 1.50]    | [ 0.00,  0.54, 0.03]    |  0.54 |  0.59 | NOMINAL  | [0.00, 0.18, 0.01]
   498 | [ 3.92,  3.74, 1.50]    | [-0.00,  0.00, 0.01]    |  0.00 |  0.27 | NOMINAL  | [-0.00, 0.00, 0.00]
   499 | [ 3.92,  3.74, 1.50]    | [ 0.00,  0.00, 0.06]    |  0.00 |  0.27 | NOMINAL  | [0.00, 0.00, 0.02]
   500 | [ 3.92,  3.74, 1.50]    | [ 0.00,  0.00, 0.00]    |  0.00 |  0.57 | BRAKE    | [0.00, 0.00, 0.00]
  ```

### [Seed 4048] Configuration: Shield ON (Oracle) — Outcome: `TIMEOUT`
- **Steps:** 500 | **Reward:** -1546.21 | **Min Clearance:** 0.075 m
- **Diagnostic Cause:** Exceeded maximum episode limit (500 steps) without reaching goal.
- **Last 5 Control Steps Telemetry:**
  ```
  Step | Pos [x, y, z]           | Vel [vx, vy, vz]        | Speed | Clr   | State    | Action Executed
  -----+-------------------------+-------------------------+-------+-------+----------+----------------
   496 | [-0.86, -3.23, 1.50]    | [ 0.00,  0.00, 0.00]    |  0.00 |  0.56 | BRAKE    | [0.00, 0.00, 0.00]
   497 | [-0.86, -3.23, 1.50]    | [ 0.00,  0.00, 0.00]    |  0.00 |  0.56 | SCAN     | [0.00, 0.00, 0.00]
   498 | [-0.86, -3.17, 1.50]    | [ 0.00,  1.50, -0.00]   |  1.50 |  0.56 | REROUTE  | [0.00, 0.50, -0.00]
   499 | [-0.86, -3.10, 1.50]    | [-0.00,  1.50, -0.00]   |  1.50 |  0.60 | REROUTE  | [-0.00, 0.50, -0.00]
   500 | [-0.86, -3.14, 1.50]    | [ 0.00, -0.80, -0.00]   |  0.80 |  0.60 | RETREAT  | [0.00, -0.27, -0.00]
  ```

### [Seed 4049] Configuration: Shield ON (Oracle) — Outcome: `TIMEOUT`
- **Steps:** 500 | **Reward:** -2616.02 | **Min Clearance:** 0.08 m
- **Diagnostic Cause:** Exceeded maximum episode limit (500 steps) without reaching goal.
- **Last 5 Control Steps Telemetry:**
  ```
  Step | Pos [x, y, z]           | Vel [vx, vy, vz]        | Speed | Clr   | State    | Action Executed
  -----+-------------------------+-------------------------+-------+-------+----------+----------------
   496 | [-3.95,  0.56, 1.50]    | [ 0.00, -0.80, 0.00]    |  0.80 |  0.52 | RETREAT  | [0.00, -0.27, 0.00]
   497 | [-3.95,  0.52, 1.50]    | [ 0.00, -0.80, 0.00]    |  0.80 |  0.28 | RETREAT  | [0.00, -0.27, 0.00]
   498 | [-3.95,  0.49, 1.50]    | [ 0.00, -0.80, 0.00]    |  0.80 |  0.48 | RETREAT  | [0.00, -0.27, 0.00]
   499 | [-3.95,  0.46, 1.50]    | [ 0.00, -0.80, 0.00]    |  0.80 |  0.46 | SCAN     | [0.00, -0.27, 0.00]
   500 | [-3.95,  0.52, 1.50]    | [ 0.00,  1.50, 0.00]    |  1.50 |  0.46 | REROUTE  | [0.00, 0.50, 0.00]
  ```

### [Seed 4052] Configuration: Shield ON (Oracle) — Outcome: `TIMEOUT`
- **Steps:** 500 | **Reward:** -887.96 | **Min Clearance:** 0.121 m
- **Diagnostic Cause:** Exceeded maximum episode limit (500 steps) without reaching goal.
- **Last 5 Control Steps Telemetry:**
  ```
  Step | Pos [x, y, z]           | Vel [vx, vy, vz]        | Speed | Clr   | State    | Action Executed
  -----+-------------------------+-------------------------+-------+-------+----------+----------------
   496 | [-0.31, -5.10, 1.50]    | [-1.50,  0.00, 0.00]    |  1.50 |  0.23 | REROUTE  | [-0.50, 0.00, 0.00]
   497 | [-0.37, -5.10, 1.50]    | [-1.50,  0.00, 0.00]    |  1.50 |  0.22 | REROUTE  | [-0.50, 0.00, 0.00]
   498 | [-0.43, -5.10, 1.50]    | [-1.50,  0.00, 0.00]    |  1.50 |  0.22 | REROUTE  | [-0.50, 0.00, 0.00]
   499 | [-0.50, -5.10, 1.50]    | [-1.50,  0.00, 0.00]    |  1.50 |  0.22 | REROUTE  | [-0.50, 0.00, 0.00]
   500 | [-0.56, -5.10, 1.50]    | [-1.50,  0.00, 0.00]    |  1.50 |  0.23 | REROUTE  | [-0.50, 0.00, 0.00]
  ```

### [Seed 4053] Configuration: Shield ON (Oracle) — Outcome: `TIMEOUT`
- **Steps:** 500 | **Reward:** -2420.6 | **Min Clearance:** 0.117 m
- **Diagnostic Cause:** Exceeded maximum episode limit (500 steps) without reaching goal.
- **Last 5 Control Steps Telemetry:**
  ```
  Step | Pos [x, y, z]           | Vel [vx, vy, vz]        | Speed | Clr   | State    | Action Executed
  -----+-------------------------+-------------------------+-------+-------+----------+----------------
   496 | [-3.93,  0.78, 1.50]    | [ 0.20,  0.40, 0.01]    |  0.45 |  0.46 | REROUTE  | [0.07, 0.13, 0.00]
   497 | [-3.93,  0.75, 1.50]    | [ 0.00, -0.80, 0.01]    |  0.80 |  0.54 | RETREAT  | [0.00, -0.27, 0.00]
   498 | [-3.93,  0.72, 1.50]    | [ 0.00, -0.80, 0.01]    |  0.80 |  0.49 | RETREAT  | [0.00, -0.27, 0.00]
   499 | [-3.93,  0.68, 1.50]    | [ 0.00, -0.80, 0.01]    |  0.80 |  0.63 | RETREAT  | [0.00, -0.27, 0.00]
   500 | [-3.93,  0.65, 1.50]    | [ 0.00, -0.80, 0.01]    |  0.80 |  0.66 | RETREAT  | [0.00, -0.27, 0.00]
  ```

### [Seed 4055] Configuration: Shield ON (Oracle) — Outcome: `TIMEOUT`
- **Steps:** 500 | **Reward:** -2317.92 | **Min Clearance:** 0.387 m
- **Diagnostic Cause:** Exceeded maximum episode limit (500 steps) without reaching goal.
- **Last 5 Control Steps Telemetry:**
  ```
  Step | Pos [x, y, z]           | Vel [vx, vy, vz]        | Speed | Clr   | State    | Action Executed
  -----+-------------------------+-------------------------+-------+-------+----------+----------------
   496 | [-0.67, -0.39, 1.50]    | [ 0.00, -0.80, -0.00]   |  0.80 |  0.72 | SCAN     | [0.00, -0.27, -0.00]
   497 | [-0.61, -0.32, 1.50]    | [ 1.50,  1.50, -0.00]   |  2.12 |  0.74 | REROUTE  | [0.50, 0.50, -0.00]
   498 | [-0.56, -0.26, 1.50]    | [ 1.22,  1.60, -0.00]   |  2.01 |  0.55 | REROUTE  | [0.41, 0.53, -0.00]
   499 | [-0.53, -0.19, 1.50]    | [ 0.77,  1.60, -0.00]   |  1.77 |  0.47 | REROUTE  | [0.26, 0.53, -0.00]
   500 | [-0.53, -0.22, 1.50]    | [ 0.00, -0.80, -0.00]   |  0.80 |  0.41 | RETREAT  | [0.00, -0.27, -0.00]
  ```

### [Seed 4056] Configuration: Shield ON (Oracle) — Outcome: `TIMEOUT`
- **Steps:** 500 | **Reward:** -3264.63 | **Min Clearance:** 0.187 m
- **Diagnostic Cause:** Exceeded maximum episode limit (500 steps) without reaching goal.
- **Last 5 Control Steps Telemetry:**
  ```
  Step | Pos [x, y, z]           | Vel [vx, vy, vz]        | Speed | Clr   | State    | Action Executed
  -----+-------------------------+-------------------------+-------+-------+----------+----------------
   496 | [ 0.54, -1.03, 1.50]    | [ 1.10,  0.00, 0.00]    |  1.10 |  0.34 | REROUTE  | [0.37, 0.00, 0.00]
   497 | [ 0.58, -1.03, 1.50]    | [ 0.90,  0.00, 0.00]    |  0.90 |  0.34 | REROUTE  | [0.30, 0.00, 0.00]
   498 | [ 0.60, -1.03, 1.50]    | [ 0.68,  0.00, 0.00]    |  0.68 |  0.38 | REROUTE  | [0.23, 0.00, 0.00]
   499 | [ 0.62, -1.03, 1.50]    | [ 0.46,  0.00, 0.00]    |  0.46 |  0.35 | REROUTE  | [0.15, 0.00, 0.00]
   500 | [ 0.63, -1.03, 1.50]    | [ 0.19,  0.00, 0.00]    |  0.19 |  0.36 | REROUTE  | [0.07, 0.00, 0.00]
  ```

### [Seed 4000] Configuration: Shield ON (Camera) — Outcome: `OBSTACLE_COLLISION`
- **Steps:** 67 | **Reward:** -77.9 | **Min Clearance:** 0.563 m
- **Diagnostic Cause:** Obstacle collision at speed 2.65 m/s (min clearance 1.33m).
- **Last 5 Control Steps Telemetry:**
  ```
  Step | Pos [x, y, z]           | Vel [vx, vy, vz]        | Speed | Clr   | State    | Action Executed
  -----+-------------------------+-------------------------+-------+-------+----------+----------------
    63 | [ 0.81, -2.15, 1.50]    | [-1.90,  1.71, -0.00]   |  2.56 |  1.57 | NOMINAL  | [-0.63, 0.57, -0.00]
    64 | [ 0.76, -2.09, 1.50]    | [-1.33,  1.64, -0.01]   |  2.12 |  1.50 | NOMINAL  | [-0.44, 0.55, -0.00]
    65 | [ 0.86, -2.03, 1.50]    | [ 2.44,  1.40, -0.03]   |  2.82 |  1.43 | NOMINAL  | [0.81, 0.47, -0.01]
    66 | [ 0.96, -1.98, 1.50]    | [ 2.43,  1.23, -0.00]   |  2.72 |  1.37 | NOMINAL  | [0.81, 0.41, -0.00]
    67 | [ 1.06, -1.93, 1.50]    | [ 2.40,  1.12, 0.00]    |  2.65 |  1.33 | NOMINAL  | [0.80, 0.38, 0.00]
  ```

### [Seed 4001] Configuration: Shield ON (Camera) — Outcome: `TIMEOUT`
- **Steps:** 500 | **Reward:** -2705.27 | **Min Clearance:** 0.329 m
- **Diagnostic Cause:** Exceeded maximum episode limit (500 steps) without reaching goal.
- **Last 5 Control Steps Telemetry:**
  ```
  Step | Pos [x, y, z]           | Vel [vx, vy, vz]        | Speed | Clr   | State    | Action Executed
  -----+-------------------------+-------------------------+-------+-------+----------+----------------
   496 | [-3.77, -1.31, 1.50]    | [ 0.00, -0.80, -0.00]   |  0.80 |  0.56 | RETREAT  | [0.00, -0.27, -0.00]
   497 | [-3.77, -1.35, 1.50]    | [ 0.00, -0.80, -0.00]   |  0.80 |  0.59 | SCAN     | [0.00, -0.27, -0.00]
   498 | [-3.71, -1.33, 1.50]    | [ 1.50,  0.40, -0.00]   |  1.55 |  0.62 | REROUTE  | [0.50, 0.13, -0.00]
   499 | [-3.65, -1.31, 1.50]    | [ 1.50,  0.40, -0.00]   |  1.55 |  0.61 | REROUTE  | [0.50, 0.13, -0.00]
   500 | [-3.59, -1.30, 1.50]    | [ 1.50,  0.40, -0.00]   |  1.55 |  0.60 | REROUTE  | [0.50, 0.13, -0.00]
  ```

### [Seed 4002] Configuration: Shield ON (Camera) — Outcome: `OBSTACLE_COLLISION`
- **Steps:** 57 | **Reward:** 35.1 | **Min Clearance:** 0.38 m
- **Diagnostic Cause:** Obstacle collision at speed 3.00 m/s (min clearance 3.35m).
- **Last 5 Control Steps Telemetry:**
  ```
  Step | Pos [x, y, z]           | Vel [vx, vy, vz]        | Speed | Clr   | State    | Action Executed
  -----+-------------------------+-------------------------+-------+-------+----------+----------------
    53 | [-0.15, -4.18, 1.48]    | [ 1.50,  1.60, 0.04]    |  2.19 |  3.57 | REROUTE  | [0.50, 0.53, 0.01]
    54 | [-0.07, -4.11, 1.48]    | [ 1.94,  1.62, 0.00]    |  2.53 |  3.50 | NOMINAL  | [0.65, 0.54, 0.00]
    55 | [-0.02, -4.05, 1.49]    | [ 1.16,  1.26, 0.13]    |  1.72 |  3.43 | NOMINAL  | [0.39, 0.42, 0.04]
    56 | [-0.11, -4.03, 1.49]    | [-2.12,  0.71, -0.00]   |  2.23 |  3.38 | NOMINAL  | [-0.71, 0.24, -0.00]
    57 | [-0.23, -3.97, 1.49]    | [-2.72,  1.26, -0.05]   |  3.00 |  3.35 | NOMINAL  | [-0.91, 0.42, -0.02]
  ```

### [Seed 4003] Configuration: Shield ON (Camera) — Outcome: `TIMEOUT`
- **Steps:** 500 | **Reward:** -2971.6 | **Min Clearance:** 0.353 m
- **Diagnostic Cause:** Exceeded maximum episode limit (500 steps) without reaching goal.
- **Last 5 Control Steps Telemetry:**
  ```
  Step | Pos [x, y, z]           | Vel [vx, vy, vz]        | Speed | Clr   | State    | Action Executed
  -----+-------------------------+-------------------------+-------+-------+----------+----------------
   496 | [ 3.27, -1.18, 1.50]    | [ 0.00, -0.80, -0.00]   |  0.80 |  0.54 | RETREAT  | [0.00, -0.27, -0.00]
   497 | [ 3.27, -1.21, 1.50]    | [ 0.00, -0.80, -0.00]   |  0.80 |  0.57 | RETREAT  | [0.00, -0.27, -0.00]
   498 | [ 3.27, -1.24, 1.50]    | [ 0.00, -0.80, -0.00]   |  0.80 |  0.60 | RETREAT  | [0.00, -0.27, -0.00]
   499 | [ 3.27, -1.27, 1.50]    | [ 0.00, -0.80, -0.00]   |  0.80 |  0.64 | SCAN     | [0.00, -0.27, -0.00]
   500 | [ 3.24, -1.26, 1.50]    | [-0.91,  0.40, -0.00]   |  0.99 |  0.67 | REROUTE  | [-0.30, 0.13, -0.00]
  ```

### [Seed 4004] Configuration: Shield ON (Camera) — Outcome: `OBSTACLE_COLLISION`
- **Steps:** 73 | **Reward:** -97.52 | **Min Clearance:** 0.394 m
- **Diagnostic Cause:** Obstacle collision at speed 2.94 m/s (min clearance 1.97m).
- **Last 5 Control Steps Telemetry:**
  ```
  Step | Pos [x, y, z]           | Vel [vx, vy, vz]        | Speed | Clr   | State    | Action Executed
  -----+-------------------------+-------------------------+-------+-------+----------+----------------
    69 | [-0.37, -3.01, 1.50]    | [ 0.00,  0.00, 0.00]    |  0.00 |  0.39 | SCAN     | [0.00, 0.00, 0.00]
    70 | [-0.43, -3.01, 1.50]    | [-1.50,  0.00, 0.00]    |  1.50 |  0.39 | REROUTE  | [-0.50, 0.00, 0.00]
    71 | [-0.49, -2.94, 1.50]    | [-1.50,  1.60, 0.00]    |  2.19 |  2.24 | REROUTE  | [-0.50, 0.53, 0.00]
    72 | [-0.38, -2.88, 1.50]    | [ 2.60,  1.50, -0.03]   |  3.00 |  2.17 | NOMINAL  | [0.86, 0.50, -0.01]
    73 | [-0.27, -2.83, 1.50]    | [ 2.65,  1.29, -0.01]   |  2.94 |  1.97 | NOMINAL  | [0.88, 0.43, -0.01]
  ```

### [Seed 4005] Configuration: Shield ON (Camera) — Outcome: `OBSTACLE_COLLISION`
- **Steps:** 43 | **Reward:** 43.09 | **Min Clearance:** 2.063 m
- **Diagnostic Cause:** Obstacle collision at speed 3.00 m/s (min clearance 2.41m).
- **Last 5 Control Steps Telemetry:**
  ```
  Step | Pos [x, y, z]           | Vel [vx, vy, vz]        | Speed | Clr   | State    | Action Executed
  -----+-------------------------+-------------------------+-------+-------+----------+----------------
    39 | [ 0.06, -3.42, 1.52]    | [-0.20,  2.78, 0.00]    |  2.79 |  2.85 | NOMINAL  | [-0.07, 0.93, 0.00]
    40 | [ 0.05, -3.30, 1.52]    | [-0.28,  2.74, -0.02]   |  2.75 |  2.74 | NOMINAL  | [-0.09, 0.91, -0.01]
    41 | [ 0.03, -3.19, 1.52]    | [-0.45,  2.74, -0.01]   |  2.77 |  2.62 | NOMINAL  | [-0.15, 0.91, -0.00]
    42 | [ 0.10, -3.08, 1.52]    | [ 1.64,  2.51, -0.00]   |  3.00 |  2.51 | NOMINAL  | [0.55, 0.84, -0.00]
    43 | [ 0.19, -3.00, 1.52]    | [ 2.16,  2.09, -0.02]   |  3.00 |  2.41 | NOMINAL  | [0.72, 0.69, -0.01]
  ```

### [Seed 4006] Configuration: Shield ON (Camera) — Outcome: `TIMEOUT`
- **Steps:** 500 | **Reward:** -2384.96 | **Min Clearance:** 0.104 m
- **Diagnostic Cause:** Exceeded maximum episode limit (500 steps) without reaching goal.
- **Last 5 Control Steps Telemetry:**
  ```
  Step | Pos [x, y, z]           | Vel [vx, vy, vz]        | Speed | Clr   | State    | Action Executed
  -----+-------------------------+-------------------------+-------+-------+----------+----------------
   496 | [ 3.60, -0.97, 1.50]    | [ 1.50,  0.00, 0.00]    |  1.50 |  0.42 | REROUTE  | [0.50, 0.00, 0.00]
   497 | [ 3.66, -0.97, 1.50]    | [ 1.50,  0.00, 0.00]    |  1.50 |  0.42 | REROUTE  | [0.50, 0.00, 0.00]
   498 | [ 3.73, -0.97, 1.50]    | [ 1.50,  0.00, 0.00]    |  1.50 |  0.42 | REROUTE  | [0.50, 0.00, 0.00]
   499 | [ 3.78, -0.97, 1.50]    | [ 1.42,  0.00, 0.00]    |  1.42 |  0.41 | REROUTE  | [0.47, 0.00, 0.00]
   500 | [ 3.83, -0.97, 1.50]    | [ 1.22,  0.00, 0.00]    |  1.22 |  0.41 | REROUTE  | [0.41, 0.00, 0.00]
  ```

### [Seed 4007] Configuration: Shield ON (Camera) — Outcome: `TIMEOUT`
- **Steps:** 500 | **Reward:** -2905.45 | **Min Clearance:** 0.335 m
- **Diagnostic Cause:** Exceeded maximum episode limit (500 steps) without reaching goal.
- **Last 5 Control Steps Telemetry:**
  ```
  Step | Pos [x, y, z]           | Vel [vx, vy, vz]        | Speed | Clr   | State    | Action Executed
  -----+-------------------------+-------------------------+-------+-------+----------+----------------
   496 | [-3.01, -1.32, 1.50]    | [ 0.00, -0.80, -0.00]   |  0.80 |  0.55 | RETREAT  | [0.00, -0.27, -0.00]
   497 | [-3.01, -1.35, 1.50]    | [ 0.00, -0.80, -0.00]   |  0.80 |  0.58 | SCAN     | [0.00, -0.27, -0.00]
   498 | [-2.97, -1.33, 1.50]    | [ 0.95,  0.40, -0.00]   |  1.03 |  0.62 | REROUTE  | [0.32, 0.13, -0.00]
   499 | [-2.91, -1.32, 1.50]    | [ 1.50,  0.40, -0.00]   |  1.55 |  0.60 | REROUTE  | [0.50, 0.13, -0.00]
   500 | [-2.85, -1.30, 1.50]    | [ 1.50,  0.40, -0.00]   |  1.55 |  0.59 | REROUTE  | [0.50, 0.13, -0.00]
  ```

### [Seed 4008] Configuration: Shield ON (Camera) — Outcome: `OBSTACLE_COLLISION`
- **Steps:** 27 | **Reward:** -25.27 | **Min Clearance:** 0.931 m
- **Diagnostic Cause:** Obstacle collision at speed 2.62 m/s (min clearance 1.32m).
- **Last 5 Control Steps Telemetry:**
  ```
  Step | Pos [x, y, z]           | Vel [vx, vy, vz]        | Speed | Clr   | State    | Action Executed
  -----+-------------------------+-------------------------+-------+-------+----------+----------------
    23 | [-0.27, -5.57, 1.50]    | [-0.33,  2.70, 0.00]    |  2.72 |  1.77 | NOMINAL  | [-0.11, 0.90, 0.00]
    24 | [-0.27, -5.45, 1.50]    | [-0.01,  2.78, -0.02]   |  2.78 |  1.66 | NOMINAL  | [-0.00, 0.93, -0.01]
    25 | [-0.30, -5.33, 1.50]    | [-0.72,  2.83, 0.01]    |  2.92 |  1.55 | NOMINAL  | [-0.24, 0.94, 0.00]
    26 | [-0.30, -5.22, 1.50]    | [ 0.13,  2.71, 0.02]    |  2.71 |  1.43 | NOMINAL  | [0.04, 0.90, 0.01]
    27 | [-0.23, -5.13, 1.50]    | [ 1.50,  2.16, -0.01]   |  2.62 |  1.32 | NOMINAL  | [0.50, 0.72, -0.01]
  ```

### [Seed 4009] Configuration: Shield ON (Camera) — Outcome: `TIMEOUT`
- **Steps:** 500 | **Reward:** -2316.06 | **Min Clearance:** 0.324 m
- **Diagnostic Cause:** Exceeded maximum episode limit (500 steps) without reaching goal.
- **Last 5 Control Steps Telemetry:**
  ```
  Step | Pos [x, y, z]           | Vel [vx, vy, vz]        | Speed | Clr   | State    | Action Executed
  -----+-------------------------+-------------------------+-------+-------+----------+----------------
   496 | [ 2.67, -0.99, 1.50]    | [ 1.50,  0.05, -0.00]   |  1.50 |  0.45 | REROUTE  | [0.50, 0.02, -0.00]
   497 | [ 2.73, -0.98, 1.50]    | [ 1.50,  0.18, -0.00]   |  1.51 |  0.45 | REROUTE  | [0.50, 0.06, -0.00]
   498 | [ 2.80, -0.97, 1.50]    | [ 1.50,  0.13, -0.00]   |  1.50 |  0.45 | REROUTE  | [0.50, 0.04, -0.00]
   499 | [ 2.86, -0.97, 1.50]    | [ 1.50,  0.14, -0.00]   |  1.51 |  0.45 | REROUTE  | [0.50, 0.05, -0.00]
   500 | [ 2.92, -0.96, 1.50]    | [ 1.50,  0.14, -0.00]   |  1.51 |  0.45 | REROUTE  | [0.50, 0.04, -0.00]
  ```

### [Seed 4010] Configuration: Shield ON (Camera) — Outcome: `TIMEOUT`
- **Steps:** 500 | **Reward:** -2437.96 | **Min Clearance:** 0.352 m
- **Diagnostic Cause:** Exceeded maximum episode limit (500 steps) without reaching goal.
- **Last 5 Control Steps Telemetry:**
  ```
  Step | Pos [x, y, z]           | Vel [vx, vy, vz]        | Speed | Clr   | State    | Action Executed
  -----+-------------------------+-------------------------+-------+-------+----------+----------------
   496 | [-3.06, -1.26, 1.50]    | [ 0.00, -0.80, -0.00]   |  0.80 |  0.52 | RETREAT  | [0.00, -0.27, -0.00]
   497 | [-3.06, -1.30, 1.50]    | [ 0.00, -0.80, -0.00]   |  0.80 |  0.55 | RETREAT  | [0.00, -0.27, -0.00]
   498 | [-3.06, -1.33, 1.50]    | [ 0.00, -0.80, -0.00]   |  0.80 |  0.59 | SCAN     | [0.00, -0.27, -0.00]
   499 | [-3.02, -1.31, 1.50]    | [ 0.91,  0.40, -0.00]   |  0.99 |  0.62 | REROUTE  | [0.30, 0.13, -0.00]
   500 | [-2.96, -1.30, 1.50]    | [ 1.50,  0.40, -0.00]   |  1.55 |  0.60 | REROUTE  | [0.50, 0.13, -0.00]
  ```

### [Seed 4011] Configuration: Shield ON (Camera) — Outcome: `OBSTACLE_COLLISION`
- **Steps:** 80 | **Reward:** -122.41 | **Min Clearance:** 0.518 m
- **Diagnostic Cause:** Obstacle collision at speed 1.55 m/s (min clearance 0.52m).
- **Last 5 Control Steps Telemetry:**
  ```
  Step | Pos [x, y, z]           | Vel [vx, vy, vz]        | Speed | Clr   | State    | Action Executed
  -----+-------------------------+-------------------------+-------+-------+----------+----------------
    76 | [-1.08, -1.19, 1.50]    | [ 0.00,  0.00, 0.00]    |  0.00 |  0.55 | BRAKE    | [0.00, 0.00, 0.00]
    77 | [-1.08, -1.19, 1.50]    | [ 0.00,  0.00, 0.00]    |  0.00 |  0.55 | SCAN     | [0.00, 0.00, 0.00]
    78 | [-1.14, -1.17, 1.50]    | [-1.50,  0.40, -0.01]   |  1.55 |  0.55 | REROUTE  | [-0.50, 0.13, -0.00]
    79 | [-1.21, -1.15, 1.50]    | [-1.50,  0.40, -0.01]   |  1.55 |  0.53 | REROUTE  | [-0.50, 0.13, -0.00]
    80 | [-1.27, -1.14, 1.50]    | [-1.50,  0.40, -0.01]   |  1.55 |  0.52 | REROUTE  | [-0.50, 0.13, -0.00]
  ```

### [Seed 4012] Configuration: Shield ON (Camera) — Outcome: `OBSTACLE_COLLISION`
- **Steps:** 73 | **Reward:** -130.93 | **Min Clearance:** 0.847 m
- **Diagnostic Cause:** Obstacle collision at speed 1.63 m/s (min clearance 0.85m).
- **Last 5 Control Steps Telemetry:**
  ```
  Step | Pos [x, y, z]           | Vel [vx, vy, vz]        | Speed | Clr   | State    | Action Executed
  -----+-------------------------+-------------------------+-------+-------+----------+----------------
    69 | [-1.06, -1.56, 1.51]    | [-1.74,  0.70, 0.00]    |  1.88 |  0.94 | NOMINAL  | [-0.58, 0.23, 0.00]
    70 | [-1.12, -1.52, 1.51]    | [-1.64,  0.76, -0.02]   |  1.81 |  0.92 | NOMINAL  | [-0.55, 0.25, -0.01]
    71 | [-1.19, -1.50, 1.51]    | [-1.63,  0.60, 0.06]    |  1.74 |  0.89 | NOMINAL  | [-0.54, 0.20, 0.02]
    72 | [-1.26, -1.47, 1.51]    | [-1.57,  0.63, -0.07]   |  1.69 |  0.87 | NOMINAL  | [-0.52, 0.21, -0.03]
    73 | [-1.32, -1.44, 1.51]    | [-1.42,  0.81, -0.01]   |  1.63 |  0.85 | NOMINAL  | [-0.47, 0.27, -0.00]
  ```

### [Seed 4013] Configuration: Shield ON (Camera) — Outcome: `TIMEOUT`
- **Steps:** 500 | **Reward:** -2367.05 | **Min Clearance:** 0.371 m
- **Diagnostic Cause:** Exceeded maximum episode limit (500 steps) without reaching goal.
- **Last 5 Control Steps Telemetry:**
  ```
  Step | Pos [x, y, z]           | Vel [vx, vy, vz]        | Speed | Clr   | State    | Action Executed
  -----+-------------------------+-------------------------+-------+-------+----------+----------------
   496 | [ 2.16, -1.09, 1.50]    | [ 1.50,  0.40, -0.00]   |  1.55 |  0.53 | REROUTE  | [0.50, 0.13, -0.00]
   497 | [ 2.23, -1.07, 1.50]    | [ 1.50,  0.40, -0.00]   |  1.55 |  0.52 | REROUTE  | [0.50, 0.13, -0.00]
   498 | [ 2.29, -1.06, 1.50]    | [ 1.50,  0.40, -0.00]   |  1.55 |  0.50 | REROUTE  | [0.50, 0.13, -0.00]
   499 | [ 2.35, -1.04, 1.50]    | [ 1.50,  0.40, -0.00]   |  1.55 |  0.48 | REROUTE  | [0.50, 0.13, -0.00]
   500 | [ 2.41, -1.03, 1.50]    | [ 1.50,  0.24, -0.00]   |  1.52 |  0.46 | REROUTE  | [0.50, 0.08, -0.00]
  ```

### [Seed 4014] Configuration: Shield ON (Camera) — Outcome: `TIMEOUT`
- **Steps:** 500 | **Reward:** -2343.71 | **Min Clearance:** 0.375 m
- **Diagnostic Cause:** Exceeded maximum episode limit (500 steps) without reaching goal.
- **Last 5 Control Steps Telemetry:**
  ```
  Step | Pos [x, y, z]           | Vel [vx, vy, vz]        | Speed | Clr   | State    | Action Executed
  -----+-------------------------+-------------------------+-------+-------+----------+----------------
   496 | [ 2.96, -1.05, 1.50]    | [-1.50,  0.37, 0.00]    |  1.55 |  0.47 | REROUTE  | [-0.50, 0.12, 0.00]
   497 | [ 2.90, -1.04, 1.50]    | [-1.50,  0.17, 0.00]    |  1.51 |  0.45 | REROUTE  | [-0.50, 0.06, 0.00]
   498 | [ 2.83, -1.04, 1.50]    | [-1.50,  0.00, 0.00]    |  1.50 |  0.45 | REROUTE  | [-0.50, 0.00, 0.00]
   499 | [ 2.77, -1.04, 1.50]    | [-1.50,  0.14, 0.00]    |  1.51 |  0.45 | REROUTE  | [-0.50, 0.05, 0.00]
   500 | [ 2.71, -1.04, 1.50]    | [-1.50,  0.00, 0.00]    |  1.50 |  0.45 | REROUTE  | [-0.50, 0.00, 0.00]
  ```

### [Seed 4015] Configuration: Shield ON (Camera) — Outcome: `OBSTACLE_COLLISION`
- **Steps:** 104 | **Reward:** -333.11 | **Min Clearance:** 0.459 m
- **Diagnostic Cause:** Obstacle collision at speed 1.53 m/s (min clearance 0.46m).
- **Last 5 Control Steps Telemetry:**
  ```
  Step | Pos [x, y, z]           | Vel [vx, vy, vz]        | Speed | Clr   | State    | Action Executed
  -----+-------------------------+-------------------------+-------+-------+----------+----------------
   100 | [ 1.93, -1.08, 1.50]    | [ 1.50,  0.40, -0.01]   |  1.55 |  0.50 | REROUTE  | [0.50, 0.13, -0.00]
   101 | [ 1.99, -1.06, 1.50]    | [ 1.50,  0.40, -0.01]   |  1.55 |  0.49 | REROUTE  | [0.50, 0.13, -0.00]
   102 | [ 2.05, -1.05, 1.50]    | [ 1.50,  0.40, -0.01]   |  1.55 |  0.48 | REROUTE  | [0.50, 0.13, -0.00]
   103 | [ 2.12, -1.03, 1.50]    | [ 1.50,  0.39, -0.01]   |  1.55 |  0.47 | REROUTE  | [0.50, 0.13, -0.00]
   104 | [ 2.18, -1.02, 1.50]    | [ 1.50,  0.28, -0.00]   |  1.53 |  0.46 | REROUTE  | [0.50, 0.09, -0.00]
  ```

### [Seed 4016] Configuration: Shield ON (Camera) — Outcome: `OBSTACLE_COLLISION`
- **Steps:** 23 | **Reward:** -9.71 | **Min Clearance:** 4.663 m
- **Diagnostic Cause:** Obstacle collision at speed 3.00 m/s (min clearance 4.66m).
- **Last 5 Control Steps Telemetry:**
  ```
  Step | Pos [x, y, z]           | Vel [vx, vy, vz]        | Speed | Clr   | State    | Action Executed
  -----+-------------------------+-------------------------+-------+-------+----------+----------------
    19 | [-0.08, -5.70, 1.50]    | [-1.05,  2.81, -0.02]   |  3.00 |  5.13 | NOMINAL  | [-0.35, 0.94, -0.01]
    20 | [-0.12, -5.58, 1.50]    | [-1.10,  2.79, -0.00]   |  3.00 |  5.01 | NOMINAL  | [-0.37, 0.93, -0.00]
    21 | [-0.17, -5.46, 1.50]    | [-1.15,  2.77, -0.01]   |  3.00 |  4.89 | NOMINAL  | [-0.38, 0.92, -0.00]
    22 | [-0.22, -5.35, 1.50]    | [-1.23,  2.74, -0.01]   |  3.00 |  4.78 | NOMINAL  | [-0.41, 0.91, -0.01]
    23 | [-0.28, -5.24, 1.50]    | [-1.38,  2.66, -0.03]   |  3.00 |  4.66 | NOMINAL  | [-0.46, 0.89, -0.01]
  ```

### [Seed 4017] Configuration: Shield ON (Camera) — Outcome: `OBSTACLE_COLLISION`
- **Steps:** 35 | **Reward:** 18.79 | **Min Clearance:** 0.841 m
- **Diagnostic Cause:** Obstacle collision at speed 2.79 m/s (min clearance 3.99m).
- **Last 5 Control Steps Telemetry:**
  ```
  Step | Pos [x, y, z]           | Vel [vx, vy, vz]        | Speed | Clr   | State    | Action Executed
  -----+-------------------------+-------------------------+-------+-------+----------+----------------
    31 | [ 0.63, -5.01, 1.50]    | [ 0.33,  2.66, -0.01]   |  2.68 |  4.45 | NOMINAL  | [0.11, 0.89, -0.00]
    32 | [ 0.60, -4.89, 1.50]    | [-0.69,  2.80, 0.00]    |  2.88 |  4.34 | NOMINAL  | [-0.23, 0.93, 0.00]
    33 | [ 0.59, -4.78, 1.50]    | [-0.37,  2.72, 0.01]    |  2.74 |  4.22 | NOMINAL  | [-0.12, 0.91, 0.00]
    34 | [ 0.57, -4.67, 1.50]    | [-0.37,  2.72, -0.01]   |  2.75 |  4.11 | NOMINAL  | [-0.12, 0.91, -0.00]
    35 | [ 0.58, -4.55, 1.50]    | [ 0.16,  2.79, -0.00]   |  2.79 |  3.99 | NOMINAL  | [0.05, 0.93, -0.00]
  ```

### [Seed 4018] Configuration: Shield ON (Camera) — Outcome: `OBSTACLE_COLLISION`
- **Steps:** 85 | **Reward:** -141.92 | **Min Clearance:** 0.445 m
- **Diagnostic Cause:** Obstacle collision at speed 1.50 m/s (min clearance 0.45m).
- **Last 5 Control Steps Telemetry:**
  ```
  Step | Pos [x, y, z]           | Vel [vx, vy, vz]        | Speed | Clr   | State    | Action Executed
  -----+-------------------------+-------------------------+-------+-------+----------+----------------
    81 | [ 0.35, -1.09, 1.49]    | [ 1.50,  0.30, 0.03]    |  1.53 |  0.46 | REROUTE  | [0.50, 0.10, 0.01]
    82 | [ 0.42, -1.09, 1.49]    | [ 1.50,  0.07, 0.03]    |  1.50 |  0.45 | REROUTE  | [0.50, 0.02, 0.01]
    83 | [ 0.48, -1.09, 1.49]    | [ 1.50,  0.16, 0.03]    |  1.51 |  0.45 | REROUTE  | [0.50, 0.05, 0.01]
    84 | [ 0.54, -1.09, 1.49]    | [ 1.50,  0.00, 0.02]    |  1.50 |  0.45 | REROUTE  | [0.50, 0.00, 0.01]
    85 | [ 0.60, -1.09, 1.49]    | [ 1.50,  0.00, 0.02]    |  1.50 |  0.45 | REROUTE  | [0.50, 0.00, 0.01]
  ```

### [Seed 4019] Configuration: Shield ON (Camera) — Outcome: `TIMEOUT`
- **Steps:** 500 | **Reward:** -2349.92 | **Min Clearance:** 0.374 m
- **Diagnostic Cause:** Exceeded maximum episode limit (500 steps) without reaching goal.
- **Last 5 Control Steps Telemetry:**
  ```
  Step | Pos [x, y, z]           | Vel [vx, vy, vz]        | Speed | Clr   | State    | Action Executed
  -----+-------------------------+-------------------------+-------+-------+----------+----------------
   496 | [ 2.96, -1.04, 1.50]    | [-1.50,  0.39, -0.00]   |  1.55 |  0.47 | REROUTE  | [-0.50, 0.13, -0.00]
   497 | [ 2.90, -1.03, 1.50]    | [-1.50,  0.19, -0.00]   |  1.51 |  0.45 | REROUTE  | [-0.50, 0.06, -0.00]
   498 | [ 2.83, -1.03, 1.50]    | [-1.50,  0.00, -0.00]   |  1.50 |  0.45 | REROUTE  | [-0.50, 0.00, -0.00]
   499 | [ 2.77, -1.02, 1.50]    | [-1.50,  0.14, -0.00]   |  1.51 |  0.45 | REROUTE  | [-0.50, 0.04, -0.00]
   500 | [ 2.71, -1.02, 1.50]    | [-1.50,  0.00, -0.00]   |  1.50 |  0.45 | REROUTE  | [-0.50, 0.00, -0.00]
  ```

### [Seed 4020] Configuration: Shield ON (Camera) — Outcome: `OBSTACLE_COLLISION`
- **Steps:** 165 | **Reward:** -587.37 | **Min Clearance:** 0.375 m
- **Diagnostic Cause:** Obstacle collision at speed 1.50 m/s (min clearance 0.45m).
- **Last 5 Control Steps Telemetry:**
  ```
  Step | Pos [x, y, z]           | Vel [vx, vy, vz]        | Speed | Clr   | State    | Action Executed
  -----+-------------------------+-------------------------+-------+-------+----------+----------------
   161 | [-1.77, -1.14, 1.50]    | [ 1.50,  0.11, 0.00]    |  1.50 |  0.45 | REROUTE  | [0.50, 0.04, 0.00]
   162 | [-1.70, -1.14, 1.50]    | [ 1.50,  0.11, 0.00]    |  1.50 |  0.45 | REROUTE  | [0.50, 0.04, 0.00]
   163 | [-1.64, -1.13, 1.50]    | [ 1.50,  0.11, 0.00]    |  1.50 |  0.45 | REROUTE  | [0.50, 0.04, 0.00]
   164 | [-1.58, -1.13, 1.50]    | [ 1.50,  0.11, 0.00]    |  1.50 |  0.45 | REROUTE  | [0.50, 0.04, 0.00]
   165 | [-1.52, -1.12, 1.50]    | [ 1.50,  0.11, 0.00]    |  1.50 |  0.45 | REROUTE  | [0.50, 0.04, 0.00]
  ```

### [Seed 4021] Configuration: Shield ON (Camera) — Outcome: `OBSTACLE_COLLISION`
- **Steps:** 112 | **Reward:** -321.45 | **Min Clearance:** 0.407 m
- **Diagnostic Cause:** Obstacle collision at speed 1.50 m/s (min clearance 0.41m).
- **Last 5 Control Steps Telemetry:**
  ```
  Step | Pos [x, y, z]           | Vel [vx, vy, vz]        | Speed | Clr   | State    | Action Executed
  -----+-------------------------+-------------------------+-------+-------+----------+----------------
   108 | [-1.75, -1.07, 1.50]    | [-1.50,  0.00, -0.01]   |  1.50 |  0.42 | REROUTE  | [-0.50, 0.00, -0.00]
   109 | [-1.82, -1.07, 1.50]    | [-1.50,  0.00, -0.01]   |  1.50 |  0.42 | REROUTE  | [-0.50, 0.00, -0.00]
   110 | [-1.88, -1.07, 1.50]    | [-1.50,  0.00, -0.00]   |  1.50 |  0.41 | REROUTE  | [-0.50, 0.00, -0.00]
   111 | [-1.94, -1.07, 1.50]    | [-1.50,  0.00, -0.00]   |  1.50 |  0.41 | REROUTE  | [-0.50, 0.00, -0.00]
   112 | [-2.00, -1.07, 1.50]    | [-1.50,  0.00, -0.00]   |  1.50 |  0.41 | REROUTE  | [-0.50, 0.00, -0.00]
  ```

### [Seed 4022] Configuration: Shield ON (Camera) — Outcome: `OBSTACLE_COLLISION`
- **Steps:** 72 | **Reward:** -95.68 | **Min Clearance:** 0.382 m
- **Diagnostic Cause:** Obstacle collision at speed 1.50 m/s (min clearance 0.38m).
- **Last 5 Control Steps Telemetry:**
  ```
  Step | Pos [x, y, z]           | Vel [vx, vy, vz]        | Speed | Clr   | State    | Action Executed
  -----+-------------------------+-------------------------+-------+-------+----------+----------------
    68 | [-0.33, -1.85, 1.50]    | [-1.50,  0.00, -0.01]   |  1.50 |  0.44 | REROUTE  | [-0.50, 0.00, -0.00]
    69 | [-0.39, -1.85, 1.50]    | [-1.50,  0.00, -0.01]   |  1.50 |  0.41 | REROUTE  | [-0.50, 0.00, -0.00]
    70 | [-0.46, -1.85, 1.50]    | [-1.50,  0.00, -0.01]   |  1.50 |  0.40 | REROUTE  | [-0.50, 0.00, -0.00]
    71 | [-0.52, -1.85, 1.50]    | [-1.50,  0.00, -0.01]   |  1.50 |  0.39 | REROUTE  | [-0.50, 0.00, -0.00]
    72 | [-0.58, -1.85, 1.50]    | [-1.50,  0.00, -0.01]   |  1.50 |  0.38 | REROUTE  | [-0.50, 0.00, -0.00]
  ```

### [Seed 4023] Configuration: Shield ON (Camera) — Outcome: `TIMEOUT`
- **Steps:** 500 | **Reward:** -2299.91 | **Min Clearance:** 0.371 m
- **Diagnostic Cause:** Exceeded maximum episode limit (500 steps) without reaching goal.
- **Last 5 Control Steps Telemetry:**
  ```
  Step | Pos [x, y, z]           | Vel [vx, vy, vz]        | Speed | Clr   | State    | Action Executed
  -----+-------------------------+-------------------------+-------+-------+----------+----------------
   496 | [ 1.91, -1.15, 1.50]    | [ 1.50,  0.40, -0.00]   |  1.55 |  0.57 | REROUTE  | [0.50, 0.13, -0.00]
   497 | [ 1.98, -1.14, 1.50]    | [ 1.50,  0.40, -0.00]   |  1.55 |  0.56 | REROUTE  | [0.50, 0.13, -0.00]
   498 | [ 2.04, -1.12, 1.50]    | [ 1.50,  0.40, -0.00]   |  1.55 |  0.55 | REROUTE  | [0.50, 0.13, -0.00]
   499 | [ 2.10, -1.10, 1.50]    | [ 1.50,  0.40, -0.00]   |  1.55 |  0.54 | REROUTE  | [0.50, 0.13, -0.00]
   500 | [ 2.16, -1.09, 1.50]    | [ 1.50,  0.40, -0.00]   |  1.55 |  0.53 | REROUTE  | [0.50, 0.13, -0.00]
  ```

### [Seed 4024] Configuration: Shield ON (Camera) — Outcome: `OBSTACLE_COLLISION`
- **Steps:** 28 | **Reward:** -0.04 | **Min Clearance:** 1.55 m
- **Diagnostic Cause:** Obstacle collision at speed 2.86 m/s (min clearance 1.55m).
- **Last 5 Control Steps Telemetry:**
  ```
  Step | Pos [x, y, z]           | Vel [vx, vy, vz]        | Speed | Clr   | State    | Action Executed
  -----+-------------------------+-------------------------+-------+-------+----------+----------------
    24 | [-0.11, -5.19, 1.50]    | [-1.17,  2.66, 0.05]    |  2.91 |  1.90 | NOMINAL  | [-0.39, 0.89, 0.02]
    25 | [-0.15, -5.07, 1.50]    | [-0.95,  2.73, 0.02]    |  2.89 |  1.83 | NOMINAL  | [-0.32, 0.91, 0.01]
    26 | [-0.15, -4.96, 1.50]    | [ 0.02,  2.76, 0.01]    |  2.76 |  1.76 | NOMINAL  | [0.01, 0.92, 0.00]
    27 | [-0.16, -4.84, 1.50]    | [-0.32,  2.81, -0.01]   |  2.83 |  1.65 | NOMINAL  | [-0.11, 0.94, -0.00]
    28 | [-0.18, -4.72, 1.50]    | [-0.50,  2.82, 0.00]    |  2.86 |  1.55 | NOMINAL  | [-0.17, 0.94, 0.00]
  ```

### [Seed 4025] Configuration: Shield ON (Camera) — Outcome: `OBSTACLE_COLLISION`
- **Steps:** 47 | **Reward:** 53.64 | **Min Clearance:** 0.557 m
- **Diagnostic Cause:** Obstacle collision at speed 2.87 m/s (min clearance 3.29m).
- **Last 5 Control Steps Telemetry:**
  ```
  Step | Pos [x, y, z]           | Vel [vx, vy, vz]        | Speed | Clr   | State    | Action Executed
  -----+-------------------------+-------------------------+-------+-------+----------+----------------
    43 | [ 0.32, -4.32, 1.49]    | [-0.02,  2.30, -0.01]   |  2.30 |  3.68 | NOMINAL  | [-0.01, 0.77, -0.00]
    44 | [ 0.30, -4.21, 1.49]    | [-0.30,  2.66, -0.02]   |  2.68 |  3.63 | NOMINAL  | [-0.10, 0.89, -0.01]
    45 | [ 0.29, -4.09, 1.49]    | [-0.23,  2.78, -0.00]   |  2.79 |  3.48 | NOMINAL  | [-0.08, 0.93, -0.00]
    46 | [ 0.29, -3.97, 1.49]    | [-0.14,  2.85, -0.01]   |  2.85 |  3.36 | NOMINAL  | [-0.05, 0.95, -0.01]
    47 | [ 0.28, -3.85, 1.49]    | [-0.22,  2.86, -0.03]   |  2.87 |  3.29 | NOMINAL  | [-0.07, 0.95, -0.01]
  ```

### [Seed 4026] Configuration: Shield ON (Camera) — Outcome: `OBSTACLE_COLLISION`
- **Steps:** 31 | **Reward:** 48.76 | **Min Clearance:** 3.786 m
- **Diagnostic Cause:** Obstacle collision at speed 2.96 m/s (min clearance 3.79m).
- **Last 5 Control Steps Telemetry:**
  ```
  Step | Pos [x, y, z]           | Vel [vx, vy, vz]        | Speed | Clr   | State    | Action Executed
  -----+-------------------------+-------------------------+-------+-------+----------+----------------
    27 | [ 0.57, -4.80, 1.51]    | [ 0.94,  2.79, -0.01]   |  2.95 |  4.24 | NOMINAL  | [0.31, 0.93, -0.00]
    28 | [ 0.62, -4.69, 1.51]    | [ 1.20,  2.75, 0.02]    |  3.00 |  4.12 | NOMINAL  | [0.40, 0.92, 0.01]
    29 | [ 0.67, -4.57, 1.51]    | [ 1.21,  2.75, 0.00]    |  3.00 |  4.01 | NOMINAL  | [0.40, 0.92, 0.00]
    30 | [ 0.71, -4.46, 1.51]    | [ 0.99,  2.75, 0.01]    |  2.92 |  3.90 | NOMINAL  | [0.33, 0.92, 0.00]
    31 | [ 0.75, -4.34, 1.51]    | [ 0.93,  2.81, 0.01]    |  2.96 |  3.79 | NOMINAL  | [0.31, 0.94, 0.00]
  ```

### [Seed 4027] Configuration: Shield ON (Camera) — Outcome: `TIMEOUT`
- **Steps:** 500 | **Reward:** -2510.86 | **Min Clearance:** 0.322 m
- **Diagnostic Cause:** Exceeded maximum episode limit (500 steps) without reaching goal.
- **Last 5 Control Steps Telemetry:**
  ```
  Step | Pos [x, y, z]           | Vel [vx, vy, vz]        | Speed | Clr   | State    | Action Executed
  -----+-------------------------+-------------------------+-------+-------+----------+----------------
   496 | [-3.65, -1.36, 1.50]    | [ 0.00, -0.80, -0.00]   |  0.80 |  0.58 | SCAN     | [0.00, -0.27, -0.00]
   497 | [-3.59, -1.35, 1.50]    | [ 1.50,  0.40, -0.00]   |  1.55 |  0.61 | REROUTE  | [0.50, 0.13, -0.00]
   498 | [-3.53, -1.33, 1.50]    | [ 1.50,  0.40, -0.00]   |  1.55 |  0.60 | REROUTE  | [0.50, 0.13, -0.00]
   499 | [-3.46, -1.31, 1.50]    | [ 1.50,  0.40, -0.00]   |  1.55 |  0.58 | REROUTE  | [0.50, 0.13, -0.00]
   500 | [-3.40, -1.30, 1.50]    | [ 1.50,  0.40, -0.00]   |  1.55 |  0.57 | REROUTE  | [0.50, 0.13, -0.00]
  ```

### [Seed 4028] Configuration: Shield ON (Camera) — Outcome: `OBSTACLE_COLLISION`
- **Steps:** 131 | **Reward:** -522.34 | **Min Clearance:** 0.121 m
- **Diagnostic Cause:** Obstacle collision at speed 1.46 m/s (min clearance 0.79m).
- **Last 5 Control Steps Telemetry:**
  ```
  Step | Pos [x, y, z]           | Vel [vx, vy, vz]        | Speed | Clr   | State    | Action Executed
  -----+-------------------------+-------------------------+-------+-------+----------+----------------
   127 | [ 0.08, -1.57, 1.50]    | [ 0.68,  1.32, -0.03]   |  1.49 |  0.96 | NOMINAL  | [0.23, 0.44, -0.01]
   128 | [ 0.04, -1.52, 1.50]    | [-0.87,  1.10, 0.04]    |  1.40 |  0.91 | NOMINAL  | [-0.29, 0.37, 0.01]
   129 | [-0.01, -1.48, 1.50]    | [-1.23,  1.14, -0.03]   |  1.67 |  0.86 | NOMINAL  | [-0.41, 0.38, -0.01]
   130 | [-0.07, -1.45, 1.50]    | [-1.39,  0.66, -0.01]   |  1.54 |  0.81 | NOMINAL  | [-0.46, 0.22, -0.00]
   131 | [-0.11, -1.41, 1.50]    | [-1.14,  0.92, -0.02]   |  1.46 |  0.79 | NOMINAL  | [-0.38, 0.31, -0.01]
  ```

### [Seed 4029] Configuration: Shield ON (Camera) — Outcome: `TIMEOUT`
- **Steps:** 500 | **Reward:** -2543.37 | **Min Clearance:** 0.329 m
- **Diagnostic Cause:** Exceeded maximum episode limit (500 steps) without reaching goal.
- **Last 5 Control Steps Telemetry:**
  ```
  Step | Pos [x, y, z]           | Vel [vx, vy, vz]        | Speed | Clr   | State    | Action Executed
  -----+-------------------------+-------------------------+-------+-------+----------+----------------
   496 | [-3.66, -1.35, 1.50]    | [ 0.00, -0.80, -0.00]   |  0.80 |  0.58 | SCAN     | [0.00, -0.27, -0.00]
   497 | [-3.60, -1.33, 1.50]    | [ 1.50,  0.40, -0.00]   |  1.55 |  0.62 | REROUTE  | [0.50, 0.13, -0.00]
   498 | [-3.54, -1.31, 1.50]    | [ 1.50,  0.40, -0.00]   |  1.55 |  0.60 | REROUTE  | [0.50, 0.13, -0.00]
   499 | [-3.48, -1.30, 1.50]    | [ 1.50,  0.40, -0.00]   |  1.55 |  0.59 | REROUTE  | [0.50, 0.13, -0.00]
   500 | [-3.41, -1.28, 1.50]    | [ 1.50,  0.40, -0.00]   |  1.55 |  0.58 | REROUTE  | [0.50, 0.13, -0.00]
  ```

### [Seed 4030] Configuration: Shield ON (Camera) — Outcome: `OBSTACLE_COLLISION`
- **Steps:** 72 | **Reward:** -40.28 | **Min Clearance:** 0.555 m
- **Diagnostic Cause:** Obstacle collision at speed 1.91 m/s (min clearance 1.10m).
- **Last 5 Control Steps Telemetry:**
  ```
  Step | Pos [x, y, z]           | Vel [vx, vy, vz]        | Speed | Clr   | State    | Action Executed
  -----+-------------------------+-------------------------+-------+-------+----------+----------------
    68 | [ 0.99, -1.93, 1.50]    | [ 2.00,  1.60, 0.02]    |  2.56 |  1.35 | NOMINAL  | [0.67, 0.53, 0.01]
    69 | [ 0.91, -1.85, 1.50]    | [-1.79,  1.85, -0.00]   |  2.57 |  1.28 | NOMINAL  | [-0.60, 0.62, -0.00]
    70 | [ 1.00, -1.81, 1.50]    | [ 2.16,  1.13, 0.01]    |  2.44 |  1.21 | NOMINAL  | [0.72, 0.38, 0.00]
    71 | [ 0.94, -1.74, 1.50]    | [-1.52,  1.52, 0.03]    |  2.15 |  1.17 | NOMINAL  | [-0.51, 0.51, 0.01]
    72 | [ 0.99, -1.68, 1.50]    | [ 1.28,  1.42, -0.02]   |  1.91 |  1.10 | NOMINAL  | [0.43, 0.47, -0.01]
  ```

### [Seed 4031] Configuration: Shield ON (Camera) — Outcome: `TIMEOUT`
- **Steps:** 500 | **Reward:** -2377.45 | **Min Clearance:** 0.348 m
- **Diagnostic Cause:** Exceeded maximum episode limit (500 steps) without reaching goal.
- **Last 5 Control Steps Telemetry:**
  ```
  Step | Pos [x, y, z]           | Vel [vx, vy, vz]        | Speed | Clr   | State    | Action Executed
  -----+-------------------------+-------------------------+-------+-------+----------+----------------
   496 | [ 3.23, -0.97, 1.50]    | [ 1.50,  0.00, -0.00]   |  1.50 |  0.44 | REROUTE  | [0.50, 0.00, -0.00]
   497 | [ 3.29, -0.97, 1.50]    | [ 1.50,  0.00, -0.00]   |  1.50 |  0.43 | REROUTE  | [0.50, 0.00, -0.00]
   498 | [ 3.35, -0.97, 1.50]    | [ 1.50,  0.00, -0.00]   |  1.50 |  0.43 | REROUTE  | [0.50, 0.00, -0.00]
   499 | [ 3.41, -0.97, 1.50]    | [ 1.50,  0.00, -0.00]   |  1.50 |  0.43 | REROUTE  | [0.50, 0.00, -0.00]
   500 | [ 3.48, -0.97, 1.50]    | [ 1.50,  0.00, -0.00]   |  1.50 |  0.43 | REROUTE  | [0.50, 0.00, -0.00]
  ```

### [Seed 4032] Configuration: Shield ON (Camera) — Outcome: `TIMEOUT`
- **Steps:** 500 | **Reward:** -2457.68 | **Min Clearance:** 0.355 m
- **Diagnostic Cause:** Exceeded maximum episode limit (500 steps) without reaching goal.
- **Last 5 Control Steps Telemetry:**
  ```
  Step | Pos [x, y, z]           | Vel [vx, vy, vz]        | Speed | Clr   | State    | Action Executed
  -----+-------------------------+-------------------------+-------+-------+----------+----------------
   496 | [-3.17, -1.32, 1.50]    | [ 0.00, -0.80, -0.00]   |  0.80 |  0.59 | SCAN     | [0.00, -0.27, -0.00]
   497 | [-3.13, -1.30, 1.50]    | [ 1.03,  0.40, -0.00]   |  1.11 |  0.62 | REROUTE  | [0.34, 0.13, -0.00]
   498 | [-3.07, -1.29, 1.50]    | [ 1.50,  0.40, -0.00]   |  1.55 |  0.61 | REROUTE  | [0.50, 0.13, -0.00]
   499 | [-3.01, -1.27, 1.50]    | [ 1.50,  0.40, -0.00]   |  1.55 |  0.60 | REROUTE  | [0.50, 0.13, -0.00]
   500 | [-2.94, -1.25, 1.50]    | [ 1.50,  0.40, -0.00]   |  1.55 |  0.58 | REROUTE  | [0.50, 0.13, -0.00]
  ```

### [Seed 4033] Configuration: Shield ON (Camera) — Outcome: `TIMEOUT`
- **Steps:** 500 | **Reward:** -2412.96 | **Min Clearance:** 0.33 m
- **Diagnostic Cause:** Exceeded maximum episode limit (500 steps) without reaching goal.
- **Last 5 Control Steps Telemetry:**
  ```
  Step | Pos [x, y, z]           | Vel [vx, vy, vz]        | Speed | Clr   | State    | Action Executed
  -----+-------------------------+-------------------------+-------+-------+----------+----------------
   496 | [-3.28, -1.31, 1.50]    | [ 1.50,  0.40, -0.00]   |  1.55 |  0.60 | REROUTE  | [0.50, 0.13, -0.00]
   497 | [-3.22, -1.30, 1.50]    | [ 1.50,  0.40, -0.00]   |  1.55 |  0.59 | REROUTE  | [0.50, 0.13, -0.00]
   498 | [-3.16, -1.28, 1.50]    | [ 1.50,  0.40, -0.00]   |  1.55 |  0.58 | REROUTE  | [0.50, 0.13, -0.00]
   499 | [-3.09, -1.26, 1.50]    | [ 1.50,  0.40, -0.00]   |  1.55 |  0.56 | REROUTE  | [0.50, 0.13, -0.00]
   500 | [-3.03, -1.25, 1.50]    | [ 1.50,  0.40, -0.00]   |  1.55 |  0.55 | REROUTE  | [0.50, 0.13, -0.00]
  ```

### [Seed 4034] Configuration: Shield ON (Camera) — Outcome: `TIMEOUT`
- **Steps:** 500 | **Reward:** -2450.08 | **Min Clearance:** 0.341 m
- **Diagnostic Cause:** Exceeded maximum episode limit (500 steps) without reaching goal.
- **Last 5 Control Steps Telemetry:**
  ```
  Step | Pos [x, y, z]           | Vel [vx, vy, vz]        | Speed | Clr   | State    | Action Executed
  -----+-------------------------+-------------------------+-------+-------+----------+----------------
   496 | [-3.10, -1.34, 1.50]    | [ 0.00, -0.80, -0.00]   |  0.80 |  0.58 | SCAN     | [0.00, -0.27, -0.00]
   497 | [-3.05, -1.32, 1.50]    | [ 1.03,  0.40, -0.00]   |  1.10 |  0.62 | REROUTE  | [0.34, 0.13, -0.00]
   498 | [-2.99, -1.31, 1.50]    | [ 1.50,  0.40, -0.00]   |  1.55 |  0.60 | REROUTE  | [0.50, 0.13, -0.00]
   499 | [-2.93, -1.29, 1.50]    | [ 1.50,  0.40, -0.00]   |  1.55 |  0.59 | REROUTE  | [0.50, 0.13, -0.00]
   500 | [-2.87, -1.27, 1.50]    | [ 1.50,  0.40, -0.00]   |  1.55 |  0.58 | REROUTE  | [0.50, 0.13, -0.00]
  ```

### [Seed 4035] Configuration: Shield ON (Camera) — Outcome: `OBSTACLE_COLLISION`
- **Steps:** 91 | **Reward:** -175.36 | **Min Clearance:** 0.044 m
- **Diagnostic Cause:** Obstacle collision at speed 1.50 m/s (min clearance 0.04m).
- **Last 5 Control Steps Telemetry:**
  ```
  Step | Pos [x, y, z]           | Vel [vx, vy, vz]        | Speed | Clr   | State    | Action Executed
  -----+-------------------------+-------------------------+-------+-------+----------+----------------
    87 | [ 0.66, -1.08, 1.50]    | [ 1.50,  0.00, -0.01]   |  1.50 |  0.44 | REROUTE  | [0.50, 0.00, -0.00]
    88 | [ 0.72, -1.08, 1.50]    | [ 1.50,  0.00, -0.01]   |  1.50 |  0.44 | REROUTE  | [0.50, 0.00, -0.00]
    89 | [ 0.78, -1.08, 1.50]    | [ 1.50,  0.00, -0.01]   |  1.50 |  0.44 | REROUTE  | [0.50, 0.00, -0.00]
    90 | [ 0.84, -1.08, 1.50]    | [ 1.50,  0.00, -0.01]   |  1.50 |  0.13 | REROUTE  | [0.50, 0.00, -0.00]
    91 | [ 0.91, -1.08, 1.50]    | [ 1.50,  0.00, -0.01]   |  1.50 |  0.04 | REROUTE  | [0.50, 0.00, -0.00]
  ```

### [Seed 4036] Configuration: Shield ON (Camera) — Outcome: `TIMEOUT`
- **Steps:** 500 | **Reward:** -2471.61 | **Min Clearance:** 0.364 m
- **Diagnostic Cause:** Exceeded maximum episode limit (500 steps) without reaching goal.
- **Last 5 Control Steps Telemetry:**
  ```
  Step | Pos [x, y, z]           | Vel [vx, vy, vz]        | Speed | Clr   | State    | Action Executed
  -----+-------------------------+-------------------------+-------+-------+----------+----------------
   496 | [ 3.25, -1.01, 1.50]    | [ 1.50,  0.00, -0.00]   |  1.50 |  0.41 | REROUTE  | [0.50, 0.00, -0.00]
   497 | [ 3.31, -1.01, 1.50]    | [ 1.50,  0.00, -0.00]   |  1.50 |  0.41 | REROUTE  | [0.50, 0.00, -0.00]
   498 | [ 3.31, -1.04, 1.50]    | [ 0.00, -0.80, -0.00]   |  0.80 |  0.40 | RETREAT  | [0.00, -0.27, -0.00]
   499 | [ 3.31, -1.07, 1.50]    | [ 0.00, -0.80, -0.00]   |  0.80 |  0.43 | RETREAT  | [0.00, -0.27, -0.00]
   500 | [ 3.31, -1.11, 1.50]    | [ 0.00, -0.80, -0.00]   |  0.80 |  0.47 | RETREAT  | [0.00, -0.27, -0.00]
  ```

### [Seed 4037] Configuration: Shield ON (Camera) — Outcome: `TIMEOUT`
- **Steps:** 500 | **Reward:** -2484.45 | **Min Clearance:** 0.338 m
- **Diagnostic Cause:** Exceeded maximum episode limit (500 steps) without reaching goal.
- **Last 5 Control Steps Telemetry:**
  ```
  Step | Pos [x, y, z]           | Vel [vx, vy, vz]        | Speed | Clr   | State    | Action Executed
  -----+-------------------------+-------------------------+-------+-------+----------+----------------
   496 | [-2.81, -1.30, 1.50]    | [ 1.50,  0.40, 0.00]    |  1.55 |  0.59 | REROUTE  | [0.50, 0.13, 0.00]
   497 | [-2.75, -1.28, 1.50]    | [ 1.50,  0.40, 0.00]    |  1.55 |  0.57 | REROUTE  | [0.50, 0.13, 0.00]
   498 | [-2.69, -1.27, 1.50]    | [ 1.50,  0.40, 0.00]    |  1.55 |  0.56 | REROUTE  | [0.50, 0.13, 0.00]
   499 | [-2.62, -1.25, 1.50]    | [ 1.50,  0.40, 0.00]    |  1.55 |  0.55 | REROUTE  | [0.50, 0.13, 0.00]
   500 | [-2.56, -1.23, 1.50]    | [ 1.50,  0.40, 0.00]    |  1.55 |  0.54 | REROUTE  | [0.50, 0.13, 0.00]
  ```

### [Seed 4038] Configuration: Shield ON (Camera) — Outcome: `OBSTACLE_COLLISION`
- **Steps:** 53 | **Reward:** -8.59 | **Min Clearance:** 0.536 m
- **Diagnostic Cause:** Obstacle collision at speed 2.85 m/s (min clearance 3.70m).
- **Last 5 Control Steps Telemetry:**
  ```
  Step | Pos [x, y, z]           | Vel [vx, vy, vz]        | Speed | Clr   | State    | Action Executed
  -----+-------------------------+-------------------------+-------+-------+----------+----------------
    49 | [ 0.70, -4.68, 1.50]    | [ 1.50,  1.60, 0.00]    |  2.19 |  4.07 | REROUTE  | [0.50, 0.53, 0.00]
    50 | [ 0.71, -4.59, 1.50]    | [ 0.08,  2.17, -0.01]   |  2.17 |  4.01 | NOMINAL  | [0.03, 0.72, -0.00]
    51 | [ 0.71, -4.49, 1.50]    | [ 0.12,  2.51, -0.02]   |  2.52 |  3.92 | NOMINAL  | [0.04, 0.84, -0.01]
    52 | [ 0.70, -4.38, 1.50]    | [-0.32,  2.69, -0.01]   |  2.71 |  3.81 | NOMINAL  | [-0.10, 0.90, -0.00]
    53 | [ 0.69, -4.26, 1.50]    | [-0.15,  2.84, -0.02]   |  2.85 |  3.70 | NOMINAL  | [-0.05, 0.95, -0.01]
  ```

### [Seed 4039] Configuration: Shield ON (Camera) — Outcome: `TIMEOUT`
- **Steps:** 500 | **Reward:** -2224.18 | **Min Clearance:** 0.344 m
- **Diagnostic Cause:** Exceeded maximum episode limit (500 steps) without reaching goal.
- **Last 5 Control Steps Telemetry:**
  ```
  Step | Pos [x, y, z]           | Vel [vx, vy, vz]        | Speed | Clr   | State    | Action Executed
  -----+-------------------------+-------------------------+-------+-------+----------+----------------
   496 | [-1.73, -1.26, 1.50]    | [-1.50,  0.40, -0.00]   |  1.55 |  0.63 | REROUTE  | [-0.50, 0.13, -0.00]
   497 | [-1.79, -1.24, 1.50]    | [-1.50,  0.40, -0.00]   |  1.55 |  0.61 | REROUTE  | [-0.50, 0.13, -0.00]
   498 | [-1.85, -1.22, 1.50]    | [-1.50,  0.40, -0.00]   |  1.55 |  0.59 | REROUTE  | [-0.50, 0.13, -0.00]
   499 | [-1.91, -1.21, 1.50]    | [-1.50,  0.40, -0.00]   |  1.55 |  0.57 | REROUTE  | [-0.50, 0.13, -0.00]
   500 | [-1.98, -1.19, 1.50]    | [-1.50,  0.40, -0.00]   |  1.55 |  0.55 | REROUTE  | [-0.50, 0.13, -0.00]
  ```

### [Seed 4040] Configuration: Shield ON (Camera) — Outcome: `TIMEOUT`
- **Steps:** 500 | **Reward:** -2377.17 | **Min Clearance:** 0.324 m
- **Diagnostic Cause:** Exceeded maximum episode limit (500 steps) without reaching goal.
- **Last 5 Control Steps Telemetry:**
  ```
  Step | Pos [x, y, z]           | Vel [vx, vy, vz]        | Speed | Clr   | State    | Action Executed
  -----+-------------------------+-------------------------+-------+-------+----------+----------------
   496 | [-3.53, -1.30, 1.50]    | [ 0.00, -0.80, -0.00]   |  0.80 |  0.52 | RETREAT  | [0.00, -0.27, -0.00]
   497 | [-3.53, -1.33, 1.50]    | [ 0.00, -0.80, -0.00]   |  0.80 |  0.55 | RETREAT  | [0.00, -0.27, -0.00]
   498 | [-3.53, -1.36, 1.50]    | [ 0.00, -0.80, -0.00]   |  0.80 |  0.58 | SCAN     | [0.00, -0.27, -0.00]
   499 | [-3.47, -1.35, 1.50]    | [ 1.50,  0.40, -0.00]   |  1.55 |  0.61 | REROUTE  | [0.50, 0.13, -0.00]
   500 | [-3.41, -1.33, 1.50]    | [ 1.50,  0.40, -0.00]   |  1.55 |  0.60 | REROUTE  | [0.50, 0.13, -0.00]
  ```

### [Seed 4041] Configuration: Shield ON (Camera) — Outcome: `TIMEOUT`
- **Steps:** 500 | **Reward:** -2510.57 | **Min Clearance:** 0.359 m
- **Diagnostic Cause:** Exceeded maximum episode limit (500 steps) without reaching goal.
- **Last 5 Control Steps Telemetry:**
  ```
  Step | Pos [x, y, z]           | Vel [vx, vy, vz]        | Speed | Clr   | State    | Action Executed
  -----+-------------------------+-------------------------+-------+-------+----------+----------------
   496 | [ 3.15, -1.00, 1.50]    | [ 1.50,  0.00, -0.00]   |  1.50 |  0.42 | REROUTE  | [0.50, 0.00, -0.00]
   497 | [ 3.21, -1.00, 1.50]    | [ 1.50,  0.00, -0.00]   |  1.50 |  0.42 | REROUTE  | [0.50, 0.00, -0.00]
   498 | [ 3.27, -1.00, 1.50]    | [ 1.50,  0.00, -0.00]   |  1.50 |  0.41 | REROUTE  | [0.50, 0.00, -0.00]
   499 | [ 3.27, -1.03, 1.50]    | [ 0.00, -0.80, -0.00]   |  0.80 |  0.41 | RETREAT  | [0.00, -0.27, -0.00]
   500 | [ 3.27, -1.07, 1.50]    | [ 0.00, -0.80, -0.00]   |  0.80 |  0.44 | RETREAT  | [0.00, -0.27, -0.00]
  ```

### [Seed 4042] Configuration: Shield ON (Camera) — Outcome: `TIMEOUT`
- **Steps:** 500 | **Reward:** -2796.4 | **Min Clearance:** 0.33 m
- **Diagnostic Cause:** Exceeded maximum episode limit (500 steps) without reaching goal.
- **Last 5 Control Steps Telemetry:**
  ```
  Step | Pos [x, y, z]           | Vel [vx, vy, vz]        | Speed | Clr   | State    | Action Executed
  -----+-------------------------+-------------------------+-------+-------+----------+----------------
   496 | [ 2.97, -0.98, 1.50]    | [-1.50,  0.40, -0.00]   |  1.55 |  0.49 | REROUTE  | [-0.50, 0.13, -0.00]
   497 | [ 2.90, -0.96, 1.50]    | [-1.50,  0.40, -0.00]   |  1.55 |  0.47 | REROUTE  | [-0.50, 0.13, -0.00]
   498 | [ 2.84, -0.96, 1.50]    | [-1.50,  0.09, -0.00]   |  1.50 |  0.45 | REROUTE  | [-0.50, 0.03, -0.00]
   499 | [ 2.78, -0.96, 1.50]    | [-1.50,  0.00, -0.00]   |  1.50 |  0.44 | REROUTE  | [-0.50, 0.00, -0.00]
   500 | [ 2.72, -0.96, 1.50]    | [-1.50,  0.00, -0.00]   |  1.50 |  0.44 | REROUTE  | [-0.50, 0.00, -0.00]
  ```

### [Seed 4043] Configuration: Shield ON (Camera) — Outcome: `OBSTACLE_COLLISION`
- **Steps:** 129 | **Reward:** -439.66 | **Min Clearance:** 0.439 m
- **Diagnostic Cause:** Obstacle collision at speed 1.55 m/s (min clearance 0.57m).
- **Last 5 Control Steps Telemetry:**
  ```
  Step | Pos [x, y, z]           | Vel [vx, vy, vz]        | Speed | Clr   | State    | Action Executed
  -----+-------------------------+-------------------------+-------+-------+----------+----------------
   125 | [ 2.34, -1.19, 1.50]    | [ 1.50,  0.40, -0.00]   |  1.55 |  0.64 | REROUTE  | [0.50, 0.13, -0.00]
   126 | [ 2.40, -1.17, 1.50]    | [ 1.50,  0.40, -0.00]   |  1.55 |  0.63 | REROUTE  | [0.50, 0.13, -0.00]
   127 | [ 2.47, -1.16, 1.50]    | [ 1.50,  0.40, -0.00]   |  1.55 |  0.61 | REROUTE  | [0.50, 0.13, -0.00]
   128 | [ 2.53, -1.14, 1.50]    | [ 1.50,  0.40, -0.00]   |  1.55 |  0.59 | REROUTE  | [0.50, 0.13, -0.00]
   129 | [ 2.59, -1.12, 1.50]    | [ 1.50,  0.40, -0.00]   |  1.55 |  0.57 | REROUTE  | [0.50, 0.13, -0.00]
  ```

### [Seed 4044] Configuration: Shield ON (Camera) — Outcome: `OBSTACLE_COLLISION`
- **Steps:** 97 | **Reward:** -288.49 | **Min Clearance:** 0.135 m
- **Diagnostic Cause:** Obstacle collision at speed 1.50 m/s (min clearance 0.14m).
- **Last 5 Control Steps Telemetry:**
  ```
  Step | Pos [x, y, z]           | Vel [vx, vy, vz]        | Speed | Clr   | State    | Action Executed
  -----+-------------------------+-------------------------+-------+-------+----------+----------------
    93 | [ 1.82, -1.08, 1.51]    | [ 1.50,  0.40, -0.01]   |  1.55 |  0.50 | REROUTE  | [0.50, 0.13, -0.01]
    94 | [ 1.88, -1.07, 1.51]    | [ 1.50,  0.40, -0.01]   |  1.55 |  0.48 | REROUTE  | [0.50, 0.13, -0.00]
    95 | [ 1.94, -1.07, 1.51]    | [ 1.50,  0.00, -0.01]   |  1.50 |  0.37 | REROUTE  | [0.50, 0.00, -0.00]
    96 | [ 2.00, -1.07, 1.50]    | [ 1.50,  0.00, -0.01]   |  1.50 |  0.22 | REROUTE  | [0.50, 0.00, -0.00]
    97 | [ 2.07, -1.07, 1.50]    | [ 1.50,  0.00, -0.01]   |  1.50 |  0.14 | REROUTE  | [0.50, 0.00, -0.00]
  ```

### [Seed 4045] Configuration: Shield ON (Camera) — Outcome: `OBSTACLE_COLLISION`
- **Steps:** 34 | **Reward:** 56.13 | **Min Clearance:** 1.149 m
- **Diagnostic Cause:** Obstacle collision at speed 2.84 m/s (min clearance 3.45m).
- **Last 5 Control Steps Telemetry:**
  ```
  Step | Pos [x, y, z]           | Vel [vx, vy, vz]        | Speed | Clr   | State    | Action Executed
  -----+-------------------------+-------------------------+-------+-------+----------+----------------
    30 | [-0.21, -4.48, 1.49]    | [ 0.03,  2.82, -0.02]   |  2.82 |  3.91 | NOMINAL  | [0.01, 0.94, -0.01]
    31 | [-0.19, -4.36, 1.50]    | [ 0.45,  2.83, 0.02]    |  2.86 |  3.80 | NOMINAL  | [0.15, 0.94, 0.01]
    32 | [-0.20, -4.24, 1.49]    | [-0.23,  2.86, -0.03]   |  2.87 |  3.68 | NOMINAL  | [-0.07, 0.95, -0.01]
    33 | [-0.21, -4.12, 1.49]    | [-0.23,  2.86, -0.03]   |  2.87 |  3.56 | NOMINAL  | [-0.07, 0.95, -0.01]
    34 | [-0.22, -4.00, 1.49]    | [-0.24,  2.83, -0.01]   |  2.84 |  3.45 | NOMINAL  | [-0.08, 0.94, -0.00]
  ```

### [Seed 4046] Configuration: Shield ON (Camera) — Outcome: `OBSTACLE_COLLISION`
- **Steps:** 366 | **Reward:** -1821.98 | **Min Clearance:** 0.327 m
- **Diagnostic Cause:** Obstacle collision at speed 1.50 m/s (min clearance 0.42m).
- **Last 5 Control Steps Telemetry:**
  ```
  Step | Pos [x, y, z]           | Vel [vx, vy, vz]        | Speed | Clr   | State    | Action Executed
  -----+-------------------------+-------------------------+-------+-------+----------+----------------
   362 | [-0.89, -1.07, 1.50]    | [ 1.50,  0.00, 0.00]    |  1.50 |  0.43 | REROUTE  | [0.50, 0.00, 0.00]
   363 | [-0.83, -1.07, 1.50]    | [ 1.50,  0.00, 0.00]    |  1.50 |  0.43 | REROUTE  | [0.50, 0.00, 0.00]
   364 | [-0.77, -1.07, 1.50]    | [ 1.50,  0.00, 0.00]    |  1.50 |  0.42 | REROUTE  | [0.50, 0.00, 0.00]
   365 | [-0.70, -1.07, 1.50]    | [ 1.50,  0.00, 0.00]    |  1.50 |  0.42 | REROUTE  | [0.50, 0.00, 0.00]
   366 | [-0.64, -1.07, 1.50]    | [ 1.50,  0.00, 0.00]    |  1.50 |  0.42 | REROUTE  | [0.50, 0.00, 0.00]
  ```

### [Seed 4047] Configuration: Shield ON (Camera) — Outcome: `OBSTACLE_COLLISION`
- **Steps:** 79 | **Reward:** -136.83 | **Min Clearance:** 0.449 m
- **Diagnostic Cause:** Obstacle collision at speed 1.50 m/s (min clearance 0.45m).
- **Last 5 Control Steps Telemetry:**
  ```
  Step | Pos [x, y, z]           | Vel [vx, vy, vz]        | Speed | Clr   | State    | Action Executed
  -----+-------------------------+-------------------------+-------+-------+----------+----------------
    75 | [ 0.61, -1.14, 1.49]    | [ 1.50,  0.40, 0.02]    |  1.55 |  0.52 | REROUTE  | [0.50, 0.13, 0.01]
    76 | [ 0.67, -1.13, 1.49]    | [ 1.50,  0.40, 0.02]    |  1.55 |  0.50 | REROUTE  | [0.50, 0.13, 0.01]
    77 | [ 0.73, -1.11, 1.49]    | [ 1.50,  0.40, 0.02]    |  1.55 |  0.48 | REROUTE  | [0.50, 0.13, 0.01]
    78 | [ 0.80, -1.10, 1.49]    | [ 1.50,  0.31, 0.02]    |  1.53 |  0.46 | REROUTE  | [0.50, 0.10, 0.01]
    79 | [ 0.86, -1.10, 1.49]    | [ 1.50,  0.00, 0.01]    |  1.50 |  0.45 | REROUTE  | [0.50, 0.00, 0.01]
  ```

### [Seed 4048] Configuration: Shield ON (Camera) — Outcome: `OBSTACLE_COLLISION`
- **Steps:** 63 | **Reward:** 17.53 | **Min Clearance:** 0.388 m
- **Diagnostic Cause:** Obstacle collision at speed 1.55 m/s (min clearance 0.53m).
- **Last 5 Control Steps Telemetry:**
  ```
  Step | Pos [x, y, z]           | Vel [vx, vy, vz]        | Speed | Clr   | State    | Action Executed
  -----+-------------------------+-------------------------+-------+-------+----------+----------------
    59 | [ 0.09, -3.33, 1.48]    | [ 0.05,  0.17, -0.03]   |  0.18 |  0.55 | NOMINAL  | [0.02, 0.06, -0.01]
    60 | [ 0.09, -3.33, 1.48]    | [ 0.00,  0.00, 0.00]    |  0.00 |  0.55 | BRAKE    | [0.00, 0.00, 0.00]
    61 | [ 0.09, -3.33, 1.48]    | [ 0.00,  0.00, 0.00]    |  0.00 |  0.55 | SCAN     | [0.00, 0.00, 0.00]
    62 | [ 0.15, -3.31, 1.48]    | [ 1.50,  0.40, 0.04]    |  1.55 |  0.55 | REROUTE  | [0.50, 0.13, 0.01]
    63 | [ 0.21, -3.29, 1.49]    | [ 1.50,  0.40, 0.03]    |  1.55 |  0.53 | REROUTE  | [0.50, 0.13, 0.01]
  ```

### [Seed 4049] Configuration: Shield ON (Camera) — Outcome: `OBSTACLE_COLLISION`
- **Steps:** 37 | **Reward:** 71.64 | **Min Clearance:** 1.442 m
- **Diagnostic Cause:** Obstacle collision at speed 3.00 m/s (min clearance 2.48m).
- **Last 5 Control Steps Telemetry:**
  ```
  Step | Pos [x, y, z]           | Vel [vx, vy, vz]        | Speed | Clr   | State    | Action Executed
  -----+-------------------------+-------------------------+-------+-------+----------+----------------
    33 | [-0.41, -4.14, 1.50]    | [-1.11,  2.79, 0.01]    |  3.00 |  2.94 | NOMINAL  | [-0.37, 0.93, 0.00]
    34 | [-0.39, -4.03, 1.49]    | [ 0.50,  2.76, -0.12]   |  2.80 |  2.83 | NOMINAL  | [0.17, 0.92, -0.04]
    35 | [-0.37, -3.91, 1.49]    | [ 0.56,  2.85, 0.00]    |  2.90 |  2.71 | NOMINAL  | [0.19, 0.95, 0.00]
    36 | [-0.32, -3.79, 1.49]    | [ 1.10,  2.79, 0.02]    |  3.00 |  2.60 | NOMINAL  | [0.37, 0.93, 0.01]
    37 | [-0.26, -3.69, 1.50]    | [ 1.55,  2.57, 0.01]    |  3.00 |  2.48 | NOMINAL  | [0.52, 0.86, 0.00]
  ```

### [Seed 4050] Configuration: Shield ON (Camera) — Outcome: `TIMEOUT`
- **Steps:** 500 | **Reward:** -2298.05 | **Min Clearance:** 0.329 m
- **Diagnostic Cause:** Exceeded maximum episode limit (500 steps) without reaching goal.
- **Last 5 Control Steps Telemetry:**
  ```
  Step | Pos [x, y, z]           | Vel [vx, vy, vz]        | Speed | Clr   | State    | Action Executed
  -----+-------------------------+-------------------------+-------+-------+----------+----------------
   496 | [-3.80, -1.19, 1.50]    | [ 0.00, -0.80, -0.00]   |  0.80 |  0.42 | RETREAT  | [0.00, -0.27, -0.00]
   497 | [-3.80, -1.22, 1.50]    | [ 0.00, -0.80, -0.00]   |  0.80 |  0.45 | RETREAT  | [0.00, -0.27, -0.00]
   498 | [-3.80, -1.25, 1.50]    | [ 0.00, -0.80, -0.00]   |  0.80 |  0.48 | RETREAT  | [0.00, -0.27, -0.00]
   499 | [-3.80, -1.29, 1.50]    | [ 0.00, -0.80, -0.00]   |  0.80 |  0.52 | RETREAT  | [0.00, -0.27, -0.00]
   500 | [-3.80, -1.32, 1.50]    | [ 0.00, -0.80, -0.00]   |  0.80 |  0.55 | RETREAT  | [0.00, -0.27, -0.00]
  ```

### [Seed 4051] Configuration: Shield ON (Camera) — Outcome: `TIMEOUT`
- **Steps:** 500 | **Reward:** -2721.27 | **Min Clearance:** 0.131 m
- **Diagnostic Cause:** Exceeded maximum episode limit (500 steps) without reaching goal.
- **Last 5 Control Steps Telemetry:**
  ```
  Step | Pos [x, y, z]           | Vel [vx, vy, vz]        | Speed | Clr   | State    | Action Executed
  -----+-------------------------+-------------------------+-------+-------+----------+----------------
   496 | [-3.27, -1.22, 1.50]    | [-1.50,  0.00, -0.00]   |  1.50 |  0.41 | REROUTE  | [-0.50, 0.00, -0.00]
   497 | [-3.33, -1.22, 1.50]    | [-1.50,  0.00, -0.00]   |  1.50 |  0.40 | REROUTE  | [-0.50, 0.00, -0.00]
   498 | [-3.40, -1.22, 1.50]    | [-1.50,  0.00, -0.00]   |  1.50 |  0.40 | REROUTE  | [-0.50, 0.00, -0.00]
   499 | [-3.46, -1.22, 1.50]    | [-1.50,  0.00, -0.00]   |  1.50 |  0.39 | REROUTE  | [-0.50, 0.00, -0.00]
   500 | [-3.52, -1.22, 1.50]    | [-1.50,  0.00, -0.00]   |  1.50 |  0.39 | REROUTE  | [-0.50, 0.00, -0.00]
  ```

### [Seed 4052] Configuration: Shield ON (Camera) — Outcome: `TIMEOUT`
- **Steps:** 500 | **Reward:** -2861.95 | **Min Clearance:** 0.175 m
- **Diagnostic Cause:** Exceeded maximum episode limit (500 steps) without reaching goal.
- **Last 5 Control Steps Telemetry:**
  ```
  Step | Pos [x, y, z]           | Vel [vx, vy, vz]        | Speed | Clr   | State    | Action Executed
  -----+-------------------------+-------------------------+-------+-------+----------+----------------
   496 | [ 3.83, -1.24, 1.50]    | [ 0.00, -0.80, -0.00]   |  0.80 |  0.50 | SCAN     | [0.00, -0.27, -0.00]
   497 | [ 3.77, -1.23, 1.50]    | [-1.49,  0.40, -0.00]   |  1.55 |  0.53 | REROUTE  | [-0.50, 0.13, -0.00]
   498 | [ 3.71, -1.21, 1.50]    | [-1.50,  0.40, -0.00]   |  1.55 |  0.48 | REROUTE  | [-0.50, 0.13, -0.00]
   499 | [ 3.65, -1.21, 1.50]    | [-1.50,  0.00, -0.00]   |  1.50 |  0.44 | REROUTE  | [-0.50, 0.00, -0.00]
   500 | [ 3.58, -1.21, 1.50]    | [-1.50,  0.00, -0.00]   |  1.50 |  0.42 | REROUTE  | [-0.50, 0.00, -0.00]
  ```

### [Seed 4053] Configuration: Shield ON (Camera) — Outcome: `TIMEOUT`
- **Steps:** 500 | **Reward:** -2352.9 | **Min Clearance:** 0.379 m
- **Diagnostic Cause:** Exceeded maximum episode limit (500 steps) without reaching goal.
- **Last 5 Control Steps Telemetry:**
  ```
  Step | Pos [x, y, z]           | Vel [vx, vy, vz]        | Speed | Clr   | State    | Action Executed
  -----+-------------------------+-------------------------+-------+-------+----------+----------------
   496 | [ 2.54, -1.01, 1.50]    | [ 1.50,  0.00, -0.00]   |  1.50 |  0.44 | REROUTE  | [0.50, 0.00, -0.00]
   497 | [ 2.60, -1.01, 1.50]    | [ 1.50,  0.00, -0.00]   |  1.50 |  0.44 | REROUTE  | [0.50, 0.00, -0.00]
   498 | [ 2.66, -1.01, 1.50]    | [ 1.50,  0.00, -0.00]   |  1.50 |  0.44 | REROUTE  | [0.50, 0.00, -0.00]
   499 | [ 2.73, -1.01, 1.50]    | [ 1.50,  0.00, -0.00]   |  1.50 |  0.43 | REROUTE  | [0.50, 0.00, -0.00]
   500 | [ 2.79, -1.01, 1.50]    | [ 1.50,  0.00, -0.00]   |  1.50 |  0.43 | REROUTE  | [0.50, 0.00, -0.00]
  ```

### [Seed 4054] Configuration: Shield ON (Camera) — Outcome: `OBSTACLE_COLLISION`
- **Steps:** 68 | **Reward:** -5.7 | **Min Clearance:** 0.546 m
- **Diagnostic Cause:** Obstacle collision at speed 1.07 m/s (min clearance 0.68m).
- **Last 5 Control Steps Telemetry:**
  ```
  Step | Pos [x, y, z]           | Vel [vx, vy, vz]        | Speed | Clr   | State    | Action Executed
  -----+-------------------------+-------------------------+-------+-------+----------+----------------
    64 | [ 0.64, -4.01, 1.48]    | [-0.41,  0.99, -0.01]   |  1.07 |  0.85 | NOMINAL  | [-0.14, 0.33, -0.01]
    65 | [ 0.66, -3.96, 1.48]    | [ 0.50,  1.24, -0.03]   |  1.34 |  0.80 | NOMINAL  | [0.17, 0.41, -0.01]
    66 | [ 0.65, -3.91, 1.48]    | [-0.23,  1.05, 0.01]    |  1.07 |  0.76 | NOMINAL  | [-0.08, 0.35, 0.01]
    67 | [ 0.66, -3.87, 1.48]    | [ 0.29,  0.97, -0.03]   |  1.01 |  0.72 | NOMINAL  | [0.10, 0.32, -0.01]
    68 | [ 0.68, -3.83, 1.48]    | [ 0.35,  1.01, -0.03]   |  1.07 |  0.68 | NOMINAL  | [0.12, 0.34, -0.01]
  ```

### [Seed 4055] Configuration: Shield ON (Camera) — Outcome: `TIMEOUT`
- **Steps:** 500 | **Reward:** -2410.37 | **Min Clearance:** 0.306 m
- **Diagnostic Cause:** Exceeded maximum episode limit (500 steps) without reaching goal.
- **Last 5 Control Steps Telemetry:**
  ```
  Step | Pos [x, y, z]           | Vel [vx, vy, vz]        | Speed | Clr   | State    | Action Executed
  -----+-------------------------+-------------------------+-------+-------+----------+----------------
   496 | [-3.51, -1.26, 1.50]    | [ 0.00, -0.80, 0.00]    |  0.80 |  0.43 | RETREAT  | [0.00, -0.27, 0.00]
   497 | [-3.51, -1.29, 1.50]    | [ 0.00, -0.80, 0.00]    |  0.80 |  0.47 | RETREAT  | [0.00, -0.27, 0.00]
   498 | [-3.51, -1.33, 1.50]    | [ 0.00, -0.80, 0.00]    |  0.80 |  0.50 | RETREAT  | [0.00, -0.27, 0.00]
   499 | [-3.51, -1.36, 1.50]    | [ 0.00, -0.80, 0.00]    |  0.80 |  0.53 | RETREAT  | [0.00, -0.27, 0.00]
   500 | [-3.51, -1.39, 1.50]    | [ 0.00, -0.80, 0.00]    |  0.80 |  0.57 | SCAN     | [0.00, -0.27, 0.00]
  ```

### [Seed 4056] Configuration: Shield ON (Camera) — Outcome: `OBSTACLE_COLLISION`
- **Steps:** 54 | **Reward:** 15.46 | **Min Clearance:** 1.566 m
- **Diagnostic Cause:** Obstacle collision at speed 2.90 m/s (min clearance 1.57m).
- **Last 5 Control Steps Telemetry:**
  ```
  Step | Pos [x, y, z]           | Vel [vx, vy, vz]        | Speed | Clr   | State    | Action Executed
  -----+-------------------------+-------------------------+-------+-------+----------+----------------
    50 | [ 1.06, -2.62, 1.48]    | [ 2.57,  1.55, 0.04]    |  3.00 |  1.96 | NOMINAL  | [0.86, 0.52, 0.01]
    51 | [ 1.16, -2.55, 1.48]    | [ 2.51,  1.64, 0.02]    |  3.00 |  1.81 | NOMINAL  | [0.84, 0.55, 0.01]
    52 | [ 1.27, -2.48, 1.48]    | [ 2.55,  1.58, 0.01]    |  3.00 |  1.71 | NOMINAL  | [0.85, 0.53, 0.01]
    53 | [ 1.21, -2.42, 1.48]    | [-1.37,  1.57, 0.03]    |  2.09 |  1.62 | NOMINAL  | [-0.46, 0.52, 0.01]
    54 | [ 1.32, -2.36, 1.48]    | [ 2.55,  1.39, -0.00]   |  2.90 |  1.57 | NOMINAL  | [0.85, 0.46, -0.00]
  ```

### [Seed 4057] Configuration: Shield ON (Camera) — Outcome: `TIMEOUT`
- **Steps:** 500 | **Reward:** -2214.92 | **Min Clearance:** 0.304 m
- **Diagnostic Cause:** Exceeded maximum episode limit (500 steps) without reaching goal.
- **Last 5 Control Steps Telemetry:**
  ```
  Step | Pos [x, y, z]           | Vel [vx, vy, vz]        | Speed | Clr   | State    | Action Executed
  -----+-------------------------+-------------------------+-------+-------+----------+----------------
   496 | [-3.56, -1.34, 1.50]    | [ 1.50,  0.40, -0.00]   |  1.55 |  0.56 | REROUTE  | [0.50, 0.13, -0.00]
   497 | [-3.50, -1.33, 1.50]    | [ 1.50,  0.40, -0.00]   |  1.55 |  0.55 | REROUTE  | [0.50, 0.13, -0.00]
   498 | [-3.43, -1.31, 1.50]    | [ 1.50,  0.40, -0.00]   |  1.55 |  0.54 | REROUTE  | [0.50, 0.13, -0.00]
   499 | [-3.37, -1.29, 1.50]    | [ 1.50,  0.40, -0.00]   |  1.55 |  0.53 | REROUTE  | [0.50, 0.13, -0.00]
   500 | [-3.31, -1.28, 1.50]    | [ 1.50,  0.40, -0.00]   |  1.55 |  0.52 | REROUTE  | [0.50, 0.13, -0.00]
  ```

### [Seed 4058] Configuration: Shield ON (Camera) — Outcome: `OBSTACLE_COLLISION`
- **Steps:** 56 | **Reward:** -68.99 | **Min Clearance:** 0.563 m
- **Diagnostic Cause:** Obstacle collision at speed 2.84 m/s (min clearance 3.94m).
- **Last 5 Control Steps Telemetry:**
  ```
  Step | Pos [x, y, z]           | Vel [vx, vy, vz]        | Speed | Clr   | State    | Action Executed
  -----+-------------------------+-------------------------+-------+-------+----------+----------------
    52 | [ 0.66, -4.93, 1.49]    | [ 1.50,  1.60, 0.03]    |  2.19 |  4.31 | REROUTE  | [0.50, 0.53, 0.01]
    53 | [ 0.64, -4.84, 1.48]    | [-0.41,  2.19, -0.01]   |  2.23 |  4.25 | NOMINAL  | [-0.14, 0.73, -0.00]
    54 | [ 0.63, -4.73, 1.48]    | [-0.29,  2.50, -0.02]   |  2.51 |  4.16 | NOMINAL  | [-0.10, 0.83, -0.01]
    55 | [ 0.61, -4.62, 1.48]    | [-0.52,  2.69, -0.05]   |  2.75 |  4.05 | NOMINAL  | [-0.17, 0.90, -0.02]
    56 | [ 0.59, -4.50, 1.48]    | [-0.41,  2.81, 0.01]    |  2.84 |  3.94 | NOMINAL  | [-0.14, 0.94, 0.00]
  ```

### [Seed 4059] Configuration: Shield ON (Camera) — Outcome: `OBSTACLE_COLLISION`
- **Steps:** 81 | **Reward:** -132.38 | **Min Clearance:** 0.554 m
- **Diagnostic Cause:** Obstacle collision at speed 1.55 m/s (min clearance 0.55m).
- **Last 5 Control Steps Telemetry:**
  ```
  Step | Pos [x, y, z]           | Vel [vx, vy, vz]        | Speed | Clr   | State    | Action Executed
  -----+-------------------------+-------------------------+-------+-------+----------+----------------
    77 | [-1.36, -1.19, 1.50]    | [-0.07,  0.62, 0.05]    |  0.63 |  0.59 | NOMINAL  | [-0.03, 0.21, 0.02]
    78 | [-1.35, -1.18, 1.50]    | [ 0.33,  0.22, 0.01]    |  0.40 |  0.57 | NOMINAL  | [0.11, 0.07, 0.00]
    79 | [-1.35, -1.18, 1.50]    | [ 0.00,  0.00, 0.00]    |  0.00 |  0.55 | BRAKE    | [0.00, 0.00, 0.00]
    80 | [-1.35, -1.18, 1.50]    | [ 0.00,  0.00, 0.00]    |  0.00 |  0.55 | SCAN     | [0.00, 0.00, 0.00]
    81 | [-1.41, -1.16, 1.50]    | [-1.50,  0.40, 0.01]    |  1.55 |  0.55 | REROUTE  | [-0.50, 0.13, 0.00]
  ```
