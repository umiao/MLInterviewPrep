export interface Problem {
  id: number;
  leetcode_id: number | null;
  title: string;
  url: string | null;
  difficulty: "easy" | "medium" | "hard" | null;
  tags: string[];
  pattern: string | null;
  category: "algorithm" | "ml_coding" | "system_design";
  source: string | null;
  company_tags: string[];
  priority: number;
  is_completed: boolean;
  comfort_level: number;
  created_at: string;
  last_attempted_at: string | null;
  next_review_at: string | null;
  framework_node_id: number | null;
  description: string | null;
  neetcode_slug: string | null;
  description_source: string | null;
  notes: string | null;
}

export type Difficulty = "easy" | "medium" | "hard";
export type Category = "algorithm" | "ml_coding" | "system_design";
export type SortField =
  | "comfort_level"
  | "last_attempted_at"
  | "next_review_at"
  | "created_at"
  | "difficulty";
export type SortOrder = "asc" | "desc";

export type AttemptResult = "solved" | "hint" | "failed" | "timeout";

export interface AttemptCreate {
  duration_seconds: number | null;
  result: AttemptResult;
  approach_notes: string | null;
  complexity_time: string | null;
  complexity_space: string | null;
  comfort_after: number;
}

export interface Attempt {
  id: number;
  problem_id: number;
  started_at: string | null;
  duration_seconds: number | null;
  result: string | null;
  approach_notes: string | null;
  complexity_time: string | null;
  complexity_space: string | null;
  llm_review: string | null;
  comfort_after: number | null;
}

export interface ProblemFilters {
  difficulty?: Difficulty;
  pattern?: string;
  source?: string;
  company?: string;
  is_completed?: boolean;
  category?: Category;
  sort_by: SortField;
  sort_order: SortOrder;
  limit: number;
  offset: number;
}

// --- Stats types ---

export interface PatternStat {
  pattern: string;
  count: number;
  completed: number;
  avg_comfort: number;
}

export interface ProblemStats {
  total: number;
  completed: number;
  avg_comfort: number;
  by_difficulty: Record<string, number>;
  by_pattern: PatternStat[];
  weak_patterns: string[];
  total_attempts: number;
  avg_duration_seconds: number;
}

// --- Review types ---

export type ReviewVerdict =
  | "optimal"
  | "suboptimal"
  | "incorrect"
  | "needs_clarification";

export interface ReviewResult {
  verdict: ReviewVerdict;
  feedback: string;
  hint: string | null;
  optimal_complexity: { time: string; space: string };
  pattern: string;
  follow_up: string;
}

// --- QA types ---

export interface QAChatMessage {
  role: "user" | "assistant";
  content: string;
  timestamp: string;
}

export interface QAChatResponse {
  session_id: number;
  reply: string;
  messages: QAChatMessage[];
}

export interface QASessionSummary {
  id: number;
  problem_id: number | null;
  topic: string | null;
  created_at: string | null;
  summary: string | null;
}
