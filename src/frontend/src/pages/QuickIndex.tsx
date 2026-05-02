import { useState } from "react";
import { Link, useSearchParams } from "react-router-dom";
import { useQuery } from "@tanstack/react-query";
import { api } from "../utils/api";
import type { BehavioralThemeSummary } from "../types/behavioral";
import type { FrameworkNode } from "../types/framework";
import { useRouteScrollRestore } from "../hooks/useRouteScrollRestore";
import ProblemDrawer from "../components/problems/ProblemDrawer";
import FrameworkNodeDrawer from "../components/framework/FrameworkNodeDrawer";

const LC_PROBLEMS: {
  dbId: number;
  lcId: number;
  title: string;
  family: string;
}[] = [
  { dbId: 93, lcId: 146, title: "LRU Cache", family: "stateful_ds_design" },
  { dbId: 179, lcId: 716, title: "Max Stack", family: "stateful_ds_design" },
  { dbId: 182, lcId: 432, title: "All O`one Data Structure", family: "stateful_ds_design" },
  { dbId: 99, lcId: 215, title: "Kth Largest Element in an Array", family: "heap_topk" },
  { dbId: 510, lcId: 373, title: "Find K Pairs with Smallest Sums", family: "heap_topk" },
  { dbId: 115, lcId: 127, title: "Word Ladder", family: "graph_bfs" },
  { dbId: 48, lcId: 269, title: "Alien Dictionary", family: "graph_topo_sort" },
  { dbId: 42, lcId: 200, title: "Number of Islands", family: "graph_grid_traversal" },
  { dbId: 29, lcId: 235, title: "Lowest Common Ancestor of a BST", family: "tree_lca" },
  { dbId: 38, lcId: 212, title: "Word Search II", family: "trie_multiword" },
  { dbId: 10, lcId: 15, title: "3Sum", family: "two_pointers_target" },
  { dbId: 303, lcId: 28, title: "Find the Index of the First Occurrence in a String", family: "string_matching_kmp" },
  { dbId: 344, lcId: 214, title: "Shortest Palindrome", family: "string_matching_kmp" },
  { dbId: 672, lcId: 686, title: "Repeated String Match", family: "string_matching_kmp" },
  { dbId: 352, lcId: 796, title: "Rotate String", family: "string_matching_kmp" },
  { dbId: 1091, lcId: 1392, title: "Longest Happy Prefix", family: "string_matching_kmp" },
  { dbId: 805, lcId: 2503, title: "Max Points From Grid Queries", family: "offline_queries_dsu" },
  { dbId: 216, lcId: 2791, title: "Palindrome Paths in Tree", family: "tree_dp_rerooting" },
  { dbId: 183, lcId: 2858, title: "Min Edge Reversals", family: "tree_dp_rerooting" },
  { dbId: 227, lcId: 399, title: "Evaluate Division", family: "union_find_weighted" },
];

// Render order + display labels for non-Stateful-DS family groups.
// Insertion order is the render order in the UI.
const FAMILY_LABELS: Record<string, string> = {
  heap_topk: "Heap / Top-K",
  graph_bfs: "Graph BFS (Word Ladder family)",
  graph_topo_sort: "Graph Topological Sort",
  graph_grid_traversal: "Graph / Grid Traversal",
  tree_lca: "Tree: LCA",
  trie_multiword: "Trie: Multi-word Search",
  two_pointers_target: "Two-Pointers Target Sum",
  string_matching_kmp: "String Matching (KMP family)",
  offline_queries_dsu: "Offline Queries + DSU",
  tree_dp_rerooting: "Tree DP / Rerooting",
  union_find_weighted: "Weighted Union-Find",
};

// Stateful data-structure design family (problems.family='stateful_ds_design').
// Rendered as a collapsible group above ungrouped LC problems.
const STATEFUL_DS_DESIGN: { lcId: number; title: string }[] = [
  { lcId: 146, title: "LRU Cache" },
  { lcId: 362, title: "Design Hit Counter" },
  { lcId: 432, title: "All O`one Data Structure" },
  { lcId: 460, title: "LFU Cache" },
  { lcId: 703, title: "Kth Largest Element in a Stream" },
  { lcId: 716, title: "Max Stack" },
  { lcId: 895, title: "Maximum Frequency Stack" },
  { lcId: 1146, title: "Snapshot Array" },
  { lcId: 1244, title: "Design A Leaderboard" },
  { lcId: 1825, title: "Finding MK Average" },
  { lcId: 1845, title: "Seat Reservation Manager" },
];

const ML_PROBLEMS: { dbId: number; title: string }[] = [
  { dbId: 1064, title: "K-Means (K-Means++)" },
  { dbId: 1102, title: "Linear Regression (closed-form lstsq + GD)" },
  { dbId: 1106, title: "K-Nearest Neighbors (KNN + Weighted)" },
  { dbId: 1107, title: "Logistic Regression (Sigmoid + Stable BCE + GD)" },
  { dbId: 1108, title: "Geometric Median (Weiszfeld + Vardi-Zhang 1999)" },
];

const CLUSTER_FAMILIES: { id: string; label: string; theme_slugs: string[] }[] = [
  { id: "failure", label: "Failure & Ownership", theme_slugs: ["failure_setback", "ownership_accountability"] },
  { id: "conflict", label: "Conflict, Collaboration & Integrity", theme_slugs: ["conflict_disagreement", "collaboration_teamwork", "ethical_integrity_backbone"] },
  { id: "decision", label: "Decision under Ambiguity", theme_slugs: ["prioritization_tradeoffs", "ambiguity_uncertainty"] },
  { id: "execution", label: "Execution & Pressure", theme_slugs: ["deadline_pressure", "process_systems", "oncall_prod_incident"] },
  { id: "leadership", label: "Leadership & People", theme_slugs: ["leadership_direction", "mentoring_coaching"] },
  { id: "technical", label: "Technical Depth", theme_slugs: ["technical_problem_solving", "code_quality_tech_debt"] },
  { id: "data", label: "Data & Customer", theme_slugs: ["data_analysis", "customer_user_focus"] },
];

const ALL_KNOWN_SLUGS = new Set(CLUSTER_FAMILIES.flatMap((f) => f.theme_slugs));

type KnowledgeTab = {
  id: string;
  label: string;
  pillarPath: string;
};

const KNOWLEDGE_TABS: KnowledgeTab[] = [
  { id: "stats", label: "Stats", pillarPath: "pillar7" },
  { id: "llm", label: "LLM", pillarPath: "pillar6" },
  { id: "ml_theory", label: "ML Theory", pillarPath: "pillar2" },
  { id: "ml_system_design", label: "ML System Design", pillarPath: "pillar3" },
  { id: "mlops", label: "MLOps", pillarPath: "pillar5" },
  { id: "applied_ml", label: "Applied ML", pillarPath: "pillar4" },
];

const BASE_TABS = ["lc", "ml", "bq"] as const;
const KNOWLEDGE_TAB_IDS = KNOWLEDGE_TABS.map((t) => t.id);
const ALL_TAB_IDS: string[] = [...BASE_TABS, ...KNOWLEDGE_TAB_IDS];

type SectionType = string;

/** Collect all leaf descendants of a node. */
function collectLeaves(node: FrameworkNode): FrameworkNode[] {
  if (!node.children?.length) return [node];
  return node.children.flatMap(collectLeaves);
}

/** Group leaves by their depth-1 category (immediate child of the pillar root). */
function getGroupedLeaves(
  pillar: FrameworkNode,
): { category: string; leaves: FrameworkNode[] }[] {
  if (!pillar.children?.length) return [];
  const groups: { category: string; leaves: FrameworkNode[] }[] = [];
  for (const cat of pillar.children) {
    const leaves = collectLeaves(cat);
    if (leaves.length > 0) {
      groups.push({ category: cat.title, leaves });
    }
  }
  return groups;
}

export default function QuickIndex() {
  useRouteScrollRestore();
  const [params, setParams] = useSearchParams();
  const raw = params.get("section");
  const section: SectionType = raw && ALL_TAB_IDS.includes(raw) ? raw : "lc";

  const [drawerLcId, setDrawerLcId] = useState<number | null>(null);
  const [drawerDbId, setDrawerDbId] = useState<number | null>(null);
  const [drawerNodeId, setDrawerNodeId] = useState<number | null>(null);
  const closeDrawer = () => {
    setDrawerLcId(null);
    setDrawerDbId(null);
  };
  const closeNodeDrawer = () => setDrawerNodeId(null);

  const { data: themes } = useQuery({
    queryKey: ["behavioral-themes"],
    queryFn: () => api.get<BehavioralThemeSummary[]>("/behavioral/themes"),
    enabled: section === "bq",
    staleTime: Infinity,
    gcTime: 1000 * 60 * 60,
  });

  const isKnowledgeTab = KNOWLEDGE_TAB_IDS.includes(section);

  const { data: tree } = useQuery<FrameworkNode[]>({
    queryKey: ["framework", "tree"],
    queryFn: () => api.get<FrameworkNode[]>("/framework/tree"),
    enabled: isKnowledgeTab,
    staleTime: 60_000,
  });

  const themeBySlug = new Map(
    (themes ?? []).map((t) => [t.slug, t]),
  );

  const otherThemes = (themes ?? []).filter((t) => !ALL_KNOWN_SLUGS.has(t.slug));

  const activeTab = KNOWLEDGE_TABS.find((t) => t.id === section);
  const pillarRoot = activeTab
    ? (tree ?? []).find((n) => n.path === activeTab.pillarPath) ?? null
    : null;
  const groupedLeaves = pillarRoot ? getGroupedLeaves(pillarRoot) : [];

  const baseTabBtn = (active: boolean) =>
    "px-4 py-2 rounded-lg border text-sm font-medium transition-all " +
    (active
      ? "border-blue-500 bg-blue-50 text-blue-700"
      : "border-gray-200 bg-white text-gray-600 hover:border-gray-300");

  return (
    <div className="p-6 h-full overflow-y-scroll">
      <h1 className="text-2xl font-bold mb-6">Quick Index</h1>

      <div className="flex flex-wrap gap-2 mb-6">
        {BASE_TABS.map((s) => (
          <button
            key={s}
            onClick={() => setParams({ section: s })}
            className={baseTabBtn(section === s)}
          >
            {s === "lc" ? "LeetCode" : s === "ml" ? "ML Coding" : "Behavioral"}
          </button>
        ))}
        <span className="mx-1 border-l border-gray-200" aria-hidden />
        {KNOWLEDGE_TABS.map((t) => (
          <button
            key={t.id}
            onClick={() => setParams({ section: t.id })}
            className={baseTabBtn(section === t.id)}
          >
            {t.label}
          </button>
        ))}
      </div>

      {section === "lc" && (
        <div className="space-y-6">
          <details open className="group">
            <summary className="cursor-pointer text-sm font-semibold text-gray-500 uppercase tracking-wider mb-2 select-none">
              Stateful Data Structure Design
              <span className="ml-2 text-xs font-normal text-gray-400">
                ({STATEFUL_DS_DESIGN.length})
              </span>
            </summary>
            <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4 mt-3">
              {STATEFUL_DS_DESIGN.map((p) => (
                <button
                  key={p.lcId}
                  type="button"
                  onClick={() => {
                    setDrawerDbId(null);
                    setDrawerLcId(p.lcId);
                  }}
                  className="text-left block p-4 rounded-lg border border-gray-200 hover:border-blue-400 hover:shadow-md transition-all bg-white"
                >
                  <span className="text-xs text-gray-400 font-mono">
                    #{p.lcId}
                  </span>
                  <div className="mt-1 font-medium text-gray-800">
                    {p.title}
                  </div>
                </button>
              ))}
            </div>
          </details>
          {Object.keys(FAMILY_LABELS).map((familySlug) => {
            const familyProblems = LC_PROBLEMS.filter(
              (p) => p.family === familySlug,
            );
            if (familyProblems.length === 0) return null;
            return (
              <details key={familySlug} open className="group">
                <summary className="cursor-pointer text-sm font-semibold text-gray-500 uppercase tracking-wider mb-2 select-none">
                  {FAMILY_LABELS[familySlug]}
                  <span className="ml-2 text-xs font-normal text-gray-400">
                    ({familyProblems.length})
                  </span>
                </summary>
                <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4 mt-3">
                  {familyProblems.map((p) => (
                    <button
                      key={p.dbId}
                      type="button"
                      onClick={() => {
                        setDrawerDbId(null);
                        setDrawerLcId(p.lcId);
                      }}
                      className="text-left block p-4 rounded-lg border border-gray-200 hover:border-blue-400 hover:shadow-md transition-all bg-white"
                    >
                      <span className="text-xs text-gray-400 font-mono">
                        #{p.lcId}
                      </span>
                      <div className="mt-1 font-medium text-gray-800">
                        {p.title}
                      </div>
                    </button>
                  ))}
                </div>
              </details>
            );
          })}
        </div>
      )}

      {section === "ml" && (
        <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4">
          {ML_PROBLEMS.map((p) => (
            <button
              key={p.dbId}
              type="button"
              onClick={() => {
                setDrawerLcId(null);
                setDrawerDbId(p.dbId);
              }}
              className="text-left block p-4 rounded-lg border border-gray-200 hover:border-blue-400 hover:shadow-md transition-all bg-white"
            >
              <span className="text-xs text-gray-400 font-mono">Custom</span>
              <div className="mt-1 font-medium text-gray-800">{p.title}</div>
            </button>
          ))}
        </div>
      )}

      {section === "bq" && (
        <div className="space-y-8">
          {CLUSTER_FAMILIES.map((family) => {
            const familyThemes = family.theme_slugs
              .map((slug) => themeBySlug.get(slug))
              .filter((t): t is BehavioralThemeSummary => t !== undefined);
            if (familyThemes.length === 0) return null;
            return (
              <div key={family.id}>
                <h3 className="text-sm font-semibold text-gray-500 uppercase tracking-wider mb-2">
                  {family.label}
                </h3>
                <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4">
                  {familyThemes.map((theme) => (
                    <ThemeCard key={theme.slug} theme={theme} />
                  ))}
                </div>
              </div>
            );
          })}
          {otherThemes.length > 0 && (
            <div>
              <h3 className="text-sm font-semibold text-gray-500 uppercase tracking-wider mb-2">
                Other
              </h3>
              <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4">
                {otherThemes.map((theme) => (
                  <ThemeCard key={theme.slug} theme={theme} />
                ))}
              </div>
            </div>
          )}
        </div>
      )}

      {isKnowledgeTab && (
        <div className="space-y-8">
          {!tree && (
            <p className="text-gray-400 italic">Loading knowledge tree...</p>
          )}
          {tree && !pillarRoot && (
            <p className="text-gray-400 italic">
              Pillar not found in framework tree.
            </p>
          )}
          {groupedLeaves.map((group) => (
            <div key={group.category}>
              <h3 className="text-sm font-semibold text-gray-500 uppercase tracking-wider mb-2">
                {group.category}
              </h3>
              <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4">
                {group.leaves.map((leaf) => (
                  <button
                    key={leaf.id}
                    type="button"
                    onClick={() => setDrawerNodeId(leaf.id)}
                    className="text-left block p-4 rounded-lg border border-gray-200 hover:border-blue-400 hover:shadow-md transition-all bg-white"
                  >
                    <div className="flex items-start justify-between gap-2">
                      <div className="font-medium text-gray-800">
                        {leaf.title}
                      </div>
                      <span className="text-xs text-gray-500 font-mono shrink-0">
                        {leaf.progress_pct}%
                      </span>
                    </div>
                    <div className="mt-2 h-1 bg-gray-100 rounded-full overflow-hidden">
                      <div
                        className="h-full bg-blue-500 rounded-full transition-all"
                        style={{ width: `${leaf.progress_pct}%` }}
                      />
                    </div>
                  </button>
                ))}
              </div>
            </div>
          ))}
        </div>
      )}

      <ProblemDrawer lcId={drawerLcId} dbId={drawerDbId} onClose={closeDrawer} />
      <FrameworkNodeDrawer nodeId={drawerNodeId} onClose={closeNodeDrawer} />
    </div>
  );
}

function ThemeCard({ theme }: { theme: BehavioralThemeSummary }) {
  const dimmed = theme.question_count === 0 && theme.example_count === 0;
  return (
    <Link
      to={`/behavioral/theme/${theme.slug}?from=quick-index`}
      className={
        "block p-4 rounded-lg border transition-all bg-white " +
        (dimmed
          ? "border-gray-100 text-gray-400"
          : "border-gray-200 hover:border-blue-400 hover:shadow-md")
      }
    >
      <div className={"font-medium " + (dimmed ? "text-gray-400" : "text-gray-800")}>
        {theme.label}
      </div>
      <div className={"mt-1 text-xs " + (dimmed ? "text-gray-300" : "text-gray-500")}>
        {theme.question_count} questions / {theme.example_count} examples
      </div>
    </Link>
  );
}
