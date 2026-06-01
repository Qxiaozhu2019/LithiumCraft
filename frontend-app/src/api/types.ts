export type IntelligenceStatus = "active" | "blocked" | "archived";
export type SourceStatus = "enabled" | "disabled" | "manual_only" | "blocked_by_policy";
export type SourceType = "announcement" | "policy" | "media" | "paper" | "patent" | "rss" | "webpage";
export type TaskStatus = "pending" | "running" | "success" | "failed" | "skipped";
export type BriefStatus = "pending" | "success" | "failed";

export interface Page<T> {
  items: T[];
  total: number;
  page: number;
  page_size: number;
}

export interface TokenResponse {
  access_token: string;
  token_type: string;
}

export interface LoginRequest {
  username: string;
  password: string;
}

export interface IntelligenceItem {
  id: number;
  title: string;
  summary: string;
  content_excerpt: string;
  source_url: string;
  source_name: string;
  source_published_at: string | null;
  crawled_at: string;
  category: string;
  tags: string;
  importance_score: number;
  status: IntelligenceStatus;
  block_reason: string | null;
}

export interface IntelligenceQuery {
  q?: string;
  category?: string;
  process_stage?: string;
  status?: IntelligenceStatus | "";
  date_from?: string;
  date_to?: string;
  page?: number;
  page_size?: number;
}

export interface IntelligenceUpdate {
  title?: string;
  summary?: string;
  category?: string;
  tags?: string;
  status?: IntelligenceStatus;
  block_reason?: string | null;
}

export interface DailyBrief {
  id: number;
  brief_date: string;
  title: string;
  overview: string;
  highlights: string;
  category_summary: string;
  status: BriefStatus;
  error_message: string | null;
  generated_at: string | null;
}

export interface Source {
  id: number;
  name: string;
  type: SourceType;
  entry_url: string;
  domain: string;
  status: SourceStatus;
  crawl_interval_minutes: number;
  parser_key: string;
  domain_delay_seconds: number;
  max_pages_per_run: number;
  daily_limit: number;
  failure_count: number;
  last_success_at: string | null;
  last_error: string | null;
  notes: string;
}

export interface SourcePayload {
  name: string;
  type: SourceType;
  entry_url: string;
  domain: string;
  status: SourceStatus;
  crawl_interval_minutes: number;
  parser_key: string;
  domain_delay_seconds: number;
  max_pages_per_run: number;
  daily_limit: number;
  notes: string;
}

export interface CrawlTask {
  id: number;
  task_type: string;
  source_id: number | null;
  status: TaskStatus;
  fetched_count: number;
  inserted_count: number;
  blocked_count: number;
  error_message: string | null;
  duration_ms: number;
  started_at: string | null;
  finished_at: string | null;
}

export interface Category {
  id: number;
  name: string;
  kind: string;
  description: string;
}

export interface Setting {
  id: number;
  key: string;
  value: string;
  description: string;
}

export interface ProcessStage {
  slug: string;
  name: string;
  description: string;
  keywords: string[];
  diagram_steps: string[];
  item_count: number;
  latest_crawled_at: string | null;
}

export interface ProcessImage {
  title: string;
  alt: string;
  image_url: string;
  source_url: string | null;
  source_name: string;
  is_local: boolean;
}

export interface ProcessStageDetail extends ProcessStage {
  items: IntelligenceItem[];
  images: ProcessImage[];
  source_count: number;
}
