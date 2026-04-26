export interface LinkedQuestion {
  id: number;
  question_id: string;
  text: string;
  category_id: string;
  relevance_note: string | null;
  is_primary: boolean;
}

export interface ProbeNotes {
  core_signal?: string | null;
  what_good_looks_like?: string[] | null;
  what_L5_adds?: string[] | null;
  common_failure_modes?: string[] | null;
}

export interface BehavioralExample {
  id: number;
  example_id: string;
  title: string;
  source_project: string | null;
  situation: string | null;
  task: string | null;
  action: string | null;
  result: string | null;
  evidence_quotes: string[];
  principle_tags: string[];
  risk_statement: string | null;
  analogy: string | null;
  tech_terms: Record<string, string>;
  cn_elevator_pitch?: string | null;
  is_golden: boolean;
  golden_at: string | null;
  is_signature?: boolean;
  signature_at?: string | null;
  theme_tags?: ThemeTag[];
  facet_tags?: FacetTag[];
  linked_questions: LinkedQuestion[];
}

export interface ThemeTag {
  slug: string;
  label: string;
}

export interface FacetTag {
  slug: string;
  label: string;
}

export interface BehavioralThemeSummary {
  id: number;
  slug: string;
  label: string;
  description: string | null;
  display_order: number;
  question_count: number;
  example_count: number;
}

export type ThemeMode = "or" | "and";
