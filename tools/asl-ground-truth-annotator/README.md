# ASL Ground Truth Annotator

A small local, browser-based tool for creating and correcting timestamped
English ground truth for ASL videos in `data/asl_corpus/`.

## Privacy — read this first

**Local-only annotation. Video and ground truth files stay on this machine.**

This tool is a static HTML/CSS/JS page with no build step, no server-side
component, and no network calls of any kind — no `fetch`, no XHR, no
WebSocket, no external `<script>`/`<link>` sources. Videos are loaded via
`<input type="file">` and read straight into the browser as a local
`blob:` URL; imports are read via the File API; exports are generated
in-memory and handed to the browser's normal file-save flow. Nothing is
uploaded anywhere, and the page works the same with Wi-Fi off.

`data/asl_corpus/` contains identifiable real-user video from a paid
product (see `data/asl_corpus/README.md`). Do not point any other tool,
script, or service at these files.

## Launch

From the repo root:

```
python3 -m http.server 8934 --bind 127.0.0.1 -d tools/asl-ground-truth-annotator
```

then open **http://127.0.0.1:8934/index.html** in a browser. `--bind
127.0.0.1` keeps the server on loopback only — it is not reachable from
the network.

A local static server is used instead of opening `index.html` directly as
a `file://` URL because Chrome's file-upload security model interacts
poorly with automation/extensions on `file://` pages in some setups; the
app itself makes no network calls either way, so `python3 -m http.server`
here is just a local file server, not a network dependency. If you prefer,
opening `index.html` directly by double-clicking it also works in most
browsers — try that first if you don't want to run a command.

Stop the server with `Ctrl+C` when done.

## Workflow

1. **Load video…** — pick the matching `.mp4` from
   `data/asl_corpus/videos/`. The `video` field auto-fills as
   `videos/<filename>` (edit if needed — it's just a label recorded in
   the exported JSON, not a filesystem path the tool resolves).
2. Either **Import SRT/JSON…** an existing reference/prediction to start
   from, or click **+ Add segment (at playhead)** to start from scratch.
3. Play/scrub to the right moment, use **Start←** / **End←** (or the
   `S`/`E` keys) on the segment row to set precise in/out points, type
   the English caption, repeat.
4. **Export SRT** and/or **Export JSON** when done. Exporting also clears
   the "Unsaved changes" indicator.

## Import behavior

The importer inspects file extension and JSON shape and picks one of:

- **`.srt`** — standard SubRip. Cues become editable segments
  (`gt_kind` defaults to `human`, `speaker` unset).
- **Baseline-0 prediction JSON** (`{project_id, video, producer, warning,
  segments:[{line,start,end,text}]}`) — converted to editable segments,
  `gt_kind` set to `model`, and the model's own `warning` string is
  surfaced as a toast so you don't lose that context.
- **Canonical JSON** (this tool's own export shape, or anything with a
  top-level `segments` array of `{start,end,text}` and no `producer`/
  `project_id`/`line`) — reopens a full project, including `meta`.
- **Non-timestamped reference** (e.g. `1434_screenrec_youtube_16.6s.json`,
  which has `lines: [{signer, text, in_clip}]` with no `start`/`end`) —
  **not** imported as segments. The tool refuses to fabricate timing for
  untimed source data; instead it shows a clear warning banner and lists
  the lines read-only in a side panel, so you can still see the content
  while transcribing it manually against the video.

Anything else (unparseable JSON, empty SRT) surfaces an error toast and
changes nothing.

## Export

- **SRT**: sequential numbering from 1, `HH:MM:SS,mmm` timestamps,
  multiline caption text preserved, sorted by start time.
- **JSON**: the canonical shape —
  `{video, duration_s, meta:{gt_kind, source_file, verified}, segments:[{id,start,end,text,speaker}]}`,
  segments sorted by start and renumbered 1..n. `duration_s` comes from
  the loaded video's actual duration.

Internally all times are floats in seconds, edited/stored at millisecond
precision (3 decimal places).

## Keyboard shortcuts

Shortcuts are disabled while a text field/button has focus (so typing a
caption never triggers them), except `Esc`, which blurs the current field.

| Key | Action |
|---|---|
| `Space` | Play / pause |
| `←` / `→` | Seek −0.5s / +0.5s |
| `Shift+←` / `Shift+→` | Seek −0.05s / +0.05s (fine step) |
| `S` | Set the **selected** row's start = current playhead |
| `E` | Set the **selected** row's end = current playhead |
| `A` | Add a new segment at the current playhead |
| `Delete` / `Backspace` | Delete the selected row |
| `Esc` | Clear focus / dismiss the current field |

Click anywhere on a segment row to select it before using `S`/`E`/`Delete`.
There is no true frame-step API available to a plain HTML5 `<video>`
across browsers, so the "fine step" is a fixed 0.05s jump rather than an
exact single-frame seek — precise enough for subtitle-style annotation,
but note this if you need exact frame boundaries on very high-fps source.

## Validation

Shown live above the segment table and per-row:

- **Errors** (red row): `end <= start`, `start < 0`, or `end` beyond the
  loaded video's duration.
- **Warnings** (yellow): empty caption text, segments not sorted by
  start (auto-corrected by the tool in practice), and **overlapping
  segments** — overlap is flagged but never blocks export, since
  multi-signer dialogue can legitimately overlap.

If no video is loaded yet, end-of-clip bounds can't be checked and the
summary says so.

## Recommended workflow for new ground truth

1. Load the video, watch it once at normal speed to get the gist.
2. Scrub back to the start, add the first segment (`A`), play through the
   first utterance, hit `E` (or click **End←**) right as it finishes,
   type the English caption.
3. Continue with `A` (new segment starts at the current playhead,
   already positioned right after the previous end) → play → `E` → type.
4. Use `Shift+←`/`Shift+→` to nudge boundaries precisely once you're
   close.
5. Before exporting, check the validation summary is clean (or that any
   warnings are expected/intentional, e.g. real overlap), set `gt_kind`
   to `human` and check `verified` once you've reviewed the full pass.
6. Export both SRT (for quick diffing/eyeballing) and JSON (for
   evaluation tooling) into `data/asl_corpus/ground_truth/`.

## Known limitations

- No true per-frame seeking (browsers don't expose a reliable
  cross-browser frame-step API on `<video>`); fine-step is a fixed 0.05s.
- No autosave/undo — export regularly, and treat the "Unsaved changes"
  indicator as the guardrail (a native "leave page?" prompt also fires on
  tab close/navigate while unsaved).
- Single-video, single-annotator, single-session by design (no project
  list, no database, no auth, no collaboration) — this is intentionally
  out of scope for the MVP.
- Speaker labels are free-text, not validated against a fixed roster.
