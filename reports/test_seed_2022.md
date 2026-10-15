# Stop, Hover & Re-Route (SHR) Drone Safety Shield Benchmark Report

**Date:** 2026-10-15T22:36:18Z  
**Seeds:** `2022` (1 episodes)  
**Checkpoint:** `best_model.pt`  

## Executive Summary & Comparison Table

| Metric | Baseline (OFF) | Shield ON (Oracle) | Shield ON (Camera) | Target |
|---|:---:|:---:|:---:|:---:|
| **Success Rate (95% CI)** | — |   0.0% [ 0.0%, 79.3%] (0/1) | — | **>= 85.0%** |
| **Total Collision Rate** | — |   0.0% [ 0.0%, 79.3%] (0/1) | — | **<= 2.0%** |
| Obstacle Collisions | — |   0.0% [ 0.0%, 79.3%] (0/1) | — | — |
| Wall OOB Collisions | — |   0.0% [ 0.0%, 79.3%] (0/1) | — | — |
| Timeout Rate | — | 100.0% [20.7%, 100.0%] (1/1) | — | **<= 5.0%** |
| **Mean Reward** | — +/- — | -851.58 +/- 0.00 | — +/- — | — |
| **Mean Min Clearance** | — m | 0.27 m | — m | — |
| **Mean Episode Steps** | — | 500.0 | — | — |
| **Standoff Distance** | N/A | 0.76 m | — m | **>= 0.45 m** |
| **Step Overhead (Baseline Succ)** | Baseline | —% | —% | **<= 15.0%** |

## Acceptance Criteria Audit

## Crash Forensics Log

Total non-success episodes analyzed: **1**

### [Seed 2022] Configuration: Shield ON (oracle) — Outcome: `TIMEOUT`
- **Steps:** 500 | **Reward:** -851.58 | **Min Clearance:** 0.27 m
- **Diagnostic Cause:** Exceeded maximum episode limit (500 steps) without reaching goal.
- **Last 5 Control Steps Telemetry:**
  ```
  Step | Pos [x, y, z]           | Vel [vx, vy, vz]        | Speed | Clr   | State    | Action Executed
  -----+-------------------------+-------------------------+-------+-------+----------+----------------
   496 | [ 1.19, -4.39, 1.50]    | [-0.67,  0.62, -0.02]   |  0.91 |  0.59 | NOMINAL  | [-0.22, 0.21, -0.01]
   497 | [ 1.20, -4.36, 1.49]    | [ 0.22,  0.74, -0.07]   |  0.78 |  0.55 | NOMINAL  | [0.07, 0.25, -0.02]
   498 | [ 1.19, -4.33, 1.49]    | [-0.24,  0.76, -0.00]   |  0.80 |  0.56 | NOMINAL  | [-0.08, 0.25, -0.00]
   499 | [ 1.19, -4.30, 1.49]    | [-0.01,  0.68, -0.04]   |  0.68 |  0.53 | NOMINAL  | [-0.00, 0.23, -0.01]
   500 | [ 1.19, -4.28, 1.49]    | [ 0.06,  0.53, -0.00]   |  0.53 |  0.50 | NOMINAL  | [0.02, 0.18, -0.00]
  ```
