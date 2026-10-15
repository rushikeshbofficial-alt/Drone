"""
stress_test_shield.py - Adversarial Stress & Fuzz Testing Harness for SHR Drone Safety Shield
---------------------------------------------------------------------------------------------
Empirical Challenger 1 Suite for Gate 1 Verification.

Tests:
1. Corner Trap Stress Test:
   - Command drone toward arena corners (X=4.5, Y=9.5, etc.) at maximum speed (+3.0 m/s).
   - Test multiple starting points (center, intermediate, extreme boundary proximity).
   - Verify speed governor and wall capping prevent wall penetration / out-of-bounds collision.
   - Body surface must never penetrate arena boundary (|x| + 0.20 <= 4.601, |y| + 0.20 <= 9.601).

2. Rapid Action Oscillation Stress Test:
   - Command alternating maximum actions [+1, +1, 0, 0] and [-1, -1, 0, 0] at 24 Hz near an obstacle.
   - Verify stability (no NaN/Inf, altitude maintained), zero collisions, and hysteresis chattering suppression.

3. High-Speed Head-On Impact Test:
   - Force maximum velocity +3.0 m/s directly toward obstacle centers across multiple seeds & obstacle types.
   - Verify active zero-action stop triggers, stops before obstacle, and maintains standoff >= 0.45 m.

4. Random Action Fuzzing (500 steps):
   - 500 steps of random uniform actions [-1, 1]^4 with StopAndRerouteShield(env, sensor_mode="oracle").
   - Verify 0 collisions and that all telemetry fields in info are valid floats/bools without NaN or Inf.

5. Enabled=False Bit-Exact Fuzzing (100 steps):
   - 100 steps of random actions comparing raw unshielded environment vs shield with enabled=False.
   - Verify byte-identical observations, identical rewards, identical terminations, and disabled telemetry contract.
"""

import math
import unittest
from typing import Dict, List, Optional, Tuple, Any
import numpy as np

from environment import IndoorDroneNavEnv
from drone_shield import (
    StopAndRerouteShield,
    ShieldState,
    point_obstacle_distance_2d,
    cast_ray_oracle,
)

try:
    import pybullet as p
    PYBULLET_AVAILABLE = True
except ImportError:
    PYBULLET_AVAILABLE = False


def set_drone_kinematics(env: IndoorDroneNavEnv, pos: List[float], vel: List[float]) -> None:
    """Safely updates drone position and velocity in PyBullet or analytical mode."""
    if getattr(env, "pybullet_active", False) and PYBULLET_AVAILABLE:
        p.resetBasePositionAndOrientation(
            env.drone_id, pos, [0.0, 0.0, 0.0, 1.0], physicsClientId=env.client_id
        )
        p.resetBaseVelocity(
            env.drone_id, vel, [0.0, 0.0, 0.0], physicsClientId=env.client_id
        )
    else:
        env.drone_pos = np.array(pos, dtype=np.float32)
        env.drone_vel = np.array(vel, dtype=np.float32)


class TestCornerTrapStress(unittest.TestCase):
    """
    Test 1: Corner trap stress test.
    Place or command drone towards arena corner (e.g. X=4.5, Y=9.5) at high speed (3.0 m/s).
    Verify the shield speed governor and wall capping prevent wall penetration / out-of-bounds collision.
    """

    def test_corner_trap_escape_and_wall_capping(self):
        corners_to_test = [
            ("North-East (+X, +Y)", [1.0, 1.0, 0.0, 0.0], [0.0, 0.0, 1.5]),
            ("North-East near wall", [1.0, 1.0, 0.0, 0.0], [4.0, 9.0, 1.5]),
            ("North-East near threshold", [1.0, 1.0, 0.0, 0.0], [4.3, 9.3, 1.5]),
            ("North-West (-X, +Y)", [-1.0, 1.0, 0.0, 0.0], [-4.0, 9.0, 1.5]),
            ("South-East (+X, -Y)", [1.0, -1.0, 0.0, 0.0], [4.0, -9.0, 1.5]),
            ("South-West (-X, -Y)", [-1.0, -1.0, 0.0, 0.0], [-4.0, -9.0, 1.5]),
        ]

        for desc, action_cmd, start_pos in corners_to_test:
            with self.subTest(scenario=desc, start_pos=start_pos):
                env = IndoorDroneNavEnv(gui=False, seed=42, max_steps=120)
                shield = StopAndRerouteShield(env, sensor_mode="oracle", enabled=True)
                obs, info = shield.reset(seed=42)
                set_drone_kinematics(env, start_pos, [0.0, 0.0, 0.0])
                shield._reset_shield_state()

                action = np.array(action_cmd, dtype=np.float32)
                collided = False
                max_x = -float("inf")
                min_x = float("inf")
                max_y = -float("inf")
                min_y = float("inf")
                governor_interventions = 0

                for step in range(80):
                    obs, reward, terminated, truncated, info = shield.step(action)
                    pos = shield.drone_pos

                    max_x = max(max_x, float(pos[0]))
                    min_x = min(min_x, float(pos[0]))
                    max_y = max(max_y, float(pos[1]))
                    min_y = min(min_y, float(pos[1]))

                    if info.get("intervened", False):
                        governor_interventions += 1

                    if info.get("collision", False) or (terminated and not info.get("goal_reached", False)):
                        collided = True
                        break

                shield.close()

                # Assertions
                self.assertFalse(collided, f"Collision detected in corner trap scenario: {desc}")
                self.assertGreater(governor_interventions, 0, f"Speed governor should intervene in {desc}")

                # Effective body extent check: body radius is 0.20m, arena boundaries are [-4.6, 4.6] and [-9.6, 9.6]
                self.assertLessEqual(
                    max_x + 0.20,
                    4.601,
                    f"East wall penetrated: max_x={max_x:.3f} + 0.20 = {max_x + 0.20:.3f} > 4.60",
                )
                self.assertGreaterEqual(
                    min_x - 0.20,
                    -4.601,
                    f"West wall penetrated: min_x={min_x:.3f} - 0.20 = {min_x - 0.20:.3f} < -4.60",
                )
                self.assertLessEqual(
                    max_y + 0.20,
                    9.601,
                    f"North wall penetrated: max_y={max_y:.3f} + 0.20 = {max_y + 0.20:.3f} > 9.60",
                )
                self.assertGreaterEqual(
                    min_y - 0.20,
                    -9.601,
                    f"South wall penetrated: min_y={min_y:.3f} - 0.20 = {min_y - 0.20:.3f} < -9.60",
                )


class TestRapidActionOscillationStress(unittest.TestCase):
    """
    Test 2: Rapid action oscillation stress test.
    Command alternating maximum actions [+1, +1, 0, 0] and [-1, -1, 0, 0] at 24 Hz near an obstacle.
    Verify the shield maintains stability, doesn't crash into obstacle, and hysteresis prevents chattering.
    """

    def test_rapid_action_oscillation_near_obstacle(self):
        seeds_to_test = [101, 202, 303]

        for seed in seeds_to_test:
            with self.subTest(seed=seed):
                env = IndoorDroneNavEnv(gui=False, seed=seed, max_steps=150)
                shield = StopAndRerouteShield(env, sensor_mode="oracle", enabled=True)
                obs, info = shield.reset(seed=seed)

                # Find first interior obstacle (index >= 4)
                interior_obs = [s for s in env.obstacle_specs[4:] if abs(s["pos"][0]) < 3.5 and abs(s["pos"][1]) < 7.5]
                self.assertGreater(len(interior_obs), 0, f"Seed {seed} must contain interior obstacles")
                target_obs = interior_obs[0]
                ox, oy, _ = target_obs["pos"]
                r_obs = float(target_obs.get("radius", 0.4)) if target_obs.get("type") == "cylinder" else float(target_obs.get("half_ext", [0.4, 0.4, 0.4])[1])

                # Position drone 0.85m standoff in front of obstacle along -Y
                standoff_init = 0.85
                start_y = oy - (r_obs + 0.20 + standoff_init)
                start_x = ox
                set_drone_kinematics(env, [start_x, start_y, 1.5], [0.0, 0.0, 0.0])
                shield._reset_shield_state()

                act_pos = np.array([1.0, 1.0, 0.0, 0.0], dtype=np.float32)
                act_neg = np.array([-1.0, -1.0, 0.0, 0.0], dtype=np.float32)

                collided = False
                min_surface_dist = float("inf")
                state_history = []

                for step in range(100):
                    action = act_pos if (step % 2 == 0) else act_neg
                    obs, reward, terminated, truncated, info = shield.step(action)
                    pos = shield.drone_pos
                    vel = shield.drone_vel

                    # Stability check: no NaN or Inf in position or velocity
                    self.assertFalse(np.isnan(pos).any(), f"NaN in drone_pos at step {step}")
                    self.assertFalse(np.isinf(pos).any(), f"Inf in drone_pos at step {step}")
                    self.assertFalse(np.isnan(vel).any(), f"NaN in drone_vel at step {step}")
                    self.assertFalse(np.isinf(vel).any(), f"Inf in drone_vel at step {step}")

                    # Altitude stability check
                    self.assertGreaterEqual(float(pos[2]), 0.8, f"Altitude dropped too low at step {step}: {pos[2]}")
                    self.assertLessEqual(float(pos[2]), 2.5, f"Altitude climbed too high at step {step}: {pos[2]}")

                    # Surface distance to target obstacle
                    center_dist = math.hypot(pos[0] - ox, pos[1] - oy)
                    surface_dist = center_dist - (r_obs + 0.20)
                    min_surface_dist = min(min_surface_dist, surface_dist)

                    state_history.append(info["shield_state"])

                    if info.get("collision", False) or (terminated and not info.get("goal_reached", False)):
                        collided = True
                        break

                shield.close()

                self.assertFalse(collided, f"Collision occurred during rapid oscillation on seed {seed}")
                self.assertGreater(min_surface_dist, 0.0, f"Drone penetrated obstacle boundary on seed {seed}")

                # Verify hysteresis / chattering suppression:
                # Without cooldown/hysteresis, a naive controller would flip states every single step (100 flips in 100 steps).
                # The SHR shield must maintain stable state sequences.
                transitions = sum(1 for i in range(1, len(state_history)) if state_history[i] != state_history[i - 1])
                self.assertLess(
                    transitions,
                    45,
                    f"Excessive state chattering detected on seed {seed}: {transitions} transitions in 100 steps",
                )


class TestHighSpeedHeadOnImpact(unittest.TestCase):
    """
    Test 3: High-speed head-on impact test.
    Force maximum velocity +3.0 m/s directly toward an obstacle center.
    Verify active zero-action stop triggers and stops before obstacle surface, maintaining standoff >= 0.45 m.
    """

    def test_head_on_impact_standoff(self):
        seeds_to_test = [101, 202, 303, 404, 505]
        standoff_records = []
        total_trials = 0

        for seed in seeds_to_test:
            env = IndoorDroneNavEnv(gui=False, seed=seed, max_steps=60)
            shield = StopAndRerouteShield(env, sensor_mode="oracle", enabled=True)
            obs, info = shield.reset(seed=seed)

            interior_obs = [s for s in env.obstacle_specs[4:] if abs(s["pos"][0]) < 3.2 and abs(s["pos"][1]) < 7.0]

            for obs_idx, target_obs in enumerate(interior_obs[:2]):
                ox, oy, _ = target_obs["pos"]
                obs_type = target_obs.get("type", "box")
                if obs_type == "cylinder":
                    r_obs = float(target_obs["radius"])
                else:
                    r_obs = float(target_obs["half_ext"][1])

                for approach_dist in [1.8, 2.5, 3.2]:
                    start_y = oy - (r_obs + 0.20 + approach_dist)
                    start_x = ox
                    start_pos = [start_x, start_y, 1.5]

                    # Ensure start position is clear of boundary walls and other obstacles
                    if abs(start_x) > 4.1 or abs(start_y) > 9.0:
                        continue
                    if point_obstacle_distance_2d(np.array(start_pos, dtype=np.float32), env.obstacle_specs, r_drone=0.20) < 0.25:
                        continue

                    total_trials += 1
                    # Force maximum initial velocity +3.0 m/s directly toward obstacle
                    set_drone_kinematics(env, start_pos, [0.0, 3.0, 0.0])
                    shield._reset_shield_state()

                    action = np.array([0.0, 1.0, 0.0, 0.0], dtype=np.float32)
                    collided = False
                    stopped = False
                    measured_standoff = None

                    for step in range(30):
                        obs, reward, terminated, truncated, info = shield.step(action)
                        pos = shield.drone_pos
                        vel = shield.drone_vel
                        speed = math.hypot(vel[0], vel[1])

                        if obs_type == "cylinder":
                            center_dist = math.hypot(pos[0] - ox, pos[1] - oy)
                            surface_dist = center_dist - (r_obs + 0.20)
                        else:
                            dx = max(0.0, abs(pos[0] - ox) - target_obs["half_ext"][0])
                            dy = max(0.0, abs(pos[1] - oy) - target_obs["half_ext"][1])
                            surface_dist = math.hypot(dx, dy) - 0.20

                        if info.get("collision", False):
                            collided = True
                            break

                        if info["shield_state"] in (ShieldState.BRAKE.value, ShieldState.SCAN.value) and not stopped:
                            if speed < 0.08:
                                stopped = True
                                measured_standoff = surface_dist
                                standoff_records.append(surface_dist)

                        if stopped and step > 6:
                            break

                    self.assertFalse(
                        collided,
                        f"Collision in head-on test: seed={seed}, obs={obs_idx}, approach={approach_dist}m",
                    )
                    self.assertTrue(
                        stopped,
                        f"Failed to achieve full stop: seed={seed}, obs={obs_idx}, approach={approach_dist}m",
                    )
                    self.assertIsNotNone(measured_standoff)
                    self.assertGreaterEqual(
                        measured_standoff,
                        0.45,
                        f"Standoff violation! Measured {measured_standoff:.4f}m < 0.45m on seed {seed}, obs {obs_idx}",
                    )

            shield.close()

        self.assertGreater(total_trials, 5, "Must test at least 5 head-on approach trials")
        min_so = min(standoff_records)
        mean_so = np.mean(standoff_records)
        print(f"\n[Test 3 Summary] Head-on trials: {total_trials}, All stopped, Min standoff: {min_so:.4f}m, Mean standoff: {mean_so:.4f}m (Target: >= 0.45m)")


class TestRandomActionFuzzing(unittest.TestCase):
    """
    Test 4: Random action fuzzing.
    Run 500 steps of random uniform actions [-1, 1]^4 with StopAndRerouteShield(env, sensor_mode="oracle").
    Verify 0 collisions and that all telemetry fields in info are valid floats/bools without NaN or infinite values.
    """

    def test_random_fuzzing_500_steps(self):
        env = IndoorDroneNavEnv(gui=False, seed=42, max_steps=600)
        shield = StopAndRerouteShield(env, sensor_mode="oracle", enabled=True)
        obs, info = shield.reset(seed=42)

        np.random.seed(424242)

        required_telemetry_keys = [
            "shield_state",
            "policy_action",
            "executed_action",
            "intervened",
            "ttc",
            "clearance",
            "standoff_distance",
            "stop_latency",
            "dist_to_goal",
            "tau_inv",
            "collision",
            "goal_reached",
            "min_depth",
        ]

        total_collisions = 0
        collision_details = []
        episodes = 1

        for step in range(500):
            action = np.random.uniform(-1.0, 1.0, size=4).astype(np.float32)
            obs, reward, terminated, truncated, info = shield.step(action)

            # Check collision
            if info.get("collision", False):
                total_collisions += 1
                collision_details.append({
                    "step": step,
                    "pos": shield.drone_pos.tolist(),
                    "vel": shield.drone_vel.tolist(),
                    "state": info.get("shield_state"),
                    "action": action.tolist(),
                })

            # Validate all required telemetry fields
            for key in required_telemetry_keys:
                self.assertIn(key, info, f"Missing telemetry key '{key}' at step {step}")
                val = info[key]

                if key in ("intervened", "collision", "goal_reached"):
                    self.assertIsInstance(val, (bool, np.bool_), f"Key {key} must be bool at step {step}")
                elif key == "shield_state":
                    self.assertIsInstance(val, str)
                    self.assertIn(val, [s.value for s in ShieldState])
                elif key in ("policy_action", "executed_action"):
                    self.assertIsInstance(val, np.ndarray)
                    self.assertEqual(val.shape, (4,))
                    self.assertFalse(np.isnan(val).any(), f"NaN in {key} at step {step}")
                    self.assertFalse(np.isinf(val).any(), f"Inf in {key} at step {step}")
                elif key == "stop_latency":
                    self.assertIsInstance(val, (int, np.integer))
                    self.assertGreaterEqual(val, 0)
                else:
                    self.assertIsInstance(val, (float, np.floating, int))
                    self.assertFalse(math.isnan(float(val)), f"NaN in {key} at step {step}")
                    self.assertFalse(math.isinf(float(val)), f"Infinite value in {key} at step {step}")

            if terminated or truncated:
                episodes += 1
                obs, info = shield.reset(seed=42 + episodes)

        shield.close()

        if total_collisions > 0:
            print(f"\n[Test 4 Failure Trace] Total collisions: {total_collisions}")
            for c in collision_details:
                print(f"  Step {c['step']}: state={c['state']} pos={c['pos']} vel={c['vel']} cmd_act={c['action']}")

        self.assertEqual(
            total_collisions,
            0,
            f"Collisions occurred during 500-step random fuzzing: {total_collisions}. "
            f"Collisions: {collision_details}",
        )
        print(f"\n[Test 4 Summary] 500-step random fuzzing completed across {episodes} episodes with 0 collisions and 100% valid finite telemetry.")

    def test_horizontal_fuzzing_500_steps(self):
        """
        Diagnostic isolation test:
        Demonstrates that when vz=0 (horizontal 2D motion), the shield achieves 0 collisions over 500 steps,
        confirming that the failure in test_random_fuzzing_500_steps is specifically due to unconstrained
        vertical descent/climb in NOMINAL state.
        """
        env = IndoorDroneNavEnv(gui=False, seed=42, max_steps=600)
        shield = StopAndRerouteShield(env, sensor_mode="oracle", enabled=True)
        shield.reset(seed=42)
        np.random.seed(424242)

        collisions = 0
        for step in range(500):
            action = np.array([
                np.random.uniform(-1.0, 1.0),
                np.random.uniform(-1.0, 1.0),
                0.0,  # Zero vertical action
                np.random.uniform(-1.0, 1.0),
            ], dtype=np.float32)

            obs, reward, terminated, truncated, info = shield.step(action)
            if info.get("collision", False):
                collisions += 1

            if terminated or truncated:
                shield.reset(seed=42 + step)

        shield.close()
        self.assertEqual(collisions, 0, f"Horizontal fuzzing experienced {collisions} collisions")
        print("\n[Diagnostic Test 4B] Horizontal-only (vz=0) fuzzing achieved 0 collisions across 500 steps.")

    def test_vertical_boundary_vulnerability(self):
        """
        Adversarial vulnerability test:
        Demonstrates that in NOMINAL state, commanding downward flight action [0, 0, -1, 0]
        results in a floor collision at z=0.15m because the speed governor in drone_shield.py
        does not govern vz against arena vertical limits (z_min=0.15, z_max=3.5).
        """
        env = IndoorDroneNavEnv(gui=False, seed=42, max_steps=50)
        shield = StopAndRerouteShield(env, sensor_mode="oracle", enabled=True)
        shield.reset(seed=42)

        action_down = np.array([0.0, 0.0, -1.0, 0.0], dtype=np.float32)
        floor_collided = False
        hit_step = None

        for step in range(25):
            obs, reward, terminated, truncated, info = shield.step(action_down)
            pos = shield.drone_pos
            if info.get("collision", False):
                floor_collided = True
                hit_step = step
                break

        shield.close()
        print(f"\n[Diagnostic Test 4C] Downward action [0, 0, -1, 0] hit floor collision: {floor_collided} at step {hit_step} (z={pos[2]:.3f})")
        # As an empirical challenger, we assert whether vertical protection exists:
        self.assertFalse(floor_collided, f"Floor collision occurred at step {hit_step} (z={pos[2]:.3f}) under negative vz in NOMINAL state!")


class TestPassThroughFuzzing(unittest.TestCase):
    """
    Test 5: Enabled=False bit-exact fuzzing across 100 steps.
    Verify byte-identical observations, actions, rewards, and terminations between raw env and shield wrapper.
    """

    def test_enabled_false_bit_exact_100_steps(self):
        env_raw = IndoorDroneNavEnv(gui=False, seed=888, max_steps=120)
        env_shield_off = StopAndRerouteShield(
            IndoorDroneNavEnv(gui=False, seed=888, max_steps=120),
            enabled=False,
        )

        obs_raw, info_raw = env_raw.reset(seed=888)
        obs_off, info_off = env_shield_off.reset(seed=888)

        np.testing.assert_array_equal(obs_raw["visual"], obs_off["visual"])
        np.testing.assert_array_equal(obs_raw["velocity"], obs_off["velocity"])
        self.assertEqual(info_off["shield_state"], ShieldState.DISABLED.value)
        self.assertFalse(info_off["intervened"])

        np.random.seed(888123)

        for step in range(100):
            action = np.random.uniform(-1.0, 1.0, size=4).astype(np.float32)

            o_raw, r_raw, term_raw, trunc_raw, i_raw = env_raw.step(action)
            o_off, r_off, term_off, trunc_off, i_off = env_shield_off.step(action)

            # Bit-exact checks
            np.testing.assert_array_equal(
                o_raw["visual"],
                o_off["visual"],
                err_msg=f"Visual observation mismatch at step {step}",
            )
            np.testing.assert_array_equal(
                o_raw["velocity"],
                o_off["velocity"],
                err_msg=f"Velocity observation mismatch at step {step}",
            )
            self.assertEqual(r_raw, r_off, f"Reward mismatch at step {step}: {r_raw} != {r_off}")
            self.assertEqual(term_raw, term_off, f"Termination mismatch at step {step}")
            self.assertEqual(trunc_raw, trunc_off, f"Truncation mismatch at step {step}")

            # Telemetry checks in disabled mode
            self.assertEqual(i_off["shield_state"], ShieldState.DISABLED.value)
            self.assertFalse(i_off["intervened"])
            np.testing.assert_array_equal(i_off["policy_action"], action)
            np.testing.assert_array_equal(i_off["executed_action"], action)

            # Underlying env info keys must match
            for k in ["dist_to_goal", "tau_inv", "collision", "goal_reached", "min_depth"]:
                self.assertEqual(i_raw[k], i_off[k], f"Info key {k} mismatch at step {step}")

            if term_raw or trunc_raw:
                seed = 888 + step + 1
                obs_raw, info_raw = env_raw.reset(seed=seed)
                obs_off, info_off = env_shield_off.reset(seed=seed)
                np.testing.assert_array_equal(obs_raw["visual"], obs_off["visual"])
                np.testing.assert_array_equal(obs_raw["velocity"], obs_off["velocity"])

        env_raw.close()
        env_shield_off.close()
        print("\n[Test 5 Summary] Enabled=False 100-step bit-exact fuzzing passed with 100% mathematical identity.")


if __name__ == "__main__":
    unittest.main(verbosity=2)
