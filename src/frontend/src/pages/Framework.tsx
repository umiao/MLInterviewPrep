import { useCallback, useState } from "react";
import { useQuery, useQueryClient } from "@tanstack/react-query";
import { api } from "../utils/api";
import FrameworkTreeView from "../components/FrameworkTreeView";
import FrameworkTreemap from "../components/FrameworkTreemap";
import NodeDetailPanel from "../components/NodeDetailPanel";
import StudyPlanCard from "../components/StudyPlanCard";
import type { FrameworkNode, FrameworkStats, NodeStatus } from "../types/framework";

type ViewMode = "tree" | "treemap";

const STATUS_COLORS: Record<NodeStatus, string> = {
  not_started: "bg-red-400",
  in_progress: "bg-yellow-400",
  review: "bg-blue-400",
  mastered: "bg-green-400",
};

const STATUS_LABELS: Record<NodeStatus, string> = {
  not_started: "Not Started",
  in_progress: "In Progress",
  review: "Review",
  mastered: "Mastered",
};

/** Stats summary sidebar. */
function StatsPanel({ stats }: { stats: FrameworkStats }) {
  const statuses: NodeStatus[] = ["mastered", "review", "in_progress", "not_started"];
  const total = stats.total_nodes || 1;

  return (
    <div className="space-y-4">
      {/* Overall progress */}
      <div className="bg-white rounded-lg border border-gray-200 p-4">
        <h3 className="text-sm font-semibold text-gray-500 uppercase tracking-wide mb-2">
          Overall Progress
        </h3>
        <div className="text-3xl font-bold text-blue-600 mb-2">
          {Math.round(stats.overall_progress_pct)}%
        </div>
        {/* Stacked bar */}
        <div className="h-3 bg-gray-200 rounded-full overflow-hidden flex">
          {statuses.map((s) => {
            const pct = ((stats.by_status[s] ?? 0) / total) * 100;
            return pct > 0 ? (
              <div
                key={s}
                className={`${STATUS_COLORS[s]} transition-all duration-300`}
                style={{ width: `${pct}%` }}
                title={`${STATUS_LABELS[s]}: ${stats.by_status[s]}`}
              />
            ) : null;
          })}
        </div>
        {/* Status counts */}
        <div className="mt-3 space-y-1">
          {statuses.map((s) => (
            <div key={s} className="flex items-center justify-between text-sm">
              <div className="flex items-center gap-2">
                <div className={`w-2.5 h-2.5 rounded-full ${STATUS_COLORS[s]}`} />
                <span className="text-gray-600">{STATUS_LABELS[s]}</span>
              </div>
              <span className="font-medium text-gray-800">{stats.by_status[s] ?? 0}</span>
            </div>
          ))}
        </div>
      </div>

      {/* Study hours */}
      <div className="bg-white rounded-lg border border-gray-200 p-4">
        <h3 className="text-sm font-semibold text-gray-500 uppercase tracking-wide mb-2">
          Study This Week
        </h3>
        <div className="text-2xl font-bold text-gray-800">
          {stats.study_hours_this_week}h
        </div>
        <p className="text-xs text-gray-400 mt-1">{stats.total_study_logs} total sessions</p>
      </div>

      {/* Weakest nodes */}
      {stats.weakest_nodes.length > 0 && (
        <div className="bg-white rounded-lg border border-gray-200 p-4">
          <h3 className="text-sm font-semibold text-gray-500 uppercase tracking-wide mb-2">
            Needs Attention
          </h3>
          <div className="space-y-2">
            {stats.weakest_nodes.slice(0, 5).map((n) => (
              <div key={n.id} className="flex items-center justify-between">
                <span className="text-sm text-gray-700 truncate" title={n.title}>
                  {n.title}
                </span>
                <span className="text-xs text-red-600 font-medium shrink-0 ml-2">
                  conf: {n.confidence_level}/5
                </span>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Hours by pillar */}
      {stats.study_hours_by_pillar.length > 0 && (
        <div className="bg-white rounded-lg border border-gray-200 p-4">
          <h3 className="text-sm font-semibold text-gray-500 uppercase tracking-wide mb-2">
            Hours by Pillar
          </h3>
          <div className="space-y-2">
            {stats.study_hours_by_pillar.map((p) => (
              <div key={p.title} className="flex items-center justify-between text-sm">
                <span className="text-gray-700 truncate" title={p.title}>{p.title}</span>
                <span className="text-gray-500 font-medium shrink-0 ml-2">{p.hours}h</span>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}

export default function Framework() {
  const queryClient = useQueryClient();
  const { data: tree, isLoading: treeLoading, error: treeError } = useQuery({
    queryKey: ["framework", "tree"],
    queryFn: () => api.get<FrameworkNode[]>("/framework/tree"),
  });
  const { data: stats, isLoading: statsLoading } = useQuery({
    queryKey: ["framework", "stats"],
    queryFn: () => api.get<FrameworkStats>("/framework/stats"),
  });

  const [viewMode, setViewMode] = useState<ViewMode>("tree");
  const [selectedNode, setSelectedNode] = useState<FrameworkNode | null>(null);

  const handleNodeUpdated = useCallback(() => {
    queryClient.invalidateQueries({ queryKey: ["framework"] });
  }, [queryClient]);

  if (treeLoading || statsLoading) {
    return (
      <div className="flex items-center justify-center h-64 text-gray-400">
        Loading framework...
      </div>
    );
  }

  if (treeError) {
    return (
      <div className="bg-red-50 border border-red-200 rounded-lg p-4 text-red-700">
        Failed to load framework: {treeError.message}
      </div>
    );
  }

  if (!tree || tree.length === 0) {
    return (
      <div className="space-y-4">
        <h1 className="text-2xl font-bold text-gray-800">Framework</h1>
        <p className="text-gray-500">
          No framework data yet. Import or seed framework nodes to get started.
        </p>
      </div>
    );
  }

  return (
    <div className="space-y-4">
      {/* Header */}
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold text-gray-800">Framework</h1>
        {/* View toggle */}
        <div className="flex bg-gray-100 rounded-lg p-0.5">
          <button
            className={`px-3 py-1.5 text-sm font-medium rounded-md transition-colors ${
              viewMode === "tree"
                ? "bg-white text-gray-800 shadow-sm"
                : "text-gray-500 hover:text-gray-700"
            }`}
            onClick={() => setViewMode("tree")}
          >
            Tree
          </button>
          <button
            className={`px-3 py-1.5 text-sm font-medium rounded-md transition-colors ${
              viewMode === "treemap"
                ? "bg-white text-gray-800 shadow-sm"
                : "text-gray-500 hover:text-gray-700"
            }`}
            onClick={() => setViewMode("treemap")}
          >
            Treemap
          </button>
        </div>
      </div>

      {/* Main content: sidebar + visualization */}
      <div className="flex gap-4">
        {/* Left: main visualization */}
        <div className="flex-1 min-w-0 bg-white rounded-lg border border-gray-200 p-4">
          {viewMode === "tree" ? (
            <FrameworkTreeView
              nodes={tree}
              onSelect={setSelectedNode}
              selectedId={selectedNode?.id ?? null}
            />
          ) : (
            <FrameworkTreemap
              nodes={tree}
              onSelect={setSelectedNode}
              selectedId={selectedNode?.id ?? null}
            />
          )}
        </div>

        {/* Right: node detail + stats */}
        <div className="w-72 shrink-0 space-y-4 max-h-[calc(100vh-8rem)] overflow-y-auto">
          {selectedNode && (
            <NodeDetailPanel node={selectedNode} onNodeUpdated={handleNodeUpdated} />
          )}
          <StudyPlanCard />
          {stats && <StatsPanel stats={stats} />}
        </div>
      </div>
    </div>
  );
}
