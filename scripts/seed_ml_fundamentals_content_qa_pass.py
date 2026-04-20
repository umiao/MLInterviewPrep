"""Seed: T-P1-550 [T-MLF-10] content QA pass -- acronym expansions for 27
ml-fundamentals leaves.

Targeted, idempotent substitutions. For each `(path, (needle, replacement))`
entry in QA_FIXES the script:

  1. Looks up the leaf's current description in framework_nodes.
  2. If `replacement` already appears in the description, records SKIP.
  3. Else if `needle` appears, performs a single `.replace(needle, replacement, 1)`
     and records UPDATED.
  4. Else records NOT_FOUND (the target text was already changed by someone
     else; we don't fail -- we just log it).

Each QA fix adds first-occurrence canonical expansion
`**English Full Name** (ACRO, 中文)` per the content-style guide
(`feedback_content_style_cn_en.md`). The ORIGINAL seed scripts (cat12, cat34,
cat5, q21, q22, q2324_2627, q25) remain untouched -- their DESC_* constants
still represent the "initial golden answer" content. This QA-pass script
layers the style-guide fixes on top, and is idempotent: running twice
produces `updated=0` on the second pass.

Acceptance:
  - sha256 of affected description blobs changes between pre and post.
  - Second run produces updated=0 skipped=<N_fixes>.
  - Audit report `logs/mlf_content_qa_audit.md` shows reduced A count.
"""
from __future__ import annotations

import hashlib
import sqlite3
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
DB_PATH = REPO_ROOT / "data" / "mle_prep.db"


# QA_FIXES -- one list of (needle, replacement) tuples per leaf path.
# Each substitution is a single first-occurrence expansion of an acronym.
QA_FIXES: dict[str, list[tuple[str, str]]] = {
    # -- Attention & Transformer --------------------------------------------
    "ml-fundamentals/attention_transformer/kv-cache": [
        (
            "decoder-only LLM 推理时",
            "decoder-only **Large Language Model** (LLM, 大语言模型) 推理时",
        ),
    ],
    "ml-fundamentals/attention_transformer/mha-mqa-gqa": [
        (
            "。LLM 推理的瓶颈是",
            "。**Large Language Model** (LLM, 大语言模型) 推理的瓶颈是",
        ),
    ],
    "ml-fundamentals/attention_transformer/positional-encoding": [
        (
            "几乎垄断 2023+ 的 LLM：",
            "几乎垄断 2023+ 的 **Large Language Model** (LLM, 大语言模型)：",
        ),
        (
            "更多用于 MPT 那条技术线",
            "更多用于 MPT（MosaicML Pretrained Transformer，MosaicML 预训练大模型系列）那条技术线",
        ),
    ],
    "ml-fundamentals/attention_transformer/pre-norm-vs-post-norm": [
        (
            "现代 LLM（LLaMA、GPT-3+、PaLM、Mistral）",
            "现代 **Large Language Model** (LLM, 大语言模型)（LLaMA、GPT-3+、PaLM、Mistral）",
        ),
        (
            "$F$ 表示 attention 或 FFN 子模块",
            "$F$ 表示 attention 或 **Feed-Forward Network** (FFN, 前馈网络) 子模块",
        ),
    ],
    "ml-fundamentals/attention_transformer/self-attention-complexity-optimization": [
        (
            "现在是所有主流 LLM 训练/推理的标配",
            "现在是所有主流 **Large Language Model** (LLM, 大语言模型) 训练/推理的标配",
        ),
        (
            "**Mamba / SSM** (State Space Models)",
            "Mamba / **State Space Model** (SSM, 状态空间模型)",
        ),
        (
            "- **KV Cache**：推理时前面 token 的",
            "- **Key-Value Cache** (KV Cache, 键值缓存)：推理时前面 token 的",
        ),
    ],
    # -- Classical ML -------------------------------------------------------
    "ml-fundamentals/classical_ml/cross-entropy-kl-divergence": [
        (
            "## 4. 为什么不直接用 MSE\n\n- MSE + softmax 是非凸的",
            "## 4. 为什么不直接用 **Mean Squared Error** (MSE, 均方误差)\n\n- MSE + softmax 是非凸的",
        ),
        (
            "- VAE 的 ELBO 里出现的是这个",
            "- **Variational AutoEncoder** (VAE, 变分自编码器) 的 **Evidence Lower Bound** (ELBO, 证据下界) 里出现的是这个",
        ),
        (
            "原始 GAN 的 loss 就等价于最小化 JS",
            "原始 **Generative Adversarial Network** (GAN, 生成对抗网络) 的 loss 就等价于最小化 JS",
        ),
        (
            "WGAN 用的就是它",
            "**Wasserstein GAN** (WGAN, Wasserstein 生成对抗网络) 用的就是它",
        ),
    ],
    "ml-fundamentals/classical_ml/gbdt-vs-rf-xgboost": [
        (
            "## 1. GBDT vs Random Forest：本质差别\n\n两者都是 tree ensemble",
            "## 1. GBDT vs Random Forest：本质差别\n\n**Gradient Boosted Decision Trees** (GBDT, 梯度提升决策树) 与 **Random Forest** (RF, 随机森林) 两者都是 tree ensemble",
        ),
    ],
    "ml-fundamentals/classical_ml/logistic-regression-loss": [
        (
            "## 2. 从 MLE 推导 loss",
            "## 2. 从 **Maximum Likelihood Estimation** (MLE, 最大似然估计) 推导 loss",
        ),
        (
            "和线性回归 MSE 的梯度长得一模一样",
            "和线性回归 **Mean Squared Error** (MSE, 均方误差) 的梯度长得一模一样",
        ),
    ],
    # -- DL Training --------------------------------------------------------
    "ml-fundamentals/dl_training/activation-function-evolution": [
        (
            "$\\Phi$ 是标准正态的 CDF",
            "$\\Phi$ 是标准正态的 **Cumulative Distribution Function** (CDF, 累积分布函数)",
        ),
        (
            "Google 2017 年用 NAS 搜出来的",
            "Google 2017 年用 **Neural Architecture Search** (NAS, 神经架构搜索) 搜出来的",
        ),
        (
            "## 5. 为什么 LLM 都转向 GLU 系列",
            "## 5. 为什么 **Large Language Model** (LLM, 大语言模型) 都转向 GLU 系列",
        ),
        (
            "**(a) 表达力更强**：标准 FFN 是",
            "**(a) 表达力更强**：标准 **Feed-Forward Network** (FFN, 前馈网络) 是",
        ),
    ],
    "ml-fundamentals/dl_training/adam-vs-sgd-adamw": [
        (
            "Transformer / LLM / 不规则 loss landscape",
            "Transformer / **Large Language Model** (LLM, 大语言模型) / 不规则 loss landscape",
        ),
    ],
    "ml-fundamentals/dl_training/batchnorm-vs-layernorm": [
        (
            "batch=1（LLM 推理一个 query）",
            "batch=1（**Large Language Model** (LLM, 大语言模型) 推理一个 query）",
        ),
    ],
    "ml-fundamentals/dl_training/dropout": [
        (
            "**(b) Inverted dropout**（现代默认，PyTorch / TF 实现）",
            "**(b) Inverted dropout**（现代默认，PyTorch / TensorFlow (TF) 实现）",
        ),
        (
            "- **和 BatchNorm 一起用有冲突**：dropout 改变激活分布，BN 的 running stats",
            "- **和 BatchNorm 一起用有冲突**：dropout 改变激活分布，**Batch Normalization** (BN, 批归一化) 的 running stats",
        ),
        (
            "attention weight 后、FFN 内部、残差加和前",
            "attention weight 后、**Feed-Forward Network** (FFN, 前馈网络) 内部、残差加和前",
        ),
    ],
    "ml-fundamentals/dl_training/vanishing-exploding-gradient": [
        (
            "治标，但对 RNN / LLM 是标配",
            "治标，但对 RNN / **Large Language Model** (LLM, 大语言模型) 是标配",
        ),
        (
            "6. **加 normalization 层**：BN / LN / RMSNorm",
            "6. **加 normalization 层**：**Batch Normalization** (BN, 批归一化) / **Layer Normalization** (LN, 层归一化) / RMSNorm",
        ),
    ],
    # -- Eval & Data --------------------------------------------------------
    "ml-fundamentals/eval_data/auc-vs-pr-curve": [
        (
            "## 1. 先理清 ROC 曲线本身",
            "## 1. 先理清 **Receiver Operating Characteristic** (ROC, 受试者工作特征) 曲线本身",
        ),
        (
            "## 3. 为什么不平衡时 PR 比 ROC 更合适",
            "## 3. 为什么不平衡时 **Precision-Recall** (PR, 精确率-召回率) 比 ROC 更合适",
        ),
    ],
    "ml-fundamentals/eval_data/class-imbalance-handling": [
        (
            "- ADASYN：在 hard-to-learn 的区域生成更多",
            "- **Adaptive Synthetic Sampling** (ADASYN, 自适应合成采样)：在 hard-to-learn 的区域生成更多",
        ),
        (
            "用 Isolation Forest、One-Class SVM、",
            "用 Isolation Forest、One-Class **Support Vector Machine** (SVM, 支持向量机)、",
        ),
        (
            "（插完再用 ENN 清噪声）",
            "（插完再用 **Edited Nearest Neighbors** (ENN, 编辑最近邻) 清噪声）",
        ),
        (
            "换成 PR-AUC / F1 / Recall@FPR",
            "换成 PR-AUC / F1 / Recall@**False Positive Rate** (FPR, 假正率)",
        ),
    ],
    # -- LLM & Stats --------------------------------------------------------
    "ml-fundamentals/llm_stats/ab-test-pvalue-sample-size-multiple-testing": [
        (
            "收集关键指标（CTR、收入、留存）",
            "收集关键指标（**Click-Through Rate** (CTR, 点击率)、收入、留存）",
        ),
        (
            "适合大规模探索（基因组 GWAS、指标 dashboard）",
            "适合大规模探索（基因组 **Genome-Wide Association Study** (GWAS, 全基因组关联分析)、指标 dashboard）",
        ),
        (
            "### 3.3 variance reduction：CUPED\n\nCUPED（Deng 2013）",
            "### 3.3 variance reduction：CUPED\n\n**Controlled-experiment Using Pre-Experiment Data** (CUPED, 预实验数据控制法，Deng 2013)",
        ),
        (
            "### 3.4 SRM (Sample Ratio Mismatch)",
            "### 3.4 **Sample Ratio Mismatch** (SRM, 样本比例不匹配)",
        ),
        (
            "random unit 的 IID 假设出问题",
            "random unit 的 **Independent and Identically Distributed** (IID, 独立同分布) 假设出问题",
        ),
        (
            "的 OLS 斜率。直接在 control 组上拟合",
            "的 **Ordinary Least Squares** (OLS, 普通最小二乘) 斜率。直接在 control 组上拟合",
        ),
    ],
    "ml-fundamentals/llm_stats/clt-vs-lln": [
        (
            "**独立同分布**（**Independent and Identically Distributed**，IID，独立同分布）样本",
            "**Independent and Identically Distributed** (IID, 独立同分布) 样本",
        ),
    ],
    "ml-fundamentals/llm_stats/mle-vs-map": [
        (
            "### 2.2 MSE 损失 = 高斯似然下的 MLE",
            "### 2.2 **Mean Squared Error** (MSE, 均方误差) 损失 = 高斯似然下的 MLE",
        ),
        (
            "现代贝叶斯更倾向 HMC（Hamiltonian Monte Carlo）",
            "现代贝叶斯更倾向 **Hamiltonian Monte Carlo** (HMC, 哈密顿蒙特卡洛)",
        ),
        (
            "(ii) **Expectation-Maximization**（EM）交替更新",
            "(ii) **Expectation-Maximization** (EM, 期望最大化) 交替更新",
        ),
    ],
    "ml-fundamentals/llm_stats/scaling-law-chinchilla": [
        (
            "LoRA / PEFT 下更是如此",
            "LoRA / **Parameter-Efficient Fine-Tuning** (PEFT, 参数高效微调) 下更是如此",
        ),
    ],
    "ml-fundamentals/llm_stats/sft-rlhf-dpo": [
        (
            "### 4.2 DPO vs IPO vs KTO —— 偏好损失的选择",
            "### 4.2 DPO vs IPO vs KTO（**Kahneman-Tversky Optimization**，KTO，前景理论偏好优化） —— 偏好损失的选择",
        ),
        (
            "改用 MSE 的对比损失",
            "改用 **Mean Squared Error** (MSE, 均方误差) 的对比损失",
        ),
    ],
    "ml-fundamentals/llm_stats/tokenization-bpe-wordpiece-sentencepiece": [
        (
            "LLM 里任何一个 token 被 `<unk>`",
            "**Large Language Model** (LLM, 大语言模型) 里任何一个 token 被 `<unk>`",
        ),
        (
            "先定义一个大词表再基于 EM 剪枝",
            "先定义一个大词表再基于 **Expectation-Maximization** (EM, 期望最大化) 剪枝",
        ),
    ],
    # -- Unsupervised -------------------------------------------------------
    "ml-fundamentals/unsupervised/em-and-gmm": [
        (
            "## 1. Motivation：为什么需要 GMM 和 EM\n\nK-means 假设簇是球形",
            "## 1. Motivation：为什么需要 **Gaussian Mixture Model** (GMM, 高斯混合模型) 和 **Expectation-Maximization** (EM, 期望最大化)\n\nK-means 假设簇是球形",
        ),
        (
            "用 BIC / AIC / held-out likelihood 选",
            "用 **Bayesian Information Criterion** (BIC, 贝叶斯信息准则) / **Akaike Information Criterion** (AIC, 赤池信息准则) / held-out likelihood 选",
        ),
        (
            "HMM 的 Baum-Welch",
            "**Hidden Markov Model** (HMM, 隐马尔可夫模型) 的 Baum-Welch",
        ),
        (
            "VAE 的训练也是 ELBO 最大化的变分版本",
            "**Variational AutoEncoder** (VAE, 变分自编码器) 的训练也是 **Evidence Lower Bound** (ELBO, 证据下界) 最大化的变分版本",
        ),
        (
            "（DPMM）把 K 设得偏大让它自动压掉",
            "（**Dirichlet Process Mixture Model**，DPMM，狄利克雷过程混合模型）把 K 设得偏大让它自动压掉",
        ),
    ],
    "ml-fundamentals/unsupervised/k-means-assumptions-and-failures": [
        (
            "大簇的 SSE 会主导总 loss",
            "大簇的 **Sum of Squared Errors** (SSE, 误差平方和) 会主导总 loss",
        ),
        (
            "Spectral clustering、DBSCAN",
            "Spectral clustering、**Density-Based Spatial Clustering of Applications with Noise** (DBSCAN, 基于密度的带噪聚类)",
        ),
        (
            "先降维（PCA / UMAP）再聚类",
            "先降维（**Principal Component Analysis** (PCA, 主成分分析) / **Uniform Manifold Approximation and Projection** (UMAP, 均匀流形近似与投影)）再聚类",
        ),
        (
            "GMM+BIC |",
            "GMM+**Bayesian Information Criterion** (BIC, 贝叶斯信息准则) |",
        ),
    ],
}


def sha256_of_affected(conn: sqlite3.Connection) -> str:
    """SHA-256 over (path, description) for every leaf in QA_FIXES."""
    h = hashlib.sha256()
    for path in sorted(QA_FIXES.keys()):
        row = conn.execute(
            "SELECT description FROM framework_nodes WHERE path = ?", (path,)
        ).fetchone()
        h.update(path.encode("utf-8"))
        h.update(b"\x00")
        h.update((row[0] or "").encode("utf-8"))
        h.update(b"\x00")
    return h.hexdigest()


def main() -> int:
    if not DB_PATH.exists():
        print(f"[FAIL] DB not found: {DB_PATH}")
        return 1

    conn = sqlite3.connect(str(DB_PATH))
    try:
        pre_hash = sha256_of_affected(conn)
        print(f"[PRE]  sha256={pre_hash}")

        total_updated = 0
        total_skipped = 0
        total_not_found = 0
        affected_paths = 0

        for path, fixes in QA_FIXES.items():
            row = conn.execute(
                "SELECT id, description FROM framework_nodes WHERE path = ?",
                (path,),
            ).fetchone()
            if row is None:
                print(f"[FAIL] missing node at path={path}")
                return 1
            node_id, current = row
            if current is None:
                print(f"[FAIL] null description at path={path}")
                return 1

            new_desc = current
            leaf_updated = 0
            leaf_skipped = 0
            leaf_not_found = 0

            for needle, replacement in fixes:
                if replacement in new_desc:
                    leaf_skipped += 1
                    continue
                if needle in new_desc:
                    new_desc = new_desc.replace(needle, replacement, 1)
                    leaf_updated += 1
                else:
                    leaf_not_found += 1
                    print(
                        f"[NOT_FOUND] path={path} needle={needle[:60]!r}"
                    )

            if new_desc != current:
                conn.execute(
                    "UPDATE framework_nodes SET description = ? WHERE id = ?",
                    (new_desc, node_id),
                )
                affected_paths += 1
                print(
                    f"[UPDATE] id={node_id} path={path} "
                    f"applied={leaf_updated} skipped={leaf_skipped} "
                    f"not_found={leaf_not_found} "
                    f"len={len(new_desc)} (was {len(current)})"
                )
            else:
                print(
                    f"[SKIP]   id={node_id} path={path} "
                    f"applied=0 skipped={leaf_skipped} "
                    f"not_found={leaf_not_found}"
                )

            total_updated += leaf_updated
            total_skipped += leaf_skipped
            total_not_found += leaf_not_found

        conn.commit()
        post_hash = sha256_of_affected(conn)
        print(f"[POST] sha256={post_hash}")
    finally:
        conn.close()

    total_fixes = sum(len(v) for v in QA_FIXES.values())
    print(
        f"[SUMMARY] leaves_affected={affected_paths}/{len(QA_FIXES)} "
        f"fixes_applied={total_updated} skipped_already_applied={total_skipped} "
        f"not_found={total_not_found} total_fix_rules={total_fixes}"
    )
    if total_not_found > 0:
        print(
            "[WARN] some needles were not found -- either already fixed by a "
            "different path or content drift; inspect log above."
        )
    print("[DONE]")
    return 0


if __name__ == "__main__":
    sys.exit(main())
