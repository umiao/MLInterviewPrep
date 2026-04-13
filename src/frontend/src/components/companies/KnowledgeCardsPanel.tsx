import { useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { api } from "../../utils/api";
import MarkdownPreview from "../ui/MarkdownPreview";

export interface KnowledgeCardOverlay {
  company_id: number;
  angle: string;
  overlay_body: string;
  source_file: string | null;
  source_line_start: number | null;
  source_line_end: number | null;
}

export interface KnowledgeCard {
  id: number;
  slug: string;
  title: string;
  canonical_body: string;
  tags: string[];
  provenance: {
    source_company: string | null;
    source_file: string | null;
    source_line_start: number | null;
    source_line_end: number | null;
  };
  overlays: KnowledgeCardOverlay[];
}

interface Props {
  companyId: number;
}

/**
 * Merged company-prep view: canonical knowledge cards + any company-specific
 * overlays stacked beneath, angle-labeled. Cards with overlays for the current
 * company come first; the rest are collapsed into a "Shared canonical cards"
 * section for quick reference.
 */
export default function KnowledgeCardsPanel({ companyId }: Props) {
  const [showShared, setShowShared] = useState(false);
  const { data, isLoading, isError } = useQuery<KnowledgeCard[]>({
    queryKey: ["knowledgeCards", companyId],
    queryFn: () =>
      api.get<KnowledgeCard[]>(`/knowledge_cards?company_id=${companyId}`),
    enabled: companyId > 0,
  });

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-64 text-gray-400">
        Loading knowledge cards...
      </div>
    );
  }
  if (isError || !data) {
    return (
      <div className="flex items-center justify-center h-64 text-red-500">
        Failed to load knowledge cards.
      </div>
    );
  }

  const withOverlays = data.filter((c) => c.overlays.length > 0);
  const sharedOnly = data.filter((c) => c.overlays.length === 0);

  return (
    <div className="flex-1 overflow-auto p-6 min-h-0">
      <div className="max-w-4xl mx-auto space-y-8">
        {withOverlays.length === 0 ? (
          <p className="text-gray-500 italic">
            No company-specific overlays yet for this company. All {data.length}{" "}
            shared canonical cards are listed below.
          </p>
        ) : (
          <section className="space-y-6">
            <h2 className="text-lg font-semibold text-gray-800">
              Company-specific ({withOverlays.length})
            </h2>
            {withOverlays.map((card) => (
              <CardBlock key={card.slug} card={card} />
            ))}
          </section>
        )}

        <section>
          <button
            onClick={() => setShowShared((s) => !s)}
            className="text-sm text-blue-600 hover:text-blue-800 mb-4"
          >
            {showShared ? "Hide" : "Show"} shared canonical cards (
            {sharedOnly.length})
          </button>
          {showShared && (
            <div className="space-y-6">
              {sharedOnly.map((card) => (
                <CardBlock key={card.slug} card={card} />
              ))}
            </div>
          )}
        </section>
      </div>
    </div>
  );
}

function CardBlock({ card }: { card: KnowledgeCard }) {
  return (
    <article className="border border-gray-200 rounded-lg bg-white shadow-sm">
      <header className="px-5 py-3 border-b border-gray-200 bg-gray-50 rounded-t-lg">
        <h3 className="text-base font-semibold text-gray-800">{card.title}</h3>
        <div className="mt-1 flex flex-wrap gap-1 text-xs text-gray-500">
          <span className="font-mono">{card.slug}</span>
          {card.tags.map((t) => (
            <span
              key={t}
              className="px-2 py-0.5 rounded bg-gray-200 text-gray-600"
            >
              {t}
            </span>
          ))}
        </div>
      </header>
      <div className="px-5 py-4 prep-prose">
        <MarkdownPreview markdown={card.canonical_body} />
      </div>
      {card.overlays.map((o, idx) => (
        <div
          key={idx}
          className="px-5 py-4 border-t border-dashed border-blue-200 bg-blue-50/40"
        >
          <div className="text-xs uppercase tracking-wide font-semibold text-blue-700 mb-2">
            Company angle: {o.angle}
          </div>
          <div className="prep-prose">
            <MarkdownPreview markdown={o.overlay_body} />
          </div>
        </div>
      ))}
    </article>
  );
}
