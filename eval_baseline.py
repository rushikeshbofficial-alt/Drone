"""
eval_baseline.py - Detailed Evaluation Script
Records exact behavioral metrics for BC baseline and PPO checkpoints.
"""
import os
import json
import torch
import numpy as np
from environment import IndoorDroneNavEnv
from model import PhysicsInformedActorCritic

def eval_checkpoint(ckpt_path, seeds_dict):
    device = 'cuda' if torch.cuda.is_available() else 'cpu'
    model = PhysicsInformedActorCritic().to(device)
    model.load_state_dict(torch.load(ckpt_path, map_location=device, weights_only=True))
    model.eval()

    output = {}

    for set_name, seeds in seeds_dict.items():
        results = []
        all_steering = []
        all_throttle = []

        for seed in seeds:
            env = IndoorDroneNavEnv(gui=False, seed=seed, max_steps=500)
            obs, info = env.reset(seed=seed)
            ep_rew = 0.0
            steps = 0
            min_clearance = float('inf')
            ep_steer = []
            ep_throttle = []

            while True:
                vis_t = torch.tensor(obs['visual'], dtype=torch.float32, device=device).unsqueeze(0)
                vel_t = torch.tensor(obs['velocity'], dtype=torch.float32, device=device).unsqueeze(0)
                with torch.no_grad():
                    act = model(vis_t, vel_t).squeeze(0).cpu().numpy()

                ep_steer.append(float(act[0]))
                ep_throttle.append(float(act[1]))
                all_steering.append(float(act[0]))
                all_throttle.append(float(act[1]))

                obs, rew, term, trunc, sinfo = env.step(act)
                ep_rew += rew
                steps += 1
                if 'min_depth' in sinfo:
                    min_clearance = min(min_clearance, float(sinfo['min_depth']))

                if term or trunc:
                    is_success = bool(sinfo.get('goal_reached', False))
                    is_collision = bool(sinfo.get('collision', False))
                    status = 'SUCCESS' if is_success else ('COLLISION' if is_collision else 'TIMEOUT')
                    results.append({
                        'seed': seed,
                        'status': status,
                        'success': 1.0 if is_success else 0.0,
                        'collision': 1.0 if is_collision else 0.0,
                        'steps': steps,
                        'reward': float(ep_rew),
                        'goal_dist': float(sinfo.get('dist_to_goal', 0.0)),
                        'min_clearance': float(min_clearance) if min_clearance != float('inf') else 0.0,
                        'steer_mean': float(np.mean(ep_steer)),
                        'steer_std': float(np.std(ep_steer)),
                        'steer_abs_mean': float(np.mean(np.abs(ep_steer))),
                        'throttle_mean': float(np.mean(ep_throttle)),
                        'throttle_std': float(np.std(ep_throttle)),
                    })
                    env.close()
                    break

        succ_rate = float(np.mean([r['success'] for r in results]) * 100)
        coll_rate = float(np.mean([r['collision'] for r in results]) * 100)
        mean_len = float(np.mean([r['steps'] for r in results]))
        mean_dist = float(np.mean([r['goal_dist'] for r in results]))
        mean_rew = float(np.mean([r['reward'] for r in results]))
        std_rew = float(np.std([r['reward'] for r in results]))
        mean_min_clear = float(np.mean([r['min_clearance'] for r in results]))

        output[set_name] = {
            'success_rate': succ_rate,
            'collision_rate': coll_rate,
            'mean_episode_length': mean_len,
            'final_goal_distance': mean_dist,
            'mean_reward': mean_rew,
            'std_reward': std_rew,
            'mean_min_clearance': mean_min_clear,
            'steering_mean': float(np.mean(all_steering)),
            'steering_std': float(np.std(all_steering)),
            'steering_abs_mean': float(np.mean(np.abs(all_steering))),
            'throttle_mean': float(np.mean(all_throttle)),
            'throttle_std': float(np.std(all_throttle)),
            'per_seed': results
        }

    return output

if __name__ == '__main__':
    import sys
    ckpt = sys.argv[1] if len(sys.argv) > 1 else 'bc_25k_clean.pt'
    seeds = {
        'training': [42, 142, 242, 342, 442],
        'unseen': [101, 202, 303, 404, 505]
    }
    res = eval_checkpoint(ckpt, seeds)
    print(json.dumps(res, indent=2))
