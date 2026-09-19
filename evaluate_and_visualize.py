"""
evaluate_and_visualize.py - High-Definition Unified XAI Dashboard
------------------------------------------------------------------
Loads trained Actor-Critic model weights and evaluates performance across 5 unseen layouts.
Renders a crisp, high-definition 3-panel dashboard (1280x540):
1. Panel 1: 3D Environment Overhead Arena Map (Drone, Obstacles, Goal Target)
2. Panel 2: Drone Camera Feed + Dense Optical Flow Motion Vectors
3. Panel 3: Real-Time Saliency Heatmap (XAI Obstacle Focus)
"""

import os
import time
import argparse
import numpy as np
import cv2

from environment import IndoorDroneNavEnv
from model import PhysicsInformedActorCritic
from explainability import DroneXAIEngine

TORCH_AVAILABLE = True
try:
    import torch
except (ImportError, OSError):
    TORCH_AVAILABLE = False


def get_eval_device():
    """Returns CUDA if available (RTX 5060 sm_120 now supported with Nightly), else CPU."""
    if not TORCH_AVAILABLE:
        return "cpu"
    if not torch.cuda.is_available():
        return "cpu"
    return "cuda"


def draw_optical_flow_vectors(rgb_img: np.ndarray, flow: np.ndarray, target_size=(390, 390), step: int = 16) -> np.ndarray:
    """
    Overlays high-definition dense optical flow motion arrows on bicubic upscaled BGR image frame
    with anti-aliased glowing vector arrows and motion direction color-coding.
    """
    target_w, target_h = target_size
    h_orig, w_orig = flow.shape[:2]

    # Bicubic upscaling of raw RGB frame to HD resolution
    hd_rgb = cv2.resize(rgb_img, (target_w, target_h), interpolation=cv2.INTER_CUBIC)
    bgr = cv2.cvtColor(hd_rgb, cv2.COLOR_RGB2BGR)

    # Upscale optical flow vectors to match HD scale
    scale_x = target_w / float(w_orig)
    scale_y = target_h / float(h_orig)
    hd_flow_x = cv2.resize(flow[:, :, 0], (target_w, target_h), interpolation=cv2.INTER_CUBIC) * scale_x
    hd_flow_y = cv2.resize(flow[:, :, 1], (target_w, target_h), interpolation=cv2.INTER_CUBIC) * scale_y

    y, x = np.mgrid[step // 2:target_h:step, step // 2:target_w:step].reshape(2, -1).astype(int)
    fx, fy = hd_flow_x[y, x], hd_flow_y[y, x]

    for i in range(len(x)):
        x1, y1 = x[i], y[i]
        dx, dy = fx[i], fy[i]
        mag = np.hypot(dx, dy)

        if mag > 1.2:
            x2 = int(round(x1 + dx * 2.0))
            y2 = int(round(y1 + dy * 2.0))

            # Dynamic color coding based on motion magnitude: Cyan (steady) -> Lime (active) -> Yellow/Red (fast)
            if mag < 4.0:
                color = (255, 255, 0)   # Cyan
            elif mag < 10.0:
                color = (0, 255, 120)   # Lime
            else:
                color = (0, 200, 255)   # Gold / Yellow

            cv2.arrowedLine(bgr, (x1, y1), (x2, y2), color, 1, cv2.LINE_AA, tipLength=0.35)

    return bgr


def create_unified_dashboard_canvas(
    sim_view: np.ndarray,
    flow_view: np.ndarray,
    saliency_view: np.ndarray,
    fps: float,
    latency_ms: float,
    fidelity_iou: float,
    goal_dist: float,
    step_num: int,
    train_stats: dict = None   # Optional: training metrics dict for live training mode
) -> np.ndarray:
    """
    Assembles a crisp dashboard canvas with 3 side-by-side panels + optional
    live training stats bar at the bottom showing progress, SPS, reward, and losses.
    """
    panel_w, panel_h = 390, 390
    header_h = 80
    stats_h  = 64 if train_stats else 0    # bottom bar only shown during training
    canvas_w = panel_w * 3 + 60
    canvas_h = panel_h + header_h + 40 + stats_h

    # Dark Slate Background
    canvas = np.full((canvas_h, canvas_w, 3), (22, 18, 28), dtype=np.uint8)

    # ── Header Bar ──────────────────────────────────────────────────────────
    cv2.rectangle(canvas, (0, 0), (canvas_w, header_h), (38, 28, 48), -1)
    cv2.line(canvas, (0, header_h), (canvas_w, header_h), (120, 80, 255), 2)

    cv2.putText(canvas, "REAL-TIME EXPLAINABLE AUTONOMOUS DRONE NAVIGATION", (25, 36),
                cv2.FONT_HERSHEY_DUPLEX, 0.75, (255, 255, 255), 1, cv2.LINE_AA)
    cv2.putText(canvas, "MONOCULAR VISION | DENSE OPTICAL FLOW | PHYSICS PPO POLICY | CAPTUM XAI", (25, 62),
                cv2.FONT_HERSHEY_SIMPLEX, 0.44, (160, 120, 255), 1, cv2.LINE_AA)

    # Top-right badge: step / goal dist
    cv2.rectangle(canvas, (canvas_w - 230, 18), (canvas_w - 25, 58), (50, 35, 70), -1)
    cv2.rectangle(canvas, (canvas_w - 230, 18), (canvas_w - 25, 58), (120, 80, 255), 1)
    cv2.putText(canvas, f"STEP: {step_num:,} | GOAL: {goal_dist:.2f}m", (canvas_w - 218, 43),
                cv2.FONT_HERSHEY_SIMPLEX, 0.42, (255, 255, 255), 1, cv2.LINE_AA)

    # ── Panels ───────────────────────────────────────────────────────────────
    # Resize panels using smooth bicubic super-resolution for crystal-clear visuals
    sim_resized  = cv2.resize(sim_view,      (panel_w, panel_h), interpolation=cv2.INTER_CUBIC)
    flow_resized = cv2.resize(flow_view,     (panel_w, panel_h), interpolation=cv2.INTER_CUBIC)
    sal_resized  = cv2.resize(saliency_view, (panel_w, panel_h), interpolation=cv2.INTER_CUBIC)

    x1, y1 = 20,                header_h + 20
    x2, y2 = x1 + panel_w + 15, header_h + 20
    x3, y3 = x2 + panel_w + 15, header_h + 20

    canvas[y1:y1 + panel_h, x1:x1 + panel_w] = sim_resized
    canvas[y2:y2 + panel_h, x2:x2 + panel_w] = flow_resized
    canvas[y3:y3 + panel_h, x3:x3 + panel_w] = sal_resized

    panels_info = [
        (x1, y1, "1. 3D ARENA & DRONE MAP",        f"Target Distance: {goal_dist:.2f} m",                        (200, 160, 255)),
        (x2, y2, "2. DRONE VISION & OPTICAL FLOW",  f"FPS: {fps:.1f}  |  Latency: {latency_ms:.2f} ms",          (0,   255, 120)),
        (x3, y3, "3. XAI SALIENCY HEATMAP",         f"Spatial IoU Fidelity: {fidelity_iou:.3f}",                 (0,   200, 255)),
    ]

    for px, py, title, metric, accent in panels_info:
        cv2.rectangle(canvas, (px, py), (px + panel_w, py + panel_h), (80, 60, 100), 2)
        cv2.rectangle(canvas, (px, py), (px + panel_w, py + 32), (30, 22, 42), -1)
        cv2.putText(canvas, title, (px + 12, py + 22),
                    cv2.FONT_HERSHEY_DUPLEX, 0.48, (255, 255, 255), 1, cv2.LINE_AA)
        cv2.rectangle(canvas, (px, py + panel_h - 32), (px + panel_w, py + panel_h), (20, 15, 30), -1)
        cv2.putText(canvas, metric, (px + 12, py + panel_h - 10),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.48, accent, 1, cv2.LINE_AA)

    # ── Training Stats Bar (only shown during training) ──────────────────────
    if train_stats:
        bar_y = header_h + panel_h + 40
        bar_h = stats_h

        # Dark background for stats bar
        cv2.rectangle(canvas, (0, bar_y), (canvas_w, bar_y + bar_h), (28, 20, 40), -1)
        cv2.line(canvas, (0, bar_y), (canvas_w, bar_y), (120, 80, 255), 2)

        gs      = train_stats.get("global_step",    0)
        total   = train_stats.get("total_timesteps", 1)
        sps     = train_stats.get("sps",             0.0)
        best_r  = train_stats.get("best_reward",     float("-inf"))
        ep_cnt  = train_stats.get("episode_count",   0)
        pl      = train_stats.get("policy_loss",     0.0)
        vl      = train_stats.get("value_loss",      0.0)
        entropy = train_stats.get("entropy",         0.0)
        pct     = gs / max(total, 1)

        # Progress bar background + filled portion
        pb_x, pb_y, pb_w, pb_h = 20, bar_y + 14, canvas_w - 40, 12
        cv2.rectangle(canvas, (pb_x, pb_y), (pb_x + pb_w, pb_y + pb_h), (60, 45, 80), -1)
        fill_w = int(pb_w * pct)
        if fill_w > 0:
            # Gradient: purple → cyan
            for i in range(fill_w):
                t = i / max(fill_w, 1)
                r = int(120 * (1 - t) + 0   * t)
                g = int(80  * (1 - t) + 255 * t)
                b = int(255 * (1 - t) + 200 * t)
                cv2.line(canvas, (pb_x + i, pb_y), (pb_x + i, pb_y + pb_h), (b, g, r), 1)
        cv2.rectangle(canvas, (pb_x, pb_y), (pb_x + pb_w, pb_y + pb_h), (120, 80, 255), 1)

        # Pct label on bar
        pct_label = f"{pct * 100:.1f}%  ({gs:,} / {total:,} steps)"
        cv2.putText(canvas, pct_label, (pb_x + 6, pb_y + 9),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.37, (255, 255, 255), 1, cv2.LINE_AA)

        # Metrics row below bar
        my = bar_y + bar_h - 12
        best_str = f"{best_r:.1f}" if best_r != float("-inf") else "---"
        metrics = [
            (f"SPS: {sps:.0f}",          (0, 255, 160)),
            (f"Best Reward: {best_str}",  (0, 200, 255)),
            (f"Episodes: {ep_cnt:,}",     (200, 160, 255)),
            (f"P-Loss: {pl:.4f}",         (255, 200, 80)),
            (f"V-Loss: {vl:.4f}",         (255, 140, 60)),
            (f"Entropy: {entropy:.4f}",   (180, 255, 180)),
        ]
        mx = 25
        for label, color in metrics:
            cv2.putText(canvas, label, (mx, my), cv2.FONT_HERSHEY_SIMPLEX, 0.44, color, 1, cv2.LINE_AA)
            mx += int(canvas_w / len(metrics))

    return canvas




def evaluate_policy(args):
    device = get_eval_device()
    print(f"[*] Evaluation Running on Device: {device}")

    model = PhysicsInformedActorCritic()
    if TORCH_AVAILABLE and hasattr(model, "to"):
        model.to(device)
        if os.path.exists(args.checkpoint):
            print(f"[*] Loading checkpoint: {args.checkpoint}")
            state_dict = torch.load(args.checkpoint, map_location=device, weights_only=True)
            model.load_state_dict(state_dict)
            print(f"[+] Checkpoint loaded successfully.")
        else:
            print(f"[!] WARNING: Checkpoint '{args.checkpoint}' not found! Using random weights.")
        model.eval()

    xai_engine = DroneXAIEngine(model=model, device=device)

    # Evaluate on both training seeds AND unseen seeds for a fair comparison
    if args.eval_mode == "unseen":
        eval_seeds = [101, 202, 303, 404, 505]
        print("[*] Evaluating on 5 UNSEEN environment seeds...")
    elif args.eval_mode == "training":
        eval_seeds = [42, 142, 242, 342, 442]
        print("[*] Evaluating on 5 TRAINING environment seeds (upper bound check)...")
    else:  # 'all'
        eval_seeds = [42, 142, 242, 342, 101, 202, 303, 404, 505]
        print("[*] Evaluating on 4 training + 5 unseen seeds...")

    seed_rewards, seed_successes, seed_collisions = [], [], []
    seed_fidelities, seed_latencies = [], []

    dashboard_win_name = "Real-Time Explainable Autonomous Drone Navigation Dashboard"
    if not args.headless:
        try:
            cv2.namedWindow(dashboard_win_name, cv2.WINDOW_NORMAL)
            cv2.resizeWindow(dashboard_win_name, 1280, 540)
        except Exception as e:
            print(f"[!] Warning: OpenCV GUI window unavailable ({e}). Running in headless mode.")
            args.headless = True

    for seed_idx, seed in enumerate(eval_seeds):
        env = IndoorDroneNavEnv(gui=False, seed=seed, max_steps=args.max_steps)
        obs, info = env.reset(seed=seed)

        ep_reward = 0.0
        step_count = 0
        ep_fidelities = []
        ep_latencies = []

        while True:
            t_start = time.perf_counter()

            vis_obs = obs["visual"]
            vel_obs = obs["velocity"]

            if TORCH_AVAILABLE and hasattr(model, "to"):
                vis_t = torch.tensor(vis_obs, dtype=torch.float32, device=device).unsqueeze(0)
                vel_t = torch.tensor(vel_obs, dtype=torch.float32, device=device).unsqueeze(0)

                with torch.no_grad():
                    action_mean = model(vis_t, vel_t).squeeze(0).cpu().numpy()
            else:
                action_mean = model.forward(vis_obs, vel_obs).flatten()

            saliency_attr = xai_engine.compute_attribution(
                visual_obs=vis_obs,
                velocity_obs=vel_obs,
                target_action_idx=0,
                mode="saliency"
            )

            t_end = time.perf_counter()
            latency_ms = (t_end - t_start) * 1000.0
            ep_latencies.append(latency_ms)

            depth_meters = env.last_depth_map
            if depth_meters is not None:
                fidelity_iou = DroneXAIEngine.compute_explanation_fidelity(saliency_attr, depth_meters)
                ep_fidelities.append(fidelity_iou)
            else:
                fidelity_iou = 0.0

            next_obs, reward, terminated, truncated, step_info = env.step(action_mean)
            ep_reward += reward
            step_count += 1

            rgb_raw = (vis_obs[:3].transpose(1, 2, 0) * 255).astype(np.uint8)
            flow_field = vis_obs[3:5].transpose(1, 2, 0)

            # Panel 1: 3D Overhead Simulation Map (Shows Drone, Obstacles, Goal)
            sim_overhead = env.render_overhead_simulation_view((390, 390))

            # Panel 2: Camera Feed + Dense Optical Flow Vectors
            flow_overlay = draw_optical_flow_vectors(rgb_raw, flow_field)

            # Panel 3: High-Contrast Saliency Heatmap Overlay (TURBO Colormap)
            saliency_overlay = DroneXAIEngine.generate_heatmap_overlay(rgb_raw, saliency_attr, alpha=0.65)

            fps = 1000.0 / (latency_ms + 1e-6)

            if not args.headless:
                try:
                    dashboard_canvas = create_unified_dashboard_canvas(
                        sim_view=sim_overhead,
                        flow_view=flow_overlay,
                        saliency_view=saliency_overlay,
                        fps=fps,
                        latency_ms=latency_ms,
                        fidelity_iou=np.mean(ep_fidelities),
                        goal_dist=step_info.get("dist_to_goal", 0.0),
                        step_num=step_count
                    )
                    cv2.imshow(dashboard_win_name, dashboard_canvas)
                    cv2.waitKey(1)
                except Exception as e:
                    args.headless = True

            obs = next_obs

            if terminated or truncated:
                collision = step_info.get("collision", False)
                goal_reached = step_info.get("goal_reached", False)

                seed_rewards.append(ep_reward)
                seed_successes.append(1.0 if goal_reached else 0.0)
                seed_collisions.append(1.0 if collision else 0.0)
                seed_fidelities.append(np.mean(ep_fidelities) if ep_fidelities else 0.0)
                seed_latencies.append(np.mean(ep_latencies))

                status_str = "SUCCESS" if goal_reached else ("COLLISION" if collision else "TIMEOUT")
                n = len(eval_seeds)
                print(f"[Env {seed_idx+1}/{n} seed={seed}] {status_str} | Steps: {step_count} | "
                      f"Reward: {ep_reward:.2f} | Fidelity: {np.mean(ep_fidelities):.3f} | "
                      f"Latency: {np.mean(ep_latencies):.2f}ms")
                break

        env.close()

    if not args.headless:
        cv2.destroyAllWindows()

    print("\n" + "=" * 65)
    print("      FINAL EVALUATION & EXPLAINABILITY REPORT SUMMARY      ")
    print("=" * 65)
    print(f"Environments Evaluated        : {len(eval_seeds)} ({args.eval_mode} mode)")
    print(f"Mean Episode Reward           : {np.mean(seed_rewards):.2f} +/- {np.std(seed_rewards):.2f}")
    print(f"Success Rate (Goal Reached)  : {np.mean(seed_successes) * 100.0:.1f}%")
    print(f"Collision Rate               : {np.mean(seed_collisions) * 100.0:.1f}%")
    print(f"Mean Explanation Fidelity IoU: {np.mean(seed_fidelities):.4f}")
    print(f"Mean Decision Latency        : {np.mean(seed_latencies):.2f} ms ({1000.0 / np.mean(seed_latencies):.1f} FPS)")
    print("=" * 65)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Evaluation & Live XAI Dashboard for Drone Navigation")
    parser.add_argument("--checkpoint", type=str, default="best_model.pt", help="Path to model checkpoint")
    parser.add_argument("--max-steps",  type=int, default=500, help="Max timesteps per evaluation episode")
    parser.add_argument("--headless",   action="store_true",  help="Run without GUI dashboard")
    parser.add_argument("--gui",        action="store_true",  help="Alias for non-headless (default)")
    parser.add_argument("--eval-mode",  type=str, default="training",
                        choices=["training", "unseen", "all"],
                        help="Which seeds to evaluate on: 'training' (same as training), "
                             "'unseen' (new layouts), 'all' (both)")

    args = parser.parse_args()
    evaluate_policy(args)
