import { useMemo } from "react";
import { Link, useSearchParams } from "react-router-dom";
import { useQuery } from "@tanstack/react-query";
import { api } from "../utils/api";
import type { FrameworkNode } from "../types/framework";
import { useRouteScrollRestore } from "../hooks/useRouteScrollRestore";
import FrameworkNodeDrawer from "../components/framework/FrameworkNodeDrawer";
import GoldenBadge from "../components/ui/GoldenBadge";
import { goldenCardClass } from "../utils/goldenStyle";

type CategorySlug =
  | "classical_ml"
  | "eval_data"
  | "unsupervised"
  | "dl_training"
  | "attention_transformer"
  | "llm_stats";

type InterviewFreq = "high" | "mid" | "low";

interface InventoryItem {
  id: number;
  slug: string;
  category: CategorySlug;
  title_zh: string;
  title_en: string;
  interview_freq: InterviewFreq;
}

const CATEGORY_LABELS: Record<CategorySlug, string> = {
  classical_ml: "Classical ML",
  eval_data: "Evaluation & Data",
  unsupervised: "Unsupervised",
  dl_training: "DL Training",
  attention_transformer: "Attention & Transformer",
  llm_stats: "LLM & Stats",
};

const CATEGORY_ORDER: CategorySlug[] = [
  "classical_ml",
  "eval_data",
  "unsupervised",
  "dl_training",
  "attention_transformer",
  "llm_stats",
];

type TabSlug = CategorySlug | "all";
const TAB_ORDER: TabSlug[] = ["all", ...CATEGORY_ORDER];

// Mirrors data/ml_fundamentals_inventory.yaml. Keep in sync when the YAML changes.
const INVENTORY: InventoryItem[] = [
  { id: 1, slug: "bias-variance-tradeoff", category: "classical_ml", title_zh: "Bias-Variance 权衡", title_en: "Bias-Variance Tradeoff", interview_freq: "high" },
  { id: 2, slug: "l1-vs-l2-regularization", category: "classical_ml", title_zh: "L1 vs L2 正则化", title_en: "L1 vs L2 Regularization", interview_freq: "high" },
  { id: 3, slug: "logistic-regression-loss", category: "classical_ml", title_zh: "Logistic Regression 损失函数", title_en: "Logistic Regression Loss", interview_freq: "high" },
  { id: 4, slug: "gbdt-vs-rf-xgboost", category: "classical_ml", title_zh: "GBDT vs Random Forest + XGBoost 改进", title_en: "GBDT vs Random Forest + XGBoost Improvements", interview_freq: "high" },
  { id: 5, slug: "class-imbalance-handling", category: "eval_data", title_zh: "类别不平衡处理", title_en: "Class Imbalance Handling", interview_freq: "high" },
  { id: 6, slug: "auc-vs-pr-curve", category: "eval_data", title_zh: "AUC 与 PR 曲线", title_en: "AUC vs PR Curve", interview_freq: "high" },
  { id: 7, slug: "k-means-assumptions-and-failures", category: "unsupervised", title_zh: "K-means 假设与失败场景", title_en: "K-means Assumptions and Failure Modes", interview_freq: "high" },
  { id: 8, slug: "em-and-gmm", category: "unsupervised", title_zh: "EM + GMM", title_en: "EM Algorithm with GMM", interview_freq: "mid" },
  { id: 9, slug: "batchnorm-vs-layernorm", category: "dl_training", title_zh: "BatchNorm vs LayerNorm", title_en: "BatchNorm vs LayerNorm", interview_freq: "high" },
  { id: 10, slug: "adam-vs-sgd-adamw", category: "dl_training", title_zh: "Adam vs SGD + AdamW", title_en: "Adam vs SGD and AdamW", interview_freq: "high" },
  { id: 11, slug: "vanishing-exploding-gradient", category: "dl_training", title_zh: "梯度消失 / 爆炸", title_en: "Vanishing / Exploding Gradient", interview_freq: "mid" },
  { id: 12, slug: "dropout", category: "dl_training", title_zh: "Dropout", title_en: "Dropout", interview_freq: "mid" },
  { id: 13, slug: "activation-function-evolution", category: "dl_training", title_zh: "激活函数演进", title_en: "Activation Function Evolution", interview_freq: "mid" },
  { id: 14, slug: "cross-entropy-kl-divergence", category: "classical_ml", title_zh: "Cross-Entropy 与 KL Divergence", title_en: "Cross-Entropy and KL Divergence", interview_freq: "high" },
  { id: 15, slug: "self-attention-complexity-optimization", category: "attention_transformer", title_zh: "Self-Attention 复杂度与优化", title_en: "Self-Attention Complexity and Optimizations", interview_freq: "high" },
  { id: 16, slug: "scaled-dot-product-attention", category: "attention_transformer", title_zh: "Scaled Dot-Product Attention", title_en: "Scaled Dot-Product Attention", interview_freq: "high" },
  { id: 17, slug: "mha-mqa-gqa", category: "attention_transformer", title_zh: "MHA / MQA / GQA 多头注意力权衡", title_en: "MHA vs MQA vs GQA", interview_freq: "high" },
  { id: 18, slug: "positional-encoding", category: "attention_transformer", title_zh: "位置编码：Sinusoidal / Learned / RoPE / ALiBi", title_en: "Positional Encoding (Sinusoidal, Learned, RoPE, ALiBi)", interview_freq: "mid" },
  { id: 19, slug: "kv-cache", category: "attention_transformer", title_zh: "KV cache 原理与显存", title_en: "KV Cache — Mechanics and Memory Cost", interview_freq: "mid" },
  { id: 20, slug: "pre-norm-vs-post-norm", category: "attention_transformer", title_zh: "Pre-norm vs Post-norm", title_en: "Pre-norm vs Post-norm", interview_freq: "low" },
  { id: 21, slug: "sft-rlhf-dpo", category: "llm_stats", title_zh: "SFT / RLHF / DPO 目标函数", title_en: "SFT / RLHF / DPO Objectives", interview_freq: "high" },
  { id: 22, slug: "moe-routing-load-balancing", category: "llm_stats", title_zh: "MoE routing 与 load balancing loss", title_en: "MoE Routing and Load-Balancing Loss", interview_freq: "mid" },
  { id: 23, slug: "tokenization-bpe-wordpiece-sentencepiece", category: "llm_stats", title_zh: "Tokenization：BPE / WordPiece / SentencePiece", title_en: "Tokenization (BPE, WordPiece, SentencePiece)", interview_freq: "mid" },
  { id: 24, slug: "scaling-law-chinchilla", category: "llm_stats", title_zh: "Scaling law：Chinchilla 修正 Kaplan", title_en: "Scaling Law (Chinchilla vs Kaplan)", interview_freq: "low" },
  { id: 25, slug: "mle-vs-map", category: "llm_stats", title_zh: "MLE vs MAP", title_en: "MLE vs MAP Estimation", interview_freq: "high" },
  { id: 26, slug: "clt-vs-lln", category: "llm_stats", title_zh: "中心极限定理 vs 大数定律", title_en: "Central Limit Theorem vs Law of Large Numbers", interview_freq: "mid" },
  { id: 27, slug: "ab-test-pvalue-sample-size-multiple-testing", category: "llm_stats", title_zh: "A/B test：p-value、样本量、多重检验", title_en: "A/B Test (p-value, Sample Size, Multiple Testing)", interview_freq: "mid" },
];

const ML_FUNDAMENTALS_ROOT_PATH = "ml-fundamentals";

const FREQ_BADGE: Record<InterviewFreq, { label: string; cls: string }> = {
  high: { label: "high freq", cls: "bg-red-50 text-red-700 border-red-200" },
  mid: { label: "mid freq", cls: "bg-amber-50 text-amber-700 border-amber-200" },
  low: { label: "low freq", cls: "bg-gray-50 text-gray-600 border-gray-200" },
};

function isTabSlug(v: string | null): v is TabSlug {
  return !!v && (TAB_ORDER as string[]).includes(v);
}

interface LeafInfo {
  id: number;
  is_golden: boolean;
}

/** Walk subtree and collect slug -> {id, is_golden} for all leaves. */
function buildSlugToLeafInfo(
  root: FrameworkNode | undefined,
): Map<string, LeafInfo> {
  const map = new Map<string, LeafInfo>();
  if (!root) return map;
  const walk = (n: FrameworkNode) => {
    if (!n.children?.length) {
      // leaf path format: 'ml-fundamentals/<cat>/<slug>'
      const parts = n.path.split("/");
      if (parts.length === 3 && parts[0] === ML_FUNDAMENTALS_ROOT_PATH) {
        map.set(parts[2], { id: n.id, is_golden: Boolean(n.is_golden) });
      }
      return;
    }
    n.children.forEach(walk);
  };
  walk(root);
  return map;
}

export default function MLFundamentals() {
  useRouteScrollRestore();
  const [params, setParams] = useSearchParams();

  const rawCat = params.get("cat");
  const rawSlug = params.get("slug");
  const goldenOnly = params.get("golden") === "1";

  const slugByCat = useMemo(() => {
    const m = new Map<string, CategorySlug>();
    INVENTORY.forEach((it) => m.set(it.slug, it.category));
    return m;
  }, []);

  const activeCat: TabSlug = isTabSlug(rawCat)
    ? rawCat
    : rawSlug && slugByCat.has(rawSlug)
    ? (slugByCat.get(rawSlug) as CategorySlug)
    : "all";

  const activeSlug =
    rawSlug &&
    slugByCat.has(rawSlug) &&
    (activeCat === "all" || slugByCat.get(rawSlug) === activeCat)
      ? rawSlug
      : null;

  const { data: tree } = useQuery<FrameworkNode[]>({
    queryKey: ["framework", "tree"],
    queryFn: () => api.get<FrameworkNode[]>("/framework/tree"),
    staleTime: 60_000,
  });

  const slugToLeafInfo = useMemo(() => {
    const root = (tree ?? []).find((n) => n.path === ML_FUNDAMENTALS_ROOT_PATH);
    return buildSlugToLeafInfo(root);
  }, [tree]);

  const drawerNodeId = activeSlug
    ? slugToLeafInfo.get(activeSlug)?.id ?? null
    : null;

  /** Items visible in the current tab, with goldenOnly filter applied. */
  const categoryItems = useMemo(() => {
    const base =
      activeCat === "all"
        ? [...INVENTORY].sort((a, b) => a.id - b.id)
        : INVENTORY.filter((it) => it.category === activeCat);
    if (!goldenOnly) return base;
    return base.filter((it) => slugToLeafInfo.get(it.slug)?.is_golden);
  }, [activeCat, goldenOnly, slugToLeafInfo]);

  /** Per-tab count, reflecting goldenOnly filter so tab labels stay accurate. */
  const tabCount = (tab: TabSlug): number => {
    const base =
      tab === "all"
        ? INVENTORY
        : INVENTORY.filter((it) => it.category === tab);
    if (!goldenOnly) return base.length;
    return base.filter((it) => slugToLeafInfo.get(it.slug)?.is_golden).length;
  };

  /** Write params while preserving goldenOnly across navigation. */
  const writeParams = (next: Record<string, string>) => {
    if (goldenOnly) next.golden = "1";
    setParams(next);
  };

  const selectTab = (tab: TabSlug) => {
    // Preserve slug if it belongs to the new tab (all accepts any), else clear.
    const next: Record<string, string> = { cat: tab };
    if (
      rawSlug &&
      slugByCat.has(rawSlug) &&
      (tab === "all" || slugByCat.get(rawSlug) === tab)
    ) {
      next.slug = rawSlug;
    }
    writeParams(next);
  };

  const openCard = (slug: string, itemCat: CategorySlug) => {
    // From the All tab, stay in All on open; otherwise pin to the item's cat.
    writeParams({ cat: activeCat === "all" ? "all" : itemCat, slug });
  };

  const closeDrawer = () => {
    writeParams({ cat: activeCat });
  };

  const toggleGoldenOnly = () => {
    const next: Record<string, string> = { cat: activeCat };
    if (activeSlug) next.slug = activeSlug;
    if (!goldenOnly) next.golden = "1";
    setParams(next);
  };

  const tabBtn = (active: boolean) =>
    "px-4 py-2 rounded-lg border text-sm font-medium transition-all " +
    (active
      ? "border-blue-500 bg-blue-50 text-blue-700"
      : "border-gray-200 bg-white text-gray-600 hover:border-gray-300");

  return (
    <div className="p-6 h-full overflow-y-scroll">
      <h1 className="text-2xl font-bold mb-2">ML 八股文 · Fundamentals</h1>
      <p className="text-sm text-gray-500 mb-6">
        27 high-frequency ML interview questions, grouped by category. Click any
        card to open the drawer; share via URL (<code>?cat=…&amp;slug=…</code>).
      </p>

      <div className="flex flex-wrap items-center gap-2 mb-6">
        {TAB_ORDER.map((tab) => (
          <button
            key={tab}
            onClick={() => selectTab(tab)}
            className={tabBtn(tab === activeCat)}
          >
            {tab === "all" ? "All" : CATEGORY_LABELS[tab]}
            <span className="ml-2 text-xs text-gray-400">
              ({tabCount(tab)})
            </span>
          </button>
        ))}
        <button
          type="button"
          onClick={toggleGoldenOnly}
          aria-pressed={goldenOnly}
          title={goldenOnly ? "Show all items" : "Show only golden items"}
          className={
            "ml-auto px-3 py-2 rounded-lg border text-sm font-medium transition-all inline-flex items-center gap-1.5 " +
            (goldenOnly
              ? "border-orange-300 bg-orange-50 text-orange-700"
              : "border-gray-200 bg-white text-gray-600 hover:border-gray-300")
          }
        >
          <svg
            viewBox="0 0 24 24"
            width="14"
            height="14"
            fill={goldenOnly ? "currentColor" : "none"}
            stroke="currentColor"
            strokeWidth={goldenOnly ? 0 : 2}
            strokeLinejoin="round"
            aria-hidden="true"
          >
            <path d="M12 2.5l2.9 6.3 6.9.7-5.2 4.7 1.5 6.8L12 17.7l-6.1 3.3 1.5-6.8L2.2 9.5l6.9-.7L12 2.5z" />
          </svg>
          Golden only
        </button>
      </div>

      {categoryItems.length === 0 ? (
        <div className="p-8 text-center text-sm text-gray-500 bg-gray-50 border border-gray-200 rounded-lg">
          {goldenOnly
            ? "No golden items in this category yet."
            : "No items in this category yet."}
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {categoryItems.map((it) => {
            const badge = FREQ_BADGE[it.interview_freq];
            const info = slugToLeafInfo.get(it.slug);
            const hasNode = info !== undefined;
            const isGolden = Boolean(info?.is_golden);
            return (
              <button
                key={it.slug}
                type="button"
                onClick={() => openCard(it.slug, it.category)}
                disabled={!hasNode}
                className={
                  "text-left block p-4 rounded-lg border bg-white transition-all " +
                  (hasNode
                    ? "border-gray-200 hover:border-blue-400 hover:shadow-md"
                    : "border-gray-100 opacity-60 cursor-not-allowed") +
                  " " +
                  goldenCardClass(isGolden)
                }
              >
                <div className="flex items-start justify-between gap-2">
                  <span className="text-xs text-gray-400 font-mono">
                    #{it.id}
                  </span>
                  <div className="flex items-center gap-1.5">
                    <GoldenBadge golden={isGolden} />
                    <span
                      className={
                        "text-[10px] px-2 py-0.5 rounded-full border uppercase tracking-wider " +
                        badge.cls
                      }
                    >
                      {badge.label}
                    </span>
                  </div>
                </div>
                <div className="mt-2 font-medium text-gray-800">
                  {it.title_zh}
                </div>
                <div className="mt-1 text-xs text-gray-500">{it.title_en}</div>
              </button>
            );
          })}
        </div>
      )}

      <div className="mt-10 pt-6 border-t border-gray-200 text-sm text-gray-500">
        <span>延伸: </span>
        <Link
          to="/quick-index?section=ml_system_design"
          className="text-blue-600 hover:underline"
        >
          MLSD pillar
        </Link>
      </div>

      <FrameworkNodeDrawer nodeId={drawerNodeId} onClose={closeDrawer} />
    </div>
  );
}
