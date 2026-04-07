import { useState, useEffect } from "react";
import { useMutation, useQueryClient } from "@tanstack/react-query";
import Modal from "../ui/Modal";
import { api } from "../../utils/api";
import type { InterviewEvent, EventType, EventStatus } from "../../types/timeline";
import { EVENT_TYPE_LABELS } from "../../types/timeline";

const EVENT_TYPES: EventType[] = [
  "hr_call", "phone_screen", "technical", "onsite",
  "offer_deadline", "behavioral", "system_design", "take_home", "other",
];

const EVENT_STATUSES: EventStatus[] = [
  "upcoming", "completed", "cancelled", "rescheduled",
];

interface Props {
  open: boolean;
  onClose: () => void;
  /** If provided, we're in edit mode. */
  event?: InterviewEvent | null;
}

/** Convert an ISO datetime string to local datetime-local input value. */
function toDatetimeLocal(iso: string): string {
  const d = new Date(iso);
  const pad = (n: number) => String(n).padStart(2, "0");
  return `${d.getFullYear()}-${pad(d.getMonth() + 1)}-${pad(d.getDate())}T${pad(d.getHours())}:${pad(d.getMinutes())}`;
}

export default function EventFormModal({ open, onClose, event }: Props) {
  const qc = useQueryClient();
  const isEdit = !!event;

  const [companyName, setCompanyName] = useState("");
  const [eventType, setEventType] = useState<EventType>("technical");
  const [title, setTitle] = useState("");
  const [scheduledAt, setScheduledAt] = useState("");
  const [durationMinutes, setDurationMinutes] = useState("");
  const [location, setLocation] = useState("");
  const [description, setDescription] = useState("");
  const [status, setStatus] = useState<EventStatus>("upcoming");

  useEffect(() => {
    if (event) {
      setCompanyName(event.company_name);
      setEventType(event.event_type as EventType);
      setTitle(event.title);
      setScheduledAt(toDatetimeLocal(event.scheduled_at));
      setDurationMinutes(event.duration_minutes?.toString() ?? "");
      setLocation(event.location ?? "");
      setDescription(event.description ?? "");
      setStatus(event.status as EventStatus);
    } else {
      setCompanyName("");
      setEventType("technical");
      setTitle("");
      setScheduledAt("");
      setDurationMinutes("");
      setLocation("");
      setDescription("");
      setStatus("upcoming");
    }
  }, [event, open]);

  const createMutation = useMutation({
    mutationFn: (body: Record<string, unknown>) =>
      api.post("/timeline/events", body),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["timeline", "events"] });
      qc.invalidateQueries({ queryKey: ["companies"] });
      onClose();
    },
  });

  const updateMutation = useMutation({
    mutationFn: (body: Record<string, unknown>) =>
      api.put(`/timeline/events/${event?.id}`, body),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["timeline", "events"] });
      qc.invalidateQueries({ queryKey: ["companies"] });
      onClose();
    },
  });

  const deleteMutation = useMutation({
    mutationFn: () => api.del(`/timeline/events/${event?.id}`),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["timeline", "events"] });
      qc.invalidateQueries({ queryKey: ["companies"] });
      onClose();
    },
  });

  const isSubmitting = createMutation.isPending || updateMutation.isPending;

  function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    const body: Record<string, unknown> = {
      company_name: companyName,
      event_type: eventType,
      title,
      scheduled_at: scheduledAt,
      status,
    };
    if (durationMinutes) body.duration_minutes = parseInt(durationMinutes, 10);
    if (location) body.location = location;
    if (description) body.description = description;

    if (isEdit) {
      updateMutation.mutate(body);
    } else {
      createMutation.mutate(body);
    }
  }

  const inputClass = "w-full border border-gray-300 rounded-md px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent";
  const labelClass = "block text-sm font-medium text-gray-700 mb-1";

  return (
    <Modal
      open={open}
      onClose={onClose}
      title={isEdit ? "Edit Event" : "Add Interview Event"}
      width="max-w-lg"
    >
      <form onSubmit={handleSubmit} className="space-y-4">
        {/* Company Name */}
        <div>
          <label className={labelClass}>Company Name *</label>
          <input
            type="text"
            required
            value={companyName}
            onChange={(e) => setCompanyName(e.target.value)}
            className={inputClass}
            placeholder="e.g. LinkedIn"
          />
        </div>

        {/* Event Type + Status */}
        <div className="grid grid-cols-2 gap-3">
          <div>
            <label className={labelClass}>Event Type *</label>
            <select
              value={eventType}
              onChange={(e) => setEventType(e.target.value as EventType)}
              className={inputClass}
            >
              {EVENT_TYPES.map((t) => (
                <option key={t} value={t}>{EVENT_TYPE_LABELS[t]}</option>
              ))}
            </select>
          </div>
          <div>
            <label className={labelClass}>Status</label>
            <select
              value={status}
              onChange={(e) => setStatus(e.target.value as EventStatus)}
              className={inputClass}
            >
              {EVENT_STATUSES.map((s) => (
                <option key={s} value={s}>{s.charAt(0).toUpperCase() + s.slice(1)}</option>
              ))}
            </select>
          </div>
        </div>

        {/* Title */}
        <div>
          <label className={labelClass}>Title *</label>
          <input
            type="text"
            required
            value={title}
            onChange={(e) => setTitle(e.target.value)}
            className={inputClass}
            placeholder="e.g. MLE Phone Screen"
          />
        </div>

        {/* Scheduled At + Duration */}
        <div className="grid grid-cols-2 gap-3">
          <div>
            <label className={labelClass}>Scheduled At *</label>
            <input
              type="datetime-local"
              required
              value={scheduledAt}
              onChange={(e) => setScheduledAt(e.target.value)}
              className={inputClass}
            />
          </div>
          <div>
            <label className={labelClass}>Duration (min)</label>
            <input
              type="number"
              min="1"
              value={durationMinutes}
              onChange={(e) => setDurationMinutes(e.target.value)}
              className={inputClass}
              placeholder="45"
            />
          </div>
        </div>

        {/* Location */}
        <div>
          <label className={labelClass}>Location / Link</label>
          <input
            type="text"
            value={location}
            onChange={(e) => setLocation(e.target.value)}
            className={inputClass}
            placeholder="Zoom URL or office address"
          />
        </div>

        {/* Description */}
        <div>
          <label className={labelClass}>Notes</label>
          <textarea
            value={description}
            onChange={(e) => setDescription(e.target.value)}
            className={inputClass}
            rows={2}
            placeholder="Preparation notes..."
          />
        </div>

        {/* Actions */}
        <div className="flex items-center justify-between pt-2">
          {isEdit ? (
            <button
              type="button"
              onClick={() => deleteMutation.mutate()}
              className="text-sm text-red-600 hover:text-red-800"
              disabled={deleteMutation.isPending}
            >
              Delete
            </button>
          ) : (
            <div />
          )}
          <div className="flex gap-2">
            <button
              type="button"
              onClick={onClose}
              className="px-4 py-2 text-sm text-gray-600 hover:text-gray-800"
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={isSubmitting}
              className="px-4 py-2 text-sm font-medium text-white bg-blue-600 rounded-md hover:bg-blue-700 disabled:opacity-50"
            >
              {isSubmitting ? "Saving..." : isEdit ? "Update" : "Create"}
            </button>
          </div>
        </div>

        {(createMutation.error || updateMutation.error) && (
          <p className="text-sm text-red-600">
            {String(createMutation.error?.message || updateMutation.error?.message)}
          </p>
        )}
      </form>
    </Modal>
  );
}
