export interface PitchParts {
  summary: string;
  facts: string[];
}

export function parsePitch(pitch: string): PitchParts {
  const separator = " | KEY FACTS: ";
  const idx = pitch.indexOf(separator);
  if (idx === -1) return { summary: pitch, facts: [] };
  const summary = pitch.substring(0, idx);
  const factsStr = pitch.substring(idx + separator.length);
  const facts = factsStr
    .split("|")
    .map((f) => f.trim())
    .filter(Boolean);
  return { summary, facts };
}
