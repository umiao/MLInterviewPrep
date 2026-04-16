export type CompanyStatus =
  | "applied"
  | "phone_screen"
  | "onsite"
  | "offer"
  | "rejected";

export interface Company {
  id: number;
  name: string;
  group_tag: string | null;
  interview_stages: Record<string, unknown>[];
  status: CompanyStatus;
  applied_at: string | null;
  notes: string | null;
  prep_notes: string | null;
}

export interface CompanyWithWeights extends Company {
  topic_weights: TopicWeight[];
}

export interface TopicWeight {
  node_id: number;
  node_title: string;
  weight: number;
}

export interface FocusTopic {
  node_id: number;
  title: string;
  weight: number;
  progress_pct: number;
  confidence: number;
}

export interface CompanyCreate {
  name: string;
  group_tag?: string | null;
  status?: CompanyStatus;
  applied_at?: string | null;
  notes?: string | null;
  prep_notes?: string | null;
}

export interface CompanyDocument {
  id: number;
  company_id: number;
  title: string;
  content: string;
  source_type: string;
  doc_kind: string;
  created_at: string | null;
  updated_at: string | null;
}

export interface CardIndexProblem {
  id: number;
  leetcode_id: number | null;
  title: string;
  one_liner: string;
}

export interface CardIndexCard {
  name_zh: string;
  name_en: string;
  summary_zh: string;
  problems: CardIndexProblem[];
}

export interface CardIndexContent {
  schema_version: number;
  cards: CardIndexCard[];
}
