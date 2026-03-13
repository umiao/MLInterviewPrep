/**
 * API utility layer -- thin fetch wrapper with base URL, error handling,
 * and automatic JSON parsing.
 */

const BASE_URL = "/api";

export interface ApiError {
  status: number;
  message: string;
  detail?: unknown;
}

export class ApiRequestError extends Error {
  status: number;
  detail?: unknown;

  constructor(status: number, message: string, detail?: unknown) {
    super(message);
    this.name = "ApiRequestError";
    this.status = status;
    this.detail = detail;
  }
}

async function handleResponse<T>(response: Response): Promise<T> {
  if (!response.ok) {
    let detail: unknown;
    try {
      detail = await response.json();
    } catch {
      // response body is not JSON
    }
    const message =
      typeof detail === "object" && detail !== null && "detail" in detail
        ? String((detail as Record<string, unknown>).detail)
        : response.statusText;
    throw new ApiRequestError(response.status, message, detail);
  }
  // 204 No Content
  if (response.status === 204) {
    return undefined as T;
  }
  return response.json() as Promise<T>;
}

type RequestOptions = Omit<RequestInit, "body"> & {
  body?: unknown;
  params?: Record<string, string | number | boolean | undefined>;
};

function buildUrl(path: string, params?: RequestOptions["params"]): string {
  const url = `${BASE_URL}${path}`;
  if (!params) return url;
  const searchParams = new URLSearchParams();
  for (const [key, value] of Object.entries(params)) {
    if (value !== undefined) {
      searchParams.append(key, String(value));
    }
  }
  const qs = searchParams.toString();
  return qs ? `${url}?${qs}` : url;
}

function buildInit(options?: RequestOptions): RequestInit {
  // eslint-disable-next-line @typescript-eslint/no-unused-vars -- params consumed by buildUrl
  const { body, params, headers, ...rest } = options ?? {};
  const init: RequestInit = { ...rest };
  if (body !== undefined) {
    init.body = JSON.stringify(body);
    init.headers = {
      "Content-Type": "application/json",
      ...(headers as Record<string, string>),
    };
  } else if (headers) {
    init.headers = headers;
  }
  return init;
}

export const api = {
  async get<T = unknown>(
    path: string,
    options?: RequestOptions,
  ): Promise<T> {
    const url = buildUrl(path, options?.params);
    const init = buildInit({ ...options, method: "GET" });
    return handleResponse<T>(await fetch(url, init));
  },

  async post<T = unknown>(
    path: string,
    body?: unknown,
    options?: RequestOptions,
  ): Promise<T> {
    const url = buildUrl(path, options?.params);
    const init = buildInit({ ...options, body, method: "POST" });
    return handleResponse<T>(await fetch(url, init));
  },

  async put<T = unknown>(
    path: string,
    body?: unknown,
    options?: RequestOptions,
  ): Promise<T> {
    const url = buildUrl(path, options?.params);
    const init = buildInit({ ...options, body, method: "PUT" });
    return handleResponse<T>(await fetch(url, init));
  },

  async del<T = unknown>(
    path: string,
    options?: RequestOptions,
  ): Promise<T> {
    const url = buildUrl(path, options?.params);
    const init = buildInit({ ...options, method: "DELETE" });
    return handleResponse<T>(await fetch(url, init));
  },
};
