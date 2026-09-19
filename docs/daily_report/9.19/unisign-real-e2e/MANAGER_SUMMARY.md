# Uni-Sign real-checkpoint E2E — manager summary (task "a")

**Result: E2E COMPLETE.** The Uni-Sign FastAPI/Docker service now runs end to end with the real official How2Sign checkpoint, locally. Full detail is in `RESULTS.md`.

- **Checkpoint:** downloaded from the official Hugging Face repo. SHA256 and size both match (1,186,925,007 bytes). It is git-ignored, was not committed or baked into the image, and there was no ACR or Azure step.
- **Service:** `/healthz` 200. **`/readyz` 200**, model loaded strictly in 19 s. `linux/amd64` container, run under emulation on an Apple Silicon Mac.
- **Short clip** (`g0uGWjwdOIw_1-8-rgb_front`, 5.9 s), HTTP 200, 40 s warm:
  - Reference: *It got a lot to do with math and geometry, geometric designs.*
  - Uni-Sign: *So, the main thing is that mathematics are involved in the design.*
  - Meaning is close and wording differs. WER 1.00, CER 0.75, BLEU 0.0, chrF 21.8. Deterministic across runs.
- **Long clip** (`FzmL8SL6Bow_1-8-rgb_front`, 25.8 s), HTTP 200, 101 s:
  - Uni-Sign: *We're going to go ahead and put this on the bottom and we're going to go ahead and put this on the bottom and we're going to go ahead and take our rubber band and*
  - This is 38 words against a 78-word reference, repetitive and off-target. WER 0.87, CER 0.70, BLEU 2.5, chrF 20.5.

**What happens when Uni-Sign gets a long clip directly** (the manager's question):
- The API succeeds and returns one string.
- Of the 618 frames extracted, **only a random 256 (41%) reach the model**, because of the upstream `max_length=256` cap. 59% of the video is dropped at random.
- The same long clip sent twice gave **two different translations**, because the frame sampling is unseeded per request.
- The output was not cut off by the 100-token cap (it used 50). The model stopped early, on a dangling "and".
- Peak memory was 6.6 GiB of the 7.65 GiB limit.

**Read this with caution:** this is n=2, so no quality ranking is possible. The short clip also scored WER 1.0. I did not test a mid-length clip that stays under the 256-frame cap, so I can't yet separate frame subsampling from the model simply struggling with long clips.

**Does long-video segmentation look worth testing?** Yes, on this evidence, but it's motivation and not proof.

**Other findings:**
- The rtmlib pose weights (~132 MB) download at the first request. This adds ~13 s of cold start and needs outbound network.
- curl needs `;type=video/mp4` on the upload or the service returns 415.
- The README still says "not inference-tested". It's now stale, and I didn't edit it.
- The CC BY-NC-4.0 blocker on ACR and production is unchanged.

**Next step: c — not b.**
