import { useQuery } from "@tanstack/react-query";
import { api } from "../utils/api";
import type {
  CardIndexCard,
  CardIndexContent,
  CardIndexProblem,
  CompanyDocument,
} from "../types/company";

interface CompanyCardIndexProps {
  companyId: number;
  onLcClick: (lcId: number) => void;
  onDbClick: (dbId: number) => void;
}

/**
 * Renders a company's card_index document as a responsive grid of bilingual
 * cluster cards. Each card lists problems that open the appropriate drawer
 * via the onLcClick / onDbClick callbacks.
 */
export default function CompanyCardIndex({
  companyId,
  onLcClick,
  onDbClick,
}: CompanyCardIndexProps) {
  const { data, isLoading, isError } = useQuery<CompanyDocument[]>({
    queryKey: ["companyDocuments", companyId],
    queryFn: () =>
      api.get<CompanyDocument[]>(`/companies/${companyId}/documents`),
    enabled: companyId > 0,
  });

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-64 text-gray-400">
        Loading card index...
      </div>
    );
  }
  if (isError || !data) {
    return (
      <div className="flex items-center justify-center h-64 text-red-500">
        Failed to load card index.
      </div>
    );
  }

  const cardDoc = data.find((d) => d.doc_kind === "card_index");
  if (!cardDoc) {
    return (
      <div className="p-6 text-gray-500 italic">
        No card index available for this company yet.
      </div>
    );
  }

  let parsed: CardIndexContent;
  try {
    parsed = JSON.parse(cardDoc.content) as CardIndexContent;
  } catch {
    return (
      <div className="p-6 text-red-500">
        Card index document is malformed JSON.
      </div>
    );
  }

  if (!parsed.cards || parsed.cards.length === 0) {
    return (
      <div className="p-6 text-gray-500 italic">
        Card index contains no cards.
      </div>
    );
  }

  return (
    <div className="p-6">
      <div
        className="grid gap-4"
        style={{
          gridTemplateColumns: "repeat(auto-fit, minmax(380px, 1fr))",
        }}
      >
        {parsed.cards.map((card, idx) => (
          <CardBlock
            key={idx}
            card={card}
            onLcClick={onLcClick}
            onDbClick={onDbClick}
          />
        ))}
      </div>
    </div>
  );
}

interface CardBlockProps {
  card: CardIndexCard;
  onLcClick: (lcId: number) => void;
  onDbClick: (dbId: number) => void;
}

function CardBlock({ card, onLcClick, onDbClick }: CardBlockProps) {
  const collapse = card.problems.length > 5;
  const list = (
    <ul className="mt-2 space-y-1.5 text-sm">
      {card.problems.map((p) => (
        <ProblemRow
          key={p.id}
          problem={p}
          onLcClick={onLcClick}
          onDbClick={onDbClick}
        />
      ))}
    </ul>
  );

  return (
    <article className="border border-gray-200 rounded-lg bg-white shadow-sm p-4">
      <h3 className="text-base mb-1">
        <span className="font-bold text-gray-900">{card.name_zh}</span>
        <span className="font-normal text-gray-500"> -- {card.name_en}</span>
      </h3>
      {card.summary_zh && (
        <p className="text-xs text-gray-500 italic mb-2">{card.summary_zh}</p>
      )}
      {collapse ? (
        <details>
          <summary className="cursor-pointer text-xs text-gray-600 select-none hover:text-gray-800">
            {card.problems.length} {"\u9898"}
          </summary>
          {list}
        </details>
      ) : (
        list
      )}
    </article>
  );
}

interface ProblemRowProps {
  problem: CardIndexProblem;
  onLcClick: (lcId: number) => void;
  onDbClick: (dbId: number) => void;
}

function ProblemRow({ problem, onLcClick, onDbClick }: ProblemRowProps) {
  const isLc = problem.leetcode_id !== null && problem.leetcode_id !== undefined;
  const label = isLc ? `LC ${problem.leetcode_id}` : `db:${problem.id}`;
  return (
    <li>
      <button
        type="button"
        onClick={() =>
          isLc ? onLcClick(problem.leetcode_id as number) : onDbClick(problem.id)
        }
        className="text-left text-blue-700 hover:text-blue-900 hover:underline"
      >
        <span className="font-mono text-xs text-gray-500 mr-1">{label}</span>
        <span>{problem.title}</span>
      </button>
      {problem.one_liner && (
        <span className="text-gray-500 text-xs"> -- {problem.one_liner}</span>
      )}
    </li>
  );
}
