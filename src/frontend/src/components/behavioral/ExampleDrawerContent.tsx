import type { BehavioralExample } from "../../types/behavioral";
import MarkdownPreview from "../ui/MarkdownPreview";

const STAR_COLORS: Record<string, { label: string; border: string }> = {
  Situation: { label: "text-blue-700", border: "border-blue-300" },
  Task: { label: "text-amber-700", border: "border-amber-300" },
  Action: { label: "text-emerald-700", border: "border-emerald-300" },
  Result: { label: "text-purple-700", border: "border-purple-300" },
};

function StarSection({ label, content }: { label: string; content: string | null }) {
  if (!content) return null;
  const colors = STAR_COLORS[label] ?? { label: "text-blue-700", border: "border-blue-300" };
  return (
    <div className="mb-4">
      <span className={`font-bold ${colors.label} text-sm uppercase tracking-wider`}>
        {label}
      </span>
      <div className="mt-1 text-[15px] leading-relaxed text-gray-800">
        <MarkdownPreview markdown={content} />
      </div>
    </div>
  );
}

export default function ExampleDrawerContent({ example }: { example: BehavioralExample }) {
  return (
    <div>
      <div className="mb-5">
        <div className="flex items-center gap-3 mb-1">
          <span className="text-sm font-mono font-bold text-blue-500 bg-blue-50 px-2 py-0.5 rounded">
            {example.example_id}
          </span>
          <h3 className="text-xl font-bold text-gray-900">{example.title}</h3>
        </div>
        {example.source_project && (
          <p className="text-sm text-gray-500 mt-1">
            Source: <span className="font-medium text-gray-700">{example.source_project}</span>
          </p>
        )}
      </div>

      <StarSection label="Situation" content={example.situation} />
      <StarSection label="Task" content={example.task} />
      <StarSection label="Action" content={example.action} />
      <StarSection label="Result" content={example.result} />

      {example.risk_statement && (
        <div className="mb-4 bg-red-50 rounded-lg p-3 border border-red-200">
          <span className="font-bold text-red-700 text-sm uppercase tracking-wider">
            Risk if not addressed
          </span>
          <div className="text-red-900 text-[15px] mt-1 leading-relaxed">
            <MarkdownPreview markdown={example.risk_statement} />
          </div>
        </div>
      )}

      {example.analogy && (
        <div className="mb-4 bg-purple-50 rounded-lg p-3 border border-purple-200">
          <span className="font-bold text-purple-700 text-sm uppercase tracking-wider">
            Simple Analogy
          </span>
          <div className="text-purple-900 text-[15px] mt-1 italic leading-relaxed">
            <MarkdownPreview markdown={example.analogy} />
          </div>
        </div>
      )}

      {Object.keys(example.tech_terms).length > 0 && (
        <div className="mb-4 bg-teal-50 rounded-lg p-3 border border-teal-200">
          <span className="font-bold text-teal-800 text-sm uppercase tracking-wider">
            Technical Terms
          </span>
          <dl className="mt-2 space-y-1">
            {Object.entries(example.tech_terms).map(([term, def_]) => (
              <div key={term} className="text-[15px]">
                <dt className="inline font-bold text-teal-900">{term}</dt>
                <dd className="inline text-gray-800"> -- {def_}</dd>
              </div>
            ))}
          </dl>
        </div>
      )}

      {example.evidence_quotes.length > 0 && (
        <div className="mb-4">
          <span className="font-bold text-amber-800 text-sm uppercase tracking-wider">
            Evidence
          </span>
          {example.evidence_quotes.map((q, i) => (
            <blockquote
              key={i}
              className="text-gray-700 text-sm italic border-l-3 border-amber-400 pl-3 mt-2 leading-relaxed"
              style={{ borderLeftWidth: "3px" }}
            >
              {q}
            </blockquote>
          ))}
        </div>
      )}

      {example.linked_questions.length > 0 && (
        <div className="mb-4">
          <span className="font-bold text-green-800 text-sm uppercase tracking-wider">
            Cross-references ({example.linked_questions.length} questions)
          </span>
          {example.linked_questions.map((lq) => (
            <div
              key={lq.id}
              className="mt-2 bg-green-50 rounded-lg p-3 border border-green-200"
            >
              <div className="flex items-center gap-2">
                <span className="text-sm font-mono font-bold text-green-600">
                  {lq.question_id}
                </span>
                <span className="text-sm text-gray-900 font-medium">{lq.text}</span>
              </div>
              {lq.relevance_note && (
                <blockquote
                  className="text-sm text-green-700 mt-1.5 border-l-3 border-green-400 pl-3 leading-relaxed"
                  style={{ borderLeftWidth: "3px" }}
                >
                  {lq.relevance_note}
                </blockquote>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
