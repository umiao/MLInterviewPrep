"""Seed: T-P1-807 [KG-INT B3-5] -- meta-prep/onsite-loop-templates children.

Distills shared onsite loop *templates* (full pipeline shapes and round-type
playbooks) from the 10 P0+P1 companies' prep surfaces (`company_documents` of
kind prep_note / hub_doc) into shared `meta-prep/onsite-loop-templates/<slug>`
framework_nodes per the promotion threshold locked in
`docs/workflow/promotion_criteria.md` (>=3 of 11 P0+P1 companies AND
de-companiable wording).

A grep-driven coverage scan was run across the loop-structure prose of the 10
P0+P1 companies (LinkedIn ids=22/23/26 SD + BQ + LC indices; DoorDash ids=4/41
domain prep + master; Google ids=38/53/92 recruiter call + R2 coding index +
prep hub; Uber ids=36/37/50 HR call + VO guide + phone screen; Pinterest
ids=39/83 recruiter call + ML VO prep; Adobe id=17 phone screen day7; Slack
id=59 HR call; Meta id=82 AI-Native onsite hub). Five templates cleared the
>=3 P0+P1 threshold AND the "meaningful instance" judgment (round structure
prose with timing / evaluator / evaluation axes / anti-patterns, not just
word-frequency mentions). The 5 child templates:

  1. standard-4-round-mle-vo  (loop body shape) -- Google/LinkedIn/Meta/
     Pinterest/Uber
  2. pre-loop-recruiter-and-tech-screen  (loop prefix) -- Adobe/Google/
     LinkedIn/Pinterest/Slack/Uber
  3. ml-system-design-round  (single-round playbook) -- Google/LinkedIn/Meta/
     Pinterest/Slack/Uber
  4. behavioral-bq-round  (single-round playbook) -- DoorDash/Google/LinkedIn/
     Meta/Pinterest/Slack/Uber
  5. project-deep-dive-round  (single-round playbook) -- DoorDash/LinkedIn/
     Pinterest/Slack

Each child node embeds:
  - Round / loop scope + typical timing (e.g. "60min single round" or
    "4 rounds totaling 4h") + position in pipeline
  - Evaluation axes (what the interviewer scores) + 3-5 sample question shapes
  - Round structure / playbook (the "how" once you're in the round)
  - Cross-links via kg://N (framework_nodes.id) for adjacent KG nodes
  - Top failure modes / interview anti-patterns
  - relevant_companies CSV listing the >=3 P0+P1 sources

The parent stub `meta-prep/onsite-loop-templates` (T-P1-800) had a
`TODO[KG-INT-B3-5]` marker. This seed updates the parent description to a
real summary on first run.

Scope decision (which templates made the cut):
  Hard-promoted (>=3 P0+P1, distinct loop-structure signal):
    standard-4-round-mle-vo, pre-loop-recruiter-and-tech-screen,
    ml-system-design-round, behavioral-bq-round, project-deep-dive-round.
  Soft-rejected (passes word-frequency but not "meaningful instance"):
    "team match round" (n=2: Pinterest + Uber explicit -- below threshold;
    deferred to T-P1-821 B4-promotion if >=1 more P0+P1 surfaces it),
    "hiring committee debrief" (n=1 explicit: Google implicit -- below
    threshold), "5-round extended loop with cross-functional" (n=2: Meta +
    Uber -- below threshold; the 4-round-VO template covers the common
    shape and the 5th round is company-specific framing).

Safety:
  1. SHA-256 of the `meta-prep/onsite-loop-templates` subtree captured
     pre/post.
  2. Refuses to overwrite a child whose title/description/companies have
     drifted from this seed (someone hand-edited it).
  3. Idempotent: re-run yields inserted=0, updated=0, skipped=6
     (1 parent + 5 children).
  4. Parent description UPDATED only on first run (TODO marker present).
  5. Post-run invariant: exactly 6 rows match
     path = 'meta-prep/onsite-loop-templates' OR
     path LIKE 'meta-prep/onsite-loop-templates/%'.
  6. AC checks:
       - children count >= 3 (task spec)
       - each child has >=3 valid P0+P1 sources in relevant_companies
       - description contains at least one kg:// cross-link
       - description contains a "structural diagram" cue (round-by-round
         table OR pipeline arrow chain) -- enforced via STRUCT_DIAGRAM_RE

Usage:
    python scripts/seed_meta_prep_onsite_loop_templates.py
"""
from __future__ import annotations

import hashlib
import re
import sqlite3
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
DB_PATH = REPO_ROOT / "data" / "mle_prep.db"

PARENT_PATH = "meta-prep/onsite-loop-templates"
PARENT_TITLE = "Onsite Loop Templates"
PARENT_DESCRIPTION_NEW = (
    "跨公司 onsite loop 通用 template 与 round-type playbook (shared "
    "loop-structure substrate, distilled from 10 P0+P1 companies' loop-prose "
    "surfaces). 子节点按**两个维度**拆分: (1) **pipeline-level shape** -- "
    "整个面试流水线的形状 (e.g. standard-4-round-mle-vo 描述 onsite 主体 4 "
    "轮的典型 layout; pre-loop-recruiter-and-tech-screen 描述 recruiter "
    "call + tech screen 的 2 步 prefix); (2) **single-round playbook** -- "
    "某一轮的执行 template (e.g. ml-system-design-round 的 60min "
    "requirement-gather -> retrieval -> ranking -> serving -> monitoring "
    "checklist; behavioral-bq-round 的 STAR-T 5-pack 结构; "
    "project-deep-dive-round 的 4-axis framing/feature/deploy/eval drill). "
    "每个子节点带: 轮次 scope + 时长 (e.g. 60min) + 在 pipeline 中的位置 + "
    "评估 axes (interviewer 给分点) + sample question shapes + standard "
    "round playbook + kg://N cross-links (指向 pillar1 / behavioral / SD "
    "邻接节点) + anti-patterns. 这是 onsite-prep round (R0/R1/onsite 主体 "
    "+ post-onsite) 的**结构索引层** -- 看到 'XX 公司 onsite 4 轮' 先映射到 "
    "对应 template, 再用 round-level playbook 起手. 不是公司具体面试题库 "
    "(题在 problems / company_documents 表), 而是 loop-shape -> playbook "
    "的 router."
)
PARENT_TODO_MARKER = "TODO[KG-INT-B3-5]"

P0P1_COMPANY_NAMES = {
    "LinkedIn", "DoorDash", "Google", "Uber", "Adobe",
    "TikTok", "Slack", "PARSPEC", "Pinterest", "Meta",
}

# Each tuple: (slug, title, description, [companies])
# Description must embed at least one kg://N or sd://slug cross-link AND
# a "structural diagram" cue (a round-by-round '|' table OR an arrow chain).
TEMPLATES: list[tuple[str, str, str, list[str]]] = [
    (
        "standard-4-round-mle-vo",
        "Standard 4-Round MLE Virtual Onsite (Loop Body)",
        "MLE / Senior MLE 标准 onsite **主体 4 轮** 的 canonical pipeline "
        "shape. 4 轮总 ~4h (含 break), 每轮 60min (Pinterest 风格里 DSA "
        "缩到 45min×2 + 60min×3 是变体). **Round-by-round 结构**:\n\n"
        "| Round | 类型 | 时长 | 评估 axes | 高频信号 |\n"
        "|-------|------|------|-----------|----------|\n"
        "| 1 | Coding (DSA / LC) | 60min | algorithm choice / "
        "Big-O / clean code / corner cases | sliding-window / DP / graph |\n"
        "| 2 | ML Coding (from-scratch / data manipulation) | 60min | "
        "numpy 熟练度 / 算法原理 / numerical stability | k-means / "
        "logreg / linreg from scratch (no sklearn) |\n"
        "| 3 | ML System Design | 60min | requirement gather / "
        "tradeoff articulation / scale-aware choice | recsys / search / "
        "ads / fraud |\n"
        "| 4 | Behavioral (BQ) | 45-60min | leadership / conflict / "
        "ownership / quantified impact | STAR-T 5-pack |\n\n"
        "**Pipeline 位置**: recruiter call -> tech screen (1-2 轮) -> "
        "**this 4-round VO** -> debrief / hiring committee -> "
        "(team match) -> offer. 这 4 轮是 'pipeline 主体', 通过 = 推到 "
        "下一阶段. **Variants**: (a) Pinterest 拆 R1 成 2 场 DSA 各 "
        "45min, 加 1 场 Competency/HM; (b) Meta AI-native 把 R1+R2 "
        "合并成 2 场 'AI-Native Coding' (60min code-pad + LLM 协同) + "
        "1 场 ML SD + 1 场 BQ; (c) Google 把 R1 拆成 'ML Fundamentals' "
        "(R1) + 'Coding' (R2), 共 R1-R4 4 轮; (d) Uber 在 4 轮之外加 "
        "1 场 HR call (~30min); 主体仍是 4 轮. **Trigger phrase**: "
        "'4 rounds onsite', '4-hour virtual loop', '主体 4 轮 + HR'. "
        "**Round-level playbook 子节点 (cross-link)**: kg://243 (parent "
        "onsite-loop-templates), ml-system-design-round (sibling), "
        "behavioral-bq-round (sibling), project-deep-dive-round "
        "(sibling). **General KG 邻接**: kg://1 (pillar1 Coding & "
        "Algorithms), kg://2 (pillar2 ML System Design), "
        "kg://5 (pillar5 Behavioral). **Anti-patterns**: 把 4 轮当成 "
        "'4 个独立 LC' 备 (R3/R4 完全不同 axes); R2 ML coding 用 "
        "sklearn 一行 (面试官想看 numpy from-scratch 实现); R3 SD 直接 "
        "画架构图不先 gather requirement (latency / scale / cold-start "
        "三问没问出来 = 失分); R4 BQ 讲项目细节不讲 leadership signal "
        "(讲了 100 行代码但没讲 conflict resolution / mentorship / "
        "quantified business impact).",
        ["Google", "LinkedIn", "Meta", "Pinterest", "Uber"],
    ),
    (
        "pre-loop-recruiter-and-tech-screen",
        "Pre-Loop: Recruiter Call + Tech Screen (Pipeline Prefix)",
        "Onsite 主 loop **之前**的 2-step pipeline prefix, ~25% 候选人 "
        "在这阶段被刷掉. **Two-step structural diagram** "
        "(recruiter call -> tech screen -> onsite invite -> [ 4-round VO "
        "loop body, 见 standard-4-round-mle-vo ]):\n\n"
        "| Step | 类型 | 时长 | 主考 | 评估 axes |\n"
        "|------|------|------|------|-----------|\n"
        "| 0a | Recruiter / HR Phone Screen | 25-45min | Recruiter | "
        "background fit / why-company / comp ballpark / loop preview |\n"
        "| 0b | Tech Screen (Coding) | 45-60min | IC engineer | LC "
        "medium / 1-2 道题 / clean code / clarify before typing |\n\n"
        "**Step 0a (recruiter call)** 内容标配: (1) self-intro 60-90sec "
        "English (current role + signature project + why exploring); "
        "(2) why-this-company (3-5 specific points, 别只说 'great team'); "
        "(3) comp + timeline + visa (recruiter 主导节奏); (4) "
        "candidate's questions (准备 3-5 个 about team / role / "
        "interview loop, 不是 'when do I hear back'). Mindset: 'first "
        "formal interview round', 不是聊天. **Step 0b (tech screen)** "
        "通常 1-2 道 LC medium, 比 onsite R1 简单一档但同样要 production-"
        "quality code. Trigger phrase: 'recruiter call', 'HR phone "
        "screen', 'tech screen', 'phone interview', '电话面'. "
        "**Pipeline 位置**: 这是 funnel 的第一段, 通过 = 进 onsite 4-"
        "round VO; 不通过 = pipeline 终结. **Cross-links**: "
        "kg://243 (parent onsite-loop-templates), kg://5 (pillar5 "
        "Behavioral, recruiter call 的 culture-fit 部分), "
        "kg://1 (pillar1 Coding, tech screen 主考). **Anti-patterns**: "
        "Step 0a 把 self-intro 拖到 3 分钟 (60-90sec rule, 超时 "
        "recruiter 会 cut); 没准备 'why this company' specific 说辞 "
        "(说 'great culture' 没引用 specific product/blog/team 等于零); "
        "Step 0b 不 clarify 直接写代码 (面试官故意 underspecified, "
        "扣分点); tech screen 用 silent coding (recruiter 反馈 'didn't "
        "communicate well' 是高频淘汰原因); recruiter call 不问 loop "
        "details (后续 onsite 备考会缺信息).",
        ["Adobe", "Google", "LinkedIn", "Pinterest", "Slack", "Uber"],
    ),
    (
        "ml-system-design-round",
        "ML System Design Round Playbook (Single-Round Template)",
        "Onsite **R3 (or equivalent)** 的 60min ML SD round 的执行 "
        "template. 核心 framing: 把 ML 嵌进 internet-scale 系统, "
        "infra ↔ modeling 双向影响都能讲. **5-stage structural "
        "playbook** (顺序 + 时间分配建议):\n\n"
        "| Stage | 时长 | 输出 | 失分点 |\n"
        "|-------|------|------|--------|\n"
        "| 1. Requirement gather | 5-8min | functional + non-functional "
        "(QPS / latency / corpus 大小) | 直接画架构 (零分) |\n"
        "| 2. Multi-stage funnel | 8-12min | retrieval -> pre-rank -> "
        "rank -> rerank/policy 漏斗 | 单一模型一把梭 |\n"
        "| 3. Per-stage model + data | 15-20min | two-tower / "
        "cross-encoder / GBDT/DNN / feature store / labels | 没 "
        "tradeoff 只列 buzzword |\n"
        "| 4. Serving + scaling | 8-12min | cache / sharding / "
        "fallback / cold-start / batched inference | 没 latency budget |\n"
        "| 5. Eval + monitoring | 5-8min | offline NDCG/Recall + online "
        "A/B + guardrail metric + drift detection | 没 online + offline "
        "对齐 |\n\n"
        "**Trigger phrase**: '60min ML system design', 'design a "
        "ranking/recommendation/search system', '设计 X 推荐系统', "
        "'ML system design round'. **Mandatory talking-point map** "
        "(每个 SD 题都要碰): retrieval (kg://255 multi-stage funnel + "
        "kg://252 two-tower + kg://253 ANN HNSW/IVF-PQ), ranking "
        "(kg://257 LTR pointwise/pairwise/listwise + kg://259 "
        "feature-cross DLRM/DCN + kg://258 MMoE/PLE multitask), "
        "calibration (kg://262 isotonic/Platt/temperature), eval "
        "(kg://261 NDCG/Recall + kg://264 A/B framework), serving "
        "(kg://255 funnel + kg://275 quantization + kg://270 cache "
        "LRU/LFU), cold-start (kg://260), debias (kg://266). **Sample "
        "question shapes**: (a) 'design Pin recommendation' / (b) "
        "'design ad CTR ranker' / (c) 'design typeahead autocomplete' "
        "/ (d) 'design fraud detection' / (e) 'design query understanding'. "
        "**Cross-links**: kg://243 (parent onsite-loop-templates), "
        "kg://2 (pillar2 ML System Design), kg://242 (sibling pillar "
        "system-design-must-knows). **Anti-patterns**: 跳过 stage 1 直接 "
        "画 retrieval+rank (interviewer 等你问 latency / QPS / corpus, "
        "不问就扣 'didn't gather requirement'); 单一 model 解决所有 stage "
        "(漏斗不分级 = 不会做 internet-scale); 列 buzzword 不讲 tradeoff "
        "('我用 HNSW' 没说 vs IVF-PQ 的 recall/latency tradeoff = 零分); "
        "没讲 train-serve skew 怎么避免 (feature store 的 dual-write "
        "/ shared featurization library); offline metric 跟 online "
        "objective 没对齐 (NDCG@10 上去了 CTR 没动 -- 没解释 = 失分).",
        ["Google", "LinkedIn", "Meta", "Pinterest", "Slack", "Uber"],
    ),
    (
        "behavioral-bq-round",
        "Behavioral / BQ Round Playbook (Single-Round Template)",
        "Onsite **R4 (or equivalent)** 的 45-60min behavioral round 的 "
        "执行 template. 核心 framing: 不是聊天, 是从 5-pack 的 story "
        "库里**精确路由 + 结构化 delivery**, 让面试官在 3-4min 内打到 "
        "leadership / conflict / ownership / failure 的全部 axes. "
        "**Round-level structural diagram** (典型 60min BQ round 的 "
        "时间分配):\n\n"
        "| Phase | 时长 | 内容 | 主考点 |\n"
        "|-------|------|------|--------|\n"
        "| Opening | 2-3min | self-intro + warm-up | 对答清晰 |\n"
        "| Core BQ | 35-45min | 5-7 questions × 3-4min/each | story "
        "routing + STAR-T |\n"
        "| Follow-up probe | 5-10min | 'what would you do "
        "differently?' / 'how did manager react?' | reflection + "
        "self-awareness |\n"
        "| Candidate Qs | 5min | 你问 interviewer | 准备 3 "
        "个 specific 问题 |\n\n"
        "**Story-pack pre-build** (5-7 stories覆盖以下 cluster, 详见 "
        "kg://240 meta-prep/behavioral-clusters): (1) conflict-"
        "resolution-cross-team (kg://245); (2) project-ownership-end-"
        "to-end (kg://246); (3) ambiguity-self-initiated (kg://247); "
        "(4) technical-leadership-mentorship (kg://248); (5) failure-"
        "and-difficult-feedback (kg://249); (6) prioritization-tight-"
        "deadline (kg://250). **Delivery framework**: STAR-T "
        "(Situation 30sec - Task 30sec - Action 90sec - Result "
        "60sec - Transfer 30sec, 详见 kg://251) -- 'Transfer' (T) 是 "
        "senior signal: 把 lesson 抽象成 framework 可复用. **Trigger "
        "phrase**: 'tell me about a time when...', 'walk me through "
        "a project where...', 'how did you handle...', '过去遇到 "
        "X 的 example'. **Routing decision**: 听到关键词 -> 1-2sec "
        "选最佳 story (准备 5-question -> story 路由表). **Cross-"
        "links**: kg://243 (parent onsite-loop-templates), kg://5 "
        "(pillar5 Behavioral), kg://240 (sibling meta-prep/"
        "behavioral-clusters), kg://251 (STAR-T framework). **Anti-"
        "patterns**: story 太长超过 4min (interviewer 没机会 "
        "follow-up = 信息不全); 选错 story (问 'leadership' 答 "
        "'conflict' = routing 失误); STAR-T 漏 'Result' 的量化数据 "
        "('we improved metrics' 没具体数字); 听到 'failure' 选了 "
        "实际成功的 story (面试官想测 self-awareness, 你避而不答 = "
        "扣分); follow-up probe 'what would you do differently' 答 "
        "'nothing' (零反思 = 严重扣分); 没准备 candidate's questions "
        "或问 'when do I hear back' (浪费 5min, recruiter 会处理 "
        "logistics).",
        ["DoorDash", "Google", "LinkedIn", "Meta", "Pinterest", "Slack",
         "Uber"],
    ),
    (
        "project-deep-dive-round",
        "Project Deep-Dive Round Playbook (Single-Round Template)",
        "Onsite 中**专门 deep-dive 一个 ML 项目**的 round template "
        "(45-60min). 区别于 ML SD (从零设计新系统) 和 BQ (讲 leadership "
        "故事), 这一轮 interviewer 要你对**自己 own 过的 1 个真实项目** "
        "做端到端 deep-dive, 4 axes 逐一钻. 部分公司 (Pinterest 'ML "
        "Practitioner', LinkedIn 'Project Deep Dive', DoorDash 'Domain "
        "Prep') 单设此轮; 部分公司在 ML SD 或 BQ round 内嵌入 deep-dive "
        "段. **4-axis structural drill diagram**:\n\n"
        "| Axis | 时长 | interviewer 钻法 | 候选人输出 |\n"
        "|------|------|------------------|-----------|\n"
        "| 1. Problem framing & model selection | 10-15min | 为什么要 "
        "ML? 为什么这个 model? vs alternatives? | business obj -> ML "
        "framing 推导链 |\n"
        "| 2. Featurization | 10-15min | dense vs sparse / feature "
        "importance / overfit 怎么防 | 具体 feature list + reg "
        "选择理由 |\n"
        "| 3. Training + deployment | 10-15min | offline -> online / "
        "QPS / latency / cold-start fallback | 完整 train-serve "
        "pipeline |\n"
        "| 4. Evaluation + iteration | 10-15min | offline metric / "
        "online A/B / guardrail / 迭代后续 | 量化 business impact + "
        "next-step plan |\n\n"
        "**Pre-round prep** (面试前 24h 必做): 选 1 个 signature project "
        "(自己最熟 + 量化 result + 跨 axes 都能聊), 准备 'kill-line' "
        "(30sec elevator pitch) + 5-min deep narrative + 30-min "
        "drill-down materials. **Mindset**: 你不是 model 调参员, 是从 "
        "problem framing 一路 own 到 deployment 的 senior IC, 每个决策 "
        "都能讲清 *为什么* 和 *放弃了什么*. **Trigger phrase**: 'walk "
        "me through your most impactful project', 'tell me about an "
        "ML project you owned', 'project deep dive', 'ML practitioner "
        "round', 'domain deep dive'. **Cross-links**: kg://243 (parent "
        "onsite-loop-templates), kg://2 (pillar2 ML System Design, "
        "Axis 1+3 重叠), kg://3 (pillar3 ML Theory, Axis 1+2 model "
        "选择), kg://246 (meta-prep/behavioral-clusters/project-"
        "ownership-end-to-end, BQ 角度的 ownership story). **Anti-"
        "patterns**: 选了不熟的 'looks impressive' 项目 (deep-dive "
        "时漏洞百出); Axis 1 (framing) 跳过直接讲 model 实现 (失去 "
        "business sense signal); Axis 4 (eval) 只讲 offline metric "
        "(NDCG 上去了但没 online A/B = 没真上线 = 没 ownership); "
        "feature importance 答 'I used SHAP' 没具体数值或 ranking "
        "(零信号); deployment 答 'engineer team 部署的' (= no "
        "deployment ownership = 零 senior signal); 'what would you "
        "do differently' 答 'nothing' (= no reflection = 严重失分).",
        ["DoorDash", "LinkedIn", "Pinterest", "Slack"],
    ),
]


def sha256_subtree(conn: sqlite3.Connection) -> str:
    """SHA-256 of all 'meta-prep/onsite-loop-templates%' rows, ordered by path."""
    rows = conn.execute(
        "SELECT path, depth, title, description, relevant_companies "
        "FROM framework_nodes "
        "WHERE path = ? OR path LIKE 'meta-prep/onsite-loop-templates/%' "
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
    """Update parent description if still TODO; otherwise SKIP."""
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
    """Insert child if absent; SKIP if present with matching content."""
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


CROSS_LINK_RE = re.compile(r"(kg://\d+|sd://[a-z0-9-]+)")
# A "structural diagram" cue is either a markdown table with at least 2 rows
# of '|' OR an arrow-chain (->) of >=3 segments.
STRUCT_TABLE_RE = re.compile(
    r"\|[^\n]*\|[^\n]*\|.*\n\|[\s:|-]+\|.*\n(\|[^\n]*\|[^\n]*\n){2,}",
    re.MULTILINE,
)
STRUCT_ARROW_RE = re.compile(r"\S+\s*->\s*\S+\s*->\s*\S+\s*->\s*\S+")


def _has_structural_diagram(text: str) -> bool:
    """Heuristic: text has either a >=2-row markdown table or a 4-segment arrow chain."""
    return bool(STRUCT_TABLE_RE.search(text) or STRUCT_ARROW_RE.search(text))


def assert_promotion_threshold() -> None:
    """Static AC: each template has >=3 P0+P1 sources, all valid names; >=3 children;
    each description embeds at least one kg:// or sd:// cross-link AND a
    structural diagram (markdown table or arrow chain)."""
    if len(TEMPLATES) < 3:
        raise AssertionError(
            f"[AC-FAIL] only {len(TEMPLATES)} templates defined; AC requires >=3"
        )
    seen_slugs: set[str] = set()
    for slug, _title, description, companies in TEMPLATES:
        if slug in seen_slugs:
            raise AssertionError(f"[AC-FAIL] duplicate slug {slug!r}")
        seen_slugs.add(slug)
        if len(companies) < 3:
            raise AssertionError(
                f"[AC-FAIL] template {slug!r} has only {len(companies)} sources; "
                f"promotion threshold is >=3"
            )
        if len(companies) != len(set(companies)):
            raise AssertionError(
                f"[AC-FAIL] template {slug!r} has duplicate sources: {companies}"
            )
        invalid = set(companies) - P0P1_COMPANY_NAMES
        if invalid:
            raise AssertionError(
                f"[AC-FAIL] template {slug!r} references non-P0+P1 companies: "
                f"{sorted(invalid)}"
            )
        if not CROSS_LINK_RE.search(description):
            raise AssertionError(
                f"[AC-FAIL] template {slug!r} description has no kg:// or sd:// "
                f"cross-link"
            )
        if not _has_structural_diagram(description):
            raise AssertionError(
                f"[AC-FAIL] template {slug!r} description has no structural "
                f"diagram (need >=2-row markdown table OR 4-segment arrow chain)"
            )


def seed(conn: sqlite3.Connection) -> dict[str, int]:
    """Update parent description (if TODO) and seed N child templates."""
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

    for slug, title, description, companies in TEMPLATES:
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
        n_links = len(CROSS_LINK_RE.findall(description))
        print(
            f"[{action}] child  id={child_id} "
            f"slug={slug} sources={len(companies)} cross_links={n_links}"
        )

    return counts


def main() -> None:
    if not DB_PATH.exists():
        print(f"[FAIL] DB not found: {DB_PATH}")
        sys.exit(1)

    assert_promotion_threshold()
    print(
        f"[AC-OK] all {len(TEMPLATES)} templates have >=3 valid P0+P1 sources, "
        f"embed at least one kg:// or sd:// cross-link, and contain a "
        f"structural diagram (table or arrow chain)"
    )

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
            "WHERE path = ? OR path LIKE 'meta-prep/onsite-loop-templates/%'",
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

    expected_total = 1 + len(TEMPLATES)
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
