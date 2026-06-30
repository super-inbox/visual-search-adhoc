export type CurifyQueryStatus =
  | "pending"
  | "running"
  | "ok"
  | "ok_empty"
  | "partial"
  | "error";

export interface QueryItem {
  query_id: number;
  group: string;
  query: string;
}

export interface LabelEntry {
  text: string;
  type: "chip" | "topic" | "filter" | "suggestion" | "unknown";
  href: string;
}

export interface ResultEntry {
  rank: number;
  title: string;
  subtitle: string;
  templateId: string;
  templateName: string;
  href: string;
  imageUrl: string;
  sourceType: "inspiration" | "template" | "unknown";
  visibleText: string;
}

export interface ScreenshotPaths {
  page1: string;
  page2: string;
}

export interface CurifyQueryObservation {
  index: number;
  query: string;
  group: string;
  curifyUrl: string;
  finalUrl: string;
  status: CurifyQueryStatus;
  redirected: boolean;
  redirectType: string;
  capturedAt: string;
  labels: LabelEntry[];
  topResults: ResultEntry[];
  counts: {
    labels: number;
    topResults: number;
  };
  screenshots: ScreenshotPaths;
  notes: string;
  error: string | null;
}

export interface CurifyObservationsFile {
  metadata: {
    surface: "curify_search";
    query_count: number;
    excluded_queries: string[];
    collection_method: string;
    generated_at: string;
    curify_base_url: string;
    viewport: { width: number; height: number };
  };
  queries: CurifyQueryObservation[];
}
