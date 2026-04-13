import { useState } from "react";
import { Link, useSearchParams } from "react-router-dom";
import { useQuery } from "@tanstack/react-query";
import { api } from "../utils/api";
import type { BehavioralThemeSummary } from "../types/behavioral";
import { useRouteScrollRestore } from "../hooks/useRouteScrollRestore";
import ProblemDrawer from "../components/problems/ProblemDrawer";

const LC_PROBLEMS: { dbId: number; lcId: number; title: string }[] = [
  { dbId: 93, lcId: 146, title: "LRU Cache" },
  { dbId: 179, lcId: 716, title: "Max Stack" },
  { dbId: 182, lcId: 432, title: "All O`one Data Structure" },
  { dbId: 99, lcId: 215, title: "Kth Largest Element in an Array" },
  { dbId: 115, lcId: 127, title: "Word Ladder" },
  { dbId: 510, lcId: 373, title: "Find K Pairs with Smallest Sums" },
  { dbId: 29, lcId: 235, title: "Lowest Common Ancestor of a BST" },
  { dbId: 38, lcId: 212, title: "Word Search II" },
  { dbId: 48, lcId: 269, title: "Alien Dictionary" },
  { dbId: 10, lcId: 15, title: "3Sum" },
  { dbId: 42, lcId: 200, title: "Number of Islands" },
  { dbId: 805, lcId: 2503, title: "Max Points From Grid Queries" },
  { dbId: 216, lcId: 2791, title: "Palindrome Paths in Tree" },
  { dbId: 183, lcId: 2858, title: "Min Edge Reversals" },
];

const ML_PROBLEMS: { dbId: number; title: string }[] = [
  { dbId: 1064, title: "K-Means (K-Means++)" },
  { dbId: 1050, title: "Lock Combination BFS (Bidirectional)" },
];

const CLUSTER_FAMILIES: { id: string; label: string; theme_slugs: string[] }[] = [
  { id: "failure", label: "Failure & Ownership", theme_slugs: ["failure_setback", "ownership_accountability"] },
  { id: "conflict", label: "Conflict & Collaboration", theme_slugs: ["conflict_disagreement", "collaboration_teamwork"] },
  { id: "decision", label: "Decision under Ambiguity", theme_slugs: ["prioritization_tradeoffs", "ambiguity_uncertainty", "scope_creep_ambiguous"] },
  { id: "execution", label: "Execution & Pressure", theme_slugs: ["deadline_pressure", "process_systems", "oncall_prod_incident"] },
  { id: "leadership", label: "Leadership & People", theme_slugs: ["leadership_direction", "mentoring_coaching"] },
  { id: "technical", label: "Technical Depth", theme_slugs: ["technical_problem_solving", "code_quality_tech_debt"] },
  { id: "data", label: "Data and Decisions", theme_slugs: ["data_analysis"] },
];

const ALL_KNOWN_SLUGS = new Set(CLUSTER_FAMILIES.flatMap((f) => f.theme_slugs));

type SectionType = "lc" | "ml" | "bq";

export default function QuickIndex() {
  useRouteScrollRestore();
  const [params, setParams] = useSearchParams();
  const raw = params.get("section");
  const section: SectionType =
    raw === "lc" || raw === "ml" || raw === "bq" ? raw : "lc";

  const [drawerLcId, setDrawerLcId] = useState<number | null>(null);
  const [drawerDbId, setDrawerDbId] = useState<number | null>(null);
  const closeDrawer = () => {
    setDrawerLcId(null);
    setDrawerDbId(null);
  };

  const { data: themes } = useQuery({
    queryKey: ["behavioral-themes"],
    queryFn: () => api.get<BehavioralThemeSummary[]>("/behavioral/themes"),
    enabled: section === "bq",
    staleTime: Infinity,
    gcTime: 1000 * 60 * 60,
  });

  const themeBySlug = new Map(
    (themes ?? []).map((t) => [t.slug, t]),
  );

  const otherThemes = (themes ?? []).filter((t) => !ALL_KNOWN_SLUGS.has(t.slug));

  return (
    <div className="p-6 h-full overflow-y-scroll">
      <h1 className="text-2xl font-bold mb-6">Quick Index</h1>

      <div className="flex gap-2 mb-6">
        {(["lc", "ml", "bq"] as const).map((s) => (
          <button
            key={s}
            onClick={() => setParams({ section: s })}
            className={
              "px-4 py-2 rounded-lg border text-sm font-medium transition-all " +
              (section === s
                ? "border-blue-500 bg-blue-50 text-blue-700"
                : "border-gray-200 bg-white text-gray-600 hover:border-gray-300")
            }
          >
            {s === "lc" ? "LeetCode" : s === "ml" ? "ML Coding" : "Behavioral"}
          </button>
        ))}
      </div>

      {section === "lc" && (
        <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4">
          {LC_PROBLEMS.map((p) => (
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
              <div className="mt-1 font-medium text-gray-800">{p.title}</div>
            </button>
          ))}
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

      <ProblemDrawer lcId={drawerLcId} dbId={drawerDbId} onClose={closeDrawer} />
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
