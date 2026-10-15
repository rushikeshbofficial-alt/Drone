"""
environment.py - Custom Gymnasium Drone Navigation Environment
--------------------------------------------------------------
Physics-Informed Autonomous Drone Navigation in Unstructured 3D Indoor Environments.
Features 240 Hz PyBullet Physics with 24 Hz Gymnasium Control, Monocular RGB-D Vision,
60% ROI Farneback Optical Flow, Bounded Time-to-Collision (tau^-1), and Physics Rewards.
Includes bright, high-contrast 3D Perspective First-Person & Third-Person Renderers.
"""

import math
import numpy as np
import cv2
import gymnasium as gym
from gymnasium import spaces

PYBULLET_AVAILABLE = True
try:
    import pybullet as p
    import pybullet_data
except ImportError:
    PYBULLET_AVAILABLE = False


class IndoorDroneNavEnv(gym.Env):
    """Gymnasium environment for autonomous indoor drone navigation."""
    metadata = {"render_modes": ["human", "rgb_array"], "render_fps": 24}

    def __init__(
        self,
        gui: bool = False,
        seed: int = 42,
        max_steps: int = 500,
        tau_inv_max: float = 5.0,
    ):
        super().__init__()
        self.gui = gui
        self.seed_val = seed
        self.max_steps = max_steps
        self.tau_inv_max = tau_inv_max
        self.current_step = 0
        self.pybullet_active = PYBULLET_AVAILABLE

        # Frequency and Substepping configuration
        self.physics_freq = 240.0
        self.control_freq = 24.0
        self.physics_substeps = int(self.physics_freq / self.control_freq)  # 8 substeps
        self.dt = 1.0 / self.physics_freq

        # Visual camera resolution (84x84)
        self.img_width = 84
        self.img_height = 84
        self.fov = 65.0
        self.aspect = self.img_width / self.img_height
        self.near_val = 0.1
        self.far_val = 12.0

        # Create 60% Central ROI Mask for optical flow calculation
        self.roi_mask = np.zeros((self.img_height, self.img_width), dtype=np.uint8)
        margin_h = int(self.img_height * 0.20)
        margin_w = int(self.img_width * 0.20)
        self.roi_mask[margin_h:self.img_height - margin_h, margin_w:self.img_width - margin_w] = 1
        self.roi_y_slice = slice(margin_h, self.img_height - margin_h)
        self.roi_x_slice = slice(margin_w, self.img_width - margin_w)

        # Precompute unrotated ray direction unit vectors for fast vectorized raycasting
        focal_len = (self.img_width / 2.0) / math.tan(math.radians(self.fov / 2.0))
        px = np.arange(self.img_width, dtype=np.float32)
        py = np.arange(self.img_height, dtype=np.float32)
        px_grid, py_grid = np.meshgrid(px, py)

        ray_dx = (px_grid - self.img_width / 2.0) / focal_len
        ray_dy = np.ones_like(ray_dx)
        ray_dz = -(py_grid - self.img_height / 2.0) / focal_len

        ray_mag = np.sqrt(ray_dx * ray_dx + ray_dy * ray_dy + ray_dz * ray_dz)
        self._unit_rx_unrot = (ray_dx / ray_mag).astype(np.float32)
        self._unit_ry_unrot = (ray_dy / ray_mag).astype(np.float32)
        self._unit_rz = (ray_dz / ray_mag).astype(np.float32)

        self.observation_space = spaces.Dict(
            {
                "visual": spaces.Box(low=-np.inf, high=np.inf, shape=(5, 84, 84), dtype=np.float32),
                "velocity": spaces.Box(low=-10.0, high=10.0, shape=(3,), dtype=np.float32),
            }
        )

        self.action_space = spaces.Box(low=-1.0, high=1.0, shape=(4,), dtype=np.float32)

        if self.pybullet_active:
            try:
                self.client_id = p.connect(p.GUI if self.gui else p.DIRECT)
                p.setAdditionalSearchPath(pybullet_data.getDataPath(), physicsClientId=self.client_id)
            except Exception:
                self.pybullet_active = False

        self.drone_pos = np.array([0.0, -8.0, 1.5], dtype=np.float32)
        self.drone_vel = np.zeros(3, dtype=np.float32)
        self.drone_orn = np.zeros(3, dtype=np.float32)
        self.drone_id = None
        self.obstacle_specs = []
        self.obstacle_ids = []
        self.prev_gray_frame = None
        self.goal_pos = np.array([0.0, 8.0, 1.5], dtype=np.float32)
        self.start_pos = np.array([0.0, -8.0, 1.5], dtype=np.float32)
        self.last_depth_map = None

        self._set_seed(self.seed_val)

    def _set_seed(self, seed: int):
        np.random.seed(seed)

    # Hard arena limits — drone is instantly clamped to these in every substep
    ARENA_X_LIM = 4.6
    ARENA_Y_LIM = 9.6
    ARENA_Z_MIN = 0.15
    ARENA_Z_MAX = 3.5

    def reset(self, seed=None, options=None):
        super().reset(seed=seed)
        if seed is not None:
            self._set_seed(seed)

        self.current_step = 0
        self.out_of_bounds = False          # set True the moment drone hits a wall
        self.drone_pos = self.start_pos.copy()
        self.drone_vel = np.zeros(3, dtype=np.float32)
        self.drone_orn = np.zeros(3, dtype=np.float32)

        if self.pybullet_active:
            p.resetSimulation(physicsClientId=self.client_id)
            p.setGravity(0, 0, -9.81, physicsClientId=self.client_id)
            p.setTimeStep(self.dt, physicsClientId=self.client_id)
            p.loadURDF("plane.urdf", physicsClientId=self.client_id)

            drone_col = p.createCollisionShape(p.GEOM_BOX, halfExtents=[0.2, 0.2, 0.08], physicsClientId=self.client_id)
            drone_vis = p.createVisualShape(p.GEOM_BOX, halfExtents=[0.2, 0.2, 0.08], rgbaColor=[0.1, 0.7, 1.0, 1.0], physicsClientId=self.client_id)
            self.drone_id = p.createMultiBody(
                baseMass=1.0,
                baseCollisionShapeIndex=drone_col,
                baseVisualShapeIndex=drone_vis,
                basePosition=self.start_pos.tolist(),
                physicsClientId=self.client_id
            )

        self._spawn_indoor_obstacles()
        self.prev_gray_frame = None
        self.prev_dist_to_goal = float(np.linalg.norm(self.start_pos - self.goal_pos))
        self.ep_reward_components = {
            "progress": 0.0,
            "goal_vel": 0.0,
            "ttc": 0.0,
            "attitude": 0.0,
            "proximity": 0.0,
            "terminal": 0.0,
        }
        obs = self._get_observation()
        info = {"goal_dist": self.prev_dist_to_goal}
        return obs, info

    def _spawn_indoor_obstacles(self):
        """Spawns 3D indoor obstacle geometries with bright, distinct colors."""
        self._obstacle_ids = []
        self.obstacle_specs = []

        # Room boundary walls (Bright Crisp Light Gray)
        wall_spec = [
            ([5.0, 0.1, 2.0], [0.0, 10.0, 2.0], (220, 220, 220)),
            ([5.0, 0.1, 2.0], [0.0, -10.0, 2.0], (220, 220, 220)),
            ([0.1, 10.0, 2.0], [5.0, 0.0, 2.0], (200, 200, 200)),
            ([0.1, 10.0, 2.0], [-5.0, 0.0, 2.0], (200, 200, 200)),
        ]
        for half_ext, pos, color in wall_spec:
            self.obstacle_specs.append({"type": "box", "half_ext": half_ext, "pos": pos, "color": color})
            if self.pybullet_active:
                col = p.createCollisionShape(p.GEOM_BOX, halfExtents=half_ext, physicsClientId=self.client_id)
                vis = p.createVisualShape(p.GEOM_BOX, halfExtents=half_ext, rgbaColor=[0.85, 0.85, 0.85, 1.0], physicsClientId=self.client_id)
                body = p.createMultiBody(baseMass=0.0, baseCollisionShapeIndex=col, baseVisualShapeIndex=vis, basePosition=pos, physicsClientId=self.client_id)
                self._obstacle_ids.append(body)

        # Dynamic Obstacles: Bright Orange Cylinders & Emerald Green Cuboids
        num_obstacles = np.random.randint(6, 12)
        for _ in range(num_obstacles):
            obs_type = np.random.choice(["cylinder", "box"])
            x = np.random.uniform(-3.5, 3.5)
            y = np.random.uniform(-5.0, 5.0)
            z = np.random.uniform(1.0, 2.5)

            if obs_type == "cylinder":
                radius = np.random.uniform(0.35, 0.65)
                height = np.random.uniform(2.5, 4.0)
                pos = [x, y, height / 2.0]
                # Bright Orange/Coral RGB: (255, 100, 40)
                self.obstacle_specs.append({"type": "cylinder", "radius": radius, "height": height, "pos": pos, "color": (255, 100, 40)})
                if self.pybullet_active:
                    col = p.createCollisionShape(p.GEOM_CYLINDER, radius=radius, height=height, physicsClientId=self.client_id)
                    vis = p.createVisualShape(p.GEOM_CYLINDER, radius=radius, length=height, rgbaColor=[1.0, 0.4, 0.1, 1.0], physicsClientId=self.client_id)
                    body = p.createMultiBody(baseMass=0.0, baseCollisionShapeIndex=col, baseVisualShapeIndex=vis, basePosition=pos, physicsClientId=self.client_id)
                    self._obstacle_ids.append(body)
            else:
                extents = [np.random.uniform(0.35, 0.65) for _ in range(3)]
                pos = [x, y, z]
                # Bright Emerald Green RGB: (40, 220, 110)
                self.obstacle_specs.append({"type": "box", "half_ext": extents, "pos": pos, "color": (40, 220, 110)})
                if self.pybullet_active:
                    col = p.createCollisionShape(p.GEOM_BOX, halfExtents=extents, physicsClientId=self.client_id)
                    vis = p.createVisualShape(p.GEOM_BOX, halfExtents=extents, rgbaColor=[0.1, 0.85, 0.4, 1.0], physicsClientId=self.client_id)
                    body = p.createMultiBody(baseMass=0.0, baseCollisionShapeIndex=col, baseVisualShapeIndex=vis, basePosition=pos, physicsClientId=self.client_id)
                    self._obstacle_ids.append(body)

    def _get_camera_images(self):
        """Renders high-contrast monocular RGB and Depth frames from front-facing camera."""
        if self.pybullet_active:
            pos, orn = p.getBasePositionAndOrientation(self.drone_id, physicsClientId=self.client_id)
            rot_matrix = p.getMatrixFromQuaternion(orn, physicsClientId=self.client_id)
            rot_matrix = np.array(rot_matrix).reshape(3, 3)

            forward = rot_matrix @ np.array([0.0, 1.0, 0.0])
            up = rot_matrix @ np.array([0.0, 0.0, 1.0])
            cam_pos = np.array(pos) + rot_matrix @ np.array([0.0, 0.2, 0.0])
            target_pos = cam_pos + forward

            view_matrix = p.computeViewMatrix(
                cameraEyePosition=cam_pos.tolist(),
                cameraTargetPosition=target_pos.tolist(),
                cameraUpVector=up.tolist(),
                physicsClientId=self.client_id
            )
            proj_matrix = p.computeProjectionMatrixFOV(
                fov=self.fov, aspect=self.aspect, nearVal=self.near_val, farVal=self.far_val, physicsClientId=self.client_id
            )

            _, _, rgb_img, depth_img, _ = p.getCameraImage(
                width=self.img_width,
                height=self.img_height,
                viewMatrix=view_matrix,
                projectionMatrix=proj_matrix,
                renderer=p.ER_TINY_RENDERER,
                physicsClientId=self.client_id
            )

            rgb = np.array(rgb_img, dtype=np.uint8).reshape(self.img_height, self.img_width, 4)[:, :, :3]
            depth_buffer = np.array(depth_img, dtype=np.float32).reshape(self.img_height, self.img_width)
            depth_meters = self.far_val * self.near_val / (self.far_val - (self.far_val - self.near_val) * depth_buffer)
            self.last_depth_map = depth_meters
            return rgb, depth_meters
        else:
            # High-Performance Vectorized NumPy 3D Perspective Raycasting Engine
            # Note: PyBullet is unavailable in this environment (Python 3.12 without C++ build tools),
            # so this analytical raycaster serves as the primary high-fidelity simulation engine.
            cam_x, cam_y, cam_z = float(self.drone_pos[0]), float(self.drone_pos[1]), float(self.drone_pos[2])
            yaw = float(self.drone_orn[2])

            cos_y = math.cos(yaw)
            sin_y = math.sin(yaw)

            rx = self._unit_rx_unrot * cos_y + self._unit_ry_unrot * sin_y
            ry = -self._unit_rx_unrot * sin_y + self._unit_ry_unrot * cos_y
            rz = self._unit_rz

            min_dist = np.full((self.img_height, self.img_width), self.far_val, dtype=np.float32)
            rgb = np.full((self.img_height, self.img_width, 3), (60, 55, 50), dtype=np.uint8)

            # Intersect floor (z=0)
            floor_mask = rz < -1e-4
            t_floor = np.where(floor_mask, -cam_z / np.where(floor_mask, rz, -1.0), self.far_val)
            valid_floor = floor_mask & (t_floor > 0) & (t_floor < min_dist)

            fx = cam_x + rx * t_floor
            fy = cam_y + ry * t_floor
            check = (np.floor(fx).astype(np.int32) + np.floor(fy).astype(np.int32)) % 2

            min_dist = np.where(valid_floor, t_floor, min_dist)
            rgb[valid_floor & (check == 0)] = [230, 230, 230]
            rgb[valid_floor & (check != 0)] = [90, 90, 100]

            # Intersect obstacles
            for spec in self.obstacle_specs:
                ox, oy, oz = spec["pos"]
                dx = cam_x - ox
                dy = cam_y - oy

                if spec["type"] == "cylinder":
                    r = spec["radius"]
                    a = rx * rx + ry * ry
                    b = 2.0 * (dx * rx + dy * ry)
                    c = dx * dx + dy * dy - r * r
                    disc = b * b - 4.0 * a * c
                    cyl_mask = (disc >= 0) & (a > 1e-6)
                    sqrt_disc = np.sqrt(np.maximum(0.0, disc))
                    t_cyl = (-b - sqrt_disc) / (2.0 * a + 1e-8)
                    hit_z = cam_z + rz * t_cyl
                    valid_cyl = cyl_mask & (t_cyl > 0) & (t_cyl < min_dist) & (hit_z >= 0) & (hit_z <= spec["height"])
                    min_dist = np.where(valid_cyl, t_cyl, min_dist)
                    rgb[valid_cyl] = spec["color"]
                else:
                    r_approx = max(spec["half_ext"])
                    dist_to_center = math.hypot(dx, dy)
                    proj = -(dx * rx + dy * ry)
                    perp_sq = np.maximum(0.0, dist_to_center**2 - proj**2)
                    valid_box = (dist_to_center < min_dist + r_approx) & (proj > 0) & (proj < min_dist) & (perp_sq < r_approx**2)
                    min_dist = np.where(valid_box, proj, min_dist)
                    rgb[valid_box] = spec["color"]

            shade = np.maximum(0.45, 1.0 - 0.5 * (min_dist / self.far_val))
            rgb = (rgb * shade[:, :, None]).astype(np.uint8)

            self.last_depth_map = min_dist
            return rgb, min_dist

    def render_overhead_simulation_view(self, out_size=(380, 380)) -> np.ndarray:
        """Renders a 3rd-person isometric/overhead view showing drone and obstacles."""
        view_w, view_h = out_size
        img = np.full((view_h, view_w, 3), (245, 245, 245), dtype=np.uint8)  # Clean bright background

        # Arena bounds: X in [-5, 5], Y in [-10, 10]
        def world_to_img(wx, wy):
            px = int((wx + 5.0) / 10.0 * (view_w - 40) + 20)
            py = int((10.0 - wy) / 20.0 * (view_h - 40) + 20)
            return px, py

        # Draw Arena Grid Lines
        for gx in range(-5, 6, 2):
            p1 = world_to_img(gx, -10.0)
            p2 = world_to_img(gx, 10.0)
            cv2.line(img, p1, p2, (220, 220, 220), 1)

        for gy in range(-10, 11, 2):
            p1 = world_to_img(-5.0, gy)
            p2 = world_to_img(5.0, gy)
            cv2.line(img, p1, p2, (220, 220, 220), 1)

        # Draw Goal Target (Glowing Gold Circle with Pulse)
        goal_px = world_to_img(self.goal_pos[0], self.goal_pos[1])
        cv2.circle(img, goal_px, 14, (0, 215, 255), -1)
        cv2.circle(img, goal_px, 18, (0, 165, 255), 2)
        cv2.putText(img, "GOAL", (goal_px[0] - 18, goal_px[1] + 4), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255, 255, 255), 1)

        # Draw Obstacles (Bright Colors)
        for spec in self.obstacle_specs:
            ox, oy, _ = spec["pos"]
            opx = world_to_img(ox, oy)
            bgr_col = (spec["color"][2], spec["color"][1], spec["color"][0])

            if spec["type"] == "cylinder":
                r_px = max(6, int(spec.get("radius", 0.4) * 20))
                cv2.circle(img, opx, r_px, bgr_col, -1)
                cv2.circle(img, opx, r_px, (40, 40, 40), 1)
            else:
                w_px = max(8, int(spec["half_ext"][0] * 20))
                h_px = max(8, int(spec["half_ext"][1] * 20))
                top_left = (opx[0] - w_px, opx[1] - h_px)
                bot_right = (opx[0] + w_px, opx[1] + h_px)
                cv2.rectangle(img, top_left, bot_right, bgr_col, -1)
                cv2.rectangle(img, top_left, bot_right, (40, 40, 40), 1)

        # Draw Drone Position & Heading Vector
        if self.pybullet_active:
            pos, orn = p.getBasePositionAndOrientation(self.drone_id, physicsClientId=self.client_id)
            d_x, d_y = pos[0], pos[1]
            euler = p.getEulerFromQuaternion(orn, physicsClientId=self.client_id)
            yaw = euler[2]
        else:
            d_x, d_y = self.drone_pos[0], self.drone_pos[1]
            yaw = self.drone_orn[2]

        dpx = world_to_img(d_x, d_y)

        # Draw Drone Quadrotor Frame (Cyan/Blue)
        cv2.circle(img, dpx, 10, (255, 120, 0), -1)
        cv2.circle(img, dpx, 12, (255, 255, 255), 2)

        # Drone Heading Arrow
        hx = dpx[0] + int(20 * math.sin(yaw))
        hy = dpx[1] - int(20 * math.cos(yaw))
        cv2.arrowedLine(img, dpx, (hx, hy), (0, 0, 255), 2, tipLength=0.4)

        return img

    def _compute_optical_flow_and_tau(self, current_gray):
        """Computes fast OpenCV Farneback optical flow and calculates bounded tau^-1 on central 60% ROI."""
        if self.prev_gray_frame is None:
            flow = np.zeros((self.img_height, self.img_width, 2), dtype=np.float32)
            tau_inv_bounded = 0.0
        else:
            flow = cv2.calcOpticalFlowFarneback(
                self.prev_gray_frame,
                current_gray,
                None,
                pyr_scale=0.5,
                levels=2,
                winsize=9,
                iterations=2,
                poly_n=5,
                poly_sigma=1.1,
                flags=0
            )

            u = flow[:, :, 0]
            v = flow[:, :, 1]

            du_dx = cv2.Sobel(u, cv2.CV_32F, 1, 0, ksize=3)
            dv_dy = cv2.Sobel(v, cv2.CV_32F, 0, 1, ksize=3)
            divergence_roi = du_dx[self.roi_y_slice, self.roi_x_slice] + dv_dy[self.roi_y_slice, self.roi_x_slice]
            mean_expansion = float(np.mean(divergence_roi))
            tau_inv_bounded = float(np.clip(np.maximum(0.0, mean_expansion), 0.0, self.tau_inv_max))

        self.prev_gray_frame = current_gray.copy()
        return flow, tau_inv_bounded

    def _get_observation(self):
        rgb, depth = self._get_camera_images()
        gray = cv2.cvtColor(rgb, cv2.COLOR_RGB2GRAY)
        flow, tau_inv = self._compute_optical_flow_and_tau(gray)

        rgb_norm = rgb.astype(np.float32) / 255.0
        flow_u = flow[:, :, 0:1]
        flow_v = flow[:, :, 1:2]

        visual_obs = np.concatenate([rgb_norm, flow_u, flow_v], axis=-1)
        visual_obs = np.transpose(visual_obs, (2, 0, 1)).astype(np.float32)

        if self.pybullet_active:
            vel, _ = p.getBaseVelocity(self.drone_id, physicsClientId=self.client_id)
            vel_vec = np.array(vel, dtype=np.float32)
        else:
            vel_vec = self.drone_vel.copy()

        self.current_tau_inv = tau_inv
        return {"visual": visual_obs, "velocity": vel_vec}

    def _clamp_to_arena(self, pos):
        """Returns (clamped_pos, was_oob). Keeps drone inside hard arena limits."""
        x = float(np.clip(pos[0], -self.ARENA_X_LIM, self.ARENA_X_LIM))
        y = float(np.clip(pos[1], -self.ARENA_Y_LIM, self.ARENA_Y_LIM))
        z = float(np.clip(pos[2],  self.ARENA_Z_MIN,  self.ARENA_Z_MAX))
        oob = (x != float(pos[0])) or (y != float(pos[1])) or (z != float(pos[2]))
        return [x, y, z], oob

    def step(self, action):
        action = np.clip(action, -1.0, 1.0)
        target_vel = action[:3] * 3.0
        yaw_rate = action[3] * 1.0
        self.out_of_bounds = False

        for _ in range(self.physics_substeps):
            if self.pybullet_active:
                p.resetBaseVelocity(
                    self.drone_id,
                    linearVelocity=target_vel.tolist(),
                    angularVelocity=[0.0, 0.0, float(yaw_rate)],
                    physicsClientId=self.client_id
                )
                p.stepSimulation(physicsClientId=self.client_id)
                # Hard clamp position every substep — prevents tunneling regardless of speed
                raw_pos, raw_orn = p.getBasePositionAndOrientation(
                    self.drone_id, physicsClientId=self.client_id
                )
                clamped, oob = self._clamp_to_arena(raw_pos)
                if oob:
                    self.out_of_bounds = True
                    p.resetBasePositionAndOrientation(
                        self.drone_id, clamped, raw_orn, physicsClientId=self.client_id
                    )
                    p.resetBaseVelocity(
                        self.drone_id, [0, 0, 0], [0, 0, 0], physicsClientId=self.client_id
                    )
            else:
                self.drone_vel = target_vel.copy()
                self._drone_orn[2] += yaw_rate * self.dt
                self.drone_pos += self.drone_vel * self.dt
                clamped, oob = self._clamp_to_arena(self.drone_pos)
                if oob:
                    self.out_of_bounds = True
                    self.drone_pos = np.array(clamped, dtype=np.float32)
                    self.drone_vel = np.zeros(3, dtype=np.float32)

        self.current_step += 1
        obs = self._get_observation()

        if self.pybullet_active:
            pos, orn = p.getBasePositionAndOrientation(self.drone_id, physicsClientId=self.client_id)
            pos = np.array(pos, dtype=np.float32)
            euler = p.getEulerFromQuaternion(orn, physicsClientId=self.client_id)
            roll, pitch, yaw = euler[0], euler[1], euler[2]
            contact_points = p.getContactPoints(bodyA=self.drone_id, physicsClientId=self.client_id)
            collision = len(contact_points) > 0
        else:
            pos = self.drone_pos.copy()
            roll, pitch, yaw = self.drone_orn[0], self.drone_orn[1], self.drone_orn[2]
            collision = False
            for spec in self.obstacle_specs:
                ox, oy, _ = spec["pos"]
                dist = np.linalg.norm(pos[:2] - np.array([ox, oy]))
                obs_r = spec.get("radius", 0.4)
                if dist < (obs_r + 0.25):
                    collision = True
                    break

        # Out-of-bounds = wall collision
        if self.out_of_bounds:
            collision = True

        dist_to_goal = float(np.linalg.norm(pos - self.goal_pos))
        goal_reached = dist_to_goal < 0.8

        # Progress reward (positive for moving closer to target)
        if not hasattr(self, "prev_dist_to_goal") or self.prev_dist_to_goal is None:
            self.prev_dist_to_goal = float(np.linalg.norm(self.start_pos - self.goal_pos))

        r_progress = 6.0 * (self.prev_dist_to_goal - dist_to_goal)
        self.prev_dist_to_goal = dist_to_goal

        goal_dir = (self.goal_pos - pos) / (dist_to_goal + 1e-6)

        # Clearance factor based on depth map
        min_depth = self.far_val
        if self.last_depth_map is not None:
            min_depth = float(np.percentile(self.last_depth_map, 5))

        # Gate goal velocity reward by clearance so full-throttle collision rushes are not bribed
        clearance_factor = float(np.clip((min_depth - 0.8) / 1.0, 0.0, 1.0))
        r_goal = 2.5 * float(np.dot(obs["velocity"], goal_dir)) * clearance_factor

        r_ttc = -2.0 * self.current_tau_inv
        r_attitude = -0.5 * (abs(roll) + abs(pitch))

        # Nonlinear quadratic proximity safety penalty:
        # Quadratically penalizes penetrating within 1.2m of obstacles/walls
        # Provides gentle gradient far away, strong quadratic repulsion close up
        r_proximity = 0.0
        if min_depth < 1.2:
            r_proximity = -5.0 * ((1.2 - min_depth) ** 2)

        terminal_reward = 0.0
        terminated = False
        truncated = False

        if collision:
            terminal_reward = -100.0
            terminated = True
        elif goal_reached:
            terminal_reward = 100.0
            terminated = True
        elif self.current_step >= self.max_steps:
            truncated = True

        reward = r_progress + r_goal + r_ttc + r_attitude + r_proximity + terminal_reward

        # Update cumulative episode reward components
        if not hasattr(self, "ep_reward_components"):
            self.ep_reward_components = {"progress": 0.0, "goal_vel": 0.0, "ttc": 0.0, "attitude": 0.0, "proximity": 0.0, "terminal": 0.0}

        self.ep_reward_components["progress"] += r_progress
        self.ep_reward_components["goal_vel"] += r_goal
        self.ep_reward_components["ttc"] += r_ttc
        self.ep_reward_components["attitude"] += r_attitude
        self.ep_reward_components["proximity"] += r_proximity
        self.ep_reward_components["terminal"] += terminal_reward

        info = {
            "dist_to_goal": dist_to_goal,
            "tau_inv": self.current_tau_inv,
            "collision": collision,
            "goal_reached": goal_reached,
            "min_depth": min_depth,
            "reward_components": {
                "step_progress": r_progress,
                "step_goal_vel": r_goal,
                "step_ttc": r_ttc,
                "step_attitude": r_attitude,
                "step_proximity": r_proximity,
                "step_terminal": terminal_reward,
                "ep_progress": self.ep_reward_components["progress"],
                "ep_goal_vel": self.ep_reward_components["goal_vel"],
                "ep_ttc": self.ep_reward_components["ttc"],
                "ep_attitude": self.ep_reward_components["attitude"],
                "ep_proximity": self.ep_reward_components["proximity"],
                "ep_terminal": self.ep_reward_components["terminal"],
            },
        }

        return obs, reward, terminated, truncated, info

    def close(self):
        if self.pybullet_active and p.isConnected(self.client_id):
            p.disconnect(physicsClientId=self.client_id)

    # ── Read-Only Property Accessors (Gate 0 SHR Interface Contracts) ───────────

    @property
    def drone_pos(self) -> np.ndarray:
        """Returns a copy of the drone's world-frame position [x, y, z] in meters."""
        if self.pybullet_active and getattr(self, "drone_id", None) is not None:
            pos, _ = p.getBasePositionAndOrientation(self.drone_id, physicsClientId=self.client_id)
            return np.array(pos, dtype=np.float32)
        val = getattr(self, "_drone_pos", None)
        if val is None:
            return np.array([0.0, -8.0, 1.5], dtype=np.float32)
        return np.array(val, dtype=np.float32, copy=True)

    @drone_pos.setter
    def drone_pos(self, value):
        self._drone_pos = np.array(value, dtype=np.float32)

    @property
    def drone_vel(self) -> np.ndarray:
        """Returns a copy of the drone's world-frame linear velocity [vx, vy, vz] in m/s."""
        if self.pybullet_active and getattr(self, "drone_id", None) is not None:
            vel, _ = p.getBaseVelocity(self.drone_id, physicsClientId=self.client_id)
            return np.array(vel, dtype=np.float32)
        val = getattr(self, "_drone_vel", None)
        if val is None:
            return np.zeros(3, dtype=np.float32)
        return np.array(val, dtype=np.float32, copy=True)

    @drone_vel.setter
    def drone_vel(self, value):
        self._drone_vel = np.array(value, dtype=np.float32)

    @property
    def drone_orientation(self) -> np.ndarray:
        """
        Returns a copy of the drone's orientation.
        In PyBullet mode: quaternion [x, y, z, w].
        In analytical mode: Euler angles [roll, pitch, yaw] in radians.
        """
        if self.pybullet_active and getattr(self, "drone_id", None) is not None:
            _, orn = p.getBasePositionAndOrientation(self.drone_id, physicsClientId=self.client_id)
            return np.array(orn, dtype=np.float32)
        val = getattr(self, "_drone_orn", None)
        if val is None:
            return np.zeros(3, dtype=np.float32)
        return np.array(val, dtype=np.float32, copy=True)

    @property
    def drone_orn(self) -> np.ndarray:
        """Returns a copy of the drone's Euler angles [roll, pitch, yaw] in radians."""
        if self.pybullet_active and getattr(self, "drone_id", None) is not None:
            _, orn = p.getBasePositionAndOrientation(self.drone_id, physicsClientId=self.client_id)
            euler = p.getEulerFromQuaternion(orn, physicsClientId=self.client_id)
            return np.array(euler, dtype=np.float32)
        val = getattr(self, "_drone_orn", None)
        if val is None:
            return np.zeros(3, dtype=np.float32)
        return np.array(val, dtype=np.float32, copy=True)

    @drone_orn.setter
    def drone_orn(self, value):
        self._drone_orn = np.array(value, dtype=np.float32)

    @property
    def last_depth_image(self) -> np.ndarray:
        """Returns a copy of the latest raw camera depth map in meters (84x84 float32)."""
        val = getattr(self, "_last_depth_map", None)
        if val is None:
            return np.full((self.img_height, self.img_width), self.far_val, dtype=np.float32)
        return np.array(val, dtype=np.float32, copy=True)

    @property
    def last_depth_map(self):
        """Returns a copy of the latest raw depth map or None if uninitialized."""
        val = getattr(self, "_last_depth_map", None)
        if val is None:
            return None
        return np.array(val, dtype=np.float32, copy=True)

    @last_depth_map.setter
    def last_depth_map(self, value):
        self._last_depth_map = value

    @property
    def obstacle_ids(self) -> list:
        """Returns a copy of the list of obstacle IDs."""
        val = getattr(self, "_obstacle_ids", None)
        if val is None:
            return []
        return list(val)

    @obstacle_ids.setter
    def obstacle_ids(self, value):
        self._obstacle_ids = list(value)

    @property
    def obstacle_positions(self) -> list:
        """Returns a list of obstacle center positions [(x, y, z), ...] as float32 numpy arrays."""
        return [np.array(spec["pos"], dtype=np.float32, copy=True) for spec in getattr(self, "obstacle_specs", [])]

    @property
    def obstacle_geometries(self) -> list:
        """Returns a deep copy of obstacle specification dictionaries."""
        import copy
        return copy.deepcopy(getattr(self, "obstacle_specs", []))

    @property
    def goal_position(self) -> np.ndarray:
        """Returns a copy of the goal position [x, y, z] in meters."""
        return np.array(self.goal_pos, dtype=np.float32, copy=True)

    @property
    def start_position(self) -> np.ndarray:
        """Returns a copy of the start position [x, y, z] in meters."""
        return np.array(self.start_pos, dtype=np.float32, copy=True)

    @property
    def arena_bounds(self) -> dict:
        """Returns the hard arena limits."""
        return {
            "x_lim": self.ARENA_X_LIM,
            "y_lim": self.ARENA_Y_LIM,
            "z_min": self.ARENA_Z_MIN,
            "z_max": self.ARENA_Z_MAX,
        }

