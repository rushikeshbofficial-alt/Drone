# Stop, Hover & Re-Route (SHR) Drone Safety Shield Benchmark Report

**Date:** 2026-10-16T11:25:56Z  
**Seeds:** `5000-5049` (50 episodes)  
**Checkpoint:** `best_model_baseline.pt`  

## Executive Summary & Comparison Table

| Metric | Baseline (OFF) | Shield ON (Oracle) | Shield ON (Camera) | Target |
|---|:---:|:---:|:---:|:---:|
| **Success Rate (95% CI)** |  28.0% [17.5%, 41.7%] (14/50) | 100.0% [92.9%, 100.0%] (50/50) |  52.0% [38.5%, 65.2%] (26/50) | **>= 85.0%** |
| **Total Collision Rate** |  72.0% [58.3%, 82.5%] (36/50) |   0.0% [ 0.0%,  7.1%] (0/50) |  46.0% [33.0%, 59.6%] (23/50) | **<= 2.0%** |
| Obstacle Collisions |  72.0% [58.3%, 82.5%] (36/50) |   0.0% [ 0.0%,  7.1%] (0/50) |  46.0% [33.0%, 59.6%] (23/50) | — |
| Wall OOB Collisions |   0.0% [ 0.0%,  7.1%] (0/50) |   0.0% [ 0.0%,  7.1%] (0/50) |   0.0% [ 0.0%,  7.1%] (0/50) | — |
| Timeout Rate |   0.0% [ 0.0%,  7.1%] (0/50) |   0.0% [ 0.0%,  7.1%] (0/50) |   2.0% [ 0.4%, 10.5%] (1/50) | **<= 5.0%** |
| **Mean Reward** | -9.41 +/- 161.40 | -215.74 +/- 281.48 | -448.68 +/- 436.44 | — |
| **Mean Min Clearance** | 0.13 m | 0.36 m | 0.27 m | — |
| **Mean Episode Steps** | 90.0 | 246.9 | 208.1 | — |
| **Standoff Distance** | N/A | 1.84 m | 0.57 m | **>= 0.45 m** |
| **Step Overhead (Baseline Succ)** | Baseline | 45.79% | 51.72% | **<= 15.0%** |

## Acceptance Criteria Audit

| Criterion | Target | Achieved (Oracle) | Verdict |
|---|:---:|:---:|:---:|
| Total Collisions <= 2.0% | <= 2.0% | 0.0% | **✅ PASS** |
| Success Rate >= 85.0% | >= 85.0% | 100.0% | **✅ PASS** |
| Timeout Rate <= 5.0% | <= 5.0% | 0.0% | **✅ PASS** |
| Standoff Distance >= 0.45m | >= 0.45 m | 1.84 m | **✅ PASS** |
| Step Overhead on Baseline-Success <= 15.0% | <= 15.0% | 45.8% | **❌ FAIL** |

**Overall Status:** ⚠️ **ACTION REQUIRED: CRITERIA UNMET**

## Crash Forensics Log

Total non-success episodes analyzed: **60**

### [Seed 5001] Configuration: Baseline (Shield OFF) — Outcome: `OBSTACLE_COLLISION`
- **Steps:** 41 | **Reward:** 6.21 | **Min Clearance:** 0.3 m
- **Diagnostic Cause:** Obstacle collision at speed 3.17 m/s (min clearance 0.36m).
- **Last 5 Control Steps Telemetry:**
  ```
  Step | Pos [x, y, z]           | Vel [vx, vy, vz]        | Speed | Clr   | State    | Action Executed
  -----+-------------------------+-------------------------+-------+-------+----------+----------------
    37 | [ 1.00, -3.83, 1.49]    | [ 2.79,  1.86, -0.02]   |  3.35 |  0.30 | DISABLED | [0.93, 0.62, -0.01]
    38 | [ 1.06, -3.77, 1.49]    | [ 1.65,  1.62, 0.07]    |  2.31 |  0.30 | DISABLED | [0.55, 0.54, 0.03]
    39 | [ 1.14, -3.69, 1.49]    | [ 1.88,  1.83, 0.00]    |  2.62 |  0.30 | DISABLED | [0.63, 0.61, 0.00]
    40 | [ 1.25, -3.63, 1.49]    | [ 2.68,  1.51, 0.02]    |  3.08 |  0.37 | DISABLED | [0.89, 0.50, 0.01]
    41 | [ 1.37, -3.57, 1.49]    | [ 2.85,  1.40, 0.04]    |  3.17 |  0.36 | DISABLED | [0.95, 0.47, 0.01]
  ```

### [Seed 5002] Configuration: Baseline (Shield OFF) — Outcome: `OBSTACLE_COLLISION`
- **Steps:** 43 | **Reward:** 69.1 | **Min Clearance:** 0.124 m
- **Diagnostic Cause:** Obstacle collision at speed 2.77 m/s (min clearance 0.15m).
- **Last 5 Control Steps Telemetry:**
  ```
  Step | Pos [x, y, z]           | Vel [vx, vy, vz]        | Speed | Clr   | State    | Action Executed
  -----+-------------------------+-------------------------+-------+-------+----------+----------------
    39 | [ 0.07, -3.33, 1.50]    | [-0.23,  2.80, -0.03]   |  2.81 |  0.26 | DISABLED | [-0.08, 0.93, -0.01]
    40 | [ 0.08, -3.22, 1.50]    | [ 0.17,  2.79, -0.01]   |  2.80 |  0.17 | DISABLED | [0.06, 0.93, -0.00]
    41 | [ 0.14, -3.10, 1.50]    | [ 1.39,  2.73, -0.00]   |  3.06 |  0.12 | DISABLED | [0.46, 0.91, -0.00]
    42 | [ 0.12, -3.00, 1.50]    | [-0.56,  2.54, 0.03]    |  2.60 |  0.14 | DISABLED | [-0.19, 0.84, 0.01]
    43 | [ 0.08, -2.89, 1.50]    | [-0.79,  2.65, 0.01]    |  2.77 |  0.15 | DISABLED | [-0.26, 0.89, 0.00]
  ```

### [Seed 5003] Configuration: Baseline (Shield OFF) — Outcome: `OBSTACLE_COLLISION`
- **Steps:** 56 | **Reward:** -7.36 | **Min Clearance:** 0.119 m
- **Diagnostic Cause:** Obstacle collision at speed 3.18 m/s (min clearance 0.15m).
- **Last 5 Control Steps Telemetry:**
  ```
  Step | Pos [x, y, z]           | Vel [vx, vy, vz]        | Speed | Clr   | State    | Action Executed
  -----+-------------------------+-------------------------+-------+-------+----------+----------------
    52 | [ 0.05, -1.91, 1.50]    | [ 0.66,  2.60, 0.00]    |  2.68 |  0.16 | DISABLED | [0.22, 0.87, 0.00]
    53 | [ 0.11, -1.81, 1.50]    | [ 1.41,  2.50, 0.01]    |  2.87 |  0.18 | DISABLED | [0.47, 0.83, 0.00]
    54 | [ 0.21, -1.70, 1.50]    | [ 2.26,  2.46, -0.00]   |  3.35 |  0.14 | DISABLED | [0.75, 0.82, -0.00]
    55 | [ 0.15, -1.60, 1.49]    | [-1.38,  2.40, -0.03]   |  2.76 |  0.14 | DISABLED | [-0.46, 0.80, -0.01]
    56 | [ 0.24, -1.51, 1.49]    | [ 2.18,  2.32, -0.02]   |  3.18 |  0.15 | DISABLED | [0.73, 0.77, -0.01]
  ```

### [Seed 5004] Configuration: Baseline (Shield OFF) — Outcome: `OBSTACLE_COLLISION`
- **Steps:** 41 | **Reward:** 84.6 | **Min Clearance:** 0.233 m
- **Diagnostic Cause:** Obstacle collision at speed 2.17 m/s (min clearance 0.23m).
- **Last 5 Control Steps Telemetry:**
  ```
  Step | Pos [x, y, z]           | Vel [vx, vy, vz]        | Speed | Clr   | State    | Action Executed
  -----+-------------------------+-------------------------+-------+-------+----------+----------------
    37 | [ 0.49, -3.76, 1.50]    | [ 2.10,  2.12, 0.02]    |  2.98 |  0.54 | DISABLED | [0.70, 0.70, 0.01]
    38 | [ 0.59, -3.68, 1.50]    | [ 2.36,  2.02, -0.01]   |  3.10 |  0.43 | DISABLED | [0.79, 0.67, -0.00]
    39 | [ 0.66, -3.60, 1.50]    | [ 1.75,  1.91, -0.01]   |  2.60 |  0.34 | DISABLED | [0.58, 0.64, -0.01]
    40 | [ 0.56, -3.52, 1.50]    | [-2.39,  1.78, 0.11]    |  2.98 |  0.28 | DISABLED | [-0.80, 0.59, 0.04]
    41 | [ 0.61, -3.45, 1.50]    | [ 1.12,  1.85, -0.03]   |  2.17 |  0.23 | DISABLED | [0.37, 0.62, -0.01]
  ```

### [Seed 5007] Configuration: Baseline (Shield OFF) — Outcome: `OBSTACLE_COLLISION`
- **Steps:** 47 | **Reward:** -2.97 | **Min Clearance:** 0.136 m
- **Diagnostic Cause:** Obstacle collision at speed 3.66 m/s (min clearance 0.14m).
- **Last 5 Control Steps Telemetry:**
  ```
  Step | Pos [x, y, z]           | Vel [vx, vy, vz]        | Speed | Clr   | State    | Action Executed
  -----+-------------------------+-------------------------+-------+-------+----------+----------------
    43 | [ 0.31, -3.06, 1.52]    | [ 0.21,  2.70, 0.03]    |  2.71 |  0.14 | DISABLED | [0.07, 0.90, 0.01]
    44 | [ 0.34, -2.95, 1.52]    | [ 0.65,  2.69, 0.03]    |  2.77 |  0.15 | DISABLED | [0.22, 0.90, 0.01]
    45 | [ 0.38, -2.85, 1.52]    | [ 1.12,  2.56, -0.02]   |  2.80 |  0.14 | DISABLED | [0.38, 0.85, -0.01]
    46 | [ 0.46, -2.75, 1.52]    | [ 1.91,  2.43, 0.02]    |  3.09 |  0.15 | DISABLED | [0.64, 0.81, 0.01]
    47 | [ 0.34, -2.65, 1.52]    | [-2.95,  2.18, -0.02]   |  3.66 |  0.14 | DISABLED | [-0.98, 0.72, -0.01]
  ```

### [Seed 5009] Configuration: Baseline (Shield OFF) — Outcome: `OBSTACLE_COLLISION`
- **Steps:** 123 | **Reward:** -315.3 | **Min Clearance:** 0.109 m
- **Diagnostic Cause:** Obstacle collision at speed 1.97 m/s (min clearance 0.21m).
- **Last 5 Control Steps Telemetry:**
  ```
  Step | Pos [x, y, z]           | Vel [vx, vy, vz]        | Speed | Clr   | State    | Action Executed
  -----+-------------------------+-------------------------+-------+-------+----------+----------------
   119 | [-1.75,  3.88, 1.48]    | [ 0.69,  1.18, -0.04]   |  1.36 |  0.36 | DISABLED | [0.23, 0.39, -0.01]
   120 | [-1.79,  3.93, 1.48]    | [-0.87,  1.32, 0.02]    |  1.58 |  0.30 | DISABLED | [-0.29, 0.44, 0.01]
   121 | [-1.76,  3.98, 1.48]    | [ 0.81,  1.28, -0.02]   |  1.51 |  0.28 | DISABLED | [0.27, 0.43, -0.01]
   122 | [-1.71,  4.04, 1.48]    | [ 1.18,  1.43, -0.02]   |  1.86 |  0.29 | DISABLED | [0.39, 0.48, -0.01]
   123 | [-1.75,  4.11, 1.48]    | [-1.09,  1.64, -0.04]   |  1.97 |  0.21 | DISABLED | [-0.36, 0.55, -0.01]
  ```

### [Seed 5010] Configuration: Baseline (Shield OFF) — Outcome: `OBSTACLE_COLLISION`
- **Steps:** 93 | **Reward:** -188.95 | **Min Clearance:** 0.111 m
- **Diagnostic Cause:** Obstacle collision at speed 2.73 m/s (min clearance 0.13m).
- **Last 5 Control Steps Telemetry:**
  ```
  Step | Pos [x, y, z]           | Vel [vx, vy, vz]        | Speed | Clr   | State    | Action Executed
  -----+-------------------------+-------------------------+-------+-------+----------+----------------
    89 | [-1.08,  0.52, 1.50]    | [ 2.23,  2.21, 0.01]    |  3.14 |  0.14 | DISABLED | [0.74, 0.73, 0.00]
    90 | [-0.98,  0.60, 1.50]    | [ 2.29,  2.13, -0.06]   |  3.13 |  0.15 | DISABLED | [0.77, 0.71, -0.02]
    91 | [-0.88,  0.69, 1.50]    | [ 2.55,  1.98, -0.03]   |  3.23 |  0.15 | DISABLED | [0.85, 0.66, -0.01]
    92 | [-0.92,  0.77, 1.50]    | [-0.97,  1.95, 0.01]    |  2.17 |  0.14 | DISABLED | [-0.32, 0.65, 0.00]
    93 | [-0.84,  0.85, 1.49]    | [ 1.78,  2.07, -0.03]   |  2.73 |  0.13 | DISABLED | [0.59, 0.69, -0.01]
  ```

### [Seed 5013] Configuration: Baseline (Shield OFF) — Outcome: `OBSTACLE_COLLISION`
- **Steps:** 159 | **Reward:** -507.57 | **Min Clearance:** 0.055 m
- **Diagnostic Cause:** Obstacle collision at speed 2.79 m/s (min clearance 0.25m).
- **Last 5 Control Steps Telemetry:**
  ```
  Step | Pos [x, y, z]           | Vel [vx, vy, vz]        | Speed | Clr   | State    | Action Executed
  -----+-------------------------+-------------------------+-------+-------+----------+----------------
   155 | [ 1.44,  2.56, 1.62]    | [-0.56,  2.07, 0.00]    |  2.14 |  0.39 | DISABLED | [-0.18, 0.69, 0.00]
   156 | [ 1.46,  2.66, 1.62]    | [ 0.59,  2.17, -0.01]   |  2.25 |  0.40 | DISABLED | [0.20, 0.72, -0.00]
   157 | [ 1.42,  2.75, 1.62]    | [-1.10,  2.28, 0.03]    |  2.54 |  0.39 | DISABLED | [-0.37, 0.76, 0.01]
   158 | [ 1.46,  2.85, 1.62]    | [ 1.07,  2.38, -0.06]   |  2.62 |  0.33 | DISABLED | [0.36, 0.80, -0.02]
   159 | [ 1.52,  2.95, 1.62]    | [ 1.40,  2.42, -0.00]   |  2.79 |  0.25 | DISABLED | [0.47, 0.81, -0.00]
  ```

### [Seed 5014] Configuration: Baseline (Shield OFF) — Outcome: `OBSTACLE_COLLISION`
- **Steps:** 64 | **Reward:** -58.53 | **Min Clearance:** 0.125 m
- **Diagnostic Cause:** Obstacle collision at speed 3.43 m/s (min clearance 0.15m).
- **Last 5 Control Steps Telemetry:**
  ```
  Step | Pos [x, y, z]           | Vel [vx, vy, vz]        | Speed | Clr   | State    | Action Executed
  -----+-------------------------+-------------------------+-------+-------+----------+----------------
    60 | [ 0.11, -1.70, 1.48]    | [-0.56,  1.89, -0.01]   |  1.97 |  0.14 | DISABLED | [-0.18, 0.63, -0.00]
    61 | [ 0.20, -1.62, 1.48]    | [ 2.37,  1.80, -0.02]   |  2.98 |  0.15 | DISABLED | [0.79, 0.60, -0.01]
    62 | [ 0.26, -1.55, 1.48]    | [ 1.33,  1.80, -0.04]   |  2.24 |  0.14 | DISABLED | [0.45, 0.60, -0.01]
    63 | [ 0.34, -1.47, 1.48]    | [ 2.00,  1.94, -0.02]   |  2.79 |  0.14 | DISABLED | [0.67, 0.65, -0.01]
    64 | [ 0.47, -1.39, 1.48]    | [ 2.97,  1.72, 0.05]    |  3.43 |  0.15 | DISABLED | [0.99, 0.57, 0.02]
  ```

### [Seed 5016] Configuration: Baseline (Shield OFF) — Outcome: `OBSTACLE_COLLISION`
- **Steps:** 59 | **Reward:** 0.45 | **Min Clearance:** 0.187 m
- **Diagnostic Cause:** Obstacle collision at speed 2.69 m/s (min clearance 0.19m).
- **Last 5 Control Steps Telemetry:**
  ```
  Step | Pos [x, y, z]           | Vel [vx, vy, vz]        | Speed | Clr   | State    | Action Executed
  -----+-------------------------+-------------------------+-------+-------+----------+----------------
    55 | [ 0.14, -3.46, 1.49]    | [ 2.31,  1.30, -0.04]   |  2.65 |  0.29 | DISABLED | [0.77, 0.43, -0.01]
    56 | [ 0.26, -3.41, 1.49]    | [ 2.95,  1.16, -0.02]   |  3.17 |  0.32 | DISABLED | [0.98, 0.39, -0.01]
    57 | [ 0.38, -3.34, 1.49]    | [ 2.87,  1.66, -0.01]   |  3.31 |  0.28 | DISABLED | [0.95, 0.55, -0.00]
    58 | [ 0.30, -3.27, 1.49]    | [-1.81,  1.63, -0.04]   |  2.44 |  0.21 | DISABLED | [-0.60, 0.54, -0.01]
    59 | [ 0.21, -3.21, 1.49]    | [-2.23,  1.50, 0.02]    |  2.69 |  0.19 | DISABLED | [-0.74, 0.50, 0.01]
  ```

### [Seed 5018] Configuration: Baseline (Shield OFF) — Outcome: `OBSTACLE_COLLISION`
- **Steps:** 56 | **Reward:** -3.46 | **Min Clearance:** 0.132 m
- **Diagnostic Cause:** Obstacle collision at speed 1.57 m/s (min clearance 0.15m).
- **Last 5 Control Steps Telemetry:**
  ```
  Step | Pos [x, y, z]           | Vel [vx, vy, vz]        | Speed | Clr   | State    | Action Executed
  -----+-------------------------+-------------------------+-------+-------+----------+----------------
    52 | [ 0.10, -2.31, 1.50]    | [ 2.63,  1.09, -0.03]   |  2.85 |  0.15 | DISABLED | [0.88, 0.36, -0.01]
    53 | [ 0.04, -2.26, 1.50]    | [-1.24,  1.18, 0.05]    |  1.71 |  0.15 | DISABLED | [-0.41, 0.39, 0.02]
    54 | [ 0.04, -2.22, 1.50]    | [-0.06,  1.12, -0.01]   |  1.12 |  0.17 | DISABLED | [-0.02, 0.37, -0.01]
    55 | [ 0.07, -2.18, 1.50]    | [ 0.63,  0.87, -0.02]   |  1.07 |  0.14 | DISABLED | [0.21, 0.29, -0.01]
    56 | [ 0.02, -2.13, 1.50]    | [-1.06,  1.15, 0.01]    |  1.57 |  0.15 | DISABLED | [-0.35, 0.38, 0.01]
  ```

### [Seed 5019] Configuration: Baseline (Shield OFF) — Outcome: `OBSTACLE_COLLISION`
- **Steps:** 91 | **Reward:** -170.45 | **Min Clearance:** 0.102 m
- **Diagnostic Cause:** Obstacle collision at speed 2.96 m/s (min clearance 0.38m).
- **Last 5 Control Steps Telemetry:**
  ```
  Step | Pos [x, y, z]           | Vel [vx, vy, vz]        | Speed | Clr   | State    | Action Executed
  -----+-------------------------+-------------------------+-------+-------+----------+----------------
    87 | [ 2.02,  1.60, 1.51]    | [-0.97,  2.90, 0.03]    |  3.06 |  0.14 | DISABLED | [-0.33, 0.97, 0.01]
    88 | [ 2.01,  1.71, 1.50]    | [-0.22,  2.78, -0.02]   |  2.79 |  0.12 | DISABLED | [-0.07, 0.93, -0.01]
    89 | [ 2.00,  1.83, 1.51]    | [-0.08,  2.83, 0.03]    |  2.83 |  0.32 | DISABLED | [-0.03, 0.94, 0.01]
    90 | [ 1.99,  1.95, 1.51]    | [-0.23,  2.88, -0.01]   |  2.89 |  0.40 | DISABLED | [-0.08, 0.96, -0.00]
    91 | [ 1.96,  2.07, 1.50]    | [-0.72,  2.87, -0.01]   |  2.96 |  0.38 | DISABLED | [-0.24, 0.95, -0.01]
  ```

### [Seed 5021] Configuration: Baseline (Shield OFF) — Outcome: `OBSTACLE_COLLISION`
- **Steps:** 77 | **Reward:** -93.69 | **Min Clearance:** 0.078 m
- **Diagnostic Cause:** Obstacle collision at speed 1.88 m/s (min clearance 0.08m).
- **Last 5 Control Steps Telemetry:**
  ```
  Step | Pos [x, y, z]           | Vel [vx, vy, vz]        | Speed | Clr   | State    | Action Executed
  -----+-------------------------+-------------------------+-------+-------+----------+----------------
    73 | [-1.12, -0.28, 1.49]    | [ 2.10,  2.18, -0.03]   |  3.02 |  0.14 | DISABLED | [0.70, 0.73, -0.01]
    74 | [-1.04, -0.19, 1.49]    | [ 2.10,  2.17, 0.02]    |  3.02 |  0.12 | DISABLED | [0.70, 0.72, 0.01]
    75 | [-0.92, -0.11, 1.49]    | [ 2.86,  1.97, 0.03]    |  3.47 |  0.25 | DISABLED | [0.95, 0.66, 0.01]
    76 | [-0.88, -0.03, 1.49]    | [ 0.99,  1.85, 0.01]    |  2.10 |  0.18 | DISABLED | [0.33, 0.62, 0.00]
    77 | [-0.84,  0.04, 1.49]    | [ 0.88,  1.66, 0.02]    |  1.88 |  0.08 | DISABLED | [0.29, 0.55, 0.01]
  ```

### [Seed 5023] Configuration: Baseline (Shield OFF) — Outcome: `OBSTACLE_COLLISION`
- **Steps:** 68 | **Reward:** -98.31 | **Min Clearance:** 0.118 m
- **Diagnostic Cause:** Obstacle collision at speed 3.11 m/s (min clearance 0.14m).
- **Last 5 Control Steps Telemetry:**
  ```
  Step | Pos [x, y, z]           | Vel [vx, vy, vz]        | Speed | Clr   | State    | Action Executed
  -----+-------------------------+-------------------------+-------+-------+----------+----------------
    64 | [-1.05, -1.54, 1.49]    | [-2.48,  1.83, 0.04]    |  3.08 |  0.15 | DISABLED | [-0.83, 0.61, 0.01]
    65 | [-1.16, -1.47, 1.49]    | [-2.55,  1.74, 0.05]    |  3.09 |  0.14 | DISABLED | [-0.85, 0.58, 0.02]
    66 | [-1.26, -1.40, 1.49]    | [-2.41,  1.72, 0.03]    |  2.96 |  0.14 | DISABLED | [-0.80, 0.57, 0.01]
    67 | [-1.38, -1.33, 1.49]    | [-2.99,  1.58, -0.02]   |  3.38 |  0.14 | DISABLED | [-1.00, 0.53, -0.01]
    68 | [-1.50, -1.27, 1.49]    | [-2.78,  1.39, -0.05]   |  3.11 |  0.14 | DISABLED | [-0.93, 0.46, -0.02]
  ```

### [Seed 5024] Configuration: Baseline (Shield OFF) — Outcome: `OBSTACLE_COLLISION`
- **Steps:** 66 | **Reward:** -112.31 | **Min Clearance:** 0.121 m
- **Diagnostic Cause:** Obstacle collision at speed 2.74 m/s (min clearance 0.13m).
- **Last 5 Control Steps Telemetry:**
  ```
  Step | Pos [x, y, z]           | Vel [vx, vy, vz]        | Speed | Clr   | State    | Action Executed
  -----+-------------------------+-------------------------+-------+-------+----------+----------------
    62 | [-0.87, -1.10, 1.51]    | [-1.24,  2.51, 0.06]    |  2.80 |  0.15 | DISABLED | [-0.41, 0.84, 0.02]
    63 | [-0.81, -1.02, 1.52]    | [ 1.62,  1.86, 0.18]    |  2.47 |  0.13 | DISABLED | [0.54, 0.62, 0.06]
    64 | [-0.91, -0.95, 1.52]    | [-2.45,  1.77, 0.01]    |  3.02 |  0.14 | DISABLED | [-0.82, 0.59, 0.00]
    65 | [-0.81, -0.88, 1.52]    | [ 2.32,  1.75, -0.03]   |  2.91 |  0.13 | DISABLED | [0.77, 0.58, -0.01]
    66 | [-0.90, -0.80, 1.52]    | [-2.07,  1.80, 0.02]    |  2.74 |  0.13 | DISABLED | [-0.69, 0.60, 0.01]
  ```

### [Seed 5026] Configuration: Baseline (Shield OFF) — Outcome: `OBSTACLE_COLLISION`
- **Steps:** 42 | **Reward:** 83.57 | **Min Clearance:** 0.167 m
- **Diagnostic Cause:** Obstacle collision at speed 2.41 m/s (min clearance 0.17m).
- **Last 5 Control Steps Telemetry:**
  ```
  Step | Pos [x, y, z]           | Vel [vx, vy, vz]        | Speed | Clr   | State    | Action Executed
  -----+-------------------------+-------------------------+-------+-------+----------+----------------
    38 | [-0.12, -3.72, 1.50]    | [-0.07,  1.93, 0.01]    |  1.93 |  0.56 | DISABLED | [-0.02, 0.64, 0.00]
    39 | [-0.12, -3.63, 1.50]    | [-0.12,  2.16, 0.01]    |  2.16 |  0.46 | DISABLED | [-0.04, 0.72, 0.01]
    40 | [-0.07, -3.53, 1.50]    | [ 1.40,  2.29, -0.03]   |  2.69 |  0.37 | DISABLED | [0.47, 0.76, -0.01]
    41 | [ 0.01, -3.43, 1.50]    | [ 1.74,  2.40, 0.03]    |  2.96 |  0.27 | DISABLED | [0.58, 0.80, 0.01]
    42 | [ 0.00, -3.33, 1.50]    | [-0.08,  2.41, -0.01]   |  2.41 |  0.17 | DISABLED | [-0.03, 0.80, -0.00]
  ```

### [Seed 5027] Configuration: Baseline (Shield OFF) — Outcome: `OBSTACLE_COLLISION`
- **Steps:** 62 | **Reward:** -47.83 | **Min Clearance:** 0.126 m
- **Diagnostic Cause:** Obstacle collision at speed 3.51 m/s (min clearance 0.16m).
- **Last 5 Control Steps Telemetry:**
  ```
  Step | Pos [x, y, z]           | Vel [vx, vy, vz]        | Speed | Clr   | State    | Action Executed
  -----+-------------------------+-------------------------+-------+-------+----------+----------------
    58 | [-0.03, -1.39, 1.50]    | [ 0.19,  1.89, 0.01]    |  1.90 |  0.17 | DISABLED | [0.06, 0.63, 0.01]
    59 | [-0.03, -1.29, 1.50]    | [ 0.12,  2.38, -0.01]   |  2.38 |  0.15 | DISABLED | [0.04, 0.79, -0.00]
    60 | [ 0.10, -1.20, 1.50]    | [ 2.88,  2.27, 0.01]    |  3.67 |  0.18 | DISABLED | [0.96, 0.76, 0.00]
    61 | [ 0.22, -1.10, 1.50]    | [ 2.91,  2.21, -0.03]   |  3.66 |  0.15 | DISABLED | [0.97, 0.74, -0.01]
    62 | [ 0.09, -1.03, 1.50]    | [-2.99,  1.83, -0.01]   |  3.51 |  0.16 | DISABLED | [-1.00, 0.61, -0.00]
  ```

### [Seed 5028] Configuration: Baseline (Shield OFF) — Outcome: `OBSTACLE_COLLISION`
- **Steps:** 52 | **Reward:** -8.79 | **Min Clearance:** 0.126 m
- **Diagnostic Cause:** Obstacle collision at speed 3.55 m/s (min clearance 0.17m).
- **Last 5 Control Steps Telemetry:**
  ```
  Step | Pos [x, y, z]           | Vel [vx, vy, vz]        | Speed | Clr   | State    | Action Executed
  -----+-------------------------+-------------------------+-------+-------+----------+----------------
    48 | [ 0.38, -2.69, 1.50]    | [ 1.22,  2.13, 0.04]    |  2.46 |  0.15 | DISABLED | [0.41, 0.71, 0.01]
    49 | [ 0.46, -2.60, 1.50]    | [ 1.94,  2.11, -0.02]   |  2.87 |  0.13 | DISABLED | [0.65, 0.70, -0.01]
    50 | [ 0.35, -2.52, 1.50]    | [-2.67,  1.93, -0.01]   |  3.29 |  0.13 | DISABLED | [-0.89, 0.64, -0.00]
    51 | [ 0.22, -2.44, 1.49]    | [-2.96,  1.89, -0.06]   |  3.51 |  0.13 | DISABLED | [-0.99, 0.63, -0.02]
    52 | [ 0.35, -2.36, 1.50]    | [ 2.97,  1.96, 0.04]    |  3.55 |  0.17 | DISABLED | [0.99, 0.65, 0.01]
  ```

### [Seed 5029] Configuration: Baseline (Shield OFF) — Outcome: `OBSTACLE_COLLISION`
- **Steps:** 60 | **Reward:** -154.68 | **Min Clearance:** 0.141 m
- **Diagnostic Cause:** Obstacle collision at speed 2.11 m/s (min clearance 0.14m).
- **Last 5 Control Steps Telemetry:**
  ```
  Step | Pos [x, y, z]           | Vel [vx, vy, vz]        | Speed | Clr   | State    | Action Executed
  -----+-------------------------+-------------------------+-------+-------+----------+----------------
    56 | [ 1.46, -2.42, 1.52]    | [-1.23,  1.30, -0.02]   |  1.79 |  0.20 | DISABLED | [-0.41, 0.43, -0.01]
    57 | [ 1.43, -2.36, 1.52]    | [-0.83,  1.23, -0.03]   |  1.49 |  0.14 | DISABLED | [-0.28, 0.41, -0.01]
    58 | [ 1.53, -2.31, 1.52]    | [ 2.58,  1.40, -0.02]   |  2.94 |  0.15 | DISABLED | [0.86, 0.47, -0.01]
    59 | [ 1.64, -2.25, 1.52]    | [ 2.58,  1.47, -0.01]   |  2.97 |  0.15 | DISABLED | [0.86, 0.49, -0.00]
    60 | [ 1.69, -2.17, 1.52]    | [ 1.26,  1.69, 0.05]    |  2.11 |  0.14 | DISABLED | [0.42, 0.56, 0.02]
  ```

### [Seed 5030] Configuration: Baseline (Shield OFF) — Outcome: `OBSTACLE_COLLISION`
- **Steps:** 63 | **Reward:** -178.81 | **Min Clearance:** 0.115 m
- **Diagnostic Cause:** Obstacle collision at speed 3.52 m/s (min clearance 0.12m).
- **Last 5 Control Steps Telemetry:**
  ```
  Step | Pos [x, y, z]           | Vel [vx, vy, vz]        | Speed | Clr   | State    | Action Executed
  -----+-------------------------+-------------------------+-------+-------+----------+----------------
    59 | [ 1.37, -1.54, 1.51]    | [ 0.26,  2.57, 0.00]    |  2.58 |  0.12 | DISABLED | [0.09, 0.86, 0.00]
    60 | [ 1.38, -1.43, 1.51]    | [ 0.33,  2.63, 0.01]    |  2.65 |  0.12 | DISABLED | [0.11, 0.88, 0.00]
    61 | [ 1.28, -1.33, 1.52]    | [-2.47,  2.35, 0.05]    |  3.41 |  0.12 | DISABLED | [-0.82, 0.78, 0.02]
    62 | [ 1.33, -1.24, 1.52]    | [ 1.27,  2.17, -0.01]   |  2.51 |  0.14 | DISABLED | [0.42, 0.72, -0.00]
    63 | [ 1.22, -1.15, 1.52]    | [-2.76,  2.19, -0.02]   |  3.52 |  0.12 | DISABLED | [-0.92, 0.73, -0.01]
  ```

### [Seed 5031] Configuration: Baseline (Shield OFF) — Outcome: `OBSTACLE_COLLISION`
- **Steps:** 50 | **Reward:** 39.14 | **Min Clearance:** 0.131 m
- **Diagnostic Cause:** Obstacle collision at speed 3.06 m/s (min clearance 0.14m).
- **Last 5 Control Steps Telemetry:**
  ```
  Step | Pos [x, y, z]           | Vel [vx, vy, vz]        | Speed | Clr   | State    | Action Executed
  -----+-------------------------+-------------------------+-------+-------+----------+----------------
    46 | [-0.04, -2.66, 1.49]    | [-1.85,  2.33, 0.00]    |  2.98 |  0.14 | DISABLED | [-0.62, 0.78, 0.00]
    47 | [-0.06, -2.56, 1.49]    | [-0.67,  2.32, -0.02]   |  2.42 |  0.14 | DISABLED | [-0.23, 0.77, -0.01]
    48 | [-0.04, -2.46, 1.49]    | [ 0.44,  2.48, 0.01]    |  2.52 |  0.13 | DISABLED | [0.15, 0.83, 0.01]
    49 | [ 0.03, -2.36, 1.49]    | [ 1.70,  2.54, 0.01]    |  3.05 |  0.14 | DISABLED | [0.56, 0.84, 0.01]
    50 | [ 0.11, -2.26, 1.49]    | [ 1.96,  2.35, -0.09]   |  3.06 |  0.14 | DISABLED | [0.65, 0.78, -0.03]
  ```

### [Seed 5032] Configuration: Baseline (Shield OFF) — Outcome: `OBSTACLE_COLLISION`
- **Steps:** 84 | **Reward:** -201.79 | **Min Clearance:** 0.122 m
- **Diagnostic Cause:** Obstacle collision at speed 2.72 m/s (min clearance 0.14m).
- **Last 5 Control Steps Telemetry:**
  ```
  Step | Pos [x, y, z]           | Vel [vx, vy, vz]        | Speed | Clr   | State    | Action Executed
  -----+-------------------------+-------------------------+-------+-------+----------+----------------
    80 | [-0.46, -0.21, 1.49]    | [-2.63,  1.71, 0.02]    |  3.14 |  0.17 | DISABLED | [-0.88, 0.57, 0.01]
    81 | [-0.57, -0.13, 1.49]    | [-2.60,  1.87, -0.03]   |  3.20 |  0.28 | DISABLED | [-0.87, 0.62, -0.01]
    82 | [-0.50, -0.04, 1.49]    | [ 1.73,  2.09, 0.03]    |  2.71 |  0.20 | DISABLED | [0.58, 0.69, 0.01]
    83 | [-0.52,  0.04, 1.49]    | [-0.54,  1.97, 0.02]    |  2.04 |  0.14 | DISABLED | [-0.18, 0.66, 0.01]
    84 | [-0.44,  0.12, 1.49]    | [ 1.82,  2.03, 0.01]    |  2.72 |  0.14 | DISABLED | [0.61, 0.68, 0.00]
  ```

### [Seed 5033] Configuration: Baseline (Shield OFF) — Outcome: `OBSTACLE_COLLISION`
- **Steps:** 75 | **Reward:** -105.59 | **Min Clearance:** 0.115 m
- **Diagnostic Cause:** Obstacle collision at speed 2.91 m/s (min clearance 0.16m).
- **Last 5 Control Steps Telemetry:**
  ```
  Step | Pos [x, y, z]           | Vel [vx, vy, vz]        | Speed | Clr   | State    | Action Executed
  -----+-------------------------+-------------------------+-------+-------+----------+----------------
    71 | [-0.04, -0.82, 1.49]    | [ 2.18,  1.45, -0.01]   |  2.62 |  0.18 | DISABLED | [0.73, 0.48, -0.00]
    72 | [ 0.06, -0.76, 1.49]    | [ 2.40,  1.44, -0.00]   |  2.80 |  0.15 | DISABLED | [0.80, 0.48, -0.00]
    73 | [-0.04, -0.69, 1.49]    | [-2.22,  1.59, -0.01]   |  2.73 |  0.14 | DISABLED | [-0.74, 0.53, -0.00]
    74 | [-0.13, -0.63, 1.49]    | [-2.22,  1.52, 0.00]    |  2.69 |  0.15 | DISABLED | [-0.74, 0.51, 0.00]
    75 | [-0.23, -0.56, 1.49]    | [-2.50,  1.48, -0.00]   |  2.91 |  0.16 | DISABLED | [-0.83, 0.49, -0.00]
  ```

### [Seed 5034] Configuration: Baseline (Shield OFF) — Outcome: `OBSTACLE_COLLISION`
- **Steps:** 61 | **Reward:** -24.26 | **Min Clearance:** 0.11 m
- **Diagnostic Cause:** Obstacle collision at speed 2.56 m/s (min clearance 0.12m).
- **Last 5 Control Steps Telemetry:**
  ```
  Step | Pos [x, y, z]           | Vel [vx, vy, vz]        | Speed | Clr   | State    | Action Executed
  -----+-------------------------+-------------------------+-------+-------+----------+----------------
    57 | [ 0.68, -2.19, 1.51]    | [ 0.24,  1.09, 0.01]    |  1.12 |  0.15 | DISABLED | [0.08, 0.36, 0.00]
    58 | [ 0.65, -2.15, 1.51]    | [-0.72,  1.02, -0.01]   |  1.25 |  0.16 | DISABLED | [-0.24, 0.34, -0.00]
    59 | [ 0.66, -2.11, 1.51]    | [ 0.03,  1.04, 0.05]    |  1.04 |  0.12 | DISABLED | [0.01, 0.35, 0.02]
    60 | [ 0.71, -2.07, 1.51]    | [ 1.33,  0.92, 0.01]    |  1.62 |  0.12 | DISABLED | [0.44, 0.31, 0.00]
    61 | [ 0.81, -2.02, 1.51]    | [ 2.26,  1.20, 0.02]    |  2.56 |  0.12 | DISABLED | [0.75, 0.40, 0.01]
  ```

### [Seed 5036] Configuration: Baseline (Shield OFF) — Outcome: `OBSTACLE_COLLISION`
- **Steps:** 71 | **Reward:** -74.0 | **Min Clearance:** 0.118 m
- **Diagnostic Cause:** Obstacle collision at speed 3.40 m/s (min clearance 0.14m).
- **Last 5 Control Steps Telemetry:**
  ```
  Step | Pos [x, y, z]           | Vel [vx, vy, vz]        | Speed | Clr   | State    | Action Executed
  -----+-------------------------+-------------------------+-------+-------+----------+----------------
    67 | [-1.54, -0.68, 1.51]    | [-2.81,  2.00, -0.01]   |  3.45 |  0.14 | DISABLED | [-0.94, 0.67, -0.00]
    68 | [-1.45, -0.59, 1.50]    | [ 2.27,  2.12, -0.03]   |  3.10 |  0.15 | DISABLED | [0.76, 0.70, -0.01]
    69 | [-1.38, -0.50, 1.50]    | [ 1.76,  2.16, -0.06]   |  2.79 |  0.16 | DISABLED | [0.59, 0.72, -0.02]
    70 | [-1.27, -0.41, 1.50]    | [ 2.44,  2.18, -0.02]   |  3.27 |  0.12 | DISABLED | [0.81, 0.73, -0.01]
    71 | [-1.16, -0.32, 1.50]    | [ 2.68,  2.09, -0.03]   |  3.40 |  0.14 | DISABLED | [0.89, 0.70, -0.01]
  ```

### [Seed 5037] Configuration: Baseline (Shield OFF) — Outcome: `OBSTACLE_COLLISION`
- **Steps:** 51 | **Reward:** 20.82 | **Min Clearance:** 0.127 m
- **Diagnostic Cause:** Obstacle collision at speed 2.06 m/s (min clearance 0.13m).
- **Last 5 Control Steps Telemetry:**
  ```
  Step | Pos [x, y, z]           | Vel [vx, vy, vz]        | Speed | Clr   | State    | Action Executed
  -----+-------------------------+-------------------------+-------+-------+----------+----------------
    47 | [-0.12, -2.68, 1.50]    | [-2.22,  1.50, 0.04]    |  2.68 |  0.13 | DISABLED | [-0.74, 0.50, 0.01]
    48 | [-0.14, -2.62, 1.50]    | [-0.40,  1.53, -0.01]   |  1.58 |  0.15 | DISABLED | [-0.14, 0.51, -0.00]
    49 | [-0.11, -2.56, 1.50]    | [ 0.79,  1.42, -0.00]   |  1.62 |  0.15 | DISABLED | [0.26, 0.47, -0.00]
    50 | [-0.04, -2.50, 1.50]    | [ 1.75,  1.28, -0.05]   |  2.17 |  0.14 | DISABLED | [0.58, 0.43, -0.02]
    51 | [-0.11, -2.46, 1.50]    | [-1.72,  1.13, 0.01]    |  2.06 |  0.13 | DISABLED | [-0.57, 0.38, 0.01]
  ```

### [Seed 5038] Configuration: Baseline (Shield OFF) — Outcome: `OBSTACLE_COLLISION`
- **Steps:** 76 | **Reward:** -184.07 | **Min Clearance:** 0.108 m
- **Diagnostic Cause:** Obstacle collision at speed 2.72 m/s (min clearance 0.15m).
- **Last 5 Control Steps Telemetry:**
  ```
  Step | Pos [x, y, z]           | Vel [vx, vy, vz]        | Speed | Clr   | State    | Action Executed
  -----+-------------------------+-------------------------+-------+-------+----------+----------------
    72 | [ 1.37, -0.55, 1.50]    | [ 2.82,  2.01, 0.07]    |  3.46 |  0.13 | DISABLED | [0.94, 0.67, 0.02]
    73 | [ 1.25, -0.48, 1.50]    | [-3.00,  1.74, -0.05]   |  3.46 |  0.15 | DISABLED | [-1.00, 0.58, -0.02]
    74 | [ 1.21, -0.42, 1.50]    | [-0.92,  1.48, 0.03]    |  1.74 |  0.16 | DISABLED | [-0.31, 0.49, 0.01]
    75 | [ 1.11, -0.36, 1.50]    | [-2.40,  1.44, -0.01]   |  2.80 |  0.14 | DISABLED | [-0.80, 0.48, -0.00]
    76 | [ 1.01, -0.30, 1.49]    | [-2.39,  1.29, -0.05]   |  2.72 |  0.15 | DISABLED | [-0.80, 0.43, -0.02]
  ```

### [Seed 5039] Configuration: Baseline (Shield OFF) — Outcome: `OBSTACLE_COLLISION`
- **Steps:** 52 | **Reward:** -16.62 | **Min Clearance:** 0.113 m
- **Diagnostic Cause:** Obstacle collision at speed 1.54 m/s (min clearance 0.12m).
- **Last 5 Control Steps Telemetry:**
  ```
  Step | Pos [x, y, z]           | Vel [vx, vy, vz]        | Speed | Clr   | State    | Action Executed
  -----+-------------------------+-------------------------+-------+-------+----------+----------------
    48 | [ 0.31, -2.80, 1.50]    | [-0.81,  1.74, -0.02]   |  1.92 |  0.13 | DISABLED | [-0.27, 0.58, -0.01]
    49 | [ 0.39, -2.73, 1.50]    | [ 1.89,  1.70, -0.02]   |  2.54 |  0.11 | DISABLED | [0.63, 0.57, -0.01]
    50 | [ 0.45, -2.66, 1.50]    | [ 1.52,  1.58, -0.02]   |  2.19 |  0.14 | DISABLED | [0.51, 0.53, -0.01]
    51 | [ 0.45, -2.60, 1.50]    | [-0.01,  1.44, -0.02]   |  1.44 |  0.15 | DISABLED | [-0.00, 0.48, -0.01]
    52 | [ 0.49, -2.55, 1.50]    | [ 0.86,  1.28, -0.02]   |  1.54 |  0.12 | DISABLED | [0.28, 0.43, -0.01]
  ```

### [Seed 5040] Configuration: Baseline (Shield OFF) — Outcome: `OBSTACLE_COLLISION`
- **Steps:** 112 | **Reward:** -347.48 | **Min Clearance:** 0.111 m
- **Diagnostic Cause:** Obstacle collision at speed 2.38 m/s (min clearance 0.17m).
- **Last 5 Control Steps Telemetry:**
  ```
  Step | Pos [x, y, z]           | Vel [vx, vy, vz]        | Speed | Clr   | State    | Action Executed
  -----+-------------------------+-------------------------+-------+-------+----------+----------------
   108 | [ 0.36,  2.08, 1.48]    | [-2.78,  1.86, -0.07]   |  3.35 |  0.13 | DISABLED | [-0.93, 0.62, -0.02]
   109 | [ 0.37,  2.16, 1.48]    | [ 0.43,  1.85, -0.03]   |  1.90 |  0.12 | DISABLED | [0.14, 0.62, -0.01]
   110 | [ 0.40,  2.24, 1.48]    | [ 0.70,  1.95, -0.05]   |  2.07 |  0.15 | DISABLED | [0.23, 0.65, -0.02]
   111 | [ 0.37,  2.31, 1.48]    | [-0.75,  1.78, 0.01]    |  1.94 |  0.15 | DISABLED | [-0.25, 0.59, 0.01]
   112 | [ 0.32,  2.40, 1.48]    | [-1.31,  1.98, -0.02]   |  2.38 |  0.17 | DISABLED | [-0.44, 0.66, -0.01]
  ```

### [Seed 5041] Configuration: Baseline (Shield OFF) — Outcome: `OBSTACLE_COLLISION`
- **Steps:** 39 | **Reward:** 94.19 | **Min Clearance:** 0.321 m
- **Diagnostic Cause:** Obstacle collision at speed 2.65 m/s (min clearance 0.32m).
- **Last 5 Control Steps Telemetry:**
  ```
  Step | Pos [x, y, z]           | Vel [vx, vy, vz]        | Speed | Clr   | State    | Action Executed
  -----+-------------------------+-------------------------+-------+-------+----------+----------------
    35 | [-0.31, -3.93, 1.50]    | [-1.01,  2.58, -0.02]   |  2.77 |  0.69 | DISABLED | [-0.34, 0.86, -0.01]
    36 | [-0.34, -3.82, 1.50]    | [-0.71,  2.61, -0.02]   |  2.70 |  0.59 | DISABLED | [-0.24, 0.87, -0.01]
    37 | [-0.34, -3.71, 1.50]    | [ 0.09,  2.66, -0.01]   |  2.66 |  0.51 | DISABLED | [0.03, 0.89, -0.01]
    38 | [-0.35, -3.60, 1.50]    | [-0.33,  2.60, 0.01]    |  2.62 |  0.42 | DISABLED | [-0.11, 0.87, 0.00]
    39 | [-0.36, -3.49, 1.50]    | [-0.24,  2.64, 0.01]    |  2.65 |  0.32 | DISABLED | [-0.08, 0.88, 0.00]
  ```

### [Seed 5042] Configuration: Baseline (Shield OFF) — Outcome: `OBSTACLE_COLLISION`
- **Steps:** 90 | **Reward:** -186.03 | **Min Clearance:** 0.115 m
- **Diagnostic Cause:** Obstacle collision at speed 2.88 m/s (min clearance 0.14m).
- **Last 5 Control Steps Telemetry:**
  ```
  Step | Pos [x, y, z]           | Vel [vx, vy, vz]        | Speed | Clr   | State    | Action Executed
  -----+-------------------------+-------------------------+-------+-------+----------+----------------
    86 | [-0.38,  0.85, 1.50]    | [ 1.08,  2.58, -0.01]   |  2.79 |  0.16 | DISABLED | [0.36, 0.86, -0.00]
    87 | [-0.36,  0.96, 1.50]    | [ 0.50,  2.73, 0.01]    |  2.77 |  0.18 | DISABLED | [0.17, 0.91, 0.00]
    88 | [-0.31,  1.08, 1.50]    | [ 1.07,  2.74, -0.02]   |  2.94 |  0.14 | DISABLED | [0.36, 0.91, -0.01]
    89 | [-0.28,  1.19, 1.50]    | [ 0.70,  2.73, -0.04]   |  2.81 |  0.18 | DISABLED | [0.23, 0.91, -0.01]
    90 | [-0.26,  1.31, 1.50]    | [ 0.66,  2.81, 0.05]    |  2.88 |  0.14 | DISABLED | [0.22, 0.94, 0.01]
  ```

### [Seed 5043] Configuration: Baseline (Shield OFF) — Outcome: `OBSTACLE_COLLISION`
- **Steps:** 42 | **Reward:** 65.46 | **Min Clearance:** 0.153 m
- **Diagnostic Cause:** Obstacle collision at speed 3.17 m/s (min clearance 0.15m).
- **Last 5 Control Steps Telemetry:**
  ```
  Step | Pos [x, y, z]           | Vel [vx, vy, vz]        | Speed | Clr   | State    | Action Executed
  -----+-------------------------+-------------------------+-------+-------+----------+----------------
    38 | [-0.04, -3.92, 1.50]    | [ 2.97,  1.25, 0.07]    |  3.22 |  0.52 | DISABLED | [0.99, 0.42, 0.03]
    39 | [-0.16, -3.87, 1.50]    | [-2.82,  1.25, 0.00]    |  3.08 |  0.57 | DISABLED | [-0.94, 0.42, 0.00]
    40 | [-0.28, -3.82, 1.50]    | [-2.98,  1.19, 0.07]    |  3.21 |  0.50 | DISABLED | [-0.99, 0.40, 0.02]
    41 | [-0.16, -3.77, 1.50]    | [ 2.96,  1.26, -0.00]   |  3.22 |  0.47 | DISABLED | [0.99, 0.42, -0.00]
    42 | [-0.04, -3.71, 1.50]    | [ 2.85,  1.40, -0.01]   |  3.17 |  0.15 | DISABLED | [0.95, 0.47, -0.00]
  ```

### [Seed 5044] Configuration: Baseline (Shield OFF) — Outcome: `OBSTACLE_COLLISION`
- **Steps:** 65 | **Reward:** -41.97 | **Min Clearance:** 0.113 m
- **Diagnostic Cause:** Obstacle collision at speed 3.43 m/s (min clearance 0.14m).
- **Last 5 Control Steps Telemetry:**
  ```
  Step | Pos [x, y, z]           | Vel [vx, vy, vz]        | Speed | Clr   | State    | Action Executed
  -----+-------------------------+-------------------------+-------+-------+----------+----------------
    61 | [-1.00, -1.57, 1.48]    | [-1.75,  1.32, 0.01]    |  2.19 |  0.14 | DISABLED | [-0.58, 0.44, 0.00]
    62 | [-1.10, -1.52, 1.48]    | [-2.44,  1.28, 0.01]    |  2.75 |  0.14 | DISABLED | [-0.81, 0.43, 0.00]
    63 | [-1.22, -1.46, 1.48]    | [-2.90,  1.50, -0.01]   |  3.27 |  0.14 | DISABLED | [-0.97, 0.50, -0.01]
    64 | [-1.35, -1.39, 1.48]    | [-2.97,  1.76, -0.07]   |  3.45 |  0.14 | DISABLED | [-0.99, 0.59, -0.02]
    65 | [-1.47, -1.31, 1.48]    | [-2.88,  1.87, -0.00]   |  3.43 |  0.14 | DISABLED | [-0.96, 0.62, -0.00]
  ```

### [Seed 5046] Configuration: Baseline (Shield OFF) — Outcome: `OBSTACLE_COLLISION`
- **Steps:** 34 | **Reward:** 1.16 | **Min Clearance:** 0.231 m
- **Diagnostic Cause:** Obstacle collision at speed 2.46 m/s (min clearance 0.23m).
- **Last 5 Control Steps Telemetry:**
  ```
  Step | Pos [x, y, z]           | Vel [vx, vy, vz]        | Speed | Clr   | State    | Action Executed
  -----+-------------------------+-------------------------+-------+-------+----------+----------------
    30 | [ 0.48, -4.52, 1.50]    | [ 2.14,  2.16, 0.06]    |  3.04 |  0.62 | DISABLED | [0.71, 0.72, 0.02]
    31 | [ 0.48, -4.42, 1.50]    | [-0.07,  2.26, 0.01]    |  2.26 |  0.53 | DISABLED | [-0.02, 0.75, 0.01]
    32 | [ 0.54, -4.32, 1.50]    | [ 1.59,  2.44, -0.02]   |  2.92 |  0.45 | DISABLED | [0.53, 0.81, -0.01]
    33 | [ 0.48, -4.23, 1.50]    | [-1.41,  2.31, 0.01]    |  2.71 |  0.34 | DISABLED | [-0.47, 0.77, 0.00]
    34 | [ 0.45, -4.13, 1.49]    | [-0.89,  2.30, -0.04]   |  2.46 |  0.23 | DISABLED | [-0.29, 0.77, -0.01]
  ```

### [Seed 5047] Configuration: Baseline (Shield OFF) — Outcome: `OBSTACLE_COLLISION`
- **Steps:** 49 | **Reward:** 28.81 | **Min Clearance:** 0.114 m
- **Diagnostic Cause:** Obstacle collision at speed 2.81 m/s (min clearance 0.11m).
- **Last 5 Control Steps Telemetry:**
  ```
  Step | Pos [x, y, z]           | Vel [vx, vy, vz]        | Speed | Clr   | State    | Action Executed
  -----+-------------------------+-------------------------+-------+-------+----------+----------------
    45 | [ 0.99, -2.76, 1.50]    | [-1.75,  2.26, 0.01]    |  2.86 |  0.21 | DISABLED | [-0.58, 0.76, 0.00]
    46 | [ 0.95, -2.67, 1.50]    | [-0.89,  2.19, -0.00]   |  2.36 |  0.17 | DISABLED | [-0.30, 0.73, -0.00]
    47 | [ 0.89, -2.58, 1.50]    | [-1.44,  2.23, -0.02]   |  2.65 |  0.14 | DISABLED | [-0.48, 0.74, -0.01]
    48 | [ 0.83, -2.49, 1.50]    | [-1.30,  2.24, -0.01]   |  2.59 |  0.12 | DISABLED | [-0.43, 0.75, -0.00]
    49 | [ 0.77, -2.39, 1.50]    | [-1.62,  2.30, -0.00]   |  2.81 |  0.11 | DISABLED | [-0.54, 0.77, -0.00]
  ```

### [Seed 5049] Configuration: Baseline (Shield OFF) — Outcome: `OBSTACLE_COLLISION`
- **Steps:** 60 | **Reward:** -26.27 | **Min Clearance:** 0.109 m
- **Diagnostic Cause:** Obstacle collision at speed 3.45 m/s (min clearance 0.14m).
- **Last 5 Control Steps Telemetry:**
  ```
  Step | Pos [x, y, z]           | Vel [vx, vy, vz]        | Speed | Clr   | State    | Action Executed
  -----+-------------------------+-------------------------+-------+-------+----------+----------------
    56 | [ 0.91, -1.76, 1.48]    | [-2.13,  2.22, -0.01]   |  3.08 |  0.14 | DISABLED | [-0.71, 0.74, -0.00]
    57 | [ 0.95, -1.68, 1.48]    | [ 1.05,  2.02, -0.08]   |  2.27 |  0.13 | DISABLED | [0.35, 0.67, -0.03]
    58 | [ 1.00, -1.59, 1.48]    | [ 1.18,  1.96, -0.03]   |  2.28 |  0.13 | DISABLED | [0.39, 0.65, -0.01]
    59 | [ 1.12, -1.52, 1.47]    | [ 2.73,  1.90, -0.02]   |  3.33 |  0.13 | DISABLED | [0.91, 0.63, -0.01]
    60 | [ 1.23, -1.43, 1.47]    | [ 2.81,  2.00, -0.05]   |  3.45 |  0.14 | DISABLED | [0.94, 0.67, -0.01]
  ```

### [Seed 5001] Configuration: Shield ON (Camera) — Outcome: `OBSTACLE_COLLISION`
- **Steps:** 59 | **Reward:** -1.2 | **Min Clearance:** 0.557 m
- **Diagnostic Cause:** Obstacle collision at speed 3.00 m/s (min clearance 3.00m).
- **Last 5 Control Steps Telemetry:**
  ```
  Step | Pos [x, y, z]           | Vel [vx, vy, vz]        | Speed | Clr   | State    | Action Executed
  -----+-------------------------+-------------------------+-------+-------+----------+----------------
    55 | [-0.02, -3.88, 1.50]    | [ 0.12,  1.59, -0.01]   |  1.60 |  3.27 | NOMINAL  | [0.04, 0.53, -0.00]
    56 | [-0.04, -3.81, 1.50]    | [-0.34,  1.57, -0.01]   |  1.61 |  3.21 | NOMINAL  | [-0.12, 0.52, -0.00]
    57 | [-0.04, -3.74, 1.49]    | [-0.16,  1.66, -0.01]   |  1.67 |  3.14 | NOMINAL  | [-0.05, 0.55, -0.00]
    58 | [ 0.04, -3.67, 1.49]    | [ 1.91,  1.66, -0.00]   |  2.53 |  3.08 | NOMINAL  | [0.64, 0.55, -0.00]
    59 | [ 0.14, -3.62, 1.50]    | [ 2.65,  1.41, 0.03]    |  3.00 |  3.00 | NOMINAL  | [0.88, 0.47, 0.01]
  ```

### [Seed 5002] Configuration: Shield ON (Camera) — Outcome: `OBSTACLE_COLLISION`
- **Steps:** 41 | **Reward:** 78.85 | **Min Clearance:** 2.554 m
- **Diagnostic Cause:** Obstacle collision at speed 2.91 m/s (min clearance 2.55m).
- **Last 5 Control Steps Telemetry:**
  ```
  Step | Pos [x, y, z]           | Vel [vx, vy, vz]        | Speed | Clr   | State    | Action Executed
  -----+-------------------------+-------------------------+-------+-------+----------+----------------
    37 | [ 0.09, -3.58, 1.50]    | [-0.13,  2.86, -0.01]   |  2.86 |  3.00 | NOMINAL  | [-0.04, 0.95, -0.00]
    38 | [ 0.07, -3.47, 1.50]    | [-0.25,  2.79, -0.00]   |  2.80 |  2.88 | NOMINAL  | [-0.08, 0.93, -0.00]
    39 | [ 0.08, -3.35, 1.50]    | [ 0.01,  2.85, -0.00]   |  2.85 |  2.76 | NOMINAL  | [0.00, 0.95, -0.00]
    40 | [ 0.11, -3.24, 1.50]    | [ 0.73,  2.74, -0.01]   |  2.84 |  2.65 | NOMINAL  | [0.24, 0.91, -0.01]
    41 | [ 0.06, -3.12, 1.50]    | [-1.15,  2.68, -0.05]   |  2.91 |  2.55 | NOMINAL  | [-0.38, 0.89, -0.01]
  ```

### [Seed 5005] Configuration: Shield ON (Camera) — Outcome: `TIMEOUT`
- **Steps:** 500 | **Reward:** -2349.9 | **Min Clearance:** 0.074 m
- **Diagnostic Cause:** Exceeded maximum episode limit (500 steps) without reaching goal.
- **Last 5 Control Steps Telemetry:**
  ```
  Step | Pos [x, y, z]           | Vel [vx, vy, vz]        | Speed | Clr   | State    | Action Executed
  -----+-------------------------+-------------------------+-------+-------+----------+----------------
   496 | [ 1.52, -0.69, 1.50]    | [-0.00,  0.00, -0.00]   |  0.00 |  0.07 | PLANNER  | [-0.00, 0.00, -0.00]
   497 | [ 1.52, -0.69, 1.50]    | [-0.00,  0.00, -0.00]   |  0.00 |  0.07 | PLANNER  | [-0.00, 0.00, -0.00]
   498 | [ 1.52, -0.69, 1.50]    | [-0.00,  0.00, -0.00]   |  0.00 |  0.07 | PLANNER  | [-0.00, 0.00, -0.00]
   499 | [ 1.52, -0.69, 1.50]    | [-0.00,  0.00, -0.00]   |  0.00 |  0.07 | PLANNER  | [-0.00, 0.00, -0.00]
   500 | [ 1.52, -0.69, 1.50]    | [-0.00,  0.00, -0.00]   |  0.00 |  0.07 | PLANNER  | [-0.00, 0.00, -0.00]
  ```

### [Seed 5008] Configuration: Shield ON (Camera) — Outcome: `OBSTACLE_COLLISION`
- **Steps:** 106 | **Reward:** -282.21 | **Min Clearance:** 0.234 m
- **Diagnostic Cause:** Obstacle collision at speed 1.54 m/s (min clearance 0.33m).
- **Last 5 Control Steps Telemetry:**
  ```
  Step | Pos [x, y, z]           | Vel [vx, vy, vz]        | Speed | Clr   | State    | Action Executed
  -----+-------------------------+-------------------------+-------+-------+----------+----------------
   102 | [-3.00, -0.82, 1.50]    | [-1.50,  0.35, -0.00]   |  1.54 |  0.28 | REROUTE  | [-0.50, 0.12, -0.00]
   103 | [-3.06, -0.81, 1.50]    | [-1.50,  0.35, -0.00]   |  1.54 |  0.26 | REROUTE  | [-0.50, 0.12, -0.00]
   104 | [-3.12, -0.79, 1.50]    | [-1.50,  0.35, -0.00]   |  1.54 |  0.36 | REROUTE  | [-0.50, 0.12, -0.00]
   105 | [-3.19, -0.78, 1.50]    | [-1.50,  0.35, -0.00]   |  1.54 |  0.35 | REROUTE  | [-0.50, 0.12, -0.00]
   106 | [-3.25, -0.77, 1.50]    | [-1.50,  0.35, -0.00]   |  1.54 |  0.33 | REROUTE  | [-0.50, 0.12, -0.00]
  ```

### [Seed 5011] Configuration: Shield ON (Camera) — Outcome: `OBSTACLE_COLLISION`
- **Steps:** 108 | **Reward:** -278.58 | **Min Clearance:** 0.241 m
- **Diagnostic Cause:** Obstacle collision at speed 1.50 m/s (min clearance 0.24m).
- **Last 5 Control Steps Telemetry:**
  ```
  Step | Pos [x, y, z]           | Vel [vx, vy, vz]        | Speed | Clr   | State    | Action Executed
  -----+-------------------------+-------------------------+-------+-------+----------+----------------
   104 | [ 2.27, -0.81, 1.50]    | [ 1.50,  0.00, 0.00]    |  1.50 |  0.25 | REROUTE  | [0.50, 0.00, 0.00]
   105 | [ 2.33, -0.80, 1.50]    | [ 1.50,  0.35, 0.00]    |  1.54 |  0.25 | REROUTE  | [0.50, 0.12, 0.00]
   106 | [ 2.40, -0.80, 1.50]    | [ 1.50,  0.00, 0.00]    |  1.50 |  0.24 | REROUTE  | [0.50, 0.00, 0.00]
   107 | [ 2.46, -0.80, 1.50]    | [ 1.50,  0.00, 0.00]    |  1.50 |  0.25 | REROUTE  | [0.50, 0.00, 0.00]
   108 | [ 2.52, -0.80, 1.50]    | [ 1.50,  0.00, 0.00]    |  1.50 |  0.24 | REROUTE  | [0.50, 0.00, 0.00]
  ```

### [Seed 5012] Configuration: Shield ON (Camera) — Outcome: `OBSTACLE_COLLISION`
- **Steps:** 113 | **Reward:** -366.4 | **Min Clearance:** 0.352 m
- **Diagnostic Cause:** Obstacle collision at speed 1.54 m/s (min clearance 0.44m).
- **Last 5 Control Steps Telemetry:**
  ```
  Step | Pos [x, y, z]           | Vel [vx, vy, vz]        | Speed | Clr   | State    | Action Executed
  -----+-------------------------+-------------------------+-------+-------+----------+----------------
   109 | [ 2.77, -1.31, 1.50]    | [ 1.50,  0.40, 0.01]    |  1.55 |  0.48 | REROUTE  | [0.50, 0.13, 0.00]
   110 | [ 2.83, -1.29, 1.50]    | [ 1.50,  0.37, 0.01]    |  1.54 |  0.47 | REROUTE  | [0.50, 0.12, 0.00]
   111 | [ 2.89, -1.28, 1.50]    | [ 1.50,  0.35, 0.01]    |  1.54 |  0.46 | REROUTE  | [0.50, 0.12, 0.00]
   112 | [ 2.95, -1.26, 1.50]    | [ 1.50,  0.35, 0.01]    |  1.54 |  0.45 | REROUTE  | [0.50, 0.12, 0.00]
   113 | [ 3.02, -1.25, 1.50]    | [ 1.50,  0.35, 0.01]    |  1.54 |  0.44 | REROUTE  | [0.50, 0.12, 0.00]
  ```

### [Seed 5014] Configuration: Shield ON (Camera) — Outcome: `OBSTACLE_COLLISION`
- **Steps:** 117 | **Reward:** -363.26 | **Min Clearance:** 0.209 m
- **Diagnostic Cause:** Obstacle collision at speed 1.50 m/s (min clearance 0.21m).
- **Last 5 Control Steps Telemetry:**
  ```
  Step | Pos [x, y, z]           | Vel [vx, vy, vz]        | Speed | Clr   | State    | Action Executed
  -----+-------------------------+-------------------------+-------+-------+----------+----------------
   113 | [-1.44, -0.88, 1.50]    | [-1.50,  0.00, 0.01]    |  1.50 |  0.23 | REROUTE  | [-0.50, 0.00, 0.00]
   114 | [-1.50, -0.88, 1.50]    | [-1.50,  0.00, 0.00]    |  1.50 |  0.22 | REROUTE  | [-0.50, 0.00, 0.00]
   115 | [-1.56, -0.88, 1.50]    | [-1.50,  0.00, 0.00]    |  1.50 |  0.22 | REROUTE  | [-0.50, 0.00, 0.00]
   116 | [-1.62, -0.88, 1.50]    | [-1.50,  0.00, 0.00]    |  1.50 |  0.21 | REROUTE  | [-0.50, 0.00, 0.00]
   117 | [-1.69, -0.88, 1.50]    | [-1.50,  0.00, 0.00]    |  1.50 |  0.21 | REROUTE  | [-0.50, 0.00, 0.00]
  ```

### [Seed 5016] Configuration: Shield ON (Camera) — Outcome: `OBSTACLE_COLLISION`
- **Steps:** 57 | **Reward:** 46.88 | **Min Clearance:** 0.56 m
- **Diagnostic Cause:** Obstacle collision at speed 3.00 m/s (min clearance 1.94m).
- **Last 5 Control Steps Telemetry:**
  ```
  Step | Pos [x, y, z]           | Vel [vx, vy, vz]        | Speed | Clr   | State    | Action Executed
  -----+-------------------------+-------------------------+-------+-------+----------+----------------
    53 | [ 0.40, -3.75, 1.50]    | [ 1.50,  1.60, 0.00]    |  2.19 |  2.83 | REROUTE  | [0.50, 0.53, 0.00]
    54 | [ 0.49, -3.69, 1.50]    | [ 2.40,  1.48, -0.03]   |  2.81 |  2.22 | NOMINAL  | [0.80, 0.49, -0.01]
    55 | [ 0.38, -3.63, 1.50]    | [-2.66,  1.39, 0.01]    |  3.00 |  2.01 | NOMINAL  | [-0.89, 0.46, 0.00]
    56 | [ 0.47, -3.59, 1.50]    | [ 2.00,  1.13, -0.02]   |  2.30 |  2.14 | NOMINAL  | [0.67, 0.38, -0.01]
    57 | [ 0.58, -3.53, 1.50]    | [ 2.68,  1.34, -0.00]   |  3.00 |  1.94 | NOMINAL  | [0.90, 0.45, -0.00]
  ```

### [Seed 5022] Configuration: Shield ON (Camera) — Outcome: `OBSTACLE_COLLISION`
- **Steps:** 101 | **Reward:** -234.41 | **Min Clearance:** 0.24 m
- **Diagnostic Cause:** Obstacle collision at speed 1.50 m/s (min clearance 0.24m).
- **Last 5 Control Steps Telemetry:**
  ```
  Step | Pos [x, y, z]           | Vel [vx, vy, vz]        | Speed | Clr   | State    | Action Executed
  -----+-------------------------+-------------------------+-------+-------+----------+----------------
    97 | [-1.31, -0.90, 1.50]    | [-1.50,  0.35, -0.00]   |  1.54 |  0.29 | REROUTE  | [-0.50, 0.12, -0.00]
    98 | [-1.37, -0.89, 1.50]    | [-1.50,  0.35, -0.00]   |  1.54 |  0.28 | REROUTE  | [-0.50, 0.12, -0.00]
    99 | [-1.43, -0.87, 1.50]    | [-1.50,  0.35, -0.00]   |  1.54 |  0.27 | REROUTE  | [-0.50, 0.12, -0.00]
   100 | [-1.49, -0.86, 1.50]    | [-1.50,  0.35, -0.00]   |  1.54 |  0.26 | REROUTE  | [-0.50, 0.12, -0.00]
   101 | [-1.56, -0.86, 1.50]    | [-1.50,  0.00, -0.00]   |  1.50 |  0.24 | REROUTE  | [-0.50, 0.00, -0.00]
  ```

### [Seed 5024] Configuration: Shield ON (Camera) — Outcome: `OBSTACLE_COLLISION`
- **Steps:** 60 | **Reward:** -38.04 | **Min Clearance:** 0.452 m
- **Diagnostic Cause:** Obstacle collision at speed 1.54 m/s (min clearance 0.45m).
- **Last 5 Control Steps Telemetry:**
  ```
  Step | Pos [x, y, z]           | Vel [vx, vy, vz]        | Speed | Clr   | State    | Action Executed
  -----+-------------------------+-------------------------+-------+-------+----------+----------------
    56 | [-0.23, -2.93, 1.50]    | [ 1.50,  0.40, -0.00]   |  1.55 |  0.50 | REROUTE  | [0.50, 0.13, -0.00]
    57 | [-0.17, -2.91, 1.50]    | [ 1.50,  0.40, -0.00]   |  1.55 |  0.49 | REROUTE  | [0.50, 0.13, -0.00]
    58 | [-0.10, -2.89, 1.50]    | [ 1.50,  0.40, -0.00]   |  1.55 |  0.47 | REROUTE  | [0.50, 0.13, -0.00]
    59 | [-0.04, -2.88, 1.50]    | [ 1.50,  0.35, -0.00]   |  1.54 |  0.46 | REROUTE  | [0.50, 0.12, -0.00]
    60 | [ 0.02, -2.87, 1.50]    | [ 1.50,  0.35, -0.00]   |  1.54 |  0.45 | REROUTE  | [0.50, 0.12, -0.00]
  ```

### [Seed 5026] Configuration: Shield ON (Camera) — Outcome: `OBSTACLE_COLLISION`
- **Steps:** 131 | **Reward:** -350.88 | **Min Clearance:** 0.243 m
- **Diagnostic Cause:** Obstacle collision at speed 1.54 m/s (min clearance 0.43m).
- **Last 5 Control Steps Telemetry:**
  ```
  Step | Pos [x, y, z]           | Vel [vx, vy, vz]        | Speed | Clr   | State    | Action Executed
  -----+-------------------------+-------------------------+-------+-------+----------+----------------
   127 | [ 1.94, -1.04, 1.51]    | [ 1.50,  0.40, -0.02]   |  1.55 |  0.47 | REROUTE  | [0.50, 0.13, -0.01]
   128 | [ 2.01, -1.03, 1.51]    | [ 1.50,  0.35, -0.02]   |  1.54 |  0.46 | REROUTE  | [0.50, 0.12, -0.01]
   129 | [ 2.07, -1.01, 1.51]    | [ 1.50,  0.35, -0.01]   |  1.54 |  0.46 | REROUTE  | [0.50, 0.12, -0.01]
   130 | [ 2.13, -1.00, 1.51]    | [ 1.50,  0.35, -0.01]   |  1.54 |  0.44 | REROUTE  | [0.50, 0.12, -0.01]
   131 | [ 2.19, -0.98, 1.51]    | [ 1.50,  0.35, -0.01]   |  1.54 |  0.43 | REROUTE  | [0.50, 0.12, -0.00]
  ```

### [Seed 5029] Configuration: Shield ON (Camera) — Outcome: `OBSTACLE_COLLISION`
- **Steps:** 26 | **Reward:** -27.56 | **Min Clearance:** 0.876 m
- **Diagnostic Cause:** Obstacle collision at speed 2.82 m/s (min clearance 2.29m).
- **Last 5 Control Steps Telemetry:**
  ```
  Step | Pos [x, y, z]           | Vel [vx, vy, vz]        | Speed | Clr   | State    | Action Executed
  -----+-------------------------+-------------------------+-------+-------+----------+----------------
    22 | [ 0.37, -5.75, 1.50]    | [-0.01,  2.50, -0.02]   |  2.50 |  2.71 | NOMINAL  | [-0.00, 0.83, -0.01]
    23 | [ 0.42, -5.64, 1.50]    | [ 1.36,  2.67, -0.01]   |  3.00 |  2.61 | NOMINAL  | [0.45, 0.89, -0.00]
    24 | [ 0.37, -5.53, 1.50]    | [-1.20,  2.75, -0.01]   |  3.00 |  2.52 | NOMINAL  | [-0.40, 0.92, -0.01]
    25 | [ 0.37, -5.42, 1.50]    | [-0.06,  2.62, -0.01]   |  2.62 |  2.40 | NOMINAL  | [-0.02, 0.87, -0.00]
    26 | [ 0.36, -5.30, 1.50]    | [-0.23,  2.81, -0.02]   |  2.82 |  2.29 | NOMINAL  | [-0.08, 0.94, -0.01]
  ```

### [Seed 5030] Configuration: Shield ON (Camera) — Outcome: `OBSTACLE_COLLISION`
- **Steps:** 159 | **Reward:** -613.36 | **Min Clearance:** 0.028 m
- **Diagnostic Cause:** Obstacle collision at speed 1.50 m/s (min clearance 0.03m).
- **Last 5 Control Steps Telemetry:**
  ```
  Step | Pos [x, y, z]           | Vel [vx, vy, vz]        | Speed | Clr   | State    | Action Executed
  -----+-------------------------+-------------------------+-------+-------+----------+----------------
   155 | [ 1.77, -0.63, 1.50]    | [-1.50,  0.00, -0.00]   |  1.50 |  0.04 | REROUTE  | [-0.50, 0.00, -0.00]
   156 | [ 1.70, -0.63, 1.50]    | [-1.50,  0.00, -0.00]   |  1.50 |  0.03 | REROUTE  | [-0.50, 0.00, -0.00]
   157 | [ 1.64, -0.63, 1.50]    | [-1.50,  0.00, -0.00]   |  1.50 |  0.03 | REROUTE  | [-0.50, 0.00, -0.00]
   158 | [ 1.58, -0.63, 1.50]    | [-1.50,  0.00, -0.00]   |  1.50 |  0.03 | REROUTE  | [-0.50, 0.00, -0.00]
   159 | [ 1.52, -0.63, 1.50]    | [-1.50,  0.00, -0.00]   |  1.50 |  0.03 | REROUTE  | [-0.50, 0.00, -0.00]
  ```

### [Seed 5031] Configuration: Shield ON (Camera) — Outcome: `OBSTACLE_COLLISION`
- **Steps:** 105 | **Reward:** -327.48 | **Min Clearance:** 0.148 m
- **Diagnostic Cause:** Obstacle collision at speed 1.50 m/s (min clearance 0.15m).
- **Last 5 Control Steps Telemetry:**
  ```
  Step | Pos [x, y, z]           | Vel [vx, vy, vz]        | Speed | Clr   | State    | Action Executed
  -----+-------------------------+-------------------------+-------+-------+----------+----------------
   101 | [-1.17, -1.05, 1.50]    | [-1.50,  0.35, -0.00]   |  1.54 |  0.44 | REROUTE  | [-0.50, 0.12, -0.00]
   102 | [-1.23, -1.03, 1.50]    | [-1.50,  0.35, -0.00]   |  1.54 |  0.42 | REROUTE  | [-0.50, 0.12, -0.00]
   103 | [-1.29, -1.02, 1.50]    | [-1.50,  0.35, -0.00]   |  1.54 |  0.39 | REROUTE  | [-0.50, 0.12, -0.00]
   104 | [-1.36, -1.02, 1.50]    | [-1.50,  0.00, -0.00]   |  1.50 |  0.24 | REROUTE  | [-0.50, 0.00, -0.00]
   105 | [-1.42, -1.02, 1.50]    | [-1.50,  0.00, -0.00]   |  1.50 |  0.15 | REROUTE  | [-0.50, 0.00, -0.00]
  ```

### [Seed 5032] Configuration: Shield ON (Camera) — Outcome: `OBSTACLE_COLLISION`
- **Steps:** 93 | **Reward:** -255.84 | **Min Clearance:** 0.337 m
- **Diagnostic Cause:** Obstacle collision at speed 1.54 m/s (min clearance 0.34m).
- **Last 5 Control Steps Telemetry:**
  ```
  Step | Pos [x, y, z]           | Vel [vx, vy, vz]        | Speed | Clr   | State    | Action Executed
  -----+-------------------------+-------------------------+-------+-------+----------+----------------
    89 | [-0.69, -1.05, 1.50]    | [-1.50,  0.35, 0.00]    |  1.54 |  0.38 | REROUTE  | [-0.50, 0.12, 0.00]
    90 | [-0.75, -1.03, 1.50]    | [-1.50,  0.35, 0.00]    |  1.54 |  0.37 | REROUTE  | [-0.50, 0.12, 0.00]
    91 | [-0.81, -1.02, 1.50]    | [-1.50,  0.35, 0.00]    |  1.54 |  0.36 | REROUTE  | [-0.50, 0.12, 0.00]
    92 | [-0.88, -1.00, 1.50]    | [-1.50,  0.35, 0.00]    |  1.54 |  0.35 | REROUTE  | [-0.50, 0.12, 0.00]
    93 | [-0.94, -0.99, 1.50]    | [-1.50,  0.35, 0.00]    |  1.54 |  0.34 | REROUTE  | [-0.50, 0.12, 0.00]
  ```

### [Seed 5037] Configuration: Shield ON (Camera) — Outcome: `OBSTACLE_COLLISION`
- **Steps:** 141 | **Reward:** -539.55 | **Min Clearance:** 0.111 m
- **Diagnostic Cause:** Obstacle collision at speed 1.50 m/s (min clearance 0.11m).
- **Last 5 Control Steps Telemetry:**
  ```
  Step | Pos [x, y, z]           | Vel [vx, vy, vz]        | Speed | Clr   | State    | Action Executed
  -----+-------------------------+-------------------------+-------+-------+----------+----------------
   137 | [ 3.43, -0.81, 1.50]    | [-1.50,  0.35, -0.00]   |  1.54 |  0.36 | REROUTE  | [-0.50, 0.12, -0.00]
   138 | [ 3.37, -0.80, 1.50]    | [-1.50,  0.35, -0.00]   |  1.54 |  0.35 | REROUTE  | [-0.50, 0.12, -0.00]
   139 | [ 3.31, -0.78, 1.50]    | [-1.50,  0.35, -0.00]   |  1.54 |  0.30 | REROUTE  | [-0.50, 0.12, -0.00]
   140 | [ 3.24, -0.78, 1.50]    | [-1.50,  0.00, -0.00]   |  1.50 |  0.19 | REROUTE  | [-0.50, 0.00, -0.00]
   141 | [ 3.18, -0.78, 1.50]    | [-1.50,  0.00, -0.00]   |  1.50 |  0.11 | REROUTE  | [-0.50, 0.00, -0.00]
  ```

### [Seed 5039] Configuration: Shield ON (Camera) — Outcome: `OBSTACLE_COLLISION`
- **Steps:** 36 | **Reward:** 55.15 | **Min Clearance:** 1.223 m
- **Diagnostic Cause:** Obstacle collision at speed 2.83 m/s (min clearance 1.44m).
- **Last 5 Control Steps Telemetry:**
  ```
  Step | Pos [x, y, z]           | Vel [vx, vy, vz]        | Speed | Clr   | State    | Action Executed
  -----+-------------------------+-------------------------+-------+-------+----------+----------------
    32 | [-0.14, -4.34, 1.50]    | [ 0.89,  2.78, -0.01]   |  2.92 |  1.84 | NOMINAL  | [0.30, 0.93, -0.00]
    33 | [-0.11, -4.23, 1.50]    | [ 0.71,  2.63, -0.02]   |  2.73 |  1.72 | NOMINAL  | [0.24, 0.88, -0.01]
    34 | [-0.03, -4.13, 1.50]    | [ 1.80,  2.40, -0.00]   |  3.00 |  1.61 | NOMINAL  | [0.60, 0.80, -0.00]
    35 | [ 0.07, -4.05, 1.50]    | [ 2.29,  1.83, 0.01]    |  2.93 |  1.51 | NOMINAL  | [0.76, 0.61, 0.00]
    36 | [ 0.16, -3.98, 1.50]    | [ 2.31,  1.64, -0.02]   |  2.83 |  1.44 | NOMINAL  | [0.77, 0.55, -0.01]
  ```

### [Seed 5043] Configuration: Shield ON (Camera) — Outcome: `OBSTACLE_COLLISION`
- **Steps:** 54 | **Reward:** 67.13 | **Min Clearance:** 0.379 m
- **Diagnostic Cause:** Obstacle collision at speed 1.54 m/s (min clearance 0.38m).
- **Last 5 Control Steps Telemetry:**
  ```
  Step | Pos [x, y, z]           | Vel [vx, vy, vz]        | Speed | Clr   | State    | Action Executed
  -----+-------------------------+-------------------------+-------+-------+----------+----------------
    50 | [-0.03, -3.94, 1.50]    | [ 1.50,  0.35, 0.00]    |  1.54 |  0.42 | REROUTE  | [0.50, 0.12, 0.00]
    51 | [ 0.03, -3.93, 1.50]    | [ 1.50,  0.35, 0.00]    |  1.54 |  0.41 | REROUTE  | [0.50, 0.12, 0.00]
    52 | [ 0.09, -3.91, 1.50]    | [ 1.50,  0.35, 0.00]    |  1.54 |  0.40 | REROUTE  | [0.50, 0.12, 0.00]
    53 | [ 0.15, -3.90, 1.50]    | [ 1.50,  0.35, 0.00]    |  1.54 |  0.39 | REROUTE  | [0.50, 0.12, 0.00]
    54 | [ 0.22, -3.88, 1.50]    | [ 1.50,  0.35, 0.00]    |  1.54 |  0.38 | REROUTE  | [0.50, 0.12, 0.00]
  ```

### [Seed 5044] Configuration: Shield ON (Camera) — Outcome: `OBSTACLE_COLLISION`
- **Steps:** 75 | **Reward:** -97.89 | **Min Clearance:** 0.622 m
- **Diagnostic Cause:** Obstacle collision at speed 0.81 m/s (min clearance 0.62m).
- **Last 5 Control Steps Telemetry:**
  ```
  Step | Pos [x, y, z]           | Vel [vx, vy, vz]        | Speed | Clr   | State    | Action Executed
  -----+-------------------------+-------------------------+-------+-------+----------+----------------
    71 | [-1.26, -1.37, 1.49]    | [-0.40,  1.43, 0.03]    |  1.48 |  0.80 | NOMINAL  | [-0.13, 0.48, 0.01]
    72 | [-1.29, -1.32, 1.49]    | [-0.72,  1.08, -0.01]   |  1.30 |  0.74 | NOMINAL  | [-0.24, 0.36, -0.00]
    73 | [-1.31, -1.28, 1.49]    | [-0.59,  0.98, 0.03]    |  1.14 |  0.69 | NOMINAL  | [-0.20, 0.33, 0.01]
    74 | [-1.33, -1.25, 1.49]    | [-0.48,  0.85, -0.02]   |  0.98 |  0.66 | NOMINAL  | [-0.16, 0.28, -0.01]
    75 | [-1.34, -1.22, 1.49]    | [-0.20,  0.78, 0.02]    |  0.81 |  0.62 | NOMINAL  | [-0.07, 0.26, 0.01]
  ```

### [Seed 5045] Configuration: Shield ON (Camera) — Outcome: `OBSTACLE_COLLISION`
- **Steps:** 107 | **Reward:** -268.18 | **Min Clearance:** 0.213 m
- **Diagnostic Cause:** Obstacle collision at speed 1.54 m/s (min clearance 0.30m).
- **Last 5 Control Steps Telemetry:**
  ```
  Step | Pos [x, y, z]           | Vel [vx, vy, vz]        | Speed | Clr   | State    | Action Executed
  -----+-------------------------+-------------------------+-------+-------+----------+----------------
   103 | [-2.16, -0.88, 1.50]    | [-1.50,  0.00, -0.00]   |  1.50 |  0.22 | REROUTE  | [-0.50, 0.00, -0.00]
   104 | [-2.22, -0.88, 1.50]    | [-1.50,  0.00, -0.00]   |  1.50 |  0.22 | REROUTE  | [-0.50, 0.00, -0.00]
   105 | [-2.28, -0.88, 1.50]    | [-1.50,  0.00, -0.00]   |  1.50 |  0.21 | REROUTE  | [-0.50, 0.00, -0.00]
   106 | [-2.35, -0.86, 1.50]    | [-1.50,  0.35, -0.00]   |  1.54 |  0.32 | REROUTE  | [-0.50, 0.12, -0.00]
   107 | [-2.41, -0.85, 1.50]    | [-1.50,  0.35, -0.00]   |  1.54 |  0.30 | REROUTE  | [-0.50, 0.12, -0.00]
  ```

### [Seed 5046] Configuration: Shield ON (Camera) — Outcome: `OBSTACLE_COLLISION`
- **Steps:** 117 | **Reward:** -282.36 | **Min Clearance:** 0.249 m
- **Diagnostic Cause:** Obstacle collision at speed 1.50 m/s (min clearance 0.25m).
- **Last 5 Control Steps Telemetry:**
  ```
  Step | Pos [x, y, z]           | Vel [vx, vy, vz]        | Speed | Clr   | State    | Action Executed
  -----+-------------------------+-------------------------+-------+-------+----------+----------------
   113 | [-0.18, -1.51, 1.49]    | [ 1.50,  1.60, 0.01]    |  2.19 |  0.82 | REROUTE  | [0.50, 0.53, 0.00]
   114 | [-0.11, -1.49, 1.50]    | [ 1.50,  0.35, 0.01]    |  1.54 |  0.35 | REROUTE  | [0.50, 0.12, 0.00]
   115 | [-0.05, -1.48, 1.50]    | [ 1.50,  0.35, 0.01]    |  1.54 |  0.27 | REROUTE  | [0.50, 0.12, 0.00]
   116 | [ 0.01, -1.47, 1.50]    | [ 1.50,  0.35, 0.01]    |  1.54 |  0.26 | REROUTE  | [0.50, 0.12, 0.00]
   117 | [ 0.07, -1.47, 1.50]    | [ 1.50,  0.00, 0.01]    |  1.50 |  0.25 | REROUTE  | [0.50, 0.00, 0.00]
  ```

### [Seed 5047] Configuration: Shield ON (Camera) — Outcome: `OBSTACLE_COLLISION`
- **Steps:** 47 | **Reward:** 22.31 | **Min Clearance:** 1.78 m
- **Diagnostic Cause:** Obstacle collision at speed 3.00 m/s (min clearance 2.02m).
- **Last 5 Control Steps Telemetry:**
  ```
  Step | Pos [x, y, z]           | Vel [vx, vy, vz]        | Speed | Clr   | State    | Action Executed
  -----+-------------------------+-------------------------+-------+-------+----------+----------------
    43 | [ 0.80, -2.96, 1.51]    | [ 1.89,  2.33, -0.03]   |  3.00 |  2.35 | NOMINAL  | [0.63, 0.78, -0.01]
    44 | [ 0.74, -2.87, 1.51]    | [-1.46,  2.09, 0.01]    |  2.54 |  2.25 | NOMINAL  | [-0.48, 0.70, 0.00]
    45 | [ 0.84, -2.79, 1.51]    | [ 2.34,  1.88, 0.04]    |  3.00 |  2.17 | NOMINAL  | [0.78, 0.63, 0.01]
    46 | [ 0.74, -2.72, 1.51]    | [-2.46,  1.71, 0.01]    |  3.00 |  2.09 | NOMINAL  | [-0.82, 0.57, 0.00]
    47 | [ 0.63, -2.66, 1.51]    | [-2.65,  1.40, -0.03]   |  3.00 |  2.02 | NOMINAL  | [-0.89, 0.47, -0.01]
  ```

### [Seed 5048] Configuration: Shield ON (Camera) — Outcome: `OBSTACLE_COLLISION`
- **Steps:** 29 | **Reward:** 6.33 | **Min Clearance:** 1.042 m
- **Diagnostic Cause:** Obstacle collision at speed 2.86 m/s (min clearance 4.17m).
- **Last 5 Control Steps Telemetry:**
  ```
  Step | Pos [x, y, z]           | Vel [vx, vy, vz]        | Speed | Clr   | State    | Action Executed
  -----+-------------------------+-------------------------+-------+-------+----------+----------------
    25 | [ 0.20, -5.21, 1.50]    | [ 0.25,  2.88, -0.02]   |  2.89 |  4.64 | NOMINAL  | [0.08, 0.96, -0.01]
    26 | [ 0.22, -5.10, 1.50]    | [ 0.42,  2.85, -0.02]   |  2.88 |  4.53 | NOMINAL  | [0.14, 0.95, -0.01]
    27 | [ 0.18, -4.98, 1.50]    | [-0.88,  2.85, -0.03]   |  2.99 |  4.41 | NOMINAL  | [-0.29, 0.95, -0.01]
    28 | [ 0.16, -4.86, 1.50]    | [-0.55,  2.84, 0.01]    |  2.89 |  4.29 | NOMINAL  | [-0.18, 0.95, 0.00]
    29 | [ 0.15, -4.74, 1.50]    | [-0.32,  2.84, -0.01]   |  2.86 |  4.17 | NOMINAL  | [-0.11, 0.95, -0.00]
  ```

### [Seed 5049] Configuration: Shield ON (Camera) — Outcome: `OBSTACLE_COLLISION`
- **Steps:** 93 | **Reward:** -181.4 | **Min Clearance:** 0.4 m
- **Diagnostic Cause:** Obstacle collision at speed 1.54 m/s (min clearance 0.40m).
- **Last 5 Control Steps Telemetry:**
  ```
  Step | Pos [x, y, z]           | Vel [vx, vy, vz]        | Speed | Clr   | State    | Action Executed
  -----+-------------------------+-------------------------+-------+-------+----------+----------------
    89 | [ 0.21, -1.08, 1.51]    | [ 1.50,  0.35, -0.02]   |  1.54 |  0.45 | REROUTE  | [0.50, 0.12, -0.01]
    90 | [ 0.27, -1.07, 1.51]    | [ 1.50,  0.35, -0.02]   |  1.54 |  0.43 | REROUTE  | [0.50, 0.12, -0.01]
    91 | [ 0.33, -1.05, 1.51]    | [ 1.50,  0.35, -0.02]   |  1.54 |  0.42 | REROUTE  | [0.50, 0.12, -0.01]
    92 | [ 0.39, -1.04, 1.51]    | [ 1.50,  0.35, -0.02]   |  1.54 |  0.41 | REROUTE  | [0.50, 0.12, -0.01]
    93 | [ 0.46, -1.02, 1.51]    | [ 1.50,  0.35, -0.02]   |  1.54 |  0.40 | REROUTE  | [0.50, 0.12, -0.01]
  ```
