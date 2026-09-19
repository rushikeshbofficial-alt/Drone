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

# Enable ANSI colors on Windows console
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
