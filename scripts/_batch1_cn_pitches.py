"""Batch 1: PUT cn_elevator_pitch for 14 examples (BLOG-01 to EX-09)."""

import json
import urllib.request

BASE = "http://localhost:8100/api/behavioral/examples"

PITCHES = {
    11: (  # BLOG-01
        "Researcher 把品牌召回模型\"甩墙\"过来，缓存需求超现有 infra 一个量级；"
        "通过 joint 压缩迭代打破 adversarial 动态，共创 productionization checklist 成团队首个 model-to-prod 标准 "
        "| KEY FACTS: 数千万 cache 条目 vs 百万级 infra | 联合压缩实验转化协作 | "
        "productionization checklist 成新规范"
    ),
    29: (  # BLOG-01B
        "品牌召回表裁剪沿用 query frequency 排序，发现 ~2% 交易贡献 50%+ GMV "
        "且 logging 被 browse 流量污染——\"20% 性能损失\"大部分是脏数据幻觉；"
        "推动 GMV-calibrated evaluation 成新标准 "
        "| KEY FACTS: ~2% 交易 = 50%+ GMV | 脏 logging 数据 | "
        "frequency != value | GMV-calibrated 评估新标准"
    ),
    12: (  # BLOG-02
        "队友 code review 反复要求已有 policy 覆盖的测试导致 PR delay；"
        "通过 1:1 沟通理解其标准并主动起草共享 review guidelines，消除摩擦 "
        "| KEY FACTS: 1:1 直接沟通 | 证据驱动对齐 | "
        "共享 review guidelines | 项目按期交付"
    ),
    13: (  # BLOG-03
        "Ads 团队要求共享 relevance 数据违反 org boundary；"
        "深挖发现真需求是验证 A/B 结果，构建 LLM relevance pipeline "
        "日产 ~18K 标签 ~$500 替代人工标注 "
        "| KEY FACTS: ~18K 标签/天 ~$500 | 人工标注 $0.30-0.80/条 | "
        "org boundary 防线 | LLM pipeline 解决真需求"
    ),
    14: (  # BLOG-04
        "团队 goal tracking 暗中奖励失败——改名、re-scope、rollover 伪装交付率；"
        "推动锁定 scope + peer confidence estimates，"
        "短期交付率下降反证系统生效 "
        "| KEY FACTS: 锁定 goal scope | peer confidence estimates | "
        "短期交付率下降 = 系统生效 | VP 级 velocity 改善"
    ),
    1: (  # EX-01
        "Hacker Week 自发发现 multi-intent query \"intent collapse\"——"
        "\"pokemon\" 90%+ 返回 trading cards 而购买数据显示一半用户要游戏/玩具；"
        "构建端到端 diversity prototype "
        "| KEY FACTS: Hacker Week 自发 | 90%+ intent collapse | "
        "200M+ annualized impact | 多年 initiative 起点"
    ),
    2: (  # EX-02 (rewritten 2026-04-23 via _rewrite_ex02_team_transfer_20260423.py)
        "Hacker Week 做出 diversity ranking prototype -- "
        "200M+ GMB opportunity 但 manager 判 out of scope，"
        "team charter 是 relevance filtering thresholds 而不是 "
        "ranking allocation，OKRs 结构上对不上；先试 soft "
        "reframe 把 project 包装进 relevance 语言，失败 -- "
        "OKRs 是 team 被 measure 的东西，不是 aspire 的东西；"
        "做了 structural call 转到 Final Ranking team，把 "
        "diversity 重新定义成 intent-aware slot allocation；"
        "正式申请前先和 receiving team lead 预谈，cold 转组 "
        "变成 warm sponsor；对前 manager 也 name 了自己的 "
        "gap -- 应该在 Hacker Week 之前就把 business case "
        "translate 成 OKR 语言"
        " | KEY FACTS: structural call 而非 political win"
        " | soft reframe 失败是信号不是 setback"
        " | 转组前先预谈 receiving team lead"
        " | +1% GMB 首次实验 -> 200M+ annualized impact"
        " | 核心 lesson: problem follows the person, not the org chart"
    ),
    3: (  # EX-03
        "发现 Sale NDCG 系统性偏向低价商品——$5 配饰排在 $100 项链前面；"
        "提出 GMB (price x sale probability) 作为正确 proxy，揭示 calibration 陷阱 "
        "| KEY FACTS: Sale NDCG 价格偏差 | GMB proxy 替代 | "
        "calibration 陷阱 | \"proxy 选择是最被低估的 ML 决策\""
    ),
    4: (  # EX-04
        "Diversity 实验后 MRR 下降但 GMB 和购买率上升引发 stakeholder 恐慌；"
        "解释 MRR 假设单一 intent 的理论局限，推动 OKR 纳入 abandonment 数据 "
        "| KEY FACTS: MRR 下降 + GMB 上升 | 单一 intent 假设 | "
        "abandonment rate guardrail | OKR 评估范式转变"
    ),
    5: (  # EX-05
        "作为唯一 MLE 发现 XGBoost 模型 +10% latency 远超 <=1% 预算；"
        "三路方案中两路失败，最终 cheap rejection + early exit 组合达标 "
        "| KEY FACTS: +10% latency vs <=1% 预算 | "
        "cheap rejection + early exit | +4-6% GMB on null/low-intent | "
        "end-to-end payload 验证新实践"
    ),
    6: (  # EX-06
        "从 diversity +1% GMB 单点实验识别出平台化机会；"
        "设计 reusable allocation primitive——caching + deficit calculation + uplift，"
        "替换 LTR scoring 为 ads-style bidding + allocation 范式 "
        "| KEY FACTS: reusable allocation primitive | ads-style bidding 范式 | "
        "多 vertical 复用 +0.6%+ GMB | 200M+ annualized impact"
    ),
    7: (  # EX-07
        "团队数月争论 relevance filtering 是否有效，发现评估数据集只含 "
        "converted results 形成 self-fulfilling prophecy；"
        "识别三大根因说服 stakeholders 转向 problem formulation "
        "| KEY FACTS: self-fulfilling prophecy | survivorship bias | "
        "非购买用户价值忽略 | 重心从 model 优化转向 problem formulation"
    ),
    8: (  # EX-08
        "发现搜索 production baseline 数月缓慢退化但无人察觉——"
        "因各组都用最新 production 做 control；溯源到 module 占位 4-6x "
        "挤压 organic results，escalate 到 VP 推动 module arbitration team 成立 "
        "| KEY FACTS: 隐性 cumulative GMB regression | module 占位 4-6x | "
        "VP escalation | module arbitration team 成立 | 200M+ 后续 impact"
    ),
    9: (  # EX-09
        "LLM query rewrite 因 tokenizer 不匹配持续返回无关结果；"
        "提出 proxy item 方案——让 LLM 生成理想商品描述再用向量匹配，"
        "最大化复用现有 infra 快速 unblock 实验 "
        "| KEY FACTS: LLM-search 适配鸿沟 | proxy item 方案 | "
        "最大化现有 infra 复用 | 最快 unblock 路径"
    ),
}


def main() -> None:
    """PUT cn_elevator_pitch for each example and verify."""
    success = 0
    for db_id, pitch in PITCHES.items():
        payload = json.dumps({"cn_elevator_pitch": pitch}).encode("utf-8")
        req = urllib.request.Request(
            f"{BASE}/{db_id}",
            data=payload,
            method="PUT",
            headers={"Content-Type": "application/json"},
        )
        with urllib.request.urlopen(req) as resp:
            result = json.loads(resp.read())
        stored = result.get("cn_elevator_pitch", "")
        if stored and stored == pitch:
            print(f"[OK] {result['example_id']} (db_id={db_id})")
            success += 1
        else:
            print(f"[FAIL] {result['example_id']} (db_id={db_id}) -- mismatch")

    print(f"\n{success}/{len(PITCHES)} examples updated successfully.")

    # Verification pass
    print("\n=== Verification: all 14 batch-1 examples ===")
    verify_ok = 0
    for db_id in PITCHES:
        url = f"{BASE}/{db_id}"
        with urllib.request.urlopen(url) as resp:
            d = json.loads(resp.read())
        has = bool(d.get("cn_elevator_pitch"))
        status = "OK" if has else "MISSING"
        print(f"[{status}] {d['example_id']} (db_id={db_id})")
        if has:
            verify_ok += 1
    print(f"\nVerification: {verify_ok}/{len(PITCHES)} have cn_elevator_pitch.")


if __name__ == "__main__":
    main()
