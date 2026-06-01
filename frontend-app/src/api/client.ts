import type {
  Category,
  CrawlTask,
  DailyBrief,
  IntelligenceItem,
  IntelligenceQuery,
  IntelligenceUpdate,
  LoginRequest,
  Page,
  ProcessStage,
  ProcessStageDetail,
  Setting,
  Source,
  SourcePayload,
  Topic,
  TopicDetail,
  TokenResponse
} from "./types";

const TOKEN_KEY = "lithiumcraft.token";
const API_BASE = (import.meta.env.VITE_API_BASE || "/api/v1").replace(/\/$/, "");

interface ApiOptions extends RequestInit {
  auth?: boolean;
  params?: Record<string, string | number | boolean | null | undefined>;
}

export class ApiError extends Error {
  status: number;
  details: unknown;

  constructor(message: string, status: number, details: unknown) {
    super(message);
    this.name = "ApiError";
    this.status = status;
    this.details = details;
  }
}

export function readToken(): string | null {
  return localStorage.getItem(TOKEN_KEY);
}

export function saveToken(token: string) {
  localStorage.setItem(TOKEN_KEY, token);
}

export function clearToken() {
  localStorage.removeItem(TOKEN_KEY);
}

function buildUrl(path: string, params?: ApiOptions["params"]) {
  const url = new URL(`${API_BASE}${path.startsWith("/") ? path : `/${path}`}`, window.location.origin);
  Object.entries(params || {}).forEach(([key, value]) => {
    if (value !== undefined && value !== null && value !== "") {
      url.searchParams.set(key, String(value));
    }
  });
  return url.toString();
}

async function parseResponse(response: Response) {
  const contentType = response.headers.get("content-type") || "";
  if (contentType.includes("application/json")) {
    return response.json();
  }
  return response.text();
}

export async function apiRequest<T>(path: string, options: ApiOptions = {}): Promise<T> {
  const { auth = true, params, headers, ...fetchOptions } = options;
  const token = readToken();
  const requestHeaders = new Headers(headers);

  if (!requestHeaders.has("Content-Type") && fetchOptions.body) {
    requestHeaders.set("Content-Type", "application/json");
  }
  if (auth && token) {
    requestHeaders.set("Authorization", `Bearer ${token}`);
  }

  const response = await fetch(buildUrl(path, params), {
    ...fetchOptions,
    headers: requestHeaders
  });
  const payload = await parseResponse(response);

  if (!response.ok) {
    if (response.status === 401 && auth) {
      clearToken();
      const redirect = encodeURIComponent(window.location.pathname + window.location.search);
      window.location.assign(`/login?redirect=${redirect}`);
    }
    const message = typeof payload === "object" && payload && "message" in payload
      ? String((payload as { message: unknown }).message)
      : typeof payload === "object" && payload && "detail" in payload
        ? String((payload as { detail: unknown }).detail)
        : response.statusText;
    throw new ApiError(message, response.status, payload);
  }

  return payload as T;
}

export function login(payload: LoginRequest) {
  return apiRequest<TokenResponse>("/auth/login", {
    method: "POST",
    auth: false,
    body: JSON.stringify(payload)
  });
}

export function listIntelligence(query: IntelligenceQuery = {}) {
  return apiRequest<Page<IntelligenceItem>>("/intelligence", { params: { ...query } });
}

export function getIntelligence(id: number) {
  return apiRequest<IntelligenceItem>(`/intelligence/${id}`);
}

export function listProcessStages() {
  return apiRequest<ProcessStage[]>("/processes");
}

export function getProcessStage(slug: string, pageSize = 20) {
  return apiRequest<ProcessStageDetail>(`/processes/${encodeURIComponent(slug)}`, {
    params: { page_size: pageSize }
  });
}

export function listTopics() {
  return apiRequest<Topic[]>("/topics");
}

export function getTopic(slug: string, pageSize = 20) {
  return apiRequest<TopicDetail>(`/topics/${encodeURIComponent(slug)}`, {
    params: { page_size: pageSize }
  });
}

export function updateIntelligence(id: number, payload: IntelligenceUpdate) {
  return apiRequest<IntelligenceItem>(`/intelligence/${id}`, {
    method: "PATCH",
    body: JSON.stringify(payload)
  });
}

export function listDailyBriefs(page = 1, pageSize = 20) {
  return apiRequest<Page<DailyBrief>>("/daily-briefs", { params: { page, page_size: pageSize } });
}

export function getDailyBrief(date: string) {
  return apiRequest<DailyBrief>(`/daily-briefs/${date}`);
}

export function generateDailyBrief(targetDate?: string) {
  return apiRequest<DailyBrief>("/daily-briefs/generate", {
    method: "POST",
    params: { target_date: targetDate }
  });
}

export function listSources(page = 1, pageSize = 50) {
  return apiRequest<Page<Source>>("/sources", { params: { page, page_size: pageSize } });
}

export function createSource(payload: SourcePayload) {
  return apiRequest<Source>("/sources", {
    method: "POST",
    body: JSON.stringify(payload)
  });
}

export function updateSource(id: number, payload: Partial<SourcePayload>) {
  return apiRequest<Source>(`/sources/${id}`, {
    method: "PATCH",
    body: JSON.stringify(payload)
  });
}

export function listCrawlTasks(page = 1, pageSize = 20) {
  return apiRequest<Page<CrawlTask>>("/crawl-tasks", { params: { page, page_size: pageSize } });
}

export function triggerCrawl(sourceId: number) {
  return apiRequest<{
    task_id: number;
    source_id: number;
    status: string;
    fetched_count: number;
    inserted_count: number;
    blocked_count: number;
    message: string;
  }>("/crawl-tasks", {
    method: "POST",
    params: { source_id: sourceId }
  });
}

export function triggerEnabledSourcesCrawl() {
  return apiRequest<{ source_count: number; tasks: Array<{ task_id: number; status: string }>; message: string }>("/crawl-tasks/enabled", {
    method: "POST"
  });
}

export function listCategories() {
  return apiRequest<Category[]>("/categories");
}

export function listSettings() {
  return apiRequest<Setting[]>("/settings");
}

export function updateSetting(key: string, value: string) {
  return apiRequest<Setting>(`/settings/${encodeURIComponent(key)}`, {
    method: "PATCH",
    body: JSON.stringify({ value })
  });
}
