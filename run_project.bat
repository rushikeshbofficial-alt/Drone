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
echo.
echo =========================================================================
set /p CHOICE="Select an option [0-6]: "

if "%CHOICE%"=="0" goto PRETRAIN
if "%CHOICE%"=="1" goto TRAIN
if "%CHOICE%"=="2" goto EVAL
if "%CHOICE%"=="3" goto TENSORBOARD
if "%CHOICE%"=="4" goto DRYRUN
if "%CHOICE%"=="5" goto OVERNIGHT
if "%CHOICE%"=="6" goto END

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
echo [*] Starting Ultra-Fast Single Environment PPO Training (Zero IPC Overhead)...
echo [*] Config: Single Environment (n_envs=1), AMP FP16, torch.compile, Batch 256
python train.py --total-timesteps 200000 --n-envs 1 --n-steps 256 --batch-size 256 --update-epochs 10 --dashboard
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
python evaluate_and_visualize.py --max-steps 500 --gui
echo.
echo [*] Quick test finished.
pause
goto MENU

:OVERNIGHT
call overnight_train.bat
goto MENU

:END
echo Exiting...
exit /b 0
