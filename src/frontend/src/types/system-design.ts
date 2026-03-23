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
  created_at: string;
  updated_at: string;
}

export type SystemDesignSection =
  | "overview"
  | "architecture"
  | "dataflow"
  | "formulas"
  | "production_constraints"
  | "tradeoffs"
  | "defense"
  | "verbal_outline";

export const SECTION_LABELS: Record<SystemDesignSection, string> = {
  overview: "Overview & Motivation",
  architecture: "Architecture Deep Dive",
  dataflow: "Data Flow & Key Components",
  formulas: "Formulas & Algorithms",
  production_constraints: "Production Constraints",
  tradeoffs: "Trade-off Analysis",
  defense: "Adversarial Defense Q&A",
  verbal_outline: "Verbal Outline",
};
