import { useMemo } from "react";
import { Link, useSearchParams } from "react-router-dom";
import { useQuery } from "@tanstack/react-query";
import { api } from "../utils/api";
import GoldenBadge from "../components/ui/GoldenBadge";

type GoldenItemType =
  | "framework_node"
  | "behavioral_example"
  | "company_document";

interface GoldenItem {
  id: number;
  item_type: GoldenItemType;
  title: string;
  preview: string;
  golden_at: string | null;
  url_path: string;
}

type TabSlug = "all" | GoldenItemType;

const TAB_ORDER: TabSlug[] = [
  "all",
  "framework_node",
  "behavioral_example",
  "company_document",
];

const TAB_LABELS: Record<TabSlug, string> = {
  all: "All",
  framework_node: "Framework Nodes",
  behavioral_example: "Behavioral",
  company_document: "Company Docs",
};

const TYPE_BADGE: Record<GoldenItemType, { label: string; cls: string }> = {
  framework_node: {
    label: "framework",
    cls: "bg-blue-50 text-blue-700 border-blue-200",
  },
  behavioral_example: {
    label: "behavioral",
    cls: "bg-purple-50 text-purple-700 border-purple-200",
  },
  company_document: {
    label: "company doc",
    cls: "bg-green-50 text-green-700 border-green-200",
  },
};

const EMPTY_PER_TAB: Record<TabSlug, string> = {
  all: "No items marked golden yet.",
  framework_node:
    "No items marked golden in this category yet.",
  behavioral_example:
    "No items marked golden in this category yet.",
  company_document:
    "No items marked golden in this category yet.",
};

function isTabSlug(v: string | null): v is TabSlug {
  return !!v && (TAB_ORDER as string[]).includes(v);
}

function formatGoldenAt(iso: string | null): string {
  if (!iso) return "-";
  const d = new Date(iso);
  if (Number.isNaN(d.getTime())) return "-";
  return d.toLocaleDateString();
}

export default function GoldenCollection() {
  const [params, setParams] = useSearchParams();
  const rawTab = params.get("tab");
  const activeTab: TabSlug = isTabSlug(rawTab) ? rawTab : "all";

  const { data, isLoading, isError } = useQuery<GoldenItem[]>({
    queryKey: ["golden"],
    queryFn: () => api.get<GoldenItem[]>("/golden"),
    staleTime: 30_000,
  });

  const items = data ?? [];

  const tabCount = (tab: TabSlug): number =>
    tab === "all" ? items.length : items.filter((i) => i.item_type === tab).length;

  const visibleItems = useMemo(
    () =>
      activeTab === "all"
        ? items
        : items.filter((i) => i.item_type === activeTab),
    [items, activeTab],
  );

  const selectTab = (tab: TabSlug) => {
    const next: Record<string, string> = {};
    if (tab !== "all") next.tab = tab;
    setParams(next);
  };

  const tabBtn = (active: boolean) =>
    "px-4 py-2 rounded-lg border text-sm font-medium transition-all " +
    (active
      ? "border-orange-400 bg-orange-50 text-orange-700"
      : "border-gray-200 bg-white text-gray-600 hover:border-gray-300");

  return (
    <div className="p-6 h-full overflow-y-scroll">
      <div className="flex items-center gap-2 mb-2">
        <svg
          viewBox="0 0 24 24"
          width="22"
          height="22"
          fill="currentColor"
          className="text-orange-500"
          aria-hidden="true"
        >
          <path d="M12 2.5l2.9 6.3 6.9.7-5.2 4.7 1.5 6.8L12 17.7l-6.1 3.3 1.5-6.8L2.2 9.5l6.9-.7L12 2.5z" />
        </svg>
        <h1 className="text-2xl font-bold">Golden Collection</h1>
      </div>
      <p className="text-sm text-gray-500 mb-6">
        Items you have curated as canonical reference material across the
        framework, behavioral examples, and company prep docs. Click any
        card to jump back to its origin page.
      </p>

      <div className="flex flex-wrap items-center gap-2 mb-6">
        {TAB_ORDER.map((tab) => (
          <button
            key={tab}
            type="button"
            onClick={() => selectTab(tab)}
            className={tabBtn(tab === activeTab)}
          >
            {TAB_LABELS[tab]}
            <span className="ml-2 text-xs text-gray-400">
              ({tabCount(tab)})
            </span>
          </button>
        ))}
      </div>

      {isLoading ? (
        <div className="p-8 text-center text-sm text-gray-500 bg-gray-50 border border-gray-200 rounded-lg">
          Loading...
        </div>
      ) : isError ? (
        <div className="p-8 text-center text-sm text-red-600 bg-red-50 border border-red-200 rounded-lg">
          Failed to load golden items.
        </div>
      ) : visibleItems.length === 0 ? (
        <div className="p-8 text-center text-sm text-gray-500 bg-gray-50 border border-gray-200 rounded-lg">
          {EMPTY_PER_TAB[activeTab]}
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {visibleItems.map((item) => {
            const badge = TYPE_BADGE[item.item_type];
            return (
              <Link
                key={`${item.item_type}-${item.id}`}
                to={item.url_path}
                className="block p-4 rounded-lg border bg-white border-gray-200 hover:border-orange-400 hover:shadow-md transition-all border-l-4 border-l-orange-500 bg-orange-50/30"
              >
                <div className="flex items-start justify-between gap-2">
                  <span
                    className={
                      "text-[10px] px-2 py-0.5 rounded-full border uppercase tracking-wider " +
                      badge.cls
                    }
                  >
                    {badge.label}
                  </span>
                  <GoldenBadge golden={true} />
                </div>
                <div className="mt-2 font-medium text-gray-800 line-clamp-2">
                  {item.title}
                </div>
                {item.preview && (
                  <div className="mt-2 text-xs text-gray-500 line-clamp-3">
                    {item.preview}
                  </div>
                )}
                <div className="mt-3 text-[11px] text-gray-400">
                  Promoted {formatGoldenAt(item.golden_at)}
                </div>
              </Link>
            );
          })}
        </div>
      )}
    </div>
  );
}
