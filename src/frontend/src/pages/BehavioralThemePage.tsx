import { useState } from "react";
import { Link, useParams } from "react-router-dom";
import { useQuery } from "@tanstack/react-query";
import { api } from "../utils/api";
import type {
  BehavioralThemeSummary,
  BehavioralExample,
} from "../types/behavioral";
import SlideOverPanel from "../components/ui/SlideOverPanel";
import ExampleDrawerContent from "../components/behavioral/ExampleDrawerContent";
import GoldenToggleButton from "../components/ui/GoldenToggleButton";
import GoldenBadge from "../components/ui/GoldenBadge";
import SignatureBadge from "../components/ui/SignatureBadge";
import FacetPills from "../components/behavioral/FacetPills";
import { goldenCardClass } from "../utils/goldenStyle";
import { parsePitch } from "../utils/parsePitch";
import { useReturnPath } from "../hooks/useReturnPath";
import { useRouteScrollRestore } from "../hooks/useRouteScrollRestore";

interface BehavioralQuestion {
  id: number;
  question_id: string;
  text: string;
  category_id: string;
  category_name: string;
  original_category: string | null;
  example_count: number;
}

export default function BehavioralThemePage() {
  const { slug } = useParams<{ slug: string }>();
  const returnUrl = useReturnPath("/quick-index?section=bq");
  useRouteScrollRestore();

  const [activeExampleId, setActiveExampleId] = useState<string | null>(null);

  const { data: themes } = useQuery<BehavioralThemeSummary[]>({
    queryKey: ["behavioral-themes"],
    queryFn: () => api.get("/behavioral/themes"),
    staleTime: Infinity,
  });

  const theme = themes?.find((t) => t.slug === slug);

  const { data: examples } = useQuery<BehavioralExample[]>({
    queryKey: ["behavioral-examples-theme", slug],
    queryFn: () =>
      api.get("/behavioral/examples", { params: { theme: slug } }),
    enabled: !!slug,
  });

  const { data: questions } = useQuery<BehavioralQuestion[]>({
    queryKey: ["behavioral-questions-theme", slug],
    queryFn: () =>
      api.get("/behavioral/questions", { params: { theme: slug } }),
    enabled: !!slug,
  });

  const activeExample = activeExampleId
    ? examples?.find((e) => e.example_id === activeExampleId) ?? null
    : null;

  return (
    <div className="max-w-6xl mx-auto py-6 px-4">
      {/* Header */}
      <div className="mb-8">
        <Link
          to={returnUrl}
          className="text-sm text-blue-600 hover:text-blue-800 inline-flex items-center gap-1 mb-3"
        >
          &larr; Back
        </Link>
        {theme ? (
          <>
            <h1 className="text-2xl font-bold text-gray-900">{theme.label}</h1>
            {theme.description && (
              <p className="mt-1 text-gray-600">{theme.description}</p>
            )}
            <div className="mt-2 text-sm text-gray-500">
              {theme.question_count} questions &middot; {theme.example_count}{" "}
              examples
            </div>
          </>
        ) : (
          <h1 className="text-2xl font-bold text-gray-900">{slug}</h1>
        )}
      </div>

      {/* Example cards */}
      <section className="mb-10">
        <h2 className="text-lg font-semibold text-gray-800 mb-4">
          Master Stories
        </h2>
        {examples && examples.length === 0 && (
          <p className="text-gray-400 italic">
            No master stories tagged to this theme yet.
          </p>
        )}
        {examples && examples.length > 0 && (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {examples.map((ex) => (
              <ExampleCard
                key={ex.example_id}
                example={ex}
                onClick={() => setActiveExampleId(ex.example_id)}
              />
            ))}
          </div>
        )}
      </section>

      {/* Questions list */}
      {questions && questions.length > 0 && (
        <section>
          <h2 className="text-lg font-semibold text-gray-800 mb-3">
            Questions ({questions.length})
          </h2>
          <ul className="space-y-2">
            {questions.map((q) => (
              <li key={q.id} className="flex items-start gap-2">
                <span className="font-mono text-xs font-bold text-green-600 bg-green-50 px-1.5 py-0.5 rounded mt-0.5 shrink-0">
                  {q.question_id}
                </span>
                <span className="text-gray-800 text-sm leading-snug">
                  {q.text}
                </span>
              </li>
            ))}
          </ul>
        </section>
      )}

      {/* Drawer */}
      <SlideOverPanel
        open={activeExample !== null}
        onClose={() => setActiveExampleId(null)}
        title={activeExample?.title ?? ""}
        headerActions={
          activeExample ? (
            <GoldenToggleButton
              itemType="behavioral_example"
              itemId={activeExample.id}
              isGolden={Boolean(activeExample.is_golden)}
            />
          ) : null
        }
        headerAccentClassName={
          activeExample?.is_golden ? "border-t-2 border-t-orange-300" : ""
        }
      >
        {activeExample && <ExampleDrawerContent example={activeExample} />}
      </SlideOverPanel>
    </div>
  );
}

function ExampleCard({
  example,
  onClick,
}: {
  example: BehavioralExample;
  onClick: () => void;
}) {
  const pitch = example.cn_elevator_pitch;
  const pitchParts = pitch ? parsePitch(pitch) : null;
  const isGolden = Boolean(example.is_golden);
  const isSignature = Boolean(example.is_signature);

  return (
    <button
      type="button"
      onClick={onClick}
      className={
        "text-left w-full p-4 rounded-lg border border-gray-200 bg-white hover:border-blue-400 hover:shadow-md transition-all " +
        goldenCardClass(isGolden)
      }
    >
      <div className="flex items-center gap-1.5 flex-wrap">
        <span className="font-mono text-xs font-bold text-blue-600 bg-blue-50 px-1.5 py-0.5 rounded">
          {example.example_id}
        </span>
        <GoldenBadge golden={isGolden} />
        <SignatureBadge signature={isSignature} />
      </div>
      <div className="mt-2 font-medium text-gray-800 text-sm leading-snug">
        {example.title}
      </div>
      <FacetPills facets={example.facet_tags} className="mt-1.5" />
      {pitchParts ? (
        <div className="mt-2">
          <p className="text-sm text-gray-700 leading-snug bq-pitch-text">
            {pitchParts.summary}
          </p>
          {pitchParts.facts.length > 0 && (
            <div className="mt-1.5 flex flex-wrap gap-1">
              {pitchParts.facts.map((fact, i) => (
                <span
                  key={i}
                  className="bq-pitch-pill text-xs bg-gray-100 text-gray-700 border border-gray-200 px-2 py-0.5 rounded-full"
                >
                  {fact}
                </span>
              ))}
            </div>
          )}
        </div>
      ) : (
        <p className="mt-2 text-sm italic text-gray-400">{example.title}</p>
      )}
    </button>
  );
}

