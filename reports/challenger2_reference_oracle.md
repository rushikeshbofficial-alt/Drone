# Stop, Hover & Re-Route (SHR) Drone Safety Shield Benchmark Report

**Date:** 2026-10-15T22:49:57Z  
**Seeds:** `reference` (5 episodes)  
**Checkpoint:** `best_model.pt`  

## Executive Summary & Comparison Table

| Metric | Baseline (OFF) | Shield ON (Oracle) | Shield ON (Camera) | Target |
|---|:---:|:---:|:---:|:---:|
| **Success Rate (95% CI)** | — | 100.0% [56.6%, 100.0%] (5/5) | — | **>= 85.0%** |
| **Total Collision Rate** | — |   0.0% [ 0.0%, 43.4%] (0/5) | — | **<= 2.0%** |
| Obstacle Collisions | — |   0.0% [ 0.0%, 43.4%] (0/5) | — | — |
| Wall OOB Collisions | — |   0.0% [ 0.0%, 43.4%] (0/5) | — | — |
| Timeout Rate | — |   0.0% [ 0.0%, 43.4%] (0/5) | — | **<= 5.0%** |
| **Mean Reward** | — +/- — | -164.60 +/- 345.79 | — +/- — | — |
| **Mean Min Clearance** | — m | 0.56 m | — m | — |
| **Mean Episode Steps** | — | 226.8 | — | — |
| **Standoff Distance** | N/A | 1.26 m | — m | **>= 0.45 m** |
| **Step Overhead (Baseline Succ)** | Baseline | —% | —% | **<= 15.0%** |

## Acceptance Criteria Audit

## Crash Forensics Log

No non-success episodes observed. Perfect zero-collision / zero-timeout execution!
