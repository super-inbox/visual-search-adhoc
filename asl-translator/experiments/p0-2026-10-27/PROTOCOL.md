# Three P0 experiments 2026-10-27

New exploratory experiment, distinct from the frozen October 23 protocol. User authorized automatic specialist investigation and the three experiments. No old labels, frozen thresholds or results are overwritten. No training, production deployment, paid cloud jobs, or holdout access.

## A Sampling

Before executing: compare seeded uniform random (Uni-Sign style), deterministic uniform, and coverage-plus-motion at the same budget of at most 256 frames. Reserve half the budget uniformly across the entire sequence, including endpoints; allocate the remainder at quantiles of clipped frame-difference energy. Keep chronological order, unique indices and the full frame budget. Static input falls back to uniform. Do not delete intervals based on references. Motion is a proxy, not a signing or information label.

Run geometry/coverage diagnostics on the 45 existing compressed OLD-window videos only. These are not official model inputs. Record real decoded frame PTS, source hashes and per-arm indices. Full sentence quality requires paired Uni-Sign decodes on matched pose inputs; proxy gains are not quality gains. R10's 5–16s interval is a pre-existing diagnostic slice, not a selection rule. No thresholds tuned after results.

## B Specialist

Inspect ASL temporal detector and open-vocabulary recognizer separately. Test public research-permitted weights locally where available. No reference names/lexicon supplied to inference. An untrimmed sentence or fixed sliding window is an unverified proposal, not a positive fingerspelling detection. Produce clip-relative PTS intervals, letter hypotheses, model identity and an explicit review-needed status. No automatic sentence replacement. Word-level span timestamps and attention/character timestamps must be distinguished. Blind human labels remain blank.

## C Repetition

Fixed new arm: same checkpoint, inputs, seed, beam=4, max_new_tokens=100 as control; treatment adds no_repeat_ngram_size=3 (TOKEN trigrams, not word trigrams). No other decode changes. Evaluate all 45 and separately R01 plus R41 control. Report text chrF/WER, word loop counts, truncation and human status pending. This is a generation experiment, not post-hoc string deduplication. Without checkpoint/runtime/input artifacts, report blocked, never infer treatment output from old candidates.
