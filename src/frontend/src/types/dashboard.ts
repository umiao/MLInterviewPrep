/** Response shapes for dashboard API endpoints. */

/* --- Legacy combined endpoint: GET /api/dashboard --- */

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

/* --- Split endpoint: GET /api/dashboard/today --- */

export interface FocusTopic {
  id: number;
  title: string;
  path: string;
  progress_pct: number;
}

export interface DashboardToday {
  suggested_focus_topic: FocusTopic | null;
  streak_days: number;
}

/* --- Split endpoint: GET /api/dashboard/activity --- */

export interface ActivityDay {
  date: string;
  attempts: number;
  study_minutes: number;
  questions_added: number;
}

/** GET /api/dashboard/activity returns ActivityDay[] */

/* --- Split endpoint: GET /api/dashboard/summary --- */

export interface DashboardSummary {
  problems: {
    total: number;
    completed: number;
  };
  framework_overall_progress_pct: number;
  company_counts_by_status: Record<string, number>;
}
