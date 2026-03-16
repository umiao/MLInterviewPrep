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
