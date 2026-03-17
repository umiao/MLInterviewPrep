/** Types for the Reading/TTS audio system. */

export type ContentType = "framework_node" | "prep_notes" | "interview_question";

export interface QueueItem {
  content_type: ContentType;
  content_id: number;
  title: string;
  urgency: number;
  total_chars: number;
  last_chunk_index: number;
  char_offset: number;
  completed: boolean;
}

export interface QueueResponse {
  items: QueueItem[];
  total: number;
}

export interface SynthesizeRequest {
  content_type: ContentType;
  content_id: number;
  voice?: string;
  rate?: string;
  engine?: string;
}

export interface SynthesizeResponse {
  mode: "file" | "browser";
  audio_url: string | null;
  text: string | null;
  cache_hit: boolean;
  content_length: number;
}

export interface SynthesizeAsyncResponse {
  job_id: string;
  status: string;
  content_length: number;
}

export interface ProgressUpdate {
  last_chunk_index: number;
  char_offset: number;
  total_chars: number;
  completed: boolean;
}

export interface AudioPlayerItem {
  content_type: ContentType;
  content_id: number;
  title: string;
}

export type PlayerStatus = "idle" | "loading" | "playing" | "paused";

export interface ListeningStats {
  total_sessions: number;
  total_listening_seconds: number;
  total_items_listened: number;
  sessions_today: number;
  listening_seconds_today: number;
  streak_days: number;
}

export interface TranscriptResponse {
  content_type: ContentType;
  content_id: number;
  transcript_text: string;
  transcript_hash: string;
  generation_method: "llm" | "preprocess_fallback";
  from_cache: boolean;
  total_chars: number;
}
