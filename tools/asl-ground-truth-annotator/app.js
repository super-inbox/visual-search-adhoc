/*
 * ASL Ground Truth Annotator — DOM wiring.
 *
 * Everything here operates on in-memory state and local File/Blob APIs
 * only. There must be no fetch/XMLHttpRequest/WebSocket calls anywhere in
 * this file — the tool is local-only by construction, not just by policy.
 */
(function () {
  'use strict';

  var uidCounter = 1;
  function newUid() { return uidCounter++; }

  var project = {
    video: '',
    duration_s: 0,
    meta: { gt_kind: 'human', source_file: '', verified: false },
    segments: []
  };
  var dirty = false;
  var selectedUid = null;
  var currentVideoUrl = null;

  // ---- DOM refs ---------------------------------------------------------

  var video = document.getElementById('video');
  var seekBar = document.getElementById('seekBar');
  var btnPlayPause = document.getElementById('btnPlayPause');
  var timeDisplay = document.getElementById('timeDisplay');
  var videoFile = document.getElementById('videoFile');
  var importFile = document.getElementById('importFile');
  var videoField = document.getElementById('videoField');
  var gtKind = document.getElementById('gtKind');
  var sourceFile = document.getElementById('sourceFile');
  var verified = document.getElementById('verified');
  var unsavedIndicator = document.getElementById('unsavedIndicator');
  var segmentBody = document.getElementById('segmentBody');
  var emptyState = document.getElementById('emptyState');
  var validationSummary = document.getElementById('validationSummary');
  var issueList = document.getElementById('issueList');
  var referencePanel = document.getElementById('referencePanel');
  var toastHost = document.getElementById('toastHost');
  var btnSplit = document.getElementById('btnSplit');

  var stepButtons = [
    document.getElementById('btnStepBackBig'),
    document.getElementById('btnStepBackSmall'),
    document.getElementById('btnStepFwdSmall'),
    document.getElementById('btnStepFwdBig')
  ];

  // ---- helpers ------------------------------------------------------

  function setDirty(v) {
    dirty = v;
    unsavedIndicator.classList.toggle('dirty', dirty);
  }

  function toast(level, message) {
    var el = document.createElement('div');
    el.className = 'toast' + (level === 'error' ? ' error' : level === 'warn' ? ' warn' : '');
    el.textContent = message;
    el.addEventListener('click', function () { el.remove(); });
    toastHost.appendChild(el);
    setTimeout(function () { el.remove(); }, 7000);
  }

  function guessVideoPath(importName) {
    var base = importName.replace(/\.[^.]+$/, '');
    return 'videos/' + base + '.mp4';
  }

  function downloadBlob(content, filename, mime) {
    var blob = new Blob([content], { type: mime });
    var url = URL.createObjectURL(blob);
    var a = document.createElement('a');
    a.href = url;
    a.download = filename;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    setTimeout(function () { URL.revokeObjectURL(url); }, 1000);
  }

  function baseNameFor(defaultStem) {
    var v = (project.video || '').split('/').pop();
    if (v) return v.replace(/\.[^.]+$/, '');
    return defaultStem;
  }

  // ---- video transport ------------------------------------------------

  videoFile.addEventListener('change', function (e) {
    var file = e.target.files[0];
    if (!file) return;
    if (currentVideoUrl) URL.revokeObjectURL(currentVideoUrl);
    currentVideoUrl = URL.createObjectURL(file);
    video.src = currentVideoUrl;
    if (!videoField.value.trim()) {
      videoField.value = 'videos/' + file.name;
      project.video = videoField.value;
      setDirty(true);
    }
    e.target.value = '';
  });

  video.addEventListener('loadedmetadata', function () {
    project.duration_s = video.duration || 0;
    seekBar.max = String(project.duration_s);
    seekBar.disabled = false;
    btnPlayPause.disabled = false;
    stepButtons.forEach(function (b) { b.disabled = false; });
    updateTimeDisplay();
    renderAll();
  });

  video.addEventListener('play', function () { btnPlayPause.textContent = '⏸ Pause'; });
  video.addEventListener('pause', function () { btnPlayPause.textContent = '▶ Play'; });

  var scrubbing = false;
  seekBar.addEventListener('input', function () {
    scrubbing = true;
    video.currentTime = parseFloat(seekBar.value);
    updateTimeDisplay();
  });
  seekBar.addEventListener('change', function () { scrubbing = false; });

  video.addEventListener('timeupdate', function () {
    if (!scrubbing) seekBar.value = String(video.currentTime);
    updateTimeDisplay();
    updateActiveRow();
    updateSplitEnabled();
  });

  function updateTimeDisplay() {
    var cur = video.duration ? video.currentTime : 0;
    var tot = video.duration || project.duration_s || 0;
    timeDisplay.textContent = ASLGT.formatClock(cur) + ' / ' + (video.src ? ASLGT.formatClock(tot) : '(no video loaded)');
  }

  btnPlayPause.addEventListener('click', function () {
    if (video.paused) video.play(); else video.pause();
  });

  function seekBy(delta) {
    if (!video.duration) return;
    video.currentTime = Math.min(Math.max(0, video.currentTime + delta), video.duration);
  }
  document.getElementById('btnStepBackBig').addEventListener('click', function () { seekBy(-0.5); });
  document.getElementById('btnStepBackSmall').addEventListener('click', function () { seekBy(-0.05); });
  document.getElementById('btnStepFwdSmall').addEventListener('click', function () { seekBy(0.05); });
  document.getElementById('btnStepFwdBig').addEventListener('click', function () { seekBy(0.5); });

  // ---- meta fields ------------------------------------------------------

  videoField.addEventListener('input', function () {
    project.video = videoField.value;
    setDirty(true);
  });
  gtKind.addEventListener('change', function () {
    project.meta.gt_kind = gtKind.value;
    setDirty(true);
  });
  sourceFile.addEventListener('input', function () {
    project.meta.source_file = sourceFile.value;
    setDirty(true);
  });
  verified.addEventListener('change', function () {
    project.meta.verified = verified.checked;
    setDirty(true);
  });

  function syncMetaFieldsToUI() {
    videoField.value = project.video || '';
    gtKind.value = project.meta.gt_kind || 'human';
    sourceFile.value = project.meta.source_file || '';
    verified.checked = !!project.meta.verified;
  }

  // ---- segment mutation ------------------------------------------------

  function sortSegments() {
    project.segments.sort(function (a, b) { return a.start - b.start; });
  }

  function addSegmentAtPlayhead() {
    var t = video.duration ? video.currentTime : 0;
    var dur = video.duration || project.duration_s || 0;
    var end = dur ? Math.min(t + 1, dur) : t + 1;
    if (end <= t) end = t + 0.5;
    var seg = { _uid: newUid(), start: ASLGT.round3(t), end: ASLGT.round3(end), text: '', speaker: null };
    project.segments.push(seg);
    selectedUid = seg._uid;
    sortSegments();
    setDirty(true);
    renderAll();
    var ta = segmentBody.querySelector('textarea[data-uid="' + seg._uid + '"]');
    if (ta) ta.focus();
  }

  function deleteSegment(uid) {
    project.segments = project.segments.filter(function (s) { return s._uid !== uid; });
    if (selectedUid === uid) selectedUid = null;
    setDirty(true);
    renderAll();
  }

  function setStartFromPlayhead(uid) {
    var seg = project.segments.find(function (s) { return s._uid === uid; });
    if (!seg) return;
    seg.start = ASLGT.round3(video.currentTime);
    setDirty(true);
    sortSegments();
    renderAll();
  }

  function setEndFromPlayhead(uid) {
    var seg = project.segments.find(function (s) { return s._uid === uid; });
    if (!seg) return;
    seg.end = ASLGT.round3(video.currentTime);
    setDirty(true);
    renderAll();
  }

  function jumpToSegment(uid) {
    var seg = project.segments.find(function (s) { return s._uid === uid; });
    if (!seg || !video.duration) return;
    video.currentTime = seg.start;
    selectedUid = uid;
    renderAll();
  }

  function splitSelected() {
    var seg = project.segments.find(function (s) { return s._uid === selectedUid; });
    if (!seg || !video.duration) return;
    var t = video.currentTime;
    if (!(t > seg.start && t < seg.end)) return;
    var second = { _uid: newUid(), start: ASLGT.round3(t), end: seg.end, text: '', speaker: seg.speaker };
    seg.end = ASLGT.round3(t);
    project.segments.push(second);
    selectedUid = second._uid;
    sortSegments();
    setDirty(true);
    renderAll();
  }

  document.getElementById('btnAddSegment').addEventListener('click', addSegmentAtPlayhead);
  document.getElementById('btnSort').addEventListener('click', function () { sortSegments(); renderAll(); });
  btnSplit.addEventListener('click', splitSelected);

  function updateSplitEnabled() {
    var seg = project.segments.find(function (s) { return s._uid === selectedUid; });
    btnSplit.disabled = !(seg && video.duration && video.currentTime > seg.start && video.currentTime < seg.end);
  }

  function updateActiveRow() {
    var t = video.currentTime;
    Array.prototype.forEach.call(segmentBody.children, function (tr) {
      var uid = Number(tr.dataset.uid);
      var seg = project.segments.find(function (s) { return s._uid === uid; });
      var active = seg && t >= seg.start && t < seg.end;
      tr.classList.toggle('active-row', !!active);
    });
  }

  // ---- rendering ------------------------------------------------------

  function renderAll() {
    sortSegments();
    var displaySegs = project.segments.map(function (s, i) {
      return { id: i + 1, _uid: s._uid, start: s.start, end: s.end, text: s.text, speaker: s.speaker };
    });

    emptyState.style.display = displaySegs.length ? 'none' : 'block';
    segmentBody.innerHTML = '';

    var issues = ASLGT.validateSegments(displaySegs, project.duration_s || 0);
    var issuesByUid = {};
    displaySegs.forEach(function (s) {
      issuesByUid[s._uid] = issues.filter(function (iss) { return iss.id === s.id; });
    });

    displaySegs.forEach(function (s) {
      var tr = document.createElement('tr');
      tr.dataset.uid = s._uid;
      var myIssues = issuesByUid[s._uid] || [];
      if (myIssues.some(function (i) { return i.level === 'error'; })) tr.classList.add('has-error');
      else if (myIssues.some(function (i) { return i.level === 'warning'; })) tr.classList.add('has-warning');
      if (s._uid === selectedUid) tr.classList.add('selected-row');

      var tdId = document.createElement('td');
      tdId.textContent = String(s.id);
      tr.appendChild(tdId);

      var tdStart = document.createElement('td');
      var startInput = document.createElement('input');
      startInput.type = 'number';
      startInput.step = '0.001';
      startInput.min = '0';
      startInput.value = s.start.toFixed(3);
      startInput.addEventListener('change', function () {
        var seg = project.segments.find(function (x) { return x._uid === s._uid; });
        seg.start = ASLGT.round3(parseFloat(startInput.value) || 0);
        setDirty(true);
        renderAll();
      });
      tdStart.appendChild(startInput);
      var startClock = document.createElement('div');
      startClock.className = 'time-display';
      startClock.textContent = ASLGT.formatClock(s.start);
      tdStart.appendChild(startClock);
      tr.appendChild(tdStart);

      var tdEnd = document.createElement('td');
      var endInput = document.createElement('input');
      endInput.type = 'number';
      endInput.step = '0.001';
      endInput.min = '0';
      endInput.value = s.end.toFixed(3);
      endInput.addEventListener('change', function () {
        var seg = project.segments.find(function (x) { return x._uid === s._uid; });
        seg.end = ASLGT.round3(parseFloat(endInput.value) || 0);
        setDirty(true);
        renderAll();
      });
      tdEnd.appendChild(endInput);
      var endClock = document.createElement('div');
      endClock.className = 'time-display';
      endClock.textContent = ASLGT.formatClock(s.end);
      tdEnd.appendChild(endClock);
      tr.appendChild(tdEnd);

      var tdSpeaker = document.createElement('td');
      var speakerInput = document.createElement('input');
      speakerInput.type = 'text';
      speakerInput.value = s.speaker || '';
      speakerInput.placeholder = '(optional)';
      speakerInput.addEventListener('input', function () {
        var seg = project.segments.find(function (x) { return x._uid === s._uid; });
        seg.speaker = speakerInput.value || null;
        setDirty(true);
      });
      tdSpeaker.appendChild(speakerInput);
      tr.appendChild(tdSpeaker);

      var tdText = document.createElement('td');
      var textArea = document.createElement('textarea');
      textArea.rows = 2;
      textArea.dataset.uid = String(s._uid);
      textArea.value = s.text || '';
      if (myIssues.some(function (i) { return /empty/.test(i.message); })) tdText.classList.add('warn-cell');
      textArea.addEventListener('input', function () {
        var seg = project.segments.find(function (x) { return x._uid === s._uid; });
        seg.text = textArea.value;
        setDirty(true);
      });
      tdText.appendChild(textArea);
      tr.appendChild(tdText);

      var tdActions = document.createElement('td');
      tdActions.className = 'actions';
      var btnJump = document.createElement('button');
      btnJump.textContent = '⏵';
      btnJump.title = 'Jump to start';
      btnJump.disabled = !video.duration;
      btnJump.addEventListener('click', function () { jumpToSegment(s._uid); });
      var btnSetStart = document.createElement('button');
      btnSetStart.textContent = 'Start←';
      btnSetStart.title = 'Set start = playhead';
      btnSetStart.disabled = !video.duration;
      btnSetStart.addEventListener('click', function () { setStartFromPlayhead(s._uid); });
      var btnSetEnd = document.createElement('button');
      btnSetEnd.textContent = 'End←';
      btnSetEnd.title = 'Set end = playhead';
      btnSetEnd.disabled = !video.duration;
      btnSetEnd.addEventListener('click', function () { setEndFromPlayhead(s._uid); });
      var btnDel = document.createElement('button');
      btnDel.textContent = 'Delete';
      btnDel.addEventListener('click', function () { deleteSegment(s._uid); });
      tdActions.appendChild(btnJump);
      tdActions.appendChild(btnSetStart);
      tdActions.appendChild(btnSetEnd);
      tdActions.appendChild(btnDel);
      tr.appendChild(tdActions);

      tr.addEventListener('click', function () {
        selectedUid = s._uid;
        Array.prototype.forEach.call(segmentBody.children, function (row) {
          row.classList.toggle('selected-row', Number(row.dataset.uid) === selectedUid);
        });
        updateSplitEnabled();
      });

      segmentBody.appendChild(tr);
    });

    var errorCount = issues.filter(function (i) { return i.level === 'error'; }).length;
    var warnCount = issues.filter(function (i) { return i.level === 'warning'; }).length;
    var parts = [];
    if (errorCount) parts.push('<span class="error">' + errorCount + ' error' + (errorCount === 1 ? '' : 's') + '</span>');
    if (warnCount) parts.push('<span class="warn">' + warnCount + ' warning' + (warnCount === 1 ? '' : 's') + '</span>');
    if (!errorCount && !warnCount && displaySegs.length) parts.push('<span class="ok">looks good</span>');
    if (!project.duration_s) parts.push('<span class="warn">no video duration known — load the video to validate end-of-clip bounds</span>');
    validationSummary.innerHTML = parts.join(' &nbsp;·&nbsp; ');

    issueList.innerHTML = '';
    issues.forEach(function (iss) {
      var div = document.createElement('div');
      div.className = 'issue ' + iss.level;
      div.textContent = (iss.level === 'error' ? '✖ ' : '⚠ ') + (iss.id ? '#' + iss.id + ': ' : '') + iss.message;
      issueList.appendChild(div);
    });

    updateSplitEnabled();
  }

  // ---- import ------------------------------------------------------

  function hideReferencePanel() {
    referencePanel.style.display = 'none';
    referencePanel.innerHTML = '';
  }

  function showReferencePanel(ref, filename) {
    referencePanel.style.display = 'block';
    var html = '<div class="banner">⚠ ' + ref.warning + '</div>';
    html += '<div><strong>' + (ref.title || filename) + '</strong>' + (ref.source ? ' — ' + ref.source : '') + '</div>';
    html += '<ul>';
    ref.lines.forEach(function (l) {
      var cls = l.in_clip === false ? ' class="out-of-clip"' : '';
      html += '<li' + cls + '>' + (l.signer ? '<em>' + l.signer + ':</em> ' : '') + escapeHtml(l.text) +
        (l.in_clip === false ? ' (outside imported clip)' : l.in_clip === 'boundary' ? ' (clip boundary)' : '') + '</li>';
    });
    html += '</ul>';
    referencePanel.innerHTML = html;
  }

  function escapeHtml(s) {
    var d = document.createElement('div');
    d.textContent = s;
    return d.innerHTML;
  }

  importFile.addEventListener('change', function (e) {
    var file = e.target.files[0];
    if (!file) return;
    var name = file.name;
    var reader = new FileReader();
    reader.onload = function () {
      var text = String(reader.result);
      if (/\.srt$/i.test(name)) {
        var segs;
        try { segs = ASLGT.parseSRT(text); } catch (err) { toast('error', 'Failed to parse SRT: ' + err.message); return; }
        if (!segs.length) { toast('error', 'No valid cues found in ' + name); return; }
        project.segments = segs.map(function (s) { return { _uid: newUid(), start: s.start, end: s.end, text: s.text, speaker: null }; });
        if (!videoField.value.trim()) videoField.value = guessVideoPath(name);
        project.video = videoField.value;
        project.meta = { gt_kind: 'human', source_file: name, verified: false };
        syncMetaFieldsToUI();
        hideReferencePanel();
        setDirty(true);
        renderAll();
        toast('ok', 'Imported ' + segs.length + ' segments from ' + name + '.');
      } else if (/\.json$/i.test(name)) {
        var obj;
        try { obj = JSON.parse(text); } catch (err) { toast('error', 'Invalid JSON in ' + name + ': ' + err.message); return; }
        var cls = ASLGT.classifyImportJSON(obj);
        if (cls.type === 'baseline0') {
          var canon = ASLGT.parseBaseline0(obj);
          project.segments = canon.segments.map(function (s) { return { _uid: newUid(), start: s.start, end: s.end, text: s.text, speaker: s.speaker }; });
          if (!videoField.value.trim() && canon.video) videoField.value = canon.video;
          project.video = videoField.value;
          project.meta = { gt_kind: 'model', source_file: name, verified: false };
          syncMetaFieldsToUI();
          hideReferencePanel();
          setDirty(true);
          renderAll();
          toast('warn', (canon.warning ? canon.warning + ' ' : '') + 'Loaded ' + canon.segments.length + ' editable prediction segments from ' + name + '.');
        } else if (cls.type === 'canonical') {
          var c = ASLGT.parseCanonical(obj);
          project = {
            video: c.video,
            duration_s: c.duration_s || 0,
            meta: c.meta,
            segments: c.segments.map(function (s) { return { _uid: newUid(), start: s.start, end: s.end, text: s.text, speaker: s.speaker }; })
          };
          syncMetaFieldsToUI();
          hideReferencePanel();
          setDirty(false);
          renderAll();
          toast('ok', 'Opened project ' + name + ' (' + project.segments.length + ' segments). Load the matching video separately if needed.');
        } else if (cls.type === 'nontimed') {
          var ref = ASLGT.parseNontimedReference(obj);
          showReferencePanel(ref, name);
          toast('warn', 'No timestamps in ' + name + ' — shown as reference only, not imported as segments.');
        } else {
          toast('error', 'Unrecognized JSON shape in ' + name + '.');
        }
      } else {
        toast('error', 'Unsupported file type: ' + name);
      }
    };
    reader.readAsText(file);
    e.target.value = '';
  });

  // ---- export ------------------------------------------------------

  document.getElementById('btnExportSrt').addEventListener('click', function () {
    if (!project.segments.length) { toast('error', 'No segments to export.'); return; }
    var text = ASLGT.exportSRT(project.segments);
    downloadBlob(text, baseNameFor('ground_truth') + '.srt', 'application/x-subrip');
    setDirty(false);
    toast('ok', 'Exported SRT (' + project.segments.length + ' segments).');
  });

  document.getElementById('btnExportJson').addEventListener('click', function () {
    var canon = ASLGT.toCanonicalJSON(project);
    downloadBlob(JSON.stringify(canon, null, 2), baseNameFor('ground_truth') + '.json', 'application/json');
    setDirty(false);
    toast('ok', 'Exported canonical JSON (' + canon.segments.length + ' segments).');
  });

  document.getElementById('btnNewProject').addEventListener('click', function () {
    if (currentVideoUrl) { URL.revokeObjectURL(currentVideoUrl); currentVideoUrl = null; }
    video.removeAttribute('src');
    video.load();
    seekBar.disabled = true;
    btnPlayPause.disabled = true;
    stepButtons.forEach(function (b) { b.disabled = true; });
    project = { video: '', duration_s: 0, meta: { gt_kind: 'human', source_file: '', verified: false }, segments: [] };
    selectedUid = null;
    syncMetaFieldsToUI();
    hideReferencePanel();
    setDirty(false);
    renderAll();
    toast('ok', 'Started a new project.');
  });

  // ---- keyboard shortcuts ------------------------------------------------

  document.addEventListener('click', function (e) {
    if (e.target.tagName === 'BUTTON') setTimeout(function () { e.target.blur(); }, 0);
  });

  document.addEventListener('keydown', function (e) {
    var tag = (document.activeElement && document.activeElement.tagName) || '';
    if (e.key === 'Escape') {
      if (document.activeElement) document.activeElement.blur();
      return;
    }
    var typing = tag === 'INPUT' || tag === 'TEXTAREA' || tag === 'SELECT' || tag === 'BUTTON';
    if (typing) return;

    if (e.key === ' ') {
      e.preventDefault();
      if (!video.duration) return;
      if (video.paused) video.play(); else video.pause();
    } else if (e.key === 'ArrowLeft') {
      e.preventDefault();
      seekBy(e.shiftKey ? -0.05 : -0.5);
    } else if (e.key === 'ArrowRight') {
      e.preventDefault();
      seekBy(e.shiftKey ? 0.05 : 0.5);
    } else if (e.key === 's' || e.key === 'S') {
      if (selectedUid != null && video.duration) { setStartFromPlayhead(selectedUid); }
      else toast('warn', 'Select a segment row first (click it), then press S.');
    } else if (e.key === 'e' || e.key === 'E') {
      if (selectedUid != null && video.duration) { setEndFromPlayhead(selectedUid); }
      else toast('warn', 'Select a segment row first (click it), then press E.');
    } else if (e.key === 'a' || e.key === 'A') {
      addSegmentAtPlayhead();
    } else if (e.key === 'Delete' || e.key === 'Backspace') {
      if (selectedUid != null) deleteSegment(selectedUid);
    }
  });

  window.addEventListener('beforeunload', function (e) {
    if (!dirty) return;
    e.preventDefault();
    e.returnValue = '';
  });

  // ---- init ------------------------------------------------------

  syncMetaFieldsToUI();
  renderAll();
})();
