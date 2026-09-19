"""
explainability.py - High-Definition Real-Time Explainable AI (XAI) Engine
--------------------------------------------------------------------------
Implements attribution analysis (Vanilla Saliency for live dashboard,
Integrated Gradients for evaluation mode) with dual-input tuple signature support.

Renders ultra-crisp, high-definition thermal heat vision overlays using:
  - Gaussian spatial smoothing & cubic super-resolution upscaling
  - Google TURBO vibrant colormap with non-linear gamma contrast boost
  - Adaptive alpha masking (keeps background clear, obstacles glow with intense heat)
  - Neon peak-saliency contour highlights around obstacle boundaries
  - Spatial IoU Explanation Fidelity metrics
"""

import numpy as np
import cv2

# Check PyTorch availability
TORCH_AVAILABLE = True
try:
    import torch
    from captum.attr import Saliency, IntegratedGradients
except (ImportError, OSError):
    TORCH_AVAILABLE = False


class DroneXAIEngine:
    """
    XAI Engine performing attribution on dual-input (visual_tensor, velocity_tensor) models.
    Supports fast Saliency for live 30+ FPS dashboards and Integrated Gradients for evaluation.
    """

    def __init__(self, model, device: str = "cpu"):
        self.model = model
        self.device = device

        if TORCH_AVAILABLE and hasattr(model, "to"):
            try:
                self.model.to(self.device)
                self.model.eval()
                self.saliency = Saliency(self.model)
                self.integrated_gradients = IntegratedGradients(self.model)
                self.torch_active = True
            except Exception:
                self.torch_active = False
        else:
            self.torch_active = False

    def compute_attribution(
        self,
        visual_obs: np.ndarray,
        velocity_obs: np.ndarray,
        target_action_idx: int = 0,
        mode: str = "saliency",
        n_steps: int = 30
    ) -> np.ndarray:
        """
        Computes 2D visual attribution intensity |A(x,y)| for input observation.
        Returns a normalized (84, 84) float32 array in range [0.0, 1.0].
        """
        if self.torch_active:
            vis_tensor = torch.tensor(visual_obs, dtype=torch.float32, device=self.device).unsqueeze(0)
            vel_tensor = torch.tensor(velocity_obs, dtype=torch.float32, device=self.device).unsqueeze(0)
            vis_tensor.requires_grad = True

            inputs = (vis_tensor, vel_tensor)

            if mode.lower() == "saliency":
                attributions = self.saliency.attribute(inputs=inputs, target=target_action_idx, abs=True)
                vis_attr = attributions[0].squeeze(0).detach().cpu().numpy()
            elif mode.lower() in ["ig", "integrated_gradients"]:
                baselines = (torch.zeros_like(vis_tensor), torch.zeros_like(vel_tensor))
                attributions = self.integrated_gradients.attribute(
                    inputs=inputs, baselines=baselines, target=target_action_idx, n_steps=n_steps
                )
                vis_attr = np.abs(attributions[0].squeeze(0).detach().cpu().numpy())
            else:
                vis_attr = np.abs(visual_obs)

            # Max pool across feature channels (3 RGB + 2 Optical Flow)
            attr_2d = np.max(vis_attr, axis=0)
        else:
            # Fallback Attribution Engine for AppLocker restricted environments
            rgb_grad_x = np.abs(cv2.Sobel(visual_obs[0], cv2.CV_32F, 1, 0, ksize=3))
            rgb_grad_y = np.abs(cv2.Sobel(visual_obs[0], cv2.CV_32F, 0, 1, ksize=3))
            flow_mag = np.linalg.norm(visual_obs[3:5], axis=0)
            attr_2d = rgb_grad_x + rgb_grad_y + 1.5 * flow_mag

        # Normalize 2D attribution map to [0.0, 1.0]
        attr_min, attr_max = attr_2d.min(), attr_2d.max()
        if attr_max - attr_min > 1e-8:
            attr_2d = (attr_2d - attr_min) / (attr_max - attr_min)
        else:
            attr_2d = np.zeros_like(attr_2d)

        return attr_2d

    @staticmethod
    def generate_heatmap_overlay(
        rgb_frame: np.ndarray,
        attr_2d: np.ndarray,
        target_size: tuple = (390, 390),
        alpha_max: float = 0.75,
        alpha: float = None
    ) -> np.ndarray:
        """
        Blends a high-definition 2D visual attribution thermal heatmap onto the RGB camera frame.
        Applies:
          - Bicubic super-resolution upscaling to target_size
          - Gaussian spatial smoothing to eliminate blockiness
          - Non-linear gamma contrast boost for vivid heat focus
          - Google TURBO scientific colormap (super vivid thermal spectrum)
          - Adaptive alpha masking (transparent in low-saliency areas, glowing hot on obstacles)
          - Contour highlight lines around peak heat zones
        """
        target_w, target_h = target_size

        # 1. Upscale base RGB image to HD with smooth interpolation & subtle sharpening
        hd_rgb = cv2.resize(rgb_frame, (target_w, target_h), interpolation=cv2.INTER_CUBIC)
        hd_bgr = cv2.cvtColor(hd_rgb, cv2.COLOR_RGB2BGR)

        # 2. Upscale Saliency 2D map to HD with bicubic interpolation
        hd_attr = cv2.resize(attr_2d.astype(np.float32), (target_w, target_h), interpolation=cv2.INTER_CUBIC)

        # 3. Apply Gaussian spatial smoothing for continuous thermal energy gradients
        hd_attr_smooth = cv2.GaussianBlur(hd_attr, (13, 13), 3.0)

        # Renormalize post-smoothing
        a_min, a_max = hd_attr_smooth.min(), hd_attr_smooth.max()
        if a_max - a_min > 1e-6:
            hd_attr_smooth = (hd_attr_smooth - a_min) / (a_max - a_min)
        else:
            hd_attr_smooth = np.zeros_like(hd_attr_smooth)

        # 4. Gamma contrast boost (gamma=0.7 makes subtle features pop out vividly)
        hd_attr_boosted = np.power(hd_attr_smooth, 0.7)

        # 5. Apply Google TURBO scientific thermal colormap
        heatmap_uint8 = (hd_attr_boosted * 255.0).astype(np.uint8)
        color_heatmap = cv2.applyColorMap(heatmap_uint8, cv2.COLORMAP_TURBO)

        # 6. Adaptive Alpha Masking: alpha scales with saliency intensity
        # Low saliency (<0.15) -> near 0 alpha (clear vision of room)
        # High saliency (>0.6)  -> high alpha (vivid thermal glow)
        alpha_map = np.clip((hd_attr_boosted - 0.1) / 0.85, 0.0, 1.0) * alpha_max
        alpha_3ch = np.stack([alpha_map] * 3, axis=-1)

        # Blend base frame with thermal heatmap using per-pixel alpha
        overlay_f = hd_bgr.astype(np.float32) * (1.0 - alpha_3ch) + color_heatmap.astype(np.float32) * alpha_3ch
        overlay = np.clip(overlay_f, 0, 255).astype(np.uint8)

        # 7. Draw Peak Heat Contour Lines (Neon Cyan / Gold rings on top 12% saliency)
        peak_mask = (hd_attr_boosted > 0.65).astype(np.uint8) * 255
        contours, _ = cv2.findContours(peak_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        cv2.drawContours(overlay, contours, -1, (255, 255, 0), 1, cv2.LINE_AA)

        return overlay

    @staticmethod
    def compute_explanation_fidelity(
        attr_2d: np.ndarray,
        depth_map: np.ndarray,
        dist_threshold: float = 1.5,
        percentile_threshold: float = 85.0
    ) -> float:
        """Computes Spatial IoU Explanation Fidelity Metric."""
        thresh_val = np.percentile(attr_2d, percentile_threshold)
        binary_attr = (attr_2d >= thresh_val).astype(np.uint8)
        binary_obstacle = (depth_map < dist_threshold).astype(np.uint8)

        intersection = np.logical_and(binary_attr, binary_obstacle).sum()
        union = np.logical_or(binary_attr, binary_obstacle).sum()

        if union == 0:
            return 1.0 if intersection == 0 else 0.0

        spatial_iou = float(intersection / (union + 1e-6))
        return spatial_iou
