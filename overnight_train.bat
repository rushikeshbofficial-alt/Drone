@echo off
cd /d "%~dp0"
set CUDA_VISIBLE_DEVICES=0
set PYBULLET_EGL=1
TITLE OVERNIGHT 4-HOUR DRONE TRAINING + AUTO SHUTDOWN
COLOR 0B
CLS

echo =========================================================================
echo       OVERNIGHT HIGH-ACCURACY PPO DRONE TRAINING (4-HOUR SESSION)
echo =========================================================================
echo.
echo  [*] Target Training Duration : ~4 Hours
echo  [*] Total Environment Steps : 4,000,000 Steps
echo  [*] Parallel Environments  : 12 Workers (SharedMemory SubprocVecEnv)
echo  [*] Hardware Acceleration   : NVIDIA RTX 5060 (CUDA Device 0, BF16 AMP)
echo  [*] Live 3-Panel Dashboard  : LAUNCHED (Auto-Updating OpenCV GUI Window)
echo  [*] TensorBoard Web Overview: LAUNCHED (http://localhost:6006 Browser Window)
echo  [*] Post-Training Action    : AUTOMATIC COMPUTER SHUTDOWN
echo.
echo =========================================================================
echo  [WARNING] Your computer will automatically SHUT DOWN once training finishes!
echo  If you want to cancel at any point, press Ctrl+C or close this window.
echo =========================================================================
echo.

if exist "best_model.pt" goto LAUNCH_SERVICES

echo [!] No pre-trained checkpoint found. Running Expert BC Pre-Trainer first (~5 mins)...
python pretrain_bc.py --n-demo-envs 300 --target-demo-steps 80000 --bc-epochs 60

:LAUNCH_SERVICES
echo.
echo [*] Step 1/3: Launching TensorBoard Web Overview at http://localhost:6006 ...
start "TensorBoard Web Monitor" /min cmd /c "python -m tensorboard.main --logdir runs"
ping 127.0.0.1 -n 3 > nul
start "" "http://localhost:6006"

echo.
echo =========================================================================
echo [*] Step 2/3: Launching 4,000,000 Timestep PPO Training + Live Dashboard Window...
echo =========================================================================
echo.

python train.py --total-timesteps 4000000 --n-envs 12 --n-steps 512 --batch-size 1024 --update-epochs 10 --dashboard

echo.
echo =========================================================================
echo  [+] OVERNIGHT PPO MODEL TRAINING COMPLETE!
echo  [+] High-Accuracy Model Weights saved to 'best_model.pt'.
echo =========================================================================
echo.
echo  [!] INITIATING AUTOMATIC COMPUTER SHUTDOWN IN 60 SECONDS...
echo  [!] To CANCEL shutdown: Open Command Prompt and type: shutdown /a
echo.

shutdown /s /f /t 60 /c "Overnight Autonomous Drone PPO Training Complete! Computer shutting down."

echo Shutdown initiated. Press any key to CANCEL shutdown...
pause
shutdown /a
echo.
echo [+] Shutdown CANCELLED! PC will remain ON.
pause
