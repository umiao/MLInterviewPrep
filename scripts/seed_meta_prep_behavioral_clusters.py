"""Seed: T-P1-803 [KG-INT B3-1] -- meta-prep/behavioral-clusters child nodes.

Distills cross-company behavioral patterns from the 11 P0+P1 companies'
prose surfaces (S1 prep_notes, S2 notes, S3 company_documents) into
shared `meta-prep/behavioral-clusters/<slug>` framework_nodes per the
promotion threshold locked in `docs/workflow/promotion_criteria.md`
(>=3 of 11 P0+P1 companies AND de-companiable wording).

Seven story clusters were extracted -- six story-type clusters plus one
delivery-framework cluster (STAR / STAR-T / STARR), each surfacing in
3+ companies' BQ surfaces. Source surfaces audited:

  LinkedIn   S3 doc id=23  ([合集] BQ + Product Sense -- 7 STAR-T templates)
  Meta       S3 doc id=88  ([Meta] AI-Native Behavioral 5-Pack)
  Pinterest  S3 doc id=48  (Pinterest BQ Question Map -- 5 questions)
  Google     S3 doc id=38, 51 (Recruiter Call + R1/R2 BQ shortlists)
  Adobe      S3 doc id=16  (Day6 STAR-T 3 project stories) + S1 prep_notes
  Uber       S3 doc id=36, 37, 50 (HR + VO + BPS) + S1 prep_notes
  DoorDash   S3 doc id=4   (R1 Project Deep Dive Prep)
  Slack      S3 doc id=59  (HR Call STARR pitches)
  TikTok     S1 prep_notes (project showcase line)
  PARSPEC    S2 notes only (no behavioral surface; not a sources_company)

The parent stub `meta-prep/behavioral-clusters` (T-P1-800) had a
`TODO[KG-INT-B3-1]` marker in description. This seed updates that
description to a real one-line summary now that the children exist.

Each child node populates `relevant_companies` (the framework_nodes
column closest to the AC's "sources_companies" field; comma-separated
company names matching existing convention -- see
`pillar1.mle_coding.implement_ml_algorithms.relevant_companies =
'LinkedIn,Uber,Adobe'`). Each list has >=3 P0+P1 names per the
promotion threshold.

Safety:
  1. SHA-256 of the `meta-prep/behavioral-clusters` subtree captured
     pre/post for audit.
  2. Refuses to run if any target child path already exists with a
     DIFFERENT title (protects against accidental overwrite of human
     edits).
  3. Idempotent: re-run yields inserted=0, updated=0, skipped=8
     (1 parent + 7 children).
  4. Parent description is UPDATED only on the first run (when it still
     contains the `TODO[KG-INT-B3-1]` marker). Subsequent runs SKIP
     the parent.
  5. Post-run invariant: exactly 8 rows match path = 'meta-prep/behavioral-clusters'
     OR path LIKE 'meta-prep/behavioral-clusters/%'.
  6. AC check: each child's relevant_companies splits to >=3 entries,
     all of which are valid P0+P1 company names from the locked list.

Usage:
    python scripts/seed_meta_prep_behavioral_clusters.py
"""
from __future__ import annotations

import hashlib
import sqlite3
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
DB_PATH = REPO_ROOT / "data" / "mle_prep.db"

PARENT_PATH = "meta-prep/behavioral-clusters"
PARENT_TITLE = "Behavioral Story Clusters"
PARENT_DESCRIPTION_NEW = (
    "跨公司 behavioral round 收集到的高频 story clusters 共享底座 "
    "(shared substrate from 8 of 11 P0+P1 companies' BQ surfaces). "
    "子节点按 cluster 拆分: 每个 cluster 列出 trigger questions、"
    "STAR (Situation-Task-Action-Result) 框架 plays、common follow-ups、"
    "以及该 cluster 在哪些 P0+P1 公司被显式 prep 过 (relevant_companies). "
    "Authoring per-company 故事时, 优先复用此处的 framework + plays, "
    "company-specific framing (e.g., Amazon LP / Google Googleyness / "
    "Uber Cultural Norms) 留在 pillar8.company_specific 子树."
)
PARENT_TODO_MARKER = "TODO[KG-INT-B3-1]"

P0P1_COMPANY_NAMES = {
    "LinkedIn", "DoorDash", "Google", "Uber", "Adobe",
    "TikTok", "Slack", "PARSPEC", "Pinterest", "Meta",
}

CLUSTERS: list[tuple[str, str, str, list[str]]] = [
    (
        "conflict-resolution-cross-team",
        "Conflict Resolution / Cross-Team Disagreement",
        "跨组或跨 org 的技术方案 / policy / 资源分配冲突. "
        "Trigger questions: 'Tell me about a conflict with another team', "
        "'How did you handle disagreement with a stakeholder', "
        "'Cross-functional collaboration that broke down'. "
        "STAR (Situation-Task-Action-Result) plays: "
        "(1) 主动约对方 tech lead 1:1 先 listen 再推方案, 不在 group 会议上 escalate; "
        "(2) 双方约束写成 shared doc, 用 fact (latency / cost / SLA) 替 opinion 对齐; "
        "(3) 提 compromise + sunset window (e.g., 过渡期同时支持两 schema 3 个月); "
        "(4) escalate via shared manager 是最后一步, 不是第一步. "
        "Anti-patterns: 'I was right, they were wrong' framing; 把冲突归咎于个人; "
        "在没 own data 之前 escalate. Common follow-up: "
        "'What if the other team simply refuses?' -- escalate with quantified "
        "downstream impact, but document the risk in writing first.",
        ["LinkedIn", "Meta", "Google", "Uber", "Pinterest"],
    ),
    (
        "project-ownership-end-to-end",
        "End-to-End Project Ownership with Quantified Impact",
        "从 problem discovery -> 方案选型 -> production launch -> "
        "post-launch monitoring 全链路 own 的项目 + 量化 business impact. "
        "Trigger questions: 'Most proud project', 'Project you owned end-to-end', "
        "'Tell me about a project that had real impact'. STAR plays: "
        "(1) Result 必须 quantified -- CTR / engagement / GMB / latency / "
        "recall@k 的具体百分比 + 用户量级; (2) Action 用 'I' 不用 'we', "
        "区分 own contribution vs team contribution; "
        "(3) 显式提至少一个 rejected alternative + 拒绝原因 (展示 judgment, "
        "不是 only-path mindset); (4) Mention guardrail metrics 而不只是 "
        "north-star (latency, crash rate, fairness, regression rate). "
        "Anti-patterns: 只讲 technical detail 忘记 business impact; "
        "vague 'we improved' 没具体数字; cherry-pick metric 而不报 trade-off. "
        "Common follow-ups: 'What if A/B was insignificant?' -- segment 切片找差异; "
        "'How would you 10x this?' -- 答 infra bottleneck 不是 model bottleneck.",
        ["LinkedIn", "Pinterest", "Meta", "Adobe", "Uber", "DoorDash", "Google"],
    ),
    (
        "ambiguity-self-initiated",
        "Ambiguity / Self-Initiated Direction Under No Mandate",
        "没人派活, 自己从 data / log / dashboard 挖出 invisible failure 并 "
        "self-scope project. Trigger questions: 'Tell me about a time you "
        "saw something nobody else noticed', 'Self-initiated project', "
        "'How do you decide what to work on under ambiguity'. STAR plays: "
        "(1) Abandon-log slice / drop-off slice 找 silent failure -- dashboard "
        "看着健康但 dominant-user cohort 健康, missing-half 用户 invisible; "
        "(2) Hacker Week / 20% time prototype 验证 hypothesis 在不动 funded "
        "scope 的情况下; (3) ROI math feasibility kill -- 在 1 周内用 "
        "QPS / latency / integration cost 算出 bad path 然后 disqualify, "
        "在 sunk cost 让 kill 政治成本变高之前; (4) 把 framing diagnosis "
        "(per-item healthy vs page-level homogeneity 这种 structural gap) "
        "写成 1-pager pitch 给 manager. Anti-patterns: 默认接受 'no scope' "
        "等同 'no work'; 在没 prototype 之前先要 funded headcount. "
        "Match-question hints: 'Used data to identify problem others missed', "
        "'Challenged the default', 'Moved fast with incomplete information'.",
        ["Meta", "Pinterest", "Google"],
    ),
    (
        "technical-leadership-mentorship",
        "Technical Leadership / Mentorship / Influence Without Authority",
        "Mentor 初级 IC / 带小团队 / 跨组影响但没 formal manager 权限. "
        "Trigger questions: 'Tell me about a time you led without authority', "
        "'Mentored a junior engineer', 'Brought a junior up to speed', "
        "'Influenced an org-level decision as IC'. STAR plays: "
        "(1) Structured onboarding -- 详细 runbook + codebase walkthrough + "
        "pair programming 前两周; (2) Modular project split -- 每人 own 独立 "
        "module 降低耦合, weekly code review 节奏; "
        "(3) 卡住时 pair-debug 一整天 + 写 internal 排查文档 (让别人成功 vs "
        "只展示自己技术); (4) Specific feedback + actionable plan, "
        "不止说 'good work' 或 'needs improvement'. Anti-patterns: "
        "'我一个人做完了所有事' 隐含 mentee 没贡献; 没 quantified mentee "
        "growth (e.g., promotion / exceeds-expectations rating). Common "
        "follow-up: 'What if the mentee under-performs?' -- 给 clear feedback + "
        "actionable plan, 仍不改善 align with their manager.",
        ["LinkedIn", "Google", "Uber", "Adobe"],
    ),
    (
        "failure-and-difficult-feedback",
        "Failure / Setback / Receiving Difficult Feedback",
        "项目失败 / mentorship 失败 / 收到 senior IC 或 manager 的 harsh "
        "feedback. Trigger questions: 'Tell me about a time you failed', "
        "'Difficult feedback you received', 'Project that didn't work', "
        "'Setback and what you learned'. STAR plays: "
        "(1) 不 defensive -- 先认 fact, 再讲 root cause analysis; "
        "(2) 把 critique 转 process -- e.g., PR-flow 不规范的 feedback 转成 "
        "team-level checklist 制度, code-review template; "
        "(3) Specific behavior change (不是 vague 'I learned to be careful'); "
        "(4) End with 'what I'd do differently' -- 具体 tactic 不是 attitude. "
        "Anti-patterns: 把 failure 归咎于 external (timing / market / team); "
        "选 too-small failure 让 interviewer 觉得 self-aware 不够; 直接复述 "
        "feedback 没 internalize. Common follow-ups: 'What was your role in it?' -- "
        "owning 50%+ 的 contribution to failure (即使不是 solo project); "
        "'Did you push back?' -- 区分 push-back-with-data vs push-back-with-ego.",
        ["LinkedIn", "Pinterest", "Google", "Meta"],
    ),
    (
        "prioritization-tight-deadline",
        "Prioritization / Tight Deadline / Resource Triage",
        "同时 3+ task 撞到一起 + tight deadline + 人力不足. Trigger "
        "questions: 'Tight deadline you faced', 'Competing priorities', "
        "'How do you prioritize when everything is on fire'. STAR plays: "
        "(1) 2x2 impact-urgency matrix 做 explicit ranking, 不是拍脑袋; "
        "(2) 与 manager align top priority -- 明确 cut-line 在哪 (which tasks "
        "可以推迟 / 委托 / 直接 drop); (3) 委托 routine 部分给队友, "
        "self-focus 在 high-impact 上; (4) 每天下午 sync 进度让 manager "
        "及时 reroute, 不是 silent 死扛 7 天再说; (5) 答 'what I cut' 而不是 "
        "'I worked harder' -- 后者 signal poor judgment. Anti-patterns: "
        "'我加班熬夜全做完了' (interviewer 想看 trade-off 能力, 不是 grit); "
        "没 explicit 'what got dropped' (说明 didn't actually prioritize). "
        "Common follow-up: 'What if manager disagrees with your priority?' -- "
        "用 quantified impact 展示差异, 最终 respect manager 的决定但 record "
        "the risk in writing.",
        ["LinkedIn", "Pinterest", "Meta"],
    ),
    (
        "storytelling-framework-starr",
        "STAR / STAR-T / STARR Delivery Framework",
        "Behavioral round 的标准 delivery 格式 -- 不是一个 story type, 是讲 "
        "story 的协议. STAR (Situation-Task-Action-Result) 是 base; "
        "STAR-T 加 Transfer (桥接到 target 公司的产品 / charter); "
        "STARR 加 second R = Reflection (what I learned + what I'd do "
        "differently). Required elements: "
        "(1) Total 控制在 2-3 min spoken (~120-180 sec); "
        "(2) Action 部分占 60-70% 时长 (这是 interviewer 真正想 probe 的); "
        "(3) Result 必须 quantified -- 百分比 / 用户量级 / latency 数字; "
        "(4) 'I' 不 'we' -- 显式 separate own contribution vs team contribution; "
        "(5) Mention 至少一个 considered-but-rejected alternative (展示 "
        "judgment); (6) Transfer 句要 specific 不能 generic -- 引用 target "
        "公司的具体产品 / infra / charter, 不只是 'this would help your team'. "
        "Anti-patterns: 5-min 项目深讲 (HR call 30 sec - 2 min cap); only "
        "technical detail 没 business impact; 'we' 全篇没 'I'. "
        "Per-company STAR variants: Google = Top 20 BQ x 3 STARs each; "
        "Uber = STARR + 8 cultural norms 映射; Pinterest = post-rework EX-XX "
        "格式 (metric 具象化 + Action I-化); Adobe = STAR-T + 'why Adobe' "
        "transfer; LinkedIn = STAR-T 重 mentorship/ knowledge-transfer angle.",
        ["LinkedIn", "Adobe", "Uber", "Google", "Slack", "Pinterest"],
    ),
]


def sha256_subtree(conn: sqlite3.Connection) -> str:
    """SHA-256 of all 'meta-prep/behavioral-clusters%' rows, ordered by path."""
    rows = conn.execute(
        "SELECT path, depth, title, description, relevant_companies "
        "FROM framework_nodes "
        "WHERE path = ? OR path LIKE 'meta-prep/behavioral-clusters/%' "
        "ORDER BY path",
        (PARENT_PATH,),
    ).fetchall()
    h = hashlib.sha256()
    for r in rows:
        h.update(repr(r).encode("utf-8"))
    return h.hexdigest()


def update_parent_description(
    conn: sqlite3.Connection, parent_id: int, current_desc: str | None
) -> str:
    """Update parent description if still TODO; otherwise SKIP.

    Returns 'UPDATED' or 'SKIPPED'.
    """
    if current_desc and PARENT_TODO_MARKER in current_desc:
        conn.execute(
            "UPDATE framework_nodes SET description = ? WHERE id = ?",
            (PARENT_DESCRIPTION_NEW, parent_id),
        )
        return "UPDATED"
    if current_desc == PARENT_DESCRIPTION_NEW:
        return "SKIPPED"
    raise RuntimeError(
        f"[CONFLICT] parent description has been edited to something "
        f"other than the TODO marker or the seed's target text. "
        f"Refusing to overwrite. Current: {current_desc!r}"
    )


def upsert_child(
    conn: sqlite3.Connection,
    *,
    parent_id: int,
    slug: str,
    title: str,
    description: str,
    relevant_companies_csv: str,
) -> tuple[str, int]:
    """Insert child if absent; SKIP if present with matching title+description+companies.

    Refuses to overwrite a child whose title/description/companies have
    been edited away from the seed (someone hand-tuned it).
    """
    path = f"{PARENT_PATH}/{slug}"
    existing = conn.execute(
        "SELECT id, title, description, relevant_companies "
        "FROM framework_nodes WHERE path = ?",
        (path,),
    ).fetchone()
    if existing is not None:
        node_id, ex_title, ex_desc, ex_companies = existing
        if (ex_title == title and ex_desc == description
                and (ex_companies or "") == relevant_companies_csv):
            return "SKIPPED", node_id
        raise RuntimeError(
            f"[CONFLICT] path={path!r} exists but content has drifted from "
            f"seed. title_match={ex_title == title} "
            f"desc_match={ex_desc == description} "
            f"companies_match={(ex_companies or '') == relevant_companies_csv}. "
            f"Refusing to overwrite hand-edited content; resolve by either "
            f"reverting the edit or updating the seed."
        )
    cur = conn.execute(
        """
        INSERT INTO framework_nodes
            (parent_id, path, depth, title, description,
             importance, priority, status, progress_pct, relevant_companies)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (parent_id, path, 2, title, description,
         0.7, "P1", "not_started", 0.0, relevant_companies_csv),
    )
    return "INSERTED", cur.lastrowid


def assert_promotion_threshold() -> None:
    """Static AC check: every cluster has >=3 P0+P1 sources, all valid names."""
    for slug, _title, _desc, companies in CLUSTERS:
        if len(companies) < 3:
            raise AssertionError(
                f"[AC-FAIL] cluster {slug!r} has only "
                f"{len(companies)} sources; promotion threshold is >=3"
            )
        if len(companies) != len(set(companies)):
            raise AssertionError(
                f"[AC-FAIL] cluster {slug!r} has duplicate sources: "
                f"{companies}"
            )
        invalid = set(companies) - P0P1_COMPANY_NAMES
        if invalid:
            raise AssertionError(
                f"[AC-FAIL] cluster {slug!r} references non-P0+P1 "
                f"companies: {sorted(invalid)}"
            )


def seed(conn: sqlite3.Connection) -> dict[str, int]:
    """Update parent description (if TODO) and seed 7 child clusters."""
    counts = {"INSERTED": 0, "UPDATED": 0, "SKIPPED": 0}

    parent = conn.execute(
        "SELECT id, description FROM framework_nodes WHERE path = ?",
        (PARENT_PATH,),
    ).fetchone()
    if parent is None:
        raise RuntimeError(
            f"[FAIL] parent {PARENT_PATH!r} does not exist; "
            f"run scripts/seed_meta_prep_pillar.py first (T-P1-800)."
        )
    parent_id, parent_desc = parent
    parent_action = update_parent_description(conn, parent_id, parent_desc)
    counts[parent_action] += 1
    print(f"[{parent_action}] parent id={parent_id} path={PARENT_PATH}")

    for slug, title, description, companies in CLUSTERS:
        relevant_companies_csv = ",".join(companies)
        action, child_id = upsert_child(
            conn,
            parent_id=parent_id,
            slug=slug,
            title=title,
            description=description,
            relevant_companies_csv=relevant_companies_csv,
        )
        counts[action] += 1
        print(
            f"[{action}] child  id={child_id} "
            f"slug={slug} sources={len(companies)}"
        )

    return counts


def main() -> None:
    if not DB_PATH.exists():
        print(f"[FAIL] DB not found: {DB_PATH}")
        sys.exit(1)

    assert_promotion_threshold()
    print("[AC-OK] all 7 clusters have >=3 valid P0+P1 sources")

    conn = sqlite3.connect(str(DB_PATH))
    try:
        pre_hash = sha256_subtree(conn)
        print(f"[PRE]  sha256={pre_hash}")

        counts = seed(conn)
        conn.commit()

        post_hash = sha256_subtree(conn)
        print(f"[POST] sha256={post_hash}")

        total = conn.execute(
            "SELECT COUNT(*) FROM framework_nodes "
            "WHERE path = ? OR path LIKE 'meta-prep/behavioral-clusters/%'",
            (PARENT_PATH,),
        ).fetchone()[0]
    finally:
        conn.close()

    print(
        f"[SUMMARY] inserted={counts['INSERTED']} "
        f"updated={counts['UPDATED']} "
        f"skipped={counts['SKIPPED']} "
        f"total_in_subtree={total}"
    )

    expected_total = 1 + len(CLUSTERS)
    if total != expected_total:
        print(f"[FAIL] Expected {expected_total} rows, got {total}")
        sys.exit(1)
    touched = counts["INSERTED"] + counts["UPDATED"] + counts["SKIPPED"]
    if touched != expected_total:
        print(f"[FAIL] Expected to touch {expected_total} nodes, touched {touched}")
        sys.exit(1)
    print("[DONE]")


if __name__ == "__main__":
    main()
