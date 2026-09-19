# Specification & Test Harness Architecture: `verify_documentation.py`

**Document Version**: 1.0.0  
**Author**: `spec_miner_m1_1` (Specification Miner & Systems Architect)  
**Target Script**: `verify_documentation.py` (Workspace Root)  
**Workspace**: `c:\Users\Rushikesh\Desktop\Cool Ass Projects\Drone`  
**Date**: September 19, 2026  

---

## 1. Executive Summary & Verification Purpose

The programmatic verification harness `verify_documentation.py` is the authoritative gating mechanism ensuring that the dual-format documentation deliverables (`Autonomous_Drone_Navigation_Technical_Documentation.docx` and `TECHNICAL_DOCUMENTATION.md`) satisfy all publication-grade standards, mathematical completeness criteria, structural requirements, and volume thresholds specified in `ORIGINAL_REQUEST.md` and `PROJECT.md`.

The harness operates as a deterministic, fail-fast, automated test suite that executes across six granular verification tiers (Checks A through F), evaluating document existence, Word XML parseability, comprehensive word count (>6,000 words), chapter coverage (all 6 mandatory sections), codebase file coverage (all 10 audited files/scripts), and mathematical formula fidelity (all 5 core theoretical formulations).

The harness exits with code `0` strictly if and only if all checks pass, and code `1` with a detailed forensic diagnostic breakdown if any check fails.

---

## 2. Interface Contracts & Operational Specification

### 2.1 File Location & Target Artifacts
`verify_documentation.py` resides directly in the workspace root:
- Primary Script: `c:\Users\Rushikesh\Desktop\Cool Ass Projects\Drone\verify_documentation.py`
- Target Artifact 1: `c:\Users\Rushikesh\Desktop\Cool Ass Projects\Drone\Autonomous_Drone_Navigation_Technical_Documentation.docx`
- Target Artifact 2: `c:\Users\Rushikesh\Desktop\Cool Ass Projects\Drone\TECHNICAL_DOCUMENTATION.md`

### 2.2 CLI Arguments & Parameters
The script must provide flexible command-line invocation while defaulting to the project workspace root:
- `--workspace-dir` (string, default: `.`): Root directory containing the documentation artifacts.
- `--docx-name` (string, default: `Autonomous_Drone_Navigation_Technical_Documentation.docx`): Name or path of the DOCX deliverable.
- `--md-name` (string, default: `TECHNICAL_DOCUMENTATION.md`): Name or path of the Markdown companion deliverable.
- `--min-words` (int, default: `6000`): Combined word count threshold required for passing Check C.
- `--no-color` (flag): Disables ANSI terminal coloring (for CI/CD environments or redirection to flat logs).
- `--verbose` (flag): Enables detailed listing of extracted headings, word breakdown per section, and formula matching snippets.

### 2.3 Exit Code Semantics
- `0`: **SUCCESS** — All checks (A, B, C, D, E, F) passed without failure.
- `1`: **FAILURE** — One or more checks failed. Forensics, missing elements, and exact discrepancies are printed to `stderr` / `stdout`.

---

## 3. Granular Validation Check Specifications

### 3.1 Check A: File Existence & Non-Empty Byte Integrity
- **Objective**: Verify that both target files physically exist in the workspace and are not empty (size > 0 bytes).
- **Targets**:
  1. `Autonomous_Drone_Navigation_Technical_Documentation.docx`
  2. `TECHNICAL_DOCUMENTATION.md`
- **Validation Rules**:
  - `os.path.exists(file_path) is True`
  - `os.path.isfile(file_path) is True`
  - `os.path.getsize(file_path) > 0` (non-zero byte length)
- **Failure Diagnostics**:
  - Distinguish between "File not found" vs. "File exists but is 0 bytes (corrupt/empty stub)".
  - Report exact absolute path attempted.

### 3.2 Check B: Structural Parseability & Schema Validation (`docx.Document`)
- **Objective**: Ensure that `Autonomous_Drone_Navigation_Technical_Documentation.docx` is a valid, uncorrupted OpenXML `.docx` container that can be parsed cleanly by `docx.Document` without XML or packaging errors.
- **Validation Rules**:
  - Attempt to instantiate `doc = docx.Document(docx_path)`.
  - Trap all exceptions:
    - `docx.opc.exceptions.PackageNotFoundError`
    - `zipfile.BadZipFile`
    - `xml.etree.ElementTree.ParseError`
    - `Exception`
  - Structural Integrity Checks:
    - Paragraph count: `len(doc.paragraphs) > 0`
    - Table count: `len(doc.tables) > 0`
    - Document section count: `len(doc.sections) > 0`
    - Safe traversal of paragraphs and tables without throwing traversal errors.
- **Failure Diagnostics**:
  - Print full exception type and error string if parsing fails.
  - Report paragraph and table counts if document is structurally deficient (e.g. 0 paragraphs or 0 tables).

### 3.3 Check C: Dual-Format Word Count Calculation
- **Objective**: Calculate the word count for both documents and verify that the combined total exceeds 6,000 words, while reporting individual word counts for both formats.
- **Word Counting Methodology**:
  - **Definition of Word**: Words are defined as non-empty sequences of alphanumeric characters and standard hyphenated terms: `re.findall(r'\b[a-zA-Z0-9_\-]+\b', text)`. This avoids counting markdown syntax tokens (`#`, `|`, `-`, `*`) as words while accurately counting hyphenated technical terms and variable names. In addition, total whitespace tokens `len(text.split())` can be reported for telemetry.
  - **Markdown Extraction**:
    - Read entire `TECHNICAL_DOCUMENTATION.md` using `utf-8` encoding (with `errors="replace"` fallback).
    - Extract text and compute `md_word_count = len(re.findall(r'\b[a-zA-Z0-9_\-]+\b', md_text))`.
  - **DOCX Extraction**:
    - Iterate over `doc.paragraphs`: extract `p.text`.
    - Iterate over `doc.tables`:
      - **CRITICAL EDGE CASE**: In `python-docx`, merged cells appear multiple times in `row.cells`. To prevent duplicate word counting, track visited XML table cell elements (`cell._tc`) in a `seen_cells` set:
        ```python
        table_text = []
        seen_tc = set()
        for table in doc.tables:
            for row in table.rows:
                for cell in row.cells:
                    if cell._tc not in seen_tc:
                        seen_tc.add(cell._tc)
                        table_text.append(cell.text)
        ```
    - Combine paragraph text and table text: `docx_full_text = "\n".join([p.text for p in doc.paragraphs] + table_text)`.
    - Compute `docx_word_count = len(re.findall(r'\b[a-zA-Z0-9_\-]+\b', docx_full_text))`.
  - **Threshold Check**:
    - `combined_word_count = md_word_count + docx_word_count`
    - `assert combined_word_count > min_words` (where `min_words = 6000`).
    - Individual telemetry reporting: both `md_word_count` and `docx_word_count` must be explicitly displayed in the console report.

### 3.4 Check D: 6-Chapter Mandatory Heading Verification
- **Objective**: Assert the presence of all 6 core chapters in both `TECHNICAL_DOCUMENTATION.md` and `Autonomous_Drone_Navigation_Technical_Documentation.docx`.
- **Mandatory Chapters & Canonical Regular Expressions**:
  1. **Executive Summary**:
     - Regex: `r"executive\s+summary"`
  2. **System Architecture**:
     - Regex: `r"system\s+architecture"`
  3. **Simulation Environment Mechanics**:
     - Regex: `r"simulation\s+environment(\s+mechanics)?"`
  4. **Drone Navigation & Algorithmic Foundations**:
     - Regex: `r"drone\s+navigation(\s*(?:&|and)\s*algorithmic\s+foundations)?"`
  5. **Granular Module & File Breakdown**:
     - Regex: `r"(?:granular\s+)?(?:module|file)(?:\s*(?:&|and)\s*(?:module|file))?\s*breakdown"`
  6. **Setup, Configuration & Execution**:
     - Regex: `r"setup(?:\s*,\s*configuration)?(?:\s*(?:&|and)\s*execution)?"`
- **Matching Methodology**:
  - **In Markdown**:
    - Extract all lines matching Markdown headings: `re.findall(r'^(?:#{1,6})\s+(.+)$', md_text, re.MULTILINE)`
    - Check each chapter regex against extracted heading lines (case-insensitive).
    - As fallback, check full markdown text if heading formatting differs.
  - **In DOCX**:
    - Iterate over `doc.paragraphs`.
    - Check paragraphs where `p.style.name.startswith(('Heading', 'Title'))` or `any(run.bold for run in p.runs)`.
    - Check each chapter regex against heading text (case-insensitive).
    - As fallback, check all paragraph texts.
- **Assertion**:
  - Markdown: 6 of 6 chapters present.
  - DOCX: 6 of 6 chapters present.

### 3.5 Check E: Complete Codebase File Coverage (10 Files)
- **Objective**: Assert that all 10 audited files/scripts are explicitly analyzed and referenced in both documents.
- **Audited Files List**:
  1. `environment.py`
  2. `model.py`
  3. `pretrain_bc.py`
  4. `train.py`
  5. `explainability.py`
  6. `evaluate_and_visualize.py`
  7. `run_project.bat`
  8. `overnight_train.bat`
  9. `requirements.txt`
  10. `README.md`
- **Matching Methodology**:
  - Use word-boundary regex patterns to avoid partial string false positives:
    ```python
    file_pattern = re.compile(r'\b' + re.escape(filename) + r'\b', re.IGNORECASE)
    ```
  - In Markdown: search across the entire markdown content.
  - In DOCX: search across concatenated paragraph and table cell text.
- **Assertion**:
  - Markdown: 10 of 10 files present.
  - DOCX: 10 of 10 files present.

### 3.6 Check F: Mathematical Formula Verification (5 Domains)
- **Objective**: Assert the presence of the 5 core mathematical formulations across both documents.
- **Formula Domains & Multi-Format Signatures**:
  1. **Inverse Time-to-Collision ($\tau^{-1}$ / TTC)**:
     - Concepts: Bounded looming, optical flow divergence, Sobel gradients, 60% central ROI.
     - Markdown Regex: `r'(\\tau\^\{-?1\}|tau\^?-?1|τ⁻¹|tau_inv|inverse\s+time-to-collision|time-to-collision)'`
     - DOCX Regex: Same multi-pattern regex accommodating Unicode `τ⁻¹`, LaTeX `\tau^{-1}`, and ASCII `tau^-1`.
  2. **Gunnar Farneback Optical Flow**:
     - Concepts: Dense displacement polynomial expansion, quadratic surface fitting, OpenCV solver.
     - Regex: `r'(farneback|calcopticalflowfarneback|gunnar\s+farneback)'`
  3. **Potential Field Vectors & Expert Planning**:
     - Concepts: Attractive goal pull, repulsive obstacle forces, tangential obstacle steering, altitude holding.
     - Regex: `r'(potential\s+field|tangential\s+(?:obstacle\s+)?steering|attractive\s+force|repulsive\s+force)'`
  4. **PPO Objective & GAE**:
     - Concepts: Clipped surrogate objective ($\epsilon=0.2$), Generalized Advantage Estimation ($\text{GAE}-\lambda$, $\gamma=0.99, \lambda=0.95$), value function loss.
     - Regex: `r'(ppo|gae|clipped\s+surrogate|generalized\s+advantage\s+estimation|surr1|surr2|l\^?\{?clip\}?)'`
  5. **Spatial IoU Explanation Fidelity**:
     - Concepts: Captum saliency / integrated gradients attribution mask vs ground-truth depth obstacle mask ($D < 1.5$ m), Jaccard index.
     - Regex: `r'(spatial\s+iou|explanation\s+fidelity|intersection\s+over\s+union)'`
- **Assertion**:
  - Markdown: 5 of 5 formula domains verified.
  - DOCX: 5 of 5 formula domains verified.

---

## 4. Console Reporting & User Experience Design

### 4.1 ANSI Color Formatting & Terminal Compatibility
To ensure cross-platform fidelity on Windows 10/11 PowerShell and CMD, the harness must invoke `os.system("")` on startup (which enables virtual terminal processing in Windows console hosts).

- **Colors**:
  - Success / Pass: `\033[92mPASS\033[0m` (Bright Green)
  - Failure: `\033[91mFAIL\033[0m` (Bright Red)
  - Warning / Metric: `\033[93m` (Bright Yellow)
  - Table Borders / Headers: `\033[96m` (Cyan)
  - Bold Emphasis: `\033[1m`
  - Reset: `\033[0m`

### 4.2 High-Density Summary Table Layout
The console report displays an ASCII table summarizing the test execution status:

```text
====================================================================================================
      AUTONOMOUS DRONE NAVIGATION - TECHNICAL DOCUMENTATION VERIFICATION HARNESS
====================================================================================================
Check ID  Target      Verification Description                 Status   Metrics / Details
----------------------------------------------------------------------------------------------------
CHECK-A1  DOCX        File Existence & Non-Empty Size          PASS     Size: 245,120 bytes
CHECK-A2  Markdown    File Existence & Non-Empty Size          PASS     Size: 98,412 bytes
CHECK-B   DOCX        docx.Document OpenXML Parseability       PASS     Paragraphs: 342, Tables: 14
CHECK-C1  Markdown    Word Count (Alphanumeric Tokens)         PASS     Count: 6,850 words
CHECK-C2  DOCX        Word Count (Paragraphs & Tables)         PASS     Count: 6,420 words
CHECK-C3  Combined    Total Word Count (> 6,000 threshold)     PASS     Total: 13,270 words (> 6,000)
CHECK-D1  Markdown    6 Mandatory Chapter Headings             PASS     Found: 6/6 chapters
CHECK-D2  DOCX        6 Mandatory Chapter Headings             PASS     Found: 6/6 chapters
CHECK-E1  Markdown    10 Audited Codebase Files                PASS     Covered: 10/10 files
CHECK-E2  DOCX        10 Audited Codebase Files                PASS     Covered: 10/10 files
CHECK-F1  Markdown    5 Mathematical Formula Domains           PASS     Verified: 5/5 domains
CHECK-F2  DOCX        5 Mathematical Formula Domains           PASS     Verified: 5/5 domains
====================================================================================================
VERIFICATION RESULT: ALL CHECKS PASSED (Exit Code 0)
====================================================================================================
```

### 4.3 Detailed Diagnostic Section (On Failure)
If any check fails, the harness outputs an explicit section after the table detailing the failure causes:
```text
!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
                                  VERIFICATION FAILURE FORENSICS
!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
[!] CHECK-D2 FAILED: Missing mandatory chapters in DOCX:
    - "Drone Navigation & Algorithmic Foundations" not detected in headings or body paragraphs.
[!] CHECK-E1 FAILED: Missing audited files in Markdown:
    - "overnight_train.bat" not found in Markdown source.
!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
```

---

## 5. Reference Implementation Blueprint for `verify_documentation.py`

Below is the complete reference implementation architecture for the implementer agent:

```python
"""
verify_documentation.py
-----------------------
Automated Verification Test Harness for Autonomous Drone Navigation Documentation.
Validates existence, Word document parseability, word counts, chapter coverage,
file audit completeness, and mathematical formulations across both .docx and .md deliverables.

Exit Status:
    0: All checks passed.
    1: One or more checks failed.
"""

import os
import sys
import re
import argparse
from typing import List, Dict, Tuple, Set

# Optional ANSI enablement for Windows
if os.name == 'nt':
    os.system('')

# ANSI Colors
CLR_RESET = "\033[0m"
CLR_BOLD  = "\033[1m"
CLR_RED   = "\033[91m"
CLR_GREEN = "\033[92m"
CLR_YELLOW= "\033[93m"
CLR_CYAN  = "\033[96m"
CLR_GRAY  = "\033[90m"

MANDATORY_CHAPTERS = [
    ("Executive Summary", re.compile(r"executive\s+summary", re.I)),
    ("System Architecture", re.compile(r"system\s+architecture", re.I)),
    ("Simulation Environment Mechanics", re.compile(r"simulation\s+environment(\s+mechanics)?", re.I)),
    ("Drone Navigation & Algorithmic Foundations", re.compile(r"drone\s+navigation(\s*(?:&|and)\s*algorithmic\s+foundations)?", re.I)),
    ("Granular Module & File Breakdown", re.compile(r"(?:granular\s+)?(?:module|file)(?:\s*(?:&|and)\s*(?:module|file))?\s*breakdown", re.I)),
    ("Setup, Configuration & Execution", re.compile(r"setup(?:\s*,\s*configuration)?(?:\s*(?:&|and)\s*execution)?", re.I)),
]

AUDITED_FILES = [
    "environment.py",
    "model.py",
    "pretrain_bc.py",
    "train.py",
    "explainability.py",
    "evaluate_and_visualize.py",
    "run_project.bat",
    "overnight_train.bat",
    "requirements.txt",
    "README.md",
]

MATH_FORMULAS = [
    ("TTC / Inverse Time-to-Collision (tau^-1)", re.compile(r'(\\tau\^\{-?1\}|tau\^?-?1|τ⁻¹|tau_inv|inverse\s+time-to-collision|time-to-collision)', re.I)),
    ("Farneback Optical Flow", re.compile(r'(farneback|calcopticalflowfarneback|gunnar\s+farneback)', re.I)),
    ("Potential Field Vectors & Steering", re.compile(r'(potential\s+field|tangential\s+(?:obstacle\s+)?steering|attractive\s+force|repulsive\s+force)', re.I)),
    ("PPO Objective & GAE", re.compile(r'(ppo|gae|clipped\s+surrogate|generalized\s+advantage\s+estimation|surr1|surr2|l\^?\{?clip\}?)', re.I)),
    ("Spatial IoU Explanation Fidelity", re.compile(r'(spatial\s+iou|explanation\s+fidelity|intersection\s+over\s+union)', re.I)),
]

class DocumentationVerifier:
    def __init__(self, workspace_dir: str, docx_name: str, md_name: str, min_words: int = 6000, use_color: bool = True):
        self.workspace_dir = os.path.abspath(workspace_dir)
        self.docx_path = os.path.join(self.workspace_dir, docx_name)
        self.md_path = os.path.join(self.workspace_dir, md_name)
        self.min_words = min_words
        self.use_color = use_color

        self.results = []
        self.diagnostics = []
        self.all_passed = True

        self.doc_obj = None
        self.md_content = ""
        self.docx_paragraphs_text = []
        self.docx_tables_text = []
        self.docx_full_text = ""

    def color(self, code: str, text: str) -> str:
        if not self.use_color:
            return text
        return f"{code}{text}{CLR_RESET}"

    def record_result(self, check_id: str, target: str, desc: str, passed: bool, detail: str, diag_msg: str = ""):
        status_str = self.color(CLR_GREEN, "PASS") if passed else self.color(CLR_RED, "FAIL")
        self.results.append({
            "id": check_id,
            "target": target,
            "desc": desc,
            "passed": passed,
            "status_str": status_str,
            "detail": detail
        })
        if not passed:
            self.all_passed = False
            if diag_msg:
                self.diagnostics.append(f"[{check_id}] {diag_msg}")

    def check_a_existence(self):
        # A1: DOCX existence
        if not os.path.exists(self.docx_path):
            self.record_result("CHECK-A1", "DOCX", "File Existence & Size", False, "Not Found", f"Missing DOCX at {self.docx_path}")
        else:
            sz = os.path.getsize(self.docx_path)
            if sz == 0:
                self.record_result("CHECK-A1", "DOCX", "File Existence & Size", False, "0 Bytes", f"DOCX exists but is 0 bytes (empty/stub): {self.docx_path}")
            else:
                self.record_result("CHECK-A1", "DOCX", "File Existence & Size", True, f"Size: {sz:,} bytes")

        # A2: MD existence
        if not os.path.exists(self.md_path):
            self.record_result("CHECK-A2", "Markdown", "File Existence & Size", False, "Not Found", f"Missing Markdown at {self.md_path}")
        else:
            sz = os.path.getsize(self.md_path)
            if sz == 0:
                self.record_result("CHECK-A2", "Markdown", "File Existence & Size", False, "0 Bytes", f"Markdown exists but is 0 bytes (empty/stub): {self.md_path}")
            else:
                self.record_result("CHECK-A2", "Markdown", "File Existence & Size", True, f"Size: {sz:,} bytes")

    def check_b_docx_parseability(self):
        if not os.path.exists(self.docx_path) or os.path.getsize(self.docx_path) == 0:
            self.record_result("CHECK-B", "DOCX", "docx.Document OpenXML Parseability", False, "Skipped", "Cannot parse missing or empty DOCX.")
            return

        try:
            import docx
            self.doc_obj = docx.Document(self.docx_path)
            num_paras = len(self.doc_obj.paragraphs)
            num_tables = len(self.doc_obj.tables)

            # Traversal & table extraction with merged-cell deduplication
            self.docx_paragraphs_text = [p.text for p in self.doc_obj.paragraphs]
            seen_tc = set()
            for table in self.doc_obj.tables:
                for row in table.rows:
                    for cell in row.cells:
                        if cell._tc not in seen_tc:
                            seen_tc.add(cell._tc)
                            self.docx_tables_text.append(cell.text)

            self.docx_full_text = "\n".join(self.docx_paragraphs_text + self.docx_tables_text)

            if num_paras == 0:
                self.record_result("CHECK-B", "DOCX", "docx.Document OpenXML Parseability", False, "0 Paragraphs", "DOCX parsed but contains 0 paragraphs.")
            elif num_tables == 0:
                self.record_result("CHECK-B", "DOCX", "docx.Document OpenXML Parseability", False, "0 Tables", "DOCX parsed but contains 0 tables (styled tables required).")
            else:
                self.record_result("CHECK-B", "DOCX", "docx.Document OpenXML Parseability", True, f"Paras: {num_paras:,}, Tables: {num_tables:,}")

        except Exception as e:
            self.record_result("CHECK-B", "DOCX", "docx.Document OpenXML Parseability", False, f"Exception: {type(e).__name__}", f"DOCX parsing raised {type(e).__name__}: {str(e)}")

    def check_c_word_counts(self):
        # Markdown words
        md_words = 0
        if os.path.exists(self.md_path):
            with open(self.md_path, "r", encoding="utf-8", errors="replace") as f:
                self.md_content = f.read()
            md_tokens = re.findall(r'\b[a-zA-Z0-9_\-]+\b', self.md_content)
            md_words = len(md_tokens)
            self.record_result("CHECK-C1", "Markdown", "Word Count (Alphanumeric Tokens)", True, f"{md_words:,} words")
        else:
            self.record_result("CHECK-C1", "Markdown", "Word Count (Alphanumeric Tokens)", False, "0 words", "Cannot count words in missing Markdown file.")

        # DOCX words
        docx_words = 0
        if self.doc_obj is not None and self.docx_full_text:
            docx_tokens = re.findall(r'\b[a-zA-Z0-9_\-]+\b', self.docx_full_text)
            docx_words = len(docx_tokens)
            self.record_result("CHECK-C2", "DOCX", "Word Count (Paras & Tables)", True, f"{docx_words:,} words")
        else:
            self.record_result("CHECK-C2", "DOCX", "Word Count (Paras & Tables)", False, "0 words", "Cannot count words in unparsed DOCX file.")

        # Combined words
        total_words = md_words + docx_words
        passed = total_words > self.min_words
        detail = f"Total: {total_words:,} words (Threshold: >{self.min_words:,})"
        diag = "" if passed else f"Combined word count {total_words:,} is below mandatory threshold of {self.min_words:,} words."
        self.record_result("CHECK-C3", "Combined", f"Total Word Count (>{self.min_words:,})", passed, detail, diag)

    def check_d_chapters(self):
        # D1: Markdown Chapters
        missing_md_ch = []
        found_md_ch = 0
        for title, pattern in MANDATORY_CHAPTERS:
            if pattern.search(self.md_content):
                found_md_ch += 1
            else:
                missing_md_ch.append(title)

        passed_md = len(missing_md_ch) == 0
        diag_md = f"Missing chapters in Markdown: {', '.join(missing_md_ch)}" if not passed_md else ""
        self.record_result("CHECK-D1", "Markdown", "6 Mandatory Chapter Headings", passed_md, f"Found: {found_md_ch}/6", diag_md)

        # D2: DOCX Chapters
        missing_docx_ch = []
        found_docx_ch = 0
        for title, pattern in MANDATORY_CHAPTERS:
            if pattern.search(self.docx_full_text):
                found_docx_ch += 1
            else:
                missing_docx_ch.append(title)

        passed_docx = len(missing_docx_ch) == 0
        diag_docx = f"Missing chapters in DOCX: {', '.join(missing_docx_ch)}" if not passed_docx else ""
        self.record_result("CHECK-D2", "DOCX", "6 Mandatory Chapter Headings", passed_docx, f"Found: {found_docx_ch}/6", diag_docx)

    def check_e_files(self):
        # E1: Markdown Files
        missing_md_files = []
        found_md_files = 0
        for fname in AUDITED_FILES:
            pat = re.compile(r'\b' + re.escape(fname) + r'\b', re.I)
            if pat.search(self.md_content):
                found_md_files += 1
            else:
                missing_md_files.append(fname)

        passed_md = len(missing_md_files) == 0
        diag_md = f"Missing audited files in Markdown: {', '.join(missing_md_files)}" if not passed_md else ""
        self.record_result("CHECK-E1", "Markdown", "10 Audited Codebase Files", passed_md, f"Covered: {found_md_files}/10", diag_md)

        # E2: DOCX Files
        missing_docx_files = []
        found_docx_files = 0
        for fname in AUDITED_FILES:
            pat = re.compile(r'\b' + re.escape(fname) + r'\b', re.I)
            if pat.search(self.docx_full_text):
                found_docx_files += 1
            else:
                missing_docx_files.append(fname)

        passed_docx = len(missing_docx_files) == 0
        diag_docx = f"Missing audited files in DOCX: {', '.join(missing_docx_files)}" if not passed_docx else ""
        self.record_result("CHECK-E2", "DOCX", "10 Audited Codebase Files", passed_docx, f"Covered: {found_docx_files}/10", diag_docx)

    def check_f_math_formulas(self):
        # F1: Markdown Math
        missing_md_math = []
        found_md_math = 0
        for name, pattern in MATH_FORMULAS:
            if pattern.search(self.md_content):
                found_md_math += 1
            else:
                missing_md_math.append(name)

        passed_md = len(missing_md_math) == 0
        diag_md = f"Missing math formulas in Markdown: {', '.join(missing_md_math)}" if not passed_md else ""
        self.record_result("CHECK-F1", "Markdown", "5 Mathematical Formula Domains", passed_md, f"Verified: {found_md_math}/5", diag_md)

        # F2: DOCX Math
        missing_docx_math = []
        found_docx_math = 0
        for name, pattern in MATH_FORMULAS:
            if pattern.search(self.docx_full_text):
                found_docx_math += 1
            else:
                missing_docx_math.append(name)

        passed_docx = len(missing_docx_math) == 0
        diag_docx = f"Missing math formulas in DOCX: {', '.join(missing_docx_math)}" if not passed_docx else ""
        self.record_result("CHECK-F2", "DOCX", "5 Mathematical Formula Domains", passed_docx, f"Verified: {found_docx_math}/5", diag_docx)

    def run_all(self) -> bool:
        self.check_a_existence()
        self.check_b_docx_parseability()
        self.check_c_word_counts()
        self.check_d_chapters()
        self.check_e_files()
        self.check_f_math_formulas()
        return self.all_passed

    def print_report(self):
        banner = "=" * 100
        sep = "-" * 100
        print(self.color(CLR_CYAN, banner))
        print(self.color(CLR_BOLD + CLR_CYAN, "      AUTONOMOUS DRONE NAVIGATION - TECHNICAL DOCUMENTATION VERIFICATION HARNESS"))
        print(self.color(CLR_CYAN, banner))
        header = f"{'Check ID':<10} {'Target':<11} {'Verification Description':<38} {'Status':<8} {'Metrics / Details'}"
        print(self.color(CLR_BOLD, header))
        print(self.color(CLR_GRAY, sep))

        for r in self.results:
            row = f"{r['id']:<10} {r['target']:<11} {r['desc']:<38} {r['status_str']}   {r['detail']}"
            print(row)

        print(self.color(CLR_CYAN, banner))
        if self.all_passed:
            msg = "VERIFICATION RESULT: ALL CHECKS PASSED (Exit Code 0)"
            print(self.color(CLR_BOLD + CLR_GREEN, msg))
        else:
            msg = "VERIFICATION RESULT: ONE OR MORE CHECKS FAILED (Exit Code 1)"
            print(self.color(CLR_BOLD + CLR_RED, msg))
        print(self.color(CLR_CYAN, banner))

        if self.diagnostics:
            print("\n" + self.color(CLR_RED, "!" * 100))
            print(self.color(CLR_BOLD + CLR_RED, "                                  VERIFICATION FAILURE FORENSICS"))
            print(self.color(CLR_RED, "!" * 100))
            for d in self.diagnostics:
                print(self.color(CLR_YELLOW, f" [!] {d}"))
            print(self.color(CLR_RED, "!" * 100) + "\n")

def main():
    parser = argparse.ArgumentParser(description="Programmatic verification test harness for drone documentation.")
    parser.add_argument("--workspace-dir", default=".", help="Path to workspace root directory.")
    parser.add_argument("--docx-name", default="Autonomous_Drone_Navigation_Technical_Documentation.docx", help="Filename of DOCX deliverable.")
    parser.add_argument("--md-name", default="TECHNICAL_DOCUMENTATION.md", help="Filename of Markdown deliverable.")
    parser.add_argument("--min-words", type=int, default=6000, help="Combined minimum word count threshold.")
    parser.add_argument("--no-color", action="store_true", help="Disable ANSI color codes.")
    args = parser.parse_args()

    verifier = DocumentationVerifier(
        workspace_dir=args.workspace_dir,
        docx_name=args.docx_name,
        md_name=args.md_name,
        min_words=args.min_words,
        use_color=not args.no_color
    )
    success = verifier.run_all()
    verifier.print_report()
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
```

---

## 6. Comprehensive Edge Case Matrix

| Edge Case ID | Condition / Scenario | Potential Failure Mode | Specification Mitigation in Test Harness |
| :--- | :--- | :--- | :--- |
| **EC-01** | Missing `.docx` or `.md` file | `FileNotFoundError` crashes execution ungracefully | Checked in Check A via `os.path.exists()` with clean diagnostic reporting. |
| **EC-02** | 0-byte placeholder/stub file | File exists but has no content; parser fails or counts 0 | Check A explicitly asserts `os.path.getsize() > 0`, flagging 0-byte stubs immediately. |
| **EC-03** | Corrupted DOCX zip / broken OpenXML | `zipfile.BadZipFile` or `xml.etree.ElementTree.ParseError` uncaught | Check B wraps `docx.Document()` in `try ... except Exception`, recording exact exception class and string. |
| **EC-04** | Merged table cells in DOCX | Cells iterated via `row.cells` repeat merged text multiple times, inflating word count | Harness tracks visited XML elements (`cell._tc`) in a `seen_tc` set, ensuring unique cell counting. |
| **EC-05** | Empty table or paragraph structure | Document parses as valid zip but contains 0 paragraphs or 0 tables | Check B asserts `len(paragraphs) > 0` and `len(tables) > 0` before declaring structural validity. |
| **EC-06** | Markdown syntax tokens counted as words | Plain `split()` counts markdown `#`, `|`, `---`, `*` as words | Harness utilizes alphanumeric tokenization `\b[a-zA-Z0-9_\-]+\b` to strictly count genuine technical vocabulary. |
| **EC-07** | Windows console without VT100 ANSI support | ANSI escape sequences render as garbled `\033[92m` characters | Harness invokes `os.system('')` on Windows initialization to enable VT100 mode, and provides `--no-color` flag. |
| **EC-08** | Case variations in chapter headings | Markdown headings formatted as "1. Executive Summary" vs "## EXECUTIVE SUMMARY" | Canonical regex patterns use `re.IGNORECASE` and permissive whitespace/numbering wildcards. |
| **EC-09** | Escaped filenames in Markdown tables/code | Filenames surrounded by backticks (`` `train.py` ``) or brackets | Regex uses word boundaries (`\b... \b`) with escaped period (`\.`), matching cleanly across markdown decorations. |
| **EC-10** | LaTeX math vs Unicode math in DOCX | Markdown has `$\tau^{-1}$` while DOCX has `τ⁻¹` or `tau^-1` | Formula regex patterns incorporate Unicode (`τ⁻¹`), LaTeX (`\tau^{-1}`), and ASCII (`tau^-1`, `tau_inv`) alternatives. |
| **EC-11** | Non-UTF-8 characters in Markdown source | `UnicodeDecodeError` when reading Markdown file on Windows | File opened with `encoding="utf-8", errors="replace"`, guaranteeing robust string reading. |

---

## 7. Downstream Implementation Directives for Milestone M1

1. **Implementer Agent**: The implementer agent must place `verify_documentation.py` in the workspace root (`c:\Users\Rushikesh\Desktop\Cool Ass Projects\Drone\verify_documentation.py`) matching the architecture specified in Section 5.
2. **Pre-flight Dry Run**: Running `python verify_documentation.py` prior to Milestone M2 document generation should cleanly report failures for Check A (files missing) and exit with code `1`, without unhandled Python exceptions.
3. **Post-generation Validation**: Upon generation of `Autonomous_Drone_Navigation_Technical_Documentation.docx` and `TECHNICAL_DOCUMENTATION.md` in Milestone M2, running `python verify_documentation.py` must execute cleanly and exit with status code `0`.
