/**
 * Shared slugify utility for generating heading IDs.
 * Used by both MarkdownPreview (to assign IDs) and DocTocSidebar (to build links).
 */
export function slugify(text: string): string {
  return text
    .toLowerCase()
    .trim()
    .replace(/[\s]+/g, "-") // spaces -> hyphens
    .replace(/[^\w\u4e00-\u9fff\u3400-\u4dbf-]/g, "") // keep alphanum, CJK, hyphens
    .replace(/--+/g, "-") // collapse multiple hyphens
    .replace(/^-|-$/g, ""); // trim leading/trailing hyphens
}

export interface TocHeading {
  level: number; // 1, 2, or 3
  text: string;
  id: string;
}
