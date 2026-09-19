"""
Independent OpenXML and Structural Deep-Inspection Script for Autonomous Drone Navigation Documentation.
Executed by Reviewer 2.
"""

import os
import sys
import io

# Force UTF-8 on Windows stdout
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

import docx
from docx import Document
from docx.oxml import parse_xml
import re
import xml.etree.ElementTree as ET
import zipfile

DOCX_PATH = r"c:\Users\Rushikesh\Desktop\Cool Ass Projects\Drone\Autonomous_Drone_Navigation_Technical_Documentation.docx"
MD_PATH = r"c:\Users\Rushikesh\Desktop\Cool Ass Projects\Drone\TECHNICAL_DOCUMENTATION.md"

def inspect():
    print(f"Loading {DOCX_PATH} via python-docx...")
    doc = Document(DOCX_PATH)
    print("Document successfully loaded without exception.")

    # 1. Inspect Sections, Page Setup and Geometry
    print("\n--- 1. SECTION & GEOMETRY INSPECTION ---")
    print(f"Number of sections: {len(doc.sections)}")
    for i, sec in enumerate(doc.sections):
        print(f"  Section {i}: TopMargin={sec.top_margin.inches}in, BottomMargin={sec.bottom_margin.inches}in, "
              f"LeftMargin={sec.left_margin.inches}in, RightMargin={sec.right_margin.inches}in, "
              f"PageWidth={sec.page_width.inches}in, PageHeight={sec.page_height.inches}in")
        footer = sec.footer
        print(f"  Footer paragraphs: {len(footer.paragraphs)}")
        for fp in footer.paragraphs:
            print(f"    Footer text: '{fp.text}', alignment: {fp.alignment}")
            # Check for PAGE and NUMPAGES fields in footer xml
            footer_xml = fp._p.xml
            has_page = 'w:instr="PAGE"' in footer_xml
            has_numpages = 'w:instr="NUMPAGES"' in footer_xml
            print(f"    Dynamic Page Numbers: PAGE field={has_page}, NUMPAGES field={has_numpages}")

    # 2. Inspect Paragraphs
    print("\n--- 2. PARAGRAPH INSPECTION ---")
    paragraphs = doc.paragraphs
    print(f"Total top-level paragraphs: {len(paragraphs)}")
    styles_used = set(p.style.name for p in paragraphs)
    print(f"Paragraph styles detected: {sorted(list(styles_used))}")

    # Inspect Heading counts
    headings_h1 = []
    headings_h2 = []
    headings_h3 = []
    bullet_count = 0
    body_count = 0
    for p in paragraphs:
        text = p.text.strip()
        if not text:
            continue
        runs = p.runs
        if runs:
            first_run = runs[0]
            if p.runs and p.runs[0].bold and p.runs[0].font.size and p.runs[0].font.size.pt >= 16:
                headings_h1.append(text)
            elif p.runs and p.runs[0].bold and p.runs[0].font.size and p.runs[0].font.size.pt >= 13:
                headings_h2.append(text)
            elif p.runs and p.runs[0].bold and p.runs[0].font.size and p.runs[0].font.size.pt >= 11.4:
                headings_h3.append(text)
        if p.style.name == 'List Bullet':
            bullet_count += 1
        else:
            body_count += 1

    print(f"H1 Headings detected ({len(headings_h1)}):")
    for h in headings_h1:
        print(f"  - {h}")
    print(f"H2 Headings detected ({len(headings_h2)}):")
    for h in headings_h2:
        print(f"  - {h}")
    print(f"Bullet count: {bullet_count}")

    # 3. Inspect Tables (including Callouts and Code blocks)
    print("\n--- 3. TABLE INSPECTION ---")
    tables = doc.tables
    print(f"Total tables: {len(tables)}")
    
    callouts = []
    code_blocks = []
    data_tables = []
    
    for idx, tbl in enumerate(tables):
        rows = len(tbl.rows)
        cols = len(tbl.columns)
        tbl_xml = tbl._tbl.tblPr.xml
        
        # Check if 1x1
        if rows == 1 and cols == 1:
            cell_text = tbl.cell(0, 0).text
            if 'w:val="single" w:sz="28"' in tbl_xml or "■" in cell_text:
                callouts.append((idx, cell_text[:80].replace('\n', ' ')))
            else:
                code_blocks.append((idx, cell_text[:80].replace('\n', ' ')))
        else:
            headers = [c.text.strip().replace('\n', ' ') for c in tbl.rows[0].cells]
            data_tables.append((idx, rows, cols, headers))

    print(f"Data tables count: {len(data_tables)}")
    for t in data_tables:
        print(f"  Table idx {t[0]}: {t[1]} rows x {t[2]} cols | Headers: {t[3]}")

    print(f"\nCallouts count: {len(callouts)}")
    for c in callouts:
        print(f"  Callout idx {c[0]}: {c[1]}")

    print(f"\nCode blocks count: {len(code_blocks)}")
    for cb in code_blocks:
        print(f"  Code block idx {cb[0]}: {cb[1]}")

    # 4. Word Counts & Text Density Analysis
    print("\n--- 4. WORD COUNT & TEXT ANALYSIS ---")
    para_text = [p.text for p in paragraphs]
    table_text = []
    seen_tc = set()
    for tbl in tables:
        for row in tbl.rows:
            for cell in row.cells:
                if cell._tc not in seen_tc:
                    seen_tc.add(cell._tc)
                    table_text.append(cell.text)

    full_docx_text = "\n".join(para_text + table_text)
    
    wc_regex_alnum = len(re.findall(r'\b[a-zA-Z0-9_\-]+\b', full_docx_text))
    wc_whitespace = len(full_docx_text.split())
    wc_words_only = len(re.findall(r'\b[a-zA-Z]+\b', full_docx_text))
    
    print(f"DOCX Word Count (Alphanumeric regex): {wc_regex_alnum:,}")
    print(f"DOCX Word Count (Whitespace split): {wc_whitespace:,}")
    print(f"DOCX Word Count (Alphabetic only): {wc_words_only:,}")
    print(f"DOCX Total Character Count: {len(full_docx_text):,}")

    with open(MD_PATH, "r", encoding="utf-8") as f:
        md_text = f.read()
    md_wc_regex = len(re.findall(r'\b[a-zA-Z0-9_\-]+\b', md_text))
    md_wc_split = len(md_text.split())
    print(f"\nMarkdown Word Count (Alphanumeric regex): {md_wc_regex:,}")
    print(f"Markdown Word Count (Whitespace split): {md_wc_split:,}")
    print(f"Combined Word Count (Alphanumeric regex): {wc_regex_alnum + md_wc_regex:,}")

    # 5. OpenXML Zip Package Integrity
    print("\n--- 5. OPENXML ZIP PACKAGE INTEGRITY ---")
    with zipfile.ZipFile(DOCX_PATH, 'r') as z:
        namelist = z.namelist()
        print(f"Total files in DOCX OpenXML container: {len(namelist)}")
        required_parts = [
            "[Content_Types].xml",
            "_rels/.rels",
            "word/document.xml",
            "word/styles.xml",
            "word/footer1.xml"
        ]
        for part in required_parts:
            present = part in namelist
            print(f"  Part '{part}': {'PRESENT' if present else 'MISSING'}")
            if present:
                part_data = z.read(part)
                try:
                    ET.fromstring(part_data)
                    print(f"    -> Valid XML ({len(part_data):,} bytes)")
                except Exception as e:
                    print(f"    -> XML PARSE ERROR: {e}")

    # 6. Audited Codebase Coverage in DOCX
    print("\n--- 6. AUDITED CODEBASE COVERAGE IN DOCX ---")
    files_to_check = [
        "environment.py", "model.py", "pretrain_bc.py", "train.py",
        "explainability.py", "evaluate_and_visualize.py", "run_project.bat",
        "overnight_train.bat", "requirements.txt", "README.md"
    ]
    for fn in files_to_check:
        occurrences = len(re.findall(r'\b' + re.escape(fn) + r'\b', full_docx_text, re.I))
        print(f"  {fn:<28}: {occurrences} occurrences")

    # 7. Math Formulation Coverage in DOCX
    print("\n--- 7. MATHEMATICAL FORMULATION COVERAGE IN DOCX ---")
    math_checks = [
        ("TTC / tau^-1", r'(\\tau\^\{-?1\}|tau\^?-?1|τ⁻¹|tau_inv|inverse\s+time-to-collision|time-to-collision)'),
        ("Farneback Optical Flow", r'(farneback|calcopticalflowfarneback|gunnar\s+farneback)'),
        ("Potential Field Vectors", r'(potential\s+field|tangential\s+(?:obstacle\s+)?steering|attractive\s+force|repulsive\s+force)'),
        ("PPO Objective & GAE", r'(ppo|gae|clipped\s+surrogate|generalized\s+advantage\s+estimation|surr1|surr2|l\^?\{?clip\}?)'),
        ("Spatial IoU Explanation Fidelity", r'(spatial\s+iou|explanation\s+fidelity|intersection\s+over\s+union)'),
    ]
    for label, pat in math_checks:
        matches = re.findall(pat, full_docx_text, re.I)
        print(f"  {label:<35}: {len(matches)} matches")

if __name__ == "__main__":
    inspect()
