"""Create a LinkedIn interview questions index document as a prep note in company_documents.

User request: Create in LeetCode section, note company source, simple prep note format.
"""
import json
import sqlite3
import sys

sys.stdout.reconfigure(encoding='utf-8')

DB_PATH = 'data/mle_prep.db'
SEED_DIR = 'data/linkedin_seed'


def load_seed_questions():
    """Load all seed questions from JSON files."""
    categories = {
        'coding.json': 'Coding',
        'ml_theory_and_coding.json': 'ML Theory & Coding',
        'ml_system_design.json': 'ML System Design',
    }
    all_questions = []
    for fname, cat in categories.items():
        with open(f'{SEED_DIR}/{fname}', encoding='utf-8') as f:
            data = json.load(f)
        for q in data:
            q['_category'] = cat
        all_questions.extend(data)
    return all_questions


def extract_lc_ids(tags):
    """Extract LeetCode problem IDs from tags."""
    lc_ids = []
    for t in tags:
        if t.startswith('LC-'):
            lc_ids.append(t.replace('LC-', '').replace('-variant', '*'))
    return lc_ids


def build_question_entry(idx, q):
    """Build a markdown entry for one question."""
    tags = q.get('tags', [])
    lc_ids = extract_lc_ids(tags)
    non_lc_tags = [t for t in tags if not t.startswith('LC-')]
    difficulty = q.get('difficulty_estimate', 'unknown')
    interview_round = q.get('interview_round', '')
    notes = q.get('notes', '')

    # Title line
    lc_label = f" (LC {', '.join(lc_ids)})" if lc_ids else ""
    # Extract a short title from the question text
    qtext = q['question_text']
    short_title = qtext.split('.')[0].split('?')[0][:80]
    if len(short_title) < len(qtext.split('.')[0].split('?')[0]):
        short_title += '...'

    lines = []
    lines.append(f"### Q{idx}. {short_title}{lc_label}")
    lines.append("")
    lines.append(f"- **Company**: LinkedIn | **Round**: {interview_round or 'N/A'} | **Difficulty**: {difficulty}")
    lines.append(f"- **Tags**: {', '.join(non_lc_tags[:6])}")
    lines.append("")

    # Question summary (first 2 sentences)
    sentences = qtext.replace('\n', ' ').split('. ')
    summary = '. '.join(sentences[:2])
    if len(sentences) > 2:
        summary += '...'
    lines.append(f"**题目**: {summary}")
    lines.append("")

    # Solution key points from notes
    if notes:
        # Extract key insight or first meaningful section
        note_lines = notes.strip().split('\n')
        # Find "Key Insight" or first ### after title
        key_points = []
        in_section = False
        for nl in note_lines:
            if 'Key Insight' in nl or 'Core Idea' in nl or '核心' in nl:
                in_section = True
                continue
            if in_section:
                if nl.startswith('###') or nl.startswith('```'):
                    break
                if nl.strip():
                    key_points.append(nl.strip())
            # Also grab complexity lines
            if 'Time:' in nl or 'Space:' in nl or 'O(' in nl:
                if nl.strip() not in key_points:
                    key_points.append(nl.strip())

        if key_points:
            lines.append("**解法要点**:")
            for kp in key_points[:4]:
                if not kp.startswith('-'):
                    kp = f"- {kp}"
                lines.append(kp)
            lines.append("")

    # Follow-ups from question text (often embedded)
    followup_markers = ['follow-up', 'Follow up', 'Extension', 'extended version',
                        'What if', 'How would you handle', 'How would you modify']
    followups = []
    for marker in followup_markers:
        if marker.lower() in qtext.lower():
            # Extract the follow-up sentence
            idx_m = qtext.lower().find(marker.lower())
            fu_text = qtext[idx_m:idx_m+150].split('\n')[0]
            followups.append(fu_text)

    if followups:
        lines.append("**Follow-ups**:")
        for fu in followups[:3]:
            lines.append(f"- {fu}")
        lines.append("")

    lines.append("---")
    lines.append("")
    return '\n'.join(lines)


def main():
    questions = load_seed_questions()
    print(f"Loaded {len(questions)} questions from seed data")

    # Group by category
    by_cat = {}
    for q in questions:
        cat = q['_category']
        by_cat.setdefault(cat, []).append(q)

    # Build document
    doc_lines = []
    doc_lines.append("# LinkedIn Interview Questions Index")
    doc_lines.append("")
    doc_lines.append("> 本文档汇总LinkedIn面试中所有问到的题目，包含题目描述、解法要点、Follow-up和来源标注。")
    doc_lines.append("> 数据来源：一亩三分地面经整理 + LinkedIn seed data (47题)")
    doc_lines.append("")

    # TOC
    doc_lines.append("## 目录")
    doc_lines.append("")
    global_idx = 1
    for cat in ['Coding', 'ML Theory & Coding', 'ML System Design']:
        qs = by_cat.get(cat, [])
        doc_lines.append(f"- **{cat}** ({len(qs)} 题)")
        for q in qs:
            tags = q.get('tags', [])
            lc_ids = extract_lc_ids(tags)
            lc_label = f" (LC {', '.join(lc_ids)})" if lc_ids else ""
            short = q['question_text'].split('.')[0][:60]
            doc_lines.append(f"  - Q{global_idx}: {short}{lc_label}")
            global_idx += 1
    doc_lines.append("")
    doc_lines.append("---")
    doc_lines.append("")

    # Question entries
    global_idx = 1
    for cat in ['Coding', 'ML Theory & Coding', 'ML System Design']:
        qs = by_cat.get(cat, [])
        doc_lines.append(f"## {cat} ({len(qs)} 题)")
        doc_lines.append("")
        for q in qs:
            entry = build_question_entry(global_idx, q)
            doc_lines.append(entry)
            global_idx += 1

    # Stats summary
    doc_lines.append("## 统计")
    doc_lines.append("")
    doc_lines.append(f"- **总题数**: {len(questions)}")
    for cat in ['Coding', 'ML Theory & Coding', 'ML System Design']:
        doc_lines.append(f"- **{cat}**: {len(by_cat.get(cat, []))} 题")
    total_lc = sum(1 for q in questions if any(t.startswith('LC-') for t in q.get('tags', [])))
    doc_lines.append(f"- **有LeetCode编号的题目**: {total_lc}")
    doc_lines.append("")

    content = '\n'.join(doc_lines)
    print(f"Document length: {len(content)} chars")

    # Insert as new company_document for LinkedIn (company_id=1)
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    # Check if doc 26 exists or we need a new one
    cur.execute("SELECT MAX(id) FROM company_documents")
    max_id = cur.fetchone()[0]
    print(f"Current max document id: {max_id}")

    cur.execute("""INSERT INTO company_documents (company_id, title, content, source_type)
        VALUES (1, 'LinkedIn Interview Questions Index (全题目索引)', ?, 'prep_doc')""",
        (content,))
    new_id = cur.lastrowid
    conn.commit()
    print(f"Created document id={new_id}")

    # Verify
    cur.execute("SELECT id, title, length(content), source_type FROM company_documents WHERE id=?", (new_id,))
    row = cur.fetchone()
    print(f"Verified: id={row[0]}, title={row[1]}, length={row[2]}, type={row[3]}")

    conn.close()
    print("Done!")


if __name__ == '__main__':
    main()
