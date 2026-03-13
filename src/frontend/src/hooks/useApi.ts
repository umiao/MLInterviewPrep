import { useCallback, useEffect, useRef, useState } from "react";
import { api, ApiRequestError } from "../utils/api";

type RequestOptions = {
  params?: Record<string, string | number | boolean | undefined>;
};

interface UseApiState<T> {
  data: T | null;
  loading: boolean;
  error: ApiRequestError | null;
}

interface UseApiResult<T> extends UseApiState<T> {
  refetch: () => void;
}

/**
 * Hook for GET requests that fire on mount and expose a refetch handle.
 *
 * Usage:
 *   const { data, loading, error, refetch } = useApi<Problem[]>("/problems");
 */
export function useApi<T = unknown>(
  path: string | null,
  options?: RequestOptions,
): UseApiResult<T> {
  const [state, setState] = useState<UseApiState<T>>({
    data: null,
    loading: !!path,
    error: null,
  });

  // Serialize options so we can use them as a dep without infinite loops
  const optionsKey = options ? JSON.stringify(options) : "";

  // Keep a ref to the latest fetch call so we can call it imperatively (refetch)
  const fetchIdRef = useRef(0);

  const doFetch = useCallback(async (id: number) => {
    if (!path) return;
    setState((s) => ({ ...s, loading: true, error: null }));
    try {
      const parsed: RequestOptions | undefined = optionsKey
        ? JSON.parse(optionsKey)
        : undefined;
      const data = await api.get<T>(path, parsed);
      // Only update state if this is still the latest request
      if (id === fetchIdRef.current) {
        setState({ data, loading: false, error: null });
      }
    } catch (err) {
      if (id === fetchIdRef.current) {
        const apiErr =
          err instanceof ApiRequestError
            ? err
            : new ApiRequestError(0, String(err));
        setState({ data: null, loading: false, error: apiErr });
      }
    }
  }, [path, optionsKey]);

  // Subscribe to path/options changes -- intentionally mutates fetchIdRef in
  // cleanup to invalidate in-flight requests when deps change.
  useEffect(() => {
    if (!path) return;
    const id = ++fetchIdRef.current;
    doFetch(id);
    return () => {
      fetchIdRef.current = id + 1;
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [path, optionsKey]);

  const refetch = useCallback(() => {
    const id = ++fetchIdRef.current;
    doFetch(id);
  }, [doFetch]);

  return { ...state, refetch };
}

/**
 * Hook for mutations (POST / PUT / DELETE). Returns an execute function.
 *
 * Usage:
 *   const { execute, loading, error } = useMutation<Result>("POST", "/problems");
 *   const result = await execute({ title: "Two Sum", ... });
 */
interface UseMutationResult<T> {
  execute: (body?: unknown, options?: RequestOptions) => Promise<T>;
  loading: boolean;
  error: ApiRequestError | null;
}

export function useMutation<T = unknown>(
  method: "POST" | "PUT" | "DELETE",
  path: string,
): UseMutationResult<T> {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<ApiRequestError | null>(null);

  const execute = useCallback(
    async (body?: unknown, options?: RequestOptions): Promise<T> => {
      setLoading(true);
      setError(null);
      try {
        let data: T;
        switch (method) {
          case "POST":
            data = await api.post<T>(path, body, options);
            break;
          case "PUT":
            data = await api.put<T>(path, body, options);
            break;
          case "DELETE":
            data = await api.del<T>(path, options);
            break;
        }
        return data;
      } catch (err) {
        const apiErr =
          err instanceof ApiRequestError
            ? err
            : new ApiRequestError(0, String(err));
        setError(apiErr);
        throw apiErr;
      } finally {
        setLoading(false);
      }
    },
    [method, path],
  );

  return { execute, loading, error };
}
