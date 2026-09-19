## 2026-09-19T06:46:14Z

You are spec_miner_m1_1.
Working Directory: c:\Users\Rushikesh\Desktop\Cool Ass Projects\Drone\.agents\spec_miner_m1_1
Workspace root: c:\Users\Rushikesh\Desktop\Cool Ass Projects\Drone

MANDATORY FIRST STEP:
Read c:\Users\Rushikesh\Desktop\Cool Ass Projects\Drone\.agents\ORIGINAL_REQUEST.md completely.
Also read:
- c:\Users\Rushikesh\Desktop\Cool Ass Projects\Drone\.agents\teamwork_preview_orchestrator_1\PROJECT.md

Your Task:
Design the complete specification, architecture, and verification logic for `verify_documentation.py` in the workspace root:
1. Exact validation checks required:
   - Check A: File existence for both `Autonomous_Drone_Navigation_Technical_Documentation.docx` and `TECHNICAL_DOCUMENTATION.md`.
   - Check B: Structural parseability of `Autonomous_Drone_Navigation_Technical_Documentation.docx` using `docx.Document` (ensuring no XML corruption, valid paragraphs, valid tables).
   - Check C: Word count calculation for both documents (counting words in paragraphs and tables for docx, counting words in markdown), verifying combined total > 6,000 words (and reporting individual counts).
   - Check D: Chapter heading verification: asserting the presence of all 6 mandatory chapters in both documents (Executive Summary, System Architecture, Simulation Environment Mechanics, Drone Navigation & Algorithmic Foundations, Granular Module & File Breakdown, Setup, Configuration & Execution).
   - Check E: Complete codebase file coverage: asserting the presence of all 10 audited files in both documents (`environment.py`, `model.py`, `pretrain_bc.py`, `train.py`, `explainability.py`, `evaluate_and_visualize.py`, `run_project.bat`, `overnight_train.bat`, `requirements.txt`, `README.md`).
   - Check F: Mathematical formula check: verifying presence of key formulas ($\tau^{-1}$, Farneback optical flow, potential field vectors, PPO objective/GAE, Spatial IoU).
2. Exit status behavior: Exit code 0 if all tests pass; exit code 1 with detailed failure report if any check fails.
3. Clear console output reporting table with ANSI colors / clear status lines.

Deliverables:
- Write specification and test harness design to `c:\Users\Rushikesh\Desktop\Cool Ass Projects\Drone\.agents\spec_miner_m1_1\verification_harness_spec.md`.
- Write handoff to `c:\Users\Rushikesh\Desktop\Cool Ass Projects\Drone\.agents\spec_miner_m1_1\handoff.md`.
- Send completion message to parent orchestrator.
