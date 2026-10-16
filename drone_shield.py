"""
drone_shield.py - Stop, Hover & Re-Route (SHR) Safety Shield
-------------------------------------------------------------
Tier 1 Gymnasium Wrapper providing deterministic safety guarantees
for autonomous drone navigation in 3D indoor environments.

Key Capabilities:
1. Dual-Mode Sensing:
   - "oracle": Privileged geometric raycasting against dynamic obstacles
     and arena perimeter walls along velocity cone and lateral axes.
   - "camera": Horizon-filtered central ROI depth analysis ignoring floor/ceiling reflections.
2. Physics-Informed TTC Trigger & Smooth Speed Governor:
   - Evaluates time-to-contact (TTC) and minimum clearance.
   - Speed governor smoothly scales commanded speeds approaching obstacles or walls:
     v_cap(d) = min(3.0, sqrt(2 * a_dec * max(d - d_safe, 0))).
3. SHR Finite State Machine (FSM):
   - NOMINAL: Policy control with active speed governor.
   - BRAKE: Instant zero-action active stop (0.000m stopping displacement).
   - SCAN: Clearance and goal-biased evaluation of Left vs Right avoidance paths.
   - REROUTE: Closed-loop lateral flight with altitude hold until forward clearance exceeds d_safe.
   - RETREAT: Anti-deadlock fallback when corner-trapped or blocked.
4. Pass-through toggle (enabled=False) for byte-identical A/B benchmarking.
"""

from enum import Enum
import heapq
import math
from typing import Dict, List, Optional, Tuple, Any

import gymnasium as gym
import numpy as np


class ShieldState(str, Enum):
    """FSM States for the SHR Safety Shield."""
    DISABLED = "DISABLED"
    NOMINAL = "NOMINAL"
    BRAKE = "BRAKE"
    SCAN = "SCAN"
    REROUTE = "REROUTE"
    RETREAT = "RETREAT"
    PLANNER = "PLANNER"


# ── Geometric Raycasting Helpers (Analytical 2D in horizontal plane) ──────────

def ray_cylinder_intersect_2d(
    p0: np.ndarray,
    d: np.ndarray,
    center: np.ndarray,
    radius: float,
    r_drone: float = 0.20,
) -> float:
    """
    Computes first positive intersection distance t >= 0 along ray p0 + t*d
    with a 2D circle of radius (radius + r_drone).
    Returns float('inf') if no intersection in forward ray direction.
    """
    r_eff = radius + r_drone
    delta = p0[:2] - center[:2]
    c = float(np.dot(delta, delta) - r_eff * r_eff)
    if c <= 0.0:
        return 0.0  # Already intersecting / inside effective radius

    b = float(np.dot(delta, d[:2]))
    discr = b * b - c
    if discr < 0.0:
        return float("inf")

    sqrt_discr = math.sqrt(discr)
    t = -b - sqrt_discr
    if t >= 0.0:
        return float(t)
    return float("inf")


def ray_box_intersect_2d(
    p0: np.ndarray,
    d: np.ndarray,
    center: np.ndarray,
    half_ext: np.ndarray,
    r_drone: float = 0.20,
) -> float:
    """
    Computes first positive intersection distance t >= 0 along ray p0 + t*d
    with an axis-aligned 2D bounding box centered at center with extents
    (half_ext + r_drone). Uses slab method.
    """
    hx = half_ext[0] + r_drone
    hy = half_ext[1] + r_drone

    x_min, x_max = center[0] - hx, center[0] + hx
    y_min, y_max = center[1] - hy, center[1] + hy

    x0, y0 = float(p0[0]), float(p0[1])
    dx, dy = float(d[0]), float(d[1])

    if x_min <= x0 <= x_max and y_min <= y0 <= y_max:
        return 0.0

    if abs(dx) > 1e-7:
        tx1 = (x_min - x0) / dx
        tx2 = (x_max - x0) / dx
        tx_enter = min(tx1, tx2)
        tx_exit = max(tx1, tx2)
    else:
        if x0 < x_min or x0 > x_max:
            return float("inf")
        tx_enter = -float("inf")
        tx_exit = float("inf")

    if abs(dy) > 1e-7:
        ty1 = (y_min - y0) / dy
        ty2 = (y_max - y0) / dy
        ty_enter = min(ty1, ty2)
        ty_exit = max(ty1, ty2)
    else:
        if y0 < y_min or y0 > y_max:
            return float("inf")
        ty_enter = -float("inf")
        ty_exit = float("inf")

    t_enter = max(tx_enter, ty_enter)
    t_exit = min(tx_exit, ty_exit)

    if t_exit >= max(0.0, t_enter) and t_exit >= 0.0:
        return float(max(0.0, t_enter))
    return float("inf")


def ray_arena_intersect_2d(
    p0: np.ndarray,
    d: np.ndarray,
    x_lim: float = 4.6,
    y_lim: float = 9.6,
    r_drone: float = 0.20,
) -> float:
    """
    Computes distance along ray p0 + t*d to the arena bounding walls
    accounting for drone radius: |x| <= (x_lim - r_drone), |y| <= (y_lim - r_drone).
    """
    x_eff = max(0.1, x_lim - r_drone)
    y_eff = max(0.1, y_lim - r_drone)

    x0, y0 = float(p0[0]), float(p0[1])
    dx, dy = float(d[0]), float(d[1])

    t_min = float("inf")

    if dx > 1e-7:
        t_min = min(t_min, (x_eff - x0) / dx)
    elif dx < -1e-7:
        t_min = min(t_min, (-x_eff - x0) / dx)

    if dy > 1e-7:
        t_min = min(t_min, (y_eff - y0) / dy)
    elif dy < -1e-7:
        t_min = min(t_min, (-y_eff - y0) / dy)

    return float(max(0.0, t_min))


def cast_ray_oracle(
    p0: np.ndarray,
    d: np.ndarray,
    obstacles: List[Dict[str, Any]],
    x_lim: float = 4.6,
    y_lim: float = 9.6,
    r_drone: float = 0.20,
) -> float:
    """
    Casts a 2D ray from p0 along unit direction d against all obstacles
    and arena bounding walls. Returns the minimum clearance distance in meters.
    """
    min_dist = ray_arena_intersect_2d(p0, d, x_lim=x_lim, y_lim=y_lim, r_drone=r_drone)

    for spec in obstacles:
        pos = np.asarray(spec.get("pos", [0, 0, 0]), dtype=np.float32)
        # Skip boundary wall boxes if present in obstacle_specs to avoid redundancy
        if abs(pos[0]) >= (x_lim - 0.2) or abs(pos[1]) >= (y_lim - 0.2):
            continue

        obs_type = spec.get("type", "box")
        if obs_type == "cylinder":
            radius = float(spec.get("radius", 0.4))
            dist = ray_cylinder_intersect_2d(p0, d, pos, radius, r_drone=r_drone)
        else:
            half_ext = np.asarray(spec.get("half_ext", [0.4, 0.4, 0.4]), dtype=np.float32)
            dist = ray_box_intersect_2d(p0, d, pos, half_ext, r_drone=r_drone)

        if dist < min_dist:
            min_dist = dist

    return float(min_dist)


def point_obstacle_distance_2d(
    p0: np.ndarray,
    obstacles: List[Dict[str, Any]],
    x_lim: float = 4.6,
    y_lim: float = 9.6,
    r_drone: float = 0.20,
) -> float:
    """
    Computes omnidirectional Euclidean distance from drone body surface to the
    nearest obstacle or arena wall.
    """
    x0, y0 = float(p0[0]), float(p0[1])
    x_eff = max(0.1, x_lim - r_drone)
    y_eff = max(0.1, y_lim - r_drone)

    min_dist = min(
        x_eff - abs(x0),
        y_eff - abs(y0),
    )
    min_dist = max(0.0, min_dist)

    for spec in obstacles:
        pos = np.asarray(spec.get("pos", [0, 0, 0]), dtype=np.float32)
        if abs(pos[0]) >= (x_lim - 0.2) or abs(pos[1]) >= (y_lim - 0.2):
            continue

        obs_type = spec.get("type", "box")
        if obs_type == "cylinder":
            radius = float(spec.get("radius", 0.4))
            center_dist = math.hypot(x0 - pos[0], y0 - pos[1])
            surface_dist = max(0.0, center_dist - (radius + r_drone))
        else:
            half_ext = np.asarray(spec.get("half_ext", [0.4, 0.4, 0.4]), dtype=np.float32)
            dx = max(0.0, abs(x0 - pos[0]) - half_ext[0])
            dy = max(0.0, abs(y0 - pos[1]) - half_ext[1])
            surface_dist = max(0.0, math.hypot(dx, dy) - r_drone)

        if surface_dist < min_dist:
            min_dist = surface_dist

    return float(min_dist)


# ── Privileged Simulator Information: 2D Grid / A* Path Planner ───────────────

def _plan_single_margin(
    drone_pos: np.ndarray,
    goal_pos: np.ndarray,
    obstacles: List[Dict[str, Any]],
    x_lim: float = 4.6,
    y_lim: float = 9.6,
    drone_radius: float = 0.20,
    inflation_margin: float = 0.20,
    grid_res: float = 0.15,
) -> Optional[List[Tuple[float, float]]]:
    total_inflation = drone_radius + inflation_margin

    x_min, x_max = -x_lim + total_inflation, x_lim - total_inflation
    y_min, y_max = -y_lim + total_inflation, y_lim - total_inflation

    nx = int(math.ceil((x_max - x_min) / grid_res)) + 1
    ny = int(math.ceil((y_max - y_min) / grid_res)) + 1

    dyn_obs = []
    for spec in obstacles:
        pos = spec.get("pos", [0, 0, 0])
        if abs(pos[0]) >= (x_lim - 0.2) or abs(pos[1]) >= (y_lim - 0.2):
            continue
        obs_type = spec.get("type", "box")
        if obs_type == "cylinder":
            dyn_obs.append(("cylinder", float(pos[0]), float(pos[1]), float(spec.get("radius", 0.4))))
        else:
            he = spec.get("half_ext", [0.4, 0.4, 0.4])
            dyn_obs.append(("box", float(pos[0]), float(pos[1]), float(he[0]), float(he[1])))

    def is_free(gx: float, gy: float) -> bool:
        if gx < x_min or gx > x_max or gy < y_min or gy > y_max:
            return False
        for ob in dyn_obs:
            if ob[0] == "cylinder":
                cx, cy, r = ob[1], ob[2], ob[3]
                if math.hypot(gx - cx, gy - cy) < (r + total_inflation):
                    return False
            else:
                cx, cy, hx, hy = ob[1], ob[2], ob[3], ob[4]
                if (abs(gx - cx) < (hx + total_inflation)) and (abs(gy - cy) < (hy + total_inflation)):
                    return False
        return True

    def world_to_grid(wx: float, wy: float) -> Tuple[int, int]:
        ix = int(round((wx - x_min) / grid_res))
        iy = int(round((wy - y_min) / grid_res))
        return max(0, min(nx - 1, ix)), max(0, min(ny - 1, iy))

    def grid_to_world(ix: int, iy: int) -> Tuple[float, float]:
        return x_min + ix * grid_res, y_min + iy * grid_res

    start_cell = world_to_grid(float(drone_pos[0]), float(drone_pos[1]))
    goal_cell = world_to_grid(float(goal_pos[0]), float(goal_pos[1]))

    if not is_free(*grid_to_world(*start_cell)):
        best_d = float("inf")
        best_c = start_cell
        for radius in range(1, 10):
            found_r = False
            for dx in range(-radius, radius + 1):
                for dy in (-radius, radius):
                    c = (max(0, min(nx - 1, start_cell[0] + dx)), max(0, min(ny - 1, start_cell[1] + dy)))
                    wx, wy = grid_to_world(*c)
                    if is_free(wx, wy):
                        d = math.hypot(wx - drone_pos[0], wy - drone_pos[1])
                        if d < best_d:
                            best_d = d
                            best_c = c
                            found_r = True
            for dy in range(-radius + 1, radius):
                for dx in (-radius, radius):
                    c = (max(0, min(nx - 1, start_cell[0] + dx)), max(0, min(ny - 1, start_cell[1] + dy)))
                    wx, wy = grid_to_world(*c)
                    if is_free(wx, wy):
                        d = math.hypot(wx - drone_pos[0], wy - drone_pos[1])
                        if d < best_d:
                            best_d = d
                            best_c = c
                            found_r = True
            if found_r:
                break
        start_cell = best_c

    if not is_free(*grid_to_world(*goal_cell)):
        best_d = float("inf")
        best_c = goal_cell
        for radius in range(1, 10):
            found_r = False
            for dx in range(-radius, radius + 1):
                for dy in (-radius, radius):
                    c = (max(0, min(nx - 1, goal_cell[0] + dx)), max(0, min(ny - 1, goal_cell[1] + dy)))
                    wx, wy = grid_to_world(*c)
                    if is_free(wx, wy):
                        d = math.hypot(wx - goal_pos[0], wy - goal_pos[1])
                        if d < best_d:
                            best_d = d
                            best_c = c
                            found_r = True
            for dy in range(-radius + 1, radius):
                for dx in (-radius, radius):
                    c = (max(0, min(nx - 1, goal_cell[0] + dx)), max(0, min(ny - 1, goal_cell[1] + dy)))
                    wx, wy = grid_to_world(*c)
                    if is_free(wx, wy):
                        d = math.hypot(wx - goal_pos[0], wy - goal_pos[1])
                        if d < best_d:
                            best_d = d
                            best_c = c
                            found_r = True
            if found_r:
                break
        goal_cell = best_c

    open_set = []
    heapq.heappush(open_set, (0.0, 0.0, start_cell))
    came_from = {}
    g_score = {start_cell: 0.0}

    dirs = [
        (1, 0, 1.0), (-1, 0, 1.0), (0, 1, 1.0), (0, -1, 1.0),
        (1, 1, 1.414), (-1, 1, 1.414), (1, -1, 1.414), (-1, -1, 1.414)
    ]
    target_wx, target_wy = grid_to_world(*goal_cell)

    found = False
    while open_set:
        _, cur_g, current = heapq.heappop(open_set)
        if current == goal_cell:
            found = True
            break

        for dx, dy, cost in dirs:
            next_cell = (current[0] + dx, current[1] + dy)
            if not (0 <= next_cell[0] < nx and 0 <= next_cell[1] < ny):
                continue

            n_wx, n_wy = grid_to_world(*next_cell)
            if not is_free(n_wx, n_wy):
                continue

            if dx != 0 and dy != 0:
                wx1, wy1 = grid_to_world(current[0] + dx, current[1])
                wx2, wy2 = grid_to_world(current[0], current[1] + dy)
                if not (is_free(wx1, wy1) or is_free(wx2, wy2)):
                    continue

            tentative_g = cur_g + cost * grid_res
            if next_cell not in g_score or tentative_g < g_score[next_cell]:
                came_from[next_cell] = current
                g_score[next_cell] = tentative_g
                h = math.hypot(n_wx - target_wx, n_wy - target_wy)
                heapq.heappush(open_set, (tentative_g + h, tentative_g, next_cell))

    if not found:
        return None

    path = []
    curr = goal_cell
    while curr in came_from:
        path.append(grid_to_world(*curr))
        curr = came_from[curr]
    path.append(grid_to_world(*start_cell))
    path.reverse()
    return path


def build_inflated_grid_and_plan(
    drone_pos: np.ndarray,
    goal_pos: np.ndarray,
    obstacles: List[Dict[str, Any]],
    x_lim: float = 4.6,
    y_lim: float = 9.6,
    drone_radius: float = 0.20,
    inflation_margin: float = 0.20,
    grid_res: float = 0.15,
) -> Optional[List[Tuple[float, float]]]:
    """
    Computes a collision-free 2D path from drone_pos to goal_pos using A* on an inflated obstacle grid.

    NOTE: This uses PRIVILEGED SIMULATOR INFORMATION (ground-truth geometric obstacle specs from PyBullet),
    serving as the final escalation step in the SHR v2 safety shield when heuristic reactive bypass deadlocks.
    Employs adaptive margin relaxation if tight passages are encountered.
    """
    margins = [inflation_margin]
    if inflation_margin > 0.10:
        margins.append(0.10)
    if inflation_margin > 0.05:
        margins.append(0.05)

    for m in margins:
        path = _plan_single_margin(
            drone_pos=drone_pos,
            goal_pos=goal_pos,
            obstacles=obstacles,
            x_lim=x_lim,
            y_lim=y_lim,
            drone_radius=drone_radius,
            inflation_margin=m,
            grid_res=grid_res,
        )
        if path is not None:
            return path
    return None


# ── Stop, Hover & Re-Route (SHR) Safety Wrapper ──────────────────────────────

class StopAndRerouteShield(gym.Wrapper):
    """
    Stop, Hover & Re-Route (SHR) Safety Shield Gymnasium Wrapper.

    Sits directly between the policy and the environment to prevent collisions
    with obstacles and arena boundary walls.
    """

    def __init__(
        self,
        env: gym.Env,
        sensor_mode: str = "oracle",
        enabled: bool = True,
        t_brake: float = 0.28,
        d_min: float = 0.45,
        d_safe: float = 0.55,
        a_dec: float = 4.5,
        v_reroute: float = 1.5,
        min_reroute_steps: int = 3,
        max_reroute_steps: int = 40,
        cooldown_steps: int = 3,
        max_deadlock_attempts: int = 3,
        body_radius: float = 0.20,
        target_altitude: float = 1.5,
        scan_w_clearance: float = 1.0,
        scan_w_goal: float = 1.2,
        scan_w_wall: float = 2.0,
        scan_w_history: float = 1.5,
        shield_version: str = "v1",
        guided_bypass: Optional[bool] = None,
        goal_proximity: Optional[bool] = None,
        oracle_planner: Optional[bool] = None,
        anti_amnesia: Optional[bool] = None,
        forward_creep: Optional[bool] = None,
        planner_inflation_margin: float = 0.20,
        planner_grid_res: float = 0.15,
        **kwargs,
    ):
        super().__init__(env)
        self.sensor_mode = str(sensor_mode).lower()
        if self.sensor_mode not in ("oracle", "camera"):
            raise ValueError(f"Unknown sensor_mode: {sensor_mode}. Must be 'oracle' or 'camera'.")

        self.enabled = bool(enabled)
        self.t_brake = float(t_brake)
        self.d_min = float(d_min)
        self.d_safe = float(d_safe)
        self.a_dec = float(a_dec)
        self.v_reroute = float(v_reroute)
        self.min_reroute_steps = int(min_reroute_steps)
        self.max_reroute_steps = int(max_reroute_steps)
        self.cooldown_steps = int(cooldown_steps)
        self.max_deadlock_attempts = int(max_deadlock_attempts)
        self.body_radius = float(body_radius)
        self.target_altitude = float(target_altitude)

        # Scanning weights
        self.scan_w_clearance = float(scan_w_clearance)
        self.scan_w_goal = float(scan_w_goal)
        self.scan_w_wall = float(scan_w_wall)
        self.scan_w_history = float(scan_w_history)

        # Shield version & v2 feature switches
        self.shield_version = str(shield_version).lower()
        is_v2 = (self.shield_version == "v2")
        self.guided_bypass = bool(guided_bypass) if guided_bypass is not None else is_v2
        self.goal_proximity = bool(goal_proximity) if goal_proximity is not None else is_v2
        self.oracle_planner = bool(oracle_planner) if oracle_planner is not None else is_v2
        self.anti_amnesia = bool(anti_amnesia) if anti_amnesia is not None else is_v2
        self.forward_creep = bool(forward_creep) if forward_creep is not None else is_v2
        self.planner_inflation_margin = float(planner_inflation_margin)
        self.planner_grid_res = float(planner_grid_res)

        # Arena bounds cache
        self.arena_x_lim = 4.6
        self.arena_y_lim = 9.6
        self.arena_z_min = 0.15
        self.arena_z_max = 3.5

        # FSM State
        self._reset_shield_state()

    def _reset_shield_state(self):
        """Resets all internal FSM and telemetry counters."""
        self.state = ShieldState.NOMINAL if self.enabled else ShieldState.DISABLED
        self.cooldown_counter = 0
        self.reroute_steps = 0
        self.reroute_direction: Optional[str] = None  # "LEFT" or "RIGHT"
        self.deadlock_attempts = 0
        self.retreat_steps = 0
        self.stop_latency = 0
        self.standoff_distance = 0.0
        self.last_ttc = float("inf")
        self.last_clearance = 10.0
        self.last_intervened = False
        self.brake_start_step = 0
        self.current_step = 0
        self.last_reroute_dir: Optional[str] = None

        # v2 Tracking State
        self.bypass_target_y: Optional[float] = None
        self.bypass_clear_consecutive: int = 0
        self.planned_path: Optional[List[Tuple[float, float]]] = None
        self.plan_idx: int = 0
        drone_pos = self._get_drone_pos()
        self.planner_start_y = float(drone_pos[1])
        self.last_progress_y = float(drone_pos[1])

    def _find_blocking_obstacle(self, pos: np.ndarray) -> Optional[float]:
        """
        Finds the far edge y of the closest obstacle in front of the drone.
        Used by guided bypass to retain control until the obstacle is passed.
        """
        obstacles = self._get_obstacle_specs()
        x0, y0 = float(pos[0]), float(pos[1])
        closest_y_far = None
        min_front_dist = float("inf")

        for ob in obstacles:
            p = ob.get("pos", [0, 0, 0])
            if abs(p[0]) >= (self.arena_x_lim - 0.2) or abs(p[1]) >= (self.arena_y_lim - 0.2):
                continue
            ob_type = ob.get("type", "box")
            if ob_type == "cylinder":
                r = float(ob.get("radius", 0.4))
                y_front = p[1] - r
                y_far = p[1] + r
                hx = r
            else:
                he = ob.get("half_ext", [0.4, 0.4, 0.4])
                y_front = p[1] - he[1]
                y_far = p[1] + he[1]
                hx = he[0]

            if y_far > y0 and (y_front - y0) < 3.5:
                if abs(p[0] - x0) <= (hx + self.body_radius + self.d_min + 0.35):
                    dist_ahead = max(0.0, y_front - y0)
                    if dist_ahead < min_front_dist:
                        min_front_dist = dist_ahead
                        closest_y_far = y_far

        return closest_y_far

    # ── Environment Property Access Helpers ────────────────────────────────────

    def _get_drone_pos(self) -> np.ndarray:
        if hasattr(self.env, "drone_pos"):
            return np.asarray(self.env.drone_pos, dtype=np.float32)
        if hasattr(self.unwrapped, "drone_pos"):
            return np.asarray(self.unwrapped.drone_pos, dtype=np.float32)
        return np.array([0.0, -8.0, self.target_altitude], dtype=np.float32)

    def _get_drone_vel(self) -> np.ndarray:
        if hasattr(self.env, "drone_vel"):
            return np.asarray(self.env.drone_vel, dtype=np.float32)
        if hasattr(self.unwrapped, "drone_vel"):
            return np.asarray(self.unwrapped.drone_vel, dtype=np.float32)
        return np.zeros(3, dtype=np.float32)

    def _get_drone_orn(self) -> np.ndarray:
        if hasattr(self.env, "drone_orn"):
            return np.asarray(self.env.drone_orn, dtype=np.float32)
        if hasattr(self.unwrapped, "drone_orn"):
            return np.asarray(self.unwrapped.drone_orn, dtype=np.float32)
        return np.zeros(3, dtype=np.float32)

    def _get_goal_pos(self) -> np.ndarray:
        if hasattr(self.env, "goal_position"):
            return np.asarray(self.env.goal_position, dtype=np.float32)
        if hasattr(self.env, "goal_pos"):
            return np.asarray(self.env.goal_pos, dtype=np.float32)
        if hasattr(self.unwrapped, "goal_pos"):
            return np.asarray(self.unwrapped.goal_pos, dtype=np.float32)
        return np.array([0.0, 8.0, self.target_altitude], dtype=np.float32)

    def _get_obstacle_specs(self) -> List[Dict[str, Any]]:
        if hasattr(self.env, "obstacle_geometries"):
            return self.env.obstacle_geometries
        if hasattr(self.env, "obstacle_specs"):
            return self.env.obstacle_specs
        if hasattr(self.unwrapped, "obstacle_specs"):
            return self.unwrapped.obstacle_specs
        return []

    def _get_last_depth_image(self) -> np.ndarray:
        if hasattr(self.env, "last_depth_image"):
            return np.asarray(self.env.last_depth_image, dtype=np.float32)
        if hasattr(self.unwrapped, "last_depth_image"):
            return np.asarray(self.unwrapped.last_depth_image, dtype=np.float32)
        return np.full((84, 84), 12.0, dtype=np.float32)

    def _get_arena_bounds(self) -> Dict[str, float]:
        if hasattr(self.env, "arena_bounds"):
            return self.env.arena_bounds
        return {
            "x_lim": self.arena_x_lim,
            "y_lim": self.arena_y_lim,
            "z_min": 0.15,
            "z_max": 3.5,
        }

    # ── Sensing Implementations ───────────────────────────────────────────────

    def _sense_oracle(self, policy_action: Optional[np.ndarray] = None) -> Dict[str, Any]:
        """
        Oracle Sensing:
        Privileged geometric query computing ray clearances along velocity vector
        (with a +/- 30 deg cone), lateral directions (+/- 90 deg), rear (180 deg),
        and direct goal line-of-sight.
        """
        pos = self._get_drone_pos()
        vel = self._get_drone_vel()
        goal = self._get_goal_pos()
        obstacles = self._get_obstacle_specs()
        bounds = self._get_arena_bounds()
        x_lim = float(bounds.get("x_lim", self.arena_x_lim))
        y_lim = float(bounds.get("y_lim", self.arena_y_lim))

        speed_xy = float(math.hypot(vel[0], vel[1]))

        # Commanded velocity from policy action
        if policy_action is not None:
            v_cmd = np.array([policy_action[0] * 3.0, policy_action[1] * 3.0], dtype=np.float32)
            speed_cmd = float(math.hypot(v_cmd[0], v_cmd[1]))
        else:
            v_cmd = np.zeros(2, dtype=np.float32)
            speed_cmd = 0.0

        # Vector towards goal in horizontal plane
        goal_diff = goal[:2] - pos[:2]
        dist_goal = float(math.hypot(goal_diff[0], goal_diff[1]))
        if dist_goal > 1e-4:
            u_goal = goal_diff / dist_goal
        else:
            u_goal = np.array([0.0, 1.0], dtype=np.float32)

        # Base forward directions: check current velocity direction AND commanded policy velocity
        dirs_to_check = []
        if speed_xy >= 0.1:
            dirs_to_check.append(np.array([vel[0] / speed_xy, vel[1] / speed_xy], dtype=np.float32))
        if speed_cmd >= 0.1:
            v_dir = np.array([v_cmd[0] / speed_cmd, v_cmd[1] / speed_cmd], dtype=np.float32)
            if not dirs_to_check or float(np.dot(dirs_to_check[0], v_dir)) < 0.95:
                dirs_to_check.append(v_dir)
        if not dirs_to_check:
            dirs_to_check.append(u_goal.copy())

        # 1. Forward Cone (+/- 30 degrees)
        cone_angles_deg = [-30.0, -20.0, -10.0, 0.0, 10.0, 20.0, 30.0]
        min_fwd_clearance = float("inf")
        min_fwd_ttc = float("inf")

        for fwd_d in dirs_to_check:
            base_angle = math.atan2(float(fwd_d[1]), float(fwd_d[0]))
            for deg in cone_angles_deg:
                ang = base_angle + math.radians(deg)
                ray_d = np.array([math.cos(ang), math.sin(ang)], dtype=np.float32)
                c = cast_ray_oracle(pos, ray_d, obstacles, x_lim, y_lim, self.body_radius)
                if c < min_fwd_clearance:
                    min_fwd_clearance = c

                # Closing speed along this ray: maximum of current velocity and commanded velocity
                spd_cur = float(vel[0] * ray_d[0] + vel[1] * ray_d[1])
                spd_pol = float(v_cmd[0] * ray_d[0] + v_cmd[1] * ray_d[1])
                closing_spd = max(0.0, spd_cur, spd_pol)

                if closing_spd > 0.05:
                    ray_ttc = c / closing_spd
                    if ray_ttc < min_fwd_ttc:
                        min_fwd_ttc = ray_ttc

        # 2. Lateral directions in world frame (Left is -X, Right is +X)
        left_clearance = float("inf")
        for deg in [-15.0, 0.0, 15.0]:
            ang = math.pi + math.radians(deg)
            ray_d = np.array([math.cos(ang), math.sin(ang)], dtype=np.float32)
            c = cast_ray_oracle(pos, ray_d, obstacles, x_lim, y_lim, self.body_radius)
            if c < left_clearance:
                left_clearance = c

        right_clearance = float("inf")
        for deg in [-15.0, 0.0, 15.0]:
            ang = math.radians(deg)
            ray_d = np.array([math.cos(ang), math.sin(ang)], dtype=np.float32)
            c = cast_ray_oracle(pos, ray_d, obstacles, x_lim, y_lim, self.body_radius)
            if c < right_clearance:
                right_clearance = c

        # 3. Rear clearance in world frame (-Y)
        rear_clearance = float("inf")
        for deg in [-15.0, 0.0, 15.0]:
            ang = (-math.pi / 2.0) + math.radians(deg)
            ray_rear = np.array([math.cos(ang), math.sin(ang)], dtype=np.float32)
            c = cast_ray_oracle(pos, ray_rear, obstacles, x_lim, y_lim, self.body_radius)
            if c < rear_clearance:
                rear_clearance = c

        # 4. Goal clearance along direct vector to goal
        goal_clearance = cast_ray_oracle(pos, u_goal, obstacles, x_lim, y_lim, self.body_radius)

        # 5. Omnidirectional nearest surface distance
        omni_clearance = point_obstacle_distance_2d(pos, obstacles, x_lim, y_lim, self.body_radius)

        # 6. Forward corridor clearance along world +Y
        ray_fwd_corr = np.array([0.0, 1.0], dtype=np.float32)
        fwd_corridor_clearance = cast_ray_oracle(pos, ray_fwd_corr, obstacles, x_lim, y_lim, self.body_radius)

        return {
            "clearance": float(min_fwd_clearance),
            "ttc": float(min_fwd_ttc),
            "left_clearance": float(left_clearance),
            "right_clearance": float(right_clearance),
            "rear_clearance": float(rear_clearance),
            "goal_clearance": float(goal_clearance),
            "fwd_corridor_clearance": float(fwd_corridor_clearance),
            "omni_clearance": float(omni_clearance),
            "u_goal": u_goal,
            "base_dir": dirs_to_check[0],
            "pos": pos,
            "vel": vel,
        }

    def _sense_camera(self, policy_action: Optional[np.ndarray] = None) -> Dict[str, Any]:
        """
        Camera Sensing:
        Extracts depth from central ROI ignoring floor reflections (lower 30% of rows)
        and ceiling (top 15% of rows). Computes Left vs Right sector depths.
        """
        depth_img = self._get_last_depth_image()
        pos = self._get_drone_pos()
        vel = self._get_drone_vel()
        orn = self._get_drone_orn()
        goal = self._get_goal_pos()

        # Camera orientation: yaw is orn[2]
        yaw = float(orn[2])
        cam_forward = np.array([math.sin(yaw), math.cos(yaw)], dtype=np.float32)

        # Sector slicing (84x84 image) around horizontal optical axis
        row_min, row_max = 34, 48

        center_roi = depth_img[row_min:row_max, 34:50]
        left_roi = depth_img[row_min:row_max, 10:34]
        right_roi = depth_img[row_min:row_max, 50:74]

        center_depth = float(np.percentile(center_roi, 25.0))
        left_depth = float(np.percentile(left_roi, 25.0))
        right_depth = float(np.percentile(right_roi, 25.0))

        fwd_clearance = max(0.0, center_depth - self.body_radius)

        # Integrate arena wall distances with camera sectors
        d_wall_left = max(0.0, float(pos[0] - (-self.arena_x_lim) - self.body_radius))
        d_wall_right = max(0.0, float(self.arena_x_lim - pos[0] - self.body_radius))
        
        # Lateral reroute movement is bounded by the arena wall distances
        lat_clear_left = d_wall_left
        lat_clear_right = d_wall_right

        # Forward closing speed along optical axis
        spd_cur = float(vel[0] * cam_forward[0] + vel[1] * cam_forward[1])
        if policy_action is not None:
            spd_pol = float(policy_action[0] * 3.0 * cam_forward[0] + policy_action[1] * 3.0 * cam_forward[1])
        else:
            spd_pol = 0.0
        speed_cam_fwd = max(0.0, spd_cur, spd_pol)

        if speed_cam_fwd > 0.05:
            ttc = fwd_clearance / speed_cam_fwd
        else:
            ttc = float("inf")

        # Goal direction
        goal_diff = goal[:2] - pos[:2]
        dist_goal = float(math.hypot(goal_diff[0], goal_diff[1]))
        if dist_goal > 1e-4:
            u_goal = goal_diff / dist_goal
        else:
            u_goal = np.array([0.0, 1.0], dtype=np.float32)

        return {
            "clearance": float(fwd_clearance),
            "ttc": float(ttc),
            "left_clearance": float(lat_clear_left),
            "right_clearance": float(lat_clear_right),
            "cam_left_depth": float(left_depth),
            "cam_right_depth": float(right_depth),
            "rear_clearance": float("inf"),
            "goal_clearance": float(fwd_clearance),
            "fwd_corridor_clearance": float(fwd_clearance),
            "omni_clearance": float(fwd_clearance),
            "u_goal": u_goal,
            "base_dir": cam_forward,
            "pos": pos,
            "vel": vel,
        }

    def _sense(self, policy_action: Optional[np.ndarray] = None) -> Dict[str, Any]:
        """Dispatches sensing query based on sensor_mode."""
        if self.sensor_mode == "camera":
            return self._sense_camera(policy_action=policy_action)
        return self._sense_oracle(policy_action=policy_action)

    # ── Speed Governor ────────────────────────────────────────────────────────

    def _apply_speed_governor(
        self,
        policy_action: np.ndarray,
        fwd_clearance: float,
        pos: np.ndarray,
    ) -> Tuple[np.ndarray, bool]:
        """
        Speed Governor:
        In NOMINAL state, smoothly scales commanded speed if approaching obstacles or arena walls:
        v_cap(d) = min(3.0, sqrt(2 * a_dec * max(d - d_safe, 0))).
        Also enforces lateral and longitudinal perimeter caps.
        """
        governed_action = policy_action.copy()
        intervened = False

        # Desired velocities in m/s (actions in [-1, 1] scaled by 3.0)
        vx = float(policy_action[0] * 3.0)
        vy = float(policy_action[1] * 3.0)
        vz = float(policy_action[2] * 3.0)
        yaw_rate = float(policy_action[3])

        def _calc_v_cap(dist: float) -> float:
            if dist <= (self.d_safe + 1e-4):
                return 0.0
            return min(3.0, math.sqrt(2.0 * self.a_dec * (dist - self.d_safe)))

        # 1. Forward obstacle governor
        v_cap_obs = _calc_v_cap(fwd_clearance)
        speed_horiz = math.hypot(vx, vy)
        if speed_horiz > v_cap_obs and speed_horiz > 1e-4:
            scale = v_cap_obs / speed_horiz
            vx *= scale
            vy *= scale
            intervened = True

        # 2. Lateral perimeter walls governor (X in [-4.6, 4.6])
        x = float(pos[0])
        d_east = max(0.0, (self.arena_x_lim - self.body_radius) - x)
        d_west = max(0.0, x - (-self.arena_x_lim + self.body_radius))

        if vx > 0.0:  # Moving East
            v_cap_east = _calc_v_cap(d_east)
            if vx > v_cap_east:
                vx = v_cap_east
                intervened = True
        elif vx < 0.0:  # Moving West
            v_cap_west = _calc_v_cap(d_west)
            if vx < -v_cap_west:
                vx = -v_cap_west
                intervened = True

        # 3. Longitudinal perimeter walls governor (Y in [-9.6, 9.6])
        y = float(pos[1])
        d_north = max(0.0, (self.arena_y_lim - self.body_radius) - y)
        d_south = max(0.0, y - (-self.arena_y_lim + self.body_radius))

        if vy > 0.0:  # Moving North
            v_cap_north = _calc_v_cap(d_north)
            if vy > v_cap_north:
                vy = v_cap_north
                intervened = True
        elif vy < 0.0:  # Moving South
            v_cap_south = _calc_v_cap(d_south)
            if vy < -v_cap_south:
                vy = -v_cap_south
                intervened = True

        # 4. Vertical boundary & altitude governor (Z in [arena_z_min, arena_z_max])
        current_z = float(pos[2]) if len(pos) > 2 else self.target_altitude
        d_floor = max(0.0, current_z - self.arena_z_min - self.body_radius)
        d_ceil = max(0.0, self.arena_z_max - self.body_radius - current_z)

        orig_vz = vz

        if vz < 0.0:  # Moving downward towards floor
            v_cap_floor = _calc_v_cap(d_floor)
            if d_floor <= self.d_safe:
                # Floor proximity limit reached: zero downward velocity and apply upward recovery
                recovery_vz = max(0.0, min(1.0, (self.d_safe - d_floor) * 2.0))
                vz = recovery_vz
                intervened = True
            elif vz < -v_cap_floor:
                vz = -v_cap_floor
                intervened = True
        elif vz > 0.0:  # Moving upward towards ceiling
            v_cap_ceil = _calc_v_cap(d_ceil)
            if d_ceil <= self.d_safe:
                vz = 0.0
                intervened = True
            elif vz > v_cap_ceil:
                vz = v_cap_ceil
                intervened = True

        # Altitude restoration bias when deviating significantly from nominal cruising altitude
        alt_err = self.target_altitude - current_z
        if abs(alt_err) > 0.40:
            v_restore = float(np.clip(2.0 * alt_err, -2.0, 2.0))
            if alt_err > 0.0:  # Drone is below cruising altitude
                if vz < v_restore:
                    vz = v_restore
                    intervened = True
            else:  # Drone is above cruising altitude
                if vz > v_restore:
                    vz = v_restore
                    intervened = True

        if abs(vz - orig_vz) > 1e-4:
            intervened = True

        governed_action[0] = np.clip(vx / 3.0, -1.0, 1.0)
        governed_action[1] = np.clip(vy / 3.0, -1.0, 1.0)
        governed_action[2] = np.clip(vz / 3.0, -1.0, 1.0)
        governed_action[3] = np.clip(yaw_rate, -1.0, 1.0)

        # Clean check whether values changed meaningfully
        if np.max(np.abs(governed_action - policy_action)) > 0.01:
            intervened = True

        return governed_action, intervened

    # ── Direction Evaluation (SCAN) ───────────────────────────────────────────

    def _evaluate_scan_direction(
        self,
        left_clearance: float,
        right_clearance: float,
        u_goal: np.ndarray,
        pos: np.ndarray,
    ) -> str:
        """
        Evaluates Left vs Right lateral avoidance options.
        Penalizes sides closer to arena walls or obstacles.
        Biased toward goal vector alignment.
        """
        x = float(pos[0])
        d_wall_left = max(0.01, (x - (-self.arena_x_lim)) - self.body_radius)
        d_wall_right = max(0.01, (self.arena_x_lim - x) - self.body_radius)

        # Proximity penalty: sharply increases when within 1.5m of wall
        pen_wall_left = (1.5 / d_wall_left) if d_wall_left < 1.5 else 0.0
        pen_wall_right = (1.5 / d_wall_right) if d_wall_right < 1.5 else 0.0

        # Goal alignment bias (in world frame, Left is -X, Right is +X)
        goal_bias_left = float(u_goal[0] * (-1.0))
        goal_bias_right = float(u_goal[0] * (+1.0))

        # Anti-deadlock history penalty
        pen_scale = 3.0 * float(self.deadlock_attempts)
        pen_hist_left = pen_scale if (self.last_reroute_dir == "LEFT" and self.deadlock_attempts > 0) else 0.0
        pen_hist_right = pen_scale if (self.last_reroute_dir == "RIGHT" and self.deadlock_attempts > 0) else 0.0

        score_left = (
            self.scan_w_clearance * left_clearance
            + self.scan_w_goal * goal_bias_left
            - self.scan_w_wall * pen_wall_left
            - pen_hist_left
        )
        score_right = (
            self.scan_w_clearance * right_clearance
            + self.scan_w_goal * goal_bias_right
            - self.scan_w_wall * pen_wall_right
            - pen_hist_right
        )

        # If one side is blocked (< d_min), force other side
        if left_clearance < self.d_min and right_clearance >= self.d_min:
            return "RIGHT"
        if right_clearance < self.d_min and left_clearance >= self.d_min:
            return "LEFT"

        return "LEFT" if score_left >= score_right else "RIGHT"

    # ── FSM Action & State Transition Logic ───────────────────────────────────

    def _compute_shield_action(
        self,
        policy_action: np.ndarray,
    ) -> Tuple[np.ndarray, bool, str, float, float, float, int]:
        """
        Executes one step of the SHR Finite State Machine.
        Returns:
            executed_action, intervened, shield_state, ttc, clearance, standoff_dist, stop_latency
        """
        policy_action = np.nan_to_num(np.asarray(policy_action, dtype=np.float32), nan=0.0, posinf=1.0, neginf=-1.0)
        telemetry = self._sense(policy_action=policy_action)
        clearance = float(telemetry["clearance"])
        ttc = float(telemetry["ttc"])
        pos = telemetry["pos"]
        vel = telemetry["vel"]
        speed = float(math.hypot(vel[0], vel[1]))

        executed_action = policy_action.copy()
        intervened = False

        # Forward progress tracking for anti_amnesia
        if self.anti_amnesia and (pos[1] - self.last_progress_y >= 1.5):
            self.deadlock_attempts = 0
            self.last_progress_y = float(pos[1])

        # Goal proximity check
        goal = self._get_goal_pos()
        dist_goal = float(math.hypot(pos[0] - goal[0], pos[1] - goal[1]))
        in_goal_proximity = (self.goal_proximity and dist_goal <= 1.6)

        # Decrement cooldown counter if active
        if self.cooldown_counter > 0:
            self.cooldown_counter -= 1

        # Check trigger: fires if (ttc < t_brake) OR (clearance < d_min) OR (omni_clearance < d_min)
        trigger_fired = (ttc < self.t_brake) or (clearance < self.d_min) or (telemetry.get("omni_clearance", float("inf")) < self.d_min)

        # ── GOAL PROXIMITY MODE OVERRIDE ───────────────────────────────────────
        if in_goal_proximity:
            intervened = True
            self.state = ShieldState.NOMINAL
            self.deadlock_attempts = 0
            u_g = telemetry["u_goal"]
            clr_along_path = min(clearance, telemetry.get("goal_clearance", clearance))
            if clr_along_path > self.d_safe:
                v_app = 1.0
            elif clr_along_path > 0.20:
                v_app = min(0.8, math.sqrt(2.0 * self.a_dec * max(0.0, clr_along_path - 0.20)))
            else:
                v_app = 0.0
            vx_cmd = u_g[0] * v_app
            vy_cmd = u_g[1] * v_app
            current_z = float(pos[2])
            vz_cmd = float(np.clip(2.0 * (self.target_altitude - current_z), -1.0, 1.0))
            raw_act = np.clip(np.array([vx_cmd / 3.0, vy_cmd / 3.0, vz_cmd / 3.0, 0.0], dtype=np.float32), -1.0, 1.0)
            return (raw_act, intervened, "NOMINAL", ttc, clearance, self.standoff_distance, self.stop_latency)

        # ── ORACLE PLANNER ESCALATION STATE (PRIVILEGED SIMULATOR INFORMATION) ──
        if self.state == ShieldState.PLANNER:
            intervened = True
            if self.planned_path is None or len(self.planned_path) == 0:
                goal_pos_2d = self._get_goal_pos()[:2]
                self.planned_path = build_inflated_grid_and_plan(
                    pos, goal_pos_2d, self._get_obstacle_specs(),
                    inflation_margin=self.planner_inflation_margin, grid_res=self.planner_grid_res
                )
                self.plan_idx = 0
                self.planner_start_y = float(pos[1])

            if self.planned_path is not None and len(self.planned_path) > 0:
                # Advance target waypoint along path
                while self.plan_idx < len(self.planned_path) - 1:
                    wx, wy = self.planned_path[self.plan_idx]
                    if math.hypot(wx - pos[0], wy - pos[1]) < 0.35:
                        self.plan_idx += 1
                    else:
                        break

                target_wpt = self.planned_path[min(self.plan_idx, len(self.planned_path) - 1)]
                dx = target_wpt[0] - pos[0]
                dy = target_wpt[1] - pos[1]
                dist_wpt = math.hypot(dx, dy)
                if dist_wpt > 1e-4:
                    ux = dx / dist_wpt
                    uy = dy / dist_wpt
                else:
                    ux, uy = 0.0, 1.0

                v_track = 1.1
                vx_cmd = ux * v_track
                vy_cmd = uy * v_track

                # Check clearance along exact trajectory
                ray_dir = np.array([ux, uy], dtype=np.float32)
                traj_clr = cast_ray_oracle(pos, ray_dir, self._get_obstacle_specs(), self.arena_x_lim, self.arena_y_lim, self.body_radius)
                if traj_clr < self.d_min:
                    scale = max(0.0, traj_clr - 0.20) / max(0.01, self.d_min - 0.20)
                    vx_cmd *= scale
                    vy_cmd *= scale

                current_z = float(pos[2])
                vz_cmd = float(np.clip(2.0 * (self.target_altitude - current_z), -1.0, 1.0))
                executed_action = np.clip(np.array([vx_cmd / 3.0, vy_cmd / 3.0, vz_cmd / 3.0, 0.0], dtype=np.float32), -1.0, 1.0)

                fwd_corr = telemetry.get("fwd_corridor_clearance", clearance)
                if (
                    (pos[1] - self.planner_start_y >= 2.0 or self.plan_idx >= len(self.planned_path) - 1)
                    and fwd_corr >= (self.d_safe + 0.30)
                    and clearance >= self.d_safe
                ):
                    self.state = ShieldState.NOMINAL
                    self.planned_path = None
                    self.cooldown_counter = self.cooldown_steps
                    self.deadlock_attempts = 0

                return (executed_action, intervened, ShieldState.PLANNER.value, ttc, clearance, self.standoff_distance, self.stop_latency)
            else:
                self.state = ShieldState.RETREAT
                self.retreat_steps = 1
                return self._compute_shield_action(policy_action)

        # ── STATE MACHINE DISPATCH ─────────────────────────────────────────────

        if self.state == ShieldState.NOMINAL:
            # Policy has control, tempered by the speed governor
            gov_action, gov_intervened = self._apply_speed_governor(policy_action, clearance, pos)
            executed_action = gov_action
            intervened = gov_intervened

            # Check for trigger activation (respecting cooldown)
            if trigger_fired and self.cooldown_counter == 0:
                self.state = ShieldState.BRAKE
                self.stop_latency = 0
                self.standoff_distance = clearance
                # Immediately dispatch instantaneous stop action
                executed_action = np.zeros(4, dtype=np.float32)
                intervened = True

        elif self.state == ShieldState.BRAKE:
            # Active instantaneous stop: command zero action [0, 0, 0, 0]
            # (RECON.md characterized stopping displacement as 0.000m)
            self.stop_latency += 1
            executed_action = np.zeros(4, dtype=np.float32)
            intervened = True

            # Measure full stop (speed < 0.08 m/s or latency >= 1)
            if speed < 0.08 or self.stop_latency >= 1:
                self.standoff_distance = clearance
                self.state = ShieldState.SCAN

        elif self.state == ShieldState.SCAN:
            # Evaluate optimal lateral path and transition immediately
            intervened = True

            left_c = telemetry.get("cam_left_depth", telemetry["left_clearance"]) if self.sensor_mode == "camera" else telemetry["left_clearance"]
            right_c = telemetry.get("cam_right_depth", telemetry["right_clearance"]) if self.sensor_mode == "camera" else telemetry["right_clearance"]

            # Choose optimal lateral direction
            chosen_dir = self._evaluate_scan_direction(
                left_clearance=left_c,
                right_clearance=right_c,
                u_goal=telemetry["u_goal"],
                pos=pos,
            )

            # Check if completely trapped: both lateral sides blocked by wall or obstacle
            max_lat_clear = max(telemetry["left_clearance"], telemetry["right_clearance"])
            d_wall_left = max(0.0, float(pos[0] - (-self.arena_x_lim) - self.body_radius))
            d_wall_right = max(0.0, float(self.arena_x_lim - pos[0] - self.body_radius))

            if max_lat_clear < self.d_min and (d_wall_left < self.d_min or d_wall_right < self.d_min):
                if self.oracle_planner and self.deadlock_attempts >= 2:
                    self.state = ShieldState.PLANNER
                    self.planned_path = None
                    return self._compute_shield_action(policy_action)
                # Corner-trapped: execute retreat fallback
                self.state = ShieldState.RETREAT
                self.retreat_steps = 1
                current_z = float(pos[2])
                vz_cmd = float(np.clip(2.0 * (self.target_altitude - current_z), -1.0, 1.0))
                executed_action = np.array([0.0, -0.8 / 3.0, vz_cmd / 3.0, 0.0], dtype=np.float32)
            else:
                self.reroute_direction = chosen_dir
                self.last_reroute_dir = chosen_dir
                self.reroute_steps = 1
                self.state = ShieldState.REROUTE

                if self.guided_bypass:
                    y_far = self._find_blocking_obstacle(pos)
                    if y_far is not None:
                        self.bypass_target_y = y_far + 0.30
                    else:
                        self.bypass_target_y = float(pos[1]) + 0.80
                    self.bypass_clear_consecutive = 0

                sign = -1.0 if self.reroute_direction == "LEFT" else 1.0
                curr_lat_clear = left_c if chosen_dir == "LEFT" else right_c
                d_wall_curr = d_wall_left if chosen_dir == "LEFT" else d_wall_right
                effective_lat_clear = min(curr_lat_clear, d_wall_curr)
                if effective_lat_clear <= self.d_min:
                    v_cap_lat = 0.0
                else:
                    v_cap_lat = min(self.v_reroute, math.sqrt(2.0 * self.a_dec * (effective_lat_clear - self.d_min)))
                vx_cmd = sign * v_cap_lat

                u_g = telemetry["u_goal"]
                fwd_corr = telemetry.get("fwd_corridor_clearance", clearance)
                d_north = max(0.0, (self.arena_y_lim - self.body_radius) - pos[1])
                effective_fwd = min(fwd_corr, d_north)
                d_south = max(0.0, float(pos[1] - (-self.arena_y_lim) - self.body_radius))
                rear_avail = min(telemetry["rear_clearance"], d_south)

                if u_g[1] < -0.1 and rear_avail > self.d_min:
                    vy_cmd = -min(0.8, math.sqrt(2.0 * self.a_dec * max(0.0, rear_avail - self.d_min)))
                elif effective_fwd > (self.d_safe + 0.20):
                    vy_cmd = min(1.5, math.sqrt(2.0 * self.a_dec * max(0.0, effective_fwd - self.d_min)))
                elif effective_fwd > self.d_min:
                    vy_cmd = min(0.4, math.sqrt(2.0 * self.a_dec * max(0.0, effective_fwd - self.d_min)))
                    if self.forward_creep or self.guided_bypass:
                        vy_cmd = max(0.35, vy_cmd)
                else:
                    if (self.forward_creep or self.guided_bypass) and effective_fwd > 0.25:
                        vy_cmd = 0.35
                    else:
                        vy_cmd = 0.0

                current_z = float(pos[2])
                vz_cmd = float(np.clip(2.0 * (self.target_altitude - current_z), -1.0, 1.0))
                executed_action = np.array([vx_cmd / 3.0, vy_cmd / 3.0, vz_cmd / 3.0, 0.0], dtype=np.float32)
                executed_action = np.clip(executed_action, -1.0, 1.0)

        elif self.state == ShieldState.REROUTE:
            self.reroute_steps += 1
            intervened = True

            u_g = telemetry["u_goal"]
            fwd_corr = telemetry.get("fwd_corridor_clearance", clearance)
            curr_lat_clear = telemetry["left_clearance"] if self.reroute_direction == "LEFT" else telemetry["right_clearance"]
            d_wall_curr = (pos[0] - (-self.arena_x_lim) - self.body_radius) if self.reroute_direction == "LEFT" else (self.arena_x_lim - pos[0] - self.body_radius)
            effective_lat_clear = min(curr_lat_clear, d_wall_curr)
            d_north = max(0.0, (self.arena_y_lim - self.body_radius) - pos[1])
            effective_fwd = min(fwd_corr, d_north)
            d_south = max(0.0, float(pos[1] - (-self.arena_y_lim) - self.body_radius))
            rear_avail = min(telemetry["rear_clearance"], d_south)

            is_max_steps = (self.reroute_steps >= self.max_reroute_steps)
            is_lateral_blocked = (effective_lat_clear < self.d_min or d_wall_curr < self.d_min)

            # Max duration or lateral blockage fallback
            if is_max_steps or is_lateral_blocked:
                self.deadlock_attempts += 1
                if self.oracle_planner and self.deadlock_attempts >= 2:
                    self.state = ShieldState.PLANNER
                    self.planned_path = None
                    return self._compute_shield_action(policy_action)

                if is_max_steps or (self.deadlock_attempts >= 2 and rear_avail > self.d_min):
                    # Max steps exceeded or both directions blocked: execute retreat fallback
                    self.state = ShieldState.RETREAT
                    self.retreat_steps = 1
                    current_z = float(pos[2])
                    vz_cmd = float(np.clip(2.0 * (self.target_altitude - current_z), -1.0, 1.0))
                    v_back = min(0.8, math.sqrt(2.0 * self.a_dec * max(0.0, rear_avail - self.d_min)))
                    executed_action = np.array([0.0, -v_back / 3.0, vz_cmd / 3.0, 0.0], dtype=np.float32)
                else:
                    # Lateral blockage on first attempt: try opposite direction directly
                    self.reroute_direction = "RIGHT" if self.reroute_direction == "LEFT" else "LEFT"
                    self.last_reroute_dir = self.reroute_direction
                    self.reroute_steps = 1
                    sign = -1.0 if self.reroute_direction == "LEFT" else 1.0
                    opp_lat_clear = telemetry["left_clearance"] if self.reroute_direction == "LEFT" else telemetry["right_clearance"]
                    opp_d_wall = (pos[0] - (-self.arena_x_lim) - self.body_radius) if self.reroute_direction == "LEFT" else (self.arena_x_lim - pos[0] - self.body_radius)
                    effective_opp = min(opp_lat_clear, opp_d_wall)
                    if effective_opp <= self.d_min:
                        v_cap_lat = 0.0
                    else:
                        v_cap_lat = min(self.v_reroute, math.sqrt(2.0 * self.a_dec * (effective_opp - self.d_min)))
                    vx_cmd = sign * v_cap_lat

                    if u_g[1] < -0.1 and rear_avail > self.d_min:
                        vy_cmd = -min(0.8, math.sqrt(2.0 * self.a_dec * max(0.0, rear_avail - self.d_min)))
                    elif effective_fwd > (self.d_safe + 0.20):
                        vy_cmd = min(1.5, math.sqrt(2.0 * self.a_dec * max(0.0, effective_fwd - self.d_min)))
                    elif effective_fwd > self.d_min:
                        vy_cmd = min(0.4, math.sqrt(2.0 * self.a_dec * max(0.0, effective_fwd - self.d_min)))
                        if self.forward_creep or self.guided_bypass:
                            vy_cmd = max(0.35, vy_cmd)
                    else:
                        if (self.forward_creep or self.guided_bypass) and effective_fwd > 0.25:
                            vy_cmd = 0.35
                        else:
                            vy_cmd = 0.0

                    current_z = float(pos[2])
                    vz_cmd = float(np.clip(2.0 * (self.target_altitude - current_z), -1.0, 1.0))
                    executed_action = np.array([vx_cmd / 3.0, vy_cmd / 3.0, vz_cmd / 3.0, 0.0], dtype=np.float32)
                    executed_action = np.clip(executed_action, -1.0, 1.0)

            # Exit Condition
            else:
                if effective_fwd >= (self.d_safe + 0.15) and clearance >= self.d_safe:
                    self.bypass_clear_consecutive += 1
                else:
                    self.bypass_clear_consecutive = 0

                if not self.guided_bypass:
                    can_exit = (
                        self.reroute_steps >= self.min_reroute_steps
                        and (
                            (u_g[1] >= 0.0 and effective_fwd >= (self.d_safe + 0.15) and clearance >= self.d_safe)
                            or (u_g[1] < 0.0 and rear_avail >= (self.d_safe + 0.15))
                        )
                    )
                else:
                    passed_far_edge = (self.bypass_target_y is not None and pos[1] >= self.bypass_target_y)
                    corridor_clear_run = (self.bypass_clear_consecutive >= 5 and effective_fwd >= 1.5)
                    can_exit = (
                        self.reroute_steps >= self.min_reroute_steps
                        and effective_fwd >= (self.d_safe + 0.15)
                        and clearance >= self.d_safe
                        and (passed_far_edge or corridor_clear_run)
                    )

                if can_exit:
                    self.state = ShieldState.NOMINAL
                    self.cooldown_counter = self.cooldown_steps
                    if not self.anti_amnesia:
                        self.deadlock_attempts = 0
                    gov_action, gov_interv = self._apply_speed_governor(policy_action, clearance, pos)
                    executed_action = gov_action
                    return (executed_action, gov_interv, self.state.value, ttc, clearance, self.standoff_distance, self.stop_latency)
                else:
                    # Active lateral flight with progression
                    sign = -1.0 if self.reroute_direction == "LEFT" else 1.0
                    if effective_lat_clear <= self.d_min:
                        v_cap_lat = 0.0
                    else:
                        v_cap_lat = min(self.v_reroute, math.sqrt(2.0 * self.a_dec * (effective_lat_clear - self.d_min)))
                    vx_cmd = sign * v_cap_lat

                    if u_g[1] < -0.1 and rear_avail > self.d_min:
                        vy_cmd = -min(0.8, math.sqrt(2.0 * self.a_dec * max(0.0, rear_avail - self.d_min)))
                    elif effective_fwd > (self.d_safe + 0.20):
                        vy_cmd = min(1.6, math.sqrt(2.0 * self.a_dec * max(0.0, effective_fwd - self.d_min)))
                    elif effective_fwd > self.d_min:
                        vy_cmd = min(0.4, math.sqrt(2.0 * self.a_dec * max(0.0, effective_fwd - self.d_min)))
                        if self.forward_creep or self.guided_bypass:
                            vy_cmd = max(0.35, vy_cmd)
                    else:
                        if (self.forward_creep or self.guided_bypass) and effective_fwd > 0.25:
                            vy_cmd = 0.35
                        else:
                            vy_cmd = 0.0

                    current_z = float(pos[2])
                    vz_cmd = float(np.clip(2.0 * (self.target_altitude - current_z), -1.0, 1.0))
                    executed_action = np.array([vx_cmd / 3.0, vy_cmd / 3.0, vz_cmd / 3.0, 0.0], dtype=np.float32)
                    executed_action = np.clip(executed_action, -1.0, 1.0)

        elif self.state == ShieldState.RETREAT:
            self.retreat_steps += 1
            intervened = True

            # Check if planner escalation should trigger from retreat
            if self.oracle_planner and self.deadlock_attempts >= 2 and self.retreat_steps >= 4:
                self.state = ShieldState.PLANNER
                self.planned_path = None
                return self._compute_shield_action(policy_action)

            # Back up slightly (-Y) to build standoff distance
            current_z = float(pos[2])
            vz_cmd = float(np.clip(2.0 * (self.target_altitude - current_z), -1.0, 1.0))

            d_south = max(0.0, pos[1] - (-self.arena_y_lim + self.body_radius))
            effective_rear = min(telemetry["rear_clearance"], d_south)

            if effective_rear > self.d_min:
                v_back = min(0.8, math.sqrt(2.0 * self.a_dec * max(0.0, effective_rear - self.d_min)))
                executed_action = np.array([0.0, -v_back / 3.0, vz_cmd / 3.0, 0.0], dtype=np.float32)
            else:
                executed_action = np.zeros(4, dtype=np.float32)

            retreat_limit = 8 if self.deadlock_attempts > 1 else 6
            if self.retreat_steps >= retreat_limit or effective_rear <= self.d_min:
                self.state = ShieldState.SCAN

        return (
            executed_action,
            intervened,
            self.state.value,
            ttc,
            clearance,
            self.standoff_distance,
            self.stop_latency,
        )

    # ── Gymnasium Wrapper Core Overrides ──────────────────────────────────────

    def reset(self, seed: Optional[int] = None, options: Optional[Dict[str, Any]] = None):
        """Resets the environment and the shield internal state."""
        obs, info = self.env.reset(seed=seed, options=options)
        self._reset_shield_state()

        if not self.enabled:
            info["shield_state"] = ShieldState.DISABLED.value
            info["intervened"] = False
        else:
            info["shield_state"] = self.state.value
            info["intervened"] = False

        return obs, info

    def step(self, action: Any):
        """
        Interception step:
        If disabled: behaves as pure pass-through wrapper.
        If enabled: runs FSM, executes governed/rerouted action, populates telemetry in info.
        Never alters observations, reward values, or termination conditions.
        """
        self.current_step += 1
        action = np.nan_to_num(np.asarray(action, dtype=np.float32), nan=0.0, posinf=1.0, neginf=-1.0)
        policy_action = action

        if not self.enabled:
            obs, reward, terminated, truncated, info = self.env.step(policy_action)
            info["shield_state"] = ShieldState.DISABLED.value
            info["policy_action"] = policy_action.copy()
            info["executed_action"] = policy_action.copy()
            info["intervened"] = False
            info["ttc"] = float("inf")
            info["clearance"] = 0.0
            info["standoff_distance"] = 0.0
            info["stop_latency"] = 0
            return obs, reward, terminated, truncated, info

        # Shield is enabled
        (
            executed_action,
            intervened,
            shield_state,
            ttc,
            clearance,
            standoff,
            latency,
        ) = self._compute_shield_action(policy_action)

        obs, reward, terminated, truncated, info = self.env.step(executed_action)

        # Enrich info dictionary with authoritative telemetry
        info["shield_state"] = shield_state
        info["policy_action"] = policy_action.copy()
        info["executed_action"] = executed_action.copy()
        info["intervened"] = bool(intervened)
        info["ttc"] = float(ttc)
        info["clearance"] = float(clearance)
        info["standoff_distance"] = float(standoff)
        info["stop_latency"] = int(latency)

        return obs, reward, terminated, truncated, info

    def __getattr__(self, name: str) -> Any:
        """Transparently delegate any attribute access to the underlying environment."""
        return getattr(self.env, name)

