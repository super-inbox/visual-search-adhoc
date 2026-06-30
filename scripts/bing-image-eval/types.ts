export type BingQueryStatus =
  | "pending"
  | "running"
  | "ok"
  | "ok_empty"
  | "blocked"
  | "error"
  | "partial";

export interface QueryItem {
  query_id: number;
  group: string;
  query: string;
}

export interface BingLabel {
  text: string;
  href: string;
  type: "chip" | "related" | "filter" | "unknown";
}

export interface BingImageResult {
  rank: number;
  title: string;
  source: string;
  pageUrl: string;
  imageUrl: string;
  thumbnailUrl: string;
  visibleText: string;
}

export interface BingQueryObservation {
  query_id: number;
  group: string;
  query: string;
  surface: "bing_images";
  bingUrl: string;
  finalUrl: string;
  capturedAt: string;
  status: BingQueryStatus;
  labels: BingLabel[];
  topResults: BingImageResult[];
  screenshots: { page1: string; page2: string };
  attempts: number;
  notes: string;
  error: string | null;
}

export interface BingObservationsFile {
  metadata: {
    surface: "bing_images";
    query_count: number;
    excluded_queries: string[];
    collection_method: string;
    generated_at: string;
    locale: string;
    viewport: { width: number; height: number };
  };
  queries: BingQueryObservation[];
}
