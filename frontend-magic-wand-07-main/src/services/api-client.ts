/**
 * UPI Guardian - Frontend API Client
 * Centralized HTTP client configured for future Flask REST API integration.
 */

export class ApiClientError extends Error {
  public readonly status: number;
  public readonly statusText: string;
  public readonly data: unknown;
  public readonly isNetworkError: boolean;
  public readonly isTimeout: boolean;

  constructor({
    message,
    status = 0,
    statusText = "",
    data = null,
    isNetworkError = false,
    isTimeout = false,
  }: {
    message: string;
    status?: number;
    statusText?: string;
    data?: unknown;
    isNetworkError?: boolean;
    isTimeout?: boolean;
  }) {
    super(message);
    this.name = "ApiClientError";
    this.status = status;
    this.statusText = statusText;
    this.data = data;
    this.isNetworkError = isNetworkError;
    this.isTimeout = isTimeout;
  }
}

export interface ApiRequestOptions extends Omit<RequestInit, "body"> {
  body?: unknown;
  params?: Record<string, string | number | boolean | undefined>;
  timeoutMs?: number;
}

export class ApiClient {
  private readonly baseUrl: string;
  private readonly defaultTimeoutMs: number;

  constructor(
    baseUrl?: string,
    defaultTimeoutMs = 10000
  ) {
    const envUrl = (import.meta.env["VITE_API_BASE_URL"] as string | undefined)?.trim();
    let configuredUrl = (baseUrl || envUrl || "http://127.0.0.1:5000/api").replace(/\/+$/, "");
    if (!configuredUrl.endsWith("/api")) {
      configuredUrl += "/api";
    }
    this.baseUrl = configuredUrl;
    this.defaultTimeoutMs = defaultTimeoutMs;
  }

  public getBaseUrl(): string {
    return this.baseUrl;
  }

  public async request<T>(endpoint: string, options: ApiRequestOptions = {}): Promise<T> {
    const { params, body, timeoutMs = this.defaultTimeoutMs, headers, ...customConfig } = options;

    let urlString = `${this.baseUrl}/${endpoint.replace(/^\/+/, "")}`;
    if (params) {
      const searchParams = new URLSearchParams();
      for (const [key, val] of Object.entries(params)) {
        if (val !== undefined && val !== null) {
          searchParams.append(key, String(val));
        }
      }
      const qs = searchParams.toString();
      if (qs) {
        urlString += (urlString.includes("?") ? "&" : "?") + qs;
      }
    }

    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), timeoutMs);

    const isJsonBody = body !== undefined && !(body instanceof FormData) && !(body instanceof Blob);

    const authToken = getAuthToken();
    const authHeaders = authToken ? { Authorization: `Bearer ${authToken}` } : {};

    const config: RequestInit = {
      ...customConfig,
      signal: controller.signal,
      headers: {
        Accept: "application/json",
        ...(isJsonBody ? { "Content-Type": "application/json" } : {}),
        ...authHeaders,
        ...headers,
      },
      ...(isJsonBody
        ? { body: JSON.stringify(body) }
        : body !== undefined
        ? { body: body as BodyInit }
        : {}),
    };

    try {
      const response = await fetch(urlString, config);
      clearTimeout(timeoutId);

      let responseData: unknown = null;
      const contentType = response.headers.get("content-type");
      if (contentType && contentType.includes("application/json")) {
        try {
          responseData = await response.json();
        } catch {
          responseData = null;
        }
      } else {
        const text = await response.text();
        responseData = text ? { message: text } : null;
      }

      if (!response.ok) {
        let message = "";
        if (responseData && typeof responseData === "object") {
          const dict = responseData as Record<string, unknown>;
          if (typeof dict["error"] === "string" && dict["error"].trim()) {
            message = dict["error"].trim();
          } else if (typeof dict["message"] === "string" && dict["message"].trim()) {
            message = dict["message"].trim();
          } else if (typeof dict["detail"] === "string" && dict["detail"].trim()) {
            message = dict["detail"].trim();
          }
        }
        if (!message) {
          message = `HTTP ${response.status}: ${response.statusText}`;
        }

        throw new ApiClientError({
          message,
          status: response.status,
          statusText: response.statusText,
          data: responseData,
        });
      }

      return responseData as T;
    } catch (err: unknown) {
      clearTimeout(timeoutId);

      if (err instanceof ApiClientError) {
        throw err;
      }

      if (err instanceof Error) {
        if (err.name === "AbortError") {
          throw new ApiClientError({
            message: `Request timed out after ${timeoutMs}ms`,
            isTimeout: true,
          });
        }
        throw new ApiClientError({
          message: "Unable to connect to UPI Guardian server.",
          isNetworkError: true,
        });
      }

      throw new ApiClientError({
        message: "Unable to connect to UPI Guardian server.",
        isNetworkError: true,
      });
    }
  }

  public get<T>(endpoint: string, options?: Omit<ApiRequestOptions, "method">): Promise<T> {
    return this.request<T>(endpoint, { ...options, method: "GET" });
  }

  public post<T>(endpoint: string, body?: unknown, options?: Omit<ApiRequestOptions, "method" | "body">): Promise<T> {
    return this.request<T>(endpoint, { ...options, method: "POST", body });
  }

  public patch<T>(endpoint: string, body?: unknown, options?: Omit<ApiRequestOptions, "method" | "body">): Promise<T> {
    return this.request<T>(endpoint, { ...options, method: "PATCH", body });
  }

  public put<T>(endpoint: string, body?: unknown, options?: Omit<ApiRequestOptions, "method" | "body">): Promise<T> {
    return this.request<T>(endpoint, { ...options, method: "PUT", body });
  }

  public delete<T>(endpoint: string, options?: Omit<ApiRequestOptions, "method">): Promise<T> {
    return this.request<T>(endpoint, { ...options, method: "DELETE" });
  }
}

export const apiClient = new ApiClient();

/**
 * Returns true if the mock provider should be used instead of the real backend.
 * Governed by the VITE_USE_MOCK_API environment variable.
 */
export function isMockEnabled(): boolean {
  const envVal = import.meta.env["VITE_USE_MOCK_API"];
  if (envVal === "false" || envVal === false) {
    return false;
  }
  return true;
}

export function getAuthToken(): string | null {
  if (typeof window === "undefined") return null;
  return localStorage.getItem("upi_guardian_access_token") || localStorage.getItem("upi_guardian_token");
}

export function setAuthToken(token: string | null, refreshToken?: string | null): void {
  if (typeof window === "undefined") return;
  if (token) {
    localStorage.setItem("upi_guardian_access_token", token);
    localStorage.setItem("upi_guardian_token", token);
  } else {
    localStorage.removeItem("upi_guardian_access_token");
    localStorage.removeItem("upi_guardian_token");
  }
  if (refreshToken) {
    localStorage.setItem("upi_guardian_refresh_token", refreshToken);
  } else if (refreshToken === null) {
    localStorage.removeItem("upi_guardian_refresh_token");
  }
}

export function clearAuthToken(): void {
  if (typeof window === "undefined") return;
  localStorage.removeItem("upi_guardian_access_token");
  localStorage.removeItem("upi_guardian_token");
  localStorage.removeItem("upi_guardian_refresh_token");
}
