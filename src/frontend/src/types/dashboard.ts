/** Response shape for GET /api/dashboard */

export interface DashboardProblems {
  total: number;
  completed: number;
  due_for_review: number;
}

export interface PillarProgress {
  title: string;
  progress: number;
}

export interface DashboardFramework {
  overall_progress_pct: number;
  pillars: PillarProgress[];
}

export interface DashboardActivity {
  attempts_7d: number;
  study_hours_7d: number;
  questions_added_7d: number;
}

export interface CompanyDeadline {
  name: string;
  status: string;
}

export interface DashboardScraper {
  total_questions: number;
}

export interface DashboardData {
  problems: DashboardProblems;
  framework: DashboardFramework;
  recent_activity: DashboardActivity;
  company_deadlines: CompanyDeadline[];
  scraper: DashboardScraper;
}
