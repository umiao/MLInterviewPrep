// Single source of truth for "does this node have drawer content?".
// Accepts either the API raw shape ({content_length}) or the in-app NodeMeta
// shape ({contentLength}), so consumers can call it without reshaping.

export interface HasContentInput {
  contentLength?: number;
  content_length?: number;
}

export function hasContent(node: HasContentInput): boolean {
  const len = node.contentLength ?? node.content_length ?? 0;
  return len > 0;
}
