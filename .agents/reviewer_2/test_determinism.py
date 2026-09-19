"""
Test Determinism of generate_docx.py
"""
import subprocess
import hashlib
import os

def hash_file(filepath):
    h = hashlib.sha256()
    with open(filepath, "rb") as f:
        while chunk := f.read(8192):
            h.update(chunk)
    return h.hexdigest()

def test_determinism():
    docx_path = r"c:\Users\Rushikesh\Desktop\Cool Ass Projects\Drone\Autonomous_Drone_Navigation_Technical_Documentation.docx"
    md_path = r"c:\Users\Rushikesh\Desktop\Cool Ass Projects\Drone\TECHNICAL_DOCUMENTATION.md"
    
    # 1st run
    res1 = subprocess.run(["python", "generate_docx.py"], capture_output=True, text=True)
    sz_docx_1 = os.path.getsize(docx_path)
    sz_md_1 = os.path.getsize(md_path)
    hash_md_1 = hash_file(md_path)
    
    # 2nd run
    res2 = subprocess.run(["python", "generate_docx.py"], capture_output=True, text=True)
    sz_docx_2 = os.path.getsize(docx_path)
    sz_md_2 = os.path.getsize(md_path)
    hash_md_2 = hash_file(md_path)
    
    print(f"Run 1: DOCX Size={sz_docx_1:,} bytes, MD Size={sz_md_1:,} bytes, MD SHA256={hash_md_1}")
    print(f"Run 2: DOCX Size={sz_docx_2:,} bytes, MD Size={sz_md_2:,} bytes, MD SHA256={hash_md_2}")
    
    assert sz_docx_1 == sz_docx_2, "DOCX size mismatch between runs"
    assert sz_md_1 == sz_md_2, "MD size mismatch between runs"
    assert hash_md_1 == hash_md_2, "MD hash mismatch between runs"
    print("Determinism test PASSED successfully!")

if __name__ == "__main__":
    test_determinism()
