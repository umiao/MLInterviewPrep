"""Replace the brief Reservoir Sampling section in Doc 21 with detailed version."""
import sqlite3
import sys

sys.stdout.reconfigure(encoding='utf-8')

DB_PATH = 'data/mle_prep.db'
STAGING_FILE = r'C:\Users\Shenghui Xu\Desktop\staging\LinkedIn蓄水池采样.md'


def main():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute('SELECT content FROM company_documents WHERE id=21')
    content = cur.fetchone()[0]

    with open(STAGING_FILE, encoding='utf-8') as f:
        new_rs = f.read()

    # Find section 12 boundaries
    start = content.find('## 12. Reservoir Sampling')
    end = content.find('\n## 13.', start)
    if start == -1 or end == -1:
        print('ERROR: Could not find section boundaries')
        return
    old_section = content[start:end]
    print(f'Old section length: {len(old_section)} chars')

    # Parse new content - skip title line
    lines = new_rs.split('\n')
    skip_to = 0
    for i, line in enumerate(lines):
        if line.startswith('> **'):
            skip_to = i
            break

    # Filter lines
    filtered = []
    in_toc = False
    in_ref = False
    for line in lines[skip_to:]:
        if line.strip() == '## 目录':
            in_toc = True
            continue
        if in_toc:
            if line.startswith('## 1.') or (line.startswith('---') and len(filtered) > 0):
                in_toc = False
                if line.startswith('---'):
                    continue
            else:
                continue
        if '## 参考文献' in line:
            in_ref = True
            continue
        if in_ref:
            continue
        # Adjust heading levels (add one # level since we're inside ## 12)
        if line.startswith('#### ') or line.startswith('### ') or line.startswith('## '):
            line = '#' + line
        filtered.append(line)

    # Remove trailing blank/--- lines
    while filtered and filtered[-1].strip() in ('', '---'):
        filtered.pop()

    # Build new section
    new_section = '## 12. Reservoir Sampling（蓄水池采样）详解\n\n'
    new_section += '\n'.join(filtered)
    new_section += '\n\n### 面试要点\n\n'
    new_section += '- **核心三算法**: 单元素采样 → Algorithm R（等权k个）→ A-Res（带权k个），逐步递进\n'
    new_section += '- **概率证明**: 必须能sketch数学归纳法证明，面试高频考点\n'
    new_section += '- **代码**: Algorithm R 核心逻辑10行以内，必须能快速手写\n'
    new_section += '- **Follow-up方向**:\n'
    new_section += '  - 分布式蓄水池采样（A-Res天然支持：各机器生成key，合并取top-k）\n'
    new_section += '  - Algorithm L跳跃优化（$N \\gg k$时从$O(N)$降到$O(k\\log(N/k))$）\n'
    new_section += '  - 滑动窗口采样（实时系统场景）\n'
    new_section += '- **实际工程**: 注意浮点精度（大权重时用log空间）、线程安全（独立Random实例）\n\n'

    new_content = content[:start] + new_section + content[end:]
    print(f'New section length: {len(new_section)} chars')
    print(f'Old total: {len(content)}, New total: {len(new_content)}')

    cur.execute('UPDATE company_documents SET content=? WHERE id=21', (new_content,))
    conn.commit()
    print('Doc 21 updated successfully')

    # Now update Doc 25 (All-in-One) - rebuild it by concatenating docs 21-24
    print('\nRebuilding Doc 25 (All-in-One)...')
    parts = []
    for doc_id in [21, 22, 23, 24]:
        cur.execute('SELECT title, content FROM company_documents WHERE id=?', (doc_id,))
        row = cur.fetchone()
        if row:
            parts.append(f'# {row[0]}\n\n{row[1]}')

    allinone = '\n\n---\n\n'.join(parts)
    header = '# LinkedIn MLE Prep: All-in-One\n\n'
    header += '> 本文档合并了所有LinkedIn面试准备笔记，便于统一复习。\n\n---\n\n'
    allinone_content = header + allinone

    cur.execute('UPDATE company_documents SET content=? WHERE id=25', (allinone_content,))
    conn.commit()
    print(f'Doc 25 updated: {len(allinone_content)} chars')

    conn.close()
    print('\nDone!')


if __name__ == '__main__':
    main()
