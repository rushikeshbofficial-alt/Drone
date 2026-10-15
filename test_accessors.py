"""
test_accessors.py - Unit tests verifying read-only @property accessors in environment.py
Verifies:
- All required accessors return correct types, shapes, and units.
- Every accessor returns a defensive copy (mutating returned value does not mutate env state).
- Accessors have zero side effects on environment step, dynamics, rewards, or termination.
"""

import unittest
import numpy as np
from environment import IndoorDroneNavEnv


class TestPropertyAccessors(unittest.TestCase):

    def setUp(self):
        self.env = IndoorDroneNavEnv(gui=False, seed=42, max_steps=100)
        self.env.reset(seed=42)

    def tearDown(self):
        self.env.close()

    def test_drone_pos_accessor(self):
        pos = self.env.drone_pos
        self.assertIsInstance(pos, np.ndarray)
        self.assertEqual(pos.shape, (3,))
        self.assertEqual(pos.dtype, np.float32)
        np.testing.assert_allclose(pos, np.array([0.0, -8.0, 1.5], dtype=np.float32))

        # Test defensive copy (immutability of internal state)
        pos[0] = 999.0
        self.assertNotEqual(self.env.drone_pos[0], 999.0)
        self.assertEqual(self.env.drone_pos[0], 0.0)

    def test_drone_vel_accessor(self):
        vel = self.env.drone_vel
        self.assertIsInstance(vel, np.ndarray)
        self.assertEqual(vel.shape, (3,))
        self.assertEqual(vel.dtype, np.float32)

        # Step with forward velocity
        self.env.step(np.array([0.0, 1.0, 0.0, 0.0], dtype=np.float32))
        vel2 = self.env.drone_vel
        self.assertAlmostEqual(float(vel2[1]), 3.0, places=4)

        # Test defensive copy
        vel2[1] = -999.0
        self.assertNotEqual(self.env.drone_vel[1], -999.0)

    def test_drone_orientation_accessor(self):
        orn = self.env.drone_orientation
        self.assertIsInstance(orn, np.ndarray)
        self.assertIn(orn.shape, [(3,), (4,)])
        self.assertEqual(orn.dtype, np.float32)

        # Test defensive copy
        orn[0] = 999.0
        self.assertNotEqual(self.env.drone_orientation[0], 999.0)

    def test_last_depth_image_accessor(self):
        depth = self.env.last_depth_image
        self.assertIsInstance(depth, np.ndarray)
        self.assertEqual(depth.shape, (84, 84))
        self.assertEqual(depth.dtype, np.float32)
        self.assertTrue(np.all(depth >= 0.05))
        self.assertTrue(np.all(depth <= 12.0))

        # Test defensive copy
        depth[0, 0] = -999.0
        self.assertNotEqual(self.env.last_depth_image[0, 0], -999.0)

    def test_obstacle_accessors(self):
        obs_ids = self.env.obstacle_ids
        self.assertIsInstance(obs_ids, list)

        obs_positions = self.env.obstacle_positions
        self.assertIsInstance(obs_positions, list)
        self.assertGreater(len(obs_positions), 0)
        for p in obs_positions:
            self.assertEqual(p.shape, (3,))
            self.assertEqual(p.dtype, np.float32)

        # Defensive copy check
        orig_x = obs_positions[0][0]
        obs_positions[0][0] = 999.0
        self.assertEqual(self.env.obstacle_positions[0][0], orig_x)

    def test_meta_accessors(self):
        goal = self.env.goal_position
        self.assertEqual(goal.shape, (3,))
        self.assertEqual(goal.dtype, np.float32)
        np.testing.assert_allclose(goal, [0.0, 8.0, 1.5])

        start = self.env.start_position
        self.assertEqual(start.shape, (3,))
        self.assertEqual(start.dtype, np.float32)
        np.testing.assert_allclose(start, [0.0, -8.0, 1.5])

        bounds = self.env.arena_bounds
        self.assertIn("x_lim", bounds)
        self.assertIn("y_lim", bounds)
        self.assertIn("z_min", bounds)
        self.assertIn("z_max", bounds)
        self.assertEqual(bounds["x_lim"], 4.6)
        self.assertEqual(bounds["y_lim"], 9.6)

    def test_zero_side_effects_on_step(self):
        """Verify that accessing properties during rollouts does not alter episode trajectory or rewards."""
        env1 = IndoorDroneNavEnv(gui=False, seed=101, max_steps=50)
        env2 = IndoorDroneNavEnv(gui=False, seed=101, max_steps=50)

        obs1, _ = env1.reset(seed=101)
        obs2, _ = env2.reset(seed=101)

        fixed_action = np.array([0.2, 0.8, -0.1, 0.05], dtype=np.float32)

        for step in range(20):
            # env1: only step
            o1, r1, term1, trunc1, info1 = env1.step(fixed_action)

            # env2: step AND aggressively read all properties
            _ = env2.drone_pos
            _ = env2.drone_vel
            _ = env2.drone_orientation
            _ = env2.last_depth_image
            _ = env2.obstacle_positions
            _ = env2.arena_bounds
            o2, r2, term2, trunc2, info2 = env2.step(fixed_action)
            _ = env2.drone_pos
            _ = env2.drone_vel

            np.testing.assert_allclose(o1["visual"], o2["visual"], err_msg=f"Visual obs mismatch at step {step}")
            np.testing.assert_allclose(o1["velocity"], o2["velocity"], err_msg=f"Velocity mismatch at step {step}")
            self.assertEqual(r1, r2, f"Reward mismatch at step {step}")
            self.assertEqual(term1, term2, f"Termination mismatch at step {step}")
            self.assertEqual(trunc1, trunc2, f"Truncation mismatch at step {step}")

        env1.close()
        env2.close()

    def test_analytical_mode_yaw_update(self):
        """Verify that yaw rate actions genuinely update internal orientation in analytical mode."""
        initial_yaw = float(self.env.drone_orn[2])
        action = np.array([0.0, 0.0, 0.0, 1.0], dtype=np.float32)  # 1.0 rad/s yaw rate
        self.env.step(action)
        updated_yaw = float(self.env.drone_orn[2])
        expected_yaw_change = 1.0 * self.env.dt * self.env.physics_substeps
        self.assertAlmostEqual(updated_yaw - initial_yaw, expected_yaw_change, places=4)

    def test_internal_obstacle_registration_and_isolation(self):
        """Verify that _obstacle_ids list is properly initialized and isolated."""
        self.assertIsInstance(self.env._obstacle_ids, list)
        self.assertEqual(self.env.obstacle_ids, self.env._obstacle_ids)
        self.assertIsNot(self.env.obstacle_ids, self.env._obstacle_ids)


if __name__ == "__main__":
    unittest.main()
