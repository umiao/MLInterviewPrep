import { useQuery } from "@tanstack/react-query";
import { api } from "../../utils/api";
import type { InterviewEvent } from "../../types/timeline";
import { EVENT_TYPE_LABELS } from "../../types/timeline";
import type { EventType } from "../../types/timeline";
import Skeleton from "../ui/Skeleton";

/** Color of the left border based on urgency. */
function urgencyColor(scheduledAt: string, isPast: boolean): string {
  if (isPast) return "border-l-gray-300";
  const now = new Date();
  const d = new Date(scheduledAt);
  const diffMs = d.getTime() - now.getTime();
  const diffDays = diffMs / (1000 * 60 * 60 * 24);
  if (diffDays < 1) return "border-l-red-500";
  if (diffDays < 2) return "border-l-red-400";
  if (diffDays < 7) return "border-l-amber-400";
  return "border-l-blue-400";
}

/** Human-friendly countdown text. */
function countdown(scheduledAt: string): string {
  const now = new Date();
  const d = new Date(scheduledAt);
  const diffMs = d.getTime() - now.getTime();
  if (diffMs < 0) return "Past";
  const diffMins = Math.floor(diffMs / 60000);
  if (diffMins < 60) return `in ${diffMins}m`;
  const diffHours = Math.floor(diffMins / 60);
  if (diffHours < 24) return `in ${diffHours}h`;
  const diffDays = Math.floor(diffHours / 24);
  if (diffDays === 1) return "Tomorrow";
  return `in ${diffDays} days`;
}

function formatDateTime(iso: string): string {
  const d = new Date(iso);
  return d.toLocaleDateString(undefined, {
    weekday: "short",
    month: "short",
    day: "numeric",
  }) + " " + d.toLocaleTimeString(undefined, {
    hour: "2-digit",
    minute: "2-digit",
  });
}

const TYPE_BADGE_COLORS: Record<string, string> = {
  hr_call: "bg-green-100 text-green-700",
  phone_screen: "bg-blue-100 text-blue-700",
  technical: "bg-purple-100 text-purple-700",
  onsite: "bg-indigo-100 text-indigo-700",
  offer_deadline: "bg-red-100 text-red-700",
  behavioral: "bg-yellow-100 text-yellow-800",
  system_design: "bg-cyan-100 text-cyan-700",
  take_home: "bg-orange-100 text-orange-700",
  other: "bg-gray-100 text-gray-700",
};

interface Props {
  onAddClick: () => void;
  onEditClick: (event: InterviewEvent) => void;
}

export default function InterviewTimeline({ onAddClick, onEditClick }: Props) {
  const { data, isLoading, error } = useQuery<InterviewEvent[]>({
    queryKey: ["timeline", "events"],
    queryFn: () => api.get<InterviewEvent[]>("/timeline/events"),
  });

  if (isLoading) {
    return (
      <div className="bg-white rounded-lg border border-gray-200 p-6 space-y-3">
        <Skeleton className="h-4 w-40" />
        <Skeleton className="h-16 w-full" />
        <Skeleton className="h-16 w-full" />
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-red-50 border border-red-200 rounded-lg p-4 text-red-700 text-sm">
        Failed to load interview timeline.
      </div>
    );
  }

  const events = data ?? [];
  const now = new Date();
  const upcoming = events
    .filter((e) => new Date(e.scheduled_at) >= now && e.status !== "cancelled")
    .sort((a, b) => new Date(a.scheduled_at).getTime() - new Date(b.scheduled_at).getTime());
  const past = events
    .filter((e) => new Date(e.scheduled_at) < now || e.status === "cancelled")
    .sort((a, b) => new Date(b.scheduled_at).getTime() - new Date(a.scheduled_at).getTime());

  return (
    <div className="bg-white rounded-lg border border-gray-200 p-6">
      <div className="flex items-center justify-between mb-4">
        <h2 className="text-sm font-semibold text-gray-500 uppercase tracking-wide">
          Interview Timeline
        </h2>
        <button
          type="button"
          onClick={onAddClick}
          className="text-sm text-blue-600 hover:text-blue-800 font-medium"
        >
          + Add Event
        </button>
      </div>

      {events.length === 0 ? (
        <p className="text-sm text-gray-400 py-8 text-center">
          No interview events yet. Click "+ Add Event" to track your first interview.
        </p>
      ) : (
        <div className="space-y-4">
          {/* Upcoming */}
          {upcoming.length > 0 && (
            <div className="space-y-2">
              <p className="text-xs font-medium text-gray-400 uppercase">Upcoming</p>
              {upcoming.map((e) => (
                <EventCard key={e.id} event={e} isPast={false} onClick={() => onEditClick(e)} />
              ))}
            </div>
          )}

          {/* Past */}
          {past.length > 0 && (
            <div className="space-y-2">
              <p className="text-xs font-medium text-gray-400 uppercase">Past</p>
              {past.slice(0, 5).map((e) => (
                <EventCard key={e.id} event={e} isPast onClick={() => onEditClick(e)} />
              ))}
            </div>
          )}
        </div>
      )}
    </div>
  );
}

function EventCard({
  event,
  isPast,
  onClick,
}: {
  event: InterviewEvent;
  isPast: boolean;
  onClick: () => void;
}) {
  const badgeColor = TYPE_BADGE_COLORS[event.event_type] ?? TYPE_BADGE_COLORS.other;
  const label = EVENT_TYPE_LABELS[event.event_type as EventType] ?? event.event_type;

  return (
    <button
      type="button"
      onClick={onClick}
      className={`w-full text-left border-l-4 rounded-r-lg px-4 py-3 bg-gray-50 hover:bg-gray-100 transition-colors ${
        urgencyColor(event.scheduled_at, isPast)
      } ${isPast ? "opacity-60" : ""}`}
    >
      <div className="flex items-center gap-2 mb-1">
        <span className={`text-xs px-2 py-0.5 rounded-full font-medium ${badgeColor}`}>
          {label}
        </span>
        <span className="font-semibold text-sm text-gray-800">{event.company_name}</span>
        {!isPast && (
          <span className="ml-auto text-xs text-gray-500">{countdown(event.scheduled_at)}</span>
        )}
      </div>
      <div className="flex items-center gap-2 text-xs text-gray-500">
        <span>{event.title}</span>
        <span>--</span>
        <span>{formatDateTime(event.scheduled_at)}</span>
        {event.duration_minutes && <span>({event.duration_minutes}min)</span>}
      </div>
    </button>
  );
}
