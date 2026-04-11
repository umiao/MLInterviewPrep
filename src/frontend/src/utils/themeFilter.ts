import type { ThemeMode, ThemeTag } from "../types/behavioral";

export interface ThemeFilterState {
  themes: string[];
  mode: ThemeMode;
}

export function parseThemeFilterFromSearch(search: string): ThemeFilterState {
  const params = new URLSearchParams(search.startsWith("?") ? search.slice(1) : search);
  const raw = params.get("themes") ?? "";
  const themes = raw
    .split(",")
    .map((s) => s.trim())
    .filter((s) => s.length > 0);
  const modeRaw = params.get("theme_mode");
  const mode: ThemeMode = modeRaw === "and" ? "and" : "or";
  return { themes, mode };
}

export function serializeThemeFilterToSearch(
  state: ThemeFilterState,
  existing?: string,
): string {
  const params = new URLSearchParams(
    existing ? (existing.startsWith("?") ? existing.slice(1) : existing) : "",
  );
  if (state.themes.length > 0) {
    params.set("themes", state.themes.join(","));
    params.set("theme_mode", state.mode);
  } else {
    params.delete("themes");
    params.delete("theme_mode");
  }
  const qs = params.toString();
  return qs ? `?${qs}` : "";
}

export function toggleThemeInState(
  state: ThemeFilterState,
  slug: string,
): ThemeFilterState {
  const idx = state.themes.indexOf(slug);
  if (idx === -1) {
    return { ...state, themes: [...state.themes, slug] };
  }
  return {
    ...state,
    themes: state.themes.filter((s) => s !== slug),
  };
}

export function questionMatchesThemeFilter(
  questionThemes: ThemeTag[] | undefined | null,
  state: ThemeFilterState,
): boolean {
  if (state.themes.length === 0) return true;
  const tags = new Set((questionThemes ?? []).map((t) => t.slug));
  if (state.mode === "or") {
    return state.themes.some((slug) => tags.has(slug));
  }
  return state.themes.every((slug) => tags.has(slug));
}
