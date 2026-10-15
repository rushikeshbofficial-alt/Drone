# Stop, Hover & Re-Route (SHR) Drone Safety Shield Benchmark Report

**Date:** 2026-10-15T22:35:30Z  
**Seeds:** `2011,2019,2022` (3 episodes)  
**Checkpoint:** `best_model.pt`  

## Executive Summary & Comparison Table

| Metric | Baseline (OFF) | Shield ON (Oracle) | Shield ON (Camera) | Target |
|---|:---:|:---:|:---:|:---:|
| **Success Rate (95% CI)** | — |  66.7% [20.8%, 93.9%] (2/3) | — | **>= 85.0%** |
| **Total Collision Rate** | — |   0.0% [ 0.0%, 56.1%] (0/3) | — | **<= 2.0%** |
| Obstacle Collisions | — |   0.0% [ 0.0%, 56.1%] (0/3) | — | — |
| Wall OOB Collisions | — |   0.0% [ 0.0%, 56.1%] (0/3) | — | — |
| Timeout Rate | — |  33.3% [ 6.1%, 79.2%] (1/3) | — | **<= 5.0%** |
| **Mean Reward** | — +/- — | -1152.82 +/- 410.50 | — +/- — | — |
| **Mean Min Clearance** | — m | 0.24 m | — m | — |
| **Mean Episode Steps** | — | 442.3 | — | — |
| **Standoff Distance** | N/A | 0.84 m | — m | **>= 0.45 m** |
| **Step Overhead (Baseline Succ)** | Baseline | —% | —% | **<= 15.0%** |

## Acceptance Criteria Audit

## Crash Forensics Log

Total non-success episodes analyzed: **1**

### [Seed 2022] Configuration: Shield ON (oracle) — Outcome: `TIMEOUT`
- **Steps:** 500 | **Reward:** -1358.06 | **Min Clearance:** 0.27 m
- **Diagnostic Cause:** Exceeded maximum episode limit (500 steps) without reaching goal.
- **Last 5 Control Steps Telemetry:**
  ```
  Step | Pos [x, y, z]           | Vel [vx, vy, vz]        | Speed | Clr   | State    | Action Executed
  -----+-------------------------+-------------------------+-------+-------+----------+----------------
   496 | [ 1.56, -4.10, 1.50]    | [-1.40,  0.00, 0.00]    |  1.40 |  0.61 | REROUTE  | [-0.47, 0.00, 0.00]
   497 | [ 1.50, -4.10, 1.50]    | [-1.40,  0.00, 0.00]    |  1.40 |  0.83 | REROUTE  | [-0.47, 0.00, 0.00]
   498 | [ 1.44, -4.10, 1.50]    | [-1.40,  0.00, 0.00]    |  1.40 |  0.77 | REROUTE  | [-0.47, 0.00, 0.00]
   499 | [ 1.50, -4.10, 1.50]    | [ 1.40,  0.00, 0.00]    |  1.40 |  0.71 | REROUTE  | [0.47, 0.00, 0.00]
   500 | [ 1.56, -4.10, 1.50]    | [ 1.40,  0.00, 0.00]    |  1.40 |  0.73 | REROUTE  | [0.47, 0.00, 0.00]
  ```
