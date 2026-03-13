export type NodeStatus = "not_started" | "in_progress" | "review" | "mastered";

export interface FrameworkNode {
  id: number;
  path: string;
  depth: number;
  title: string;
  parent_id: number | null;
  status: NodeStatus;
  progress_pct: number;
  confidence_level: number;
  importance: number;
  priority: string;
  estimated_hours: number | null;
  children: FrameworkNode[];
}

export interface StudyLog {
  id: number;
  framework_node_id: number;
  date: string;
  duration_minutes: number;
  activity_type: string | null;
  notes: string | null;
}

export interface StudyTopic {
  node_id: number;
  title: string;
  path: string;
  urgency: number;
  progress_pct: number;
  importance: number;
  confidence: number;
  allocated_minutes: number;
}

export interface StudyPlanResult {
  structured: StudyTopic[];
  plan_text: string | null;
}

export interface FrameworkStats {
  total_nodes: number;
  by_status: Record<NodeStatus, number>;
  overall_progress_pct: number;
  study_hours_this_week: number;
  study_hours_by_pillar: { title: string; hours: number }[];
  weakest_nodes: { id: number; title: string; importance: number; confidence_level: number }[];
  total_study_logs: number;
}
