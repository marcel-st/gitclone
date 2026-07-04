// Typed fetch wrapper for the orchestrator API. Uses the Django session cookie
// (the user is signed in via /admin) and sends the CSRF token on writes.

const BASE = "/orchestrator-api";

function csrfToken(): string {
  const match = document.cookie.match(/(?:^|;\s*)csrftoken=([^;]+)/);
  return match ? decodeURIComponent(match[1]) : "";
}

async function request<T>(method: string, path: string, body?: unknown): Promise<T> {
  const headers: Record<string, string> = { "Content-Type": "application/json" };
  if (method !== "GET") {
    headers["X-CSRFToken"] = csrfToken();
  }
  const resp = await fetch(`${BASE}${path}`, {
    method,
    headers,
    credentials: "same-origin",
    body: body === undefined ? undefined : JSON.stringify(body),
  });
  if (!resp.ok) {
    const text = await resp.text();
    throw new Error(`${resp.status}: ${text.slice(0, 300)}`);
  }
  if (resp.status === 204) {
    return undefined as T;
  }
  return (await resp.json()) as T;
}

export const api = {
  list: <T>(path: string): Promise<T[]> => request<T[]>("GET", path),
  get: <T>(path: string): Promise<T> => request<T>("GET", path),
  post: <T>(path: string, body?: unknown): Promise<T> => request<T>("POST", path, body),
  patch: <T>(path: string, body: unknown): Promise<T> => request<T>("PATCH", path, body),
  remove: (path: string): Promise<void> => request<void>("DELETE", path),
};
