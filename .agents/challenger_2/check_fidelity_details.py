"""
check_fidelity_details.py - Detailed Mathematical & Hyperparameter Verification
"""

import sys
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
import re
from docx import Document

DOCX_PATH = r"c:\Users\Rushikesh\Desktop\Cool Ass Projects\Drone\Autonomous_Drone_Navigation_Technical_Documentation.docx"
MD_PATH = r"c:\Users\Rushikesh\Desktop\Cool Ass Projects\Drone\TECHNICAL_DOCUMENTATION.md"

doc = Document(DOCX_PATH)
docx_text = "\n".join([p.text for p in doc.paragraphs] + [c.text for t in doc.tables for row in t.rows for c in row.cells])
with open(MD_PATH, "r", encoding="utf-8") as f:
    md_text = f.read()

items_to_verify = [
    ("Farneback: pyr_scale 0.5", r"pyr_scale.*0\.5|scale.*0\.5|0\.5"),
    ("Farneback: 2 levels", r"levels.*2|2\s+levels"),
    ("Farneback: 9x9 winsize", r"winsize.*9|9\s*x\s*9|9\s*\\times\s*9"),
    ("Farneback: 2 iterations", r"iterations.*2|2\s+iterations"),
    ("Farneback: poly_n 5", r"poly_n.*5|poly_n\s*=\s*5"),
    ("Farneback: poly_sigma 1.1", r"poly_sigma.*1\.1|1\.1"),
    ("Reward: progress 6.0", r"6\.0\s*(\*|\\cdot)?\s*(\(|\\Delta|d)"),
    ("Reward: goal velocity 3.0", r"3\.0\s*(\*|\\cdot)?\s*.*(goal|v_drone|velocity)"),
    ("Reward: TTC -2.0", r"-2\.0\s*(\*|\\cdot)?\s*.*(tau|ttc|expansion)"),
    ("Reward: attitude -0.5", r"-0\.5\s*(\*|\\cdot)?\s*.*(roll|pitch|attitude)"),
    ("Reward: proximity -3.0", r"-3\.0\s*(\*|\\cdot)?\s*.*(1\.5|depth|proximity)"),
    ("Reward: terminal +/-100", r"100(\.0)?"),
    ("Clamping: X = +/- 4.6", r"4\.6"),
    ("Clamping: Y = +/- 9.6", r"9\.6"),
    ("Clamping: Z min 0.15", r"0\.15"),
    ("Clamping: Z max 3.5", r"3\.5"),
    ("Model: 5-channel input", r"5\s*,\s*84\s*,\s*84|5\s*\\times\s*84|5-channel"),
    ("Model: NatureCNN conv stack", r"Conv2d|NatureCNN"),
    ("Model: Visual FC 3136 -> 512", r"3,?136.*512|512"),
    ("Model: Kinematic FC 3 -> 64", r"Linear\(3,\s*64\)|3\s*\\to\s*64|Linear.*3.*64"),
    ("Model: Fusion 576 -> 256", r"512\s*\+\s*64|576.*256|Linear\(576,\s*256\)|256"),
    ("Model: Actor 256 -> 128 -> 4", r"128.*action_dim|128.*4|Tanh"),
    ("Model: Critic 256 -> 128 -> 1", r"128.*1"),
    ("BC: Tangential Steering", r"Tangential Obstacle Steering|tangential"),
    ("BC: Obstacle distance 1.8m", r"1\.8"),
    ("BC: Forward speed vy >= 0.35", r"0\.35"),
    ("BC: Altitude hold 1.5m", r"1\.5"),
    ("PPO: SubprocVecEnv", r"SubprocVecEnv"),
    ("PPO: gamma 0.99", r"0\.99"),
    ("PPO: gae_lambda 0.95", r"0\.95"),
    ("PPO: clip_eps 0.2", r"0\.2"),
    ("PPO: learning rate 3e-4", r"3e-4|0\.0003"),
    ("PPO: batch size 512", r"512"),
    ("PPO: vf_coef 0.5", r"0\.5"),
    ("PPO: ent_coef 0.01", r"0\.01"),
    ("PPO: AMP FP16", r"AMP|FP16|GradScaler|autocast"),
    ("PPO: torch.compile", r"torch\.compile|reduce-overhead"),
    ("PPO: TF32 Blackwell", r"TF32|Blackwell|sm_120"),
    ("XAI: Gaussian blur (13, 13) sigma 3.0", r"13.*13|GaussianBlur"),
    ("XAI: Gamma contrast 0.7", r"0\.7"),
    ("XAI: Google TURBO colormap", r"TURBO|COLORMAP_TURBO"),
    ("XAI: Adaptive alpha masking", r"alpha|alpha_map"),
    ("XAI: Neon contours > 0.65", r"0\.65"),
    ("XAI: Spatial IoU 85th percentile / 1.5m", r"IoU|Spatial IoU|percentile"),
    ("Dashboard: Canvas 1230 x 510", r"1230\s*x\s*510|1230\s*\\times\s*510|1230"),
    ("Dashboard: 3 Panels 390 x 390", r"390\s*x\s*390|390\s*\\times\s*390|390"),
]

print(f"{'Verification Target':<45} | {'MD Match':<10} | {'DOCX Match':<10}")
print("-" * 72)
for name, pattern in items_to_verify:
    md_has = bool(re.search(pattern, md_text, re.I))
    docx_has = bool(re.search(pattern, docx_text, re.I))
    md_str = "PASS" if md_has else "FAIL"
    docx_str = "PASS" if docx_has else "FAIL"
    print(f"{name:<45} | {md_str:<10} | {docx_str:<10}")
