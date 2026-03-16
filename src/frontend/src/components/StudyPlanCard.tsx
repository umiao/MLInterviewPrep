import { useCallback, useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { api } from "../utils/api";
import LoadingSpinner from "./ui/LoadingSpinner";
import type { StudyPlanResult, StudyTopic } from "../types/framework";
import type { Company } from "../types/company";

interface StudyPlanParams {
  hours: number;
  days: number;
  companyId: string;
  useLlm: boolean;
}

const DEFAULT_PARAMS: StudyPlanParams = {
  hours: 3,
  days: 14,
  companyId: "",
  useLlm: false,
};

/** Urgency bar color based on value (0-1 range roughly). */
function urgencyColor(urgency: number): string {
  if (urgency >= 0.6) return "bg-red-500";
  if (urgency >= 0.3) return "bg-yellow-500";
  return "bg-green-500";
}

function TopicRow({ topic }: { topic: StudyTopic }) {
  return (
    <div className="flex items-center gap-3 py-1.5">
      {/* Urgency bar */}
      <div className="w-16 h-2 bg-gray-200 rounded-full overflow-hidden shrink-0">
        <div
          className={`h-full rounded-full ${urgencyColor(topic.urgency)}`}
          style={{ width: `${Math.min(topic.urgency * 100, 100)}%` }}
        />
      </div>
      {/* Title + path */}
      <div className="flex-1 min-w-0">
        <span className="text-sm text-gray-800 truncate block" title={topic.path}>
          {topic.title}
        </span>
      </div>
      {/* Allocated time */}
      <span className="text-xs text-gray-500 shrink-0">
        {topic.allocated_minutes}m
      </span>
      {/* Progress */}
      <span className="text-xs text-gray-400 shrink-0 w-10 text-right">
        {Math.round(topic.progress_pct)}%
      </span>
    </div>
  );
}

export default function StudyPlanCard() {
  const [params, setParams] = useState<StudyPlanParams>(DEFAULT_PARAMS);
  const [plan, setPlan] = useState<StudyPlanResult | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [showSettings, setShowSettings] = useState(false);

  const { data: companies } = useQuery({
    queryKey: ["companies"],
    queryFn: () => api.get<Company[]>("/companies"),
  });

  const fetchPlan = useCallback(async (p: StudyPlanParams) => {
    setLoading(true);
    setError(null);
    try {
      const queryParams: Record<string, string | number | boolean> = {
        hours: p.hours,
        days: p.days,
        use_llm: p.useLlm,
      };
      if (p.companyId) {
        queryParams.company_ids = p.companyId;
      }
      const result = await api.get<StudyPlanResult>("/framework/suggest", {
        params: queryParams,
      });
      setPlan(result);
    } catch (err) {
      setError(err instanceof Error ? err.message : String(err));
    } finally {
      setLoading(false);
    }
  }, []);

  const handleGenerate = useCallback(() => {
    fetchPlan(params);
  }, [fetchPlan, params]);

  const handleRegenerate = useCallback(() => {
    fetchPlan(params);
  }, [fetchPlan, params]);

  return (
    <div className="bg-white rounded-lg border border-gray-200 p-4">
      <div className="flex items-center justify-between mb-3">
        <h3 className="text-sm font-semibold text-gray-500 uppercase tracking-wide">
          AI Study Plan
        </h3>
        <button
          onClick={() => setShowSettings((s) => !s)}
          className="text-xs text-gray-400 hover:text-gray-600"
          title="Settings"
        >
          {showSettings ? "Hide" : "Settings"}
        </button>
      </div>

      {/* Settings panel */}
      {showSettings && (
        <div className="space-y-2 mb-3 p-3 bg-gray-50 rounded-md">
          <div className="flex items-center gap-2">
            <label className="text-xs text-gray-600 w-20">Hours:</label>
            <input
              type="number"
              min={0.5}
              step={0.5}
              value={params.hours}
              onChange={(e) =>
                setParams((p) => ({ ...p, hours: parseFloat(e.target.value) || 0.5 }))
              }
              className="w-20 text-sm border border-gray-300 rounded px-2 py-1"
            />
          </div>
          <div className="flex items-center gap-2">
            <label className="text-xs text-gray-600 w-20">Days:</label>
            <input
              type="number"
              min={1}
              value={params.days}
              onChange={(e) =>
                setParams((p) => ({ ...p, days: parseInt(e.target.value, 10) || 1 }))
              }
              className="w-20 text-sm border border-gray-300 rounded px-2 py-1"
            />
          </div>
          <div className="flex items-center gap-2">
            <label className="text-xs text-gray-600 w-20">Company:</label>
            <select
              value={params.companyId}
              onChange={(e) => setParams((p) => ({ ...p, companyId: e.target.value }))}
              className="flex-1 text-sm border border-gray-300 rounded px-2 py-1"
            >
              <option value="">All topics</option>
              {companies?.map((c) => (
                <option key={c.id} value={String(c.id)}>
                  {c.name}
                </option>
              ))}
            </select>
          </div>
          <div className="flex items-center gap-2">
            <label className="text-xs text-gray-600 w-20">LLM Plan:</label>
            <button
              onClick={() => setParams((p) => ({ ...p, useLlm: !p.useLlm }))}
              className={`relative inline-flex h-5 w-9 items-center rounded-full transition-colors ${
                params.useLlm ? "bg-blue-600" : "bg-gray-300"
              }`}
            >
              <span
                className={`inline-block h-3.5 w-3.5 rounded-full bg-white transition-transform ${
                  params.useLlm ? "translate-x-4.5" : "translate-x-0.5"
                }`}
              />
            </button>
          </div>
        </div>
      )}

      {/* Generate / Regenerate button */}
      {!plan && !loading && (
        <button
          onClick={handleGenerate}
          className="w-full py-2 text-sm font-medium text-white bg-blue-600 hover:bg-blue-700 rounded-md transition-colors"
        >
          Generate Plan
        </button>
      )}

      {/* Loading state */}
      {loading && <LoadingSpinner message="Generating study plan..." size="sm" />}

      {/* Error state */}
      {error && (
        <div className="text-sm text-red-600 bg-red-50 rounded p-2 mb-2">
          {error}
        </div>
      )}

      {/* Results */}
      {plan && !loading && (
        <div className="space-y-3">
          {/* Topic list */}
          {plan.structured.length > 0 ? (
            <div className="divide-y divide-gray-100 max-h-64 overflow-y-auto">
              {plan.structured.map((topic) => (
                <TopicRow key={topic.node_id} topic={topic} />
              ))}
            </div>
          ) : (
            <p className="text-sm text-gray-400 py-2">
              No topics to study -- everything is mastered!
            </p>
          )}

          {/* LLM plan text */}
          {plan.plan_text && (
            <div className="mt-3 p-3 bg-blue-50 rounded-md">
              <h4 className="text-xs font-semibold text-blue-700 uppercase mb-1">
                AI Recommendation
              </h4>
              <p className="text-sm text-gray-700 whitespace-pre-wrap">
                {plan.plan_text}
              </p>
            </div>
          )}

          {/* Regenerate */}
          <button
            onClick={handleRegenerate}
            className="w-full py-1.5 text-xs font-medium text-blue-600 border border-blue-300 hover:bg-blue-50 rounded-md transition-colors"
          >
            Regenerate
          </button>
        </div>
      )}
    </div>
  );
}
