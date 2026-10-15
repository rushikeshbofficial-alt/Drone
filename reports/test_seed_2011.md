# Stop, Hover & Re-Route (SHR) Drone Safety Shield Benchmark Report

**Date:** 2026-10-15T22:40:50Z  
**Seeds:** `2011` (1 episodes)  
**Checkpoint:** `best_model.pt`  

## Executive Summary & Comparison Table

| Metric | Baseline (OFF) | Shield ON (Oracle) | Shield ON (Camera) | Target |
|---|:---:|:---:|:---:|:---:|
| **Success Rate (95% CI)** | — |   0.0% [ 0.0%, 79.3%] (0/1) | — | **>= 85.0%** |
| **Total Collision Rate** | — |   0.0% [ 0.0%, 79.3%] (0/1) | — | **<= 2.0%** |
| Obstacle Collisions | — |   0.0% [ 0.0%, 79.3%] (0/1) | — | — |
| Wall OOB Collisions | — |   0.0% [ 0.0%, 79.3%] (0/1) | — | — |
| Timeout Rate | — | 100.0% [20.7%, 100.0%] (1/1) | — | **<= 5.0%** |
| **Mean Reward** | — +/- — | -2580.61 +/- 0.00 | — +/- — | — |
| **Mean Min Clearance** | — m | 0.20 m | — m | — |
| **Mean Episode Steps** | — | 500.0 | — | — |
| **Standoff Distance** | N/A | 1.05 m | — m | **>= 0.45 m** |
| **Step Overhead (Baseline Succ)** | Baseline | —% | —% | **<= 15.0%** |

## Acceptance Criteria Audit

## Crash Forensics Log

Total non-success episodes analyzed: **1**

### [Seed 2011] Configuration: Shield ON (oracle) — Outcome: `TIMEOUT`
- **Steps:** 500 | **Reward:** -2580.61 | **Min Clearance:** 0.202 m
- **Diagnostic Cause:** Exceeded maximum episode limit (500 steps) without reaching goal.
- **Last 5 Control Steps Telemetry:**
  ```
  Step | Pos [x, y, z]           | Vel [vx, vy, vz]        | Speed | Clr   | State    | Action Executed
  -----+-------------------------+-------------------------+-------+-------+----------+----------------
   496 | [ 2.03, -0.93, 1.50]    | [ 0.00, -0.80, -0.00]   |  0.80 |  4.75 | RETREAT  | [0.00, -0.27, -0.00]
   497 | [ 2.03, -0.97, 1.50]    | [ 0.00, -0.80, -0.00]   |  0.80 |  4.75 | RETREAT  | [0.00, -0.27, -0.00]
   498 | [ 2.03, -1.00, 1.50]    | [ 0.00, -0.80, -0.00]   |  0.80 |  4.75 | SCAN     | [0.00, -0.27, -0.00]
   499 | [ 2.08, -0.94, 1.50]    | [ 1.40,  1.50, -0.00]   |  2.05 |  4.75 | REROUTE  | [0.47, 0.50, -0.00]
   500 | [ 2.14, -0.87, 1.50]    | [ 1.40,  1.60, -0.00]   |  2.13 |  0.48 | REROUTE  | [0.47, 0.53, -0.00]
  ```
