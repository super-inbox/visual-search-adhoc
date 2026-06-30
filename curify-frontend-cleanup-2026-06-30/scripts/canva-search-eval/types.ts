export type CanvaQueryStatus =
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

export interface CanvaLabel {
  text: string;
  href: string;
  type: "chip" | "filter" | "category" | "related" | "unknown";
}

export interface CanvaTemplateResult {
  rank: number;
  title: string;
  description: string;
  source: "Canva";
  templateUrl: string;
  pageUrl: string;
  imageUrl: string;
  thumbnailUrl: string;
  visibleText: string;
  isPro: boolean;
}

export interface CanvaQueryObservation {
  query_id: number;
  group: string;
  query: string;
  surface: "canva_search";
  canvaUrl: string;
  finalUrl: string;
  capturedAt: string;
  status: CanvaQueryStatus;
  labels: CanvaLabel[];
  topResults: CanvaTemplateResult[];
  screenshots: { page1: string; page2: string };
  attempts: number;
  notes: string;
  error: string | null;
}

export interface CanvaObservationsFile {
  metadata: {
    surface: "canva_search";
    query_count: number;
    excluded_queries: string[];
    collection_method: string;
    generated_at: string;
    locale: string;
    viewport: { width: number; height: number };
    canva_url_pattern: string;
  };
  queries: CanvaQueryObservation[];
}
