/*
 * ASL Ground Truth Annotator — core logic (no DOM dependency).
 *
 * Pure functions for parsing/exporting SRT, importing baseline0 prediction
 * JSON, importing/round-tripping the canonical project JSON, and validating
 * a project's segments. Kept dependency-free and DOM-free so it can be
 * loaded both as a plain <script> in the browser and via require() in Node
 * for automated testing.
 */
(function (global) {
  'use strict';

  // ---- time formatting -----------------------------------------------

  // seconds (float) -> "HH:MM:SS,mmm" (SRT style, comma millis)
  function formatSRTTime(seconds) {
    var totalMs = Math.max(0, Math.round(seconds * 1000));
    var ms = totalMs % 1000;
    var totalSec = Math.floor(totalMs / 1000);
    var s = totalSec % 60;
    var totalMin = Math.floor(totalSec / 60);
    var m = totalMin % 60;
    var h = Math.floor(totalMin / 60);
    function pad(n, w) {
      w = w || 2;
      var str = String(n);
      while (str.length < w) str = '0' + str;
      return str;
    }
    return pad(h) + ':' + pad(m) + ':' + pad(s) + ',' + pad(ms, 3);
  }

  // seconds (float) -> "HH:MM:SS.mmm" (on-screen display, dot millis, to
  // visually distinguish from exported SRT strings)
  function formatClock(seconds) {
    return formatSRTTime(seconds).replace(',', '.');
  }

  // "HH:MM:SS,mmm" or "HH:MM:SS.mmm" -> seconds (float)
  function parseSRTTime(ts) {
    var m = /^(\d+):(\d{2}):(\d{2})[,.](\d{1,3})$/.exec(ts.trim());
    if (!m) throw new Error('Bad SRT timestamp: ' + ts);
    var h = parseInt(m[1], 10);
    var mm = parseInt(m[2], 10);
    var ss = parseInt(m[3], 10);
    var ms = parseInt(m[4].padEnd(3, '0'), 10);
    return h * 3600 + mm * 60 + ss + ms / 1000;
  }

  function round3(n) {
    return Math.round(n * 1000) / 1000;
  }

  // ---- SRT import/export ----------------------------------------------

  // Parses standard SRT text into [{start, end, text}], sorted by start.
  // Does not assign ids or speakers — caller wraps these into canonical form.
  function parseSRT(text) {
    var normalized = text.replace(/\r\n/g, '\n').replace(/\r/g, '\n').trim();
    if (!normalized) return [];
    var blocks = normalized.split(/\n\s*\n/);
    var out = [];
    for (var i = 0; i < blocks.length; i++) {
      var lines = blocks[i].split('\n');
      if (lines.length < 2) continue;
      // lines[0] is the numeric index (ignored, SRT numbering is
      // positional and gets regenerated on export anyway).
      var timeLine = lines[1];
      var tm = /(\d+:\d{2}:\d{2}[,.]\d{1,3})\s*-->\s*(\d+:\d{2}:\d{2}[,.]\d{1,3})/.exec(timeLine);
      if (!tm) {
        // Some SRT variants omit the index line — retry with lines[0].
        tm = /(\d+:\d{2}:\d{2}[,.]\d{1,3})\s*-->\s*(\d+:\d{2}:\d{2}[,.]\d{1,3})/.exec(lines[0]);
        if (!tm) continue;
        out.push({
          start: round3(parseSRTTime(tm[1])),
          end: round3(parseSRTTime(tm[2])),
          text: lines.slice(1).join('\n')
        });
        continue;
      }
      out.push({
        start: round3(parseSRTTime(tm[1])),
        end: round3(parseSRTTime(tm[2])),
        text: lines.slice(2).join('\n')
      });
    }
    out.sort(function (a, b) { return a.start - b.start; });
    return out;
  }

  // [{start, end, text}] -> SRT text, sequential numbering from 1.
  function exportSRT(segments) {
    var sorted = segments.slice().sort(function (a, b) { return a.start - b.start; });
    var blocks = sorted.map(function (seg, i) {
      return (i + 1) + '\n' + formatSRTTime(seg.start) + ' --> ' + formatSRTTime(seg.end) + '\n' + (seg.text || '');
    });
    return blocks.join('\n\n') + '\n';
  }

  // ---- JSON import shape detection ------------------------------------

  // Inspects a parsed JSON object and classifies it.
  // Returns { type: 'canonical' | 'baseline0' | 'nontimed' | 'unknown', ... }
  function classifyImportJSON(obj) {
    if (!obj || typeof obj !== 'object') return { type: 'unknown' };

    if (Array.isArray(obj.segments)) {
      var first = obj.segments[0];
      var looksLikeBaseline0 =
        obj.producer !== undefined ||
        obj.project_id !== undefined ||
        (first && Object.prototype.hasOwnProperty.call(first, 'line'));
      if (looksLikeBaseline0) {
        return { type: 'baseline0' };
      }
      return { type: 'canonical' };
    }

    if (Array.isArray(obj.lines)) {
      var anyTimed = obj.lines.some(function (l) {
        return typeof l.start === 'number' || typeof l.end === 'number';
      });
      if (!anyTimed) return { type: 'nontimed' };
      return { type: 'unknown' };
    }

    return { type: 'unknown' };
  }

  // baseline0 prediction JSON -> canonical-shaped {video, meta, segments}
  function parseBaseline0(obj) {
    var segments = (obj.segments || [])
      .map(function (s) {
        return { start: round3(s.start), end: round3(s.end), text: s.text || '', speaker: null };
      })
      .sort(function (a, b) { return a.start - b.start; })
      .map(function (s, i) { return Object.assign({ id: i + 1 }, s); });
    return {
      video: obj.video || '',
      duration_s: 0,
      meta: {
        gt_kind: 'model',
        source_file: obj.project_id || '',
        verified: false
      },
      warning: obj.warning || '',
      producer: obj.producer || '',
      segments: segments
    };
  }

  // canonical JSON (as previously exported by this tool, or hand-built) ->
  // normalized canonical project object.
  function parseCanonical(obj) {
    var segments = (obj.segments || [])
      .map(function (s) {
        return {
          start: round3(s.start),
          end: round3(s.end),
          text: s.text || '',
          speaker: s.speaker != null ? s.speaker : null
        };
      })
      .sort(function (a, b) { return a.start - b.start; })
      .map(function (s, i) { return Object.assign({ id: i + 1 }, s); });
    return {
      video: obj.video || '',
      duration_s: typeof obj.duration_s === 'number' ? obj.duration_s : 0,
      meta: Object.assign({ gt_kind: 'human', source_file: '', verified: false }, obj.meta || {}),
      segments: segments
    };
  }

  // Non-timestamped reference (e.g. the 1434 shape): returns lines as-is,
  // explicitly NOT as timed segments. Caller must not fabricate timing.
  function parseNontimedReference(obj) {
    return {
      warning: 'Source has no per-line timestamps. Shown as reference only — not loaded as editable segments.',
      duration_s: typeof obj.duration_s === 'number' ? obj.duration_s : null,
      source: obj.source || '',
      title: obj.title || '',
      lines: (obj.lines || []).map(function (l) {
        return { signer: l.signer || null, text: l.text || '', in_clip: l.in_clip !== undefined ? l.in_clip : null };
      })
    };
  }

  // ---- validation -------------------------------------------------------

  // segments: [{id, start, end, text, speaker}], durationS: number|0
  // Returns array of { level: 'error'|'warning', id, message }
  function validateSegments(segments, durationS) {
    var issues = [];
    var sorted = segments.slice().sort(function (a, b) { return a.start - b.start; });

    segments.forEach(function (seg) {
      if (!(seg.end > seg.start)) {
        issues.push({ level: 'error', id: seg.id, message: 'end must be greater than start' });
      }
      if (seg.start < 0) {
        issues.push({ level: 'error', id: seg.id, message: 'start is negative' });
      }
      if (durationS > 0 && seg.end > durationS) {
        issues.push({ level: 'error', id: seg.id, message: 'end exceeds video duration (' + durationS.toFixed(3) + 's)' });
      }
      if (!seg.text || !seg.text.trim()) {
        issues.push({ level: 'warning', id: seg.id, message: 'empty caption text' });
      }
    });

    for (var i = 0; i < sorted.length - 1; i++) {
      if (sorted[i].end > sorted[i + 1].start) {
        issues.push({
          level: 'warning',
          id: sorted[i + 1].id,
          message: 'overlaps with segment #' + sorted[i].id + ' (allowed for multi-signer dialogue)'
        });
      }
    }

    var isSorted = segments.every(function (s, i) { return i === 0 || segments[i - 1].start <= s.start; });
    if (!isSorted) {
      issues.push({ level: 'warning', id: null, message: 'segments are not sorted by start time' });
    }

    return issues;
  }

  // ---- canonical export ---------------------------------------------

  function toCanonicalJSON(project) {
    var sorted = project.segments.slice().sort(function (a, b) { return a.start - b.start; });
    return {
      video: project.video || '',
      duration_s: project.duration_s || 0,
      meta: {
        gt_kind: project.meta.gt_kind || 'human',
        source_file: project.meta.source_file || '',
        verified: !!project.meta.verified
      },
      segments: sorted.map(function (s, i) {
        return {
          id: i + 1,
          start: round3(s.start),
          end: round3(s.end),
          text: s.text || '',
          speaker: s.speaker != null ? s.speaker : null
        };
      })
    };
  }

  var ASLGT = {
    formatSRTTime: formatSRTTime,
    formatClock: formatClock,
    parseSRTTime: parseSRTTime,
    parseSRT: parseSRT,
    exportSRT: exportSRT,
    classifyImportJSON: classifyImportJSON,
    parseBaseline0: parseBaseline0,
    parseCanonical: parseCanonical,
    parseNontimedReference: parseNontimedReference,
    validateSegments: validateSegments,
    toCanonicalJSON: toCanonicalJSON,
    round3: round3
  };

  if (typeof module !== 'undefined' && module.exports) {
    module.exports = ASLGT;
  } else {
    global.ASLGT = ASLGT;
  }
})(typeof window !== 'undefined' ? window : globalThis);
