import * as fs from "fs";
import * as path from "path";
import { fileURLToPath } from "url";
import type { CurifyObservationsFile, CurifyQueryObservation } from "./types.js";
import { CURIFY_SEARCH_EVAL_QUERIES } from "./queries.js";
import { VIEWPORT, getCurifyBaseUrl } from "./browser.js";

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const ROOT = path.resolve(__dirname, "../..");

export const OUT_DIR = path.join(ROOT, "docs/external-signal-pilot/curify-search-eval-58");
export const DATA_DIR = path.join(OUT_DIR, "data");
export const PER_QUERY_DIR = path.join(DATA_DIR, "per-query");
export const OBSERVATIONS_PATH = path.join(DATA_DIR, "observations.json");
export const OBSERVATIONS_CSV_PATH = path.join(DATA_DIR, "observations.csv");
export const PROGRESS_CSV_PATH = path.join(DATA_DIR, "collection_progress.csv");
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

export function initObservations(): CurifyObservationsFile {
  if (fs.existsSync(OBSERVATIONS_PATH)) {
    try {
      const raw = fs.readFileSync(OBSERVATIONS_PATH, "utf8");
      return JSON.parse(raw) as CurifyObservationsFile;
    } catch {
      log("WARN", "Could not parse existing observations.json — reinitializing");
    }
  }

  const obs: CurifyObservationsFile = {
    metadata: {
      surface: "curify_search",
      query_count: 58,
      excluded_queries: [],
      collection_method: "playwright_browser",
      generated_at: new Date().toISOString(),
      curify_base_url: getCurifyBaseUrl(),
      viewport: VIEWPORT,
    },
    queries: CURIFY_SEARCH_EVAL_QUERIES.map((q) => ({
      index: q.query_id,
      query: q.query,
      group: q.group,
      curifyUrl: "",
      finalUrl: "",
      status: "pending",
      redirected: false,
      redirectType: "",
      capturedAt: "",
      labels: [],
      topResults: [],
      counts: { labels: 0, topResults: 0 },
      screenshots: { page1: "", page2: "" },
      notes: "",
      error: null,
    })),
  };

  saveObservations(obs);
  return obs;
}

export function saveObservations(obs: CurifyObservationsFile): void {
  fs.mkdirSync(DATA_DIR, { recursive: true });
  const tmp = OBSERVATIONS_PATH + ".tmp";
  const json = JSON.stringify(obs, null, 2);
  JSON.parse(json); // validate before write
  fs.writeFileSync(tmp, json, "utf8");
  fs.renameSync(tmp, OBSERVATIONS_PATH);
}

export function updateQueryObservation(
  obs: CurifyObservationsFile,
  updated: CurifyQueryObservation,
): void {
  const idx = obs.queries.findIndex((q) => q.index === updated.index);
  if (idx >= 0) {
    obs.queries[idx] = updated;
  }
  saveObservations(obs);
}

// ── collection_progress.csv (lightweight progress tracker) ─────────────────

const PROGRESS_HEADER = "index,query,status,redirected,redirectType,labelsCount,topResultsCount,capturedAt,notes";

function csvEscape(val: string | number | boolean): string {
  const s = String(val);
  if (/[,"\n\r]/.test(s)) return `"${s.replace(/"/g, '""')}"`;
  return s;
}

function makeProgressRow(q: CurifyQueryObservation): string {
  return [
    q.index,
    csvEscape(q.query),
    csvEscape(q.status),
    q.redirected,
    csvEscape(q.redirectType),
    q.counts.labels,
    q.counts.topResults,
    csvEscape(q.capturedAt || ""),
    csvEscape(q.notes || ""),
  ].join(",");
}

export function initProgressCsv(obs: CurifyObservationsFile): void {
  fs.mkdirSync(DATA_DIR, { recursive: true });
  const lines = [PROGRESS_HEADER];
  for (const q of obs.queries) lines.push(makeProgressRow(q));
  fs.writeFileSync(PROGRESS_CSV_PATH, lines.join("\n") + "\n", "utf8");
}

export function updateProgressCsv(obs: CurifyObservationsFile): void {
  const lines = [PROGRESS_HEADER];
  for (const q of obs.queries) lines.push(makeProgressRow(q));
  fs.writeFileSync(PROGRESS_CSV_PATH, lines.join("\n") + "\n", "utf8");
}

// ── observations.csv (full export for side-by-side analysis) ───────────────

const OBS_CSV_HEADER = [
  "index", "query", "status", "redirected", "redirectType",
  "curifyUrl", "finalUrl", "labelsCount", "topResultsCount",
  "top1Title", "top1Href", "top2Title", "top2Href",
  "screenshotPage1", "screenshotPage2", "notes",
].join(",");

function makeObsRow(q: CurifyQueryObservation): string {
  const top1 = q.topResults[0];
  const top2 = q.topResults[1];
  return [
    q.index,
    csvEscape(q.query),
    csvEscape(q.status),
    q.redirected,
    csvEscape(q.redirectType),
    csvEscape(q.curifyUrl),
    csvEscape(q.finalUrl),
    q.counts.labels,
    q.counts.topResults,
    csvEscape(top1?.title ?? ""),
    csvEscape(top1?.href ?? ""),
    csvEscape(top2?.title ?? ""),
    csvEscape(top2?.href ?? ""),
    csvEscape(q.screenshots.page1),
    csvEscape(q.screenshots.page2),
    csvEscape(q.notes || q.error || ""),
  ].join(",");
}

export function saveObservationsCsv(obs: CurifyObservationsFile): void {
  const lines = [OBS_CSV_HEADER];
  for (const q of obs.queries) lines.push(makeObsRow(q));
  fs.writeFileSync(OBSERVATIONS_CSV_PATH, lines.join("\n") + "\n", "utf8");
}

// ── per-query JSON ─────────────────────────────────────────────────────────

export function makeQuerySlug(query: string, queryId: number): string {
  const ascii = query
    .toLowerCase()
    .replace(/[^a-z0-9]+/g, "-")
    .replace(/^-|-$/g, "")
    .slice(0, 40);
  return ascii.length >= 2 ? ascii : `q${String(queryId).padStart(3, "0")}`;
}

export function getPerQueryPath(queryId: number, query: string): string {
  const slug = makeQuerySlug(query, queryId);
  return path.join(PER_QUERY_DIR, `${String(queryId).padStart(3, "0")}-${slug}.json`);
}

export function savePerQueryJson(q: CurifyQueryObservation): void {
  fs.mkdirSync(PER_QUERY_DIR, { recursive: true });
  const filePath = getPerQueryPath(q.index, q.query);
  const doc: CurifyQueryObservation = { ...q };
  fs.writeFileSync(filePath, JSON.stringify(doc, null, 2), "utf8");
}
