export interface LinkedQuestion {
  id: number;
  question_id: string;
  text: string;
  category_id: string;
  relevance_note: string | null;
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
  linked_questions: LinkedQuestion[];
}
