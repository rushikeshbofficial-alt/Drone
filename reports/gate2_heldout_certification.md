# Stop, Hover & Re-Route (SHR) Drone Safety Shield Benchmark Report

**Date:** 2026-10-15T23:17:59Z  
**Seeds:** `1000-1049` (50 episodes)  
**Checkpoint:** `best_model.pt`  

## Executive Summary & Comparison Table

| Metric | Baseline (OFF) | Shield ON (Oracle) | Shield ON (Camera) | Target |
|---|:---:|:---:|:---:|:---:|
| **Success Rate (95% CI)** |  24.0% [14.3%, 37.4%] (12/50) |  70.0% [56.2%, 80.9%] (35/50) |   0.0% [ 0.0%,  7.1%] (0/50) | **>= 85.0%** |
| **Total Collision Rate** |  76.0% [62.6%, 85.7%] (38/50) |   0.0% [ 0.0%,  7.1%] (0/50) |  56.0% [42.3%, 68.8%] (28/50) | **<= 2.0%** |
| Obstacle Collisions |  76.0% [62.6%, 85.7%] (38/50) |   0.0% [ 0.0%,  7.1%] (0/50) |  56.0% [42.3%, 68.8%] (28/50) | — |
| Wall OOB Collisions |   0.0% [ 0.0%,  7.1%] (0/50) |   0.0% [ 0.0%,  7.1%] (0/50) |   0.0% [ 0.0%,  7.1%] (0/50) | — |
| Timeout Rate |   0.0% [ 0.0%,  7.1%] (0/50) |  30.0% [19.1%, 43.8%] (15/50) |  44.0% [31.2%, 57.7%] (22/50) | **<= 5.0%** |
| **Mean Reward** | -23.10 +/- 145.58 | -644.97 +/- 801.00 | -1133.50 +/- 1197.86 | — |
| **Mean Min Clearance** | 0.14 m | 0.26 m | 0.44 m | — |
| **Mean Episode Steps** | 84.1 | 313.8 | 255.6 | — |
| **Standoff Distance** | N/A | 1.46 m | 0.46 m | **>= 0.45 m** |
| **Step Overhead (Baseline Succ)** | Baseline | 36.97% | 176.61% | **<= 15.0%** |

## Acceptance Criteria Audit

| Criterion | Target | Achieved (Oracle) | Verdict |
|---|:---:|:---:|:---:|
| Total Collisions <= 2.0% | <= 2.0% | 0.0% | **✅ PASS** |
| Success Rate >= 85.0% | >= 85.0% | 70.0% | **❌ FAIL** |
| Timeout Rate <= 5.0% | <= 5.0% | 30.0% | **❌ FAIL** |
| Standoff Distance >= 0.45m | >= 0.45 m | 1.46 m | **✅ PASS** |
| Step Overhead on Baseline-Success <= 15.0% | <= 15.0% | 37.0% | **❌ FAIL** |

**Overall Status:** ⚠️ **ACTION REQUIRED: CRITERIA UNMET**

## Crash Forensics Log

Total non-success episodes analyzed: **103**

### [Seed 1001] Configuration: Baseline (Shield OFF) — Outcome: `OBSTACLE_COLLISION`
- **Steps:** 58 | **Reward:** -51.58 | **Min Clearance:** 0.122 m
- **Diagnostic Cause:** Obstacle collision at speed 2.94 m/s (min clearance 0.13m).
- **Last 5 Control Steps Telemetry:**
  ```
  Step | Pos [x, y, z]           | Vel [vx, vy, vz]        | Speed | Clr   | State    | Action Executed
  -----+-------------------------+-------------------------+-------+-------+----------+----------------
    54 | [ 0.09, -2.13, 1.51]    | [ 2.44,  1.63, -0.01]   |  2.94 |  0.14 | DISABLED | [0.81, 0.54, -0.00]
    55 | [ 0.15, -2.05, 1.51]    | [ 1.45,  1.74, -0.01]   |  2.26 |  0.16 | DISABLED | [0.48, 0.58, -0.00]
    56 | [ 0.26, -1.98, 1.51]    | [ 2.50,  1.79, 0.01]    |  3.08 |  0.13 | DISABLED | [0.83, 0.60, 0.00]
    57 | [ 0.38, -1.91, 1.51]    | [ 2.87,  1.77, -0.01]   |  3.37 |  0.17 | DISABLED | [0.96, 0.59, -0.00]
    58 | [ 0.47, -1.83, 1.51]    | [ 2.25,  1.89, -0.03]   |  2.94 |  0.13 | DISABLED | [0.75, 0.63, -0.01]
  ```

### [Seed 1003] Configuration: Baseline (Shield OFF) — Outcome: `OBSTACLE_COLLISION`
- **Steps:** 62 | **Reward:** -82.36 | **Min Clearance:** 0.099 m
- **Diagnostic Cause:** Obstacle collision at speed 3.16 m/s (min clearance 0.16m).
- **Last 5 Control Steps Telemetry:**
  ```
  Step | Pos [x, y, z]           | Vel [vx, vy, vz]        | Speed | Clr   | State    | Action Executed
  -----+-------------------------+-------------------------+-------+-------+----------+----------------
    58 | [ 1.57, -1.53, 1.49]    | [ 1.77,  2.31, -0.02]   |  2.92 |  0.12 | DISABLED | [0.59, 0.77, -0.01]
    59 | [ 1.61, -1.43, 1.49]    | [ 0.92,  2.30, -0.01]   |  2.47 |  0.13 | DISABLED | [0.31, 0.77, -0.00]
    60 | [ 1.64, -1.34, 1.49]    | [ 0.66,  2.31, -0.00]   |  2.40 |  0.11 | DISABLED | [0.22, 0.77, -0.00]
    61 | [ 1.73, -1.24, 1.49]    | [ 2.16,  2.29, -0.01]   |  3.15 |  0.10 | DISABLED | [0.72, 0.76, -0.00]
    62 | [ 1.82, -1.15, 1.49]    | [ 2.16,  2.31, -0.01]   |  3.16 |  0.16 | DISABLED | [0.72, 0.77, -0.00]
  ```

### [Seed 1006] Configuration: Baseline (Shield OFF) — Outcome: `OBSTACLE_COLLISION`
- **Steps:** 39 | **Reward:** 70.09 | **Min Clearance:** 0.192 m
- **Diagnostic Cause:** Obstacle collision at speed 2.77 m/s (min clearance 0.19m).
- **Last 5 Control Steps Telemetry:**
  ```
  Step | Pos [x, y, z]           | Vel [vx, vy, vz]        | Speed | Clr   | State    | Action Executed
  -----+-------------------------+-------------------------+-------+-------+----------+----------------
    35 | [ 0.22, -3.90, 1.50]    | [-1.48,  2.56, -0.01]   |  2.96 |  0.65 | DISABLED | [-0.49, 0.85, -0.00]
    36 | [ 0.16, -3.79, 1.50]    | [-1.30,  2.63, 0.01]    |  2.93 |  0.53 | DISABLED | [-0.43, 0.88, 0.00]
    37 | [ 0.14, -3.68, 1.50]    | [-0.48,  2.63, -0.00]   |  2.67 |  0.42 | DISABLED | [-0.16, 0.88, -0.00]
    38 | [ 0.10, -3.58, 1.50]    | [-0.97,  2.55, 0.02]    |  2.73 |  0.31 | DISABLED | [-0.32, 0.85, 0.01]
    39 | [ 0.06, -3.47, 1.50]    | [-1.03,  2.57, -0.02]   |  2.77 |  0.19 | DISABLED | [-0.34, 0.86, -0.01]
  ```

### [Seed 1008] Configuration: Baseline (Shield OFF) — Outcome: `OBSTACLE_COLLISION`
- **Steps:** 33 | **Reward:** 51.11 | **Min Clearance:** 0.03 m
- **Diagnostic Cause:** Obstacle collision at speed 3.44 m/s (min clearance 0.03m).
- **Last 5 Control Steps Telemetry:**
  ```
  Step | Pos [x, y, z]           | Vel [vx, vy, vz]        | Speed | Clr   | State    | Action Executed
  -----+-------------------------+-------------------------+-------+-------+----------+----------------
    29 | [ 0.30, -4.58, 1.50]    | [ 0.23,  2.75, -0.02]   |  2.76 |  0.73 | DISABLED | [0.07, 0.92, -0.01]
    30 | [ 0.28, -4.46, 1.50]    | [-0.49,  2.80, -0.03]   |  2.84 |  0.60 | DISABLED | [-0.17, 0.93, -0.01]
    31 | [ 0.29, -4.35, 1.50]    | [ 0.35,  2.70, 0.01]    |  2.73 |  0.52 | DISABLED | [0.12, 0.90, 0.00]
    32 | [ 0.22, -4.23, 1.50]    | [-1.70,  2.79, 0.01]    |  3.27 |  0.30 | DISABLED | [-0.57, 0.93, 0.00]
    33 | [ 0.13, -4.12, 1.50]    | [-2.18,  2.67, 0.01]    |  3.44 |  0.03 | DISABLED | [-0.73, 0.89, 0.00]
  ```

### [Seed 1009] Configuration: Baseline (Shield OFF) — Outcome: `OBSTACLE_COLLISION`
- **Steps:** 38 | **Reward:** 55.63 | **Min Clearance:** 0.243 m
- **Diagnostic Cause:** Obstacle collision at speed 2.64 m/s (min clearance 0.24m).
- **Last 5 Control Steps Telemetry:**
  ```
  Step | Pos [x, y, z]           | Vel [vx, vy, vz]        | Speed | Clr   | State    | Action Executed
  -----+-------------------------+-------------------------+-------+-------+----------+----------------
    34 | [-0.10, -4.11, 1.50]    | [ 1.58,  2.11, -0.00]   |  2.63 |  0.60 | DISABLED | [0.53, 0.70, -0.00]
    35 | [-0.16, -4.01, 1.50]    | [-1.34,  2.28, 0.00]    |  2.64 |  0.49 | DISABLED | [-0.45, 0.76, 0.00]
    36 | [-0.11, -3.92, 1.50]    | [ 1.12,  2.24, -0.01]   |  2.50 |  0.41 | DISABLED | [0.37, 0.75, -0.00]
    37 | [-0.07, -3.82, 1.50]    | [ 0.95,  2.28, -0.01]   |  2.47 |  0.32 | DISABLED | [0.32, 0.76, -0.00]
    38 | [-0.02, -3.73, 1.50]    | [ 1.23,  2.33, -0.00]   |  2.64 |  0.24 | DISABLED | [0.41, 0.78, -0.00]
  ```

### [Seed 1010] Configuration: Baseline (Shield OFF) — Outcome: `OBSTACLE_COLLISION`
- **Steps:** 34 | **Reward:** 38.82 | **Min Clearance:** 0.186 m
- **Diagnostic Cause:** Obstacle collision at speed 2.21 m/s (min clearance 0.19m).
- **Last 5 Control Steps Telemetry:**
  ```
  Step | Pos [x, y, z]           | Vel [vx, vy, vz]        | Speed | Clr   | State    | Action Executed
  -----+-------------------------+-------------------------+-------+-------+----------+----------------
    30 | [-0.25, -4.49, 1.49]    | [ 0.49,  2.50, 0.01]    |  2.55 |  0.52 | DISABLED | [0.16, 0.83, 0.00]
    31 | [-0.24, -4.39, 1.50]    | [ 0.16,  2.53, 0.02]    |  2.53 |  0.41 | DISABLED | [0.06, 0.84, 0.01]
    32 | [-0.14, -4.30, 1.49]    | [ 2.53,  2.19, -0.02]   |  3.35 |  0.34 | DISABLED | [0.84, 0.73, -0.01]
    33 | [-0.02, -4.21, 1.49]    | [ 2.79,  2.13, 0.00]    |  3.51 |  0.28 | DISABLED | [0.93, 0.71, 0.00]
    34 | [-0.07, -4.13, 1.50]    | [-1.07,  1.94, 0.01]    |  2.21 |  0.19 | DISABLED | [-0.36, 0.65, 0.00]
  ```

### [Seed 1011] Configuration: Baseline (Shield OFF) — Outcome: `OBSTACLE_COLLISION`
- **Steps:** 64 | **Reward:** -43.73 | **Min Clearance:** 0.118 m
- **Diagnostic Cause:** Obstacle collision at speed 3.05 m/s (min clearance 0.16m).
- **Last 5 Control Steps Telemetry:**
  ```
  Step | Pos [x, y, z]           | Vel [vx, vy, vz]        | Speed | Clr   | State    | Action Executed
  -----+-------------------------+-------------------------+-------+-------+----------+----------------
    60 | [ 0.47, -1.39, 1.49]    | [ 2.81,  1.80, -0.01]   |  3.34 |  0.18 | DISABLED | [0.94, 0.60, -0.00]
    61 | [ 0.59, -1.32, 1.49]    | [ 2.98,  1.72, -0.01]   |  3.44 |  0.15 | DISABLED | [0.99, 0.57, -0.00]
    62 | [ 0.62, -1.24, 1.49]    | [ 0.68,  1.77, 0.01]    |  1.89 |  0.15 | DISABLED | [0.23, 0.59, 0.00]
    63 | [ 0.69, -1.17, 1.49]    | [ 1.77,  1.84, -0.02]   |  2.56 |  0.15 | DISABLED | [0.59, 0.61, -0.01]
    64 | [ 0.80, -1.09, 1.49]    | [ 2.45,  1.81, -0.06]   |  3.05 |  0.16 | DISABLED | [0.82, 0.60, -0.02]
  ```

### [Seed 1012] Configuration: Baseline (Shield OFF) — Outcome: `OBSTACLE_COLLISION`
- **Steps:** 83 | **Reward:** -137.2 | **Min Clearance:** 0.104 m
- **Diagnostic Cause:** Obstacle collision at speed 2.33 m/s (min clearance 0.10m).
- **Last 5 Control Steps Telemetry:**
  ```
  Step | Pos [x, y, z]           | Vel [vx, vy, vz]        | Speed | Clr   | State    | Action Executed
  -----+-------------------------+-------------------------+-------+-------+----------+----------------
    79 | [-2.37,  0.04, 1.50]    | [ 0.86,  2.29, -0.00]   |  2.45 |  0.14 | DISABLED | [0.29, 0.77, -0.00]
    80 | [-2.32,  0.14, 1.50]    | [ 1.17,  2.30, 0.01]    |  2.58 |  0.13 | DISABLED | [0.39, 0.77, 0.00]
    81 | [-2.24,  0.23, 1.51]    | [ 1.94,  2.23, 0.06]    |  2.96 |  0.13 | DISABLED | [0.65, 0.74, 0.02]
    82 | [-2.11,  0.33, 1.51]    | [ 2.98,  2.23, 0.06]    |  3.72 |  0.14 | DISABLED | [0.99, 0.74, 0.02]
    83 | [-2.14,  0.42, 1.51]    | [-0.73,  2.22, 0.03]    |  2.33 |  0.10 | DISABLED | [-0.24, 0.74, 0.01]
  ```

### [Seed 1014] Configuration: Baseline (Shield OFF) — Outcome: `OBSTACLE_COLLISION`
- **Steps:** 44 | **Reward:** 44.45 | **Min Clearance:** 0.196 m
- **Diagnostic Cause:** Obstacle collision at speed 3.62 m/s (min clearance 0.20m).
- **Last 5 Control Steps Telemetry:**
  ```
  Step | Pos [x, y, z]           | Vel [vx, vy, vz]        | Speed | Clr   | State    | Action Executed
  -----+-------------------------+-------------------------+-------+-------+----------+----------------
    40 | [-0.03, -3.77, 1.51]    | [-0.60,  2.56, 0.03]    |  2.63 |  0.53 | DISABLED | [-0.20, 0.85, 0.01]
    41 | [ 0.04, -3.66, 1.51]    | [ 1.63,  2.53, -0.07]   |  3.01 |  0.35 | DISABLED | [0.54, 0.84, -0.02]
    42 | [-0.06, -3.56, 1.51]    | [-2.30,  2.39, 0.03]    |  3.32 |  0.44 | DISABLED | [-0.77, 0.80, 0.01]
    43 | [-0.07, -3.46, 1.51]    | [-0.43,  2.52, -0.01]   |  2.56 |  0.35 | DISABLED | [-0.14, 0.84, -0.01]
    44 | [ 0.04, -3.36, 1.51]    | [ 2.85,  2.24, -0.02]   |  3.62 |  0.20 | DISABLED | [0.95, 0.75, -0.01]
  ```

### [Seed 1015] Configuration: Baseline (Shield OFF) — Outcome: `OBSTACLE_COLLISION`
- **Steps:** 91 | **Reward:** -206.56 | **Min Clearance:** 0.113 m
- **Diagnostic Cause:** Obstacle collision at speed 2.55 m/s (min clearance 0.15m).
- **Last 5 Control Steps Telemetry:**
  ```
  Step | Pos [x, y, z]           | Vel [vx, vy, vz]        | Speed | Clr   | State    | Action Executed
  -----+-------------------------+-------------------------+-------+-------+----------+----------------
    87 | [-0.69,  0.71, 1.52]    | [ 0.15,  2.11, 0.04]    |  2.11 |  0.14 | DISABLED | [0.05, 0.70, 0.01]
    88 | [-0.77,  0.81, 1.52]    | [-1.95,  2.50, -0.01]   |  3.17 |  0.15 | DISABLED | [-0.65, 0.83, -0.00]
    89 | [-0.88,  0.90, 1.52]    | [-2.75,  2.21, -0.03]   |  3.53 |  0.15 | DISABLED | [-0.92, 0.74, -0.01]
    90 | [-0.96,  0.99, 1.52]    | [-1.76,  2.13, -0.02]   |  2.77 |  0.14 | DISABLED | [-0.59, 0.71, -0.01]
    91 | [-1.02,  1.08, 1.51]    | [-1.54,  2.04, -0.13]   |  2.55 |  0.15 | DISABLED | [-0.51, 0.68, -0.04]
  ```

### [Seed 1016] Configuration: Baseline (Shield OFF) — Outcome: `OBSTACLE_COLLISION`
- **Steps:** 26 | **Reward:** -26.88 | **Min Clearance:** 0.237 m
- **Diagnostic Cause:** Obstacle collision at speed 2.95 m/s (min clearance 0.24m).
- **Last 5 Control Steps Telemetry:**
  ```
  Step | Pos [x, y, z]           | Vel [vx, vy, vz]        | Speed | Clr   | State    | Action Executed
  -----+-------------------------+-------------------------+-------+-------+----------+----------------
    22 | [ 0.52, -5.52, 1.50]    | [ 1.90,  2.49, -0.04]   |  3.13 |  0.55 | DISABLED | [0.63, 0.83, -0.01]
    23 | [ 0.50, -5.40, 1.49]    | [-0.33,  2.77, -0.10]   |  2.79 |  0.47 | DISABLED | [-0.11, 0.92, -0.03]
    24 | [ 0.49, -5.29, 1.49]    | [-0.28,  2.84, -0.02]   |  2.85 |  0.38 | DISABLED | [-0.09, 0.94, -0.01]
    25 | [ 0.49, -5.16, 1.49]    | [-0.10,  2.92, -0.00]   |  2.92 |  0.31 | DISABLED | [-0.03, 0.97, -0.00]
    26 | [ 0.47, -5.04, 1.49]    | [-0.42,  2.92, -0.01]   |  2.95 |  0.24 | DISABLED | [-0.14, 0.97, -0.00]
  ```

### [Seed 1017] Configuration: Baseline (Shield OFF) — Outcome: `OBSTACLE_COLLISION`
- **Steps:** 73 | **Reward:** -222.98 | **Min Clearance:** 0.095 m
- **Diagnostic Cause:** Obstacle collision at speed 3.31 m/s (min clearance 0.12m).
- **Last 5 Control Steps Telemetry:**
  ```
  Step | Pos [x, y, z]           | Vel [vx, vy, vz]        | Speed | Clr   | State    | Action Executed
  -----+-------------------------+-------------------------+-------+-------+----------+----------------
    69 | [ 2.40, -1.11, 1.49]    | [ 0.15,  1.63, -0.01]   |  1.64 |  0.12 | DISABLED | [0.05, 0.54, -0.00]
    70 | [ 2.28, -1.05, 1.49]    | [-2.88,  1.36, -0.02]   |  3.19 |  0.11 | DISABLED | [-0.96, 0.45, -0.01]
    71 | [ 2.18, -0.99, 1.49]    | [-2.38,  1.56, 0.02]    |  2.84 |  0.13 | DISABLED | [-0.79, 0.52, 0.01]
    72 | [ 2.06, -0.93, 1.49]    | [-2.96,  1.46, -0.08]   |  3.31 |  0.13 | DISABLED | [-0.99, 0.49, -0.03]
    73 | [ 2.18, -0.87, 1.49]    | [ 2.99,  1.42, 0.01]    |  3.31 |  0.12 | DISABLED | [1.00, 0.47, 0.00]
  ```

### [Seed 1018] Configuration: Baseline (Shield OFF) — Outcome: `OBSTACLE_COLLISION`
- **Steps:** 101 | **Reward:** -216.07 | **Min Clearance:** 0.092 m
- **Diagnostic Cause:** Obstacle collision at speed 1.60 m/s (min clearance 0.39m).
- **Last 5 Control Steps Telemetry:**
  ```
  Step | Pos [x, y, z]           | Vel [vx, vy, vz]        | Speed | Clr   | State    | Action Executed
  -----+-------------------------+-------------------------+-------+-------+----------+----------------
    97 | [ 2.74,  1.87, 1.48]    | [-2.60,  0.89, 0.05]    |  2.75 |  0.49 | DISABLED | [-0.87, 0.30, 0.02]
    98 | [ 2.65,  1.91, 1.48]    | [-2.33,  1.02, 0.02]    |  2.54 |  0.42 | DISABLED | [-0.78, 0.34, 0.01]
    99 | [ 2.68,  1.95, 1.48]    | [ 0.89,  0.77, -0.01]   |  1.18 |  0.41 | DISABLED | [0.30, 0.26, -0.00]
   100 | [ 2.65,  1.99, 1.48]    | [-0.74,  1.12, 0.01]    |  1.34 |  0.46 | DISABLED | [-0.25, 0.37, 0.00]
   101 | [ 2.70,  2.04, 1.48]    | [ 1.11,  1.15, -0.02]   |  1.60 |  0.39 | DISABLED | [0.37, 0.38, -0.01]
  ```

### [Seed 1020] Configuration: Baseline (Shield OFF) — Outcome: `OBSTACLE_COLLISION`
- **Steps:** 31 | **Reward:** 44.08 | **Min Clearance:** 0.262 m
- **Diagnostic Cause:** Obstacle collision at speed 2.84 m/s (min clearance 0.26m).
- **Last 5 Control Steps Telemetry:**
  ```
  Step | Pos [x, y, z]           | Vel [vx, vy, vz]        | Speed | Clr   | State    | Action Executed
  -----+-------------------------+-------------------------+-------+-------+----------+----------------
    27 | [ 0.06, -4.74, 1.50]    | [-0.86,  2.86, -0.03]   |  2.98 |  0.64 | DISABLED | [-0.29, 0.95, -0.01]
    28 | [ 0.01, -4.63, 1.49]    | [-1.13,  2.77, -0.04]   |  3.00 |  0.51 | DISABLED | [-0.38, 0.93, -0.01]
    29 | [-0.01, -4.51, 1.49]    | [-0.48,  2.75, -0.02]   |  2.79 |  0.42 | DISABLED | [-0.16, 0.92, -0.01]
    30 | [-0.02, -4.40, 1.49]    | [-0.30,  2.75, -0.02]   |  2.77 |  0.34 | DISABLED | [-0.10, 0.92, -0.01]
    31 | [-0.03, -4.28, 1.49]    | [-0.28,  2.83, -0.04]   |  2.84 |  0.26 | DISABLED | [-0.09, 0.94, -0.01]
  ```

### [Seed 1022] Configuration: Baseline (Shield OFF) — Outcome: `OBSTACLE_COLLISION`
- **Steps:** 120 | **Reward:** -335.45 | **Min Clearance:** 0.111 m
- **Diagnostic Cause:** Obstacle collision at speed 3.19 m/s (min clearance 0.13m).
- **Last 5 Control Steps Telemetry:**
  ```
  Step | Pos [x, y, z]           | Vel [vx, vy, vz]        | Speed | Clr   | State    | Action Executed
  -----+-------------------------+-------------------------+-------+-------+----------+----------------
   116 | [ 0.07,  2.10, 1.48]    | [-1.88,  2.70, -0.01]   |  3.29 |  0.14 | DISABLED | [-0.63, 0.90, -0.01]
   117 | [-0.01,  2.22, 1.48]    | [-1.73,  2.80, -0.02]   |  3.29 |  0.14 | DISABLED | [-0.58, 0.94, -0.01]
   118 | [-0.07,  2.34, 1.48]    | [-1.60,  2.83, -0.03]   |  3.25 |  0.13 | DISABLED | [-0.54, 0.94, -0.01]
   119 | [-0.12,  2.45, 1.48]    | [-1.24,  2.79, -0.01]   |  3.05 |  0.14 | DISABLED | [-0.41, 0.93, -0.00]
   120 | [-0.19,  2.57, 1.48]    | [-1.46,  2.83, -0.00]   |  3.19 |  0.13 | DISABLED | [-0.49, 0.94, -0.00]
  ```

### [Seed 1023] Configuration: Baseline (Shield OFF) — Outcome: `OBSTACLE_COLLISION`
- **Steps:** 45 | **Reward:** 69.48 | **Min Clearance:** 0.141 m
- **Diagnostic Cause:** Obstacle collision at speed 2.51 m/s (min clearance 0.14m).
- **Last 5 Control Steps Telemetry:**
  ```
  Step | Pos [x, y, z]           | Vel [vx, vy, vz]        | Speed | Clr   | State    | Action Executed
  -----+-------------------------+-------------------------+-------+-------+----------+----------------
    41 | [-0.28, -3.10, 1.50]    | [-0.93,  2.41, 0.04]    |  2.58 |  0.20 | DISABLED | [-0.31, 0.80, 0.01]
    42 | [-0.34, -2.99, 1.50]    | [-1.38,  2.57, 0.02]    |  2.92 |  0.17 | DISABLED | [-0.46, 0.86, 0.01]
    43 | [-0.41, -2.88, 1.50]    | [-1.88,  2.61, 0.01]    |  3.22 |  0.15 | DISABLED | [-0.62, 0.87, 0.01]
    44 | [-0.50, -2.77, 1.50]    | [-2.16,  2.65, 0.02]    |  3.42 |  0.16 | DISABLED | [-0.72, 0.88, 0.01]
    45 | [-0.52, -2.67, 1.50]    | [-0.47,  2.46, 0.04]    |  2.51 |  0.14 | DISABLED | [-0.15, 0.82, 0.01]
  ```

### [Seed 1025] Configuration: Baseline (Shield OFF) — Outcome: `OBSTACLE_COLLISION`
- **Steps:** 138 | **Reward:** -431.04 | **Min Clearance:** 0.099 m
- **Diagnostic Cause:** Obstacle collision at speed 1.44 m/s (min clearance 0.13m).
- **Last 5 Control Steps Telemetry:**
  ```
  Step | Pos [x, y, z]           | Vel [vx, vy, vz]        | Speed | Clr   | State    | Action Executed
  -----+-------------------------+-------------------------+-------+-------+----------+----------------
   134 | [-0.19,  2.87, 1.51]    | [-0.46,  1.36, -0.02]   |  1.44 |  0.15 | DISABLED | [-0.15, 0.45, -0.01]
   135 | [-0.10,  2.92, 1.51]    | [ 2.14,  1.23, -0.04]   |  2.46 |  0.13 | DISABLED | [0.71, 0.41, -0.01]
   136 | [-0.02,  2.97, 1.51]    | [ 1.84,  1.23, -0.04]   |  2.22 |  0.17 | DISABLED | [0.61, 0.41, -0.01]
   137 | [-0.03,  3.02, 1.51]    | [-0.18,  1.23, -0.01]   |  1.24 |  0.14 | DISABLED | [-0.06, 0.41, -0.01]
   138 | [-0.07,  3.06, 1.51]    | [-1.00,  1.04, 0.02]    |  1.44 |  0.13 | DISABLED | [-0.33, 0.35, 0.01]
  ```

### [Seed 1026] Configuration: Baseline (Shield OFF) — Outcome: `OBSTACLE_COLLISION`
- **Steps:** 52 | **Reward:** -6.87 | **Min Clearance:** 0.113 m
- **Diagnostic Cause:** Obstacle collision at speed 3.53 m/s (min clearance 0.13m).
- **Last 5 Control Steps Telemetry:**
  ```
  Step | Pos [x, y, z]           | Vel [vx, vy, vz]        | Speed | Clr   | State    | Action Executed
  -----+-------------------------+-------------------------+-------+-------+----------+----------------
    48 | [ 0.50, -2.38, 1.50]    | [ 1.07,  2.47, -0.03]   |  2.69 |  0.16 | DISABLED | [0.36, 0.82, -0.01]
    49 | [ 0.62, -2.29, 1.50]    | [ 2.90,  2.24, 0.06]    |  3.67 |  0.14 | DISABLED | [0.97, 0.75, 0.02]
    50 | [ 0.73, -2.19, 1.50]    | [ 2.69,  2.25, -0.01]   |  3.50 |  0.15 | DISABLED | [0.90, 0.75, -0.00]
    51 | [ 0.85, -2.10, 1.50]    | [ 2.78,  2.29, -0.04]   |  3.61 |  0.13 | DISABLED | [0.93, 0.76, -0.01]
    52 | [ 0.97, -2.01, 1.50]    | [ 2.77,  2.19, -0.01]   |  3.53 |  0.13 | DISABLED | [0.92, 0.73, -0.00]
  ```

### [Seed 1028] Configuration: Baseline (Shield OFF) — Outcome: `OBSTACLE_COLLISION`
- **Steps:** 89 | **Reward:** -155.55 | **Min Clearance:** 0.023 m
- **Diagnostic Cause:** Obstacle collision at speed 2.97 m/s (min clearance 0.02m).
- **Last 5 Control Steps Telemetry:**
  ```
  Step | Pos [x, y, z]           | Vel [vx, vy, vz]        | Speed | Clr   | State    | Action Executed
  -----+-------------------------+-------------------------+-------+-------+----------+----------------
    85 | [-2.09, -0.63, 1.48]    | [-1.69,  1.31, 0.02]    |  2.14 |  0.12 | DISABLED | [-0.56, 0.44, 0.01]
    86 | [-2.13, -0.57, 1.48]    | [-0.94,  1.34, -0.01]   |  1.63 |  0.15 | DISABLED | [-0.31, 0.45, -0.00]
    87 | [-2.20, -0.53, 1.48]    | [-1.72,  1.19, 0.01]    |  2.09 |  0.11 | DISABLED | [-0.57, 0.40, 0.00]
    88 | [-2.29, -0.47, 1.48]    | [-2.12,  1.24, 0.03]    |  2.46 |  0.12 | DISABLED | [-0.71, 0.41, 0.01]
    89 | [-2.40, -0.42, 1.48]    | [-2.73,  1.17, 0.02]    |  2.97 |  0.02 | DISABLED | [-0.91, 0.39, 0.01]
  ```

### [Seed 1029] Configuration: Baseline (Shield OFF) — Outcome: `OBSTACLE_COLLISION`
- **Steps:** 86 | **Reward:** -145.2 | **Min Clearance:** 0.031 m
- **Diagnostic Cause:** Obstacle collision at speed 2.82 m/s (min clearance 0.03m).
- **Last 5 Control Steps Telemetry:**
  ```
  Step | Pos [x, y, z]           | Vel [vx, vy, vz]        | Speed | Clr   | State    | Action Executed
  -----+-------------------------+-------------------------+-------+-------+----------+----------------
    82 | [ 0.07,  0.48, 1.50]    | [ 0.51,  2.43, -0.01]   |  2.48 |  0.15 | DISABLED | [0.17, 0.81, -0.00]
    83 | [ 0.13,  0.59, 1.51]    | [ 1.54,  2.56, 0.05]    |  2.99 |  0.18 | DISABLED | [0.51, 0.85, 0.02]
    84 | [ 0.08,  0.70, 1.51]    | [-1.29,  2.59, 0.02]    |  2.90 |  0.15 | DISABLED | [-0.43, 0.86, 0.01]
    85 | [ 0.04,  0.81, 1.51]    | [-1.02,  2.60, 0.06]    |  2.80 |  0.14 | DISABLED | [-0.34, 0.87, 0.02]
    86 | [-0.02,  0.91, 1.51]    | [-1.34,  2.48, 0.02]    |  2.82 |  0.03 | DISABLED | [-0.45, 0.83, 0.01]
  ```

### [Seed 1031] Configuration: Baseline (Shield OFF) — Outcome: `OBSTACLE_COLLISION`
- **Steps:** 62 | **Reward:** -44.18 | **Min Clearance:** 0.104 m
- **Diagnostic Cause:** Obstacle collision at speed 2.69 m/s (min clearance 0.10m).
- **Last 5 Control Steps Telemetry:**
  ```
  Step | Pos [x, y, z]           | Vel [vx, vy, vz]        | Speed | Clr   | State    | Action Executed
  -----+-------------------------+-------------------------+-------+-------+----------+----------------
    58 | [ 1.54, -2.02, 1.47]    | [ 2.78,  1.58, 0.02]    |  3.20 |  0.14 | DISABLED | [0.93, 0.53, 0.01]
    59 | [ 1.47, -1.97, 1.47]    | [-1.69,  1.39, 0.04]    |  2.19 |  0.12 | DISABLED | [-0.56, 0.46, 0.01]
    60 | [ 1.58, -1.91, 1.47]    | [ 2.74,  1.35, -0.01]   |  3.06 |  0.13 | DISABLED | [0.91, 0.45, -0.01]
    61 | [ 1.46, -1.86, 1.47]    | [-2.84,  1.16, 0.01]    |  3.07 |  0.12 | DISABLED | [-0.95, 0.39, 0.00]
    62 | [ 1.37, -1.80, 1.48]    | [-2.33,  1.36, 0.09]    |  2.69 |  0.10 | DISABLED | [-0.78, 0.45, 0.03]
  ```

### [Seed 1032] Configuration: Baseline (Shield OFF) — Outcome: `OBSTACLE_COLLISION`
- **Steps:** 87 | **Reward:** -241.29 | **Min Clearance:** 0.097 m
- **Diagnostic Cause:** Obstacle collision at speed 2.90 m/s (min clearance 0.12m).
- **Last 5 Control Steps Telemetry:**
  ```
  Step | Pos [x, y, z]           | Vel [vx, vy, vz]        | Speed | Clr   | State    | Action Executed
  -----+-------------------------+-------------------------+-------+-------+----------+----------------
    83 | [-2.20,  0.31, 1.49]    | [ 2.38,  1.82, 0.04]    |  2.99 |  0.12 | DISABLED | [0.79, 0.61, 0.01]
    84 | [-2.18,  0.38, 1.49]    | [ 0.64,  1.75, -0.01]   |  1.86 |  0.12 | DISABLED | [0.21, 0.58, -0.00]
    85 | [-2.14,  0.45, 1.49]    | [ 0.86,  1.67, 0.01]    |  1.88 |  0.14 | DISABLED | [0.29, 0.56, 0.01]
    86 | [-2.08,  0.52, 1.49]    | [ 1.41,  1.77, -0.00]   |  2.26 |  0.10 | DISABLED | [0.47, 0.59, -0.00]
    87 | [-1.98,  0.59, 1.49]    | [ 2.46,  1.55, -0.02]   |  2.90 |  0.12 | DISABLED | [0.82, 0.52, -0.01]
  ```

### [Seed 1033] Configuration: Baseline (Shield OFF) — Outcome: `OBSTACLE_COLLISION`
- **Steps:** 73 | **Reward:** -85.1 | **Min Clearance:** 0.101 m
- **Diagnostic Cause:** Obstacle collision at speed 2.79 m/s (min clearance 0.12m).
- **Last 5 Control Steps Telemetry:**
  ```
  Step | Pos [x, y, z]           | Vel [vx, vy, vz]        | Speed | Clr   | State    | Action Executed
  -----+-------------------------+-------------------------+-------+-------+----------+----------------
    69 | [ 1.22, -1.53, 1.50]    | [ 2.13,  1.04, 0.03]    |  2.37 |  0.15 | DISABLED | [0.71, 0.35, 0.01]
    70 | [ 1.21, -1.48, 1.50]    | [-0.20,  1.18, -0.05]   |  1.20 |  0.12 | DISABLED | [-0.07, 0.40, -0.02]
    71 | [ 1.16, -1.44, 1.49]    | [-1.35,  1.15, -0.03]   |  1.77 |  0.15 | DISABLED | [-0.45, 0.38, -0.01]
    72 | [ 1.25, -1.39, 1.49]    | [ 2.12,  1.06, -0.07]   |  2.37 |  0.14 | DISABLED | [0.71, 0.35, -0.02]
    73 | [ 1.35, -1.34, 1.49]    | [ 2.49,  1.26, -0.04]   |  2.79 |  0.12 | DISABLED | [0.83, 0.42, -0.01]
  ```

### [Seed 1034] Configuration: Baseline (Shield OFF) — Outcome: `OBSTACLE_COLLISION`
- **Steps:** 43 | **Reward:** -2.76 | **Min Clearance:** 0.147 m
- **Diagnostic Cause:** Obstacle collision at speed 1.81 m/s (min clearance 0.15m).
- **Last 5 Control Steps Telemetry:**
  ```
  Step | Pos [x, y, z]           | Vel [vx, vy, vz]        | Speed | Clr   | State    | Action Executed
  -----+-------------------------+-------------------------+-------+-------+----------+----------------
    39 | [ 0.84, -3.80, 1.50]    | [ 1.69,  1.68, 0.01]    |  2.38 |  0.40 | DISABLED | [0.56, 0.56, 0.00]
    40 | [ 0.93, -3.74, 1.50]    | [ 1.92,  1.54, -0.00]   |  2.46 |  0.33 | DISABLED | [0.64, 0.51, -0.00]
    41 | [ 0.90, -3.66, 1.51]    | [-0.67,  1.81, 0.05]    |  1.93 |  0.35 | DISABLED | [-0.22, 0.60, 0.02]
    42 | [ 0.87, -3.59, 1.50]    | [-0.59,  1.76, -0.04]   |  1.86 |  0.27 | DISABLED | [-0.20, 0.59, -0.01]
    43 | [ 0.85, -3.52, 1.50]    | [-0.61,  1.71, -0.02]   |  1.81 |  0.15 | DISABLED | [-0.20, 0.57, -0.01]
  ```

### [Seed 1035] Configuration: Baseline (Shield OFF) — Outcome: `OBSTACLE_COLLISION`
- **Steps:** 43 | **Reward:** 73.31 | **Min Clearance:** 0.221 m
- **Diagnostic Cause:** Obstacle collision at speed 2.68 m/s (min clearance 0.22m).
- **Last 5 Control Steps Telemetry:**
  ```
  Step | Pos [x, y, z]           | Vel [vx, vy, vz]        | Speed | Clr   | State    | Action Executed
  -----+-------------------------+-------------------------+-------+-------+----------+----------------
    39 | [-0.54, -3.31, 1.50]    | [-0.74,  2.82, 0.02]    |  2.91 |  0.29 | DISABLED | [-0.25, 0.94, 0.01]
    40 | [-0.58, -3.19, 1.50]    | [-1.07,  2.77, 0.01]    |  2.97 |  0.32 | DISABLED | [-0.36, 0.92, 0.01]
    41 | [-0.63, -3.08, 1.50]    | [-1.11,  2.70, 0.01]    |  2.92 |  0.30 | DISABLED | [-0.37, 0.90, 0.01]
    42 | [-0.69, -2.97, 1.50]    | [-1.38,  2.68, 0.01]    |  3.02 |  0.25 | DISABLED | [-0.46, 0.89, 0.00]
    43 | [-0.71, -2.86, 1.50]    | [-0.50,  2.63, 0.02]    |  2.68 |  0.22 | DISABLED | [-0.17, 0.88, 0.01]
  ```

### [Seed 1036] Configuration: Baseline (Shield OFF) — Outcome: `OBSTACLE_COLLISION`
- **Steps:** 54 | **Reward:** -56.53 | **Min Clearance:** 0.123 m
- **Diagnostic Cause:** Obstacle collision at speed 2.26 m/s (min clearance 0.12m).
- **Last 5 Control Steps Telemetry:**
  ```
  Step | Pos [x, y, z]           | Vel [vx, vy, vz]        | Speed | Clr   | State    | Action Executed
  -----+-------------------------+-------------------------+-------+-------+----------+----------------
    50 | [ 0.50, -2.93, 1.51]    | [-1.47,  2.12, -0.01]   |  2.58 |  0.14 | DISABLED | [-0.49, 0.71, -0.00]
    51 | [ 0.41, -2.83, 1.51]    | [-2.06,  2.21, 0.02]    |  3.02 |  0.14 | DISABLED | [-0.69, 0.74, 0.01]
    52 | [ 0.53, -2.75, 1.51]    | [ 2.73,  2.05, 0.00]    |  3.41 |  0.14 | DISABLED | [0.91, 0.68, 0.00]
    53 | [ 0.57, -2.66, 1.51]    | [ 1.08,  2.14, -0.01]   |  2.40 |  0.13 | DISABLED | [0.36, 0.71, -0.00]
    54 | [ 0.59, -2.57, 1.51]    | [ 0.46,  2.22, -0.01]   |  2.26 |  0.12 | DISABLED | [0.15, 0.74, -0.00]
  ```

### [Seed 1037] Configuration: Baseline (Shield OFF) — Outcome: `OBSTACLE_COLLISION`
- **Steps:** 47 | **Reward:** 65.01 | **Min Clearance:** 0.457 m
- **Diagnostic Cause:** Obstacle collision at speed 1.52 m/s (min clearance 0.46m).
- **Last 5 Control Steps Telemetry:**
  ```
  Step | Pos [x, y, z]           | Vel [vx, vy, vz]        | Speed | Clr   | State    | Action Executed
  -----+-------------------------+-------------------------+-------+-------+----------+----------------
    43 | [ 0.25, -4.10, 1.48]    | [ 0.41,  1.22, 0.01]    |  1.28 |  0.61 | DISABLED | [0.14, 0.41, 0.00]
    44 | [ 0.21, -4.06, 1.48]    | [-1.02,  1.01, -0.00]   |  1.44 |  0.58 | DISABLED | [-0.34, 0.34, -0.00]
    45 | [ 0.21, -4.01, 1.48]    | [ 0.15,  1.15, -0.06]   |  1.16 |  0.54 | DISABLED | [0.05, 0.38, -0.02]
    46 | [ 0.16, -3.97, 1.48]    | [-1.33,  0.96, 0.00]    |  1.65 |  0.49 | DISABLED | [-0.45, 0.32, 0.00]
    47 | [ 0.20, -3.93, 1.48]    | [ 1.08,  1.06, -0.01]   |  1.52 |  0.46 | DISABLED | [0.36, 0.35, -0.00]
  ```

### [Seed 1038] Configuration: Baseline (Shield OFF) — Outcome: `OBSTACLE_COLLISION`
- **Steps:** 67 | **Reward:** -113.09 | **Min Clearance:** 0.094 m
- **Diagnostic Cause:** Obstacle collision at speed 1.39 m/s (min clearance 0.11m).
- **Last 5 Control Steps Telemetry:**
  ```
  Step | Pos [x, y, z]           | Vel [vx, vy, vz]        | Speed | Clr   | State    | Action Executed
  -----+-------------------------+-------------------------+-------+-------+----------+----------------
    63 | [ 1.50, -1.94, 1.50]    | [ 1.31,  1.20, -0.01]   |  1.78 |  0.13 | DISABLED | [0.44, 0.40, -0.00]
    64 | [ 1.55, -1.89, 1.50]    | [ 1.32,  1.21, 0.06]    |  1.79 |  0.14 | DISABLED | [0.44, 0.40, 0.02]
    65 | [ 1.63, -1.83, 1.50]    | [ 1.76,  1.21, 0.04]    |  2.14 |  0.09 | DISABLED | [0.59, 0.40, 0.01]
    66 | [ 1.63, -1.79, 1.50]    | [ 0.17,  1.17, 0.01]    |  1.18 |  0.13 | DISABLED | [0.06, 0.39, 0.00]
    67 | [ 1.67, -1.74, 1.50]    | [ 0.84,  1.10, -0.00]   |  1.39 |  0.11 | DISABLED | [0.28, 0.37, -0.00]
  ```

### [Seed 1039] Configuration: Baseline (Shield OFF) — Outcome: `OBSTACLE_COLLISION`
- **Steps:** 114 | **Reward:** -396.2 | **Min Clearance:** 0.113 m
- **Diagnostic Cause:** Obstacle collision at speed 2.57 m/s (min clearance 0.14m).
- **Last 5 Control Steps Telemetry:**
  ```
  Step | Pos [x, y, z]           | Vel [vx, vy, vz]        | Speed | Clr   | State    | Action Executed
  -----+-------------------------+-------------------------+-------+-------+----------+----------------
   110 | [ 0.77,  1.49, 1.50]    | [-0.57,  1.23, -0.00]   |  1.36 |  0.14 | DISABLED | [-0.19, 0.41, -0.00]
   111 | [ 0.85,  1.55, 1.50]    | [ 1.77,  1.40, -0.03]   |  2.26 |  0.13 | DISABLED | [0.59, 0.47, -0.01]
   112 | [ 0.95,  1.61, 1.49]    | [ 2.59,  1.35, -0.02]   |  2.92 |  0.13 | DISABLED | [0.86, 0.45, -0.01]
   113 | [ 0.91,  1.67, 1.49]    | [-1.15,  1.39, -0.00]   |  1.80 |  0.15 | DISABLED | [-0.38, 0.46, -0.00]
   114 | [ 0.82,  1.72, 1.49]    | [-2.17,  1.37, 0.01]    |  2.57 |  0.14 | DISABLED | [-0.72, 0.46, 0.00]
  ```

### [Seed 1041] Configuration: Baseline (Shield OFF) — Outcome: `OBSTACLE_COLLISION`
- **Steps:** 52 | **Reward:** 28.31 | **Min Clearance:** 0.127 m
- **Diagnostic Cause:** Obstacle collision at speed 1.30 m/s (min clearance 0.17m).
- **Last 5 Control Steps Telemetry:**
  ```
  Step | Pos [x, y, z]           | Vel [vx, vy, vz]        | Speed | Clr   | State    | Action Executed
  -----+-------------------------+-------------------------+-------+-------+----------+----------------
    48 | [ 0.30, -2.89, 1.49]    | [ 1.57,  1.32, 0.02]    |  2.05 |  0.14 | DISABLED | [0.52, 0.44, 0.01]
    49 | [ 0.40, -2.84, 1.49]    | [ 2.22,  1.28, -0.03]   |  2.57 |  0.14 | DISABLED | [0.74, 0.43, -0.01]
    50 | [ 0.41, -2.79, 1.49]    | [ 0.36,  1.25, -0.00]   |  1.30 |  0.13 | DISABLED | [0.12, 0.41, -0.00]
    51 | [ 0.41, -2.74, 1.49]    | [-0.11,  1.10, -0.01]   |  1.11 |  0.13 | DISABLED | [-0.04, 0.37, -0.01]
    52 | [ 0.44, -2.70, 1.49]    | [ 0.87,  0.97, -0.01]   |  1.30 |  0.17 | DISABLED | [0.29, 0.32, -0.00]
  ```

### [Seed 1042] Configuration: Baseline (Shield OFF) — Outcome: `OBSTACLE_COLLISION`
- **Steps:** 38 | **Reward:** 20.71 | **Min Clearance:** 0.144 m
- **Diagnostic Cause:** Obstacle collision at speed 3.11 m/s (min clearance 0.14m).
- **Last 5 Control Steps Telemetry:**
  ```
  Step | Pos [x, y, z]           | Vel [vx, vy, vz]        | Speed | Clr   | State    | Action Executed
  -----+-------------------------+-------------------------+-------+-------+----------+----------------
    34 | [ 0.15, -4.07, 1.50]    | [-2.83,  2.31, 0.00]    |  3.65 |  0.57 | DISABLED | [-0.94, 0.77, 0.00]
    35 | [ 0.03, -3.97, 1.50]    | [-2.86,  2.29, -0.01]   |  3.67 |  0.54 | DISABLED | [-0.95, 0.76, -0.00]
    36 | [ 0.13, -3.88, 1.50]    | [ 2.47,  2.19, 0.06]    |  3.30 |  0.40 | DISABLED | [0.82, 0.73, 0.02]
    37 | [ 0.25, -3.78, 1.50]    | [ 2.84,  2.35, -0.04]   |  3.68 |  0.26 | DISABLED | [0.95, 0.78, -0.01]
    38 | [ 0.34, -3.69, 1.50]    | [ 2.14,  2.25, -0.01]   |  3.11 |  0.14 | DISABLED | [0.71, 0.75, -0.00]
  ```

### [Seed 1043] Configuration: Baseline (Shield OFF) — Outcome: `OBSTACLE_COLLISION`
- **Steps:** 53 | **Reward:** 9.47 | **Min Clearance:** 0.123 m
- **Diagnostic Cause:** Obstacle collision at speed 3.59 m/s (min clearance 0.14m).
- **Last 5 Control Steps Telemetry:**
  ```
  Step | Pos [x, y, z]           | Vel [vx, vy, vz]        | Speed | Clr   | State    | Action Executed
  -----+-------------------------+-------------------------+-------+-------+----------+----------------
    49 | [-0.49, -2.35, 1.50]    | [-2.84,  2.10, -0.11]   |  3.53 |  0.16 | DISABLED | [-0.95, 0.70, -0.04]
    50 | [-0.36, -2.28, 1.51]    | [ 2.98,  1.86, 0.05]    |  3.52 |  0.16 | DISABLED | [0.99, 0.62, 0.02]
    51 | [-0.26, -2.20, 1.51]    | [ 2.52,  1.89, 0.01]    |  3.14 |  0.15 | DISABLED | [0.84, 0.63, 0.00]
    52 | [-0.34, -2.11, 1.51]    | [-1.87,  2.06, -0.00]   |  2.78 |  0.14 | DISABLED | [-0.62, 0.69, -0.00]
    53 | [-0.21, -2.03, 1.50]    | [ 2.96,  2.04, -0.02]   |  3.59 |  0.14 | DISABLED | [0.98, 0.68, -0.01]
  ```

### [Seed 1044] Configuration: Baseline (Shield OFF) — Outcome: `OBSTACLE_COLLISION`
- **Steps:** 64 | **Reward:** -80.04 | **Min Clearance:** 0.104 m
- **Diagnostic Cause:** Obstacle collision at speed 2.14 m/s (min clearance 0.10m).
- **Last 5 Control Steps Telemetry:**
  ```
  Step | Pos [x, y, z]           | Vel [vx, vy, vz]        | Speed | Clr   | State    | Action Executed
  -----+-------------------------+-------------------------+-------+-------+----------+----------------
    60 | [-1.23, -1.68, 1.51]    | [-1.92,  1.54, -0.03]   |  2.46 |  0.15 | DISABLED | [-0.64, 0.51, -0.01]
    61 | [-1.34, -1.60, 1.51]    | [-2.80,  1.76, -0.01]   |  3.31 |  0.15 | DISABLED | [-0.93, 0.59, -0.00]
    62 | [-1.42, -1.53, 1.51]    | [-1.84,  1.75, 0.02]    |  2.54 |  0.14 | DISABLED | [-0.61, 0.58, 0.01]
    63 | [-1.42, -1.45, 1.51]    | [-0.01,  1.90, -0.01]   |  1.90 |  0.17 | DISABLED | [-0.00, 0.63, -0.00]
    64 | [-1.44, -1.37, 1.51]    | [-0.51,  2.07, -0.04]   |  2.14 |  0.10 | DISABLED | [-0.17, 0.69, -0.01]
  ```

### [Seed 1045] Configuration: Baseline (Shield OFF) — Outcome: `OBSTACLE_COLLISION`
- **Steps:** 32 | **Reward:** -2.83 | **Min Clearance:** 0.247 m
- **Diagnostic Cause:** Obstacle collision at speed 2.64 m/s (min clearance 0.25m).
- **Last 5 Control Steps Telemetry:**
  ```
  Step | Pos [x, y, z]           | Vel [vx, vy, vz]        | Speed | Clr   | State    | Action Executed
  -----+-------------------------+-------------------------+-------+-------+----------+----------------
    28 | [ 0.80, -4.76, 1.50]    | [ 0.47,  2.66, -0.02]   |  2.70 |  0.59 | DISABLED | [0.16, 0.89, -0.01]
    29 | [ 0.74, -4.65, 1.50]    | [-1.41,  2.73, 0.03]    |  3.08 |  0.51 | DISABLED | [-0.47, 0.91, 0.01]
    30 | [ 0.64, -4.55, 1.50]    | [-2.22,  2.45, -0.05]   |  3.31 |  0.47 | DISABLED | [-0.74, 0.82, -0.02]
    31 | [ 0.70, -4.46, 1.50]    | [ 1.31,  2.11, -0.04]   |  2.49 |  0.36 | DISABLED | [0.44, 0.70, -0.01]
    32 | [ 0.74, -4.36, 1.50]    | [ 1.12,  2.39, -0.06]   |  2.64 |  0.25 | DISABLED | [0.37, 0.80, -0.02]
  ```

### [Seed 1046] Configuration: Baseline (Shield OFF) — Outcome: `OBSTACLE_COLLISION`
- **Steps:** 59 | **Reward:** -59.01 | **Min Clearance:** 0.036 m
- **Diagnostic Cause:** Obstacle collision at speed 3.20 m/s (min clearance 0.04m).
- **Last 5 Control Steps Telemetry:**
  ```
  Step | Pos [x, y, z]           | Vel [vx, vy, vz]        | Speed | Clr   | State    | Action Executed
  -----+-------------------------+-------------------------+-------+-------+----------+----------------
    55 | [-1.54, -2.90, 1.51]    | [ 0.40,  1.56, -0.01]   |  1.61 |  0.37 | DISABLED | [0.13, 0.52, -0.00]
    56 | [-1.50, -2.83, 1.51]    | [ 1.15,  1.49, -0.05]   |  1.88 |  0.37 | DISABLED | [0.38, 0.50, -0.02]
    57 | [-1.59, -2.77, 1.51]    | [-2.21,  1.47, 0.02]    |  2.66 |  0.42 | DISABLED | [-0.74, 0.49, 0.01]
    58 | [-1.48, -2.71, 1.51]    | [ 2.53,  1.56, -0.04]   |  2.97 |  0.29 | DISABLED | [0.84, 0.52, -0.01]
    59 | [-1.37, -2.64, 1.51]    | [ 2.76,  1.61, -0.03]   |  3.20 |  0.04 | DISABLED | [0.92, 0.54, -0.01]
  ```

### [Seed 1047] Configuration: Baseline (Shield OFF) — Outcome: `OBSTACLE_COLLISION`
- **Steps:** 27 | **Reward:** 13.5 | **Min Clearance:** 0.298 m
- **Diagnostic Cause:** Obstacle collision at speed 2.88 m/s (min clearance 0.30m).
- **Last 5 Control Steps Telemetry:**
  ```
  Step | Pos [x, y, z]           | Vel [vx, vy, vz]        | Speed | Clr   | State    | Action Executed
  -----+-------------------------+-------------------------+-------+-------+----------+----------------
    23 | [ 0.41, -5.29, 1.50]    | [ 1.20,  2.76, -0.01]   |  3.01 |  0.79 | DISABLED | [0.40, 0.92, -0.00]
    24 | [ 0.36, -5.17, 1.50]    | [-1.07,  2.82, -0.01]   |  3.02 |  0.64 | DISABLED | [-0.36, 0.94, -0.00]
    25 | [ 0.36, -5.06, 1.50]    | [ 0.06,  2.67, -0.04]   |  2.67 |  0.55 | DISABLED | [0.02, 0.89, -0.01]
    26 | [ 0.35, -4.94, 1.49]    | [-0.21,  2.85, -0.02]   |  2.86 |  0.43 | DISABLED | [-0.07, 0.95, -0.01]
    27 | [ 0.33, -4.82, 1.49]    | [-0.58,  2.82, -0.01]   |  2.88 |  0.30 | DISABLED | [-0.19, 0.94, -0.00]
  ```

### [Seed 1048] Configuration: Baseline (Shield OFF) — Outcome: `OBSTACLE_COLLISION`
- **Steps:** 38 | **Reward:** 18.21 | **Min Clearance:** 0.405 m
- **Diagnostic Cause:** Obstacle collision at speed 2.74 m/s (min clearance 0.57m).
- **Last 5 Control Steps Telemetry:**
  ```
  Step | Pos [x, y, z]           | Vel [vx, vy, vz]        | Speed | Clr   | State    | Action Executed
  -----+-------------------------+-------------------------+-------+-------+----------+----------------
    34 | [-0.18, -4.25, 1.49]    | [-0.10,  2.61, -0.02]   |  2.61 |  0.48 | DISABLED | [-0.03, 0.87, -0.01]
    35 | [-0.21, -4.14, 1.49]    | [-0.56,  2.75, 0.01]    |  2.80 |  0.46 | DISABLED | [-0.19, 0.92, 0.01]
    36 | [-0.19, -4.03, 1.49]    | [ 0.46,  2.73, -0.01]   |  2.77 |  0.41 | DISABLED | [0.15, 0.91, -0.01]
    37 | [-0.23, -3.92, 1.49]    | [-1.03,  2.66, 0.02]    |  2.85 |  0.56 | DISABLED | [-0.34, 0.89, 0.01]
    38 | [-0.21, -3.80, 1.49]    | [ 0.46,  2.70, -0.01]   |  2.74 |  0.57 | DISABLED | [0.15, 0.90, -0.00]
  ```

### [Seed 1049] Configuration: Baseline (Shield OFF) — Outcome: `OBSTACLE_COLLISION`
- **Steps:** 59 | **Reward:** -49.71 | **Min Clearance:** 0.123 m
- **Diagnostic Cause:** Obstacle collision at speed 2.97 m/s (min clearance 0.15m).
- **Last 5 Control Steps Telemetry:**
  ```
  Step | Pos [x, y, z]           | Vel [vx, vy, vz]        | Speed | Clr   | State    | Action Executed
  -----+-------------------------+-------------------------+-------+-------+----------+----------------
    55 | [ 0.16, -2.04, 1.49]    | [-2.84,  1.65, -0.01]   |  3.28 |  0.15 | DISABLED | [-0.95, 0.55, -0.00]
    56 | [ 0.03, -1.96, 1.49]    | [-3.00,  2.12, -0.04]   |  3.67 |  0.14 | DISABLED | [-1.00, 0.71, -0.01]
    57 | [ 0.11, -1.86, 1.49]    | [ 1.81,  2.19, -0.01]   |  2.84 |  0.17 | DISABLED | [0.60, 0.73, -0.00]
    58 | [ 0.23, -1.78, 1.48]    | [ 2.80,  2.15, -0.04]   |  3.53 |  0.14 | DISABLED | [0.93, 0.71, -0.01]
    59 | [ 0.13, -1.70, 1.48]    | [-2.27,  1.91, -0.01]   |  2.97 |  0.15 | DISABLED | [-0.76, 0.64, -0.00]
  ```

### [Seed 1006] Configuration: Shield ON (Oracle) — Outcome: `TIMEOUT`
- **Steps:** 500 | **Reward:** -1110.09 | **Min Clearance:** 0.348 m
- **Diagnostic Cause:** Exceeded maximum episode limit (500 steps) without reaching goal.
- **Last 5 Control Steps Telemetry:**
  ```
  Step | Pos [x, y, z]           | Vel [vx, vy, vz]        | Speed | Clr   | State    | Action Executed
  -----+-------------------------+-------------------------+-------+-------+----------+----------------
   496 | [ 0.20,  9.05, 1.50]    | [ 1.50,  0.00, -0.00]   |  1.50 |  0.69 | REROUTE  | [0.50, 0.00, -0.00]
   497 | [ 0.27,  9.05, 1.50]    | [ 1.50,  0.00, -0.00]   |  1.50 |  0.69 | REROUTE  | [0.50, 0.00, -0.00]
   498 | [ 0.33,  9.05, 1.50]    | [ 1.50,  0.00, -0.00]   |  1.50 |  0.69 | REROUTE  | [0.50, 0.00, -0.00]
   499 | [ 0.39,  9.05, 1.50]    | [ 1.50,  0.00, -0.00]   |  1.50 |  0.69 | REROUTE  | [0.50, 0.00, -0.00]
   500 | [ 0.45,  9.05, 1.50]    | [ 1.50,  0.00, -0.00]   |  1.50 |  0.69 | REROUTE  | [0.50, 0.00, -0.00]
  ```

### [Seed 1009] Configuration: Shield ON (Oracle) — Outcome: `TIMEOUT`
- **Steps:** 500 | **Reward:** -1022.34 | **Min Clearance:** 0.202 m
- **Diagnostic Cause:** Exceeded maximum episode limit (500 steps) without reaching goal.
- **Last 5 Control Steps Telemetry:**
  ```
  Step | Pos [x, y, z]           | Vel [vx, vy, vz]        | Speed | Clr   | State    | Action Executed
  -----+-------------------------+-------------------------+-------+-------+----------+----------------
   496 | [ 0.29,  9.07, 1.50]    | [ 1.50,  0.00, 0.00]    |  1.50 |  0.67 | REROUTE  | [0.50, 0.00, 0.00]
   497 | [ 0.35,  9.07, 1.50]    | [ 1.50,  0.00, 0.00]    |  1.50 |  0.67 | REROUTE  | [0.50, 0.00, 0.00]
   498 | [ 0.41,  9.07, 1.50]    | [ 1.50,  0.00, 0.00]    |  1.50 |  0.67 | REROUTE  | [0.50, 0.00, 0.00]
   499 | [ 0.48,  9.07, 1.50]    | [ 1.50,  0.00, 0.00]    |  1.50 |  0.67 | REROUTE  | [0.50, 0.00, 0.00]
   500 | [ 0.54,  9.07, 1.50]    | [ 1.50,  0.00, 0.00]    |  1.50 |  0.67 | REROUTE  | [0.50, 0.00, 0.00]
  ```

### [Seed 1015] Configuration: Shield ON (Oracle) — Outcome: `TIMEOUT`
- **Steps:** 500 | **Reward:** -2349.81 | **Min Clearance:** 0.221 m
- **Diagnostic Cause:** Exceeded maximum episode limit (500 steps) without reaching goal.
- **Last 5 Control Steps Telemetry:**
  ```
  Step | Pos [x, y, z]           | Vel [vx, vy, vz]        | Speed | Clr   | State    | Action Executed
  -----+-------------------------+-------------------------+-------+-------+----------+----------------
   496 | [-0.36,  1.28, 1.50]    | [ 0.00,  0.00, 0.00]    |  0.00 |  0.46 | BRAKE    | [0.00, 0.00, 0.00]
   497 | [-0.36,  1.28, 1.50]    | [ 0.00,  0.00, 0.00]    |  0.00 |  0.48 | SCAN     | [0.00, 0.00, 0.00]
   498 | [-0.42,  1.34, 1.50]    | [-1.50,  1.50, -0.01]   |  2.12 |  0.48 | REROUTE  | [-0.50, 0.50, -0.00]
   499 | [-0.48,  1.41, 1.50]    | [-1.50,  1.60, -0.01]   |  2.19 |  0.34 | REROUTE  | [-0.50, 0.53, -0.00]
   500 | [-0.42,  1.47, 1.50]    | [ 1.50,  1.50, -0.01]   |  2.12 |  0.25 | REROUTE  | [0.50, 0.50, -0.00]
  ```

### [Seed 1022] Configuration: Shield ON (Oracle) — Outcome: `TIMEOUT`
- **Steps:** 500 | **Reward:** -2381.19 | **Min Clearance:** 0.123 m
- **Diagnostic Cause:** Exceeded maximum episode limit (500 steps) without reaching goal.
- **Last 5 Control Steps Telemetry:**
  ```
  Step | Pos [x, y, z]           | Vel [vx, vy, vz]        | Speed | Clr   | State    | Action Executed
  -----+-------------------------+-------------------------+-------+-------+----------+----------------
   496 | [ 0.18,  1.63, 1.50]    | [ 0.00, -0.80, -0.00]   |  0.80 |  1.05 | SCAN     | [0.00, -0.27, -0.00]
   497 | [ 0.24,  1.69, 1.50]    | [ 1.50,  1.50, -0.00]   |  2.12 |  1.05 | REROUTE  | [0.50, 0.50, -0.00]
   498 | [ 0.30,  1.76, 1.50]    | [ 1.50,  1.60, -0.00]   |  2.19 |  0.47 | REROUTE  | [0.50, 0.53, -0.00]
   499 | [ 0.36,  1.82, 1.50]    | [ 1.50,  1.60, -0.00]   |  2.19 |  0.38 | REROUTE  | [0.50, 0.53, -0.00]
   500 | [ 0.36,  1.79, 1.50]    | [ 0.00, -0.80, -0.00]   |  0.80 |  0.29 | RETREAT  | [0.00, -0.27, -0.00]
  ```

### [Seed 1026] Configuration: Shield ON (Oracle) — Outcome: `TIMEOUT`
- **Steps:** 500 | **Reward:** -2600.0 | **Min Clearance:** 0.048 m
- **Diagnostic Cause:** Exceeded maximum episode limit (500 steps) without reaching goal.
- **Last 5 Control Steps Telemetry:**
  ```
  Step | Pos [x, y, z]           | Vel [vx, vy, vz]        | Speed | Clr   | State    | Action Executed
  -----+-------------------------+-------------------------+-------+-------+----------+----------------
   496 | [-2.04,  1.42, 1.49]    | [ 0.90,  2.32, -0.02]   |  2.49 |  1.13 | NOMINAL  | [0.30, 0.77, -0.01]
   497 | [-1.97,  1.49, 1.49]    | [ 1.74,  1.64, 0.02]    |  2.39 |  1.04 | NOMINAL  | [0.58, 0.55, 0.01]
   498 | [-1.89,  1.54, 1.49]    | [ 1.91,  1.35, 0.02]    |  2.34 |  1.01 | NOMINAL  | [0.64, 0.45, 0.01]
   499 | [-1.86,  1.60, 1.50]    | [ 0.58,  1.33, 0.02]    |  1.45 |  0.63 | NOMINAL  | [0.19, 0.44, 0.01]
   500 | [-1.86,  1.65, 1.49]    | [ 0.01,  1.20, -0.02]   |  1.20 |  0.86 | NOMINAL  | [0.00, 0.40, -0.01]
  ```

### [Seed 1029] Configuration: Shield ON (Oracle) — Outcome: `TIMEOUT`
- **Steps:** 500 | **Reward:** -1261.9 | **Min Clearance:** 0.14 m
- **Diagnostic Cause:** Exceeded maximum episode limit (500 steps) without reaching goal.
- **Last 5 Control Steps Telemetry:**
  ```
  Step | Pos [x, y, z]           | Vel [vx, vy, vz]        | Speed | Clr   | State    | Action Executed
  -----+-------------------------+-------------------------+-------+-------+----------+----------------
   496 | [ 1.44,  8.92, 1.50]    | [-1.50,  0.40, -0.00]   |  1.55 |  0.71 | REROUTE  | [-0.50, 0.13, -0.00]
   497 | [ 1.38,  8.93, 1.50]    | [-1.50,  0.40, -0.00]   |  1.55 |  0.69 | REROUTE  | [-0.50, 0.13, -0.00]
   498 | [ 1.32,  8.95, 1.50]    | [-1.50,  0.40, -0.00]   |  1.55 |  0.66 | REROUTE  | [-0.50, 0.13, -0.00]
   499 | [ 1.26,  8.97, 1.50]    | [-1.50,  0.40, -0.00]   |  1.55 |  0.64 | REROUTE  | [-0.50, 0.13, -0.00]
   500 | [ 1.19,  8.98, 1.50]    | [-1.50,  0.40, -0.00]   |  1.55 |  0.61 | REROUTE  | [-0.50, 0.13, -0.00]
  ```

### [Seed 1032] Configuration: Shield ON (Oracle) — Outcome: `TIMEOUT`
- **Steps:** 500 | **Reward:** -1439.13 | **Min Clearance:** 0.058 m
- **Diagnostic Cause:** Exceeded maximum episode limit (500 steps) without reaching goal.
- **Last 5 Control Steps Telemetry:**
  ```
  Step | Pos [x, y, z]           | Vel [vx, vy, vz]        | Speed | Clr   | State    | Action Executed
  -----+-------------------------+-------------------------+-------+-------+----------+----------------
   496 | [ 1.70,  9.05, 1.50]    | [ 1.50,  0.00, -0.00]   |  1.50 |  0.69 | REROUTE  | [0.50, 0.00, -0.00]
   497 | [ 1.77,  9.05, 1.50]    | [ 1.50,  0.00, -0.00]   |  1.50 |  0.69 | REROUTE  | [0.50, 0.00, -0.00]
   498 | [ 1.83,  9.05, 1.50]    | [ 1.50,  0.00, -0.00]   |  1.50 |  0.69 | REROUTE  | [0.50, 0.00, -0.00]
   499 | [ 1.89,  9.05, 1.50]    | [ 1.50,  0.00, -0.00]   |  1.50 |  0.69 | REROUTE  | [0.50, 0.00, -0.00]
   500 | [ 1.95,  9.05, 1.50]    | [ 1.50,  0.00, -0.00]   |  1.50 |  0.69 | REROUTE  | [0.50, 0.00, -0.00]
  ```

### [Seed 1034] Configuration: Shield ON (Oracle) — Outcome: `TIMEOUT`
- **Steps:** 500 | **Reward:** -1624.24 | **Min Clearance:** 0.105 m
- **Diagnostic Cause:** Exceeded maximum episode limit (500 steps) without reaching goal.
- **Last 5 Control Steps Telemetry:**
  ```
  Step | Pos [x, y, z]           | Vel [vx, vy, vz]        | Speed | Clr   | State    | Action Executed
  -----+-------------------------+-------------------------+-------+-------+----------+----------------
   496 | [ 2.40, -3.27, 1.50]    | [-1.50,  1.60, -0.00]   |  2.19 |  0.55 | REROUTE  | [-0.50, 0.53, -0.00]
   497 | [ 2.37, -3.26, 1.50]    | [-0.65,  0.31, -0.04]   |  0.72 |  0.46 | NOMINAL  | [-0.21, 0.10, -0.01]
   498 | [ 2.37, -3.24, 1.50]    | [ 0.06,  0.51, 0.03]    |  0.51 |  0.43 | NOMINAL  | [0.02, 0.17, 0.01]
   499 | [ 2.40, -3.20, 1.50]    | [ 0.58,  0.84, 0.05]    |  1.02 |  0.52 | NOMINAL  | [0.19, 0.28, 0.02]
   500 | [ 2.40, -3.20, 1.50]    | [ 0.00,  0.00, 0.00]    |  0.00 |  0.44 | BRAKE    | [0.00, 0.00, 0.00]
  ```

### [Seed 1039] Configuration: Shield ON (Oracle) — Outcome: `TIMEOUT`
- **Steps:** 500 | **Reward:** -1169.13 | **Min Clearance:** 0.238 m
- **Diagnostic Cause:** Exceeded maximum episode limit (500 steps) without reaching goal.
- **Last 5 Control Steps Telemetry:**
  ```
  Step | Pos [x, y, z]           | Vel [vx, vy, vz]        | Speed | Clr   | State    | Action Executed
  -----+-------------------------+-------------------------+-------+-------+----------+----------------
   496 | [-0.97,  9.06, 1.50]    | [-1.50,  0.00, 0.00]    |  1.50 |  0.69 | REROUTE  | [-0.50, 0.00, 0.00]
   497 | [-1.03,  9.06, 1.50]    | [-1.50,  0.00, 0.00]    |  1.50 |  0.69 | REROUTE  | [-0.50, 0.00, 0.00]
   498 | [-1.10,  9.06, 1.50]    | [-1.50,  0.00, 0.00]    |  1.50 |  0.69 | REROUTE  | [-0.50, 0.00, 0.00]
   499 | [-1.10,  9.02, 1.50]    | [ 0.00, -0.80, 0.00]    |  0.80 |  0.69 | RETREAT  | [0.00, -0.27, 0.00]
   500 | [-1.10,  8.99, 1.50]    | [ 0.00, -0.80, 0.00]    |  0.80 |  4.80 | RETREAT  | [0.00, -0.27, 0.00]
  ```

### [Seed 1041] Configuration: Shield ON (Oracle) — Outcome: `TIMEOUT`
- **Steps:** 500 | **Reward:** -1007.8 | **Min Clearance:** 0.289 m
- **Diagnostic Cause:** Exceeded maximum episode limit (500 steps) without reaching goal.
- **Last 5 Control Steps Telemetry:**
  ```
  Step | Pos [x, y, z]           | Vel [vx, vy, vz]        | Speed | Clr   | State    | Action Executed
  -----+-------------------------+-------------------------+-------+-------+----------+----------------
   496 | [-1.00,  9.03, 1.50]    | [ 0.00, -0.80, -0.00]   |  0.80 |  0.67 | RETREAT  | [0.00, -0.27, -0.00]
   497 | [-1.00,  9.00, 1.50]    | [ 0.00, -0.80, -0.00]   |  0.80 |  6.09 | RETREAT  | [0.00, -0.27, -0.00]
   498 | [-1.00,  8.97, 1.50]    | [ 0.00, -0.80, -0.00]   |  0.80 |  6.06 | RETREAT  | [0.00, -0.27, -0.00]
   499 | [-1.00,  8.93, 1.50]    | [ 0.00, -0.80, -0.00]   |  0.80 |  6.04 | RETREAT  | [0.00, -0.27, -0.00]
   500 | [-1.00,  8.90, 1.50]    | [ 0.00, -0.80, -0.00]   |  0.80 |  6.01 | RETREAT  | [0.00, -0.27, -0.00]
  ```

### [Seed 1042] Configuration: Shield ON (Oracle) — Outcome: `TIMEOUT`
- **Steps:** 500 | **Reward:** -1075.49 | **Min Clearance:** 0.249 m
- **Diagnostic Cause:** Exceeded maximum episode limit (500 steps) without reaching goal.
- **Last 5 Control Steps Telemetry:**
  ```
  Step | Pos [x, y, z]           | Vel [vx, vy, vz]        | Speed | Clr   | State    | Action Executed
  -----+-------------------------+-------------------------+-------+-------+----------+----------------
   496 | [ 0.50,  9.05, 1.50]    | [ 1.50,  0.00, 0.00]    |  1.50 |  0.69 | REROUTE  | [0.50, 0.00, 0.00]
   497 | [ 0.56,  9.05, 1.50]    | [ 1.50,  0.00, 0.00]    |  1.50 |  0.69 | REROUTE  | [0.50, 0.00, 0.00]
   498 | [ 0.62,  9.05, 1.50]    | [ 1.50,  0.00, 0.00]    |  1.50 |  0.69 | REROUTE  | [0.50, 0.00, 0.00]
   499 | [ 0.69,  9.05, 1.50]    | [ 1.50,  0.00, 0.00]    |  1.50 |  0.69 | REROUTE  | [0.50, 0.00, 0.00]
   500 | [ 0.75,  9.05, 1.50]    | [ 1.50,  0.00, 0.00]    |  1.50 |  0.69 | REROUTE  | [0.50, 0.00, 0.00]
  ```

### [Seed 1043] Configuration: Shield ON (Oracle) — Outcome: `TIMEOUT`
- **Steps:** 500 | **Reward:** -2562.55 | **Min Clearance:** 0.256 m
- **Diagnostic Cause:** Exceeded maximum episode limit (500 steps) without reaching goal.
- **Last 5 Control Steps Telemetry:**
  ```
  Step | Pos [x, y, z]           | Vel [vx, vy, vz]        | Speed | Clr   | State    | Action Executed
  -----+-------------------------+-------------------------+-------+-------+----------+----------------
   496 | [-1.97, -1.60, 1.50]    | [ 0.00,  0.00, 0.00]    |  0.00 |  0.40 | BRAKE    | [0.00, 0.00, 0.00]
   497 | [-1.97, -1.60, 1.50]    | [ 0.00,  0.00, 0.00]    |  0.00 |  0.48 | SCAN     | [0.00, 0.00, 0.00]
   498 | [-1.91, -1.54, 1.50]    | [ 1.50,  1.50, 0.01]    |  2.12 |  0.48 | REROUTE  | [0.50, 0.50, 0.00]
   499 | [-1.84, -1.47, 1.50]    | [ 1.50,  1.60, 0.01]    |  2.19 |  0.41 | REROUTE  | [0.50, 0.53, 0.00]
   500 | [-1.91, -1.41, 1.50]    | [-1.50,  1.50, 0.01]    |  2.12 |  0.34 | REROUTE  | [-0.50, 0.50, 0.00]
  ```

### [Seed 1044] Configuration: Shield ON (Oracle) — Outcome: `TIMEOUT`
- **Steps:** 500 | **Reward:** -2729.74 | **Min Clearance:** 0.078 m
- **Diagnostic Cause:** Exceeded maximum episode limit (500 steps) without reaching goal.
- **Last 5 Control Steps Telemetry:**
  ```
  Step | Pos [x, y, z]           | Vel [vx, vy, vz]        | Speed | Clr   | State    | Action Executed
  -----+-------------------------+-------------------------+-------+-------+----------+----------------
   496 | [-1.37, -2.10, 1.50]    | [ 0.00, -0.80, 0.00]    |  0.80 |  0.81 | RETREAT  | [0.00, -0.27, 0.00]
   497 | [-1.37, -2.14, 1.50]    | [ 0.00, -0.80, 0.00]    |  0.80 |  0.78 | RETREAT  | [0.00, -0.27, 0.00]
   498 | [-1.37, -2.17, 1.50]    | [ 0.00, -0.80, 0.00]    |  0.80 |  0.75 | RETREAT  | [0.00, -0.27, 0.00]
   499 | [-1.37, -2.20, 1.50]    | [ 0.00, -0.80, 0.00]    |  0.80 |  0.71 | SCAN     | [0.00, -0.27, 0.00]
   500 | [-1.44, -2.14, 1.50]    | [-1.50,  1.50, 0.00]    |  2.12 |  0.68 | REROUTE  | [-0.50, 0.50, 0.00]
  ```

### [Seed 1046] Configuration: Shield ON (Oracle) — Outcome: `TIMEOUT`
- **Steps:** 500 | **Reward:** -2206.56 | **Min Clearance:** 0.224 m
- **Diagnostic Cause:** Exceeded maximum episode limit (500 steps) without reaching goal.
- **Last 5 Control Steps Telemetry:**
  ```
  Step | Pos [x, y, z]           | Vel [vx, vy, vz]        | Speed | Clr   | State    | Action Executed
  -----+-------------------------+-------------------------+-------+-------+----------+----------------
   496 | [ 0.85,  2.36, 1.50]    | [ 0.00, -0.80, 0.00]    |  0.80 |  2.32 | RETREAT  | [0.00, -0.27, 0.00]
   497 | [ 0.85,  2.33, 1.50]    | [ 0.00, -0.80, 0.00]    |  0.80 |  2.29 | RETREAT  | [0.00, -0.27, 0.00]
   498 | [ 0.85,  2.29, 1.50]    | [ 0.00, -0.80, 0.00]    |  0.80 |  2.25 | RETREAT  | [0.00, -0.27, 0.00]
   499 | [ 0.85,  2.26, 1.50]    | [ 0.00, -0.80, 0.00]    |  0.80 |  2.21 | RETREAT  | [0.00, -0.27, 0.00]
   500 | [ 0.85,  2.23, 1.50]    | [ 0.00, -0.80, 0.00]    |  0.80 |  2.17 | RETREAT  | [0.00, -0.27, 0.00]
  ```

### [Seed 1048] Configuration: Shield ON (Oracle) — Outcome: `TIMEOUT`
- **Steps:** 500 | **Reward:** -985.48 | **Min Clearance:** 0.223 m
- **Diagnostic Cause:** Exceeded maximum episode limit (500 steps) without reaching goal.
- **Last 5 Control Steps Telemetry:**
  ```
  Step | Pos [x, y, z]           | Vel [vx, vy, vz]        | Speed | Clr   | State    | Action Executed
  -----+-------------------------+-------------------------+-------+-------+----------+----------------
   496 | [-1.06,  8.88, 1.50]    | [ 0.00, -0.80, -0.00]   |  0.80 |  6.68 | RETREAT  | [0.00, -0.27, -0.00]
   497 | [-1.06,  8.85, 1.50]    | [ 0.00, -0.80, -0.00]   |  0.80 |  6.68 | RETREAT  | [0.00, -0.27, -0.00]
   498 | [-1.06,  8.82, 1.50]    | [ 0.00, -0.80, -0.00]   |  0.80 |  6.68 | RETREAT  | [0.00, -0.27, -0.00]
   499 | [-1.06,  8.78, 1.50]    | [ 0.00, -0.80, -0.00]   |  0.80 |  6.68 | SCAN     | [0.00, -0.27, -0.00]
   500 | [-1.00,  8.78, 1.50]    | [ 1.50,  0.00, -0.00]   |  1.50 |  6.68 | REROUTE  | [0.50, 0.00, -0.00]
  ```

### [Seed 1000] Configuration: Shield ON (Camera) — Outcome: `TIMEOUT`
- **Steps:** 500 | **Reward:** -2399.28 | **Min Clearance:** 0.286 m
- **Diagnostic Cause:** Exceeded maximum episode limit (500 steps) without reaching goal.
- **Last 5 Control Steps Telemetry:**
  ```
  Step | Pos [x, y, z]           | Vel [vx, vy, vz]        | Speed | Clr   | State    | Action Executed
  -----+-------------------------+-------------------------+-------+-------+----------+----------------
   496 | [ 2.88, -0.92, 1.50]    | [ 1.50,  0.00, 0.00]    |  1.50 |  0.32 | REROUTE  | [0.50, 0.00, 0.00]
   497 | [ 2.94, -0.92, 1.50]    | [ 1.50,  0.00, 0.00]    |  1.50 |  0.32 | REROUTE  | [0.50, 0.00, 0.00]
   498 | [ 3.00, -0.92, 1.50]    | [ 1.50,  0.00, 0.00]    |  1.50 |  0.32 | REROUTE  | [0.50, 0.00, 0.00]
   499 | [ 3.06, -0.92, 1.50]    | [ 1.50,  0.00, 0.00]    |  1.50 |  0.31 | REROUTE  | [0.50, 0.00, 0.00]
   500 | [ 3.13, -0.92, 1.50]    | [ 1.50,  0.00, 0.00]    |  1.50 |  0.31 | REROUTE  | [0.50, 0.00, 0.00]
  ```

### [Seed 1001] Configuration: Shield ON (Camera) — Outcome: `OBSTACLE_COLLISION`
- **Steps:** 80 | **Reward:** -234.89 | **Min Clearance:** 0.346 m
- **Diagnostic Cause:** Obstacle collision at speed 2.21 m/s (min clearance 1.17m).
- **Last 5 Control Steps Telemetry:**
  ```
  Step | Pos [x, y, z]           | Vel [vx, vy, vz]        | Speed | Clr   | State    | Action Executed
  -----+-------------------------+-------------------------+-------+-------+----------+----------------
    76 | [ 0.57, -2.03, 1.50]    | [ 1.50,  1.60, 0.00]    |  2.19 |  1.38 | REROUTE  | [0.50, 0.53, 0.00]
    77 | [ 0.49, -1.96, 1.50]    | [-1.88,  1.72, 0.04]    |  2.55 |  1.38 | NOMINAL  | [-0.63, 0.57, 0.01]
    78 | [ 0.57, -1.91, 1.50]    | [ 1.95,  1.22, -0.05]   |  2.30 |  0.99 | NOMINAL  | [0.65, 0.41, -0.02]
    79 | [ 0.50, -1.82, 1.50]    | [-1.84,  2.08, -0.01]   |  2.77 |  1.25 | NOMINAL  | [-0.61, 0.69, -0.00]
    80 | [ 0.54, -1.74, 1.50]    | [ 0.99,  1.97, -0.02]   |  2.21 |  1.17 | NOMINAL  | [0.33, 0.66, -0.01]
  ```

### [Seed 1002] Configuration: Shield ON (Camera) — Outcome: `TIMEOUT`
- **Steps:** 500 | **Reward:** -2454.57 | **Min Clearance:** 0.25 m
- **Diagnostic Cause:** Exceeded maximum episode limit (500 steps) without reaching goal.
- **Last 5 Control Steps Telemetry:**
  ```
  Step | Pos [x, y, z]           | Vel [vx, vy, vz]        | Speed | Clr   | State    | Action Executed
  -----+-------------------------+-------------------------+-------+-------+----------+----------------
   496 | [-3.53, -1.18, 1.50]    | [ 0.00, -0.80, -0.00]   |  0.80 |  0.41 | RETREAT  | [0.00, -0.27, -0.00]
   497 | [-3.53, -1.21, 1.50]    | [ 0.00, -0.80, -0.00]   |  0.80 |  0.44 | SCAN     | [0.00, -0.27, -0.00]
   498 | [-3.47, -1.21, 1.50]    | [ 1.50,  0.00, -0.00]   |  1.50 |  0.48 | REROUTE  | [0.50, 0.00, -0.00]
   499 | [-3.41, -1.20, 1.50]    | [ 1.50,  0.40, -0.00]   |  1.55 |  0.48 | REROUTE  | [0.50, 0.13, -0.00]
   500 | [-3.34, -1.18, 1.50]    | [ 1.50,  0.40, -0.00]   |  1.55 |  0.47 | REROUTE  | [0.50, 0.13, -0.00]
  ```

### [Seed 1003] Configuration: Shield ON (Camera) — Outcome: `OBSTACLE_COLLISION`
- **Steps:** 88 | **Reward:** -234.09 | **Min Clearance:** 0.34 m
- **Diagnostic Cause:** Obstacle collision at speed 1.55 m/s (min clearance 0.35m).
- **Last 5 Control Steps Telemetry:**
  ```
  Step | Pos [x, y, z]           | Vel [vx, vy, vz]        | Speed | Clr   | State    | Action Executed
  -----+-------------------------+-------------------------+-------+-------+----------+----------------
    84 | [ 1.62, -0.95, 1.50]    | [ 1.50,  0.00, 0.01]    |  1.50 |  0.34 | REROUTE  | [0.50, 0.00, 0.00]
    85 | [ 1.68, -0.95, 1.50]    | [ 1.50,  0.00, 0.01]    |  1.50 |  0.35 | REROUTE  | [0.50, 0.00, 0.00]
    86 | [ 1.74, -0.93, 1.50]    | [ 1.50,  0.40, 0.01]    |  1.55 |  0.35 | REROUTE  | [0.50, 0.13, 0.00]
    87 | [ 1.80, -0.93, 1.50]    | [ 1.50,  0.00, 0.01]    |  1.50 |  0.34 | REROUTE  | [0.50, 0.00, 0.00]
    88 | [ 1.87, -0.92, 1.50]    | [ 1.50,  0.40, 0.01]    |  1.55 |  0.35 | REROUTE  | [0.50, 0.13, 0.00]
  ```

### [Seed 1004] Configuration: Shield ON (Camera) — Outcome: `OBSTACLE_COLLISION`
- **Steps:** 99 | **Reward:** -329.94 | **Min Clearance:** 0.06 m
- **Diagnostic Cause:** Obstacle collision at speed 1.50 m/s (min clearance 0.06m).
- **Last 5 Control Steps Telemetry:**
  ```
  Step | Pos [x, y, z]           | Vel [vx, vy, vz]        | Speed | Clr   | State    | Action Executed
  -----+-------------------------+-------------------------+-------+-------+----------+----------------
    95 | [ 1.83, -0.94, 1.50]    | [ 1.50,  0.00, 0.00]    |  1.50 |  0.34 | REROUTE  | [0.50, 0.00, 0.00]
    96 | [ 1.89, -0.94, 1.50]    | [ 1.50,  0.00, 0.00]    |  1.50 |  0.34 | REROUTE  | [0.50, 0.00, 0.00]
    97 | [ 1.95, -0.94, 1.50]    | [ 1.50,  0.00, 0.00]    |  1.50 |  0.35 | REROUTE  | [0.50, 0.00, 0.00]
    98 | [ 2.01, -0.93, 1.50]    | [ 1.50,  0.40, 0.00]    |  1.55 |  0.35 | REROUTE  | [0.50, 0.13, 0.00]
    99 | [ 2.08, -0.93, 1.50]    | [ 1.50,  0.00, 0.00]    |  1.50 |  0.06 | REROUTE  | [0.50, 0.00, 0.00]
  ```

### [Seed 1005] Configuration: Shield ON (Camera) — Outcome: `TIMEOUT`
- **Steps:** 500 | **Reward:** -2381.46 | **Min Clearance:** 0.26 m
- **Diagnostic Cause:** Exceeded maximum episode limit (500 steps) without reaching goal.
- **Last 5 Control Steps Telemetry:**
  ```
  Step | Pos [x, y, z]           | Vel [vx, vy, vz]        | Speed | Clr   | State    | Action Executed
  -----+-------------------------+-------------------------+-------+-------+----------+----------------
   496 | [-2.27, -1.04, 1.50]    | [-1.50,  0.40, -0.00]   |  1.55 |  0.37 | REROUTE  | [-0.50, 0.13, -0.00]
   497 | [-2.33, -1.02, 1.50]    | [-1.50,  0.40, -0.00]   |  1.55 |  0.35 | REROUTE  | [-0.50, 0.13, -0.00]
   498 | [-2.39, -1.02, 1.50]    | [-1.50,  0.00, -0.00]   |  1.50 |  0.33 | REROUTE  | [-0.50, 0.00, -0.00]
   499 | [-2.45, -1.02, 1.50]    | [-1.50,  0.00, -0.00]   |  1.50 |  0.33 | REROUTE  | [-0.50, 0.00, -0.00]
   500 | [-2.52, -1.02, 1.50]    | [-1.50,  0.00, -0.00]   |  1.50 |  0.32 | REROUTE  | [-0.50, 0.00, -0.00]
  ```

### [Seed 1006] Configuration: Shield ON (Camera) — Outcome: `OBSTACLE_COLLISION`
- **Steps:** 44 | **Reward:** 86.14 | **Min Clearance:** 0.857 m
- **Diagnostic Cause:** Obstacle collision at speed 2.84 m/s (min clearance 2.63m).
- **Last 5 Control Steps Telemetry:**
  ```
  Step | Pos [x, y, z]           | Vel [vx, vy, vz]        | Speed | Clr   | State    | Action Executed
  -----+-------------------------+-------------------------+-------+-------+----------+----------------
    40 | [ 0.42, -3.64, 1.50]    | [ 0.01,  2.37, -0.01]   |  2.37 |  2.38 | NOMINAL  | [0.00, 0.79, -0.01]
    41 | [ 0.43, -3.53, 1.50]    | [ 0.21,  2.54, -0.01]   |  2.55 |  2.30 | NOMINAL  | [0.07, 0.85, -0.00]
    42 | [ 0.44, -3.42, 1.50]    | [ 0.29,  2.76, -0.01]   |  2.77 |  2.79 | NOMINAL  | [0.10, 0.92, -0.00]
    43 | [ 0.44, -3.30, 1.50]    | [-0.01,  2.84, -0.01]   |  2.84 |  2.75 | NOMINAL  | [-0.00, 0.94, -0.00]
    44 | [ 0.44, -3.18, 1.50]    | [-0.11,  2.84, -0.01]   |  2.84 |  2.63 | NOMINAL  | [-0.04, 0.95, -0.00]
  ```

### [Seed 1007] Configuration: Shield ON (Camera) — Outcome: `TIMEOUT`
- **Steps:** 500 | **Reward:** -2331.14 | **Min Clearance:** 0.248 m
- **Diagnostic Cause:** Exceeded maximum episode limit (500 steps) without reaching goal.
- **Last 5 Control Steps Telemetry:**
  ```
  Step | Pos [x, y, z]           | Vel [vx, vy, vz]        | Speed | Clr   | State    | Action Executed
  -----+-------------------------+-------------------------+-------+-------+----------+----------------
   496 | [-3.08, -1.01, 1.50]    | [-1.50,  0.00, -0.00]   |  1.50 |  0.29 | REROUTE  | [-0.50, 0.00, -0.00]
   497 | [-3.14, -1.01, 1.50]    | [-1.50,  0.00, -0.00]   |  1.50 |  0.28 | REROUTE  | [-0.50, 0.00, -0.00]
   498 | [-3.20, -1.01, 1.50]    | [-1.50,  0.00, -0.00]   |  1.50 |  0.28 | REROUTE  | [-0.50, 0.00, -0.00]
   499 | [-3.27, -1.01, 1.50]    | [-1.50,  0.00, -0.00]   |  1.50 |  0.27 | REROUTE  | [-0.50, 0.00, -0.00]
   500 | [-3.33, -1.01, 1.50]    | [-1.50,  0.00, -0.00]   |  1.50 |  0.27 | REROUTE  | [-0.50, 0.00, -0.00]
  ```

### [Seed 1008] Configuration: Shield ON (Camera) — Outcome: `TIMEOUT`
- **Steps:** 500 | **Reward:** -2441.18 | **Min Clearance:** 0.229 m
- **Diagnostic Cause:** Exceeded maximum episode limit (500 steps) without reaching goal.
- **Last 5 Control Steps Telemetry:**
  ```
  Step | Pos [x, y, z]           | Vel [vx, vy, vz]        | Speed | Clr   | State    | Action Executed
  -----+-------------------------+-------------------------+-------+-------+----------+----------------
   496 | [ 2.97, -0.86, 1.50]    | [ 1.50,  0.00, -0.00]   |  1.50 |  0.35 | REROUTE  | [0.50, 0.00, -0.00]
   497 | [ 3.03, -0.84, 1.50]    | [ 1.50,  0.40, -0.00]   |  1.55 |  0.35 | REROUTE  | [0.50, 0.13, -0.00]
   498 | [ 3.09, -0.84, 1.50]    | [ 1.50,  0.00, -0.00]   |  1.50 |  0.34 | REROUTE  | [0.50, 0.00, -0.00]
   499 | [ 3.16, -0.84, 1.50]    | [ 1.50,  0.00, -0.00]   |  1.50 |  0.35 | REROUTE  | [0.50, 0.00, -0.00]
   500 | [ 3.22, -0.84, 1.50]    | [ 1.50,  0.00, -0.00]   |  1.50 |  0.35 | REROUTE  | [0.50, 0.00, -0.00]
  ```

### [Seed 1009] Configuration: Shield ON (Camera) — Outcome: `OBSTACLE_COLLISION`
- **Steps:** 71 | **Reward:** -46.07 | **Min Clearance:** 0.359 m
- **Diagnostic Cause:** Obstacle collision at speed 2.66 m/s (min clearance 2.87m).
- **Last 5 Control Steps Telemetry:**
  ```
  Step | Pos [x, y, z]           | Vel [vx, vy, vz]        | Speed | Clr   | State    | Action Executed
  -----+-------------------------+-------------------------+-------+-------+----------+----------------
    67 | [ 0.28, -3.67, 1.50]    | [ 0.00,  0.00, 0.00]    |  0.00 |  0.36 | SCAN     | [0.00, 0.00, 0.00]
    68 | [ 0.35, -3.67, 1.50]    | [ 1.50,  0.00, 0.01]    |  1.50 |  0.36 | REROUTE  | [0.50, 0.00, 0.00]
    69 | [ 0.41, -3.60, 1.50]    | [ 1.50,  1.60, 0.01]    |  2.19 |  3.00 | REROUTE  | [0.50, 0.53, 0.00]
    70 | [ 0.48, -3.52, 1.50]    | [ 1.70,  1.79, -0.02]   |  2.46 |  2.94 | NOMINAL  | [0.57, 0.60, -0.01]
    71 | [ 0.56, -3.45, 1.50]    | [ 1.97,  1.79, 0.04]    |  2.66 |  2.87 | NOMINAL  | [0.66, 0.59, 0.01]
  ```

### [Seed 1010] Configuration: Shield ON (Camera) — Outcome: `OBSTACLE_COLLISION`
- **Steps:** 40 | **Reward:** 46.16 | **Min Clearance:** 0.823 m
- **Diagnostic Cause:** Obstacle collision at speed 2.40 m/s (min clearance 1.57m).
- **Last 5 Control Steps Telemetry:**
  ```
  Step | Pos [x, y, z]           | Vel [vx, vy, vz]        | Speed | Clr   | State    | Action Executed
  -----+-------------------------+-------------------------+-------+-------+----------+----------------
    36 | [ 0.35, -4.12, 1.49]    | [-2.20,  2.04, -0.01]   |  3.00 |  1.88 | NOMINAL  | [-0.73, 0.68, -0.01]
    37 | [ 0.34, -4.05, 1.49]    | [-0.11,  1.68, 0.00]    |  1.68 |  1.79 | NOMINAL  | [-0.04, 0.56, 0.00]
    38 | [ 0.32, -3.98, 1.49]    | [-0.42,  1.73, -0.01]   |  1.78 |  1.72 | NOMINAL  | [-0.14, 0.58, -0.00]
    39 | [ 0.36, -3.91, 1.49]    | [ 0.78,  1.77, -0.01]   |  1.94 |  1.64 | NOMINAL  | [0.26, 0.59, -0.00]
    40 | [ 0.29, -3.83, 1.49]    | [-1.58,  1.81, 0.04]    |  2.40 |  1.57 | NOMINAL  | [-0.53, 0.60, 0.01]
  ```

### [Seed 1011] Configuration: Shield ON (Camera) — Outcome: `OBSTACLE_COLLISION`
- **Steps:** 82 | **Reward:** -156.35 | **Min Clearance:** 0.294 m
- **Diagnostic Cause:** Obstacle collision at speed 1.50 m/s (min clearance 0.30m).
- **Last 5 Control Steps Telemetry:**
  ```
  Step | Pos [x, y, z]           | Vel [vx, vy, vz]        | Speed | Clr   | State    | Action Executed
  -----+-------------------------+-------------------------+-------+-------+----------+----------------
    78 | [ 0.58, -1.20, 1.50]    | [ 1.50,  0.00, 0.01]    |  1.50 |  0.54 | REROUTE  | [0.50, 0.00, 0.00]
    79 | [ 0.65, -1.18, 1.50]    | [ 1.50,  0.40, 0.00]    |  1.55 |  0.36 | REROUTE  | [0.50, 0.13, 0.00]
    80 | [ 0.71, -1.18, 1.50]    | [ 1.50,  0.00, 0.00]    |  1.50 |  0.29 | REROUTE  | [0.50, 0.00, 0.00]
    81 | [ 0.77, -1.18, 1.50]    | [ 1.50,  0.00, 0.00]    |  1.50 |  0.30 | REROUTE  | [0.50, 0.00, 0.00]
    82 | [ 0.83, -1.18, 1.50]    | [ 1.50,  0.00, 0.00]    |  1.50 |  0.30 | REROUTE  | [0.50, 0.00, 0.00]
  ```

### [Seed 1012] Configuration: Shield ON (Camera) — Outcome: `TIMEOUT`
- **Steps:** 500 | **Reward:** -2319.53 | **Min Clearance:** 0.231 m
- **Diagnostic Cause:** Exceeded maximum episode limit (500 steps) without reaching goal.
- **Last 5 Control Steps Telemetry:**
  ```
  Step | Pos [x, y, z]           | Vel [vx, vy, vz]        | Speed | Clr   | State    | Action Executed
  -----+-------------------------+-------------------------+-------+-------+----------+----------------
   496 | [-3.27, -1.09, 1.50]    | [ 1.50,  0.00, -0.00]   |  1.50 |  0.35 | REROUTE  | [0.50, 0.00, -0.00]
   497 | [-3.21, -1.07, 1.50]    | [ 1.50,  0.40, -0.00]   |  1.55 |  0.35 | REROUTE  | [0.50, 0.13, -0.00]
   498 | [-3.15, -1.07, 1.50]    | [ 1.50,  0.00, -0.00]   |  1.50 |  0.34 | REROUTE  | [0.50, 0.00, -0.00]
   499 | [-3.08, -1.07, 1.50]    | [ 1.50,  0.00, -0.00]   |  1.50 |  0.34 | REROUTE  | [0.50, 0.00, -0.00]
   500 | [-3.02, -1.07, 1.50]    | [ 1.50,  0.00, -0.00]   |  1.50 |  0.35 | REROUTE  | [0.50, 0.00, -0.00]
  ```

### [Seed 1013] Configuration: Shield ON (Camera) — Outcome: `TIMEOUT`
- **Steps:** 500 | **Reward:** -2399.42 | **Min Clearance:** 0.212 m
- **Diagnostic Cause:** Exceeded maximum episode limit (500 steps) without reaching goal.
- **Last 5 Control Steps Telemetry:**
  ```
  Step | Pos [x, y, z]           | Vel [vx, vy, vz]        | Speed | Clr   | State    | Action Executed
  -----+-------------------------+-------------------------+-------+-------+----------+----------------
   496 | [ 3.88, -0.82, 1.50]    | [ 1.50,  0.00, -0.00]   |  1.50 |  0.32 | REROUTE  | [0.50, 0.00, -0.00]
   497 | [ 3.94, -0.82, 1.50]    | [ 1.50,  0.00, -0.00]   |  1.50 |  0.31 | REROUTE  | [0.50, 0.00, -0.00]
   498 | [ 4.00, -0.82, 1.50]    | [ 1.50,  0.00, -0.00]   |  1.50 |  0.31 | REROUTE  | [0.50, 0.00, -0.00]
   499 | [ 4.00, -0.85, 1.50]    | [ 0.00, -0.80, -0.00]   |  0.80 |  0.31 | RETREAT  | [0.00, -0.27, -0.00]
   500 | [ 4.00, -0.89, 1.50]    | [ 0.00, -0.80, -0.00]   |  0.80 |  0.34 | RETREAT  | [0.00, -0.27, -0.00]
  ```

### [Seed 1014] Configuration: Shield ON (Camera) — Outcome: `OBSTACLE_COLLISION`
- **Steps:** 80 | **Reward:** -172.66 | **Min Clearance:** 0.148 m
- **Diagnostic Cause:** Obstacle collision at speed 1.50 m/s (min clearance 0.15m).
- **Last 5 Control Steps Telemetry:**
  ```
  Step | Pos [x, y, z]           | Vel [vx, vy, vz]        | Speed | Clr   | State    | Action Executed
  -----+-------------------------+-------------------------+-------+-------+----------+----------------
    76 | [ 0.48, -2.54, 1.50]    | [ 1.50,  0.40, -0.00]   |  1.55 |  0.36 | REROUTE  | [0.50, 0.13, -0.00]
    77 | [ 0.55, -2.54, 1.50]    | [ 1.50,  0.00, -0.00]   |  1.50 |  0.34 | REROUTE  | [0.50, 0.00, -0.00]
    78 | [ 0.61, -2.54, 1.50]    | [ 1.50,  0.00, -0.00]   |  1.50 |  0.34 | REROUTE  | [0.50, 0.00, -0.00]
    79 | [ 0.67, -2.54, 1.50]    | [ 1.50,  0.00, -0.00]   |  1.50 |  0.23 | REROUTE  | [0.50, 0.00, -0.00]
    80 | [ 0.73, -2.54, 1.50]    | [ 1.50,  0.00, -0.00]   |  1.50 |  0.15 | REROUTE  | [0.50, 0.00, -0.00]
  ```

### [Seed 1015] Configuration: Shield ON (Camera) — Outcome: `OBSTACLE_COLLISION`
- **Steps:** 91 | **Reward:** -193.9 | **Min Clearance:** 0.319 m
- **Diagnostic Cause:** Obstacle collision at speed 1.50 m/s (min clearance 0.32m).
- **Last 5 Control Steps Telemetry:**
  ```
  Step | Pos [x, y, z]           | Vel [vx, vy, vz]        | Speed | Clr   | State    | Action Executed
  -----+-------------------------+-------------------------+-------+-------+----------+----------------
    87 | [-1.78, -0.96, 1.50]    | [-1.50,  0.00, -0.01]   |  1.50 |  0.34 | REROUTE  | [-0.50, 0.00, -0.00]
    88 | [-1.84, -0.96, 1.50]    | [-1.50,  0.00, -0.01]   |  1.50 |  0.33 | REROUTE  | [-0.50, 0.00, -0.00]
    89 | [-1.90, -0.96, 1.50]    | [-1.50,  0.00, -0.01]   |  1.50 |  0.33 | REROUTE  | [-0.50, 0.00, -0.00]
    90 | [-1.96, -0.96, 1.50]    | [-1.50,  0.00, -0.00]   |  1.50 |  0.32 | REROUTE  | [-0.50, 0.00, -0.00]
    91 | [-2.03, -0.96, 1.50]    | [-1.50,  0.00, -0.00]   |  1.50 |  0.32 | REROUTE  | [-0.50, 0.00, -0.00]
  ```

### [Seed 1016] Configuration: Shield ON (Camera) — Outcome: `OBSTACLE_COLLISION`
- **Steps:** 30 | **Reward:** -24.6 | **Min Clearance:** 0.769 m
- **Diagnostic Cause:** Obstacle collision at speed 2.94 m/s (min clearance 4.52m).
- **Last 5 Control Steps Telemetry:**
  ```
  Step | Pos [x, y, z]           | Vel [vx, vy, vz]        | Speed | Clr   | State    | Action Executed
  -----+-------------------------+-------------------------+-------+-------+----------+----------------
    26 | [ 0.51, -5.56, 1.50]    | [ 0.13,  2.65, -0.00]   |  2.65 |  4.99 | NOMINAL  | [0.04, 0.88, -0.00]
    27 | [ 0.52, -5.44, 1.50]    | [ 0.25,  2.87, 0.00]    |  2.88 |  4.88 | NOMINAL  | [0.09, 0.96, 0.00]
    28 | [ 0.50, -5.32, 1.50]    | [-0.37,  2.91, -0.03]   |  2.93 |  4.76 | NOMINAL  | [-0.12, 0.97, -0.01]
    29 | [ 0.50, -5.20, 1.50]    | [ 0.01,  2.90, 0.01]    |  2.90 |  4.64 | NOMINAL  | [0.00, 0.97, 0.00]
    30 | [ 0.49, -5.08, 1.50]    | [-0.32,  2.92, -0.02]   |  2.94 |  4.52 | NOMINAL  | [-0.10, 0.97, -0.01]
  ```

### [Seed 1017] Configuration: Shield ON (Camera) — Outcome: `OBSTACLE_COLLISION`
- **Steps:** 95 | **Reward:** -269.74 | **Min Clearance:** 0.216 m
- **Diagnostic Cause:** Obstacle collision at speed 1.50 m/s (min clearance 0.22m).
- **Last 5 Control Steps Telemetry:**
  ```
  Step | Pos [x, y, z]           | Vel [vx, vy, vz]        | Speed | Clr   | State    | Action Executed
  -----+-------------------------+-------------------------+-------+-------+----------+----------------
    91 | [ 1.92, -0.94, 1.50]    | [ 1.50,  0.00, 0.01]    |  1.50 |  0.35 | REROUTE  | [0.50, 0.00, 0.00]
    92 | [ 1.98, -0.93, 1.50]    | [ 1.50,  0.40, 0.01]    |  1.55 |  0.35 | REROUTE  | [0.50, 0.13, 0.00]
    93 | [ 2.04, -0.93, 1.50]    | [ 1.50,  0.00, 0.00]    |  1.50 |  0.34 | REROUTE  | [0.50, 0.00, 0.00]
    94 | [ 2.10, -0.93, 1.50]    | [ 1.50,  0.00, 0.00]    |  1.50 |  0.34 | REROUTE  | [0.50, 0.00, 0.00]
    95 | [ 2.17, -0.93, 1.50]    | [ 1.50,  0.00, 0.00]    |  1.50 |  0.22 | REROUTE  | [0.50, 0.00, 0.00]
  ```

### [Seed 1018] Configuration: Shield ON (Camera) — Outcome: `TIMEOUT`
- **Steps:** 500 | **Reward:** -2396.46 | **Min Clearance:** 0.291 m
- **Diagnostic Cause:** Exceeded maximum episode limit (500 steps) without reaching goal.
- **Last 5 Control Steps Telemetry:**
  ```
  Step | Pos [x, y, z]           | Vel [vx, vy, vz]        | Speed | Clr   | State    | Action Executed
  -----+-------------------------+-------------------------+-------+-------+----------+----------------
   496 | [ 2.91, -0.92, 1.50]    | [ 1.50,  0.00, 0.00]    |  1.50 |  0.33 | REROUTE  | [0.50, 0.00, 0.00]
   497 | [ 2.97, -0.92, 1.50]    | [ 1.50,  0.00, 0.00]    |  1.50 |  0.33 | REROUTE  | [0.50, 0.00, 0.00]
   498 | [ 3.04, -0.92, 1.50]    | [ 1.50,  0.00, 0.00]    |  1.50 |  0.33 | REROUTE  | [0.50, 0.00, 0.00]
   499 | [ 3.10, -0.92, 1.50]    | [ 1.50,  0.00, 0.00]    |  1.50 |  0.32 | REROUTE  | [0.50, 0.00, 0.00]
   500 | [ 3.16, -0.92, 1.50]    | [ 1.50,  0.00, 0.00]    |  1.50 |  0.32 | REROUTE  | [0.50, 0.00, 0.00]
  ```

### [Seed 1019] Configuration: Shield ON (Camera) — Outcome: `TIMEOUT`
- **Steps:** 500 | **Reward:** -2471.73 | **Min Clearance:** 0.251 m
- **Diagnostic Cause:** Exceeded maximum episode limit (500 steps) without reaching goal.
- **Last 5 Control Steps Telemetry:**
  ```
  Step | Pos [x, y, z]           | Vel [vx, vy, vz]        | Speed | Clr   | State    | Action Executed
  -----+-------------------------+-------------------------+-------+-------+----------+----------------
   496 | [-3.34, -1.10, 1.50]    | [ 0.00, -0.80, -0.00]   |  0.80 |  0.34 | RETREAT  | [0.00, -0.27, -0.00]
   497 | [-3.34, -1.13, 1.50]    | [ 0.00, -0.80, -0.00]   |  0.80 |  0.37 | RETREAT  | [0.00, -0.27, -0.00]
   498 | [-3.34, -1.16, 1.50]    | [ 0.00, -0.80, -0.00]   |  0.80 |  0.41 | RETREAT  | [0.00, -0.27, -0.00]
   499 | [-3.34, -1.20, 1.50]    | [ 0.00, -0.80, -0.00]   |  0.80 |  0.44 | SCAN     | [0.00, -0.27, -0.00]
   500 | [-3.28, -1.20, 1.50]    | [ 1.50,  0.00, -0.00]   |  1.50 |  0.47 | REROUTE  | [0.50, 0.00, -0.00]
  ```

### [Seed 1020] Configuration: Shield ON (Camera) — Outcome: `OBSTACLE_COLLISION`
- **Steps:** 31 | **Reward:** 42.16 | **Min Clearance:** 1.975 m
- **Diagnostic Cause:** Obstacle collision at speed 2.84 m/s (min clearance 3.73m).
- **Last 5 Control Steps Telemetry:**
  ```
  Step | Pos [x, y, z]           | Vel [vx, vy, vz]        | Speed | Clr   | State    | Action Executed
  -----+-------------------------+-------------------------+-------+-------+----------+----------------
    27 | [-0.01, -4.76, 1.49]    | [-0.52,  2.84, -0.04]   |  2.89 |  4.20 | NOMINAL  | [-0.17, 0.95, -0.01]
    28 | [-0.01, -4.64, 1.49]    | [-0.02,  2.77, -0.04]   |  2.77 |  4.08 | NOMINAL  | [-0.01, 0.92, -0.01]
    29 | [-0.02, -4.53, 1.49]    | [-0.06,  2.84, -0.05]   |  2.85 |  3.97 | NOMINAL  | [-0.02, 0.95, -0.02]
    30 | [-0.02, -4.41, 1.49]    | [-0.15,  2.84, -0.06]   |  2.84 |  3.85 | NOMINAL  | [-0.05, 0.95, -0.02]
    31 | [-0.02, -4.29, 1.49]    | [-0.01,  2.84, -0.05]   |  2.84 |  3.73 | NOMINAL  | [-0.00, 0.95, -0.02]
  ```

### [Seed 1021] Configuration: Shield ON (Camera) — Outcome: `TIMEOUT`
- **Steps:** 500 | **Reward:** -2461.17 | **Min Clearance:** 0.198 m
- **Diagnostic Cause:** Exceeded maximum episode limit (500 steps) without reaching goal.
- **Last 5 Control Steps Telemetry:**
  ```
  Step | Pos [x, y, z]           | Vel [vx, vy, vz]        | Speed | Clr   | State    | Action Executed
  -----+-------------------------+-------------------------+-------+-------+----------+----------------
   496 | [ 3.54, -0.98, 1.50]    | [-1.50,  0.40, 0.00]    |  1.55 |  0.40 | REROUTE  | [-0.50, 0.13, 0.00]
   497 | [ 3.47, -0.96, 1.50]    | [-1.50,  0.40, 0.00]    |  1.55 |  0.38 | REROUTE  | [-0.50, 0.13, 0.00]
   498 | [ 3.41, -0.94, 1.50]    | [-1.50,  0.40, 0.00]    |  1.55 |  0.37 | REROUTE  | [-0.50, 0.13, 0.00]
   499 | [ 3.35, -0.93, 1.50]    | [-1.50,  0.40, 0.00]    |  1.55 |  0.35 | REROUTE  | [-0.50, 0.13, 0.00]
   500 | [ 3.29, -0.93, 1.50]    | [-1.50,  0.00, 0.00]    |  1.50 |  0.34 | REROUTE  | [-0.50, 0.00, 0.00]
  ```

### [Seed 1022] Configuration: Shield ON (Camera) — Outcome: `TIMEOUT`
- **Steps:** 500 | **Reward:** -2930.8 | **Min Clearance:** 0.235 m
- **Diagnostic Cause:** Exceeded maximum episode limit (500 steps) without reaching goal.
- **Last 5 Control Steps Telemetry:**
  ```
  Step | Pos [x, y, z]           | Vel [vx, vy, vz]        | Speed | Clr   | State    | Action Executed
  -----+-------------------------+-------------------------+-------+-------+----------+----------------
   496 | [-2.95, -1.16, 1.50]    | [ 0.00, -0.80, -0.00]   |  0.80 |  0.38 | RETREAT  | [0.00, -0.27, -0.00]
   497 | [-2.95, -1.19, 1.50]    | [ 0.00, -0.80, -0.00]   |  0.80 |  0.41 | RETREAT  | [0.00, -0.27, -0.00]
   498 | [-2.95, -1.23, 1.50]    | [ 0.00, -0.80, -0.00]   |  0.80 |  0.45 | RETREAT  | [0.00, -0.27, -0.00]
   499 | [-2.95, -1.26, 1.50]    | [ 0.00, -0.80, -0.00]   |  0.80 |  0.48 | SCAN     | [0.00, -0.27, -0.00]
   500 | [-2.89, -1.26, 1.50]    | [ 1.50,  0.00, -0.00]   |  1.50 |  0.51 | REROUTE  | [0.50, 0.00, -0.00]
  ```

### [Seed 1023] Configuration: Shield ON (Camera) — Outcome: `TIMEOUT`
- **Steps:** 500 | **Reward:** -2258.47 | **Min Clearance:** 0.242 m
- **Diagnostic Cause:** Exceeded maximum episode limit (500 steps) without reaching goal.
- **Last 5 Control Steps Telemetry:**
  ```
  Step | Pos [x, y, z]           | Vel [vx, vy, vz]        | Speed | Clr   | State    | Action Executed
  -----+-------------------------+-------------------------+-------+-------+----------+----------------
   496 | [-2.27, -1.08, 1.50]    | [-1.50,  0.40, 0.00]    |  1.55 |  0.38 | REROUTE  | [-0.50, 0.13, 0.00]
   497 | [-2.34, -1.06, 1.50]    | [-1.50,  0.40, 0.00]    |  1.55 |  0.35 | REROUTE  | [-0.50, 0.13, 0.00]
   498 | [-2.40, -1.06, 1.50]    | [-1.50,  0.00, 0.00]    |  1.50 |  0.33 | REROUTE  | [-0.50, 0.00, 0.00]
   499 | [-2.46, -1.06, 1.50]    | [-1.50,  0.00, 0.00]    |  1.50 |  0.33 | REROUTE  | [-0.50, 0.00, 0.00]
   500 | [-2.52, -1.06, 1.50]    | [-1.50,  0.00, 0.00]    |  1.50 |  0.33 | REROUTE  | [-0.50, 0.00, 0.00]
  ```

### [Seed 1024] Configuration: Shield ON (Camera) — Outcome: `TIMEOUT`
- **Steps:** 500 | **Reward:** -2473.42 | **Min Clearance:** 0.259 m
- **Diagnostic Cause:** Exceeded maximum episode limit (500 steps) without reaching goal.
- **Last 5 Control Steps Telemetry:**
  ```
  Step | Pos [x, y, z]           | Vel [vx, vy, vz]        | Speed | Clr   | State    | Action Executed
  -----+-------------------------+-------------------------+-------+-------+----------+----------------
   496 | [-3.14, -1.17, 1.50]    | [ 0.00, -0.80, -0.00]   |  0.80 |  0.45 | RETREAT  | [0.00, -0.27, -0.00]
   497 | [-3.14, -1.20, 1.50]    | [ 0.00, -0.80, -0.00]   |  0.80 |  0.49 | SCAN     | [0.00, -0.27, -0.00]
   498 | [-3.08, -1.20, 1.50]    | [ 1.50,  0.00, -0.00]   |  1.50 |  0.52 | REROUTE  | [0.50, 0.00, -0.00]
   499 | [-3.02, -1.18, 1.50]    | [ 1.50,  0.40, -0.00]   |  1.55 |  0.52 | REROUTE  | [0.50, 0.13, -0.00]
   500 | [-2.95, -1.17, 1.50]    | [ 1.50,  0.40, -0.00]   |  1.55 |  0.51 | REROUTE  | [0.50, 0.13, -0.00]
  ```

### [Seed 1025] Configuration: Shield ON (Camera) — Outcome: `TIMEOUT`
- **Steps:** 500 | **Reward:** -2408.07 | **Min Clearance:** 0.218 m
- **Diagnostic Cause:** Exceeded maximum episode limit (500 steps) without reaching goal.
- **Last 5 Control Steps Telemetry:**
  ```
  Step | Pos [x, y, z]           | Vel [vx, vy, vz]        | Speed | Clr   | State    | Action Executed
  -----+-------------------------+-------------------------+-------+-------+----------+----------------
   496 | [-3.78, -1.08, 1.50]    | [ 1.50,  0.40, -0.00]   |  1.55 |  0.44 | REROUTE  | [0.50, 0.13, -0.00]
   497 | [-3.72, -1.06, 1.50]    | [ 1.50,  0.40, -0.00]   |  1.55 |  0.42 | REROUTE  | [0.50, 0.13, -0.00]
   498 | [-3.66, -1.05, 1.50]    | [ 1.50,  0.40, -0.00]   |  1.55 |  0.41 | REROUTE  | [0.50, 0.13, -0.00]
   499 | [-3.59, -1.03, 1.50]    | [ 1.50,  0.40, -0.00]   |  1.55 |  0.40 | REROUTE  | [0.50, 0.13, -0.00]
   500 | [-3.53, -1.01, 1.50]    | [ 1.50,  0.40, -0.00]   |  1.55 |  0.38 | REROUTE  | [0.50, 0.13, -0.00]
  ```

### [Seed 1026] Configuration: Shield ON (Camera) — Outcome: `OBSTACLE_COLLISION`
- **Steps:** 64 | **Reward:** -67.57 | **Min Clearance:** 0.903 m
- **Diagnostic Cause:** Obstacle collision at speed 2.13 m/s (min clearance 0.90m).
- **Last 5 Control Steps Telemetry:**
  ```
  Step | Pos [x, y, z]           | Vel [vx, vy, vz]        | Speed | Clr   | State    | Action Executed
  -----+-------------------------+-------------------------+-------+-------+----------+----------------
    60 | [ 0.65, -1.69, 1.50]    | [ 1.94,  1.34, 0.02]    |  2.36 |  1.10 | NOMINAL  | [0.65, 0.45, 0.01]
    61 | [ 0.68, -1.64, 1.50]    | [ 0.69,  1.37, -0.01]   |  1.53 |  1.04 | NOMINAL  | [0.23, 0.46, -0.00]
    62 | [ 0.70, -1.58, 1.50]    | [ 0.54,  1.24, -0.01]   |  1.35 |  0.99 | NOMINAL  | [0.18, 0.41, -0.00]
    63 | [ 0.79, -1.55, 1.50]    | [ 2.01,  0.89, 0.02]    |  2.20 |  0.94 | NOMINAL  | [0.67, 0.30, 0.01]
    64 | [ 0.87, -1.51, 1.50]    | [ 1.94,  0.86, 0.00]    |  2.13 |  0.90 | NOMINAL  | [0.65, 0.29, 0.00]
  ```

### [Seed 1027] Configuration: Shield ON (Camera) — Outcome: `TIMEOUT`
- **Steps:** 500 | **Reward:** -2366.99 | **Min Clearance:** 0.058 m
- **Diagnostic Cause:** Exceeded maximum episode limit (500 steps) without reaching goal.
- **Last 5 Control Steps Telemetry:**
  ```
  Step | Pos [x, y, z]           | Vel [vx, vy, vz]        | Speed | Clr   | State    | Action Executed
  -----+-------------------------+-------------------------+-------+-------+----------+----------------
   496 | [-3.14, -1.13, 1.50]    | [ 1.50,  0.00, 0.00]    |  1.50 |  0.34 | REROUTE  | [0.50, 0.00, 0.00]
   497 | [-3.08, -1.13, 1.50]    | [ 1.50,  0.00, 0.00]    |  1.50 |  0.34 | REROUTE  | [0.50, 0.00, 0.00]
   498 | [-3.01, -1.13, 1.50]    | [ 1.50,  0.00, 0.00]    |  1.50 |  0.35 | REROUTE  | [0.50, 0.00, 0.00]
   499 | [-2.95, -1.12, 1.50]    | [ 1.50,  0.40, 0.00]    |  1.55 |  0.35 | REROUTE  | [0.50, 0.13, 0.00]
   500 | [-2.89, -1.12, 1.50]    | [ 1.50,  0.00, 0.00]    |  1.50 |  0.34 | REROUTE  | [0.50, 0.00, 0.00]
  ```

### [Seed 1028] Configuration: Shield ON (Camera) — Outcome: `OBSTACLE_COLLISION`
- **Steps:** 55 | **Reward:** 57.1 | **Min Clearance:** 0.413 m
- **Diagnostic Cause:** Obstacle collision at speed 1.55 m/s (min clearance 0.41m).
- **Last 5 Control Steps Telemetry:**
  ```
  Step | Pos [x, y, z]           | Vel [vx, vy, vz]        | Speed | Clr   | State    | Action Executed
  -----+-------------------------+-------------------------+-------+-------+----------+----------------
    51 | [-0.04, -3.96, 1.46]    | [ 0.00,  0.00, 0.00]    |  0.00 |  0.42 | BRAKE    | [0.00, 0.00, 0.00]
    52 | [-0.04, -3.96, 1.46]    | [ 0.00,  0.00, 0.00]    |  0.00 |  0.42 | SCAN     | [0.00, 0.00, 0.00]
    53 | [ 0.02, -3.96, 1.47]    | [ 1.50,  0.00, 0.08]    |  1.50 |  0.42 | REROUTE  | [0.50, 0.00, 0.03]
    54 | [ 0.08, -3.94, 1.47]    | [ 1.50,  0.40, 0.07]    |  1.55 |  0.42 | REROUTE  | [0.50, 0.13, 0.02]
    55 | [ 0.14, -3.93, 1.47]    | [ 1.50,  0.40, 0.07]    |  1.55 |  0.41 | REROUTE  | [0.50, 0.13, 0.02]
  ```

### [Seed 1029] Configuration: Shield ON (Camera) — Outcome: `TIMEOUT`
- **Steps:** 500 | **Reward:** -2884.11 | **Min Clearance:** 0.072 m
- **Diagnostic Cause:** Exceeded maximum episode limit (500 steps) without reaching goal.
- **Last 5 Control Steps Telemetry:**
  ```
  Step | Pos [x, y, z]           | Vel [vx, vy, vz]        | Speed | Clr   | State    | Action Executed
  -----+-------------------------+-------------------------+-------+-------+----------+----------------
   496 | [-3.54, -1.24, 1.50]    | [ 0.00, -0.80, -0.00]   |  0.80 |  0.39 | SCAN     | [0.00, -0.27, -0.00]
   497 | [-3.48, -1.24, 1.50]    | [ 1.50,  0.00, -0.00]   |  1.50 |  0.42 | REROUTE  | [0.50, 0.00, -0.00]
   498 | [-3.42, -1.23, 1.50]    | [ 1.50,  0.40, -0.00]   |  1.55 |  0.40 | REROUTE  | [0.50, 0.13, -0.00]
   499 | [-3.36, -1.21, 1.50]    | [ 1.50,  0.40, -0.00]   |  1.55 |  0.36 | REROUTE  | [0.50, 0.13, -0.00]
   500 | [-3.29, -1.21, 1.50]    | [ 1.50,  0.00, -0.00]   |  1.50 |  0.33 | REROUTE  | [0.50, 0.00, -0.00]
  ```

### [Seed 1030] Configuration: Shield ON (Camera) — Outcome: `OBSTACLE_COLLISION`
- **Steps:** 23 | **Reward:** -33.28 | **Min Clearance:** 0.917 m
- **Diagnostic Cause:** Obstacle collision at speed 3.00 m/s (min clearance 2.60m).
- **Last 5 Control Steps Telemetry:**
  ```
  Step | Pos [x, y, z]           | Vel [vx, vy, vz]        | Speed | Clr   | State    | Action Executed
  -----+-------------------------+-------------------------+-------+-------+----------+----------------
    19 | [-0.44, -5.95, 1.50]    | [-0.24,  2.42, -0.02]   |  2.43 |  3.05 | NOMINAL  | [-0.08, 0.81, -0.01]
    20 | [-0.44, -5.84, 1.50]    | [-0.13,  2.72, 0.01]    |  2.73 |  2.95 | NOMINAL  | [-0.04, 0.91, 0.00]
    21 | [-0.45, -5.72, 1.50]    | [-0.12,  2.83, -0.00]   |  2.84 |  2.84 | NOMINAL  | [-0.04, 0.94, -0.00]
    22 | [-0.42, -5.60, 1.50]    | [ 0.57,  2.87, 0.01]    |  2.93 |  2.72 | NOMINAL  | [0.19, 0.96, 0.00]
    23 | [-0.35, -5.50, 1.50]    | [ 1.63,  2.52, 0.01]    |  3.00 |  2.60 | NOMINAL  | [0.55, 0.84, 0.00]
  ```

### [Seed 1031] Configuration: Shield ON (Camera) — Outcome: `OBSTACLE_COLLISION`
- **Steps:** 55 | **Reward:** 23.9 | **Min Clearance:** 0.441 m
- **Diagnostic Cause:** Obstacle collision at speed 2.15 m/s (min clearance 1.07m).
- **Last 5 Control Steps Telemetry:**
  ```
  Step | Pos [x, y, z]           | Vel [vx, vy, vz]        | Speed | Clr   | State    | Action Executed
  -----+-------------------------+-------------------------+-------+-------+----------+----------------
    51 | [ 0.90, -3.12, 1.49]    | [ 2.43,  1.49, -0.02]   |  2.85 |  1.30 | NOMINAL  | [0.81, 0.50, -0.01]
    52 | [ 0.93, -3.07, 1.49]    | [ 0.78,  1.24, 0.07]    |  1.46 |  1.22 | NOMINAL  | [0.26, 0.41, 0.02]
    53 | [ 0.84, -3.02, 1.49]    | [-2.23,  1.22, -0.10]   |  2.54 |  1.17 | NOMINAL  | [-0.74, 0.41, -0.03]
    54 | [ 0.80, -2.95, 1.49]    | [-0.87,  1.68, -0.01]   |  1.89 |  1.13 | NOMINAL  | [-0.29, 0.56, -0.01]
    55 | [ 0.75, -2.88, 1.49]    | [-1.24,  1.75, -0.04]   |  2.15 |  1.07 | NOMINAL  | [-0.41, 0.58, -0.01]
  ```

### [Seed 1032] Configuration: Shield ON (Camera) — Outcome: `OBSTACLE_COLLISION`
- **Steps:** 48 | **Reward:** -10.0 | **Min Clearance:** 0.456 m
- **Diagnostic Cause:** Obstacle collision at speed 2.90 m/s (min clearance 3.90m).
- **Last 5 Control Steps Telemetry:**
  ```
  Step | Pos [x, y, z]           | Vel [vx, vy, vz]        | Speed | Clr   | State    | Action Executed
  -----+-------------------------+-------------------------+-------+-------+----------+----------------
    44 | [-0.45, -4.89, 1.49]    | [-1.00,  2.23, 0.01]    |  2.45 |  4.27 | NOMINAL  | [-0.33, 0.74, 0.00]
    45 | [-0.46, -4.79, 1.49]    | [-0.30,  2.31, -0.01]   |  2.33 |  4.21 | NOMINAL  | [-0.10, 0.77, -0.00]
    46 | [-0.44, -4.69, 1.49]    | [ 0.57,  2.47, 0.02]    |  2.53 |  4.12 | NOMINAL  | [0.19, 0.82, 0.01]
    47 | [-0.41, -4.58, 1.49]    | [ 0.84,  2.62, 0.02]    |  2.76 |  4.01 | NOMINAL  | [0.28, 0.88, 0.01]
    48 | [-0.36, -4.46, 1.49]    | [ 0.99,  2.73, 0.02]    |  2.90 |  3.90 | NOMINAL  | [0.33, 0.91, 0.01]
  ```

### [Seed 1033] Configuration: Shield ON (Camera) — Outcome: `OBSTACLE_COLLISION`
- **Steps:** 64 | **Reward:** -25.43 | **Min Clearance:** 0.382 m
- **Diagnostic Cause:** Obstacle collision at speed 1.55 m/s (min clearance 0.38m).
- **Last 5 Control Steps Telemetry:**
  ```
  Step | Pos [x, y, z]           | Vel [vx, vy, vz]        | Speed | Clr   | State    | Action Executed
  -----+-------------------------+-------------------------+-------+-------+----------+----------------
    60 | [ 0.54, -2.73, 1.48]    | [-1.50,  0.00, 0.03]    |  1.50 |  0.43 | REROUTE  | [-0.50, 0.00, 0.01]
    61 | [ 0.48, -2.71, 1.49]    | [-1.50,  0.40, 0.03]    |  1.55 |  0.42 | REROUTE  | [-0.50, 0.13, 0.01]
    62 | [ 0.41, -2.69, 1.49]    | [-1.50,  0.40, 0.03]    |  1.55 |  0.41 | REROUTE  | [-0.50, 0.13, 0.01]
    63 | [ 0.35, -2.68, 1.49]    | [-1.50,  0.40, 0.03]    |  1.55 |  0.40 | REROUTE  | [-0.50, 0.13, 0.01]
    64 | [ 0.29, -2.66, 1.49]    | [-1.50,  0.40, 0.02]    |  1.55 |  0.38 | REROUTE  | [-0.50, 0.13, 0.01]
  ```

### [Seed 1034] Configuration: Shield ON (Camera) — Outcome: `OBSTACLE_COLLISION`
- **Steps:** 69 | **Reward:** -76.87 | **Min Clearance:** 0.429 m
- **Diagnostic Cause:** Obstacle collision at speed 1.55 m/s (min clearance 0.50m).
- **Last 5 Control Steps Telemetry:**
  ```
  Step | Pos [x, y, z]           | Vel [vx, vy, vz]        | Speed | Clr   | State    | Action Executed
  -----+-------------------------+-------------------------+-------+-------+----------+----------------
    65 | [ 0.98, -3.57, 1.49]    | [-0.43,  0.41, -0.04]   |  0.59 |  0.44 | NOMINAL  | [-0.14, 0.14, -0.01]
    66 | [ 0.98, -3.57, 1.49]    | [ 0.00,  0.00, 0.00]    |  0.00 |  0.44 | BRAKE    | [0.00, 0.00, 0.00]
    67 | [ 0.98, -3.57, 1.49]    | [ 0.00,  0.00, 0.00]    |  0.00 |  0.44 | SCAN     | [0.00, 0.00, 0.00]
    68 | [ 0.92, -3.57, 1.49]    | [-1.50,  0.00, 0.03]    |  1.50 |  0.44 | REROUTE  | [-0.50, 0.00, 0.01]
    69 | [ 0.85, -3.56, 1.49]    | [-1.50,  0.40, 0.02]    |  1.55 |  0.50 | REROUTE  | [-0.50, 0.13, 0.01]
  ```

### [Seed 1035] Configuration: Shield ON (Camera) — Outcome: `OBSTACLE_COLLISION`
- **Steps:** 43 | **Reward:** 70.76 | **Min Clearance:** 2.305 m
- **Diagnostic Cause:** Obstacle collision at speed 2.79 m/s (min clearance 2.31m).
- **Last 5 Control Steps Telemetry:**
  ```
  Step | Pos [x, y, z]           | Vel [vx, vy, vz]        | Speed | Clr   | State    | Action Executed
  -----+-------------------------+-------------------------+-------+-------+----------+----------------
    39 | [-0.54, -3.31, 1.50]    | [-0.74,  2.82, 0.02]    |  2.91 |  2.76 | NOMINAL  | [-0.25, 0.94, 0.01]
    40 | [-0.58, -3.19, 1.50]    | [-1.07,  2.77, 0.01]    |  2.97 |  2.65 | NOMINAL  | [-0.36, 0.92, 0.01]
    41 | [-0.63, -3.08, 1.50]    | [-1.11,  2.70, 0.01]    |  2.92 |  2.53 | NOMINAL  | [-0.37, 0.90, 0.01]
    42 | [-0.69, -2.97, 1.50]    | [-1.37,  2.67, 0.01]    |  3.00 |  2.42 | NOMINAL  | [-0.46, 0.89, 0.00]
    43 | [-0.73, -2.86, 1.50]    | [-0.90,  2.64, 0.03]    |  2.79 |  2.31 | NOMINAL  | [-0.30, 0.88, 0.01]
  ```

### [Seed 1036] Configuration: Shield ON (Camera) — Outcome: `OBSTACLE_COLLISION`
- **Steps:** 108 | **Reward:** -335.89 | **Min Clearance:** 0.287 m
- **Diagnostic Cause:** Obstacle collision at speed 2.50 m/s (min clearance 1.10m).
- **Last 5 Control Steps Telemetry:**
  ```
  Step | Pos [x, y, z]           | Vel [vx, vy, vz]        | Speed | Clr   | State    | Action Executed
  -----+-------------------------+-------------------------+-------+-------+----------+----------------
   104 | [-0.93, -1.93, 1.49]    | [ 1.97,  1.25, -0.02]   |  2.33 |  1.30 | NOMINAL  | [0.66, 0.42, -0.01]
   105 | [-0.99, -1.88, 1.49]    | [-1.66,  1.23, 0.03]    |  2.07 |  1.25 | NOMINAL  | [-0.55, 0.41, 0.01]
   106 | [-0.89, -1.83, 1.49]    | [ 2.46,  1.05, -0.02]   |  2.68 |  1.20 | NOMINAL  | [0.82, 0.35, -0.01]
   107 | [-0.83, -1.78, 1.49]    | [ 1.56,  1.15, -0.05]   |  1.94 |  1.15 | NOMINAL  | [0.52, 0.38, -0.02]
   108 | [-0.73, -1.74, 1.49]    | [ 2.27,  1.07, -0.03]   |  2.50 |  1.10 | NOMINAL  | [0.76, 0.36, -0.01]
  ```

### [Seed 1037] Configuration: Shield ON (Camera) — Outcome: `OBSTACLE_COLLISION`
- **Steps:** 57 | **Reward:** 70.96 | **Min Clearance:** 0.383 m
- **Diagnostic Cause:** Obstacle collision at speed 1.55 m/s (min clearance 0.38m).
- **Last 5 Control Steps Telemetry:**
  ```
  Step | Pos [x, y, z]           | Vel [vx, vy, vz]        | Speed | Clr   | State    | Action Executed
  -----+-------------------------+-------------------------+-------+-------+----------+----------------
    53 | [ 0.24, -4.09, 1.48]    | [ 0.00,  0.00, 0.00]    |  0.00 |  0.41 | BRAKE    | [0.00, 0.00, 0.00]
    54 | [ 0.24, -4.09, 1.48]    | [ 0.00,  0.00, 0.00]    |  0.00 |  0.41 | SCAN     | [0.00, 0.00, 0.00]
    55 | [ 0.30, -4.09, 1.48]    | [ 1.50,  0.00, 0.05]    |  1.50 |  0.41 | REROUTE  | [0.50, 0.00, 0.02]
    56 | [ 0.36, -4.07, 1.48]    | [ 1.50,  0.40, 0.05]    |  1.55 |  0.40 | REROUTE  | [0.50, 0.13, 0.01]
    57 | [ 0.43, -4.06, 1.48]    | [ 1.50,  0.40, 0.04]    |  1.55 |  0.38 | REROUTE  | [0.50, 0.13, 0.01]
  ```

### [Seed 1038] Configuration: Shield ON (Camera) — Outcome: `TIMEOUT`
- **Steps:** 500 | **Reward:** -2440.73 | **Min Clearance:** 0.284 m
- **Diagnostic Cause:** Exceeded maximum episode limit (500 steps) without reaching goal.
- **Last 5 Control Steps Telemetry:**
  ```
  Step | Pos [x, y, z]           | Vel [vx, vy, vz]        | Speed | Clr   | State    | Action Executed
  -----+-------------------------+-------------------------+-------+-------+----------+----------------
   496 | [ 3.63, -0.89, 1.50]    | [ 1.50,  0.00, 0.00]    |  1.50 |  0.31 | REROUTE  | [0.50, 0.00, 0.00]
   497 | [ 3.69, -0.89, 1.50]    | [ 1.50,  0.00, 0.00]    |  1.50 |  0.31 | REROUTE  | [0.50, 0.00, 0.00]
   498 | [ 3.75, -0.89, 1.50]    | [ 1.50,  0.00, 0.00]    |  1.50 |  0.30 | REROUTE  | [0.50, 0.00, 0.00]
   499 | [ 3.82, -0.89, 1.50]    | [ 1.50,  0.00, 0.00]    |  1.50 |  0.30 | REROUTE  | [0.50, 0.00, 0.00]
   500 | [ 3.88, -0.89, 1.50]    | [ 1.50,  0.00, 0.00]    |  1.50 |  0.30 | REROUTE  | [0.50, 0.00, 0.00]
  ```

### [Seed 1039] Configuration: Shield ON (Camera) — Outcome: `TIMEOUT`
- **Steps:** 500 | **Reward:** -2530.54 | **Min Clearance:** 0.252 m
- **Diagnostic Cause:** Exceeded maximum episode limit (500 steps) without reaching goal.
- **Last 5 Control Steps Telemetry:**
  ```
  Step | Pos [x, y, z]           | Vel [vx, vy, vz]        | Speed | Clr   | State    | Action Executed
  -----+-------------------------+-------------------------+-------+-------+----------+----------------
   496 | [ 3.29, -1.12, 1.50]    | [ 0.00, -0.80, 0.00]    |  0.80 |  0.52 | RETREAT  | [0.00, -0.27, 0.00]
   497 | [ 3.29, -1.15, 1.50]    | [ 0.00, -0.80, 0.00]    |  0.80 |  0.55 | SCAN     | [0.00, -0.27, 0.00]
   498 | [ 3.22, -1.15, 1.50]    | [-1.50,  0.00, 0.00]    |  1.50 |  0.59 | REROUTE  | [-0.50, 0.00, 0.00]
   499 | [ 3.16, -1.14, 1.50]    | [-1.50,  0.40, 0.00]    |  1.55 |  0.59 | REROUTE  | [-0.50, 0.13, 0.00]
   500 | [ 3.10, -1.12, 1.50]    | [-1.50,  0.40, 0.00]    |  1.55 |  0.57 | REROUTE  | [-0.50, 0.13, 0.00]
  ```

### [Seed 1040] Configuration: Shield ON (Camera) — Outcome: `TIMEOUT`
- **Steps:** 500 | **Reward:** -2813.7 | **Min Clearance:** 0.201 m
- **Diagnostic Cause:** Exceeded maximum episode limit (500 steps) without reaching goal.
- **Last 5 Control Steps Telemetry:**
  ```
  Step | Pos [x, y, z]           | Vel [vx, vy, vz]        | Speed | Clr   | State    | Action Executed
  -----+-------------------------+-------------------------+-------+-------+----------+----------------
   496 | [ 3.65, -1.01, 1.50]    | [-1.50,  0.40, -0.00]   |  1.55 |  0.42 | REROUTE  | [-0.50, 0.13, -0.00]
   497 | [ 3.58, -1.00, 1.50]    | [-1.50,  0.40, -0.00]   |  1.55 |  0.41 | REROUTE  | [-0.50, 0.13, -0.00]
   498 | [ 3.52, -0.98, 1.50]    | [-1.50,  0.40, -0.00]   |  1.55 |  0.38 | REROUTE  | [-0.50, 0.13, -0.00]
   499 | [ 3.46, -0.96, 1.50]    | [-1.50,  0.40, -0.00]   |  1.55 |  0.35 | REROUTE  | [-0.50, 0.13, -0.00]
   500 | [ 3.40, -0.96, 1.50]    | [-1.50,  0.00, -0.00]   |  1.50 |  0.33 | REROUTE  | [-0.50, 0.00, -0.00]
  ```

### [Seed 1041] Configuration: Shield ON (Camera) — Outcome: `TIMEOUT`
- **Steps:** 500 | **Reward:** -2315.76 | **Min Clearance:** 0.24 m
- **Diagnostic Cause:** Exceeded maximum episode limit (500 steps) without reaching goal.
- **Last 5 Control Steps Telemetry:**
  ```
  Step | Pos [x, y, z]           | Vel [vx, vy, vz]        | Speed | Clr   | State    | Action Executed
  -----+-------------------------+-------------------------+-------+-------+----------+----------------
   496 | [-1.82, -1.01, 1.50]    | [ 1.50,  0.40, 0.00]    |  1.55 |  0.35 | REROUTE  | [0.50, 0.13, 0.00]
   497 | [-1.75, -1.01, 1.50]    | [ 1.50,  0.00, 0.00]    |  1.50 |  0.34 | REROUTE  | [0.50, 0.00, 0.00]
   498 | [-1.69, -1.01, 1.50]    | [ 1.50,  0.00, 0.00]    |  1.50 |  0.34 | REROUTE  | [0.50, 0.00, 0.00]
   499 | [-1.63, -1.01, 1.50]    | [ 1.50,  0.00, 0.00]    |  1.50 |  0.35 | REROUTE  | [0.50, 0.00, 0.00]
   500 | [-1.57, -1.00, 1.50]    | [ 1.50,  0.40, 0.00]    |  1.55 |  0.35 | REROUTE  | [0.50, 0.13, 0.00]
  ```

### [Seed 1042] Configuration: Shield ON (Camera) — Outcome: `TIMEOUT`
- **Steps:** 500 | **Reward:** -2404.11 | **Min Clearance:** 0.273 m
- **Diagnostic Cause:** Exceeded maximum episode limit (500 steps) without reaching goal.
- **Last 5 Control Steps Telemetry:**
  ```
  Step | Pos [x, y, z]           | Vel [vx, vy, vz]        | Speed | Clr   | State    | Action Executed
  -----+-------------------------+-------------------------+-------+-------+----------+----------------
   496 | [ 2.21, -0.99, 1.50]    | [ 1.50,  0.40, 0.00]    |  1.55 |  0.43 | REROUTE  | [0.50, 0.13, 0.00]
   497 | [ 2.27, -0.97, 1.50]    | [ 1.50,  0.40, 0.00]    |  1.55 |  0.42 | REROUTE  | [0.50, 0.13, 0.00]
   498 | [ 2.33, -0.96, 1.50]    | [ 1.50,  0.40, 0.00]    |  1.55 |  0.41 | REROUTE  | [0.50, 0.13, 0.00]
   499 | [ 2.40, -0.94, 1.50]    | [ 1.50,  0.40, 0.00]    |  1.55 |  0.39 | REROUTE  | [0.50, 0.13, 0.00]
   500 | [ 2.46, -0.92, 1.50]    | [ 1.50,  0.40, 0.00]    |  1.55 |  0.38 | REROUTE  | [0.50, 0.13, 0.00]
  ```

### [Seed 1043] Configuration: Shield ON (Camera) — Outcome: `OBSTACLE_COLLISION`
- **Steps:** 81 | **Reward:** -165.27 | **Min Clearance:** 0.406 m
- **Diagnostic Cause:** Obstacle collision at speed 1.55 m/s (min clearance 0.41m).
- **Last 5 Control Steps Telemetry:**
  ```
  Step | Pos [x, y, z]           | Vel [vx, vy, vz]        | Speed | Clr   | State    | Action Executed
  -----+-------------------------+-------------------------+-------+-------+----------+----------------
    77 | [-0.35, -2.18, 1.48]    | [ 1.50,  0.40, 0.04]    |  1.55 |  0.47 | REROUTE  | [0.50, 0.13, 0.01]
    78 | [-0.28, -2.16, 1.49]    | [ 1.50,  0.40, 0.03]    |  1.55 |  0.44 | REROUTE  | [0.50, 0.13, 0.01]
    79 | [-0.22, -2.14, 1.49]    | [ 1.50,  0.40, 0.03]    |  1.55 |  0.43 | REROUTE  | [0.50, 0.13, 0.01]
    80 | [-0.16, -2.13, 1.49]    | [ 1.50,  0.40, 0.03]    |  1.55 |  0.42 | REROUTE  | [0.50, 0.13, 0.01]
    81 | [-0.10, -2.11, 1.49]    | [ 1.50,  0.40, 0.02]    |  1.55 |  0.41 | REROUTE  | [0.50, 0.13, 0.01]
  ```

### [Seed 1044] Configuration: Shield ON (Camera) — Outcome: `OBSTACLE_COLLISION`
- **Steps:** 77 | **Reward:** -133.96 | **Min Clearance:** 0.373 m
- **Diagnostic Cause:** Obstacle collision at speed 1.55 m/s (min clearance 0.37m).
- **Last 5 Control Steps Telemetry:**
  ```
  Step | Pos [x, y, z]           | Vel [vx, vy, vz]        | Speed | Clr   | State    | Action Executed
  -----+-------------------------+-------------------------+-------+-------+----------+----------------
    73 | [-0.98, -1.91, 1.49]    | [ 1.50,  0.40, 0.01]    |  1.55 |  0.44 | REROUTE  | [0.50, 0.13, 0.01]
    74 | [-0.92, -1.89, 1.49]    | [ 1.50,  0.40, 0.01]    |  1.55 |  0.41 | REROUTE  | [0.50, 0.13, 0.00]
    75 | [-0.85, -1.87, 1.50]    | [ 1.50,  0.40, 0.01]    |  1.55 |  0.40 | REROUTE  | [0.50, 0.13, 0.00]
    76 | [-0.79, -1.86, 1.50]    | [ 1.50,  0.40, 0.01]    |  1.55 |  0.39 | REROUTE  | [0.50, 0.13, 0.00]
    77 | [-0.73, -1.84, 1.50]    | [ 1.50,  0.40, 0.01]    |  1.55 |  0.37 | REROUTE  | [0.50, 0.13, 0.00]
  ```

### [Seed 1045] Configuration: Shield ON (Camera) — Outcome: `OBSTACLE_COLLISION`
- **Steps:** 48 | **Reward:** -45.5 | **Min Clearance:** 0.454 m
- **Diagnostic Cause:** Obstacle collision at speed 3.00 m/s (min clearance 3.12m).
- **Last 5 Control Steps Telemetry:**
  ```
  Step | Pos [x, y, z]           | Vel [vx, vy, vz]        | Speed | Clr   | State    | Action Executed
  -----+-------------------------+-------------------------+-------+-------+----------+----------------
    44 | [ 0.33, -4.48, 1.50]    | [ 0.84,  2.04, -0.00]   |  2.20 |  3.08 | NOMINAL  | [0.28, 0.68, -0.00]
    45 | [ 0.37, -4.39, 1.49]    | [ 1.04,  2.26, -0.02]   |  2.49 |  3.44 | NOMINAL  | [0.35, 0.75, -0.01]
    46 | [ 0.42, -4.28, 1.50]    | [ 1.24,  2.60, 0.01]    |  2.88 |  3.35 | NOMINAL  | [0.41, 0.87, 0.00]
    47 | [ 0.41, -4.16, 1.50]    | [-0.18,  2.76, 0.07]    |  2.76 |  3.24 | NOMINAL  | [-0.06, 0.92, 0.02]
    48 | [ 0.51, -4.08, 1.50]    | [ 2.31,  1.91, 0.13]    |  3.00 |  3.12 | NOMINAL  | [0.77, 0.64, 0.04]
  ```

### [Seed 1046] Configuration: Shield ON (Camera) — Outcome: `OBSTACLE_COLLISION`
- **Steps:** 38 | **Reward:** 27.22 | **Min Clearance:** 1.221 m
- **Diagnostic Cause:** Obstacle collision at speed 2.83 m/s (min clearance 1.29m).
- **Last 5 Control Steps Telemetry:**
  ```
  Step | Pos [x, y, z]           | Vel [vx, vy, vz]        | Speed | Clr   | State    | Action Executed
  -----+-------------------------+-------------------------+-------+-------+----------+----------------
    34 | [-0.74, -4.33, 1.51]    | [ 1.15,  1.66, 0.00]    |  2.02 |  1.56 | NOMINAL  | [0.38, 0.56, 0.00]
    35 | [-0.67, -4.26, 1.51]    | [ 1.62,  1.58, -0.02]   |  2.26 |  1.50 | NOMINAL  | [0.54, 0.53, -0.01]
    36 | [-0.57, -4.19, 1.50]    | [ 2.52,  1.64, -0.04]   |  3.00 |  1.43 | NOMINAL  | [0.84, 0.55, -0.01]
    37 | [-0.46, -4.13, 1.50]    | [ 2.53,  1.48, -0.06]   |  2.94 |  1.36 | NOMINAL  | [0.84, 0.49, -0.02]
    38 | [-0.36, -4.08, 1.50]    | [ 2.54,  1.25, -0.06]   |  2.83 |  1.29 | NOMINAL  | [0.85, 0.42, -0.02]
  ```

### [Seed 1047] Configuration: Shield ON (Camera) — Outcome: `TIMEOUT`
- **Steps:** 500 | **Reward:** -2559.25 | **Min Clearance:** 0.239 m
- **Diagnostic Cause:** Exceeded maximum episode limit (500 steps) without reaching goal.
- **Last 5 Control Steps Telemetry:**
  ```
  Step | Pos [x, y, z]           | Vel [vx, vy, vz]        | Speed | Clr   | State    | Action Executed
  -----+-------------------------+-------------------------+-------+-------+----------+----------------
   496 | [-2.54, -0.99, 1.50]    | [-1.50,  0.00, 0.00]    |  1.50 |  0.28 | REROUTE  | [-0.50, 0.00, 0.00]
   497 | [-2.60, -0.99, 1.50]    | [-1.50,  0.00, 0.00]    |  1.50 |  0.28 | REROUTE  | [-0.50, 0.00, 0.00]
   498 | [-2.67, -0.99, 1.50]    | [-1.50,  0.00, 0.00]    |  1.50 |  0.28 | REROUTE  | [-0.50, 0.00, 0.00]
   499 | [-2.73, -0.99, 1.50]    | [-1.50,  0.00, 0.00]    |  1.50 |  0.27 | REROUTE  | [-0.50, 0.00, 0.00]
   500 | [-2.79, -0.99, 1.50]    | [-1.50,  0.00, 0.00]    |  1.50 |  0.27 | REROUTE  | [-0.50, 0.00, 0.00]
  ```

### [Seed 1048] Configuration: Shield ON (Camera) — Outcome: `OBSTACLE_COLLISION`
- **Steps:** 51 | **Reward:** -7.12 | **Min Clearance:** 0.542 m
- **Diagnostic Cause:** Obstacle collision at speed 2.33 m/s (min clearance 1.55m).
- **Last 5 Control Steps Telemetry:**
  ```
  Step | Pos [x, y, z]           | Vel [vx, vy, vz]        | Speed | Clr   | State    | Action Executed
  -----+-------------------------+-------------------------+-------+-------+----------+----------------
    47 | [-0.18, -4.22, 1.50]    | [-0.33,  1.09, -0.00]   |  1.14 |  1.69 | NOMINAL  | [-0.11, 0.36, -0.00]
    48 | [-0.23, -4.17, 1.50]    | [-1.17,  1.18, -0.03]   |  1.66 |  1.66 | NOMINAL  | [-0.39, 0.39, -0.01]
    49 | [-0.19, -4.12, 1.50]    | [ 0.97,  1.32, -0.05]   |  1.64 |  1.68 | NOMINAL  | [0.32, 0.44, -0.02]
    50 | [-0.21, -4.06, 1.50]    | [-0.61,  1.25, -0.00]   |  1.39 |  1.57 | NOMINAL  | [-0.20, 0.42, -0.00]
    51 | [-0.13, -4.01, 1.49]    | [ 1.97,  1.25, -0.04]   |  2.33 |  1.55 | NOMINAL  | [0.66, 0.42, -0.01]
  ```

### [Seed 1049] Configuration: Shield ON (Camera) — Outcome: `OBSTACLE_COLLISION`
- **Steps:** 69 | **Reward:** -94.47 | **Min Clearance:** 0.502 m
- **Diagnostic Cause:** Obstacle collision at speed 1.93 m/s (min clearance 1.01m).
- **Last 5 Control Steps Telemetry:**
  ```
  Step | Pos [x, y, z]           | Vel [vx, vy, vz]        | Speed | Clr   | State    | Action Executed
  -----+-------------------------+-------------------------+-------+-------+----------+----------------
    65 | [ 0.31, -1.86, 1.47]    | [ 0.47,  0.83, -0.07]   |  0.96 |  0.50 | NOMINAL  | [0.16, 0.28, -0.02]
    66 | [ 0.35, -1.80, 1.47]    | [ 0.98,  1.43, 0.00]    |  1.74 |  1.18 | NOMINAL  | [0.33, 0.48, 0.00]
    67 | [ 0.41, -1.73, 1.47]    | [ 1.41,  1.59, -0.00]   |  2.12 |  1.14 | NOMINAL  | [0.47, 0.53, -0.00]
    68 | [ 0.37, -1.67, 1.47]    | [-0.89,  1.40, 0.03]    |  1.66 |  1.07 | NOMINAL  | [-0.29, 0.47, 0.01]
    69 | [ 0.31, -1.62, 1.47]    | [-1.41,  1.31, -0.02]   |  1.93 |  1.01 | NOMINAL  | [-0.47, 0.44, -0.01]
  ```
