import type { BehavioralThemeSummary, ThemeMode } from "../../types/behavioral";

interface ThemeFilterSidebarProps {
  themes: BehavioralThemeSummary[];
  selectedSlugs: string[];
  mode: ThemeMode;
  onToggleTheme: (slug: string) => void;
  onChangeMode: (mode: ThemeMode) => void;
  onClear: () => void;
  variant?: "sidebar" | "sheet";
}

export default function ThemeFilterSidebar({
  themes,
  selectedSlugs,
  mode,
  onToggleTheme,
  onChangeMode,
  onClear,
  variant = "sidebar",
}: ThemeFilterSidebarProps) {
  const selected = new Set(selectedSlugs);
  const sorted = [...themes].sort((a, b) => {
    if (b.question_count !== a.question_count) {
      return b.question_count - a.question_count;
    }
    return a.label.localeCompare(b.label);
  });

  const containerClass =
    variant === "sheet"
      ? "w-full"
      : "w-full bg-white rounded-xl border-2 border-gray-200 shadow-sm p-4";

  return (
    <aside className={containerClass} aria-label="Theme filter">
      <div className="flex items-center justify-between mb-3">
        <h3 className="text-sm font-bold uppercase tracking-wider text-gray-700">
          Themes
        </h3>
        {selectedSlugs.length > 0 && (
          <button
            type="button"
            onClick={onClear}
            className="text-xs font-semibold text-blue-600 hover:text-blue-800"
          >
            Clear
          </button>
        )}
      </div>

      <div className="flex items-center gap-2 mb-4" role="radiogroup" aria-label="Combine themes with">
        <span className="text-xs font-semibold text-gray-500 uppercase">Combine:</span>
        {(["or", "and"] as ThemeMode[]).map((m) => (
          <button
            key={m}
            type="button"
            role="radio"
            aria-checked={mode === m}
            onClick={() => onChangeMode(m)}
            className={`px-2.5 py-1 rounded-md text-xs font-bold uppercase transition-all ${
              mode === m
                ? "bg-blue-600 text-white shadow-sm"
                : "bg-gray-100 text-gray-700 hover:bg-gray-200 border border-gray-300"
            }`}
          >
            {m}
          </button>
        ))}
      </div>

      <ul className="space-y-1.5">
        {sorted.map((theme) => {
          const isSelected = selected.has(theme.slug);
          return (
            <li key={theme.slug}>
              <button
                type="button"
                onClick={() => onToggleTheme(theme.slug)}
                aria-pressed={isSelected}
                className={`w-full flex items-center justify-between gap-2 px-3 py-2 rounded-lg text-left text-sm font-medium transition-all ${
                  isSelected
                    ? "bg-blue-600 text-white shadow-sm"
                    : "bg-gray-50 text-gray-800 hover:bg-blue-50 border border-gray-200"
                }`}
              >
                <span className="truncate">{theme.label}</span>
                <span
                  className={`text-xs font-bold shrink-0 ${
                    isSelected ? "text-blue-100" : "text-gray-500"
                  }`}
                >
                  ({theme.question_count})
                </span>
              </button>
            </li>
          );
        })}
      </ul>
    </aside>
  );
}
