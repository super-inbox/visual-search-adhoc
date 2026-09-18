# Manager request A — Real Uni-Sign local end-to-end run

Date: 2026-09-18
Scope: Phase A only, per manager's confirmed priority order A -> C -> B. No segmentation
implemented, no new repo started, no commit/push, no ACR push.

Authorization: manager explicitly approved local E2E including checkpoint download
("可以本地端到端的运行，包括把 checkpoint 下载下来，用一个短的 clip + 一个长的 clip 看一下返回的内容").

Host: Apple M3 Pro (arm64/Apple Silicon). Container run as `linux/amd64` via Docker
Desktop's QEMU emulation (the deployment target, per this service's existing Dockerfile
and prior work reports, is amd64/ACR) — inference is therefore markedly slower than
native-arch CPU inference would be. This is disclosed because it materially affects the
runtime numbers below; it does not affect correctness of the output.

## Checkpoint

- Official source: `https://huggingface.co/ZechengLi19/Uni-Sign/resolve/main/how2sign_pose_only_slt.pth`
- Local path: `~/.cache/uni_sign_checkpoints/how2sign_pose_only_slt.pth` — chosen specifically
  because it is **outside every git working tree** on this machine (verified: `git
  rev-parse --is-inside-work-tree` in that directory fails with "not a git repository").
  This is a stronger guarantee against accidental commit than gitignoring alone.
- Also confirmed the service's own default in-repo mount target is gitignored:
  `git check-ignore -v uni_sign_server/checkpoints/how2sign_pose_only_slt.pth` →
  matched by `uni_sign_server/.gitignore:6: checkpoints/`.
- Size: downloaded = **1,186,925,007 bytes** — matches expected exactly.
- SHA256: downloaded = **1bfd5f3312f04e4736f0a52f4ef9535916e6de9676a2a0d00c708748683fb00d**
  — matches expected exactly.
- Verification status: **PASS** (exact byte-for-byte match on both size and hash).
- Not baked into any Docker image layer: mounted read-only at container run time only
  (`-v ...:/app/checkpoints/how2sign_pose_only_slt.pth:ro`), never `COPY`'d in the
  Dockerfile (confirmed by reading `uni_sign_server/Dockerfile` — the checkpoint is
  referenced only via `UNISIGN_CHECKPOINT_PATH` env var, no `COPY checkpoints`).

## Service

- Repo/branch: `curify-studio`, branch `baobao/asl-unisign-fastapi-service`
  (unchanged this session — no commits made).
- Docker image: rebuilt `uni-sign-local:test` for `linux/amd64` from the current tracked
  Dockerfile/requirements.txt/patches (`docker buildx build --platform linux/amd64`).
  **Every layer hit cache** against the previously-built image, confirming the
  already-existing `uni-sign-local:test` tag was already content-identical to the
  current tracked code — no drift, no code changes needed to build.
- Container: `uni-sign-e2e`, run from that image with:
  - `-v ~/.cache/uni_sign_checkpoints/how2sign_pose_only_slt.pth:/app/checkpoints/how2sign_pose_only_slt.pth:ro`
  - `-v ~/.cache/uni_sign_hf:/tmp/hf` (HF cache for `google/mt5-base`, Apache-2.0, lazy-downloaded)
  - `-e UNISIGN_NC_CHECKPOINT_LICENSE_ACK=1` (the existing license-ack gate; without it
    `/readyz` and `/translate` would 503 per `app/unisign_bridge.py`'s
    `LicenseNotAcknowledgedError` check)
  - `--platform linux/amd64`, port `8010:8000`

### `GET /healthz`
**HTTP 200**, `{"status":"ok"}` — immediate, does not touch the model (as designed).

### `GET /readyz`
**HTTP 200**, `{"status":"ok","model_loaded":true}`.
- Called at `2026-09-18T05:52:52Z`, responded at `2026-09-18T05:53:47Z` →
  **model load time ≈ 55 seconds** (includes `google/mt5-base` download into the
  mounted HF cache — first run only — plus real checkpoint `torch.load()` and a
  **strict** `model.load_state_dict(..., strict=True)`, which succeeded with zero
  missing/unexpected keys — i.e. the real checkpoint's architecture matches the
  constructed `Uni_Sign(args)` exactly).
- Memory during/after load (`docker stats`): peaked at **5.33 GiB** during
  `torch.load()`/state-dict application, settled to **~2.4–2.8 GiB** at idle after a
  translate request (container memory limit 7.65 GiB, never close to OOM).
- This is the first time this service has loaded the **real, licensed checkpoint**
  end-to-end (prior 9.17 validation only exercised the failure path with a 22-byte
  dummy file).

## Short clip

- Input: `1477_recording_6.7s.mp4`
- Path: `asl-translator/data/asl_corpus/videos/1477_recording_6.7s.mp4` (in the
  research repo, not curify-studio)
- Duration: 6.68s (ffprobe; manifest.json agrees, 6.68s, 640x480, 25.0fps, 167 frames)
- Provenance/category: Curify's own `asl_corpus` (real submitted user recording, not
  How2Sign), `job_type: "asl_translation"`, `job_status: "COMPLETED"`. Per
  `VIDEO_TYPE_AUDIT.csv`: "Webcam recording; frames show clear ASL number handshapes
  (one finger, then two/three fingers) consistent with fingerspelling/counting content."
  Manifest notes it's the corpus's shortest/lowest-resolution clip, included specifically
  to isolate resolution from sampling density.
- Reference/ground truth: **none exists** for this clip (`manifest.json` has no
  `ground_truth` key for `1477_recording_6.7s`, only a prior `predictions_baseline0`
  entry — that's a past prediction, not a reference). No reference-vs-prediction
  comparison is possible for this clip.

### Result
- HTTP status: **200**
- Runtime (wall clock, curl `time`): **5:00.61** (≈300.6s) for a 6.68s input, under
  amd64-on-arm64 emulation (real-time factor ≈ 45x for this clip; see host-arch caveat
  above — this is not native-speed CPU inference).
- Complete JSON response:
```json
{"model":{"name":"Uni-Sign","checkpoint":"how2sign_pose_only_slt.pth","pinned_commit":"eed438bcb49e30405cd6ccdfcccca330c134e830"},"translation":"One, two, three; one, two, three; one, two, three; one, two, three; one, two, three; one, two, three; one, two, three; one, two, three; one, two, three; one, two, three; one, two, three; one, two, three; one, two, three; one, two, three; one, two, three; one, two, three; one, two,","segments":[{"start":0.0,"end":6.68,"text":"One, two, three; one, two, three; one, two, three; one, two, three; one, two, three; one, two, three; one, two, three; one, two, three; one, two, three; one, two, three; one, two, three; one, two, three; one, two, three; one, two, three; one, two, three; one, two, three; one, two,","source":"wrapper_derived","note":"start/end are NOT produced by Uni-Sign. They span the whole uploaded clip only. Uni-Sign has no native temporal alignment -- see README.md 'Timestamp semantics'."}]}
```
- Translation text: `"One, two, three; one, two, three; ..."` (repeated 16.5x, cut off
  mid-phrase at "one, two,").
- `segments[0].start` = **0.0**, `segments[0].end` = **6.68**. These are
  **wrapper-derived, NOT Uni-Sign model output** — `start` is hardcoded `0.0` and `end`
  is the ffprobe-measured upload duration, per `app/main.py`'s `/translate` handler.
  Uni-Sign's own `generate()` returns only the plain decoded string; it has no native
  timestamp/segmentation output on this pinned commit (confirmed by direct code reading,
  not inferred).
- Observation: the model output is a real, checkpoint-backed generation — plausibly
  related to the video's actual content (the video shows counting/number handshapes,
  per `VIDEO_TYPE_AUDIT.csv`'s independent visual description) — but it is
  **degenerate/looping** ("one, two, three" repeated ~16 times) and hits the
  `max_new_tokens=100` cap mid-sentence. This matches the README's pre-existing,
  documented caveat about `max_new_tokens=100` causing truncation, now confirmed with a
  real output for the first time rather than as a theoretical concern.

## Long clip

- Input: `1252_1000016397_76.8s.mp4`
- Path: `asl-translator/data/asl_corpus/videos/1252_1000016397_76.8s.mp4`
- Duration: 77.496208s (ffprobe; manifest.json lists 76.753444s — small discrepancy
  between container-duration and stream-duration metadata, both ~77s, substantially
  longer than any How2Sign sentence-level clip, satisfying the "clearly longer than
  sentence-level" selection criterion). 2283 video frames at ~29.92fps.
- Provenance/category: Curify's own `asl_corpus`, a real user submission.
  `manifest.json` records `job_type: "subtitle_only + full_translation (BOTH FAILED)"`
  — i.e. **this exact clip previously failed Curify's own production
  translation pipeline** (`failure: "Translation failed or returned empty"`), which is
  directly relevant to the manager's long-video question. `VIDEO_TYPE_AUDIT.csv`:
  "Portrait phone video at whiteboard, letterboxed; all 6 frames show active
  fingerspelling/number handshapes; already verified_gold with hand-translated GT
  including fingerspelled names."
- Reference/ground truth: **exists but is explicitly flagged as non-independent /
  circular** in this project's own `inventory.json`:
  - `ground_truth/1252_1000016397_76.8s.srt`, "human-translated by Curify, verified", 11 lines.
  - `inventory.json`'s own audit: `"independence": "non_independent"`,
    `"provenance_quality": "poor and circular"` — the SRT, the burned-caption video, and
    an internal frame-inspector's embedded gold are "one translation counted three
    times... they agree because they share a source, not because they corroborate each
    other," authored by Curify itself to send back to the submitter, with no named
    annotator and no second-annotator check. `"usable_for_official_metrics": false`.
  - Presented below for qualitative context only, **not** as a clean WER/accuracy
    baseline — per this project's own prior audit, doing so would misrepresent it.

Reference SRT (concatenated, chronological):
> The boy's name is Greg. Number two. You're going to dance? Number three. The lights
> are on the screen. Number four. The woman named Sara has a name sign. Number four.
> The man is wearing brown pants and a brown shirt. Number. The book is number three.
> You read it.

### Result
- HTTP status: **200**
- Runtime (wall clock, curl `time`): **25:27.31** (≈1527s) for a 77.5s input
  (real-time factor ≈ 20x under amd64-on-arm64 emulation).
- Complete JSON response:
```json
{"model":{"name":"Uni-Sign","checkpoint":"how2sign_pose_only_slt.pth","pinned_commit":"eed438bcb49e30405cd6ccdfcccca330c134e830"},"translation":"One, two, three, four. One, two, three, four. One, two, three, four. One, two, three, four. One, two, three, four. One, two, three, four. One, two, three, four. One, two, three, four. One, two, three, four. One, two, three, four. One, two, three, four. One, two, three, four. One, two,","segments":[{"start":0.0,"end":77.496208,"text":"One, two, three, four. One, two, three, four. One, two, three, four. One, two, three, four. One, two, three, four. One, two, three, four. One, two, three, four. One, two, three, four. One, two, three, four. One, two, three, four. One, two, three, four. One, two, three, four. One, two,","source":"wrapper_derived","note":"start/end are NOT produced by Uni-Sign. They span the whole uploaded clip only. Uni-Sign has no native temporal alignment -- see README.md 'Timestamp semantics'."}]}
```
- Translation text: `"One, two, three, four. One, two, three, four. ..."` (repeated
  12.5x, cut off mid-phrase at "One, two,").
- `segments[0].start` = **0.0**, `segments[0].end` = **77.496208** — again
  wrapper-derived (whole-clip span), not model output. Same caveat as short clip.
- Reference-vs-prediction (qualitative only, reference is non-independent — see above):
  the reference describes 6 distinct sentences plus 4 standalone "Number N" cues and 2
  proper names (Greg, Sara); the prediction is a single repeated 4-count loop
  ("one, two, three, four") with no sentence content, no names, and no variation across
  the whole 77s clip. The prediction does **not** reproduce any of the reference's
  actual sentence content, though both involve counting-adjacent content, consistent
  with the video's independently-audited visual description ("fingerspelling/number
  handshapes").

### Preprocessing behavior — code evidence, not inference

Read directly from the vendored pinned-commit source inside the running container
(`docker exec uni-sign-e2e ...`), not guessed:

1. **Every frame is pose-extracted, no stride, no cap at extraction time.**
   `demo/online_inference.py::pose_extraction()` reads every frame via
   `cv2.VideoCapture` into `vid_data` with no skipping, then runs `Wholebody()` pose
   estimation on every single frame via a 16-worker thread pool. Confirmed by container
   log: `Processing frames: 100%|██████████| 167/167` for the short clip and
   `Processing frames: 100%|██████████| 2283/2283` for the long clip — i.e. **all 2283
   frames of the 77.5s clip were pose-extracted**, not subsampled at this stage.
2. **Random subsampling happens downstream, only if `duration > max_length=256`.**
   `datasets.py::S2T_Dataset_online.load_pose()` (the exact class this service's
   `unisign_bridge.py::translate_video()` uses for the online-inference path):
   ```python
   duration = len(pose['scores'])
   ...
   if duration > self.max_length:
       tmp = sorted(random.sample(range(duration), k=self.max_length))
   else:
       tmp = list(range(duration))
   ```
   with `self.max_length = args.max_length`, defaulted in `utils.py` to
   `parser.add_argument("--max_length", default=256, type=int)`, unmodified by this
   service (`unisign_bridge.py::_build_args()` does not override `max_length`).
   - **Short clip (167 frames)**: `167 < 256` → **no subsampling**, all 167 frames used.
   - **Long clip (2283 frames)**: `2283 > 256` → **randomly subsampled to exactly 256
     frames** (≈11.2% of frames kept, sorted to preserve temporal order,
     `random.sample` without replacement). This is a genuinely random, non-uniform
     subsample (not evenly-spaced stride), seeded only once at model-load time via
     `unisign_utils.set_seed(42)` inside `unisign_bridge.py::_load_model_locked()` — the
     Python `random` module's global state is **not** reseeded per request, so the exact
     256 frames chosen for a given `/translate` call depend on how many prior calls to
     `random`-consuming code happened since model load, not on a fixed seed per request.
     This run's specific 256-frame subsample is therefore not independently reproducible
     from this report alone.
3. **`max_new_tokens=100`, `num_beams=4`** — unchanged from the benchmark config, applied
   identically to both clips (`unisign_bridge.py::translate_video()`). This caps
   generation length regardless of input length, which is the direct, code-confirmed
   cause of both outputs truncating mid-phrase.
4. No other truncation, chunking, or sliding-window logic exists in the online-inference
   path for arbitrary-length input — confirmed by reading the full `load_pose()` method
   (`datasets.py`, `S2T_Dataset_online` class) and `pose_extraction()`
   (`demo/online_inference.py`) end to end; there is no code path that segments a long
   video into multiple sentence-level sub-clips before or during inference.

## Conclusion

1. **Is real Uni-Sign local E2E now working?**
   **Yes.** For the first time, this service loaded the real, license-verified
   (byte-exact size + SHA256 match), CC BY-NC-4.0 `how2sign_pose_only_slt.pth`
   checkpoint with a **strict** `state_dict` load (zero missing/unexpected keys),
   answered `/healthz` (200) and `/readyz` (200, `model_loaded: true`) for real, and
   produced real generated text from `Uni_Sign.generate()` — not a stub, not a 503, not
   a simulated response — for both a short and a long real video. No tracked
   `curify-studio` code needed modification to achieve this (the existing image built
   from unmodified tracked Dockerfile/requirements/patches, fully cache-hit).

2. **What does it return for the short clip?** A real generated string,
   `"One, two, three; one, two, three; ..."` (repeated ~16x, truncated at
   `max_new_tokens=100`) — for a 6.68s clip independently described as showing
   number/counting handshapes. Content direction is plausible; the output itself is
   degenerate (looping, no sentence variety).

3. **What does it return for the long clip?** The same structural failure mode, worse:
   for a 77.5s clip with an 11-line, 6-sentence human reference (albeit non-independent),
   the model returns a single repeated 4-count loop
   (`"One, two, three, four. One, two, three, four. ..."`), truncated at
   `max_new_tokens=100`, with zero sentence-level content and no correspondence to any
   of the reference's actual sentences or the two fingerspelled names in it.

4. **Does the long input expose an obvious reason to investigate segmentation later?**
   **Yes, clearly.** Two independent, code-confirmed mechanisms compound on long input:
   (a) a fixed `max_new_tokens=100` output budget that is identical regardless of input
   length, so a 6-sentence 77s video gets the same output budget as a single 6.7s
   number-counting clip and the model runs out of budget after one repeated phrase; and
   (b) `max_length=256`-frame random subsampling that, for this clip, kept only ~11.2%
   of the 2283 extracted frames, discarding the vast majority of the temporal
   information in a single unstructured random draw with no notion of sentence
   boundaries. This is fully consistent with this exact clip's real production history
   (`job_type: "subtitle_only + full_translation (BOTH FAILED)"` — Curify's own pipeline
   already failed on this video). **Per instructions, no segmentation fix is implemented
   in this session** — this is recorded as evidence for Phase B, not acted on.
