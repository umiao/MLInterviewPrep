export interface SystemDesignSummary {
  id: number;
  slug: string;
  title: string;
  subtitle: string | null;
  diagram_filename: string | null;
  display_order: number;
}

export interface SystemDesign extends SystemDesignSummary {
  overview: string | null;
  architecture: string | null;
  dataflow: string | null;
  formulas: string | null;
  production_constraints: string | null;
  tradeoffs: string | null;
  defense: string | null;
  verbal_outline: string | null;
  cheat_sheet: string | null;
  created_at: string;
  updated_at: string;
}

export interface SystemDesignCheatSheet extends SystemDesignSummary {
  cheat_sheet: string | null;
}

export type SystemDesignSection =
  | "overview"
  | "architecture"
  | "dataflow"
  | "formulas"
  | "production_constraints"
  | "tradeoffs"
  | "defense"
  | "verbal_outline"
  | "cheat_sheet";

export const SECTION_LABELS: Record<SystemDesignSection, string> = {
  overview: "Overview & Motivation",
  architecture: "Architecture Deep Dive",
  dataflow: "Data Flow & Key Components",
  formulas: "Formulas & Algorithms",
  production_constraints: "Production Constraints",
  tradeoffs: "Trade-off Analysis",
  defense: "Adversarial Defense Q&A",
  verbal_outline: "Verbal Outline",
  cheat_sheet: "Cheat Sheet",
};
