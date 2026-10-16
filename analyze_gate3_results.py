import json
import numpy as np

with open('reports/gate3_heldout_v2_compare.json') as f:
    v2_comp = json.load(f)

with open('reports/gate3_heldout_v1_oracle.json') as f:
    v1_ora = json.load(f)

base = v2_comp['configurations']['baseline']
ora_v2 = v2_comp['configurations']['shield_oracle']
cam_v2 = v2_comp['configurations']['shield_camera']
ora_v1 = list(v1_ora['configurations'].values())[0]

print('=== 1. SUMMARY RATES (5000-5049) ===')
for name, cfg in [('Baseline (OFF)', base), ('Shield v1 (Oracle)', ora_v1), ('Shield v2 (Oracle)', ora_v2), ('Shield v2 (Camera)', cam_v2)]:
    succ = cfg['rates']['SUCCESS']['formatted']
    col = cfg['rates']['TOTAL_COLLISION']['formatted']
    obs = cfg['rates']['OBSTACLE_COLLISION']['formatted']
    wall = cfg['rates']['WALL_OOB']['formatted']
    to = cfg['rates']['TIMEOUT']['formatted']
    rew = f"{cfg['statistics']['mean_reward']:.2f} +/- {cfg['statistics']['std_reward']:.2f}"
    steps = f"{cfg['statistics']['mean_steps']:.1f}"
    clr = f"{cfg['statistics']['mean_min_clearance']:.2f} m"
    interv = f"{cfg['statistics']['mean_interventions_pct']:.1f}%"
    standoff = f"{cfg['statistics']['mean_standoff_distance']:.2f} m"
    print(f'{name}:')
    print(f'  Success: {succ} | Col: {col} (Obs: {obs}, Wall: {wall}) | Timeout: {to}')
    print(f'  Reward: {rew} | Steps: {steps} | Clearance: {clr} | Interv: {interv} | Standoff: {standoff}')

print('\n=== 2. A* FALLBACK (PLANNER) INVOCATIONS ===')
planner_eps_v2 = [ep['seed'] for ep in ora_v2['episodes'] if ep['state_counts'].get('PLANNER', 0) > 0]
planner_steps_v2 = [ep['state_counts'].get('PLANNER', 0) for ep in ora_v2['episodes'] if ep['state_counts'].get('PLANNER', 0) > 0]
print(f'Held-out (5000-5049) Oracle v2 Planner invocations: {len(planner_eps_v2)}/50 ({len(planner_eps_v2)/50*100:.1f}%)')
print(f'  Seeds: {planner_eps_v2}')
print(f'  Steps per invocation: {planner_steps_v2}')

# Check which seeds timed out in v1:
v1_timeouts = [ep['seed'] for ep in ora_v1['episodes'] if ep['outcome'] == 'TIMEOUT']
print(f'\nv1 Timeouts on 5000-5049: {len(v1_timeouts)}/50: {v1_timeouts}')
print('Did v2 planner trigger on these v1 timeouts?')
for s in v1_timeouts:
    ep_v2 = next(ep for ep in ora_v2['episodes'] if ep['seed'] == s)
    print(f'  Seed {s}: v2 outcome={ep_v2["outcome"]}, steps={ep_v2["steps"]}, planner_steps={ep_v2["state_counts"].get("PLANNER", 0)}')

print('\n=== 3. BASELINE-SUCCEEDING EPISODES & OVERHEAD ===')
base_succ_eps = [ep for ep in base['episodes'] if ep['outcome'] == 'SUCCESS']
print(f'Baseline success count: {len(base_succ_eps)}/50')
base_succ_seeds = [ep['seed'] for ep in base_succ_eps]
print(f'Baseline succeeding seeds: {base_succ_seeds}')

base_steps_map = {ep['seed']: ep['steps'] for ep in base_succ_eps}
ora_v2_map = {ep['seed']: ep for ep in ora_v2['episodes']}
ora_v1_map = {ep['seed']: ep for ep in ora_v1['episodes']}

base_succ_steps = [ep['steps'] for ep in base_succ_eps]
print(f'Baseline mean steps on successful eps: {np.mean(base_succ_steps):.2f} +/- {np.std(base_succ_steps):.2f}')

oh_v2 = []
oh_v1 = []
print(f'{"Seed":5s} | {"Base Steps":10s} | {"v1 Steps (OH%)":18s} | {"v2 Steps (OH%)":18s} | {"v2 Interv%":10s} | {"v2 Standoff":11s}')
print('-' * 85)
for s in base_succ_seeds:
    bs = base_steps_map[s]
    v2_s = ora_v2_map[s]['steps']
    v1_s = ora_v1_map[s]['steps']
    pct_v2 = ((v2_s - bs) / bs) * 100.0
    pct_v1 = ((v1_s - bs) / bs) * 100.0
    oh_v2.append(pct_v2)
    oh_v1.append(pct_v1)
    print(f'{s:5d} | {bs:10d} | {v1_s:8d} ({pct_v1:+6.1f}%) | {v2_s:8d} ({pct_v2:+6.1f}%) | {ora_v2_map[s]["interventions_pct"]:9.1f}% | {ora_v2_map[s]["standoff_distance"]:10.2f}m')

print('-' * 85)
print(f'Mean Overhead v2 on Baseline Successes: {np.mean(oh_v2):.2f}% +/- {np.std(oh_v2):.2f}% (median: {np.median(oh_v2):.2f}%)')
print(f'Mean Overhead v1 on Baseline Successes: {np.mean(oh_v1):.2f}% +/- {np.std(oh_v1):.2f}% (median: {np.median(oh_v1):.2f}%)')

print(f'\nv2 Steps on Baseline Successes: mean {np.mean([ora_v2_map[s]["steps"] for s in base_succ_seeds]):.2f}')
print(f'v1 Steps on Baseline Successes: mean {np.mean([ora_v1_map[s]["steps"] for s in base_succ_seeds]):.2f}')

# Acceptance criteria checks
print('\n=== 4. ACCEPTANCE CRITERIA VERIFICATION ===')
tot_col_v2 = ora_v2['rates']['TOTAL_COLLISION']['rate']
to_v2 = ora_v2['rates']['TIMEOUT']['rate']
succ_v2 = ora_v2['rates']['SUCCESS']['rate']
mean_oh_v2 = np.mean(oh_v2)
mean_standoff_v2 = ora_v2['statistics']['mean_standoff_distance']

crit = [
    ('Total Collisions <= 2.0%', f'{tot_col_v2:.1f}%', tot_col_v2 <= 2.0),
    ('Timeout Rate <= 5.0%', f'{to_v2:.1f}%', to_v2 <= 5.0),
    ('Success Rate >= 85.0%', f'{succ_v2:.1f}%', succ_v2 >= 85.0),
    ('Step Overhead <= 15.0%', f'{mean_oh_v2:.2f}%', mean_oh_v2 <= 15.0),
    ('Standoff Distance >= 0.45 m', f'{mean_standoff_v2:.2f} m', mean_standoff_v2 >= 0.45)
]

for name, val, passed in crit:
    status = 'PASSED' if passed else 'FAILED'
    print(f'{name:30s} | Achieved: {val:10s} | Status: {status}')

print('\n=== 5. DETAILED STATE BREAKDOWN ON THE 14 BASELINE SUCCESSES ===')
print(f'{"Seed":5s} | {"BaseSteps":9s} | {"v2Steps":7s} | {"NOMINAL":7s} | {"BRAKE":5s} | {"SCAN":4s} | {"REROUTE":7s} | {"RETREAT":7s} | {"PLANNER":7s} | {"Interv%":7s}')
print('-' * 85)
for s in base_succ_seeds:
    b_ep = next(e for e in base_succ_eps if e['seed'] == s)
    v_ep = next(e for e in ora_v2['episodes'] if e['seed'] == s)
    sc = v_ep['state_counts']
    print(f'{s:5d} | {b_ep["steps"]:9d} | {v_ep["steps"]:7d} | {sc.get("NOMINAL",0):7d} | {sc.get("BRAKE",0):5d} | {sc.get("SCAN",0):4d} | {sc.get("REROUTE",0):7d} | {sc.get("RETREAT",0):7d} | {sc.get("PLANNER",0):7d} | {v_ep["interventions_pct"]:6.1f}%')
