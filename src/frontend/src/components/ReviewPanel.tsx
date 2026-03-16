import { useCallback, useEffect, useRef, useState } from "react";
import { api, ApiRequestError } from "../utils/api";
import type {
  Problem,
  QAChatMessage,
  QAChatResponse,
  QASessionSummary,
  ReviewResult,
  ReviewVerdict,
} from "../types/problem";

type Mode = "review" | "qa";

const VERDICT_COLORS: Record<ReviewVerdict, string> = {
  optimal: "bg-green-100 text-green-800 border-green-300",
  suboptimal: "bg-yellow-100 text-yellow-800 border-yellow-300",
  incorrect: "bg-red-100 text-red-800 border-red-300",
  needs_clarification: "bg-blue-100 text-blue-800 border-blue-300",
};

const VERDICT_LABELS: Record<ReviewVerdict, string> = {
  optimal: "Optimal",
  suboptimal: "Suboptimal",
  incorrect: "Incorrect",
  needs_clarification: "Needs Clarification",
};

interface Props {
  problem: Problem;
  onClose: () => void;
}

function ReviewVerdicBadge({ verdict }: { verdict: ReviewVerdict }) {
  return (
    <span
      className={`inline-block text-xs font-semibold px-2 py-0.5 rounded border ${VERDICT_COLORS[verdict]}`}
    >
      {VERDICT_LABELS[verdict]}
    </span>
  );
}

function ChatBubble({ msg }: { msg: QAChatMessage }) {
  const isUser = msg.role === "user";
  return (
    <div className={`flex ${isUser ? "justify-end" : "justify-start"} mb-3`}>
      <div
        className={`max-w-[85%] px-3 py-2 rounded-lg text-sm whitespace-pre-wrap break-words ${
          isUser
            ? "bg-blue-600 text-white rounded-br-sm"
            : "bg-gray-100 text-gray-800 rounded-bl-sm"
        }`}
      >
        {msg.content}
      </div>
    </div>
  );
}

export default function ReviewPanel({ problem, onClose }: Props) {
  const [mode, setMode] = useState<Mode>("review");

  // --- Review mode state ---
  const [approachText, setApproachText] = useState("");
  const [reviewResult, setReviewResult] = useState<ReviewResult | null>(null);
  const [reviewLoading, setReviewLoading] = useState(false);
  const [reviewError, setReviewError] = useState<string | null>(null);

  // --- QA mode state ---
  const [qaMessage, setQaMessage] = useState("");
  const [qaMessages, setQaMessages] = useState<QAChatMessage[]>([]);
  const [qaSessionId, setQaSessionId] = useState<number | null>(null);
  const [qaLoading, setQaLoading] = useState(false);
  const [qaError, setQaError] = useState<string | null>(null);
  const [pastSessions, setPastSessions] = useState<QASessionSummary[]>([]);
  const [showSessions, setShowSessions] = useState(false);

  const chatEndRef = useRef<HTMLDivElement>(null);

  // Scroll chat to bottom on new messages
  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [qaMessages]);

  // Load past QA sessions for this problem
  useEffect(() => {
    api
      .get<QASessionSummary[]>("/qa/sessions", {
        params: { problem_id: problem.id },
      })
      .then(setPastSessions)
      .catch(() => {
        /* non-critical */
      });
  }, [problem.id]);

  // Close on Escape
  useEffect(() => {
    function handleKey(e: KeyboardEvent) {
      if (e.key === "Escape") onClose();
    }
    window.addEventListener("keydown", handleKey);
    return () => window.removeEventListener("keydown", handleKey);
  }, [onClose]);

  // --- Review mode handlers ---
  const submitReview = useCallback(async () => {
    if (!approachText.trim()) return;
    setReviewLoading(true);
    setReviewError(null);
    setReviewResult(null);
    try {
      const result = await api.post<ReviewResult>(
        `/problems/${problem.id}/review`,
        { approach_text: approachText.trim() },
      );
      setReviewResult(result);
    } catch (err) {
      const msg =
        err instanceof ApiRequestError ? err.message : String(err);
      setReviewError(msg);
    } finally {
      setReviewLoading(false);
    }
  }, [approachText, problem.id]);

  // --- QA mode handlers ---
  const sendQaMessage = useCallback(async () => {
    const text = qaMessage.trim();
    if (!text) return;
    setQaLoading(true);
    setQaError(null);

    // Optimistically add user message
    const userMsg: QAChatMessage = {
      role: "user",
      content: text,
      timestamp: new Date().toISOString(),
    };
    setQaMessages((prev) => [...prev, userMsg]);
    setQaMessage("");

    try {
      const resp = await api.post<QAChatResponse>("/qa/chat", {
        session_id: qaSessionId,
        problem_id: problem.id,
        topic: problem.title,
        message: text,
      });
      setQaSessionId(resp.session_id);
      setQaMessages(resp.messages);
    } catch (err) {
      const msg =
        err instanceof ApiRequestError ? err.message : String(err);
      setQaError(msg);
    } finally {
      setQaLoading(false);
    }
  }, [qaMessage, qaSessionId, problem.id, problem.title]);

  const startNewSession = useCallback(() => {
    setQaSessionId(null);
    setQaMessages([]);
    setQaError(null);
    setShowSessions(false);
  }, []);

  const loadSession = useCallback(
    async (sessionId: number) => {
      // Fetch full session by sending a dummy request? No -- we need to load messages.
      // The QA API doesn't have a GET for session messages, but we can use the sessions list.
      // Actually there's no endpoint for loading a single session's messages.
      // We'll start fresh with a note.
      setQaSessionId(sessionId);
      setQaMessages([]);
      setShowSessions(false);
      // Send a continuation message to load context
      setQaLoading(true);
      try {
        const resp = await api.post<QAChatResponse>("/qa/chat", {
          session_id: sessionId,
          problem_id: problem.id,
          message: "Please continue where we left off. Summarize what we discussed so far.",
        });
        setQaSessionId(resp.session_id);
        setQaMessages(resp.messages);
      } catch (err) {
        const msg =
          err instanceof ApiRequestError ? err.message : String(err);
        setQaError(msg);
      } finally {
        setQaLoading(false);
      }
    },
    [problem.id],
  );

  const handleQaKeyDown = useCallback(
    (e: React.KeyboardEvent) => {
      if (e.key === "Enter" && !e.shiftKey) {
        e.preventDefault();
        sendQaMessage();
      }
    },
    [sendQaMessage],
  );

  return (
    <div className="fixed inset-y-0 right-0 z-40 w-full max-w-lg bg-white shadow-2xl border-l border-gray-200 flex flex-col">
      {/* Header */}
      <div className="px-4 py-3 border-b border-gray-200 shrink-0">
        <div className="flex items-center justify-between mb-2">
          <h2 className="text-lg font-semibold truncate">{problem.title}</h2>
          <button
            onClick={onClose}
            className="text-gray-400 hover:text-gray-600 text-xl leading-none px-2"
            title="Close"
          >
            x
          </button>
        </div>
        <div className="flex items-center gap-2 text-xs text-gray-500 mb-3">
          {problem.leetcode_id && <span>#{problem.leetcode_id}</span>}
          {problem.difficulty && (
            <span className="capitalize">{problem.difficulty}</span>
          )}
          {problem.pattern && <span>| {problem.pattern}</span>}
        </div>

        {/* Mode toggle */}
        <div className="flex rounded-lg border border-gray-300 overflow-hidden">
          <button
            onClick={() => setMode("review")}
            className={`flex-1 text-sm py-1.5 font-medium transition-colors ${
              mode === "review"
                ? "bg-blue-600 text-white"
                : "bg-white text-gray-600 hover:bg-gray-50"
            }`}
          >
            Review (single-shot)
          </button>
          <button
            onClick={() => setMode("qa")}
            className={`flex-1 text-sm py-1.5 font-medium transition-colors ${
              mode === "qa"
                ? "bg-blue-600 text-white"
                : "bg-white text-gray-600 hover:bg-gray-50"
            }`}
          >
            QA (multi-turn)
          </button>
        </div>
      </div>

      {/* Body */}
      <div className="flex-1 overflow-y-auto">
        {mode === "review" ? (
          /* ===== Review Mode ===== */
          <div className="p-4 space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Your Approach
              </label>
              <textarea
                value={approachText}
                onChange={(e) => setApproachText(e.target.value)}
                rows={6}
                placeholder="Describe your approach, algorithm choice, complexity analysis..."
                className="w-full border border-gray-300 rounded px-3 py-2 text-sm resize-y focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              />
            </div>

            <button
              onClick={submitReview}
              disabled={reviewLoading || !approachText.trim()}
              className="w-full px-4 py-2 text-sm bg-blue-600 text-white rounded hover:bg-blue-700 disabled:opacity-50"
            >
              {reviewLoading ? "Reviewing..." : "Get Review"}
            </button>

            {reviewError && (
              <div className="bg-red-50 text-red-700 px-3 py-2 rounded text-sm">
                {reviewError}
              </div>
            )}

            {reviewResult && (
              <div className="space-y-3 border border-gray-200 rounded-lg p-4">
                {/* Verdict */}
                <div className="flex items-center gap-2">
                  <span className="text-sm font-medium text-gray-600">
                    Verdict:
                  </span>
                  <ReviewVerdicBadge verdict={reviewResult.verdict} />
                </div>

                {/* Feedback */}
                <div>
                  <h4 className="text-xs font-semibold text-gray-500 uppercase mb-1">
                    Feedback
                  </h4>
                  <p className="text-sm text-gray-700 whitespace-pre-wrap break-words">
                    {reviewResult.feedback}
                  </p>
                </div>

                {/* Hint */}
                {reviewResult.hint && (
                  <div>
                    <h4 className="text-xs font-semibold text-gray-500 uppercase mb-1">
                      Hint
                    </h4>
                    <p className="text-sm text-gray-600 italic">
                      {reviewResult.hint}
                    </p>
                  </div>
                )}

                {/* Optimal complexity */}
                <div className="flex gap-4">
                  <div>
                    <span className="text-xs font-semibold text-gray-500">
                      Time:
                    </span>{" "}
                    <span className="text-sm font-mono">
                      {reviewResult.optimal_complexity.time}
                    </span>
                  </div>
                  <div>
                    <span className="text-xs font-semibold text-gray-500">
                      Space:
                    </span>{" "}
                    <span className="text-sm font-mono">
                      {reviewResult.optimal_complexity.space}
                    </span>
                  </div>
                </div>

                {/* Pattern */}
                <div>
                  <span className="text-xs font-semibold text-gray-500">
                    Pattern:
                  </span>{" "}
                  <span className="text-sm text-blue-700">
                    {reviewResult.pattern}
                  </span>
                </div>

                {/* Follow-up */}
                {reviewResult.follow_up && (
                  <div className="bg-gray-50 rounded p-3">
                    <h4 className="text-xs font-semibold text-gray-500 uppercase mb-1">
                      Follow-up Question
                    </h4>
                    <p className="text-sm text-gray-700">
                      {reviewResult.follow_up}
                    </p>
                  </div>
                )}
              </div>
            )}
          </div>
        ) : (
          /* ===== QA Mode ===== */
          <div className="flex flex-col h-full">
            {/* Session controls */}
            <div className="px-4 py-2 border-b border-gray-100 flex items-center gap-2 shrink-0">
              <button
                onClick={startNewSession}
                className="text-xs px-2 py-1 bg-gray-100 text-gray-700 rounded hover:bg-gray-200"
              >
                New Session
              </button>
              {pastSessions.length > 0 && (
                <button
                  onClick={() => setShowSessions(!showSessions)}
                  className="text-xs px-2 py-1 bg-gray-100 text-gray-700 rounded hover:bg-gray-200"
                >
                  Past Sessions ({pastSessions.length})
                </button>
              )}
              {qaSessionId && (
                <span className="text-xs text-gray-400 ml-auto">
                  Session #{qaSessionId}
                </span>
              )}
            </div>

            {/* Past sessions dropdown */}
            {showSessions && (
              <div className="px-4 py-2 border-b border-gray-100 bg-gray-50 max-h-40 overflow-y-auto">
                {pastSessions.map((s) => (
                  <button
                    key={s.id}
                    onClick={() => loadSession(s.id)}
                    className="w-full text-left text-xs py-1.5 px-2 hover:bg-gray-100 rounded flex justify-between items-center"
                  >
                    <span className="truncate">
                      {s.topic || `Session #${s.id}`}
                    </span>
                    <span className="text-gray-400 ml-2 shrink-0">
                      {s.created_at
                        ? new Date(s.created_at).toLocaleDateString()
                        : ""}
                    </span>
                  </button>
                ))}
              </div>
            )}

            {/* Messages */}
            <div className="flex-1 overflow-y-auto px-4 py-3">
              {qaMessages.length === 0 && (
                <div className="text-center text-gray-400 text-sm py-8">
                  Ask a question about this problem to start a QA session.
                </div>
              )}
              {qaMessages.map((msg, i) => (
                <ChatBubble key={i} msg={msg} />
              ))}
              {qaLoading && (
                <div className="flex justify-start mb-3">
                  <div className="bg-gray-100 text-gray-500 px-3 py-2 rounded-lg text-sm">
                    Thinking...
                  </div>
                </div>
              )}
              <div ref={chatEndRef} />
            </div>

            {qaError && (
              <div className="mx-4 mb-2 bg-red-50 text-red-700 px-3 py-2 rounded text-sm">
                {qaError}
              </div>
            )}
          </div>
        )}
      </div>

      {/* QA input (only in QA mode) */}
      {mode === "qa" && (
        <div className="px-4 py-3 border-t border-gray-200 shrink-0">
          <div className="flex gap-2">
            <textarea
              value={qaMessage}
              onChange={(e) => setQaMessage(e.target.value)}
              onKeyDown={handleQaKeyDown}
              rows={2}
              placeholder="Ask a question... (Enter to send, Shift+Enter for newline)"
              className="flex-1 border border-gray-300 rounded px-3 py-2 text-sm resize-none focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              disabled={qaLoading}
            />
            <button
              onClick={sendQaMessage}
              disabled={qaLoading || !qaMessage.trim()}
              className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700 disabled:opacity-50 text-sm self-end"
            >
              Send
            </button>
          </div>
        </div>
      )}
    </div>
  );
}
