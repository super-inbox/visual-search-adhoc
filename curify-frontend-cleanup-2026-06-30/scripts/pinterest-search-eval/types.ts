export type PinterestQueryStatus =
  | "pending"
  | "running"
  | "ok"
  | "ok_empty"
  | "blocked"
  | "login_required"
  | "captcha"
  | "error"
  | "partial";

export interface QueryItem {
  query_id: number;
  group: string;
  query: string;
}

export interface PinterestLabel {
  text: string;
  href: string;
  type: "chip" | "related" | "filter" | "unknown";
}

export interface PinterestPinResult {
  rank: number;
  title: string;
  description: string;
  source: string;
  pinUrl: string;
  pageUrl: string;
  imageUrl: string;
  thumbnailUrl: string;
  visibleText: string;
}

export interface PinterestQueryObservation {
  query_id: number;
  group: string;
  query: string;
  surface: "pinterest_search";
  pinterestUrl: string;
  finalUrl: string;
  capturedAt: string;
  status: PinterestQueryStatus;
  labels: PinterestLabel[];
  topResults: PinterestPinResult[];
  screenshots: { page1: string; page2: string };
  attempts: number;
  notes: string;
  error: string | null;
}

export interface PinterestObservationsFile {
  metadata: {
    surface: "pinterest_search";
    query_count: number;
    excluded_queries: string[];
    collection_method: string;
    generated_at: string;
    locale: string;
    viewport: { width: number; height: number };
  };
  queries: PinterestQueryObservation[];
}
