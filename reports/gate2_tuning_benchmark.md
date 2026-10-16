# Stop, Hover & Re-Route (SHR) Drone Safety Shield Benchmark Report

**Date:** 2026-10-16T08:43:14Z  
**Seeds:** `4000-4029` (30 episodes)  
**Checkpoint:** `best_model_baseline.pt`  

## Executive Summary & Comparison Table

| Metric | Baseline (OFF) | Shield ON (Oracle) | Shield ON (Camera) | Target |
|---|:---:|:---:|:---:|:---:|
| **Success Rate (95% CI)** | — | 100.0% [88.6%, 100.0%] (30/30) | — | **>= 85.0%** |
| **Total Collision Rate** | — |   0.0% [ 0.0%, 11.4%] (0/30) | — | **<= 2.0%** |
| Obstacle Collisions | — |   0.0% [ 0.0%, 11.4%] (0/30) | — | — |
| Wall OOB Collisions | — |   0.0% [ 0.0%, 11.4%] (0/30) | — | — |
| Timeout Rate | — |   0.0% [ 0.0%, 11.4%] (0/30) | — | **<= 5.0%** |
| **Mean Reward** | — +/- — | -256.73 +/- 305.18 | — +/- — | — |
| **Mean Min Clearance** | — m | 0.29 m | — m | — |
| **Mean Episode Steps** | — | 261.1 | — | — |
| **Standoff Distance** | N/A | 2.19 m | — m | **>= 0.45 m** |
| **Step Overhead (Baseline Succ)** | Baseline | —% | —% | **<= 15.0%** |

## Acceptance Criteria Audit

## Crash Forensics Log

No non-success episodes observed. Perfect zero-collision / zero-timeout execution!
