@echo off
cd /d "%~dp0"
set CUDA_VISIBLE_DEVICES=0
set PYBULLET_EGL=1
TITLE Autonomous Drone Navigation - PPO and Real-Time XAI
COLOR 0A
CLS

:MENU
CLS
echo =========================================================================
echo  EXPLAINABLE AUTONOMOUS DRONE NAVIGATION IN UNSTRUCTURED INDOOR ENVIRONMENTS
echo =========================================================================
echo.
echo  [0] EXPERT PRETRAINING (BC) - Run this FIRST! Creates a working model (~5 min)
echo  [1] PPO Fine-Tuning + Live Dashboard (run after Option 0)
echo  [2] Evaluate + Live 3-Panel XAI Dashboard
echo  [3] Launch TensorBoard Monitor (http://localhost:6006)
echo  [4] Run Quick Headless Test
echo  [5] OVERNIGHT 4-HOUR TRAINING + AUTO SHUTDOWN (Run before sleeping)
echo  [6] Exit
echo  [7] Evaluate with SHR Shield v2 (Live 3-Panel GUI Dashboard)
echo  [8] SHR Shield v2 Comparative Safety Benchmark (Reference seeds, OFF vs ON)
echo.
echo =========================================================================
set /p CHOICE="Select an option [0-8]: "

if "%CHOICE%"=="0" goto PRETRAIN
if "%CHOICE%"=="1" goto TRAIN
if "%CHOICE%"=="2" goto EVAL
if "%CHOICE%"=="3" goto TENSORBOARD
if "%CHOICE%"=="4" goto DRYRUN
if "%CHOICE%"=="5" goto OVERNIGHT
if "%CHOICE%"=="6" goto END
if "%CHOICE%"=="7" goto SHIELD_V2_GUI
if "%CHOICE%"=="8" goto SHIELD_V2_BENCH

echo Invalid selection! Please try again.
pause
goto MENU

:PRETRAIN
CLS
echo [*] Starting Expert Behavioral Cloning Pretraining...
echo [*] Physics-based expert generates demonstrations, neural net learns to imitate.
echo [*] Takes approximately 5 minutes. Saves best_model.pt when done.
python pretrain_bc.py --n-demo-envs 300 --target-demo-steps 80000 --bc-epochs 60
echo.
echo [*] Pretraining complete! You can now run Option 1 for PPO fine-tuning
echo [*] or jump straight to Option 2 for evaluation.
pause
goto MENU

:TRAIN
CLS
echo [*] Starting High-Throughput Parallel PPO Training (SharedMemory IPC)...
echo [*] Config: Parallel Environments (n_envs=12), BF16 AMP, Batch 1024
python train.py --total-timesteps 500000 --n-envs 12 --n-steps 512 --batch-size 1024 --update-epochs 10 --dashboard
echo.
echo [*] Training process finished.
pause
goto MENU

:EVAL
CLS
echo [*] Launching Evaluation and Live XAI Dashboard...
echo [*] Eval Mode: TRAINING seeds (same layouts as training - fair first test)
echo [*] To test unseen environments: python evaluate_and_visualize.py --eval-mode unseen --gui
python evaluate_and_visualize.py --checkpoint best_model.pt --eval-mode training --gui
echo.
echo [*] Evaluation finished.
pause
goto MENU

:TENSORBOARD
CLS
echo [*] Starting TensorBoard server at http://localhost:6006 ...
start "" http://localhost:6006
python -m tensorboard.main --logdir runs
pause
goto MENU

:DRYRUN
CLS
echo [*] Running quick evaluation dry-run...
python evaluate_and_visualize.py --max-steps 500 --headless
echo.
echo [*] Quick test finished.
pause
goto MENU

:OVERNIGHT
call overnight_train.bat
goto MENU

:SHIELD_V2_GUI
CLS
echo [*] Launching Evaluation with SHR Safety Shield v2 (Oracle mode)...
echo [*] Live 3-Panel XAI Dashboard with Real-Time Shield Telemetry
echo [*] Privileged Simulator Information: analytical raycasting + A* path planning
echo [*] Checkpoint: best_model_baseline.pt
echo [*] Eval Mode: UNSEEN reference environments (seeds 101, 202, 303, 404, 505)
python evaluate_and_visualize.py --checkpoint best_model_baseline.pt --eval-mode unseen --gui --shield --shield-mode oracle --shield-version v2
echo.
echo [*] Shield v2 evaluation finished.
pause
goto MENU

:SHIELD_V2_BENCH
CLS
echo [*] Running SHR Shield v2 Comparative Safety Benchmark...
echo [*] Privileged Simulator Information: analytical raycasting + A* path planning
echo [*] Checkpoint: best_model_baseline.pt
echo [*] Seeds: Reference set [101, 202, 303, 404, 505]
echo [*] Sequential A/B comparison: Baseline (OFF) vs Oracle v2 (ON) vs Camera v2 (ON)
python eval_shield.py --checkpoint best_model_baseline.pt --seeds reference --compare --shield-version v2
echo.
echo [*] Comparative benchmark finished. Reports saved to reports/
pause
goto MENU

:END
echo Exiting...
exit /b 0
