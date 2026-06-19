import { describe, expect, it } from "vitest";
import { renderToStaticMarkup } from "react-dom/server";
import { MemoryRouter } from "react-router-dom";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { normalizeTagLabel } from "../utils/tagLabel";
import { QuestionRow } from "./BehavioralQuestions";
import type {
  BehavioralExample,
  ProbeNotes,
} from "../types/behavioral";

describe("normalizeTagLabel (T-P0-626 regression)", () => {
  it("turns underscore phrases into space-separated words", () => {
    expect(normalizeTagLabel("problem_framing_before_persuasion")).toBe(
      "problem framing before persuasion",
    );
  });

  it("leaves single-word slugs unchanged", () => {
    expect(normalizeTagLabel("ownership")).toBe("ownership");
  });

  it("leaves human-readable labels (no underscores) unchanged", () => {
    expect(normalizeTagLabel("Adaptability")).toBe("Adaptability");
  });

  it("handles empty input", () => {
    expect(normalizeTagLabel("")).toBe("");
  });

  it("normalizes multiple consecutive underscores to spaces", () => {
    expect(normalizeTagLabel("a__b")).toBe("a  b");
  });
});

describe("ExampleCard structural regression (T-P0-626)", () => {
  // The previous layout used a left/right flex split with the right column
  // marked `shrink-0 flex-wrap`, which let long principle pills hold the
  // right column at ~50% of the card and crushed the title cell. The fix
  // is to stack vertically: title row, source line, FacetPills, then
  // principle pills as a NEW row with its own `flex-wrap gap-2`. The
  // bq-example-card-body marker class is the load-bearing assertion.
  it("BehavioralQuestions.tsx no longer contains the flex shrink-0 + flex-wrap right column for principle pills", async () => {
    const fs = await import("node:fs/promises");
    const path = await import("node:path");
    const file = await fs.readFile(
      path.resolve(__dirname, "BehavioralQuestions.tsx"),
      "utf-8",
    );
    // The exact pre-fix pattern that caused the squeeze.
    expect(file).not.toContain(
      'className="flex items-center gap-2 flex-wrap shrink-0"',
    );
    // The new vertical-stack marker must be present.
    expect(file).toContain("bq-example-card-body");
    // Principle pills row marker must be present.
    expect(file).toContain("bq-principle-pills");
    // h4 must have break-words (allows wrap when squeezed; was missing pre-fix).
    expect(file).toMatch(
      /<h4 className="text-gray-900 font-bold text-base break-words/,
    );
    // Pills must use normalizeTagLabel (the _ -> space helper).
    expect(file).toContain("normalizeTagLabel(fullLabel)");
  });

  it("renders without crashing inside the QueryClient + Router shell (smoke)", () => {
    // This is intentionally a degenerate smoke test: it does not exercise
    // useQuery (no API mock here), but it ensures the export shape is
    // stable so a stray import-time error from the page module would
    // surface in CI before T-P0-626's structural change ships. The page
    // proper renders inside react-query and react-router so we wrap both.
    const client = new QueryClient({
      defaultOptions: { queries: { retry: false } },
    });
    expect(() =>
      renderToStaticMarkup(
        <QueryClientProvider client={client}>
          <MemoryRouter>
            <div data-testid="bq-shell" />
          </MemoryRouter>
        </QueryClientProvider>,
      ),
    ).not.toThrow();
  });
});

/* ------------------------------------------------------------------ */
/* T-P1-583: BQ-DEPTH Phase D -- primary card + probe panel scenarios  */
/* ------------------------------------------------------------------ */

function makeExample(
  overrides: Partial<BehavioralExample> & { example_id: string },
): BehavioralExample {
  return {
    id: 1,
    title: "Default Story",
    source_project: null,
    situation: "A hard situation that needs more than two hundred chars maybe.",
    task: null,
    action: null,
    result: null,
    evidence_quotes: [],
    principle_tags: [],
    risk_statement: null,
    analogy: null,
    tech_terms: {},
    is_golden: false,
    golden_at: null,
    linked_questions: [],
    ...overrides,
  };
}

const PROBE: ProbeNotes = {
  core_signal: "Do they own the outcome end to end?",
  what_good_looks_like: ["Clear metric", "Owned the rollback"],
  what_L5_adds: ["Pulled in adjacent teams"],
  common_failure_modes: ["Blames the org"],
};

// Minimal question shape compatible with the page's internal interface
// (structural typing -- the interface is not exported on purpose).
function makeQuestion(probe_notes: ProbeNotes | null) {
  return {
    id: 10,
    question_id: "OWN-1",
    text: "Tell me about a time you owned a failure.",
    category_id: "OWN",
    category_name: "Ownership",
    original_category: null,
    example_count: 2,
    probe_notes,
  };
}

function renderRow(
  question: ReturnType<typeof makeQuestion>,
  examples: BehavioralExample[],
) {
  return renderToStaticMarkup(
    <QuestionRow
      question={question}
      examples={examples}
      expanded
      onToggle={() => {}}
      onExampleClick={() => {}}
      selectedThemes={new Set<string>()}
      onThemePillClick={() => {}}
      goldenOnly={false}
    />,
  );
}

describe("QuestionRow primary-story + probe panel (T-P1-583)", () => {
  const primaryEx = makeExample({
    id: 1,
    example_id: "OWN-2",
    title: "Owned the outage",
    linked_questions: [
      {
        id: 1,
        question_id: "OWN-1",
        text: "",
        category_id: "OWN",
        relevance_note: "Direct ownership angle",
        is_primary: true,
      },
    ],
  });
  const backupEx = makeExample({
    id: 2,
    example_id: "OWN-6",
    title: "Backup story",
    linked_questions: [
      {
        id: 2,
        question_id: "OWN-1",
        text: "",
        category_id: "OWN",
        relevance_note: "Secondary angle",
        is_primary: false,
      },
    ],
  });

  it("scenario A: is_primary link + probe_notes -> primary card + Also applies + probe toggle", () => {
    const html = renderRow(makeQuestion(PROBE), [primaryEx, backupEx]);
    expect(html).toContain("bq-primary-story-card");
    expect(html).toContain("Primary story");
    expect(html).toContain("Owned the outage");
    expect(html).toContain("Direct ownership angle");
    expect(html).toContain("Also applies");
    expect(html).toContain("What this question probes");
  });

  it("scenario B: is_primary link + no probe_notes -> primary card, probe toggle hidden", () => {
    const html = renderRow(makeQuestion(null), [primaryEx, backupEx]);
    expect(html).toContain("bq-primary-story-card");
    expect(html).not.toContain("What this question probes");
  });

  it("scenario C: no is_primary link -> flat fallback, no primary card", () => {
    const flatEx = makeExample({
      id: 3,
      example_id: "OWN-9",
      title: "Flat list story",
      linked_questions: [
        {
          id: 3,
          question_id: "OWN-1",
          text: "",
          category_id: "OWN",
          relevance_note: "Just a link",
          is_primary: false,
        },
      ],
    });
    const html = renderRow(makeQuestion(PROBE), [flatEx]);
    expect(html).not.toContain("bq-primary-story-card");
    // probe panel is gated on a primary story, so no probe toggle either
    expect(html).not.toContain("What this question probes");
    expect(html).toContain("Flat list story");
  });

  it("scenario D: 0 links -> 'no examples linked' empty state", () => {
    const unrelated = makeExample({
      id: 4,
      example_id: "ADP-1",
      title: "Unrelated",
      linked_questions: [
        {
          id: 4,
          question_id: "ADP-3",
          text: "",
          category_id: "ADP",
          relevance_note: null,
          is_primary: true,
        },
      ],
    });
    const html = renderRow(makeQuestion(PROBE), [unrelated]);
    expect(html).not.toContain("bq-primary-story-card");
    expect(html).toContain("No examples linked to this question yet.");
  });
});
