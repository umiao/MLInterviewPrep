/**
 * TanStack Query hooks for the forum scraping API.
 */
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { api } from "../utils/api";

/* ------------------------------------------------------------------ */
/*  Types (mirror backend Pydantic schemas)                           */
/* ------------------------------------------------------------------ */

export interface ForumSeed {
  id: number;
  url: string;
  source_site: string;
  label: string | null;
  company_id: number | null;
  is_active: boolean;
  last_scraped_at: string | null;
  created_at: string | null;
}

export interface ForumPostLink {
  id: number;
  forum_seed_id: number;
  url: string;
  external_post_id: string | null;
  title: string | null;
  discovered_at: string | null;
  status: string;
  retry_count: number;
  last_error: string | null;
  fetch_order: number | null;
  post_id: number | null;
}

export interface ForumPost {
  id: number;
  forum_post_link_id: number;
  raw_text: string;
  content_hash: string;
  author: string | null;
  published_at: string | null;
  fetched_at: string | null;
  company_id: number | null;
}

export interface ForumProgress {
  total: number;
  pending: number;
  fetched: number;
  failed: number;
  last_fetched_url: string | null;
}

/* ------------------------------------------------------------------ */
/*  Query hooks                                                       */
/* ------------------------------------------------------------------ */

/** List forum seeds, optionally filtered by company. */
export function useForumSeeds(companyId?: number) {
  return useQuery<ForumSeed[]>({
    queryKey: ["forumSeeds", companyId],
    queryFn: () =>
      api.get<ForumSeed[]>("/forum/seeds", {
        params: companyId !== undefined ? { company_id: companyId } : undefined,
      }),
  });
}

/** List post links for a seed. */
export function useForumLinks(seedId: number) {
  return useQuery<ForumPostLink[]>({
    queryKey: ["forumLinks", seedId],
    queryFn: () => api.get<ForumPostLink[]>(`/forum/seeds/${seedId}/links`),
    enabled: seedId > 0,
  });
}

/** Fetch progress stats for a seed. */
export function useForumProgress(seedId: number) {
  return useQuery<ForumProgress>({
    queryKey: ["forumProgress", seedId],
    queryFn: () => api.get<ForumProgress>(`/forum/seeds/${seedId}/progress`),
    enabled: seedId > 0,
  });
}

/* ------------------------------------------------------------------ */
/*  Mutation hooks                                                    */
/* ------------------------------------------------------------------ */

/** Phase A: scrape seed page to discover post links. */
export function useScrapeLinks(seedId: number) {
  const qc = useQueryClient();
  return useMutation<ForumPostLink[], Error>({
    mutationFn: () =>
      api.post<ForumPostLink[]>(`/forum/seeds/${seedId}/scrape`),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["forumLinks", seedId] });
      qc.invalidateQueries({ queryKey: ["forumProgress", seedId] });
    },
  });
}

/** Fetch a single post by link ID. */
export function useFetchPost() {
  const qc = useQueryClient();
  return useMutation<ForumPost, Error, { linkId: number; seedId: number }>({
    mutationFn: ({ linkId }) =>
      api.post<ForumPost>(`/forum/links/${linkId}/fetch`),
    onSuccess: (_data, { seedId }) => {
      qc.invalidateQueries({ queryKey: ["forumLinks", seedId] });
      qc.invalidateQueries({ queryKey: ["forumProgress", seedId] });
    },
  });
}

/** Fetch the next unfetched post for a seed. */
export function useFetchNext(seedId: number) {
  const qc = useQueryClient();
  return useMutation<ForumPost, Error>({
    mutationFn: () =>
      api.post<ForumPost>(`/forum/seeds/${seedId}/fetch-next`),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["forumLinks", seedId] });
      qc.invalidateQueries({ queryKey: ["forumProgress", seedId] });
    },
  });
}

/* ------------------------------------------------------------------ */
/*  Company Document types & hooks                                     */
/* ------------------------------------------------------------------ */

export interface CompanyDocument {
  id: number;
  company_id: number;
  title: string;
  content: string;
  source_type: string;
  doc_kind: string;
  created_at: string | null;
  updated_at: string | null;
}

/** Import a forum post into a company document. */
export function useImportPost() {
  const qc = useQueryClient();
  return useMutation<
    CompanyDocument,
    Error,
    { postId: number; companyId: number; docId?: number }
  >({
    mutationFn: ({ postId, companyId, docId }) =>
      api.post<CompanyDocument>(`/forum/posts/${postId}/import`, {
        company_id: companyId,
        ...(docId !== undefined && { doc_id: docId }),
      }),
    onSuccess: (_data, { companyId }) => {
      qc.invalidateQueries({ queryKey: ["companyDocuments", companyId] });
      qc.invalidateQueries({ queryKey: ["companies", companyId] });
    },
  });
}

/** List company documents. */
export function useCompanyDocuments(companyId: number) {
  return useQuery<CompanyDocument[]>({
    queryKey: ["companyDocuments", companyId],
    queryFn: () =>
      api.get<CompanyDocument[]>(`/companies/${companyId}/documents`),
    enabled: companyId > 0,
  });
}

/** Get a single company document. */
export function useCompanyDocument(companyId: number, docId: number) {
  return useQuery<CompanyDocument>({
    queryKey: ["companyDocument", companyId, docId],
    queryFn: () =>
      api.get<CompanyDocument>(`/companies/${companyId}/documents/${docId}`),
    enabled: companyId > 0 && docId > 0,
  });
}

/** Update a company document. */
export function useUpdateDocument(companyId: number) {
  const qc = useQueryClient();
  return useMutation<
    CompanyDocument,
    Error,
    { docId: number; title?: string; content?: string }
  >({
    mutationFn: ({ docId, ...body }) =>
      api.put<CompanyDocument>(
        `/companies/${companyId}/documents/${docId}`,
        body,
      ),
    onSuccess: (data) => {
      qc.invalidateQueries({ queryKey: ["companyDocuments", companyId] });
      qc.invalidateQueries({
        queryKey: ["companyDocument", companyId, data.id],
      });
    },
  });
}
