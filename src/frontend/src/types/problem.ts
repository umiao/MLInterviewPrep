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
}

export type Difficulty = "easy" | "medium" | "hard";
export type Category = "algorithm" | "ml_coding" | "system_design";
export type SortField =
  | "comfort_level"
  | "last_attempted_at"
  | "next_review_at"
  | "created_at";
export type SortOrder = "asc" | "desc";

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
