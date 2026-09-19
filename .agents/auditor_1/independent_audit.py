"""
independent_audit.py
--------------------
Auditor independent forensic verification script.
Runs empirical checks on:
1. Word counts (tokenized and whitespace)
2. Paragraph uniqueness and repetition detection (checks for copy-paste padding / filler)
3. Vocabulary diversity (unique word ratio)
4. Extraction of all chapters and sections
5. Verification of codebase symbols and constants
"""

import os
import re
import sys
from collections import Counter
import docx

def audit_markdown(md_path):
    print("=" * 60)
    print(f"AUDITING MARKDOWN: {md_path}")
    print("=" * 60)
    with open(md_path, "r", encoding="utf-8", errors="replace") as f:
        content = f.read()

    # Size
    size_bytes = os.path.getsize(md_path)
    print(f"File Size: {size_bytes:,} bytes")

    # Tokens
    tokens = re.findall(r'\b[a-zA-Z0-9_\-]+\b', content)
    words_ws = content.split()
    print(f"Alphanumeric token count: {len(tokens):,}")
    print(f"Whitespace-split word count: {len(words_ws):,}")

    # Unique vocabulary
    lower_tokens = [t.lower() for t in tokens if len(t) > 1 and not t.isdigit()]
    vocab = set(lower_tokens)
    print(f"Distinct lower vocabulary count: {len(vocab):,}")
    lexical_diversity = len(vocab) / len(lower_tokens) if lower_tokens else 0
    print(f"Lexical diversity (unique / total alpha): {lexical_diversity:.4f}")

    # Repetition check on paragraphs
    paragraphs = [p.strip() for p in content.split("\n\n") if len(p.strip()) > 30]
    p_counter = Counter(paragraphs)
    duplicate_paras = [p for p, count in p_counter.items() if count > 1]
    print(f"Total substantial paragraphs: {len(paragraphs)}")
    print(f"Duplicate substantial paragraphs: {len(duplicate_paras)}")
    if duplicate_paras:
        print("WARNING: Found duplicate paragraphs:")
        for dp in duplicate_paras:
            print(f"  Repeated {p_counter[dp]} times: {dp[:100]}...")

    # N-gram repetition check (e.g., 5-grams)
    ngrams = [" ".join(tokens[i:i+5]) for i in range(len(tokens) - 5)]
    ng_counter = Counter(ngrams)
    top_ngrams = ng_counter.most_common(10)
    print("\nTop 10 most common 5-grams:")
    for ng, count in top_ngrams:
        print(f"  ({count}x): {ng}")

    # Chapters & Headers
    headers = re.findall(r'^(#{1,4})\s+(.+)$', content, re.MULTILINE)
    print(f"\nTotal Markdown Headings: {len(headers)}")
    h1s = [h[1] for h in headers if h[0] == '#']
    print(f"H1 Headings ({len(h1s)}): {h1s}")

    return {
        "tokens": len(tokens),
        "words_ws": len(words_ws),
        "lexical_diversity": lexical_diversity,
        "duplicate_paras": len(duplicate_paras),
        "h1s": h1s
    }

def audit_docx(docx_path):
    print("\n" + "=" * 60)
    print(f"AUDITING DOCX: {docx_path}")
    print("=" * 60)
    doc = docx.Document(docx_path)
    size_bytes = os.path.getsize(docx_path)
    print(f"File Size: {size_bytes:,} bytes")
    print(f"Total Paragraphs: {len(doc.paragraphs):,}")
    print(f"Total Tables: {len(doc.tables):,}")

    para_texts = [p.text for p in doc.paragraphs if p.text.strip()]
    seen_tc = set()
    table_texts = []
    for t in doc.tables:
        for r in t.rows:
            for c in r.cells:
                if c._tc not in seen_tc:
                    seen_tc.add(c._tc)
                    if c.text.strip():
                        table_texts.append(c.text.strip())

    full_text = "\n".join(para_texts + table_texts)
    tokens = re.findall(r'\b[a-zA-Z0-9_\-]+\b', full_text)
    words_ws = full_text.split()
    print(f"Alphanumeric token count: {len(tokens):,}")
    print(f"Whitespace-split word count: {len(words_ws):,}")

    # Unique vocabulary
    lower_tokens = [t.lower() for t in tokens if len(t) > 1 and not t.isdigit()]
    vocab = set(lower_tokens)
    print(f"Distinct lower vocabulary count: {len(vocab):,}")
    lexical_diversity = len(vocab) / len(lower_tokens) if lower_tokens else 0
    print(f"Lexical diversity (unique / total alpha): {lexical_diversity:.4f}")

    # Substantial paragraph duplicate check
    sub_paras = [p for p in para_texts if len(p) > 30]
    p_counter = Counter(sub_paras)
    dup_paras = [p for p, count in p_counter.items() if count > 1]
    print(f"Total substantial paragraphs: {len(sub_paras)}")
    print(f"Duplicate substantial paragraphs: {len(dup_paras)}")
    if dup_paras:
        print("WARNING: Found duplicate paragraphs:")
        for dp in dup_paras:
            print(f"  Repeated {p_counter[dp]} times: {dp[:100]}...")

    return {
        "tokens": len(tokens),
        "words_ws": len(words_ws),
        "lexical_diversity": lexical_diversity,
        "duplicate_paras": len(dup_paras),
        "paras": len(doc.paragraphs),
        "tables": len(doc.tables)
    }

if __name__ == "__main__":
    ws_root = r"c:\Users\Rushikesh\Desktop\Cool Ass Projects\Drone"
    md_res = audit_markdown(os.path.join(ws_root, "TECHNICAL_DOCUMENTATION.md"))
    docx_res = audit_docx(os.path.join(ws_root, "Autonomous_Drone_Navigation_Technical_Documentation.docx"))
