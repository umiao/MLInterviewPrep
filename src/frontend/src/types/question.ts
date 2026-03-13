export type QuestionType =
  | "coding"
  | "ml_theory"
  | "ml_system_design"
  | "behavioral"
  | "ml_coding"
  | "general_system_design";

export interface InterviewQuestion {
  id: number;
  scraped_page_id: number | null;
  company: string | null;
  role: string | null;
  level: string | null;
  interview_round: string | null;
  year: number | null;
  question_text: string;
  question_type: QuestionType | null;
  tags: string[];
  mapped_framework_node_id: number | null;
  is_reviewed: boolean;
  notes: string | null;
  difficulty_estimate: string | null;
  created_at: string | null;
}

export interface QuestionAnalysis {
  solution_approach: string;
  key_concepts: string[];
  difficulty: string;
  related_patterns: string[];
  suggested_study: string;
}
