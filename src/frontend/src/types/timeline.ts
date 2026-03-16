export interface InterviewEvent {
  id: number;
  company_id: number | null;
  company_name: string;
  event_type: string;
  title: string;
  description: string | null;
  scheduled_at: string; // ISO 8601
  duration_minutes: number | null;
  location: string | null;
  status: string;
  created_at: string | null;
}

export type EventType =
  | "hr_call"
  | "phone_screen"
  | "technical"
  | "onsite"
  | "offer_deadline"
  | "behavioral"
  | "system_design"
  | "take_home"
  | "other";

export type EventStatus = "upcoming" | "completed" | "cancelled" | "rescheduled";

export const EVENT_TYPE_LABELS: Record<EventType, string> = {
  hr_call: "HR Call",
  phone_screen: "Phone Screen",
  technical: "Technical",
  onsite: "Onsite",
  offer_deadline: "Offer Deadline",
  behavioral: "Behavioral",
  system_design: "System Design",
  take_home: "Take Home",
  other: "Other",
};
