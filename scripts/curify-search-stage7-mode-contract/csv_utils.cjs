#!/usr/bin/env node
"use strict";

/** Minimal RFC4180 CSV parser (quoted fields, embedded commas/newlines,
 * doubled-quote escaping) — mirrors the parser already used by
 * scripts/curify-search-collect-stage7/run_mode.cjs, reimplemented here
 * (not imported) since that file is read-only for this stage. */
function parseCsv(text) {
  const rows = [];
  let row = [];
  let field = "";
  let inQuotes = false;
  let i = 0;
  const n = text.length;
  while (i < n) {
    const c = text[i];
    if (inQuotes) {
      if (c === '"') {
        if (text[i + 1] === '"') {
          field += '"';
          i += 2;
          continue;
        }
        inQuotes = false;
        i++;
        continue;
      }
      field += c;
      i++;
      continue;
    }
    if (c === '"') {
      inQuotes = true;
      i++;
      continue;
    }
    if (c === ",") {
      row.push(field);
      field = "";
      i++;
      continue;
    }
    if (c === "\r") {
      i++;
      continue;
    }
    if (c === "\n") {
      row.push(field);
      rows.push(row);
      row = [];
      field = "";
      i++;
      continue;
    }
    field += c;
    i++;
  }
  if (field.length > 0 || row.length > 0) {
    row.push(field);
    rows.push(row);
  }
  const header = rows[0];
  return rows
    .slice(1)
    .filter((r) => r.length > 1 || (r.length === 1 && r[0] !== ""))
    .map((r) => Object.fromEntries(header.map((h, idx) => [h, r[idx] ?? ""])));
}

function csvEscape(v) {
  const s = v === undefined || v === null ? "" : String(v);
  if (/[",\n]/.test(s)) return `"${s.replace(/"/g, '""')}"`;
  return s;
}

function writeCsv(filePath, fieldnames, rows) {
  const fs = require("fs");
  if (fs.existsSync(filePath)) {
    throw new Error(`[csv_utils] refusing to overwrite existing file: ${filePath}`);
  }
  const lines = [fieldnames.join(",")];
  for (const row of rows) {
    lines.push(fieldnames.map((f) => csvEscape(row[f])).join(","));
  }
  fs.writeFileSync(filePath, lines.join("\n") + "\n", "utf-8");
}

module.exports = { parseCsv, writeCsv, csvEscape };
