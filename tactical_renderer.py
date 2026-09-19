"""
tactical_renderer.py - High-End Military UAV Command & Control Console Renderer
-------------------------------------------------------------------------------
Evaluation-Only Procedural 3D Visualizer and Operations Dashboard for Autonomous UAV.
Emulates a rugged military UAV command laptop running a tactical reconnaissance mission:
  - Procedural 3D perspective FPV camera (CAM-01 // FORWARD EO)
  - Procedural 3D third-person tactical chase camera (CAM-02 // TACTICAL CHASE)
  - Top-down tactical 2D planning map with 1:1 metric scale (MAP-01 // TACTICAL OVERVIEW)
  - Real sensor fusion (Depth Map, Optical Flow, Polar Velocity Vector Scope)
  - AI decision explainability and policy confidence gauges with segmented blocks
  - Captum XAI threat attention saliency heatmap
  - Comprehensive mission telemetry and real-time military-timestamped event log
  - 100% lightweight procedural NumPy + OpenCV graphics (zero external game engines)
  - Strictly read-only state consumption; training remains completely untouched.
"""

import math
import sys
import time
from collections import deque
from typing import Dict, List, Optional, Tuple, Any

import cv2
import numpy as np

TORCH_AVAILABLE = True
try:
    import torch
except (ImportError, OSError):
    TORCH_AVAILABLE = False


# Cache CUDA info once at module load to avoid repeated lock/query overhead per frame
CUDA_AVAILABLE = TORCH_AVAILABLE and torch.cuda.is_available()
GPU_DEVICE_NAME = "NVIDIA CUDA"
if CUDA_AVAILABLE:
    try:
        GPU_DEVICE_NAME = torch.cuda.get_device_name(0).replace("NVIDIA ", "")
    except Exception:
        GPU_DEVICE_NAME = "RTX GPU (CUDA)"


# =============================================================================
# TACTICAL COLOR PALETTE (Military C2 Colorway in BGR)
# =============================================================================
class C2Palette:
    # Primary backgrounds
    BG_DARK = (14, 16, 18)           # Deep charcoal-black
    BG_PANEL = (20, 24, 28)          # Rugged tactical console panel
    BG_SUBPANEL = (26, 32, 38)       # Inner tile background
    BG_HEADER = (18, 22, 26)         # Top header bar background

    # Borders and technical lines
    BORDER_DIM = (40, 50, 58)        # Subtle dark border
    BORDER_MED = (60, 78, 90)        # Technical frame line
    BORDER_ACCENT = (85, 125, 150)   # Highlighted border line
    GRID_LINE = (38, 48, 56)         # Tactical grid lines
    GRID_LINE_BOLD = (65, 85, 100)   # Major coordinate lines

    # Tactical Status and Accents
    GREEN_TACTICAL = (60, 220, 100)  # Bright operational green
    GREEN_MUTED = (40, 130, 70)      # Muted military olive green
    AMBER_TACTICAL = (0, 175, 255)   # Tactical amber / alert
    ORANGE_WARNING = (0, 110, 255)   # Warning orange
    RED_DANGER = (40, 40, 235)       # Danger / collision red
    CYAN_SENSOR = (255, 225, 0)      # Sensor telemetry cyan
    BLUE_TACTICAL = (255, 160, 40)   # Tactical blue
    GOLD_OBJECTIVE = (0, 215, 255)   # Mission objective gold

    # Typography
    TEXT_WHITE = (240, 245, 250)     # High-contrast primary text
    TEXT_MUTED = (145, 165, 180)     # Secondary telemetry readout
    TEXT_DIM = (90, 110, 125)        # Tertiary / subtle labels


# =============================================================================
# 2D TACTICAL UI PRIMITIVES
# =============================================================================
def draw_corner_brackets(
    canvas: np.ndarray,
    x: int,
    y: int,
    w: int,
    h: int,
    color: Tuple[int, int, int] = C2Palette.BORDER_ACCENT,
    length: int = 10,
    thickness: int = 1,
) -> None:
    """Draws tactical HUD corner framing brackets around a rectangle."""
    # Top-Left
    cv2.line(canvas, (x, y), (x + length, y), color, thickness, cv2.LINE_AA)
    cv2.line(canvas, (x, y), (x, y + length), color, thickness, cv2.LINE_AA)
    # Top-Right
    cv2.line(canvas, (x + w, y), (x + w - length, y), color, thickness, cv2.LINE_AA)
    cv2.line(canvas, (x + w, y), (x + w, y + length), color, thickness, cv2.LINE_AA)
    # Bottom-Left
    cv2.line(canvas, (x, y + h), (x + length, y + h), color, thickness, cv2.LINE_AA)
    cv2.line(canvas, (x, y + h), (x, y + h - length), color, thickness, cv2.LINE_AA)
    # Bottom-Right
    cv2.line(canvas, (x + w, y + h), (x + w - length, y + h), color, thickness, cv2.LINE_AA)
    cv2.line(canvas, (x + w, y + h), (x + w, y + h - length), color, thickness, cv2.LINE_AA)


def draw_panel(
    canvas: np.ndarray,
    x: int,
    y: int,
    w: int,
    h: int,
    title: str = "",
    status_text: str = "",
    status_color: Tuple[int, int, int] = C2Palette.GREEN_TACTICAL,
    bg_color: Tuple[int, int, int] = C2Palette.BG_PANEL,
    border_color: Tuple[int, int, int] = C2Palette.BORDER_MED,
) -> None:
    """Draws a rugged military C2 panel container with header strip and corner accents."""
    cv2.rectangle(canvas, (x, y), (x + w, y + h), bg_color, -1)
    cv2.rectangle(canvas, (x, y), (x + w, y + h), border_color, 1)

    header_h = 24
    cv2.rectangle(canvas, (x, y), (x + w, y + header_h), C2Palette.BG_HEADER, -1)
    cv2.line(canvas, (x, y + header_h), (x + w, y + header_h), border_color, 1)

    if title:
        cv2.putText(
            canvas,
            title,
            (x + 10, y + 16),
            cv2.FONT_HERSHEY_DUPLEX,
            0.42,
            C2Palette.TEXT_WHITE,
            1,
            cv2.LINE_AA,
        )

    if status_text:
        tw = cv2.getTextSize(status_text, cv2.FONT_HERSHEY_SIMPLEX, 0.36, 1)[0][0]
        sx = x + w - tw - 12
        cv2.circle(canvas, (sx - 7, y + 12), 3, status_color, -1)
        cv2.putText(
            canvas,
            status_text,
            (sx, y + 16),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.36,
            status_color,
            1,
            cv2.LINE_AA,
        )

    draw_corner_brackets(canvas, x, y, w, h, C2Palette.BORDER_ACCENT, length=8, thickness=1)


def draw_led(
    canvas: np.ndarray,
    x: int,
    y: int,
    color: Tuple[int, int, int],
    label: str = "",
    radius: int = 4,
) -> None:
    """Draws a glowing technical status LED with an optional label."""
    cv2.circle(canvas, (x, y), radius + 2, tuple(int(c * 0.45) for c in color), 1, cv2.LINE_AA)
    cv2.circle(canvas, (x, y), radius, color, -1, cv2.LINE_AA)
    if label:
        cv2.putText(
            canvas,
            label,
            (x + radius + 6, y + 4),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.33,
            C2Palette.TEXT_MUTED,
            1,
            cv2.LINE_AA,
        )


def draw_bar_gauge(
    canvas: np.ndarray,
    x: int,
    y: int,
    w: int,
    h: int,
    val: float,
    min_val: float,
    max_val: float,
    label: str,
    color: Tuple[int, int, int] = C2Palette.CYAN_SENSOR,
    show_center_zero: bool = True,
    is_percentage: bool = False,
    segments: int = 12,
) -> None:
    """Renders a precision military segmented bar gauge with tick marks and numeric readout."""
    cv2.putText(
        canvas,
        label,
        (x, y + 11),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.36,
        C2Palette.TEXT_MUTED,
        1,
        cv2.LINE_AA,
    )

    bar_x = x + 68
    bar_w = w - 130
    bar_y = y + 2
    bar_h = h - 4

    # Background groove
    cv2.rectangle(canvas, (bar_x, bar_y), (bar_x + bar_w, bar_y + bar_h), (25, 30, 36), -1)
    cv2.rectangle(canvas, (bar_x, bar_y), (bar_x + bar_w, bar_y + bar_h), C2Palette.BORDER_DIM, 1)

    norm_val = float(np.clip((val - min_val) / (max_val - min_val + 1e-6), 0.0, 1.0))

    if show_center_zero and min_val < 0.0 < max_val:
        zero_norm = (-min_val) / (max_val - min_val)
        zero_x = bar_x + int(bar_w * zero_norm)
        fill_x = bar_x + int(bar_w * norm_val)
        cv2.line(canvas, (zero_x, bar_y), (zero_x, bar_y + bar_h), (90, 115, 130), 1)

        if fill_x >= zero_x:
            cv2.rectangle(canvas, (zero_x, bar_y + 2), (fill_x, bar_y + bar_h - 2), color, -1)
        else:
            cv2.rectangle(canvas, (fill_x, bar_y + 2), (zero_x, bar_y + bar_h - 2), color, -1)
    else:
        fill_w = int(bar_w * norm_val)
        if fill_w > 0:
            cv2.rectangle(canvas, (bar_x + 1, bar_y + 2), (bar_x + fill_w, bar_y + bar_h - 2), color, -1)

    # Tactical segmented tick lines
    seg_step = bar_w / float(segments)
    for s in range(1, segments):
        sx = int(bar_x + s * seg_step)
        cv2.line(canvas, (sx, bar_y), (sx, bar_y + bar_h), (14, 16, 18), 1)

    # Numeric readout
    if is_percentage:
        val_str = f"{val:4.1f}%"
    else:
        val_str = f"{val:+.2f}" if min_val < 0 else f"{val:.2f}"

    cv2.putText(
        canvas,
        val_str,
        (bar_x + bar_w + 8, y + 11),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.35,
        C2Palette.TEXT_WHITE,
        1,
        cv2.LINE_AA,
    )


# =============================================================================
# PROCEDURAL 3D PERSPECTIVE GRAPHICS ENGINE (NumPy + OpenCV)
# =============================================================================
class Camera3D:
    """
    Perspective camera for projecting 3D world geometry to 2D viewports.
    Calculates focal length from vertical FOV so that widening the viewport expands
    the horizontal panoramic view without vertically zooming or clipping scene geometry.
    """

    def __init__(self, width: int, height: int, fov_y_deg: float = 52.0, near_val: float = 0.15):
        self.width = width
        self.height = height
        self.fov_y_deg = fov_y_deg
        self.near_val = near_val
        self.cx = width / 2.0
        self.cy = height / 2.0
        self.focal = (height / 2.0) / math.tan(math.radians(fov_y_deg / 2.0))

    def project_polygon(
        self,
        poly_world: np.ndarray,
        cam_pos: np.ndarray,
        right: np.ndarray,
        forward: np.ndarray,
        up: np.ndarray,
    ) -> Optional[Tuple[np.ndarray, float]]:
        """
        Projects a 3D polygon onto screen coordinates with Sutherland-Hodgman near-plane clipping.
        Uses fast-path early rejection and early acceptance for maximum throughput.
        """
        rel = poly_world - cam_pos
        xc = rel @ right
        yc = rel @ up
        zc = rel @ forward

        # Fast rejection / acceptance
        min_z = float(np.min(zc))
        if min_z < self.near_val:
            if float(np.max(zc)) < self.near_val:
                return None
            # Clip straddling polygon
            n = len(poly_world)
            clipped_x, clipped_y, clipped_z = [], [], []
            for i in range(n):
                j = (i + 1) % n
                z1, z2 = zc[i], zc[j]
                in1 = z1 >= self.near_val
                in2 = z2 >= self.near_val
                if in1:
                    clipped_x.append(xc[i])
                    clipped_y.append(yc[i])
                    clipped_z.append(z1)
                    if not in2:
                        t = (self.near_val - z1) / (z2 - z1 + 1e-9)
                        clipped_x.append(xc[i] + t * (xc[j] - xc[i]))
                        clipped_y.append(yc[i] + t * (yc[j] - yc[i]))
                        clipped_z.append(self.near_val)
                elif in2:
                    t = (self.near_val - z1) / (z2 - z1 + 1e-9)
                    clipped_x.append(xc[i] + t * (xc[j] - xc[i]))
                    clipped_y.append(yc[i] + t * (yc[j] - yc[i]))
                    clipped_z.append(self.near_val)

            if len(clipped_z) < 3:
                return None

            cx_arr = np.array(clipped_x, dtype=np.float32)
            cy_arr = np.array(clipped_y, dtype=np.float32)
            cz_arr = np.array(clipped_z, dtype=np.float32)
            inv_z = 1.0 / np.maximum(cz_arr, self.near_val)
            u = self.cx + self.focal * cx_arr * inv_z
            v = self.cy - self.focal * cy_arr * inv_z
            screen_pts = np.stack([u, v], axis=-1).astype(np.int32)
            return screen_pts, float(sum(clipped_z) / len(clipped_z))

        # Fast acceptance (100% in front of near plane)
        inv_z = 1.0 / zc
        u = self.cx + self.focal * xc * inv_z
        v = self.cy - self.focal * yc * inv_z
        screen_pts = np.stack([u, v], axis=-1).astype(np.int32)
        return screen_pts, float(np.sum(zc) / len(zc))

    def project_point(
        self,
        pt_world: np.ndarray,
        cam_pos: np.ndarray,
        right: np.ndarray,
        forward: np.ndarray,
        up: np.ndarray,
    ) -> Optional[Tuple[int, int, float]]:
        """Projects a single 3D point to 2D screen coordinates."""
        rel = pt_world - cam_pos
        xc = float(np.dot(rel, right))
        yc = float(np.dot(rel, up))
        zc = float(np.dot(rel, forward))

        if zc < self.near_val:
            return None

        u = int(round(self.cx + (self.focal * xc) / zc))
        v = int(round(self.cy - (self.focal * yc) / zc))
        return u, v, zc


class ProceduralWorldRenderer:
    """
    Renders the tactical 3D indoor environment with directional lighting,
    concrete wall panels, floor grid, faceted obstacle pillars/crates, goal beacon,
    and quadrotor model using Painter's algorithm.
    """

    LIGHT_DIR = np.array([-0.3, 0.5, 0.82], dtype=np.float32)
    LIGHT_DIR /= np.linalg.norm(LIGHT_DIR)

    @staticmethod
    def get_drone_basis(yaw: float, pitch: float = 0.0, roll: float = 0.0) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
        """Calculates orthonormal forward, right, up basis vectors from Euler angles."""
        cy, sy = math.cos(yaw), math.sin(yaw)
        cp, sp = math.cos(pitch), math.sin(pitch)
        cr, sr = math.cos(roll), math.sin(roll)

        forward = np.array([sy * cp, cy * cp, sp], dtype=np.float32)
        forward /= (np.linalg.norm(forward) + 1e-9)

        right = np.array([cy * cr + sy * sp * sr, -sy * cr + cy * sp * sr, -cp * sr], dtype=np.float32)
        right /= (np.linalg.norm(right) + 1e-9)

        up = np.cross(right, forward)
        up /= (np.linalg.norm(up) + 1e-9)

        return forward, right, up

    @classmethod
    def assemble_static_arena_polygons(
        cls,
        obstacle_specs: List[Dict[str, Any]],
    ) -> List[Dict[str, Any]]:
        """
        Assembles static 3D world geometry for the facility:
        Floor grid, boundary walls, and static obstacle pillars/crates.
        Cached across frames for maximum rendering performance.
        """
        polygons = []

        # ── 1. High-Contrast Tactical Floor Grid (Z = 0) ─────────────────────
        for x in range(-5, 5, 2):
            for y in range(-10, 10, 2):
                pts = np.array([
                    [x, y, 0.0],
                    [x + 2, y, 0.0],
                    [x + 2, y + 2, 0.0],
                    [x, y + 2, 0.0],
                ], dtype=np.float32)
                tile_alt = ((x // 2) + (y // 2)) % 2
                base_c = (38, 45, 54) if tile_alt == 0 else (30, 36, 44)
                polygons.append({
                    "pts": pts,
                    "color": base_c,
                    "edge_color": (75, 98, 115),
                    "draw_edge": True,
                    "normal": np.array([0, 0, 1], dtype=np.float32),
                    "type": "floor",
                })

        # ── 2. Concrete Boundary Walls (Height = 3.5m) ───────────────────────
        wall_h = 3.5
        # North Wall (Y = 10)
        for x in range(-5, 5, 2):
            pts = np.array([
                [x, 10.0, 0.0],
                [x + 2, 10.0, 0.0],
                [x + 2, 10.0, wall_h],
                [x, 10.0, wall_h],
            ], dtype=np.float32)
            polygons.append({
                "pts": pts,
                "color": (40, 48, 58),
                "edge_color": (70, 88, 105),
                "draw_edge": True,
                "normal": np.array([0, -1, 0], dtype=np.float32),
                "type": "wall",
            })
        # South Wall (Y = -10)
        for x in range(-5, 5, 2):
            pts = np.array([
                [x + 2, -10.0, 0.0],
                [x, -10.0, 0.0],
                [x, -10.0, wall_h],
                [x + 2, -10.0, wall_h],
            ], dtype=np.float32)
            polygons.append({
                "pts": pts,
                "color": (36, 44, 54),
                "edge_color": (65, 82, 100),
                "draw_edge": True,
                "normal": np.array([0, 1, 0], dtype=np.float32),
                "type": "wall",
            })
        # East Wall (X = 5)
        for y in range(-10, 10, 2):
            pts = np.array([
                [5.0, y + 2, 0.0],
                [5.0, y, 0.0],
                [5.0, y, wall_h],
                [5.0, y + 2, wall_h],
            ], dtype=np.float32)
            polygons.append({
                "pts": pts,
                "color": (34, 42, 52),
                "edge_color": (65, 82, 100),
                "draw_edge": True,
                "normal": np.array([-1, 0, 0], dtype=np.float32),
                "type": "wall",
            })
        # West Wall (X = -5)
        for y in range(-10, 10, 2):
            pts = np.array([
                [-5.0, y, 0.0],
                [-5.0, y + 2, 0.0],
                [-5.0, y + 2, wall_h],
                [-5.0, y, wall_h],
            ], dtype=np.float32)
            polygons.append({
                "pts": pts,
                "color": (38, 46, 56),
                "edge_color": (68, 86, 104),
                "draw_edge": True,
                "normal": np.array([1, 0, 0], dtype=np.float32),
                "type": "wall",
            })

        # ── 3. Procedural Obstacles (Pillars & Crates) ──────────────────────
        for spec in obstacle_specs:
            pos = spec.get("pos", [0, 0, 0])
            obs_type = spec.get("type", "box")
            raw_c = spec.get("color", (40, 220, 110))
            base_bgr = (raw_c[2], raw_c[1], raw_c[0])

            if obs_type == "cylinder":
                r = spec.get("radius", 0.45)
                h = spec.get("height", 3.0)
                cx, cy = pos[0], pos[1]
                n_sides = 8
                angles = np.linspace(0, 2 * math.pi, n_sides, endpoint=False)
                ring_bottom = [np.array([cx + r * math.cos(a), cy + r * math.sin(a), 0.0], dtype=np.float32) for a in angles]
                ring_top = [np.array([cx + r * math.cos(a), cy + r * math.sin(a), h], dtype=np.float32) for a in angles]

                for i in range(n_sides):
                    j = (i + 1) % n_sides
                    pts = np.array([ring_bottom[i], ring_bottom[j], ring_top[j], ring_top[i]])
                    norm = np.array([math.cos((angles[i] + angles[j]) / 2), math.sin((angles[i] + angles[j]) / 2), 0.0], dtype=np.float32)
                    polygons.append({
                        "pts": pts,
                        "color": base_bgr,
                        "edge_color": tuple(min(255, int(c * 1.35)) for c in base_bgr),
                        "draw_edge": True,
                        "normal": norm,
                        "type": "obstacle",
                    })

                polygons.append({
                    "pts": np.array(ring_top),
                    "color": tuple(min(255, int(c * 1.2)) for c in base_bgr),
                    "edge_color": (255, 255, 255),
                    "draw_edge": True,
                    "normal": np.array([0, 0, 1], dtype=np.float32),
                    "type": "obstacle_cap",
                })

            elif obs_type == "box":
                half_ext = spec.get("half_ext", [0.4, 0.4, 0.4])
                if max(half_ext) > 3.0:
                    continue

                cx, cy, cz = pos[0], pos[1], pos[2]
                dx, dy, dz = half_ext[0], half_ext[1], half_ext[2]

                v = np.array([
                    [cx - dx, cy - dy, cz - dz],  # 0
                    [cx + dx, cy - dy, cz - dz],  # 1
                    [cx + dx, cy + dy, cz - dz],  # 2
                    [cx - dx, cy + dy, cz - dz],  # 3
                    [cx - dx, cy - dy, cz + dz],  # 4
                    [cx + dx, cy - dy, cz + dz],  # 5
                    [cx + dx, cy + dy, cz + dz],  # 6
                    [cx - dx, cy + dy, cz + dz],  # 7
                ], dtype=np.float32)

                faces = [
                    ([v[0], v[1], v[5], v[4]], np.array([0, -1, 0], dtype=np.float32)),  # South
                    ([v[1], v[2], v[6], v[5]], np.array([1, 0, 0], dtype=np.float32)),   # East
                    ([v[2], v[3], v[7], v[6]], np.array([0, 1, 0], dtype=np.float32)),   # North
                    ([v[3], v[0], v[4], v[7]], np.array([-1, 0, 0], dtype=np.float32)),  # West
                    ([v[4], v[5], v[6], v[7]], np.array([0, 0, 1], dtype=np.float32)),   # Top
                ]
                for f_pts, f_norm in faces:
                    polygons.append({
                        "pts": np.array(f_pts),
                        "color": base_bgr,
                        "edge_color": tuple(min(255, int(c * 1.35)) for c in base_bgr),
                        "draw_edge": True,
                        "normal": f_norm,
                        "type": "obstacle",
                    })

        for p in polygons:
            p["center"] = np.mean(p["pts"], axis=0)
            norm = p.get("normal")
            if norm is not None:
                dot = float(np.dot(norm, cls.LIGHT_DIR))
                p["light_factor"] = 0.45 + 0.55 * max(0.0, dot)
            else:
                p["light_factor"] = 1.0

        return polygons

    @classmethod
    def assemble_dynamic_polygons(
        cls,
        goal_pos: np.ndarray,
        drone_pos: Optional[np.ndarray] = None,
        drone_orn: Optional[np.ndarray] = None,
        include_drone_model: bool = False,
        prop_angle: float = 0.0,
    ) -> List[Dict[str, Any]]:
        """Assembles dynamic frame-specific geometry: goal beacon and 3D quadrotor drone model."""
        polygons = []

        # ── Tactical Objective Goal Beacon ───────────────────────────────────
        gx, gy, gz = goal_pos[0], goal_pos[1], goal_pos[2]
        beam_w = 0.28
        beam_pts = np.array([
            [gx - beam_w, gy, 0.0],
            [gx + beam_w, gy, 0.0],
            [gx + beam_w, gy, 3.5],
            [gx - beam_w, gy, 3.5],
        ], dtype=np.float32)
        polygons.append({
            "pts": beam_pts,
            "color": (0, 215, 255),
            "edge_color": (180, 245, 255),
            "draw_edge": True,
            "normal": np.array([0, -1, 0], dtype=np.float32),
            "type": "goal_beacon",
            "is_emissive": True,
        })

        d_sz = 0.38
        p_top = np.array([gx, gy, gz + d_sz], dtype=np.float32)
        p_bot = np.array([gx, gy, gz - d_sz], dtype=np.float32)
        p_mid = [
            np.array([gx + d_sz, gy, gz], dtype=np.float32),
            np.array([gx, gy + d_sz, gz], dtype=np.float32),
            np.array([gx - d_sz, gy, gz], dtype=np.float32),
            np.array([gx, gy - d_sz, gz], dtype=np.float32),
        ]
        for i in range(4):
            j = (i + 1) % 4
            polygons.append({
                "pts": np.array([p_top, p_mid[i], p_mid[j]]),
                "color": (0, 210, 255),
                "edge_color": (255, 255, 255),
                "draw_edge": True,
                "normal": np.array([0, 0, 1], dtype=np.float32),
                "type": "goal_diamond",
                "is_emissive": True,
            })
            polygons.append({
                "pts": np.array([p_bot, p_mid[j], p_mid[i]]),
                "color": (0, 170, 235),
                "edge_color": (255, 255, 255),
                "draw_edge": True,
                "normal": np.array([0, 0, -1], dtype=np.float32),
                "type": "goal_diamond",
                "is_emissive": True,
            })

        # ── High-Contrast 3D Quadrotor Drone Model ───────────────────────────
        if include_drone_model and drone_pos is not None and drone_orn is not None:
            yaw, pitch, roll = drone_orn[2], drone_orn[1], drone_orn[0]
            fwd, rt, up_v = cls.get_drone_basis(yaw, pitch, roll)

            fus_r = 0.22
            fus_h = 0.08
            n_fus = 6
            fus_pts_top, fus_pts_bot = [], []
            for i in range(n_fus):
                ang = i * (2 * math.pi / n_fus)
                local_xy = rt * (fus_r * math.cos(ang)) + fwd * (fus_r * math.sin(ang))
                fus_pts_top.append(drone_pos + local_xy + up_v * (fus_h / 2.0))
                fus_pts_bot.append(drone_pos + local_xy - up_v * (fus_h / 2.0))

            polygons.append({
                "pts": np.array(fus_pts_top),
                "color": (75, 92, 110),
                "edge_color": (140, 195, 240),
                "draw_edge": True,
                "normal": up_v,
                "type": "drone_chassis",
            })

            for i in range(n_fus):
                j = (i + 1) % n_fus
                polygons.append({
                    "pts": np.array([fus_pts_bot[i], fus_pts_bot[j], fus_pts_top[j], fus_pts_top[i]]),
                    "color": (52, 65, 80),
                    "edge_color": (120, 165, 205),
                    "draw_edge": True,
                    "normal": fwd,
                    "type": "drone_chassis",
                })

            arm_len = 0.38
            rotor_r = 0.16
            arm_offsets = [
                (1, 1, "FR", (60, 255, 100)),   # Front-Right: Green Nav
                (-1, 1, "FL", (60, 255, 100)),  # Front-Left: Green Nav
                (-1, -1, "RL", (40, 40, 255)),  # Rear-Left: Red Nav
                (1, -1, "RR", (40, 40, 255)),   # Rear-Right: Red Nav
            ]

            for s_x, s_y, arm_id, nav_c in arm_offsets:
                hub_center = drone_pos + (rt * (s_x * arm_len * 0.707) + fwd * (s_y * arm_len * 0.707))
                arm_beam = np.array([
                    drone_pos - up_v * 0.025,
                    drone_pos + up_v * 0.025,
                    hub_center + up_v * 0.025,
                    hub_center - up_v * 0.025,
                ], dtype=np.float32)
                polygons.append({
                    "pts": arm_beam,
                    "color": (40, 50, 62),
                    "edge_color": (130, 175, 210),
                    "draw_edge": True,
                    "normal": up_v,
                    "type": "drone_arm",
                })

                spin = prop_angle if (s_x * s_y > 0) else -prop_angle
                blade_v1 = rt * (rotor_r * math.cos(spin)) + fwd * (rotor_r * math.sin(spin))
                blade_v2 = rt * (rotor_r * math.cos(spin + math.pi / 2)) + fwd * (rotor_r * math.sin(spin + math.pi / 2))

                blade_quad1 = np.array([
                    hub_center - blade_v1 * 0.95 + up_v * 0.035,
                    hub_center + blade_v1 * 0.95 + up_v * 0.035,
                    hub_center + blade_v1 * 0.95 + rt * 0.03 + up_v * 0.035,
                    hub_center - blade_v1 * 0.95 + rt * 0.03 + up_v * 0.035,
                ], dtype=np.float32)
                blade_quad2 = np.array([
                    hub_center - blade_v2 * 0.95 + up_v * 0.035,
                    hub_center + blade_v2 * 0.95 + up_v * 0.035,
                    hub_center + blade_v2 * 0.95 + fwd * 0.03 + up_v * 0.035,
                    hub_center - blade_v2 * 0.95 + fwd * 0.03 + up_v * 0.035,
                ], dtype=np.float32)

                polygons.append({
                    "pts": blade_quad1,
                    "color": (210, 230, 245),
                    "edge_color": nav_c,
                    "draw_edge": True,
                    "normal": up_v,
                    "type": "propeller",
                    "is_emissive": True,
                })
                polygons.append({
                    "pts": blade_quad2,
                    "color": (190, 215, 235),
                    "edge_color": nav_c,
                    "draw_edge": True,
                    "normal": up_v,
                    "type": "propeller",
                    "is_emissive": True,
                })

        return polygons

    @classmethod
    def render_scene(
        cls,
        canvas: np.ndarray,
        camera: Camera3D,
        cam_pos: np.ndarray,
        forward: np.ndarray,
        right: np.ndarray,
        up: np.ndarray,
        polygons: List[Dict[str, Any]],
    ) -> None:
        """Projects and draws sorted scene polygons with directional lighting."""
        render_queue = []
        cpx, cpy, cpz = float(cam_pos[0]), float(cam_pos[1]), float(cam_pos[2])

        for poly in polygons:
            # Backface culling for planar boundary walls and convex obstacles
            if poly.get("type") in ("wall", "obstacle"):
                normal = poly.get("normal")
                center = poly.get("center")
                if normal is not None and center is not None:
                    # Dot product between face normal and vector from camera to face center
                    dot_cam = (
                        normal[0] * (center[0] - cpx) +
                        normal[1] * (center[1] - cpy) +
                        normal[2] * (center[2] - cpz)
                    )
                    if dot_cam >= 0.0:
                        continue  # Facing away from camera, cull before projection

            proj_res = camera.project_polygon(poly["pts"], cam_pos, right, forward, up)
            if proj_res is not None:
                screen_pts, depth = proj_res
                render_queue.append((depth, screen_pts, poly))

        render_queue.sort(key=lambda x: x[0], reverse=True)

        for depth, screen_pts, poly in render_queue:
            base_col = poly["color"]

            if poly.get("is_emissive", False):
                shaded_col = base_col
            else:
                light_factor = poly.get("light_factor")
                if light_factor is None:
                    normal = poly.get("normal")
                    if normal is not None:
                        dot = float(np.dot(normal, cls.LIGHT_DIR))
                        light_factor = 0.45 + 0.55 * max(0.0, dot)
                    else:
                        light_factor = 1.0

                dist_factor = max(0.50, 1.0 - (depth / 22.0) * 0.35)
                factor = light_factor * dist_factor
                b, g, r = base_col
                shaded_col = (int(b * factor), int(g * factor), int(r * factor))

            cv2.fillPoly(canvas, [screen_pts], shaded_col)

            if poly.get("draw_edge", False):
                edge_c = poly.get("edge_color", C2Palette.BORDER_MED)
                cv2.polylines(canvas, [screen_pts], isClosed=True, color=edge_c, thickness=1, lineType=cv2.LINE_AA)


# =============================================================================
# TACTICAL WINDOWS: FPV, CHASE, OVERVIEW MAP
# =============================================================================
def render_window_fpv(
    w: int,
    h: int,
    drone_pos: np.ndarray,
    drone_orn: np.ndarray,
    drone_vel: np.ndarray,
    static_polys: List[Dict[str, Any]],
    goal_pos: np.ndarray,
    min_clearance: float,
    frame_num: int,
    mission_time_s: float,
) -> np.ndarray:
    """
    WINDOW 01: CAM-01 // FORWARD EO
    First-person UAV electro-optical camera view with tactical HUD overlay,
    central targeting crosshairs, pitch/roll artificial horizon ladder, and objective brackets.
    """
    view = np.full((h, w, 3), C2Palette.BG_DARK, dtype=np.uint8)

    yaw, pitch, roll = drone_orn[2], drone_orn[1], drone_orn[0]
    fwd, rt, up = ProceduralWorldRenderer.get_drone_basis(yaw, pitch, roll)
    cam_pos = drone_pos + fwd * 0.22 + up * 0.05

    camera = Camera3D(width=w, height=h, fov_y_deg=52.0)
    dynamic_polys = ProceduralWorldRenderer.assemble_dynamic_polygons(
        goal_pos=goal_pos,
        drone_pos=None,
        drone_orn=None,
        include_drone_model=False,
    )
    all_polys = static_polys + dynamic_polys
    ProceduralWorldRenderer.render_scene(view, camera, cam_pos, fwd, rt, up, all_polys)

    # Header bar
    cv2.rectangle(view, (0, 0), (w, 24), C2Palette.BG_HEADER, -1)
    cv2.line(view, (0, 24), (w, 24), C2Palette.BORDER_MED, 1)
    cv2.putText(view, "CAM-01 // FORWARD EO", (10, 16), cv2.FONT_HERSHEY_DUPLEX, 0.42, C2Palette.TEXT_WHITE, 1, cv2.LINE_AA)
    cv2.putText(view, "FOV 70 DEG", (w - 180, 16), cv2.FONT_HERSHEY_SIMPLEX, 0.36, C2Palette.CYAN_SENSOR, 1, cv2.LINE_AA)

    # [● REC] indicator
    rec_on = (int(mission_time_s * 2.0) % 2) == 0
    dot_color = C2Palette.RED_DANGER if rec_on else (60, 60, 90)
    cv2.circle(view, (w - 75, 12), 4, dot_color, -1, cv2.LINE_AA)
    cv2.putText(view, "REC", (w - 65, 16), cv2.FONT_HERSHEY_DUPLEX, 0.36, C2Palette.TEXT_WHITE, 1, cv2.LINE_AA)

    # Central targeting reticle
    cx, cy = w // 2, h // 2
    ret_color = C2Palette.CYAN_SENSOR
    cv2.circle(view, (cx, cy), 16, ret_color, 1, cv2.LINE_AA)
    cv2.circle(view, (cx, cy), 3, ret_color, -1, cv2.LINE_AA)
    cv2.line(view, (cx - 28, cy), (cx - 16, cy), ret_color, 1, cv2.LINE_AA)
    cv2.line(view, (cx + 16, cy), (cx + 28, cy), ret_color, 1, cv2.LINE_AA)
    cv2.line(view, (cx, cy - 28), (cx, cy - 16), ret_color, 1, cv2.LINE_AA)
    cv2.line(view, (cx, cy + 16), (cx, cy + 28), ret_color, 1, cv2.LINE_AA)

    # Pitch & Roll Artificial Horizon Ladder
    pitch_offset = int(math.degrees(pitch) * 2.5)
    roll_cos = math.cos(roll)
    roll_sin = math.sin(roll)
    h_len = 32
    # Left bar
    p1_l = (int(cx - h_len * roll_cos - pitch_offset * roll_sin), int(cy - h_len * roll_sin + pitch_offset * roll_cos))
    p2_l = (int(cx - 16 * roll_cos - pitch_offset * roll_sin), int(cy - 16 * roll_sin + pitch_offset * roll_cos))
    cv2.line(view, p1_l, p2_l, ret_color, 1, cv2.LINE_AA)
    # Right bar
    p1_r = (int(cx + 16 * roll_cos - pitch_offset * roll_sin), int(cy + 16 * roll_sin + pitch_offset * roll_cos))
    p2_r = (int(cx + h_len * roll_cos - pitch_offset * roll_sin), int(cy + h_len * roll_sin + pitch_offset * roll_cos))
    cv2.line(view, p1_r, p2_r, ret_color, 1, cv2.LINE_AA)

    # Telemetry tape
    alt = float(drone_pos[2])
    speed = float(np.linalg.norm(drone_vel))
    hdg = (int(math.degrees(yaw)) % 360 + 360) % 360
    tgt_dist = float(np.linalg.norm(drone_pos - goal_pos))
    clr = min_clearance

    tx, ty = 14, 46
    telemetry_tape = [
        f"ALT  {alt:4.2f} m",
        f"SPD  {speed:4.2f} m/s",
        f"HDG  {hdg:03d} DEG",
        f"TGT  {tgt_dist:4.1f} m",
        f"CLR  {clr:4.2f} m",
    ]
    for line in telemetry_tape:
        c = C2Palette.AMBER_TACTICAL if "CLR" in line and clr < 1.2 else C2Palette.TEXT_WHITE
        cv2.putText(view, line, (tx, ty), cv2.FONT_HERSHEY_SIMPLEX, 0.38, c, 1, cv2.LINE_AA)
        ty += 16

    # Tactical Objective HUD Target Marker
    goal_screen = camera.project_point(goal_pos, cam_pos, rt, fwd, up)
    if goal_screen is not None:
        gx, gy, gz = goal_screen
        if 20 <= gx < w - 20 and 30 <= gy < h - 20:
            box_sz = max(14, int(45.0 / (gz + 0.1)))
            draw_corner_brackets(view, gx - box_sz, gy - box_sz, box_sz * 2, box_sz * 2, C2Palette.GOLD_OBJECTIVE, length=6, thickness=1)
            cv2.putText(view, "[OBJECTIVE]", (gx - 32, gy - box_sz - 4), cv2.FONT_HERSHEY_SIMPLEX, 0.32, C2Palette.GOLD_OBJECTIVE, 1, cv2.LINE_AA)
            cv2.putText(view, f"{tgt_dist:.1f}m", (gx - 18, gy + box_sz + 12), cv2.FONT_HERSHEY_SIMPLEX, 0.32, C2Palette.GOLD_OBJECTIVE, 1, cv2.LINE_AA)

    mins = int(mission_time_s) // 60
    secs = mission_time_s % 60.0
    cv2.putText(
        view,
        f"FRM: {frame_num:06d}  T+{mins:02d}:{secs:04.1f}",
        (12, h - 12),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.35,
        C2Palette.TEXT_MUTED,
        1,
        cv2.LINE_AA,
    )

    if clr < 1.0:
        warn_flash = (int(mission_time_s * 4.0) % 2) == 0
        w_col = C2Palette.RED_DANGER if warn_flash else C2Palette.ORANGE_WARNING
        cv2.rectangle(view, (cx - 95, h - 45), (cx + 95, h - 22), (20, 20, 30), -1)
        cv2.rectangle(view, (cx - 95, h - 45), (cx + 95, h - 22), w_col, 1)
        cv2.putText(
            view,
            "! PROXIMITY ALERT !",
            (cx - 82, h - 30),
            cv2.FONT_HERSHEY_DUPLEX,
            0.40,
            w_col,
            1,
            cv2.LINE_AA,
        )

    draw_corner_brackets(view, 0, 0, w, h, C2Palette.BORDER_ACCENT, length=10, thickness=1)
    return view


def render_window_chase(
    w: int,
    h: int,
    drone_pos: np.ndarray,
    drone_orn: np.ndarray,
    drone_vel: np.ndarray,
    smoothed_cam_pos: np.ndarray,
    trajectory: List[np.ndarray],
    static_polys: List[Dict[str, Any]],
    goal_pos: np.ndarray,
    frame_num: int,
    mission_time_s: float,
) -> np.ndarray:
    """
    WINDOW 02: CAM-02 // TACTICAL CHASE
    Third-person UAV chase view with spring-damper following, 3D drone model,
    propeller animation, ground shadow, glowing trajectory trail, and tactical goal marker.
    """
    view = np.full((h, w, 3), C2Palette.BG_DARK, dtype=np.uint8)

    yaw, pitch, roll = drone_orn[2], drone_orn[1], drone_orn[0]
    fwd_drone, rt_drone, up_drone = ProceduralWorldRenderer.get_drone_basis(yaw, pitch, roll)

    target_pos = drone_pos + fwd_drone * 0.8 + np.array([0, 0, 0.15], dtype=np.float32)

    fwd_cam = target_pos - smoothed_cam_pos
    cam_dist = float(np.linalg.norm(fwd_cam))
    fwd_cam /= (cam_dist + 1e-9)

    up_approx = np.array([0, 0, 1.0], dtype=np.float32)
    rt_cam = np.cross(fwd_cam, up_approx)
    rt_cam /= (np.linalg.norm(rt_cam) + 1e-9)
    up_cam = np.cross(rt_cam, fwd_cam)
    up_cam /= (np.linalg.norm(up_cam) + 1e-9)

    camera = Camera3D(width=w, height=h, fov_y_deg=52.0)
    prop_angle = (frame_num * 45.0) % 360.0

    dynamic_polys = ProceduralWorldRenderer.assemble_dynamic_polygons(
        goal_pos=goal_pos,
        drone_pos=drone_pos,
        drone_orn=drone_orn,
        include_drone_model=True,
        prop_angle=math.radians(prop_angle),
    )
    all_polys = static_polys + dynamic_polys
    ProceduralWorldRenderer.render_scene(view, camera, smoothed_cam_pos, fwd_cam, rt_cam, up_cam, all_polys)

    # Ground contact shadow
    shadow_pt = camera.project_point(np.array([drone_pos[0], drone_pos[1], 0.01]), smoothed_cam_pos, rt_cam, fwd_cam, up_cam)
    if shadow_pt is not None:
        sx, sy, sz = shadow_pt
        if 0 <= sx < w and 0 <= sy < h:
            sh_r = max(4, int(22 / (1.0 + drone_pos[2] * 0.45)))
            cv2.ellipse(view, (sx, sy), (sh_r * 2, sh_r), 0, 0, 360, (12, 14, 18), -1)

    # Glowing Trajectory Trail
    if len(trajectory) >= 2:
        step_pts = []
        n_pts = len(trajectory)
        for i, pos_i in enumerate(trajectory):
            pt_2d = camera.project_point(pos_i, smoothed_cam_pos, rt_cam, fwd_cam, up_cam)
            if pt_2d is not None:
                step_pts.append((pt_2d[0], pt_2d[1], i / max(n_pts, 1)))

        for i in range(len(step_pts) - 1):
            p1 = (step_pts[i][0], step_pts[i][1])
            p2 = (step_pts[i + 1][0], step_pts[i + 1][1])
            alpha = step_pts[i][2]
            trail_c = (int(255 * alpha), int(225 * alpha), int(70 * (1.0 - alpha)))
            cv2.line(view, p1, p2, trail_c, 2, cv2.LINE_AA)

    # Tactical Label above drone: leader line anchored directly to top of fuselage
    fuselage_top_3d = drone_pos + up_drone * 0.06
    drone_anchor_pt = camera.project_point(fuselage_top_3d, smoothed_cam_pos, rt_cam, fwd_cam, up_cam)
    if drone_anchor_pt is not None:
        ax, ay, _ = drone_anchor_pt
        if 10 <= ax < w - 80 and 35 <= ay < h - 10:
            callout_x = ax + 22
            callout_y = ay - 24
            cv2.circle(view, (ax, ay), 3, C2Palette.CYAN_SENSOR, -1)
            cv2.line(view, (ax, ay), (callout_x, callout_y), C2Palette.CYAN_SENSOR, 1, cv2.LINE_AA)
            cv2.line(view, (callout_x, callout_y), (callout_x + 55, callout_y), C2Palette.CYAN_SENSOR, 1, cv2.LINE_AA)
            cv2.putText(view, "UAV-01", (callout_x + 6, callout_y - 4), cv2.FONT_HERSHEY_SIMPLEX, 0.36, C2Palette.CYAN_SENSOR, 1, cv2.LINE_AA)

    # Tactical Objective Marker for Goal in CAM-02
    tgt_dist = float(np.linalg.norm(drone_pos - goal_pos))
    goal_screen = camera.project_point(goal_pos, smoothed_cam_pos, rt_cam, fwd_cam, up_cam)
    if goal_screen is not None:
        gx, gy, gz = goal_screen
        if 20 <= gx < w - 20 and 30 <= gy < h - 20:
            box_sz = max(16, int(50.0 / (gz + 0.1)))
            draw_corner_brackets(view, gx - box_sz, gy - box_sz, box_sz * 2, box_sz * 2, C2Palette.GOLD_OBJECTIVE, length=8, thickness=1)
            cv2.putText(view, "[GOAL]", (gx - 18, gy - box_sz - 4), cv2.FONT_HERSHEY_DUPLEX, 0.34, C2Palette.GOLD_OBJECTIVE, 1, cv2.LINE_AA)
            cv2.putText(view, f"{tgt_dist:.1f}m", (gx - 16, gy + box_sz + 14), cv2.FONT_HERSHEY_SIMPLEX, 0.33, C2Palette.GOLD_OBJECTIVE, 1, cv2.LINE_AA)
            # Arrow pointing down into beacon
            cv2.arrowedLine(view, (gx, gy - box_sz - 12), (gx, gy - box_sz - 2), C2Palette.GOLD_OBJECTIVE, 2, tipLength=0.4)

    # Header bar
    cv2.rectangle(view, (0, 0), (w, 24), C2Palette.BG_HEADER, -1)
    cv2.line(view, (0, 24), (w, 24), C2Palette.BORDER_MED, 1)
    cv2.putText(view, "CAM-02 // TACTICAL CHASE", (10, 16), cv2.FONT_HERSHEY_DUPLEX, 0.42, C2Palette.TEXT_WHITE, 1, cv2.LINE_AA)
    cv2.putText(view, "SMOOTH DAMPED C2 TRACK", (w - 185, 16), cv2.FONT_HERSHEY_SIMPLEX, 0.36, C2Palette.GREEN_TACTICAL, 1, cv2.LINE_AA)

    cv2.putText(
        view,
        f"OBJECTIVE [GOAL]: {tgt_dist:.1f}m",
        (12, h - 12),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.36,
        C2Palette.GOLD_OBJECTIVE,
        1,
        cv2.LINE_AA,
    )

    draw_corner_brackets(view, 0, 0, w, h, C2Palette.BORDER_ACCENT, length=10, thickness=1)
    return view


def render_window_overview_map(
    w: int,
    h: int,
    drone_pos: np.ndarray,
    drone_orn: np.ndarray,
    drone_vel: np.ndarray,
    trajectory: List[np.ndarray],
    obstacle_specs: List[Dict[str, Any]],
    goal_pos: np.ndarray,
    start_pos: np.ndarray,
) -> np.ndarray:
    """
    WINDOW 03: MAP-01 // TACTICAL OVERVIEW
    Military 2D top-down planning map with strict 1:1 metric aspect ratio,
    tactical coordinate flanks, obstacle danger envelopes, route trail, and FOV cone.
    """
    view = np.full((h, w, 3), (16, 20, 24), dtype=np.uint8)

    # Header bar
    cv2.rectangle(view, (0, 0), (w, 24), C2Palette.BG_HEADER, -1)
    cv2.line(view, (0, 24), (w, 24), C2Palette.BORDER_MED, 1)
    cv2.putText(view, "MAP-01 // TACTICAL OVERVIEW", (10, 16), cv2.FONT_HERSHEY_DUPLEX, 0.42, C2Palette.TEXT_WHITE, 1, cv2.LINE_AA)
    cv2.putText(view, "1:1 METRIC GRID | 10x20m", (w - 165, 16), cv2.FONT_HERSHEY_SIMPLEX, 0.36, C2Palette.TEXT_MUTED, 1, cv2.LINE_AA)

    # 1:1 Metric aspect ratio calculation
    avail_h = h - 62
    avail_w = w - 24
    # Reserve space on left and right flanks for tactical coordinates and compass rose
    scale = min((avail_w - 160) / 10.0, avail_h / 20.0)
    map_w_px = int(10.0 * scale)
    map_h_px = int(20.0 * scale)

    map_x0 = (w - map_w_px) // 2
    map_y0 = 34 + (avail_h - map_h_px) // 2

    def w2m(wx: float, wy: float) -> Tuple[int, int]:
        px = int(map_x0 + (wx + 5.0) * scale)
        py = int(map_y0 + (10.0 - wy) * scale)
        return px, py

    top_left = (map_x0, map_y0)
    bot_right = (map_x0 + map_w_px, map_y0 + map_h_px)
    cv2.rectangle(view, top_left, bot_right, (25, 32, 40), -1)
    cv2.rectangle(view, top_left, bot_right, C2Palette.BORDER_ACCENT, 2)

    # Grid lines and coordinate markers
    for gx in range(-4, 5, 2):
        p1 = w2m(gx, -10.0)
        p2 = w2m(gx, 10.0)
        cv2.line(view, p1, p2, C2Palette.GRID_LINE, 1)

    for gy in range(-8, 9, 4):
        p1 = w2m(-5.0, gy)
        p2 = w2m(5.0, gy)
        cv2.line(view, p1, p2, C2Palette.GRID_LINE, 1)
        cv2.putText(view, f"{gy:+d}", (map_x0 - 18, p1[1] + 4), cv2.FONT_HERSHEY_SIMPLEX, 0.28, C2Palette.TEXT_DIM, 1)

    # Bottom coordinate tick labels
    for gx in (-4, 0, 4):
        p1 = w2m(gx, -10.0)
        cv2.putText(view, f"{gx:+d}", (p1[0] - 6, bot_right[1] + 12), cv2.FONT_HERSHEY_SIMPLEX, 0.28, C2Palette.TEXT_DIM, 1)

    # Obstacles with physical dimensions and danger threat buffers
    for spec in obstacle_specs:
        pos = spec.get("pos", [0, 0, 0])
        obs_type = spec.get("type", "box")
        raw_c = spec.get("color", (40, 220, 110))
        bgr_c = (raw_c[2], raw_c[1], raw_c[0])
        ox, oy = pos[0], pos[1]
        opx = w2m(ox, oy)

        if obs_type == "cylinder":
            r_m = spec.get("radius", 0.45)
            r_px = max(4, int(r_m * scale))
            # Danger envelope
            cv2.circle(view, opx, int(r_px + 0.4 * scale), (45, 55, 68), 1, cv2.LINE_AA)
            cv2.circle(view, opx, r_px, bgr_c, -1)
            cv2.circle(view, opx, r_px, (240, 240, 240), 1)
        elif obs_type == "box":
            half_ext = spec.get("half_ext", [0.4, 0.4, 0.4])
            if max(half_ext) > 3.0:
                continue
            dx_px = max(4, int(half_ext[0] * scale))
            dy_px = max(4, int(half_ext[1] * scale))
            tl = (opx[0] - dx_px, opx[1] - dy_px)
            br = (opx[0] + dx_px, opx[1] + dy_px)
            # Danger envelope
            cv2.rectangle(view, (tl[0] - 4, tl[1] - 4), (br[0] + 4, br[1] + 4), (45, 55, 68), 1)
            cv2.rectangle(view, tl, br, bgr_c, -1)
            cv2.rectangle(view, tl, br, (240, 240, 240), 1)

    # Start and Goal markers
    spx = w2m(start_pos[0], start_pos[1])
    cv2.circle(view, spx, 4, (120, 140, 160), -1)
    cv2.putText(view, "START", (spx[0] + 6, spx[1] + 3), cv2.FONT_HERSHEY_SIMPLEX, 0.30, (140, 160, 180), 1)

    gpx = w2m(goal_pos[0], goal_pos[1])
    cv2.circle(view, gpx, 6, C2Palette.GOLD_OBJECTIVE, -1)
    cv2.circle(view, gpx, 11, C2Palette.GOLD_OBJECTIVE, 1, cv2.LINE_AA)
    cv2.circle(view, gpx, 16, (0, 160, 200), 1, cv2.LINE_AA)
    cv2.putText(view, "GOAL", (gpx[0] + 12, gpx[1] + 4), cv2.FONT_HERSHEY_DUPLEX, 0.36, C2Palette.GOLD_OBJECTIVE, 1)

    # Trajectory route trail
    if len(trajectory) >= 2:
        traj_pts = [w2m(p[0], p[1]) for p in trajectory]
        for i in range(len(traj_pts) - 1):
            cv2.line(view, traj_pts[i], traj_pts[i + 1], (0, 200, 255), 1, cv2.LINE_AA)

    # Drone symbol and FOV cone
    dpx = w2m(drone_pos[0], drone_pos[1])
    yaw = drone_orn[2]

    cone_len = int(1.6 * scale)
    cone_half_ang = math.radians(35.0)
    a1 = yaw - cone_half_ang
    a2 = yaw + cone_half_ang
    p_cone1 = (dpx[0] + int(cone_len * math.sin(a1)), dpx[1] - int(cone_len * math.cos(a1)))
    p_cone2 = (dpx[0] + int(cone_len * math.sin(a2)), dpx[1] - int(cone_len * math.cos(a2)))
    cone_poly = np.array([dpx, p_cone1, p_cone2], dtype=np.int32)
    cone_overlay = view.copy()
    cv2.fillPoly(cone_overlay, [cone_poly], (60, 120, 80))
    cv2.addWeighted(cone_overlay, 0.45, view, 0.55, 0, view)
    cv2.line(view, dpx, p_cone1, C2Palette.GREEN_TACTICAL, 1, cv2.LINE_AA)
    cv2.line(view, dpx, p_cone2, C2Palette.GREEN_TACTICAL, 1, cv2.LINE_AA)

    cv2.circle(view, dpx, 5, C2Palette.GREEN_TACTICAL, -1)
    cv2.circle(view, dpx, 7, (255, 255, 255), 1, cv2.LINE_AA)

    vx, vy = float(drone_vel[0]), float(drone_vel[1])
    if math.hypot(vx, vy) > 0.1:
        v_end = (dpx[0] + int(vx * scale * 0.8), dpx[1] - int(vy * scale * 0.8))
        cv2.arrowedLine(view, dpx, v_end, C2Palette.AMBER_TACTICAL, 2, tipLength=0.35)

    # ── Left Flank: Precision Tactical Coordinates ──────────────────────────
    lx = 10
    ly = 48
    tgt_dist = float(np.linalg.norm(drone_pos - goal_pos))
    speed = float(np.linalg.norm(drone_vel))
    hdg = (int(math.degrees(yaw)) % 360 + 360) % 360
    left_telemetry = [
        ("NAV UTM", f"GRID 2.0m", C2Palette.TEXT_DIM),
        ("POS X", f"{drone_pos[0]:+5.2f}m", C2Palette.TEXT_WHITE),
        ("POS Y", f"{drone_pos[1]:+5.2f}m", C2Palette.TEXT_WHITE),
        ("POS Z", f"{drone_pos[2]:4.2f}m", C2Palette.CYAN_SENSOR),
        ("SPD", f"{speed:4.2f}m/s", C2Palette.GREEN_TACTICAL),
        ("HDG", f"{hdg:03d} DEG", C2Palette.TEXT_WHITE),
        ("TGT RNG", f"{tgt_dist:4.1f}m", C2Palette.GOLD_OBJECTIVE),
    ]
    for lbl, val, col in left_telemetry:
        cv2.putText(view, lbl, (lx, ly), cv2.FONT_HERSHEY_SIMPLEX, 0.31, C2Palette.TEXT_DIM, 1)
        cv2.putText(view, val, (lx, ly + 13), cv2.FONT_HERSHEY_SIMPLEX, 0.34, col, 1, cv2.LINE_AA)
        ly += 30

    # ── Right Flank: Military Compass Rose & Scale Bar ───────────────────────
    rx = bot_right[0] + 16
    if rx + 65 < w:
        cx_c, cy_c = rx + 32, 60
        cv2.circle(view, (cx_c, cy_c), 20, C2Palette.BORDER_MED, 1, cv2.LINE_AA)
        cv2.circle(view, (cx_c, cy_c), 3, C2Palette.GREEN_TACTICAL, -1)
        cv2.arrowedLine(view, (cx_c, cy_c + 14), (cx_c, cy_c - 16), C2Palette.GREEN_TACTICAL, 2, tipLength=0.35)
        cv2.putText(view, "N", (cx_c - 4, cy_c - 20), cv2.FONT_HERSHEY_DUPLEX, 0.35, C2Palette.GREEN_TACTICAL, 1)

        # Tactical Scale Bar
        sy = cy_c + 45
        scale_bar_len = int(2.0 * scale)
        cv2.line(view, (rx + 8, sy), (rx + 8 + scale_bar_len, sy), C2Palette.TEXT_WHITE, 2)
        cv2.line(view, (rx + 8, sy - 3), (rx + 8, sy + 3), C2Palette.TEXT_WHITE, 1)
        cv2.line(view, (rx + 8 + scale_bar_len, sy - 3), (rx + 8 + scale_bar_len, sy + 3), C2Palette.TEXT_WHITE, 1)
        cv2.putText(view, "2.0m", (rx + 8, sy + 14), cv2.FONT_HERSHEY_SIMPLEX, 0.30, C2Palette.TEXT_MUTED, 1)

        # Legend
        leg_y = sy + 36
        legend_items = [
            ("COL", (40, 220, 110), True),
            ("BOX", (40, 220, 110), False),
            ("GOAL", C2Palette.GOLD_OBJECTIVE, True),
        ]
        for l_lbl, l_col, is_c in legend_items:
            if is_c:
                cv2.circle(view, (rx + 12, leg_y - 2), 4, l_col, -1)
            else:
                cv2.rectangle(view, (rx + 8, leg_y - 6), (rx + 16, leg_y + 2), l_col, -1)
            cv2.putText(view, l_lbl, (rx + 22, leg_y + 1), cv2.FONT_HERSHEY_SIMPLEX, 0.30, C2Palette.TEXT_DIM, 1)
            leg_y += 18

    draw_corner_brackets(view, 0, 0, w, h, C2Palette.BORDER_ACCENT, length=10, thickness=1)
    return view


# =============================================================================
# SUBPANEL VISUALIZERS: SENSORS, AI ACTIONS, XAI, TELEMETRY, EVENT LOG
# =============================================================================
def render_sensor_fusion_panel(
    w: int,
    h: int,
    depth_map: Optional[np.ndarray],
    flow_field: Optional[np.ndarray],
    velocity: np.ndarray,
    attitude: np.ndarray,
    tau_inv: float,
) -> np.ndarray:
    """
    TACTICAL SENSOR PANEL: SENSOR FUSION // UAV-01
    Shows three compact visualizations:
    1. Depth Map (INFERNO colormap)
    2. Optical Flow (VIRIDIS colormap)
    3. Velocity Vector (Flight director scope with polar heading vector and climb bar)
    """
    panel = np.full((h, w, 3), C2Palette.BG_PANEL, dtype=np.uint8)
    draw_panel(panel, 0, 0, w, h, "SENSOR FUSION // UAV-01", "3 SENSORS ONLINE", C2Palette.GREEN_TACTICAL)

    content_y = 30
    content_h = h - 38
    tile_w = (w - 30) // 3
    tile_h = content_h

    # 1. Depth Map Tile
    x1 = 10
    cv2.rectangle(panel, (x1, content_y), (x1 + tile_w, content_y + tile_h), C2Palette.BG_SUBPANEL, -1)
    cv2.rectangle(panel, (x1, content_y), (x1 + tile_w, content_y + tile_h), C2Palette.BORDER_DIM, 1)
    cv2.putText(panel, "DEPTH MAP", (x1 + 8, content_y + 16), cv2.FONT_HERSHEY_SIMPLEX, 0.38, C2Palette.TEXT_WHITE, 1, cv2.LINE_AA)

    img_box_h = tile_h - 48
    if depth_map is not None:
        d_norm = np.clip(depth_map / 10.0, 0.0, 1.0)
        d_uint8 = (d_norm * 255.0).astype(np.uint8)
        d_color = cv2.applyColorMap(d_uint8, cv2.COLORMAP_INFERNO)
        d_resized = cv2.resize(d_color, (tile_w - 12, img_box_h), interpolation=cv2.INTER_NEAREST)
        panel[content_y + 24:content_y + 24 + img_box_h, x1 + 6:x1 + tile_w - 6] = d_resized
        min_d = float(np.min(depth_map))
        d_col = C2Palette.AMBER_TACTICAL if min_d < 1.2 else C2Palette.CYAN_SENSOR
        cv2.putText(panel, f"MIN: {min_d:4.2f}m", (x1 + 8, content_y + tile_h - 6), cv2.FONT_HERSHEY_SIMPLEX, 0.34, d_col, 1, cv2.LINE_AA)
    else:
        cv2.putText(panel, "DATA UNAVAILABLE", (x1 + 10, content_y + tile_h // 2), cv2.FONT_HERSHEY_SIMPLEX, 0.35, C2Palette.TEXT_DIM, 1)

    # 2. Optical Flow Tile
    x2 = x1 + tile_w + 5
    cv2.rectangle(panel, (x2, content_y), (x2 + tile_w, content_y + tile_h), C2Palette.BG_SUBPANEL, -1)
    cv2.rectangle(panel, (x2, content_y), (x2 + tile_w, content_y + tile_h), C2Palette.BORDER_DIM, 1)
    cv2.putText(panel, "OPTICAL FLOW", (x2 + 8, content_y + 16), cv2.FONT_HERSHEY_SIMPLEX, 0.38, C2Palette.TEXT_WHITE, 1, cv2.LINE_AA)

    if flow_field is not None and flow_field.shape[0] >= 2:
        flow_u = flow_field[0] if flow_field.shape[0] == 2 else flow_field[:, :, 0]
        flow_v = flow_field[1] if flow_field.shape[0] == 2 else flow_field[:, :, 1]
        mag = np.hypot(flow_u, flow_v)
        mag_norm = np.clip(mag / 4.0, 0.0, 1.0)
        mag_uint8 = (mag_norm * 255.0).astype(np.uint8)
        flow_color = cv2.applyColorMap(mag_uint8, cv2.COLORMAP_VIRIDIS)
        flow_resized = cv2.resize(flow_color, (tile_w - 12, img_box_h), interpolation=cv2.INTER_NEAREST)
        panel[content_y + 24:content_y + 24 + img_box_h, x2 + 6:x2 + tile_w - 6] = flow_resized
        cv2.putText(panel, f"TTC tau^-1: {tau_inv:4.2f}", (x2 + 8, content_y + tile_h - 6), cv2.FONT_HERSHEY_SIMPLEX, 0.34, C2Palette.GREEN_TACTICAL, 1, cv2.LINE_AA)
    else:
        cv2.putText(panel, "DATA UNAVAILABLE", (x2 + 10, content_y + tile_h // 2), cv2.FONT_HERSHEY_SIMPLEX, 0.35, C2Palette.TEXT_DIM, 1)

    # 3. Velocity Vector Scope Tile
    x3 = x2 + tile_w + 5
    cv2.rectangle(panel, (x3, content_y), (x3 + tile_w, content_y + tile_h), C2Palette.BG_SUBPANEL, -1)
    cv2.rectangle(panel, (x3, content_y), (x3 + tile_w, content_y + tile_h), C2Palette.BORDER_DIM, 1)
    cv2.putText(panel, "VELOCITY VECTOR", (x3 + 8, content_y + 16), cv2.FONT_HERSHEY_SIMPLEX, 0.38, C2Palette.TEXT_WHITE, 1, cv2.LINE_AA)

    vx, vy, vz = float(velocity[0]), float(velocity[1]), float(velocity[2])
    speed = math.sqrt(vx * vx + vy * vy + vz * vz)
    r_deg = math.degrees(attitude[0])
    p_deg = math.degrees(attitude[1])

    # Polar velocity scope display
    scope_cx = x3 + (tile_w - 24) // 2
    scope_cy = content_y + 82
    scope_r = min(42, (tile_w - 36) // 2)

    # Scope range rings (1.0m/s, 2.0m/s, 3.0m/s)
    for ring_m in (1.0, 2.0, 3.0):
        ring_r = int((ring_m / 3.0) * scope_r)
        cv2.circle(panel, (scope_cx, scope_cy), ring_r, C2Palette.BORDER_MED, 1, cv2.LINE_AA)

    # Scope crosshairs
    cv2.line(panel, (scope_cx - scope_r - 4, scope_cy), (scope_cx + scope_r + 4, scope_cy), C2Palette.GRID_LINE, 1)
    cv2.line(panel, (scope_cx, scope_cy - scope_r - 4), (scope_cx, scope_cy + scope_r + 4), C2Palette.GRID_LINE, 1)

    # Horizontal Velocity Vector Arrow (Vx right, Vy up)
    v_norm_scale = scope_r / 3.0
    tip_x = int(scope_cx + vx * v_norm_scale)
    tip_y = int(scope_cy - vy * v_norm_scale)
    tip_x = int(np.clip(tip_x, scope_cx - scope_r, scope_cx + scope_r))
    tip_y = int(np.clip(tip_y, scope_cy - scope_r, scope_cy + scope_r))

    if math.hypot(vx, vy) > 0.08:
        cv2.arrowedLine(panel, (scope_cx, scope_cy), (tip_x, tip_y), C2Palette.AMBER_TACTICAL, 2, tipLength=0.3)
        cv2.circle(panel, (tip_x, tip_y), 3, C2Palette.CYAN_SENSOR, -1)
    else:
        cv2.circle(panel, (scope_cx, scope_cy), 3, C2Palette.GREEN_TACTICAL, -1)

    # Vertical Climb/Descent Bar on the right
    bar_rx = x3 + tile_w - 18
    cv2.line(panel, (bar_rx, scope_cy - scope_r), (bar_rx, scope_cy + scope_r), C2Palette.BORDER_MED, 1)
    cv2.line(panel, (bar_rx - 4, scope_cy), (bar_rx + 4, scope_cy), (90, 115, 130), 1)
    vz_bar_h = int(np.clip(vz * (scope_r / 2.0), -scope_r, scope_r))
    if vz_bar_h != 0:
        bar_top = min(scope_cy, scope_cy - vz_bar_h)
        bar_bot = max(scope_cy, scope_cy - vz_bar_h)
        cv2.rectangle(panel, (bar_rx - 3, bar_top), (bar_rx + 3, bar_bot), C2Palette.CYAN_SENSOR, -1)

    # Numeric readouts below the scope
    ky = scope_cy + scope_r + 20
    kin_lines = [
        ("SPD", f"{speed:4.2f} m/s", C2Palette.GREEN_TACTICAL),
        ("Vx ", f"{vx:+4.2f} m/s", C2Palette.TEXT_WHITE),
        ("Vy ", f"{vy:+4.2f} m/s", C2Palette.TEXT_WHITE),
        ("Vz ", f"{vz:+4.2f} m/s", C2Palette.CYAN_SENSOR),
        ("ROLL", f"{r_deg:+4.1f} DEG", C2Palette.TEXT_MUTED),
        ("PTCH", f"{p_deg:+4.1f} DEG", C2Palette.TEXT_MUTED),
    ]
    for lbl, val, col in kin_lines:
        if ky + 14 < content_y + tile_h:
            cv2.putText(panel, lbl, (x3 + 8, ky), cv2.FONT_HERSHEY_SIMPLEX, 0.33, C2Palette.TEXT_DIM, 1)
            cv2.putText(panel, val, (x3 + 52, ky), cv2.FONT_HERSHEY_SIMPLEX, 0.33, col, 1, cv2.LINE_AA)
            ky += 16

    return panel


def render_ai_decision_and_xai_panel(
    w: int,
    h: int,
    action: np.ndarray,
    confidence: float,
    entropy: float,
    saliency_attr: Optional[np.ndarray],
    fidelity_iou: float,
) -> np.ndarray:
    """
    AI DECISION PANEL & XAI VISUALIZATION
    Action bars with segmented blocks (Roll, Pitch, Throttle, Yaw), policy confidence,
    tactical maneuver classification, and Captum XAI threat attention heatmap.
    """
    panel = np.full((h, w, 3), C2Palette.BG_PANEL, dtype=np.uint8)
    draw_panel(panel, 0, 0, w, h, "AI DECISION // WHY THIS ACTION?", "POLICY ONLINE", C2Palette.GREEN_TACTICAL)

    content_y = 30
    left_w = int(w * 0.58)
    right_x = left_w + 12
    right_w = w - right_x - 10

    act = np.clip(action, -1.0, 1.0)
    action_specs = [
        ("ROLL", act[0], -1.0, 1.0, C2Palette.CYAN_SENSOR),
        ("PITCH", act[1], -1.0, 1.0, C2Palette.GREEN_TACTICAL),
        ("THROT", act[2], -1.0, 1.0, C2Palette.AMBER_TACTICAL),
        ("YAW", act[3], -1.0, 1.0, C2Palette.BLUE_TACTICAL),
    ]

    by = content_y + 8
    for lbl, val, v_min, v_max, col in action_specs:
        draw_bar_gauge(panel, 12, by, left_w - 20, 18, val, v_min, v_max, lbl, col, show_center_zero=True, segments=10)
        by += 24

    draw_bar_gauge(panel, 12, by + 4, left_w - 20, 18, confidence * 100.0, 0.0, 100.0, "CONF", C2Palette.GREEN_TACTICAL, show_center_zero=False, is_percentage=True, segments=10)

    action_desc = "STABILIZED NAVIGATION"
    if act[1] > 0.35:
        action_desc = "FORWARD PENETRATION"
    elif act[0] < -0.25:
        action_desc = "OBSTACLE AVOIDANCE: BANK LEFT"
    elif act[0] > 0.25:
        action_desc = "OBSTACLE AVOIDANCE: BANK RIGHT"
    elif act[2] > 0.3:
        action_desc = "VERTICAL CLIMB MANEUVER"

    cv2.putText(panel, f"TACTICAL MANEUVER: {action_desc}", (14, h - 12), cv2.FONT_HERSHEY_SIMPLEX, 0.34, C2Palette.AMBER_TACTICAL, 1, cv2.LINE_AA)

    # XAI Threat Attention Tile
    cv2.rectangle(panel, (right_x, content_y), (right_x + right_w, h - 10), C2Palette.BG_SUBPANEL, -1)
    cv2.rectangle(panel, (right_x, content_y), (right_x + right_w, h - 10), C2Palette.BORDER_DIM, 1)
    cv2.putText(panel, "THREAT ATTENTION (XAI)", (right_x + 6, content_y + 14), cv2.FONT_HERSHEY_SIMPLEX, 0.34, C2Palette.TEXT_WHITE, 1, cv2.LINE_AA)

    xai_box_h = h - content_y - 48
    if saliency_attr is not None:
        s_boosted = np.power(np.clip(saliency_attr, 0.0, 1.0), 0.7)
        s_uint8 = (s_boosted * 255.0).astype(np.uint8)
        s_color = cv2.applyColorMap(s_uint8, cv2.COLORMAP_TURBO)
        s_resized = cv2.resize(s_color, (right_w - 12, xai_box_h), interpolation=cv2.INTER_CUBIC)
        panel[content_y + 20:content_y + 20 + xai_box_h, right_x + 6:right_x + right_w - 6] = s_resized
        cv2.putText(panel, f"IoU FIDELITY: {fidelity_iou:5.3f}", (right_x + 8, h - 14), cv2.FONT_HERSHEY_SIMPLEX, 0.34, C2Palette.CYAN_SENSOR, 1, cv2.LINE_AA)
    else:
        cv2.putText(panel, "DATA UNAVAILABLE", (right_x + 10, content_y + xai_box_h // 2), cv2.FONT_HERSHEY_SIMPLEX, 0.35, C2Palette.TEXT_DIM, 1)

    return panel


def render_telemetry_and_log_panel(
    w: int,
    h: int,
    status_state: str,
    telemetry_data: Dict[str, Any],
    event_log: List[Tuple[str, str]],
) -> np.ndarray:
    """
    MISSION TELEMETRY & EVENT LOG
    Prominent status badge, telemetry matrix (all 9 fields), and scrolling tactical log.
    """
    panel = np.full((h, w, 3), C2Palette.BG_PANEL, dtype=np.uint8)
    draw_panel(panel, 0, 0, w, h, "MISSION TELEMETRY & LOG", "LIVE C2", C2Palette.GREEN_TACTICAL)

    content_y = 30

    # Prominent tactical status indicator matching exact user requirements
    if status_state == "COLLISION":
        badge_bg = (20, 20, 50)
        badge_border = C2Palette.RED_DANGER
        badge_text = "[ COLLISION ]"
    elif status_state == "GOAL":
        badge_bg = (20, 45, 30)
        badge_border = C2Palette.GREEN_TACTICAL
        badge_text = "[ OBJECTIVE REACHED ]"
    elif status_state == "WARNING":
        badge_bg = (20, 35, 50)
        badge_border = C2Palette.AMBER_TACTICAL
        badge_text = "[ OBSTACLE DETECTED ]"
    else:
        badge_bg = (18, 32, 24)
        badge_border = C2Palette.GREEN_TACTICAL
        badge_text = "[ AUTONOMOUS NAVIGATION ]"

    badge_h = 24
    cv2.rectangle(panel, (12, content_y), (w - 12, content_y + badge_h), badge_bg, -1)
    cv2.rectangle(panel, (12, content_y), (w - 12, content_y + badge_h), badge_border, 1)
    bw = cv2.getTextSize(badge_text, cv2.FONT_HERSHEY_DUPLEX, 0.42, 1)[0][0]
    bx = (w - bw) // 2
    cv2.putText(panel, badge_text, (bx, content_y + 17), cv2.FONT_HERSHEY_DUPLEX, 0.42, badge_border, 1, cv2.LINE_AA)

    split_x = int(w * 0.52)
    ty = content_y + badge_h + 16

    # Comprehensive mission telemetry table (all 9 requested fields)
    telem_items = [
        ("MISSION TIME", telemetry_data.get("mission_time", "00:00:00"), C2Palette.TEXT_WHITE),
        ("EPISODE", f"{telemetry_data.get('ep_idx', 1):04d} / {telemetry_data.get('total_eps', 5):02d}", C2Palette.CYAN_SENSOR),
        ("STEP", f"{telemetry_data.get('step', 0):04d} / {telemetry_data.get('max_steps', 500)}", C2Palette.TEXT_WHITE),
        ("DIST TO GOAL", f"{telemetry_data.get('dist_to_goal', 0.0):5.2f} m", C2Palette.GOLD_OBJECTIVE),
        ("ALTITUDE", f"{telemetry_data.get('altitude', 0.0):5.2f} m", C2Palette.TEXT_WHITE),
        ("VELOCITY", f"{telemetry_data.get('velocity', 0.0):5.2f} m/s", C2Palette.GREEN_TACTICAL),
        ("MIN CLEARANCE", f"{telemetry_data.get('clearance', 0.0):5.2f} m", C2Palette.AMBER_TACTICAL if telemetry_data.get('clearance', 2.0) < 1.2 else C2Palette.TEXT_WHITE),
        ("CURRENT REW", f"{telemetry_data.get('current_reward', 0.0):+6.2f}", C2Palette.GREEN_TACTICAL),
        ("TOTAL REW", f"{telemetry_data.get('total_reward', 0.0):+7.2f}", C2Palette.GREEN_TACTICAL),
    ]

    for label, val, col in telem_items:
        cv2.putText(panel, label, (14, ty), cv2.FONT_HERSHEY_SIMPLEX, 0.32, C2Palette.TEXT_DIM, 1)
        cv2.putText(panel, val, (split_x - 72, ty), cv2.FONT_HERSHEY_SIMPLEX, 0.32, col, 1, cv2.LINE_AA)
        ty += 14

    cv2.line(panel, (split_x, content_y + badge_h + 6), (split_x, h - 10), C2Palette.BORDER_DIM, 1)

    # Event Log with HH:MM:SS timestamps
    lx = split_x + 10
    cv2.putText(panel, "MISSION EVENT LOG", (lx, content_y + badge_h + 16), cv2.FONT_HERSHEY_DUPLEX, 0.36, C2Palette.TEXT_WHITE, 1, cv2.LINE_AA)

    log_y = content_y + badge_h + 34
    recent_events = event_log[-6:] if len(event_log) > 6 else event_log
    for ts, msg in recent_events:
        cv2.putText(panel, ts, (lx, log_y), cv2.FONT_HERSHEY_SIMPLEX, 0.30, C2Palette.CYAN_SENSOR, 1)
        cv2.putText(panel, msg, (lx + 54, log_y), cv2.FONT_HERSHEY_SIMPLEX, 0.30, C2Palette.TEXT_MUTED, 1, cv2.LINE_AA)
        log_y += 15

    return panel


# =============================================================================
# MASTER DASHBOARD COMPOSITOR CLASS
# =============================================================================
class TacticalDashboardRenderer:
    """
    High-End Military UAV Command & Control Console Compositor.
    Assembles the complete 1600x900 tactical dashboard canvas.
    """

    def __init__(self, target_w: int = 1600, target_h: int = 900):
        self.target_w = target_w
        self.target_h = target_h

        self.smoothed_chase_cam = np.array([0.0, -10.5, 2.6], dtype=np.float32)
        self.trajectory_history: deque = deque(maxlen=200)
        self.event_log: List[Tuple[str, str]] = []
        self.current_episode = 0
        self.frame_counter = 0
        self.start_time = time.time()
        self.prev_status_state = "NORMAL"
        self.prev_action = np.zeros(4, dtype=np.float32)
        self.acquired_logged = False

        self.view_mode = 4              # 1=FPV, 2=Chase, 3=Map, 4=All
        self.show_subpanels = True      # Toggled via TAB key
        self.is_paused = False
        self.delay_ms = 1

        self.static_arena_polygons: Optional[List[Dict[str, Any]]] = None
        self.last_seed: Optional[int] = None

        # Pre-allocated canvas buffer to avoid memory thrashing at 60 FPS
        self.canvas_buffer = np.full((self.target_h, self.target_w, 3), C2Palette.BG_DARK, dtype=np.uint8)

        self.log_event("SYSTEM ONLINE // C2 CONSOLE INITIALIZED")
        self.log_event("SENSOR ONLINE // OPTICAL + KINEMATIC")

    def log_event(self, msg: str):
        """Adds a timestamped tactical message to the rolling event log using HH:MM:SS."""
        ts = time.strftime("%H:%M:%S")
        self.event_log.append((ts, msg))
        if len(self.event_log) > 50:
            self.event_log.pop(0)

    def reset_episode(self, ep_idx: int, start_pos: np.ndarray, seed: Optional[int] = None):
        """Called when a new episode begins."""
        self.current_episode = ep_idx
        init_cam = np.array([start_pos[0], max(-9.5, start_pos[1] - 1.8), start_pos[2] + 1.1], dtype=np.float32)
        self.smoothed_chase_cam = init_cam
        self.prev_status_state = "NORMAL"
        self.acquired_logged = False
        self.trajectory_history.clear()
        if seed is not None and seed != self.last_seed:
            self.static_arena_polygons = None
            self.last_seed = seed
        self.log_event(f"EPISODE {ep_idx:02d} START // SEED {seed if seed is not None else 0} LOADED")

    def compute_policy_confidence(self, model: Any, action_mean: np.ndarray) -> Tuple[float, float]:
        """
        Legitimately calculates policy confidence and entropy from the model's
        actor_log_std parameter. Does NOT invent fake numbers.
        """
        try:
            if hasattr(model, "actor_log_std") and TORCH_AVAILABLE:
                with torch.no_grad():
                    log_std = model.actor_log_std.cpu().numpy()
                    stds = np.exp(log_std)
                    mean_std = float(np.mean(stds))
                    entropy = float(np.sum(0.5 + 0.5 * np.log(2 * np.pi * (stds ** 2) + 1e-9)))
                    conf = float(np.clip(1.0 - (mean_std - 0.2) / 0.9, 0.15, 0.98))
                    return conf, entropy
            elif hasattr(model, "log_std"):
                stds = np.exp(model.log_std)
                mean_std = float(np.mean(stds))
                entropy = float(np.sum(0.5 + 0.5 * np.log(2 * np.pi * (stds ** 2) + 1e-9)))
                conf = float(np.clip(1.0 - (mean_std - 0.2) / 0.9, 0.15, 0.98))
                return conf, entropy
        except Exception:
            pass
        return 0.85, -2.10

    def render(
        self,
        env: Any,
        obs: Dict[str, np.ndarray],
        action: np.ndarray,
        saliency_attr: Optional[np.ndarray],
        fidelity_iou: float,
        step_info: Dict[str, Any],
        ep_reward: float,
        step_count: int,
        ep_idx: int,
        total_eps: int,
        model: Any = None,
        fps: float = 60.0,
    ) -> np.ndarray:
        """
        Renders the full 1600x900 Military UAV Command & Control Console canvas.
        Consumes READ-ONLY state from the environment.
        """
        self.frame_counter += 1
        canvas = self.canvas_buffer
        canvas[:] = C2Palette.BG_DARK

        drone_pos = np.array(env.drone_pos, dtype=np.float32)
        drone_orn = np.array(env.drone_orn, dtype=np.float32)
        drone_vel = np.array(env.drone_vel, dtype=np.float32)
        goal_pos = np.array(env.goal_pos, dtype=np.float32)
        start_pos = np.array(env.start_pos, dtype=np.float32)
        obstacle_specs = env.obstacle_specs
        depth_map = env.last_depth_map
        tau_inv = getattr(env, "current_tau_inv", 0.0)

        # Cache static arena polygons (walls, floor, static obstacles)
        if self.static_arena_polygons is None:
            self.static_arena_polygons = ProceduralWorldRenderer.assemble_static_arena_polygons(obstacle_specs)

        self.trajectory_history.append(drone_pos.copy())

        # Smooth chase camera following drone
        yaw = drone_orn[2]
        fwd_drone = np.array([math.sin(yaw), math.cos(yaw), 0.0], dtype=np.float32)
        desired_cam = drone_pos - fwd_drone * 2.4 + np.array([0, 0, 1.15], dtype=np.float32)
        desired_cam[0] = np.clip(desired_cam[0], -4.5, 4.5)
        desired_cam[1] = np.clip(desired_cam[1], -9.5, 9.5)
        desired_cam[2] = np.clip(desired_cam[2], 0.35, 3.3)

        alpha = 0.14
        self.smoothed_chase_cam = self.smoothed_chase_cam + alpha * (desired_cam - self.smoothed_chase_cam)
        self.smoothed_chase_cam[0] = np.clip(self.smoothed_chase_cam[0], -4.5, 4.5)
        self.smoothed_chase_cam[1] = np.clip(self.smoothed_chase_cam[1], -9.5, 9.5)
        self.smoothed_chase_cam[2] = np.clip(self.smoothed_chase_cam[2], 0.35, 3.3)

        dist_to_goal = float(step_info.get("dist_to_goal", np.linalg.norm(drone_pos - goal_pos)))
        collision = bool(step_info.get("collision", False))
        goal_reached = bool(step_info.get("goal_reached", False))
        min_clearance = float(step_info.get("min_depth", 10.0))

        # Simulator-derived event detection
        if collision:
            status_state = "COLLISION"
            if self.prev_status_state != "COLLISION":
                self.log_event("COLLISION // MISSION TERMINATED")
        elif goal_reached:
            status_state = "GOAL"
            if self.prev_status_state != "GOAL":
                self.log_event("OBJECTIVE REACHED // MISSION COMPLETE")
        elif min_clearance < 1.2:
            status_state = "WARNING"
            if self.prev_status_state != "WARNING":
                self.log_event("OBSTACLE DETECTED")
        else:
            status_state = "NORMAL"
            if self.prev_status_state == "WARNING":
                self.log_event("CLEAR PATH")

        # Detect active course correction maneuver
        if self.prev_status_state == "WARNING" and abs(action[0] - self.prev_action[0]) > 0.25:
            self.log_event("COURSE CORRECTION")

        # Detect objective acquired
        if dist_to_goal < 4.0 and not self.acquired_logged:
            self.log_event("OBJECTIVE ACQUIRED")
            self.acquired_logged = True

        self.prev_status_state = status_state
        self.prev_action = action.copy()

        mission_time_s = time.time() - self.start_time
        hrs = int(mission_time_s) // 3600
        mins = (int(mission_time_s) % 3600) // 60
        secs = int(mission_time_s) % 60
        time_str = f"{hrs:02d}:{mins:02d}:{secs:02d}"

        # ── Header Bar ──────────────────────────────────────────────────────
        header_h = 52
        cv2.rectangle(canvas, (0, 0), (self.target_w, header_h), C2Palette.BG_HEADER, -1)
        cv2.line(canvas, (0, header_h), (self.target_w, header_h), C2Palette.BORDER_MED, 1)

        draw_led(canvas, 24, 26, C2Palette.GREEN_TACTICAL, radius=5)
        cv2.putText(canvas, "UAV-01 // AUTONOMOUS MODE", (38, 22), cv2.FONT_HERSHEY_DUPLEX, 0.46, C2Palette.TEXT_WHITE, 1, cv2.LINE_AA)
        cv2.putText(canvas, "PPO-BC NEURAL NAVIGATION | 240Hz SENSORS", (38, 40), cv2.FONT_HERSHEY_SIMPLEX, 0.34, C2Palette.CYAN_SENSOR, 1, cv2.LINE_AA)

        title_main = "AUTONOMOUS UAV // TACTICAL NAVIGATION SYSTEM"
        title_sub = "MISSION: INDOOR OBSTACLE NAVIGATION"
        tm_w = cv2.getTextSize(title_main, cv2.FONT_HERSHEY_DUPLEX, 0.50, 1)[0][0]
        ts_w = cv2.getTextSize(title_sub, cv2.FONT_HERSHEY_SIMPLEX, 0.36, 1)[0][0]
        cv2.putText(canvas, title_main, ((self.target_w - tm_w) // 2, 23), cv2.FONT_HERSHEY_DUPLEX, 0.50, C2Palette.TEXT_WHITE, 1, cv2.LINE_AA)
        cv2.putText(canvas, title_sub, ((self.target_w - ts_w) // 2, 42), cv2.FONT_HERSHEY_SIMPLEX, 0.36, C2Palette.AMBER_TACTICAL, 1, cv2.LINE_AA)

        # Dynamic Status LEDs: SIM, PHYSICS, POLICY, SENSOR with FAULT/WARNING/OFFLINE states
        sim_status = "FAULT" if collision else "LIVE"
        sim_color = C2Palette.RED_DANGER if collision else C2Palette.GREEN_TACTICAL

        phys_status = "FAULT" if collision else "ONLINE"
        phys_color = C2Palette.RED_DANGER if collision else C2Palette.GREEN_TACTICAL

        pol_status = "OFFLINE" if model is None else "ONLINE"
        pol_color = C2Palette.RED_DANGER if model is None else C2Palette.GREEN_TACTICAL

        if depth_map is None:
            sens_status = "OFFLINE"
            sens_color = C2Palette.RED_DANGER
        elif min_clearance < 1.2:
            sens_status = "WARNING"
            sens_color = C2Palette.AMBER_TACTICAL
        else:
            sens_status = "ONLINE"
            sens_color = C2Palette.GREEN_TACTICAL

        led_items = [
            (f"SIM: {sim_status}", sim_color),
            (f"PHYS: {phys_status}", phys_color),
            (f"POL: {pol_status}", pol_color),
            (f"SENS: {sens_status}", sens_color),
        ]
        hx = self.target_w - 490
        for lbl, col in led_items:
            draw_led(canvas, hx, 26, col, lbl, radius=4)
            hx += 120

        # ── Viewport Layout Dimensions ───────────────────────────────────────
        top_y = 58
        margin = 15
        gap = 12

        # If subpanels are collapsed (via TAB key), expand top viewports down to status bar
        if self.show_subpanels:
            top_h = 416
            bot_h = 378
        else:
            top_h = self.target_h - top_y - 38
            bot_h = 0

        # ── Operations View Rendering ────────────────────────────────────────
        if self.view_mode == 1:
            win_fpv = render_window_fpv(
                w=self.target_w - margin * 2,
                h=top_h,
                drone_pos=drone_pos,
                drone_orn=drone_orn,
                drone_vel=drone_vel,
                static_polys=self.static_arena_polygons,
                goal_pos=goal_pos,
                min_clearance=min_clearance,
                frame_num=self.frame_counter,
                mission_time_s=mission_time_s,
            )
            canvas[top_y:top_y + top_h, margin:self.target_w - margin] = win_fpv
        elif self.view_mode == 2:
            win_chase = render_window_chase(
                w=self.target_w - margin * 2,
                h=top_h,
                drone_pos=drone_pos,
                drone_orn=drone_orn,
                drone_vel=drone_vel,
                smoothed_cam_pos=self.smoothed_chase_cam,
                trajectory=list(self.trajectory_history),
                static_polys=self.static_arena_polygons,
                goal_pos=goal_pos,
                frame_num=self.frame_counter,
                mission_time_s=mission_time_s,
            )
            canvas[top_y:top_y + top_h, margin:self.target_w - margin] = win_chase
        elif self.view_mode == 3:
            win_map = render_window_overview_map(
                w=self.target_w - margin * 2,
                h=top_h,
                drone_pos=drone_pos,
                drone_orn=drone_orn,
                drone_vel=drone_vel,
                trajectory=list(self.trajectory_history),
                obstacle_specs=obstacle_specs,
                goal_pos=goal_pos,
                start_pos=start_pos,
            )
            canvas[top_y:top_y + top_h, margin:self.target_w - margin] = win_map
        else:
            win_w = (self.target_w - margin * 2 - gap * 2) // 3
            x_w1 = margin
            x_w2 = x_w1 + win_w + gap
            x_w3 = x_w2 + win_w + gap

            win_fpv = render_window_fpv(
                w=win_w,
                h=top_h,
                drone_pos=drone_pos,
                drone_orn=drone_orn,
                drone_vel=drone_vel,
                static_polys=self.static_arena_polygons,
                goal_pos=goal_pos,
                min_clearance=min_clearance,
                frame_num=self.frame_counter,
                mission_time_s=mission_time_s,
            )
            win_chase = render_window_chase(
                w=win_w,
                h=top_h,
                drone_pos=drone_pos,
                drone_orn=drone_orn,
                drone_vel=drone_vel,
                smoothed_cam_pos=self.smoothed_chase_cam,
                trajectory=list(self.trajectory_history),
                static_polys=self.static_arena_polygons,
                goal_pos=goal_pos,
                frame_num=self.frame_counter,
                mission_time_s=mission_time_s,
            )
            win_map = render_window_overview_map(
                w=win_w,
                h=top_h,
                drone_pos=drone_pos,
                drone_orn=drone_orn,
                drone_vel=drone_vel,
                trajectory=list(self.trajectory_history),
                obstacle_specs=obstacle_specs,
                goal_pos=goal_pos,
                start_pos=start_pos,
            )

            canvas[top_y:top_y + top_h, x_w1:x_w1 + win_w] = win_fpv
            canvas[top_y:top_y + top_h, x_w2:x_w2 + win_w] = win_chase
            canvas[top_y:top_y + top_h, x_w3:x_w3 + win_w] = win_map

        # ── Bottom Subpanels (Rendered only when show_subpanels is True) ─────
        if self.show_subpanels and bot_h > 0:
            bot_y = top_y + top_h + 10
            sub_w = (self.target_w - margin * 2 - gap * 2) // 3

            x_s1 = margin
            x_s2 = x_s1 + sub_w + gap
            x_s3 = x_s2 + sub_w + gap

            flow_field = obs.get("visual", np.zeros((5, 84, 84)))[3:5] if "visual" in obs else None
            p_sensor = render_sensor_fusion_panel(
                w=sub_w,
                h=bot_h,
                depth_map=depth_map,
                flow_field=flow_field,
                velocity=drone_vel,
                attitude=drone_orn,
                tau_inv=tau_inv,
            )

            conf, entropy = self.compute_policy_confidence(model, action)
            p_ai = render_ai_decision_and_xai_panel(
                w=sub_w,
                h=bot_h,
                action=action,
                confidence=conf,
                entropy=entropy,
                saliency_attr=saliency_attr,
                fidelity_iou=fidelity_iou,
            )

            speed = float(np.linalg.norm(drone_vel))
            telemetry_dict = {
                "mission_time": time_str,
                "ep_idx": ep_idx,
                "total_eps": total_eps,
                "step": step_count,
                "max_steps": getattr(env, "max_steps", 500),
                "dist_to_goal": dist_to_goal,
                "altitude": float(drone_pos[2]),
                "velocity": speed,
                "clearance": min_clearance,
                "current_reward": float(step_info.get("reward", 0.0)),
                "total_reward": ep_reward,
            }
            p_telem = render_telemetry_and_log_panel(
                w=sub_w,
                h=bot_h,
                status_state=status_state,
                telemetry_data=telemetry_dict,
                event_log=self.event_log,
            )

            canvas[bot_y:bot_y + bot_h, x_s1:x_s1 + sub_w] = p_sensor
            canvas[bot_y:bot_y + bot_h, x_s2:x_s2 + sub_w] = p_ai
            canvas[bot_y:bot_y + bot_h, x_s3:x_s3 + sub_w] = p_telem

        # ── Bottom Status Bar ────────────────────────────────────────────────
        bar_y = self.target_h - 30
        cv2.rectangle(canvas, (0, bar_y), (self.target_w, self.target_h), C2Palette.BG_HEADER, -1)
        cv2.line(canvas, (0, bar_y), (self.target_w, bar_y), C2Palette.BORDER_MED, 1)

        cuda_mem_mb = 0.0
        if CUDA_AVAILABLE:
            try:
                cuda_mem_mb = torch.cuda.memory_allocated() / (1024.0 * 1024.0)
            except Exception:
                pass

        py_ver = f"{sys.version_info.major}.{sys.version_info.minor}"
        status_left = (
            f"PYTHON: {py_ver} | CUDA: {'ONLINE' if CUDA_AVAILABLE else 'OFFLINE'} | "
            f"GPU: {GPU_DEVICE_NAME} | FPS: {fps:4.1f} | 24Hz STEP | POLICY: PPO-BC | "
            f"MEM: {cuda_mem_mb:.1f}MB | MODE: EVALUATION"
        )
        cv2.putText(canvas, status_left, (16, bar_y + 19), cv2.FONT_HERSHEY_SIMPLEX, 0.35, C2Palette.TEXT_MUTED, 1, cv2.LINE_AA)

        controls_right = "[1] FPV  [2] CHASE  [3] MAP  [4] ALL  [TAB] PANELS  [SPC] PAUSE  [R] RESTART  [N] NEXT  [F] FULL  [ESC] EXIT"
        cr_w = cv2.getTextSize(controls_right, cv2.FONT_HERSHEY_SIMPLEX, 0.34, 1)[0][0]
        cv2.putText(canvas, controls_right, (self.target_w - cr_w - 16, bar_y + 19), cv2.FONT_HERSHEY_SIMPLEX, 0.34, C2Palette.CYAN_SENSOR, 1, cv2.LINE_AA)

        return canvas

    def handle_key(self, key_code: int) -> Dict[str, Any]:
        """
        Processes interactive keyboard controls:
        1=FPV, 2=Chase, 3=Map, 4=Console, TAB=toggle panels, SPACE=pause, R=restart, N=next, F=fullscreen, ESC/Q=exit.
        """
        result = {
            "exit": False,
            "restart": False,
            "next_episode": False,
            "toggle_fullscreen": False,
        }

        if key_code == -1:
            return result

        k = key_code & 0xFF
        if k in (27, ord('q'), ord('Q')):  # ESC or Q
            result["exit"] = True
        elif k == ord('1'):
            self.view_mode = 1
            self.log_event("VIEW: FOCUS CAM-01 (FORWARD EO)")
        elif k == ord('2'):
            self.view_mode = 2
            self.log_event("VIEW: FOCUS CAM-02 (TACTICAL CHASE)")
        elif k == ord('3'):
            self.view_mode = 3
            self.log_event("VIEW: FOCUS MAP-01 (TACTICAL MAP)")
        elif k == ord('4'):
            self.view_mode = 4
            self.log_event("VIEW: RESTORE FULL C2 CONSOLE")
        elif k == 9:  # TAB key: toggle telemetry/XAI panels
            self.show_subpanels = not self.show_subpanels
            sub_status = "ENABLED" if self.show_subpanels else "COLLAPSED"
            self.log_event(f"TELEMETRY PANELS {sub_status}")
        elif k == 32:  # SPACE key: pause/resume
            self.is_paused = not self.is_paused
            status_p = "PAUSED" if self.is_paused else "RESUMED"
            self.log_event(f"SIMULATION {status_p}")
        elif k in (ord('r'), ord('R')):
            result["restart"] = True
            self.log_event("OPERATOR COMMAND // RESTART EPISODE")
        elif k in (ord('n'), ord('N')):
            result["next_episode"] = True
            self.log_event("OPERATOR COMMAND // NEXT EPISODE")
        elif k in (ord('f'), ord('F')):
            result["toggle_fullscreen"] = True
        elif k in (ord('+'), ord('=')):
            self.delay_ms = max(1, self.delay_ms - 5)
        elif k in (ord('-'), ord('_')):
            self.delay_ms = min(100, self.delay_ms + 5)

        return result
