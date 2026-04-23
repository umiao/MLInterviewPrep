"""Batch 2: PUT cn_elevator_pitch for 13 examples (EX-10 to EX-33)."""

import json
import urllib.request

BASE = "http://localhost:8100/api/behavioral/examples"

PITCHES = {
    10: (  # EX-10
        "标准 A/B 测试存在 bucketing drift、on-policy replay 等系统性偏差，"
        "威胁 production 决策和 SIGIR 论文可信度；"
        "设计 paired replay + quantile stratification + debiased curve 三角验证框架，"
        "兼顾日常迭代与学术 rigor "
        "| KEY FACTS: paired replay protocol | quantile stratification | "
        "debiased curve (A/B lift - A/A lift) | 三角因果验证 | SIGIR 发表级别"
    ),
    15: (  # EX-11
        "PhD intern 实际进度不错但 peer 感知\"只有 self-learning 没有 deadline\"；"
        "通过 1:1 正面引导建立 goals-progress-confidence 汇报框架，"
        "弥合 academia-to-industry 沟通鸿沟，intern 最终拿到 return offer "
        "| KEY FACTS: 正面 framing 非批评 | goals-progress-confidence 框架 | "
        "phased deliverables + verifiable milestones | return offer"
    ),
    16: (  # EX-12
        "PhD interns 因不熟 production stack 保持 GPU 实例 24/7 运行避免回收；"
        "识别真正障碍（无 in-memory 数据审查、dependency 复杂），"
        "构建 template class 覆盖 raw data -> dataset -> model 全流程，"
        "成为研究团队 reusable onboarding 资源 "
        "| KEY FACTS: 24/7 GPU 占用 -> 正常工作模式 | template class 全流程覆盖 | "
        "notebook -> production 迁移 | 团队级 onboarding 复用"
    ),
    17: (  # EX-13
        "同事仅写不到一页 incomplete manuscript 却要求 first authorship；"
        "坚持\"authorship 反映实际贡献，不做 gift\"原则，"
        "准备学术伦理文献后 escalate 到双方 manager，"
        "建立 contribution-based 署名规范，后续再无争议 "
        "| KEY FACTS: authorship = actual contribution | 拒绝 gift authorship | "
        "manager mediation | 轮换制规范 | 零后续争议"
    ),
    18: (  # EX-14 -- rewritten 2026-04-23 (T-P0-577) per story_rewrite_protocol
        # Feasibility-first kill of agentic search via 1-week ROI math, then
        # pivot to LLM-as-Judge against the relevance backlog. Old version
        # framed pivot as a persuasion win; new version makes the kill the
        # move. Matches DB row 18 cn_elevator_pitch set by
        # _rewrite_ex14_llm_exploration_20260423.py.
        "2023 年 leadership 要 'upgrade to GenAI'，给 sandbox + "
        "API credits 自己探，没有 requirements、没"
        "有 LLM precedent；先用 1 周 feasibility 把 "
        "agentic search 路径用 ROI math 杀掉 -- 不能"
        "接 indexing pipeline、tens of QPS vs 40K peak、latency "
        "不适合 real-time；换来 standing 推 manager "
        "跳过 headline demo 找 highest-value low-hanging fruit，"
        "落到 relevance backlog 上的 LLM-as-Judge -- 不是"
        "因为新颖，是因为 cheap to operate、"
        "easy to audit、瞄准人类 annotator 已经做"
        "不好的面"
        " | KEY FACTS: 1 周 ROI math 杀 agentic"
        " | 不接 indexing pipeline + tens of QPS vs 40K peak"
        " | LLM-as-Judge 挂到 relevance backlog"
        " | solo exploration -> 多团队 production measurement infra"
        " | 核心 lesson: feasibility 才是 real authoring"
    ),
    22: (  # EX-18
        "作为唯一工程师同时承担 2-3 个业务项目，director 还要求探索 "
        "Ray/GCP/K8s 三套 distributed training 方案——实质是多 leader "
        "tech stack 分歧；主动分析 pros/cons + 资源 + timeline，"
        "推动领导层 deprioritize，释放带宽聚焦业务 "
        "| KEY FACTS: 一人 vs 三套方案 = route dispute | "
        "分析替代穷举 | deprioritize -> 下季度移除 | 聚焦业务项目"
    ),
    23: (  # EX-19
        "PM 想用 buyer-based A/B 平台做 seller conversion 测试，"
        "但同一搜索页 treated/untreated seller 商品混排导致 confounder；"
        "用具体类比说服 PM 理解问题，提出 time-of-day split 折中方案 "
        "| KEY FACTS: same-page contamination | 具体类比 > slides | "
        "time-of-day split 替代 buyer-ID split | seller-side 测试方法论"
    ),
    24: (  # EX-20
        "发现 seller risk model 系统性惩罚新卖家——零交易历史 = 高风险分，"
        "形成\"永远无法建立信誉\"的恶性循环；"
        "研究 PayPal 案例 + 平台责任法律框架，"
        "推动从 seller-only 转向 seller-listing cross-modeling，"
        "经法务确认后落地 "
        "| KEY FACTS: 新卖家 vicious cycle | PayPal 等行业案例 | "
        "precision modeling 替代 blanket penalty | 法务协作 | recommerce 战略对齐"
    ),
    25: (  # EX-21
        "新功能依赖团队 declarative artifactory 系统但长期 delay 无 timeline；"
        "深入研究发现核心价值是 JSON ranking rule expression generation，"
        "blocker 是周边 infra；用内部 caching 系统做 storage，"
        "功能按时交付且后续迁移无缝衔接 "
        "| KEY FACTS: 核心 vs 周边分离 | parity tests 验证一致性 | "
        "按时交付 vs 等一年 | 迁移仅需 storage/versioning 切换"
    ),
    26: (  # EX-22
        "自己的 custom hash 可用但\"只有我觉得直观\"本身是维护风险；"
        "主动将决策权交给 researcher，角色从 solution designer 转为 "
        "requirements definer + quality gatekeeper；"
        "researcher 选出 MurmurHash 并发现原有 dedupe hash 的 distribution bug "
        "| KEY FACTS: 可维护性 > 个人偏好 | 明确 acceptance framework | "
        "MurmurHash 优于原方案 | 发现 latent distribution bug | reusable hashing library"
    ),
    27: (  # EX-23
        "NYC C2C 业务持续下滑，VP 要求 2 周内出测试、1 月内出 launch 方案，"
        "30+ 人跨组协调；测试上线后发现 control 失效——upstream 团队"
        "\"修复\" incident 时覆盖了 control property；"
        "进一步发现 combo-launch 各 policy 互相抵消，"
        "推动逐项上线避免好 policy 被误杀 "
        "| KEY FACTS: 2 周 deadline + 30 人协调 | silent control 覆盖 | "
        "combo-launch 互相抵消 | 逐项上线策略"
    ),
    28: (  # EX-24
        "VP 想同时上线所有成功 test policy 以\"最大化 impact\"；"
        "用 conclusion-first 沟通解释 ranking 是 zero-sum allocation——"
        "多 policy 竞争同一 top positions 无 free lunch；"
        "VP 接受分析，allocation framing 成为团队长期 mental model "
        "| KEY FACTS: conclusion-first 沟通 | ranking = zero-sum allocation | "
        "no free lunch | VP 调整方向 | 持久 mental model"
    ),
    33: (  # EX-33
        "eBay 搜索 org 困于 pairwise ranking 范式，leadership 批准 MoE + neural ranking "
        "项目占用约 80 GPU nodes；主动将项目 scope 定义为\"start test\"而非\"test and launch\"，"
        "放弃包装失败为 carry-over 的保护；"
        "MoE 未达预期后如实汇报，推动 org 从 ranking modeling 转型为 allocation team，"
        "开启 allocation policy 新主线 "
        "| KEY FACTS: 80 GPU nodes | \"start test\" vs \"test and launch\" | "
        "honest negative result | org 更名 ranking -> allocation | 范式转移"
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

    # Verification pass: all 34 examples should now have cn_elevator_pitch
    print("\n=== Final verification: ALL 34 examples ===")
    url = f"{BASE}"
    with urllib.request.urlopen(url) as resp:
        all_examples = json.loads(resp.read())

    with_pitch = 0
    without_pitch = []
    for ex in all_examples:
        if ex.get("cn_elevator_pitch"):
            with_pitch += 1
        else:
            without_pitch.append(ex["example_id"])

    print(f"Total: {len(all_examples)} examples")
    print(f"With cn_elevator_pitch: {with_pitch}/{len(all_examples)}")
    if without_pitch:
        print(f"Missing: {without_pitch}")
    else:
        print("ALL examples have cn_elevator_pitch!")


if __name__ == "__main__":
    main()
