export type QueryStatus =
  | "pending"
  | "running"
  | "complete"
  | "partial"
  | "captcha"
  | "failed";

export interface QueryItem {
  query_id: number;
  group: string;
  query: string;
}

export interface ImageResult {
  rank: number;
  title: string;
  source: string;
  page_url: string;
  image_url: string;
  thumbnail_url: string;
  result_type: "organic";
  notes: string;
}

export interface QueryObservation {
  query_id: number;
  group: string;
  query: string;
  surface: "google_images";
  search_url: string;
  captured_at: string;
  labels: string[];
  top10: ImageResult[];
  screenshots: string[];
  status: QueryStatus;
  attempts: number;
  query_notes: string;
  error: string | null;
}

export interface ObservationsFile {
  metadata: {
    surface: "google_images";
    query_count: number;
    excluded_queries: string[];
    collection_method: string;
    generated_at: string;
    locale: string;
    viewport: { width: number; height: number };
  };
  queries: QueryObservation[];
}

export interface ErrorEntry {
  query_id: number;
  query: string;
  stage: ErrorStage;
  message: string;
  stack: string;
  timestamp: string;
  screenshot: string;
}

export type ErrorStage =
  | "open_page"
  | "consent"
  | "captcha"
  | "extract_labels"
  | "extract_candidates"
  | "visual_sort"
  | "extract_top10"
  | "click_preview"
  | "take_screenshot"
  | "save_data"
  | "validation";

export interface BoundingBox {
  x: number;
  y: number;
  width: number;
  height: number;
}

export interface ImageCandidate {
  element: import("playwright").ElementHandle;
  bbox: BoundingBox;
  thumbnail_url: string;
}
