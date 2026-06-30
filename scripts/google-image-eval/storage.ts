import * as fs from "fs";
import * as path from "path";
import { fileURLToPath } from "url";
import type { ObservationsFile, QueryObservation, ErrorEntry } from "./types.js";
import { GOOGLE_IMAGE_EVAL_QUERIES } from "./queries.js";
import { VIEWPORT } from "./browser.js";

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const ROOT = path.resolve(__dirname, "../..");
export const OUT_DIR = path.join(ROOT, "docs/external-signal-pilot/google-image-eval-58");
export const DATA_DIR = path.join(OUT_DIR, "data");
export const PER_QUERY_DIR = path.join(DATA_DIR, "per-query");
export const OBSERVATIONS_PATH = path.join(DATA_DIR, "observations.json");
export const PROGRESS_CSV_PATH = path.join(DATA_DIR, "collection_progress.csv");
export const ERRORS_PATH = path.join(DATA_DIR, "collection_errors.json");
export const LOG_PATH = path.join(DATA_DIR, "run.log");

// ── Logging ──────────────────────────────────────────────────────────────────

let logStream: fs.WriteStream | null = null;

export function initLog(): void {
  fs.mkdirSync(DATA_DIR, { recursive: true });
  fs.mkdirSync(PER_QUERY_DIR, { recursive: true });
  logStream = fs.createWriteStream(LOG_PATH, { flags: "a" });
}

export function log(level: "INFO" | "WARN" | "ERROR", ...parts: unknown[]): void {
  const msg = `[${new Date().toISOString()}] ${level} ${parts.join(" ")}`;
  if (level === "ERROR") console.error(msg);
  else if (level === "WARN") console.warn(msg);
  else console.log(msg);
  logStream?.write(msg + "\n");
}

// ── observations.json ────────────────────────────────────────────────────────

export function initObservations(): ObservationsFile {
  if (fs.existsSync(OBSERVATIONS_PATH)) {
    try {
      const raw = fs.readFileSync(OBSERVATIONS_PATH, "utf8");
      return JSON.parse(raw) as ObservationsFile;
    } catch {
      log("WARN", "Could not parse existing observations.json — reinitializing");
    }
  }

  const obs: ObservationsFile = {
    metadata: {
      surface: "google_images",
      query_count: 58,
      excluded_queries: [],
      collection_method: "playwright_browser",
      generated_at: new Date().toISOString(),
      locale: "en-US",
      viewport: VIEWPORT,
    },
    queries: GOOGLE_IMAGE_EVAL_QUERIES.map((q) => ({
      query_id: q.query_id,
      group: q.group,
      query: q.query,
      surface: "google_images",
      search_url: "",
      captured_at: "",
      labels: [],
      top10: [],
      screenshots: [],
      status: "pending",
      attempts: 0,
      query_notes: "",
      error: null,
    })),
  };

  saveObservations(obs);
  return obs;
}

export function saveObservations(obs: ObservationsFile): void {
  fs.mkdirSync(DATA_DIR, { recursive: true });
  const tmp = OBSERVATIONS_PATH + ".tmp";
  const json = JSON.stringify(obs, null, 2);
  // Verify JSON is valid before writing
  JSON.parse(json);
  fs.writeFileSync(tmp, json, "utf8");
  fs.renameSync(tmp, OBSERVATIONS_PATH);
}

export function updateQueryObservation(
  obs: ObservationsFile,
  updated: QueryObservation,
): void {
  const idx = obs.queries.findIndex((q) => q.query_id === updated.query_id);
  if (idx >= 0) {
    obs.queries[idx] = updated;
  }
  saveObservations(obs);
}

// ── collection_progress.csv ──────────────────────────────────────────────────

function csvEscape(val: string | number): string {
  const s = String(val);
  if (/[,"\n\r]/.test(s)) {
    return `"${s.replace(/"/g, '""')}"`;
  }
  return s;
}

const CSV_HEADER = "query_id,group,query,labels_count,top10_count,screenshot_count,status,attempts,last_updated,notes";

export function initProgressCsv(obs: ObservationsFile): void {
  fs.mkdirSync(DATA_DIR, { recursive: true });
  const lines = [CSV_HEADER];
  for (const q of obs.queries) {
    lines.push(makeProgressRow(q));
  }
  fs.writeFileSync(PROGRESS_CSV_PATH, lines.join("\n") + "\n", "utf8");
}

function makeProgressRow(q: QueryObservation): string {
  const cols = [
    q.query_id,
    csvEscape(q.group),
    csvEscape(q.query),
    q.labels.length,
    q.top10.length,
    q.screenshots.length,
    csvEscape(q.status),
    q.attempts,
    csvEscape(q.captured_at || new Date().toISOString()),
    csvEscape(q.query_notes || ""),
  ];
  return cols.join(",");
}

export function updateProgressCsv(obs: ObservationsFile): void {
  const lines = [CSV_HEADER];
  for (const q of obs.queries) {
    lines.push(makeProgressRow(q));
  }
  fs.writeFileSync(PROGRESS_CSV_PATH, lines.join("\n") + "\n", "utf8");
}

// ── collection_errors.json ───────────────────────────────────────────────────

export function loadErrors(): ErrorEntry[] {
  if (fs.existsSync(ERRORS_PATH)) {
    try {
      return JSON.parse(fs.readFileSync(ERRORS_PATH, "utf8")) as ErrorEntry[];
    } catch {
      return [];
    }
  }
  return [];
}

export function appendError(entry: ErrorEntry): void {
  const errors = loadErrors();
  errors.push(entry);
  fs.writeFileSync(ERRORS_PATH, JSON.stringify(errors, null, 2), "utf8");
}

// ── per-query JSON ────────────────────────────────────────────────────────────

function makeQuerySlug(query: string, queryId: number): string {
  const ascii = query
    .toLowerCase()
    .replace(/[^a-z0-9]+/g, "-")
    .replace(/^-|-$/g, "")
    .slice(0, 40);
  return ascii.length >= 2 ? ascii : `q${String(queryId).padStart(3, "0")}`;
}

export function savePerQueryJson(q: QueryObservation): void {
  fs.mkdirSync(PER_QUERY_DIR, { recursive: true });
  const slug = makeQuerySlug(q.query, q.query_id);
  const fileName = `${String(q.query_id).padStart(3, "0")}-${slug}.json`;
  const filePath = path.join(PER_QUERY_DIR, fileName);

  const [page1 = "", page2 = ""] = q.screenshots;
  const perQueryDoc = {
    index: q.query_id,
    query: q.query,
    googleUrl: q.search_url,
    status: q.status === "complete" ? "ok" : q.status,
    capturedAt: q.captured_at,
    labels: q.labels,
    topResults: q.top10.map((r) => ({
      rank: r.rank,
      title: r.title,
      source: r.source,
      pageUrl: r.page_url,
      imageUrl: r.image_url,
    })),
    screenshots: { page1, page2 },
    notes: q.query_notes || (q.error ?? ""),
  };

  fs.writeFileSync(filePath, JSON.stringify(perQueryDoc, null, 2), "utf8");
}
