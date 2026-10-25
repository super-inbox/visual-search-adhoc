# P0-13: Boss summary. Is our ASL bottleneck the representation or the amount of labeled data?

**Status: COMPLETE.** One controlled training run (CPU, 2.7 h) plus re-evaluation of the existing P0.2 run.

**What we did.** We kept everything from P0.2 fixed: the same 2,751 training clips, the same val and frozen test
sets, the same model, optimizer and decoding. We changed **only the input**. Instead of our hand-tracked body
landmarks, the model reads frozen features from the pretrained Uni-Sign encoder (`how2sign_pose_only_slt.pth`).

**Result on the clean 147-clip frozen test set:**

| | BLEU | chrF | WER | Distinct predictions |
|---|---|---|---|---|
| Our P0.2 model (landmarks) | 1.02 | 11.12 | 1.025 | 102 / 147 |
| **Same model, Uni-Sign features** | **3.25** | **17.05** | **0.939** | **147 / 147** |
| Difference (95 % CI) | **+2.23** [1.28, 3.39] | **+5.93** [4.66, 7.34] | −0.086 | |

- **The model now actually uses the video.** Shuffling which video goes with which sentence barely hurts the old
  model (loss +0.067) but hurts the new one 19× more (loss +1.280; BLEU falls to about 0.6).
- **It still holds with identical video clips.** Part of the gain comes from Uni-Sign's better-cut clips. On 128
  clips where both models see exactly the same video segment, the gain is +2.2 BLEU / +4.0 chrF (both CIs
  exclude 0).

**Conclusion.** At a fixed 2,751 labeled clips, swapping in a pretrained sign representation roughly
**triples BLEU**. In this setup, that supports a representation bottleneck rather than simply too few labels in
our own training run.

**Caveats (important):**

1. **The pretrained encoder itself was trained on much more data** (about 31k How2Sign sentences plus 984 h of
   YouTube-ASL). So the finding is "a representation learned from lots of sign data beats one learned from our
   2,751 clips". It is **not** "labeled data doesn't matter".
2. **Quality is still far from usable** (3.3 BLEU). The same features with Uni-Sign's own large decoder score
   6.4–9.0 BLEU, so our small decoder or its training data is now the next limit.
3. Single training seed. The validation set had to be excluded from the verdict because Uni-Sign was trained on
   those exact clips. The frozen test set is clean.
4. The Uni-Sign weights are non-commercial (CC BY-NC-4.0).

**Recommended next step.** Fine-tune on top of the pretrained encoder instead of training our own encoder from
scratch. The cheapest test is the same 2,751-clip setup with Uni-Sign's own mT5 decoder fine-tuned (encoder
frozen), plus a randomly initialized Uni-Sign encoder control to separate "pretraining" from "architecture".
Then evaluate on real Curify videos.
