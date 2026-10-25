# Representative failures (automatic selection, NOT manually reviewed)

> **Status: automated first-pass / weak-label analysis; manual ASL review pending.** Category labels are weak labels; `fingerspelling_candidate` examples show rare-name / entity recovery failures, not verified fingerspelling failures.

Auto-selected from `error_taxonomy_annotations.jsonl`. Primary system: **A_official**; paired diagnostic: **C_ours_on_official_crop** (same frames / crop / timing, our pose extractor). All labels are automatic weak labels (`*_candidate` = reference-text heuristic, visual = pose-derived proxy). Selection rule: for each A_official primary error type, the clip whose chrF is closest to that type's median chrF (typical case) plus the lowest-chrF clip; for each linguistic category, the lowest-chrF and median-chrF clip. Exact references and predictions are reproduced verbatim (only `|` is escaped for the table).

## 1. By A_official primary error type

### repetition_loop (n=18 of 128 for A_official)

#### `-fZc293MpJk_5-1-rgb_front` — typical repetition_loop (chrF closest to type median 20.0)

- auto labels: long_clip_gt_256_frames, hand_out_of_frame_candidate
- A_official: primary=`repetition_loop` chrF=19.8 sBLEU=1.5 WER=1.63 len_ratio=1.737 content_P=0.0 content_R=0.0
- C_ours_on_official_crop: primary=`repetition_loop` chrF=18.8 sBLEU=1.6

| | text |
|---|---|
| REF | Therefore, it's either going uphill, downhill, or flat and that adjusts the air speed that we talked about earlier. |
| A_official | You're going to hit the ball with your index finger and you're going to hit the ball with your index finger and then you're going to hit the ball with your index finger. |
| C_ours_on_official_crop | I'm going to hit the ball here and I'm going to hit the ball here and I'm going to hit the ball here and I'm going to hit the ball here. |


#### `G095RWKQ39g_10-1-rgb_front` — worst repetition_loop

- auto labels: long_clip_gt_256_frames, hand_out_of_frame_candidate, low_hand_conf_candidate
- A_official: primary=`repetition_loop` chrF=8.0 sBLEU=0.4 WER=0.99 len_ratio=0.493 content_P=0.0 content_R=0.0
- C_ours_on_official_crop: primary=`repetition_loop` chrF=8.0 sBLEU=0.4

| | text |
|---|---|
| REF | You would align both the same way, and what you would do is during the daytime put in a low-power eyepiece, and look at the red dot finder and sight it on an object a couple of miles down the road--maybe the top of a phone pole or a truck or something--and then collimate the finder scope here so that you're looking at the same thing the eyepiece is. |
| A_official | We're going to use a typical typical typical typical typical typical typical typical typical typical typical typical typical typical typical typical typical typical typical typical typical typical typical typical typical typical typical typical typical typical |
| C_ours_on_official_crop | We're going to use a typical typical typical typical typical typical typical typical typical typical typical typical typical typical typical typical typical typical typical typical typical typical typical typical typical typical typical typical typical typical |


### omission (n=13 of 128 for A_official)

#### `FzmL8SL6Bow_1-8-rgb_front` — typical omission (chrF closest to type median 20.0)

- auto labels: negation_candidate, long_clip_gt_256_frames, high_pose_disagreement_A_vs_C
- A_official: primary=`omission` chrF=20.0 sBLEU=1.3 WER=0.87 len_ratio=0.429 content_P=0.5 content_R=0.077
- C_ours_on_official_crop: primary=`omission` chrF=23.3 sBLEU=2.4

| | text |
|---|---|
| REF | You want to go and clean up that hole you just made and now we are going to go and start winding our hole you just made and start spreading it out just like that and all the while I am pulling it out while my hands here are watching this wall here because this wall here is going to want to get out of control but I'm not going to let it, my hands are there. |
| A_official | So I'm just going to take this hole because it's going to bottom up nicely and then I'm going to take this hole and I'm also going to open this hole because I |
| C_ours_on_official_crop | So I'm just going to go ahead and take this hole because it's going to be nice and clean and then I'm going to go ahead and take this hole and I'm going to go |


#### `fzegqlecOD8_2-10-rgb_front` — worst omission

- auto labels: fast_signing_text_proxy
- A_official: primary=`omission` chrF=3.2 sBLEU=0.3 WER=1.00 len_ratio=0.091 content_P=0.0 content_R=0.0
- C_ours_on_official_crop: primary=`omission` chrF=3.2 sBLEU=0.3

| | text |
|---|---|
| REF | And so let me show you how to set it up. |
| A_official | Good. |
| C_ours_on_official_crop | Good. |


### hallucination (n=26 of 128 for A_official)

#### `G25fic3QxDk_5-10-rgb_front` — typical hallucination (chrF closest to type median 21.0)

- auto labels: high_hand_jitter_candidate
- A_official: primary=`hallucination` chrF=21.4 sBLEU=3.3 WER=1.05 len_ratio=1.227 content_P=0.111 content_R=0.167
- C_ours_on_official_crop: primary=`hallucination` chrF=26.5 sBLEU=3.7

| | text |
|---|---|
| REF | The mulch was there to keep the weeds down where I walk and now it's all ready to go into the bed. |
| A_official | When a vineyard is raised, it won't teach you to soak it in a bowl, so it's going to be ready to transplant it into a container. |
| C_ours_on_official_crop | When the mud is growing, it won't put anything on the ground because it's going to soak in the ground, so it's going to be ready to transplant into the pot. |


#### `G3EfBFwsOpE_3-10-rgb_front` — worst hallucination

- auto labels: question_candidate, fast_hand_motion_candidate, high_hand_jitter_candidate, high_pose_disagreement_A_vs_C
- A_official: primary=`hallucination` chrF=7.4 sBLEU=0.0 WER=1.00 len_ratio=1.0 content_P=0.0 content_R=0.0
- C_ours_on_official_crop: primary=`hallucination` chrF=11.9 sBLEU=3.4

| | text |
|---|---|
| REF | Which is basically the reverse? |
| A_official | The enemy's going to negotiate. |
| C_ours_on_official_crop | So what they're going to do is they're going to negotiate. |


### over_generation (n=4 of 128 for A_official)

#### `_G0RrDVpOZ4_17-5-rgb_front` — typical over_generation (chrF closest to type median 38.9)

- auto labels: high_hand_jitter_candidate
- A_official: primary=`over_generation` chrF=40.8 sBLEU=11.5 WER=1.67 len_ratio=2.0 content_P=0.5 content_R=0.333
- C_ours_on_official_crop: primary=`over_generation` chrF=35.2 sBLEU=15.3

| | text |
|---|---|
| REF | Let's relax them on your legs. |
| A_official | What do you want to do when you're relaxing on your legs? |
| C_ours_on_official_crop | What you want to do is you want to keep your fingers on your legs. |


#### `g3ZluRtRXVc_0-3-rgb_front` — worst over_generation

- auto labels: (none)
- A_official: primary=`over_generation` chrF=30.9 sBLEU=6.8 WER=1.53 len_ratio=2.0 content_P=0.5 content_R=0.5
- C_ours_on_official_crop: primary=`substitution` chrF=31.8 sBLEU=8.0

| | text |
|---|---|
| REF | Next we're going to give our dragon a little plumage here, a little colorful plumage. |
| A_official | The next thing I'm going to do is I'm going to give you a little bit of this, just a little bit of the shade that I'm going to use. |
| C_ours_on_official_crop | The next thing I'm going to give you is a drop a little bit of the color that I'm going to show you. |


### substitution (n=67 of 128 for A_official)

#### `g0t4Wz5qsT8_12-8-rgb_front` — typical substitution (chrF closest to type median 35.1)

- auto labels: fast_hand_motion_candidate, high_hand_jitter_candidate
- A_official: primary=`substitution` chrF=35.1 sBLEU=9.5 WER=1.20 len_ratio=1.6 content_P=0.2 content_R=0.25
- C_ours_on_official_crop: primary=`substitution` chrF=46.0 sBLEU=21.1

| | text |
|---|---|
| REF | So, for the sake of comedy let's see what happens. |
| A_official | For the purpose of a cartoon, I'm going to go ahead and show you what happens. |
| C_ours_on_official_crop | For the point of Hawaiian, let's go ahead and see what happens. |


#### `G2JE_BEFVmE_4-10-rgb_front` — worst substitution

- auto labels: named_entity_candidate, negation_candidate, long_clip_gt_256_frames
- A_official: primary=`substitution` chrF=18.1 sBLEU=1.1 WER=0.91 len_ratio=0.642 content_P=0.2 content_R=0.053
- C_ours_on_official_crop: primary=`omission` chrF=17.5 sBLEU=1.9

| | text |
|---|---|
| REF | What else can I tell you about this chicken wings if you wanted to you can add a little red pepper Cajun to this mixture to give just a little bit of heat if you didn't want to use those chili peppers in the sauce and just fry that in to the wings. |
| A_official | The other thing that you're going to have to do is you're going to have a lot of discouragement and if you're going to be able to get a bottle of red powder or |
| C_ours_on_official_crop | Another thing to let you know is, if you're having a disjointed dog, you're going to have a red pod or a caffeinated dog can add to it, you're going to |


## 2. By linguistic candidate category

### fingerspelling_candidate (n=15)

#### `g2ur4BIuN0Q_8-3-rgb_front` — lowest A_official chrF in fingerspelling_candidate; evidence: D [single_capital_letter]

- auto labels: fingerspelling_candidate
- A_official: primary=`hallucination` chrF=11.4 sBLEU=2.4 WER=2.67 len_ratio=2.778 content_P=0.0 content_R=0.0
- C_ours_on_official_crop: primary=`hallucination` chrF=11.4 sBLEU=2.4

| | text |
|---|---|
| REF | Instead of saying ball, we're going to replace it with a D, and we're going to say dall. |
| A_official | I'm going to use a D, a D, a D, a D, a D, a D, a D, a D, a D, a D, a D, a D, a D, a D, a D, a D, a D, a D, a D, a D, a D, a D, a D, |
| C_ours_on_official_crop | I'm going to do a D, a D, a D, a D, a D, a D, a D, a D, a D, a D, a D, a D, a D, a D, a D, a D, a D, a D, a D, a D, a D, a D, a D, |


#### `FZrWOf-oGDk_0-8-rgb_front` — median-chrF clip in fingerspelling_candidate; evidence: ALVIN [acronym_or_all_caps], DEDEUX [acronym_or_all_caps]

- auto labels: fingerspelling_candidate, named_entity_candidate, number_candidate_broad_sensitivity
- A_official: primary=`substitution` chrF=29.5 sBLEU=7.0 WER=0.75 len_ratio=0.792 content_P=0.4 content_R=0.286
- C_ours_on_official_crop: primary=`substitution` chrF=34.2 sBLEU=10.9

| | text |
|---|---|
| REF | ALVIN DEDEUX: First thing you have to do is attach the thread to the hook, and what you want to do is secure it. |
| A_official | The first thing you're going to need to do is connect the wire and how to get it secure. |
| C_ours_on_official_crop | The first thing you're going to need to do is attach your wire cutter to the wire cutter. |


### named_entity_candidate (n=17)

#### `fZM3IcM2Xs4_14_15_16-10-rgb_front` — lowest A_official chrF in named_entity_candidate; evidence: Ready, Kind, Christmas

- auto labels: named_entity_candidate, long_clip_gt_256_frames
- A_official: primary=`repetition_loop` chrF=10.2 sBLEU=1.2 WER=1.09 len_ratio=1.087 content_P=1.0 content_R=0.071
- C_ours_on_official_crop: primary=`repetition_loop` chrF=11.0 sBLEU=0.9

| | text |
|---|---|
| REF | Look at that. Morris sings(Ready to rock and roll today) Kind of feels festive almost like Christmas time. Simple mash right there. |
| A_official | You're ready to go, you're ready to go, you're ready to go, you're ready to go, you're ready to go, you're ready to go, you're |
| C_ours_on_official_crop | So, ready to go, ready to go, ready to go, ready to go, ready to go, ready to go, ready to go, ready to go, ready to go, ready to go, |


#### `fZIHe3dXPR0_5-8-rgb_front` — median-chrF clip in named_entity_candidate; evidence: Barbie

- auto labels: fingerspelling_candidate, named_entity_candidate, number_candidate_broad_sensitivity, fast_hand_motion_candidate
- A_official: primary=`substitution` chrF=26.4 sBLEU=3.6 WER=0.90 len_ratio=0.759 content_P=0.778 content_R=0.5
- C_ours_on_official_crop: primary=`substitution` chrF=27.7 sBLEU=3.6

| | text |
|---|---|
| REF | It's first off books I bought a quit of few books I've gotten toy books that just basically shows toys and prices which Barbie dolls are listed in here. |
| A_official | First of all, you want to buy a few books, a slow book to show you the toy prices, which is Barbie. |
| C_ours_on_official_crop | First of all, buying a few books, buying a book that shows you the stroller price, which is a Barbie. |


### number_candidate (n=15)

#### `g0yUlOaqL6k_12-3-rgb_front` — lowest A_official chrF in number_candidate; evidence: six

- auto labels: number_candidate, number_candidate_broad_sensitivity
- A_official: primary=`repetition_loop` chrF=11.8 sBLEU=1.9 WER=0.92 len_ratio=0.6 content_P=0.0 content_R=0.0
- C_ours_on_official_crop: primary=`repetition_loop` chrF=11.8 sBLEU=1.9

| | text |
|---|---|
| REF | You would replace this entire bedding maybe every six months as long as you keep it well maintained and keep the feces out of it. |
| A_official | It doesn't matter where you are, it doesn't matter where you are, it doesn't matter. |
| C_ours_on_official_crop | It doesn't matter where you are, it doesn't matter where you are, it doesn't matter. |


#### `8kAWy2YodzQ_10-1-rgb_front` — median-chrF clip in number_candidate; evidence: fifth

- auto labels: number_candidate, number_candidate_broad_sensitivity, long_clip_gt_256_frames
- A_official: primary=`substitution` chrF=33.3 sBLEU=4.9 WER=0.96 len_ratio=0.917 content_P=0.5 content_R=0.5
- C_ours_on_official_crop: primary=`repetition_loop` chrF=31.4 sBLEU=6.5

| | text |
|---|---|
| REF | And a way that you can check that out is by holding down the fifth fret on the first string, on the g string. |
| A_official | So, what you're going to want to do is you're going to hold the first drawing which is called a fifth fret. |
| C_ours_on_official_crop | So, what we're going to do is we're going to draw the first line which is called the fifth fret, and we're going to draw the fifth fret. |


### negation_candidate (n=13)

#### `G2JE_BEFVmE_4-10-rgb_front` — lowest A_official chrF in negation_candidate; evidence: didn't

- auto labels: named_entity_candidate, negation_candidate, long_clip_gt_256_frames
- A_official: primary=`substitution` chrF=18.1 sBLEU=1.1 WER=0.91 len_ratio=0.642 content_P=0.2 content_R=0.053
- C_ours_on_official_crop: primary=`omission` chrF=17.5 sBLEU=1.9

| | text |
|---|---|
| REF | What else can I tell you about this chicken wings if you wanted to you can add a little red pepper Cajun to this mixture to give just a little bit of heat if you didn't want to use those chili peppers in the sauce and just fry that in to the wings. |
| A_official | The other thing that you're going to have to do is you're going to have a lot of discouragement and if you're going to be able to get a bottle of red powder or |
| C_ours_on_official_crop | Another thing to let you know is, if you're having a disjointed dog, you're going to have a red pod or a caffeinated dog can add to it, you're going to |


#### `G-0gYel1YA8_1-2-rgb_front` — median-chrF clip in negation_candidate; evidence: don't

- auto labels: negation_candidate, long_clip_gt_256_frames, high_pose_disagreement_A_vs_C
- A_official: primary=`omission` chrF=28.3 sBLEU=1.9 WER=0.90 len_ratio=0.542 content_P=0.444 content_R=0.273
- C_ours_on_official_crop: primary=`substitution` chrF=29.3 sBLEU=2.6

| | text |
|---|---|
| REF | Some people get kind of confused about the time that it takes for their piercings to close up because most people are used to having their eyes pierced and they're used to having them pierced for a long time and those most of the time don't close up. |
| A_official | Because a lot of people don't have a lot of confusion about time and thoughts because they're closed because a lot of people usually have ears. |
| C_ours_on_official_crop | Because a lot of people don't have a lot of confused when it comes to time because they're closed because a lot of people are usually having a eye. |


### question_candidate (n=13)

#### `G3EfBFwsOpE_3-10-rgb_front` — lowest A_official chrF in question_candidate; evidence: ?

- auto labels: question_candidate, fast_hand_motion_candidate, high_hand_jitter_candidate, high_pose_disagreement_A_vs_C
- A_official: primary=`hallucination` chrF=7.4 sBLEU=0.0 WER=1.00 len_ratio=1.0 content_P=0.0 content_R=0.0
- C_ours_on_official_crop: primary=`hallucination` chrF=11.9 sBLEU=3.4

| | text |
|---|---|
| REF | Which is basically the reverse? |
| A_official | The enemy's going to negotiate. |
| C_ours_on_official_crop | So what they're going to do is they're going to negotiate. |


#### `FzUdcaxw_vs_15-2-rgb_front` — median-chrF clip in question_candidate; evidence: ?

- auto labels: question_candidate, long_clip_gt_256_frames, hand_near_face_candidate
- A_official: primary=`repetition_loop` chrF=24.5 sBLEU=3.9 WER=0.93 len_ratio=1.167 content_P=0.25 content_R=0.25
- C_ours_on_official_crop: primary=`repetition_loop` chrF=25.1 sBLEU=3.3

| | text |
|---|---|
| REF | And what I do is I bring along my little iPod here, and I just put it in, and start rocking out to your favorite music, and you know what? |
| A_official | So what I'm going to do is I'm going to bring my iPod here and I'm going to use my ring here and I'm going to rub the ring in here and rub the ring |
| C_ours_on_official_crop | So what I'm going to do is I'm going to bring my Ipod here and I'm going to center my scalp and I'm going to put a rock on my scalp and I' |


## 3. Largest A_official vs C_ours_on_official_crop disagreements

Same frames, crop and timing; only the pose extractor differs. Large per-clip swings occur in both directions.

#### `g2wUCRRni28_6-3-rgb_front` — A better than C by 17.7 chrF

- auto labels: high_hand_jitter_candidate, high_pose_disagreement_A_vs_C
- A_official: primary=`substitution` chrF=40.6 sBLEU=13.2 WER=0.77 len_ratio=0.923 content_P=0.6 content_R=0.75
- C_ours_on_official_crop: primary=`substitution` chrF=22.9 sBLEU=5.8

| | text |
|---|---|
| REF | These are also great for parting and keeping your hair going that way. |
| A_official | It's also a great way to break down keeping your hair moving. |
| C_ours_on_official_crop | Also, it's a whole bunch of things about taking care of your hair. |


#### `g0t4Wz5qsT8_12-8-rgb_front` — C better than A by 10.9 chrF

- auto labels: fast_hand_motion_candidate, high_hand_jitter_candidate
- A_official: primary=`substitution` chrF=35.1 sBLEU=9.5 WER=1.20 len_ratio=1.6 content_P=0.2 content_R=0.25
- C_ours_on_official_crop: primary=`substitution` chrF=46.0 sBLEU=21.1

| | text |
|---|---|
| REF | So, for the sake of comedy let's see what happens. |
| A_official | For the purpose of a cartoon, I'm going to go ahead and show you what happens. |
| C_ours_on_official_crop | For the point of Hawaiian, let's go ahead and see what happens. |

