# Stop, Hover & Re-Route (SHR) Drone Safety Shield Benchmark Report

**Date:** 2026-10-15T22:40:18Z  
**Seeds:** `2005,2011,2015,2016,2018,2021,2022` (7 episodes)  
**Checkpoint:** `best_model.pt`  

## Executive Summary & Comparison Table

| Metric | Baseline (OFF) | Shield ON (Oracle) | Shield ON (Camera) | Target |
|---|:---:|:---:|:---:|:---:|
| **Success Rate (95% CI)** | — |  85.7% [48.7%, 97.4%] (6/7) | — | **>= 85.0%** |
| **Total Collision Rate** | — |   0.0% [ 0.0%, 35.4%] (0/7) | — | **<= 2.0%** |
| Obstacle Collisions | — |   0.0% [ 0.0%, 35.4%] (0/7) | — | — |
| Wall OOB Collisions | — |   0.0% [ 0.0%, 35.4%] (0/7) | — | — |
| Timeout Rate | — |  14.3% [ 2.6%, 51.3%] (1/7) | — | **<= 5.0%** |
| **Mean Reward** | — +/- — | -690.27 +/- 817.51 | — +/- — | — |
| **Mean Min Clearance** | — m | 0.13 m | — m | — |
| **Mean Episode Steps** | — | 304.4 | — | — |
| **Standoff Distance** | N/A | 1.65 m | — m | **>= 0.45 m** |
| **Step Overhead (Baseline Succ)** | Baseline | —% | —% | **<= 15.0%** |

## Acceptance Criteria Audit

## Crash Forensics Log

Total non-success episodes analyzed: **1**

### [Seed 2011] Configuration: Shield ON (oracle) — Outcome: `TIMEOUT`
- **Steps:** 500 | **Reward:** -2586.24 | **Min Clearance:** 0.201 m
- **Diagnostic Cause:** Exceeded maximum episode limit (500 steps) without reaching goal.
- **Last 5 Control Steps Telemetry:**
  ```
  Step | Pos [x, y, z]           | Vel [vx, vy, vz]        | Speed | Clr   | State    | Action Executed
  -----+-------------------------+-------------------------+-------+-------+----------+----------------
   496 | [ 2.06, -0.92, 1.50]    | [ 1.40,  1.60, -0.00]   |  2.13 |  0.58 | REROUTE  | [0.47, 0.53, -0.00]
   497 | [ 2.07, -0.90, 1.50]    | [ 0.27,  0.46, -0.00]   |  0.53 |  0.50 | NOMINAL  | [0.09, 0.15, -0.00]
   498 | [ 2.07, -0.88, 1.50]    | [ 0.04,  0.39, 0.02]    |  0.40 |  0.48 | NOMINAL  | [0.01, 0.13, 0.01]
   499 | [ 2.08, -0.87, 1.50]    | [ 0.17,  0.24, 0.07]    |  0.30 |  0.47 | NOMINAL  | [0.06, 0.08, 0.02]
   500 | [ 2.08, -0.87, 1.50]    | [ 0.08,  0.09, 0.01]    |  0.12 |  0.45 | NOMINAL  | [0.03, 0.03, 0.01]
  ```
