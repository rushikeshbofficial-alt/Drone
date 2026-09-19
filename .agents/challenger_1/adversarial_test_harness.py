"""
adversarial_test_harness.py
----------------------------
Adversarial stress-testing suite for verify_documentation.py and documentation deliverables.
Constructs synthetic corruptions and edge cases to empirically verify that:
1. verify_documentation.py strictly detects and rejects non-compliant inputs (returns exit code 1).
2. verify_documentation.py accurately parses the real .docx and .md deliverables (returns exit code 0).
3. Evaluates regex specificity, heading anchoring, and failure forensics reporting.
"""

import os
import sys
import re
import shutil
import tempfile
import subprocess
import docx

WORKSPACE_DIR = os.path.abspath(r"c:\Users\Rushikesh\Desktop\Cool Ass Projects\Drone")
VERIFY_SCRIPT = os.path.join(WORKSPACE_DIR, "verify_documentation.py")
REAL_DOCX = os.path.join(WORKSPACE_DIR, "Autonomous_Drone_Navigation_Technical_Documentation.docx")
REAL_MD = os.path.join(WORKSPACE_DIR, "TECHNICAL_DOCUMENTATION.md")

class AdversarialRunner:
    def __init__(self):
        self.temp_dir = tempfile.mkdtemp(prefix="adv_test_")
        self.tests_passed = 0
        self.tests_failed = 0
        self.test_records = []

    def cleanup(self):
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir, ignore_errors=True)

    def run_verifier(self, args: list) -> tuple[int, str]:
        cmd = [sys.executable, VERIFY_SCRIPT, "--workspace-dir", self.temp_dir, "--no-color"] + args
        proc = subprocess.run(cmd, capture_output=True, text=True, cwd=WORKSPACE_DIR)
        return proc.returncode, proc.stdout + proc.stderr

    def record_test(self, name: str, expected_exit: int, actual_exit: int, expected_in_output: str, output: str, notes: str = ""):
        exit_ok = (expected_exit == actual_exit)
        output_ok = (expected_in_output in output)
        passed = exit_ok and output_ok
        if passed:
            self.tests_passed += 1
            status = "PASS"
        else:
            self.tests_failed += 1
            status = "FAIL"

        self.test_records.append({
            "name": name,
            "status": status,
            "expected_exit": expected_exit,
            "actual_exit": actual_exit,
            "expected_in_output": expected_in_output,
            "notes": notes
        })
        print(f"[{status}] {name} -> Exit {actual_exit} (Exp: {expected_exit}) | Output check: {output_ok}")
        if not passed:
            print(f"       EXPECTED IN OUTPUT: {expected_in_output}")
            print(f"       OUTPUT TAIL:\n{output[-600:]}")

    def test_baseline_real_files(self):
        """Verify that genuine deliverables produce exit code 0 and all 12 PASS."""
        shutil.copy(REAL_DOCX, os.path.join(self.temp_dir, "real.docx"))
        shutil.copy(REAL_MD, os.path.join(self.temp_dir, "real.md"))

        exit_code, out = self.run_verifier(["--docx-name", "real.docx", "--md-name", "real.md"])
        self.record_test("T01: Baseline Real Deliverables Pass All Checks", 0, exit_code, "ALL CHECKS PASSED (Exit Code 0)", out)

    def test_missing_docx(self):
        """Verify that missing DOCX causes exit code 1 and CHECK-A1 FAIL."""
        exit_code, out = self.run_verifier(["--docx-name", "nonexistent.docx", "--md-name", "real.md"])
        self.record_test("T02: Synthetic Missing DOCX File", 1, exit_code, "CHECK-A1   DOCX        File Existence & Size                  FAIL", out)

    def test_missing_md(self):
        """Verify that missing MD causes exit code 1 and CHECK-A2 FAIL."""
        exit_code, out = self.run_verifier(["--docx-name", "real.docx", "--md-name", "nonexistent.md"])
        self.record_test("T03: Synthetic Missing Markdown File", 1, exit_code, "CHECK-A2   Markdown    File Existence & Size                  FAIL", out)

    def test_empty_docx(self):
        """Verify that 0-byte DOCX causes exit code 1 and 0 Bytes warning."""
        empty_docx = os.path.join(self.temp_dir, "empty.docx")
        open(empty_docx, "wb").close()

        exit_code, out = self.run_verifier(["--docx-name", "empty.docx", "--md-name", "real.md"])
        self.record_test("T04: Synthetic 0-Byte Empty DOCX File", 1, exit_code, "0 Bytes", out)

    def test_empty_md(self):
        """Verify that 0-byte MD causes exit code 1 and 0 Bytes warning."""
        empty_md = os.path.join(self.temp_dir, "empty.md")
        open(empty_md, "wb").close()

        exit_code, out = self.run_verifier(["--docx-name", "real.docx", "--md-name", "empty.md"])
        self.record_test("T05: Synthetic 0-Byte Empty Markdown File", 1, exit_code, "0 Bytes", out)

    def test_corrupted_docx(self):
        """Verify that corrupted binary in DOCX triggers exception handler in CHECK-B and exits with 1."""
        corrupt_docx = os.path.join(self.temp_dir, "corrupt.docx")
        with open(corrupt_docx, "wb") as f:
            f.write(b"CORRUPTED_BINARY_HEADER_NOT_A_ZIP_ARCHIVE_MOCK_DATA")

        exit_code, out = self.run_verifier(["--docx-name", "corrupt.docx", "--md-name", "real.md"])
        self.record_test("T06: Synthetic Corrupted Non-Zip DOCX File", 1, exit_code, "CHECK-B    DOCX        docx.Document OpenXML Parseability     FAIL", out)

    def test_word_count_threshold_high(self):
        """Verify that setting threshold higher than deliverables word count (e.g. 25,000) causes exit 1."""
        exit_code, out = self.run_verifier(["--docx-name", "real.docx", "--md-name", "real.md", "--min-words", "25000"])
        self.record_test("T07: Synthetic Strict Word Count (>25,000) Threshold Failure", 1, exit_code, "CHECK-C3   Combined    Total Word Count (>25,000)             FAIL", out)

    def test_word_count_truncated_files(self):
        """Verify that truncated files (<6,000 words total) trigger CHECK-C3 FAIL."""
        trunc_md = os.path.join(self.temp_dir, "trunc.md")
        with open(trunc_md, "w", encoding="utf-8") as f:
            f.write("# Short Document\nOnly a few words here.")

        doc = docx.Document()
        doc.add_paragraph("Short docx text.")
        doc.add_table(rows=1, cols=1).cell(0, 0).text = "Table"
        trunc_docx = os.path.join(self.temp_dir, "trunc.docx")
        doc.save(trunc_docx)

        exit_code, out = self.run_verifier(["--docx-name", "trunc.docx", "--md-name", "trunc.md", "--min-words", "6000"])
        self.record_test("T08: Synthetic Truncated Documents Under 6,000 Words", 1, exit_code, "CHECK-C3   Combined    Total Word Count (>6,000)              FAIL", out)

    def test_missing_chapter_md(self):
        """Verify that stripping all occurrences of a chapter heading in MD triggers CHECK-D1 FAIL."""
        with open(REAL_MD, "r", encoding="utf-8") as f:
            md_text = f.read()

        # Strip all occurrences matching simulation\s+environment
        mutated_text = re.sub(r"simulation\s+environment", "physics_test_platform", md_text, flags=re.I)
        mutated_path = os.path.join(self.temp_dir, "mut_no_sim_chap.md")
        with open(mutated_path, "w", encoding="utf-8") as f:
            f.write(mutated_text)

        exit_code, out = self.run_verifier(["--docx-name", "real.docx", "--md-name", "mut_no_sim_chap.md"])
        self.record_test("T09: Synthetic Missing 'Simulation Environment Mechanics' in MD", 1, exit_code, "CHECK-D1   Markdown    6 Mandatory Chapter Headings           FAIL", out)

    def test_missing_chapter_docx(self):
        """Verify that removing all occurrences of a chapter heading in DOCX triggers CHECK-D2 FAIL."""
        doc = docx.Document(REAL_DOCX)
        for p in doc.paragraphs:
            p.text = re.sub(r"executive\s+summary", "Project Context Overview", p.text, flags=re.I)
        for table in doc.tables:
            for row in table.rows:
                for cell in row.cells:
                    cell.text = re.sub(r"executive\s+summary", "Project Context Overview", cell.text, flags=re.I)

        mut_docx_path = os.path.join(self.temp_dir, "mut_no_exec_docx.docx")
        doc.save(mut_docx_path)

        exit_code, out = self.run_verifier(["--docx-name", "mut_no_exec_docx.docx", "--md-name", "real.md"])
        self.record_test("T10: Synthetic Missing 'Executive Summary' in DOCX", 1, exit_code, "CHECK-D2   DOCX        6 Mandatory Chapter Headings           FAIL", out)

    def test_missing_audited_file_md(self):
        """Verify that omitting an audited file (e.g. pretrain_bc.py) in MD triggers CHECK-E1 FAIL."""
        with open(REAL_MD, "r", encoding="utf-8") as f:
            md_text = f.read()

        mutated_text = re.sub(r"\bpretrain_bc\.py\b", "imitation_planner.py", md_text, flags=re.I)
        mutated_path = os.path.join(self.temp_dir, "mut_no_pretrain_md.md")
        with open(mutated_path, "w", encoding="utf-8") as f:
            f.write(mutated_text)

        exit_code, out = self.run_verifier(["--docx-name", "real.docx", "--md-name", "mut_no_pretrain_md.md"])
        self.record_test("T11: Synthetic Missing 'pretrain_bc.py' in MD", 1, exit_code, "CHECK-E1   Markdown    10 Audited Codebase Files              FAIL", out)

    def test_missing_audited_file_docx(self):
        """Verify that omitting an audited file (e.g. explainability.py) in DOCX triggers CHECK-E2 FAIL."""
        doc = docx.Document(REAL_DOCX)
        for p in doc.paragraphs:
            p.text = re.sub(r"\bexplainability\.py\b", "xai_attributions.py", p.text, flags=re.I)
        for table in doc.tables:
            for row in table.rows:
                for cell in row.cells:
                    cell.text = re.sub(r"\bexplainability\.py\b", "xai_attributions.py", cell.text, flags=re.I)

        mut_docx_path = os.path.join(self.temp_dir, "mut_no_xai_docx.docx")
        doc.save(mut_docx_path)

        exit_code, out = self.run_verifier(["--docx-name", "mut_no_xai_docx.docx", "--md-name", "real.md"])
        self.record_test("T12: Synthetic Missing 'explainability.py' in DOCX", 1, exit_code, "CHECK-E2   DOCX        10 Audited Codebase Files              FAIL", out)

    def test_missing_math_formula_md(self):
        """Verify that omitting a math formula domain (e.g. Farneback optical flow) in MD triggers CHECK-F1 FAIL."""
        with open(REAL_MD, "r", encoding="utf-8") as f:
            md_text = f.read()

        mutated_text = re.sub(r"farneback|calcopticalflowfarneback", "lucas_kanade", md_text, flags=re.I)
        mutated_path = os.path.join(self.temp_dir, "mut_no_farneback_md.md")
        with open(mutated_path, "w", encoding="utf-8") as f:
            f.write(mutated_text)

        exit_code, out = self.run_verifier(["--docx-name", "real.docx", "--md-name", "mut_no_farneback_md.md"])
        self.record_test("T13: Synthetic Missing Farneback Optical Flow in MD", 1, exit_code, "CHECK-F1   Markdown    5 Mathematical Formula Domains         FAIL", out)

    def test_missing_math_formula_docx(self):
        """Verify that omitting Spatial IoU / Explanation Fidelity in DOCX triggers CHECK-F2 FAIL."""
        doc = docx.Document(REAL_DOCX)
        for p in doc.paragraphs:
            p.text = re.sub(r"spatial\s+iou|explanation\s+fidelity|intersection\s+over\s+union", "bounding_accuracy", p.text, flags=re.I)
        for table in doc.tables:
            for row in table.rows:
                for cell in row.cells:
                    cell.text = re.sub(r"spatial\s+iou|explanation\s+fidelity|intersection\s+over\s+union", "bounding_accuracy", cell.text, flags=re.I)

        mut_docx_path = os.path.join(self.temp_dir, "mut_no_iou_docx.docx")
        doc.save(mut_docx_path)

        exit_code, out = self.run_verifier(["--docx-name", "mut_no_iou_docx.docx", "--md-name", "real.md"])
        self.record_test("T14: Synthetic Missing Spatial IoU in DOCX", 1, exit_code, "CHECK-F2   DOCX        5 Mathematical Formula Domains         FAIL", out)

    def test_docx_zero_tables(self):
        """Verify that a valid docx with 0 tables triggers CHECK-B FAIL ('0 Tables') and exits with 1."""
        doc = docx.Document()
        doc.add_heading("Autonomous Drone Navigation Documentation", level=0)
        doc.add_heading("1. Executive Summary", level=1)
        doc.add_paragraph("This is a document without tables.")
        doc_no_tbl_path = os.path.join(self.temp_dir, "no_tables.docx")
        doc.save(doc_no_tbl_path)

        exit_code, out = self.run_verifier(["--docx-name", "no_tables.docx", "--md-name", "real.md"])
        self.record_test("T15: Synthetic DOCX with Zero Tables Fails CHECK-B", 1, exit_code, "CHECK-B    DOCX        docx.Document OpenXML Parseability     FAIL", out)

    def test_missing_exec_summary_header_md(self):
        """Verify that replacing '# Chapter 1: Executive Summary' without replacement causes CHECK-D1 FAIL."""
        with open(REAL_MD, "r", encoding="utf-8") as f:
            md_text = f.read()

        mutated_text = md_text.replace("# Chapter 1: Executive Summary", "# Chapter 1: General Background")
        mut_path = os.path.join(self.temp_dir, "mut_no_exec_hdr.md")
        with open(mut_path, "w", encoding="utf-8") as f:
            f.write(mutated_text)

        exit_code, out = self.run_verifier(["--docx-name", "real.docx", "--md-name", "mut_no_exec_hdr.md"])
        self.record_test("T16: Renamed Executive Summary Header in MD Triggers Failure", 1, exit_code, "CHECK-D1   Markdown    6 Mandatory Chapter Headings           FAIL", out)

    def test_unanchored_regex_behavior(self):
        """
        Adversarial Analysis:
        Demonstrate that verify_documentation.py uses unanchored regexes.
        If the header '# Chapter 1: Executive Summary' is missing, but a casual sentence
        'This provides an executive summary of the system' is added to a paragraph,
        the unanchored regex matches and CHECK-D1 passes.
        """
        with open(REAL_MD, "r", encoding="utf-8") as f:
            md_text = f.read()

        # Replace header with casual prose
        mutated_text = md_text.replace("# Chapter 1: Executive Summary", "# Chapter 1: General Background\nHere is an executive summary in body text.")
        mut_path = os.path.join(self.temp_dir, "unanchored_demo.md")
        with open(mut_path, "w", encoding="utf-8") as f:
            f.write(mutated_text)

        exit_code, out = self.run_verifier(["--docx-name", "real.docx", "--md-name", "unanchored_demo.md"])
        self.record_test(
            "T17: Unanchored Regex Match on Casual Body Text (Structural Analysis)",
            0, exit_code, "ALL CHECKS PASSED (Exit Code 0)", out,
            notes="Identifies that verify_documentation.py matches substring rather than strict heading AST elements."
        )

    def run_all(self):
        print("=" * 90)
        print("STARTING ADVERSARIAL STRESS TEST SUITE FOR verify_documentation.py")
        print("=" * 90)
        try:
            self.test_baseline_real_files()
            self.test_missing_docx()
            self.test_missing_md()
            self.test_empty_docx()
            self.test_empty_md()
            self.test_corrupted_docx()
            self.test_word_count_threshold_high()
            self.test_word_count_truncated_files()
            self.test_missing_chapter_md()
            self.test_missing_chapter_docx()
            self.test_missing_audited_file_md()
            self.test_missing_audited_file_docx()
            self.test_missing_math_formula_md()
            self.test_missing_math_formula_docx()
            self.test_docx_zero_tables()
            self.test_missing_exec_summary_header_md()
            self.test_unanchored_regex_behavior()
        finally:
            self.cleanup()

        print("=" * 90)
        print(f"ADVERSARIAL SUITE SUMMARY: {self.tests_passed} PASSED, {self.tests_failed} FAILED (Total: {self.tests_passed + self.tests_failed})")
        print("=" * 90)
        return self.tests_failed == 0

if __name__ == "__main__":
    runner = AdversarialRunner()
    ok = runner.run_all()
    sys.exit(0 if ok else 1)
