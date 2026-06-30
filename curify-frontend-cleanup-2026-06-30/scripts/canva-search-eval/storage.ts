import * as fs from "fs";
import * as path from "path";
import { fileURLToPath } from "url";
import type { CanvaObservationsFile, CanvaQueryObservation } from "./types.js";
import { CANVA_SEARCH_EVAL_QUERIES } from "./queries.js";
import { VIEWPORT, buildCanvaSearchUrl, CANVA_URL_PATTERN } from "./browser.js";
import { makeSlug } from "./screenshots.js";

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const ROOT = path.resolve(__dirname, "../..");

export const OUT_DIR = path.join(ROOT, "docs/external-signal-pilot/canva-search-eval-58");
export const DATA_DIR = path.join(OUT_DIR, "data");
export const PER_QUERY_DIR = path.join(DATA_DIR, "per-query");
export const OBSERVATIONS_PATH = path.join(DATA_DIR, "observations.json");
export const OBSERVATIONS_CSV_PATH = path.join(DATA_DIR, "observations.csv");
export const PROGRESS_CSV_PATH = path.join(DATA_DIR, "collection_progress.csv");
export const ERRORS_PATH = path.join(DATA_DIR, "collection_errors.json");
export const LOG_PATH = path.join(DATA_DIR, "run.log");
export const SCREENSHOTS_BASE = path.join(OUT_DIR, "screenshots");

// ── Logging ───────────────────────────────────────────────────────────────────

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

// ── observations.json ─────────────────────────────────────────────────────────

export function initObservations(): CanvaObservationsFile {
  if (fs.existsSync(OBSERVATIONS_PATH)) {
    try {
      const raw = fs.readFileSync(OBSERVATIONS_PATH, "utf8");
      return JSON.parse(raw) as CanvaObservationsFile;
    } catch {
      log("WARN", "Could not parse existing observations.json — reinitializing");
    }
  }

  const obs: CanvaObservationsFile = {
    metadata: {
      surface: "canva_search",
      query_count: 58,
      excluded_queries: [],
      collection_method: "playwright_browser",
      generated_at: new Date().toISOString(),
      locale: "en-US",
      viewport: VIEWPORT,
      canva_url_pattern: CANVA_URL_PATTERN,
    },
    queries: CANVA_SEARCH_EVAL_QUERIES.map((q) => ({
      query_id: q.query_id,
      group: q.group,
      query: q.query,
      surface: "canva_search",
      canvaUrl: buildCanvaSearchUrl(q.query),
      finalUrl: "",
      capturedAt: "",
      status: "pending",
      labels: [],
      topResults: [],
      screenshots: { page1: "", page2: "" },
      attempts: 0,
      notes: "",
      error: null,
    })),
  };

  saveObservations(obs);
  return obs;
}

export function saveObservations(obs: CanvaObservationsFile): void {
  fs.mkdirSync(DATA_DIR, { recursive: true });
  const tmp = OBSERVATIONS_PATH + ".tmp";
  const json = JSON.stringify(obs, null, 2);
  JSON.parse(json); // validate before write
  fs.writeFileSync(tmp, json, "utf8");
  fs.renameSync(tmp, OBSERVATIONS_PATH);
}

export function updateQueryObservation(
  obs: CanvaObservationsFile,
  updated: CanvaQueryObservation,
): void {
  const idx = obs.queries.findIndex((q) => q.query_id === updated.query_id);
  if (idx >= 0) obs.queries[idx] = updated;
  saveObservations(obs);
  saveObservationsCsv(obs);
}

// ── collection_progress.csv ───────────────────────────────────────────────────

function csvEscape(val: string | number | boolean | null | undefined): string {
  const s = String(val ?? "");
  if (/[,"\n\r]/.test(s)) return `"${s.replace(/"/g, '""')}"`;
  return s;
}

const PROGRESS_HEADER =
  "query_id,group,query,labels_count,top_results_count,screenshot_page1,screenshot_page2,status,attempts,last_updated,notes";

export function initProgressCsv(obs: CanvaObservationsFile): void {
  fs.mkdirSync(DATA_DIR, { recursive: true });
  const lines = [PROGRESS_HEADER];
  for (const q of obs.queries) lines.push(makeProgressRow(q));
  fs.writeFileSync(PROGRESS_CSV_PATH, lines.join("\n") + "\n", "utf8");
}

function makeProgressRow(q: CanvaQueryObservation): string {
  return [
    q.query_id,
    csvEscape(q.group),
    csvEscape(q.query),
    q.labels.length,
    q.topResults.length,
    csvEscape(q.screenshots.page1),
    csvEscape(q.screenshots.page2),
    csvEscape(q.status),
    q.attempts,
    csvEscape(q.capturedAt || new Date().toISOString()),
    csvEscape(q.notes),
  ].join(",");
}

export function updateProgressCsv(obs: CanvaObservationsFile): void {
  const lines = [PROGRESS_HEADER];
  for (const q of obs.queries) lines.push(makeProgressRow(q));
  fs.writeFileSync(PROGRESS_CSV_PATH, lines.join("\n") + "\n", "utf8");
}

// ── observations.csv (final output format) ────────────────────────────────────

const OBS_CSV_HEADER =
  "index,query,status,canvaUrl,finalUrl,labelsCount,topResultsCount," +
  "top1Title,top1TemplateUrl,top1PageUrl,top2Title,top2TemplateUrl,top2PageUrl," +
  "screenshotPage1,screenshotPage2,notes";

function makeObsCsvRow(q: CanvaQueryObservation): string {
  const top1 = q.topResults[0];
  const top2 = q.topResults[1];
  return [
    q.query_id,
    csvEscape(q.query),
    csvEscape(q.status),
    csvEscape(q.canvaUrl),
    csvEscape(q.finalUrl),
    q.labels.length,
    q.topResults.length,
    csvEscape(top1?.title ?? ""),
    csvEscape(top1?.templateUrl ?? ""),
    csvEscape(top1?.pageUrl ?? ""),
    csvEscape(top2?.title ?? ""),
    csvEscape(top2?.templateUrl ?? ""),
    csvEscape(top2?.pageUrl ?? ""),
    csvEscape(q.screenshots.page1),
    csvEscape(q.screenshots.page2),
    csvEscape(q.notes),
  ].join(",");
}

export function saveObservationsCsv(obs: CanvaObservationsFile): void {
  const lines = [OBS_CSV_HEADER];
  for (const q of obs.queries) lines.push(makeObsCsvRow(q));
  fs.writeFileSync(OBSERVATIONS_CSV_PATH, lines.join("\n") + "\n", "utf8");
}

// ── collection_errors.json ────────────────────────────────────────────────────

export interface ErrorEntry {
  query_id: number;
  query: string;
  stage: string;
  message: string;
  stack: string;
  timestamp: string;
  screenshot: string;
}

function loadErrors(): ErrorEntry[] {
  if (fs.existsSync(ERRORS_PATH)) {
    try { return JSON.parse(fs.readFileSync(ERRORS_PATH, "utf8")) as ErrorEntry[]; } catch { return []; }
  }
  return [];
}

export function appendError(entry: ErrorEntry): void {
  const errors = loadErrors();
  errors.push(entry);
  fs.writeFileSync(ERRORS_PATH, JSON.stringify(errors, null, 2), "utf8");
}

// ── per-query JSON ─────────────────────────────────────────────────────────────

export function savePerQueryJson(q: CanvaQueryObservation): void {
  fs.mkdirSync(PER_QUERY_DIR, { recursive: true });
  const slug = makeSlug(q.query, q.query_id);
  const fileName = `${String(q.query_id).padStart(3, "0")}-${slug}.json`;
  const filePath = path.join(PER_QUERY_DIR, fileName);

  const doc = {
    index: q.query_id,
    query: q.query,
    canvaUrl: q.canvaUrl,
    finalUrl: q.finalUrl,
    status: q.status,
    capturedAt: q.capturedAt,
    labels: q.labels,
    topResults: q.topResults,
    counts: {
      labels: q.labels.length,
      topResults: q.topResults.length,
    },
    screenshots: {
      page1: q.screenshots.page1,
      page2: q.screenshots.page2,
    },
    notes: q.notes || q.error || "",
  };

  fs.writeFileSync(filePath, JSON.stringify(doc, null, 2), "utf8");
}
