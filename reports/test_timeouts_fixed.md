# Stop, Hover & Re-Route (SHR) Drone Safety Shield Benchmark Report

**Date:** 2026-10-15T22:39:02Z  
**Seeds:** `2005,2011,2015,2016,2018,2021,2022` (7 episodes)  
**Checkpoint:** `best_model.pt`  

## Executive Summary & Comparison Table

| Metric | Baseline (OFF) | Shield ON (Oracle) | Shield ON (Camera) | Target |
|---|:---:|:---:|:---:|:---:|
| **Success Rate (95% CI)** | — |   0.0% [ 0.0%, 35.4%] (0/7) | — | **>= 85.0%** |
| **Total Collision Rate** | — |   0.0% [ 0.0%, 35.4%] (0/7) | — | **<= 2.0%** |
| Obstacle Collisions | — |   0.0% [ 0.0%, 35.4%] (0/7) | — | — |
| Wall OOB Collisions | — |   0.0% [ 0.0%, 35.4%] (0/7) | — | — |
| Timeout Rate | — | 100.0% [64.6%, 100.0%] (7/7) | — | **<= 5.0%** |
| **Mean Reward** | — +/- — | -1996.77 +/- 923.95 | — +/- — | — |
| **Mean Min Clearance** | — m | 0.26 m | — m | — |
| **Mean Episode Steps** | — | 500.0 | — | — |
| **Standoff Distance** | N/A | 0.93 m | — m | **>= 0.45 m** |
| **Step Overhead (Baseline Succ)** | Baseline | —% | —% | **<= 15.0%** |

## Acceptance Criteria Audit

## Crash Forensics Log

Total non-success episodes analyzed: **7**

### [Seed 2005] Configuration: Shield ON (oracle) — Outcome: `TIMEOUT`
- **Steps:** 500 | **Reward:** -2428.39 | **Min Clearance:** 0.26 m
- **Diagnostic Cause:** Exceeded maximum episode limit (500 steps) without reaching goal.
- **Last 5 Control Steps Telemetry:**
  ```
  Step | Pos [x, y, z]           | Vel [vx, vy, vz]        | Speed | Clr   | State    | Action Executed
  -----+-------------------------+-------------------------+-------+-------+----------+----------------
   496 | [ 1.07, -2.30, 1.51]    | [-1.40,  1.50, -0.03]   |  2.05 |  0.55 | REROUTE  | [-0.47, 0.50, -0.01]
   497 | [ 1.01, -2.24, 1.51]    | [-1.40,  1.60, -0.02]   |  2.13 |  0.74 | REROUTE  | [-0.47, 0.53, -0.01]
   498 | [ 1.00, -2.19, 1.51]    | [-0.32,  1.16, -0.02]   |  1.20 |  0.69 | NOMINAL  | [-0.11, 0.39, -0.01]
   499 | [ 1.04, -2.17, 1.51]    | [ 1.09,  0.53, 0.06]    |  1.21 |  0.69 | NOMINAL  | [0.36, 0.17, 0.02]
   500 | [ 1.04, -2.17, 1.51]    | [ 0.00,  0.00, 0.00]    |  0.00 |  0.44 | NOMINAL  | [0.00, 0.00, 0.00]
  ```

### [Seed 2011] Configuration: Shield ON (oracle) — Outcome: `TIMEOUT`
- **Steps:** 500 | **Reward:** -2992.51 | **Min Clearance:** 0.361 m
- **Diagnostic Cause:** Exceeded maximum episode limit (500 steps) without reaching goal.
- **Last 5 Control Steps Telemetry:**
  ```
  Step | Pos [x, y, z]           | Vel [vx, vy, vz]        | Speed | Clr   | State    | Action Executed
  -----+-------------------------+-------------------------+-------+-------+----------+----------------
   496 | [ 2.00, -1.13, 1.50]    | [ 0.00, -0.80, 0.00]    |  0.80 |  0.53 | RETREAT  | [0.00, -0.27, 0.00]
   497 | [ 2.00, -1.16, 1.50]    | [ 0.00, -0.80, 0.00]    |  0.80 |  4.79 | RETREAT  | [0.00, -0.27, 0.00]
   498 | [ 2.00, -1.20, 1.50]    | [ 0.00, -0.80, 0.00]    |  0.80 |  4.79 | RETREAT  | [0.00, -0.27, 0.00]
   499 | [ 2.00, -1.23, 1.50]    | [ 0.00, -0.80, 0.00]    |  0.80 |  4.79 | RETREAT  | [0.00, -0.27, 0.00]
   500 | [ 2.00, -1.26, 1.50]    | [ 0.00, -0.80, 0.00]    |  0.80 |  4.79 | RETREAT  | [0.00, -0.27, 0.00]
  ```

### [Seed 2015] Configuration: Shield ON (oracle) — Outcome: `TIMEOUT`
- **Steps:** 500 | **Reward:** -2396.44 | **Min Clearance:** 0.364 m
- **Diagnostic Cause:** Exceeded maximum episode limit (500 steps) without reaching goal.
- **Last 5 Control Steps Telemetry:**
  ```
  Step | Pos [x, y, z]           | Vel [vx, vy, vz]        | Speed | Clr   | State    | Action Executed
  -----+-------------------------+-------------------------+-------+-------+----------+----------------
   496 | [-0.93,  2.84, 1.50]    | [ 0.00, -0.80, 0.01]    |  0.80 |  4.90 | RETREAT  | [0.00, -0.27, 0.00]
   497 | [-0.93,  2.81, 1.50]    | [ 0.00, -0.80, 0.01]    |  0.80 |  4.88 | RETREAT  | [0.00, -0.27, 0.00]
   498 | [-0.93,  2.77, 1.50]    | [ 0.00, -0.80, 0.01]    |  0.80 |  4.85 | RETREAT  | [0.00, -0.27, 0.00]
   499 | [-0.93,  2.74, 1.50]    | [ 0.00, -0.80, 0.01]    |  0.80 |  4.83 | RETREAT  | [0.00, -0.27, 0.00]
   500 | [-0.93,  2.71, 1.50]    | [ 0.00, -0.80, 0.01]    |  0.80 |  4.81 | SCAN     | [0.00, -0.27, 0.00]
  ```

### [Seed 2016] Configuration: Shield ON (oracle) — Outcome: `TIMEOUT`
- **Steps:** 500 | **Reward:** -40.01 | **Min Clearance:** 0.123 m
- **Diagnostic Cause:** Exceeded maximum episode limit (500 steps) without reaching goal.
- **Last 5 Control Steps Telemetry:**
  ```
  Step | Pos [x, y, z]           | Vel [vx, vy, vz]        | Speed | Clr   | State    | Action Executed
  -----+-------------------------+-------------------------+-------+-------+----------+----------------
   496 | [ 1.60, -5.24, 1.50]    | [-0.68,  0.99, -0.03]   |  1.20 |  0.69 | NOMINAL  | [-0.23, 0.33, -0.01]
   497 | [ 1.57, -5.22, 1.50]    | [-0.81,  0.42, -0.02]   |  0.91 |  0.59 | NOMINAL  | [-0.27, 0.14, -0.01]
   498 | [ 1.54, -5.17, 1.50]    | [-0.58,  1.01, -0.04]   |  1.17 |  0.68 | NOMINAL  | [-0.19, 0.34, -0.01]
   499 | [ 1.54, -5.15, 1.49]    | [-0.04,  0.68, -0.03]   |  0.68 |  0.53 | NOMINAL  | [-0.01, 0.23, -0.01]
   500 | [ 1.53, -5.13, 1.49]    | [-0.27,  0.48, -0.02]   |  0.55 |  0.50 | NOMINAL  | [-0.09, 0.16, -0.01]
  ```

### [Seed 2018] Configuration: Shield ON (oracle) — Outcome: `TIMEOUT`
- **Steps:** 500 | **Reward:** -2512.4 | **Min Clearance:** 0.231 m
- **Diagnostic Cause:** Exceeded maximum episode limit (500 steps) without reaching goal.
- **Last 5 Control Steps Telemetry:**
  ```
  Step | Pos [x, y, z]           | Vel [vx, vy, vz]        | Speed | Clr   | State    | Action Executed
  -----+-------------------------+-------------------------+-------+-------+----------+----------------
   496 | [-0.65, -1.78, 1.50]    | [ 1.40,  1.50, 0.00]    |  2.05 |  0.65 | REROUTE  | [0.47, 0.50, 0.00]
   497 | [-0.65, -1.81, 1.50]    | [ 0.00, -0.80, 0.00]    |  0.80 |  0.39 | RETREAT  | [0.00, -0.27, 0.00]
   498 | [-0.65, -1.84, 1.50]    | [ 0.00, -0.80, 0.00]    |  0.80 |  0.46 | RETREAT  | [0.00, -0.27, 0.00]
   499 | [-0.65, -1.88, 1.50]    | [ 0.00, -0.80, 0.00]    |  0.80 |  0.46 | RETREAT  | [0.00, -0.27, 0.00]
   500 | [-0.65, -1.91, 1.50]    | [ 0.00, -0.80, 0.00]    |  0.80 |  0.48 | RETREAT  | [0.00, -0.27, 0.00]
  ```

### [Seed 2021] Configuration: Shield ON (oracle) — Outcome: `TIMEOUT`
- **Steps:** 500 | **Reward:** -2288.07 | **Min Clearance:** 0.242 m
- **Diagnostic Cause:** Exceeded maximum episode limit (500 steps) without reaching goal.
- **Last 5 Control Steps Telemetry:**
  ```
  Step | Pos [x, y, z]           | Vel [vx, vy, vz]        | Speed | Clr   | State    | Action Executed
  -----+-------------------------+-------------------------+-------+-------+----------+----------------
   496 | [ 0.30, -0.83, 1.50]    | [ 0.00, -0.80, 0.00]    |  0.80 |  0.68 | RETREAT  | [0.00, -0.27, 0.00]
   497 | [ 0.30, -0.86, 1.50]    | [ 0.00, -0.80, 0.00]    |  0.80 |  2.07 | RETREAT  | [0.00, -0.27, 0.00]
   498 | [ 0.30, -0.90, 1.50]    | [ 0.00, -0.80, 0.00]    |  0.80 |  2.07 | RETREAT  | [0.00, -0.27, 0.00]
   499 | [ 0.30, -0.93, 1.50]    | [ 0.00, -0.80, 0.00]    |  0.80 |  2.26 | RETREAT  | [0.00, -0.27, 0.00]
   500 | [ 0.30, -0.96, 1.50]    | [ 0.00, -0.80, 0.00]    |  0.80 |  2.23 | RETREAT  | [0.00, -0.27, 0.00]
  ```

### [Seed 2022] Configuration: Shield ON (oracle) — Outcome: `TIMEOUT`
- **Steps:** 500 | **Reward:** -1319.57 | **Min Clearance:** 0.249 m
- **Diagnostic Cause:** Exceeded maximum episode limit (500 steps) without reaching goal.
- **Last 5 Control Steps Telemetry:**
  ```
  Step | Pos [x, y, z]           | Vel [vx, vy, vz]        | Speed | Clr   | State    | Action Executed
  -----+-------------------------+-------------------------+-------+-------+----------+----------------
   496 | [ 1.58, -4.24, 1.49]    | [-1.40,  0.00, 0.02]    |  1.40 |  0.45 | REROUTE  | [-0.47, 0.00, 0.01]
   497 | [ 1.52, -4.23, 1.49]    | [-1.40,  0.40, 0.01]    |  1.46 |  0.88 | REROUTE  | [-0.47, 0.13, 0.01]
   498 | [ 1.58, -4.21, 1.49]    | [ 1.40,  0.40, 0.01]    |  1.46 |  0.67 | REROUTE  | [0.47, 0.13, 0.01]
   499 | [ 1.58, -4.24, 1.49]    | [ 0.00, -0.80, 0.01]    |  0.80 |  0.65 | RETREAT  | [0.00, -0.27, 0.00]
   500 | [ 1.58, -4.28, 1.50]    | [ 0.00, -0.80, 0.01]    |  0.80 |  5.16 | RETREAT  | [0.00, -0.27, 0.00]
  ```
