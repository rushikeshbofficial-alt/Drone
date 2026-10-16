# Stop, Hover & Re-Route (SHR) Drone Safety Shield Benchmark Report

**Date:** 2026-10-16T08:44:18Z  
**Seeds:** `4030-4059` (30 episodes)  
**Checkpoint:** `best_model_baseline.pt`  

## Executive Summary & Comparison Table

| Metric | Baseline (OFF) | Shield ON (Oracle) | Shield ON (Camera) | Target |
|---|:---:|:---:|:---:|:---:|
| **Success Rate (95% CI)** | — | 100.0% [88.6%, 100.0%] (30/30) | — | **>= 85.0%** |
| **Total Collision Rate** | — |   0.0% [ 0.0%, 11.4%] (0/30) | — | **<= 2.0%** |
| Obstacle Collisions | — |   0.0% [ 0.0%, 11.4%] (0/30) | — | — |
| Wall OOB Collisions | — |   0.0% [ 0.0%, 11.4%] (0/30) | — | — |
| Timeout Rate | — |   0.0% [ 0.0%, 11.4%] (0/30) | — | **<= 5.0%** |
| **Mean Reward** | — +/- — | -185.13 +/- 284.00 | — +/- — | — |
| **Mean Min Clearance** | — m | 0.40 m | — m | — |
| **Mean Episode Steps** | — | 245.5 | — | — |
| **Standoff Distance** | N/A | 1.85 m | — m | **>= 0.45 m** |
| **Step Overhead (Baseline Succ)** | Baseline | —% | —% | **<= 15.0%** |

## Acceptance Criteria Audit

## Crash Forensics Log

No non-success episodes observed. Perfect zero-collision / zero-timeout execution!
