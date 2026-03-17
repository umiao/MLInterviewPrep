/**
 * TranscriptViewer -- displays a faithful spoken-word transcript for a content item.
 * Fetches from GET /reading/transcript/{content_type}/{content_id}.
 * Shows a "Listen" button at the bottom if user wants audio.
 */
import { useQuery } from "@tanstack/react-query";
import { api } from "../../utils/api";
import type { ContentType, TranscriptResponse } from "../../types/reading";

interface TranscriptViewerProps {
  contentType: ContentType;
  contentId: number;
  title: string;
  onClose: () => void;
  onListen?: () => void;
}

export default function TranscriptViewer({
  contentType,
  contentId,
  title,
  onClose,
  onListen,
}: TranscriptViewerProps) {
  const { data, isLoading, error } = useQuery<TranscriptResponse>({
    queryKey: ["transcript", contentType, contentId],
    queryFn: () =>
      api.get<TranscriptResponse>(
        `/reading/transcript/${contentType}/${contentId}`,
      ),
  });

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/40">
      <div className="bg-white rounded-lg shadow-xl w-full max-w-2xl max-h-[80vh] flex flex-col mx-4">
        {/* Header */}
        <div className="flex items-center justify-between px-5 py-4 border-b border-gray-200">
          <div className="min-w-0 flex-1">
            <h2 className="text-lg font-semibold text-gray-900 truncate">
              {title}
            </h2>
            {data && data.generation_method === "preprocess_fallback" && (
              <span className="text-xs text-amber-600">
                Fallback text (LLM unavailable)
              </span>
            )}
          </div>
          <button
            onClick={onClose}
            className="ml-4 text-gray-400 hover:text-gray-600 text-xl leading-none"
            title="Close"
          >
            x
          </button>
        </div>

        {/* Body */}
        <div className="flex-1 overflow-y-auto px-5 py-4">
          {isLoading && (
            <div className="text-center text-gray-400 py-8">
              Generating transcript...
            </div>
          )}

          {error && (
            <div className="bg-red-50 text-red-700 px-4 py-3 rounded text-sm">
              {(error as Error).message || "Failed to load transcript"}
            </div>
          )}

          {data && (
            <div className="prose prose-sm max-w-none text-gray-700 whitespace-pre-wrap leading-relaxed">
              {data.transcript_text}
            </div>
          )}
        </div>

        {/* Footer */}
        <div className="flex items-center justify-between px-5 py-3 border-t border-gray-200">
          <div className="text-xs text-gray-400">
            {data && `${data.total_chars.toLocaleString()} chars`}
          </div>
          <div className="flex gap-2">
            <button
              onClick={onClose}
              className="px-3 py-1.5 text-sm border border-gray-300 rounded hover:bg-gray-100 text-gray-600"
            >
              Close
            </button>
            {onListen && (
              <button
                onClick={() => {
                  onListen();
                  onClose();
                }}
                className="px-3 py-1.5 text-sm bg-green-600 text-white rounded hover:bg-green-700"
              >
                Listen
              </button>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
