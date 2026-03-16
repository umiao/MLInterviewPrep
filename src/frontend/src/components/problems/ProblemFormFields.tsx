import FormField from "../ui/FormField";
import FrameworkNodePicker from "../framework/FrameworkNodePicker";
import type { Category, Difficulty } from "../../types/problem";

const DIFFICULTIES: Difficulty[] = ["easy", "medium", "hard"];
const CATEGORIES: { value: Category; label: string }[] = [
  { value: "algorithm", label: "Algorithm" },
  { value: "ml_coding", label: "ML Coding" },
  { value: "system_design", label: "System Design" },
];

export interface ProblemFormData {
  title: string;
  leetcode_id: string;
  url: string;
  difficulty: Difficulty | "";
  tags: string;
  pattern: string;
  category: Category;
  source: string;
  company_tags: string;
  priority: number;
  framework_node_id: number | null;
}

export const EMPTY_FORM: ProblemFormData = {
  title: "",
  leetcode_id: "",
  url: "",
  difficulty: "",
  tags: "",
  pattern: "",
  category: "algorithm",
  source: "",
  company_tags: "",
  priority: 2,
  framework_node_id: null,
};

interface ProblemFormFieldsProps {
  form: ProblemFormData;
  onChange: (updates: Partial<ProblemFormData>) => void;
  errors: Record<string, string>;
}

export default function ProblemFormFields({
  form,
  onChange,
  errors,
}: ProblemFormFieldsProps) {
  const inputClass =
    "w-full text-sm border border-gray-300 rounded px-2 py-1.5 focus:outline-none focus:ring-1 focus:ring-blue-300 focus:border-blue-300";

  return (
    <>
      <FormField label="Title" htmlFor="pf-title" required error={errors.title}>
        <input
          id="pf-title"
          type="text"
          value={form.title}
          onChange={(e) => onChange({ title: e.target.value })}
          className={inputClass}
          placeholder="Two Sum"
        />
      </FormField>

      <div className="grid grid-cols-2 gap-3">
        <FormField label="LeetCode ID" htmlFor="pf-lcid">
          <input
            id="pf-lcid"
            type="number"
            value={form.leetcode_id}
            onChange={(e) => onChange({ leetcode_id: e.target.value })}
            className={inputClass}
            placeholder="1"
          />
        </FormField>

        <FormField label="Difficulty" htmlFor="pf-diff">
          <select
            id="pf-diff"
            value={form.difficulty}
            onChange={(e) =>
              onChange({ difficulty: (e.target.value as Difficulty) || "" })
            }
            className={inputClass}
          >
            <option value="">--</option>
            {DIFFICULTIES.map((d) => (
              <option key={d} value={d} className="capitalize">
                {d.charAt(0).toUpperCase() + d.slice(1)}
              </option>
            ))}
          </select>
        </FormField>
      </div>

      <FormField label="URL" htmlFor="pf-url">
        <input
          id="pf-url"
          type="url"
          value={form.url}
          onChange={(e) => onChange({ url: e.target.value })}
          className={inputClass}
          placeholder="https://leetcode.com/problems/two-sum"
        />
      </FormField>

      <div className="grid grid-cols-2 gap-3">
        <FormField label="Category" htmlFor="pf-cat">
          <select
            id="pf-cat"
            value={form.category}
            onChange={(e) => onChange({ category: e.target.value as Category })}
            className={inputClass}
          >
            {CATEGORIES.map((c) => (
              <option key={c.value} value={c.value}>
                {c.label}
              </option>
            ))}
          </select>
        </FormField>

        <FormField label="Priority" htmlFor="pf-pri">
          <select
            id="pf-pri"
            value={form.priority}
            onChange={(e) => onChange({ priority: Number(e.target.value) })}
            className={inputClass}
          >
            <option value={1}>1 - Low</option>
            <option value={2}>2 - Medium</option>
            <option value={3}>3 - High</option>
          </select>
        </FormField>
      </div>

      <FormField label="Pattern" htmlFor="pf-pattern">
        <input
          id="pf-pattern"
          type="text"
          value={form.pattern}
          onChange={(e) => onChange({ pattern: e.target.value })}
          className={inputClass}
          placeholder="e.g. Two Pointers, DP"
        />
      </FormField>

      <FormField label="Source" htmlFor="pf-source">
        <input
          id="pf-source"
          type="text"
          value={form.source}
          onChange={(e) => onChange({ source: e.target.value })}
          className={inputClass}
          placeholder="e.g. leetcode, neetcode150"
        />
      </FormField>

      <FormField
        label="Tags"
        htmlFor="pf-tags"
      >
        <input
          id="pf-tags"
          type="text"
          value={form.tags}
          onChange={(e) => onChange({ tags: e.target.value })}
          className={inputClass}
          placeholder="Comma-separated: array, hash-map"
        />
      </FormField>

      <FormField
        label="Company Tags"
        htmlFor="pf-company"
      >
        <input
          id="pf-company"
          type="text"
          value={form.company_tags}
          onChange={(e) => onChange({ company_tags: e.target.value })}
          className={inputClass}
          placeholder="Comma-separated: google, meta"
        />
      </FormField>

      <FormField label="Framework Topic">
        <FrameworkNodePicker
          value={form.framework_node_id}
          onChange={(id) => onChange({ framework_node_id: id })}
          placeholder="Link to a framework topic..."
        />
      </FormField>
    </>
  );
}

/** Convert form data to the API payload shape. */
export function formToPayload(form: ProblemFormData): Record<string, unknown> {
  const splitCsv = (s: string) =>
    s
      .split(",")
      .map((t) => t.trim())
      .filter(Boolean);

  return {
    title: form.title.trim(),
    leetcode_id: form.leetcode_id ? Number(form.leetcode_id) : null,
    url: form.url.trim() || null,
    difficulty: form.difficulty || null,
    tags: splitCsv(form.tags),
    pattern: form.pattern.trim() || null,
    category: form.category,
    source: form.source.trim() || null,
    company_tags: splitCsv(form.company_tags),
    priority: form.priority,
    framework_node_id: form.framework_node_id,
  };
}
