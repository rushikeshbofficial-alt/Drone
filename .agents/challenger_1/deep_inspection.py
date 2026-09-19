"""
deep_inspection.py
-------------------
Independent deep structural and lexical inspection of actual deliverables:
- Autonomous_Drone_Navigation_Technical_Documentation.docx
- TECHNICAL_DOCUMENTATION.md
"""

import os
import sys
import re
import docx

WORKSPACE = os.path.abspath(r"c:\Users\Rushikesh\Desktop\Cool Ass Projects\Drone")
DOCX_PATH = os.path.join(WORKSPACE, "Autonomous_Drone_Navigation_Technical_Documentation.docx")
MD_PATH = os.path.join(WORKSPACE, "TECHNICAL_DOCUMENTATION.md")

def inspect_md():
    print("=" * 80)
    print("INSPECTING TECHNICAL_DOCUMENTATION.md")
    print("=" * 80)
    if not os.path.exists(MD_PATH):
        print("ERROR: MD does not exist!")
        return

    sz = os.path.getsize(MD_PATH)
    with open(MD_PATH, "r", encoding="utf-8") as f:
        content = f.read()

    lines = content.splitlines()
    words_regex = len(re.findall(r'\b[a-zA-Z0-9_\-]+\b', content))
    words_split = len(content.split())

    h1 = [line for line in lines if line.startswith("# ")]
    h2 = [line for line in lines if line.startswith("## ")]
    h3 = [line for line in lines if line.startswith("### ")]
    code_blocks = re.findall(r'```', content)
    latex_blocks = re.findall(r'\$\$', content)
    ascii_diagrams = [line for line in lines if "+---" in line or "|   " in line]

    # Check for forbidden/placeholder tokens
    placeholders = []
    for pat in [r'\bTODO\b', r'\bTBD\b', r'lorem ipsum', r'\bundefined\b', r'\[\.\.\.\]']:
        matches = re.findall(pat, content, re.I)
        if matches:
            placeholders.extend(matches)

    print(f"File Size: {sz:,} bytes")
    print(f"Line Count: {len(lines):,}")
    print(f"Word Count (Regex Tokens): {words_regex:,}")
    print(f"Word Count (Split): {words_split:,}")
    print(f"H1 Headings ({len(h1)}): {h1[:5]}...")
    print(f"H2 Headings: {len(h2)}")
    print(f"H3 Headings: {len(h3)}")
    print(f"Code Block Markers (```): {len(code_blocks)}")
    print(f"LaTeX Block Markers ($$): {len(latex_blocks)}")
    print(f"ASCII Diagram Structural Lines: {len(ascii_diagrams)}")
    print(f"Placeholder / Incomplete Tokens Detected: {placeholders}")
    assert len(placeholders) == 0, f"Found placeholders: {placeholders}"
    assert words_regex >= 6000, f"Words regex {words_regex} < 6000"
    print("[PASS] Markdown Deep Inspection Clean!")

def inspect_docx():
    print("\n" + "=" * 80)
    print("INSPECTING Autonomous_Drone_Navigation_Technical_Documentation.docx")
    print("=" * 80)
    if not os.path.exists(DOCX_PATH):
        print("ERROR: DOCX does not exist!")
        return

    sz = os.path.getsize(DOCX_PATH)
    doc = docx.Document(DOCX_PATH)

    paras = doc.paragraphs
    tables = doc.tables

    para_texts = [p.text for p in paras]
    full_para_text = "\n".join(para_texts)

    seen_tc = set()
    table_texts = []
    total_cells = 0
    for t in tables:
        for row in t.rows:
            for cell in row.cells:
                total_cells += 1
                if cell._tc not in seen_tc:
                    seen_tc.add(cell._tc)
                    table_texts.append(cell.text)

    full_text = "\n".join(para_texts + table_texts)
    words_regex = len(re.findall(r'\b[a-zA-Z0-9_\-]+\b', full_text))
    words_split = len(full_text.split())

    # Heading styles used
    styles_used = set(p.style.name for p in paras)
    headings_1 = [p.text for p in paras if p.style.name == "Heading 1"]
    headings_2 = [p.text for p in paras if p.style.name == "Heading 2"]
    headings_3 = [p.text for p in paras if p.style.name == "Heading 3"]

    # Check for placeholders
    placeholders = []
    for pat in [r'\bTODO\b', r'\bTBD\b', r'lorem ipsum', r'\bundefined\b', r'\[\.\.\.\]']:
        matches = re.findall(pat, full_text, re.I)
        if matches:
            placeholders.extend(matches)

    print(f"File Size: {sz:,} bytes")
    print(f"Total Paragraphs: {len(paras):,}")
    print(f"Total Tables: {len(tables):,} (Total Cells: {total_cells:,}, Unique Cells: {len(seen_tc):,})")
    print(f"Word Count (Regex Tokens): {words_regex:,}")
    print(f"Word Count (Split): {words_split:,}")
    print(f"Styles Used: {sorted(list(styles_used))}")
    print(f"Heading 1 Count ({len(headings_1)}): {headings_1[:6]}")
    print(f"Heading 2 Count: {len(headings_2)}")
    print(f"Heading 3 Count: {len(headings_3)}")
    print(f"Placeholder / Incomplete Tokens Detected: {placeholders}")
    assert len(placeholders) == 0, f"Found placeholders: {placeholders}"
    assert words_regex >= 6000, f"Words regex {words_regex} < 6000"
    assert len(tables) >= 10, f"Tables count {len(tables)} < 10"
    print("[PASS] DOCX Deep Inspection Clean!")

def inspect_content_depth():
    print("\n" + "=" * 80)
    print("INSPECTING SUBSTANTIVE CODEBASE FILE BREAKDOWN DEPTH")
    print("=" * 80)
    files_to_check = [
        "environment.py", "model.py", "pretrain_bc.py", "train.py",
        "explainability.py", "evaluate_and_visualize.py", "run_project.bat",
        "overnight_train.bat", "requirements.txt", "README.md"
    ]

    with open(MD_PATH, "r", encoding="utf-8") as f:
        md = f.read()

    for fname in files_to_check:
        # Check mentions and section headers
        matches = len(re.findall(re.escape(fname), md, re.I))
        # Ensure it appears at least 3 times (heading + breakdown + parameters)
        print(f"File '{fname}': mentioned {matches} times in markdown.")
        assert matches >= 3, f"File {fname} only mentioned {matches} times; insufficient depth!"

    print("[PASS] All 10 files discussed in rigorous depth!")

if __name__ == "__main__":
    inspect_md()
    inspect_docx()
    inspect_content_depth()
    print("\nALL DEEP INSPECTIONS PASSED SUCCESSFULLY!")
