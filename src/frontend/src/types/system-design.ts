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
  overview: "概览 (Overview)",
  architecture: "架构 (Architecture)",
  dataflow: "数据流 (Data Flow)",
  formulas: "公式估算 (Formulas)",
  production_constraints: "生产约束 (Production Constraints)",
  tradeoffs: "权衡取舍 (Tradeoffs)",
  defense: "应答策略 (Defense)",
  verbal_outline: "口述脉络 (Verbal Outline)",
  cheat_sheet: "速查表 (Cheat Sheet)",
};
