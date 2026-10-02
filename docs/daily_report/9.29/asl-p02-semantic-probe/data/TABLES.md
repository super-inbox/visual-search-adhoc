## t5enc — frozen (gallery 147; chance R@1 0.7%, R@5 3.4%, R@10 6.8%, median rank 74, 4-way 25%)

| State | Representation | Pool | R@1 | R@5 | R@10 [95% CI] | Med. rank | 4-way random | 4-way len-matched [95% CI] |
|---|---|---|---:|---:|---:|---:|---:|---:|
| init | Block 2 | mean | 2.7 | 11.6 | 17.0 [11.5–23.1] | 37 | 39.5 | 36.7 [29.4–44.8] |
| init | Block 4 | mean | 1.4 | 11.6 | 19.7 [13.6–26.5] | 35 | 43.5 | 38.8 [31.3–46.8] |
| init | Bridge GELU | mean | 0.7 | 10.2 | 21.1 [15.0–27.9] | 39 | 40.8 | 35.4 [28.1–43.4] |
| init | T5 input | mean | 0.7 | 8.8 | 21.1 [15.0–27.9] | 41 | 38.8 | 35.4 [28.1–43.4] |
| ep5 | Block 2 | mean | 1.4 | 9.5 | 20.4 [14.3–26.5] | 38 | 42.2 | 35.4 [28.1–43.4] |
| ep5 | Block 4 | mean | 1.4 | 6.8 | 17.0 [10.9–23.1] | 40 | 39.5 | 37.4 [30.0–45.5] |
| ep5 | Bridge GELU | mean | 0.7 | 10.9 | 17.0 [10.9–23.1] | 45 | 36.7 | 33.3 [26.2–41.3] |
| ep5 | T5 input | mean | 1.4 | 10.9 | 19.7 [13.6–25.9] | 44 | 38.1 | 34.0 [26.8–42.0] |
| ep18 | Block 2 | mean | 1.4 | 12.2 | 21.1 [14.3–27.9] | 35 | 39.5 | 36.1 [28.7–44.1] |
| ep18 | Block 4 | mean | 1.4 | 11.6 | 19.7 [13.6–26.5] | 37 | 41.5 | 37.4 [30.0–45.5] |
| ep18 | Bridge GELU | mean | 1.4 | 9.5 | 16.3 [10.2–22.4] | 44 | 41.5 | 36.7 [29.4–44.8] |
| ep18 | T5 input | mean | 2.0 | 9.5 | 15.6 [10.2–21.8] | 49 | 40.1 | 36.1 [28.7–44.1] |
| ep28 | Block 2 | mean | 1.4 | 15.0 | 20.4 [14.3–26.5] | 36 | 42.9 | 36.1 [28.7–44.1] |
| ep28 | Block 4 | mean | 1.4 | 11.6 | 20.4 [14.3–27.2] | 41 | 43.5 | 37.4 [30.0–45.5] |
| ep28 | Bridge GELU | mean | 2.7 | 11.6 | 16.3 [10.2–22.4] | 44 | 38.1 | 29.9 [23.1–37.8] |
| ep28 | T5 input | mean | 2.0 | 10.9 | 17.7 [11.6–23.8] | 42 | 39.5 | 30.6 [23.7–38.5] |
| ep18 | Block 2 | mean+std | 0.7 | 12.2 | 21.1 [15.0–27.9] | 39 | 42.9 | 39.5 [31.9–47.5] |
| ep18 | Block 4 | mean+std | 1.4 | 9.5 | 17.0 [10.9–23.1] | 41 | 39.5 | 33.3 [26.2–41.3] |
| ep18 | T5 input | mean+std | 1.4 | 10.2 | 14.3 [8.8–20.4] | 39 | 40.8 | 35.4 [28.1–43.4] |
| ep28 | Block 2 | mean+std | 2.0 | 12.9 | 21.1 [14.3–27.2] | 34 | 39.5 | 37.4 [30.0–45.5] |
| ep28 | Block 4 | mean+std | 1.4 | 15.6 | 21.8 [15.0–28.6] | 36 | 43.5 | 36.7 [29.4–44.8] |
| ep28 | T5 input | mean+std | 2.7 | 11.6 | 17.7 [11.6–24.5] | 42 | 38.8 | 32.7 [25.6–40.6] |
| nuisance | length (log raw frames, log model-input T) | - | 2.0 | 8.2 | 18.4 [12.2–25.2] | 34 | 46.9 | 32.0 [25.0–39.9] |
| nuisance | normalised landmarks: mean over time (501) | - | 3.4 | 12.2 | 23.1 [16.3–29.9] | 36 | 38.1 | 40.1 [32.6–48.2] |
| nuisance | normalised landmarks: mean+std over time (1002) | - | 1.4 | 15.0 | 27.9 [21.1–35.4] | 25 | 46.9 | 42.9 [35.1–50.9] |
| ep18 | Block 2 | CONTROL: train pairs shuffled | 2.0 | 3.4 | 5.4 | 66 | 23.8 | 27.2 |
| ep18 | Block 4 | CONTROL: train pairs shuffled | 1.4 | 4.8 | 6.1 | 66 | 26.5 | 28.6 |
| ep18 | T5 input | CONTROL: train pairs shuffled | 0.7 | 4.8 | 6.8 | 67 | 25.9 | 23.8 |
| ep28 | Block 2 | CONTROL: train pairs shuffled | 2.0 | 4.1 | 6.8 | 69 | 22.4 | 27.2 |
| ep28 | Block 4 | CONTROL: train pairs shuffled | 0.7 | 4.1 | 8.8 | 73 | 22.4 | 27.2 |
| ep28 | T5 input | CONTROL: train pairs shuffled | 0.0 | 5.4 | 7.5 | 68 | 27.2 | 27.9 |

## t5enc — val (gallery 366; chance R@1 0.3%, R@5 1.4%, R@10 2.7%, median rank 184, 4-way 25%)

| State | Representation | Pool | R@1 | R@5 | R@10 [95% CI] | Med. rank | 4-way random | 4-way len-matched [95% CI] |
|---|---|---|---:|---:|---:|---:|---:|---:|
| init | Block 2 | mean | 1.9 | 6.8 | 10.7 [7.7–13.9] | 74 | 50.0 | 38.3 [33.4–43.3] |
| init | Block 4 | mean | 1.6 | 6.0 | 7.9 [5.2–10.9] | 82 | 49.2 | 37.4 [32.6–42.5] |
| init | Bridge GELU | mean | 1.4 | 5.7 | 9.3 [6.6–12.3] | 80 | 47.5 | 38.8 [33.9–43.9] |
| init | T5 input | mean | 1.4 | 5.5 | 9.3 [6.6–12.6] | 81 | 47.8 | 37.4 [32.6–42.5] |
| ep5 | Block 2 | mean | 0.8 | 6.0 | 9.0 [6.3–12.0] | 87 | 43.7 | 35.0 [30.3–40.0] |
| ep5 | Block 4 | mean | 1.6 | 6.3 | 8.7 [6.3–11.7] | 82 | 44.3 | 36.6 [31.8–41.7] |
| ep5 | Bridge GELU | mean | 1.4 | 5.7 | 9.3 [6.3–12.3] | 87 | 43.7 | 34.2 [29.5–39.2] |
| ep5 | T5 input | mean | 1.1 | 6.0 | 9.8 [6.8–12.8] | 86 | 43.7 | 35.8 [31.1–40.8] |
| ep18 | Block 2 | mean | 0.8 | 5.2 | 7.9 [5.2–10.7] | 88 | 44.3 | 34.2 [29.5–39.2] |
| ep18 | Block 4 | mean | 1.1 | 5.2 | 9.0 [6.3–11.8] | 92 | 46.4 | 36.6 [31.8–41.7] |
| ep18 | Bridge GELU | mean | 1.9 | 6.3 | 9.3 [6.6–12.0] | 91 | 43.2 | 36.6 [31.8–41.7] |
| ep18 | T5 input | mean | 1.9 | 5.7 | 9.3 [6.6–12.3] | 88 | 43.4 | 33.9 [29.2–38.9] |
| ep28 | Block 2 | mean | 1.4 | 6.3 | 10.1 [7.1–13.1] | 88 | 45.9 | 34.7 [30.0–39.7] |
| ep28 | Block 4 | mean | 0.8 | 5.7 | 12.3 [9.0–15.6] | 86 | 44.8 | 37.2 [32.4–42.2] |
| ep28 | Bridge GELU | mean | 1.1 | 5.7 | 11.5 [8.2–14.5] | 89 | 43.2 | 36.3 [31.6–41.4] |
| ep28 | T5 input | mean | 1.1 | 6.8 | 11.5 [8.2–14.5] | 91 | 42.9 | 37.2 [32.4–42.2] |
| ep18 | Block 2 | mean+std | 1.1 | 5.7 | 8.7 [6.0–11.5] | 82 | 47.5 | 36.6 [31.8–41.7] |
| ep18 | Block 4 | mean+std | 1.6 | 4.6 | 9.3 [6.6–12.0] | 86 | 45.1 | 35.5 [30.8–40.5] |
| ep18 | T5 input | mean+std | 2.2 | 6.3 | 9.0 [6.3–11.7] | 94 | 44.8 | 33.3 [28.7–38.3] |
| ep28 | Block 2 | mean+std | 0.3 | 5.7 | 9.8 [6.8–12.8] | 90 | 47.5 | 36.6 [31.8–41.7] |
| ep28 | Block 4 | mean+std | 1.4 | 6.3 | 10.4 [7.4–13.4] | 84 | 46.4 | 37.2 [32.4–42.2] |
| ep28 | T5 input | mean+std | 0.5 | 6.3 | 11.2 [7.9–14.2] | 83 | 44.3 | 38.0 [33.2–43.1] |
| nuisance | length (log raw frames, log model-input T) | - | 0.5 | 4.1 | 6.3 [4.1–8.7] | 95 | 44.3 | 24.6 [20.5–29.3] |
| nuisance | normalised landmarks: mean over time (501) | - | 1.1 | 8.5 | 13.9 [10.7–17.5] | 72 | 47.3 | 39.1 [34.2–44.2] |
| nuisance | normalised landmarks: mean+std over time (1002) | - | 1.9 | 9.0 | 14.8 [11.2–18.3] | 70 | 51.6 | 42.9 [37.9–48.0] |
| ep18 | Block 2 | CONTROL: train pairs shuffled | 0.8 | 1.6 | 3.0 | 169 | 26.5 | 24.3 |
| ep18 | Block 4 | CONTROL: train pairs shuffled | 0.3 | 1.6 | 2.7 | 164 | 28.4 | 25.7 |
| ep18 | T5 input | CONTROL: train pairs shuffled | 0.3 | 1.4 | 1.6 | 186 | 23.8 | 24.0 |
| ep28 | Block 2 | CONTROL: train pairs shuffled | 0.5 | 1.4 | 3.0 | 174 | 27.3 | 25.7 |
| ep28 | Block 4 | CONTROL: train pairs shuffled | 0.5 | 1.1 | 4.4 | 163 | 29.0 | 23.0 |
| ep28 | T5 input | CONTROL: train pairs shuffled | 0.3 | 1.6 | 3.3 | 164 | 28.1 | 20.5 |

## tfidf — frozen (gallery 147; chance R@1 0.7%, R@5 3.4%, R@10 6.8%, median rank 74, 4-way 25%)

| State | Representation | Pool | R@1 | R@5 | R@10 [95% CI] | Med. rank | 4-way random | 4-way len-matched [95% CI] |
|---|---|---|---:|---:|---:|---:|---:|---:|
| init | Block 2 | mean | 2.7 | 8.2 | 15.6 [9.5–21.8] | 43 | 36.1 | 33.3 [26.2–41.3] |
| init | Block 4 | mean | 1.4 | 5.4 | 12.9 [8.2–18.4] | 45 | 33.3 | 31.3 [24.4–39.2] |
| init | Bridge GELU | mean | 0.7 | 6.8 | 11.6 [6.8–17.0] | 56 | 33.3 | 29.9 [23.1–37.8] |
| init | T5 input | mean | 1.4 | 6.8 | 10.9 [6.1–15.6] | 49 | 29.3 | 29.9 [23.1–37.8] |
| ep5 | Block 2 | mean | 2.0 | 7.5 | 13.6 [8.2–19.7] | 46 | 33.3 | 27.9 [21.3–35.6] |
| ep5 | Block 4 | mean | 0.7 | 4.1 | 13.6 [8.8–19.1] | 52 | 24.5 | 25.2 [18.8–32.8] |
| ep5 | Bridge GELU | mean | 0.0 | 7.5 | 12.2 [6.8–18.4] | 50 | 29.3 | 32.0 [25.0–39.9] |
| ep5 | T5 input | mean | 0.0 | 8.2 | 13.6 [8.8–19.7] | 58 | 26.5 | 29.3 [22.5–37.1] |
| ep18 | Block 2 | mean | 1.4 | 11.6 | 14.3 [8.8–20.4] | 46 | 31.3 | 32.7 [25.6–40.6] |
| ep18 | Block 4 | mean | 2.0 | 8.8 | 15.0 [8.8–21.1] | 52 | 27.9 | 31.3 [24.4–39.2] |
| ep18 | Bridge GELU | mean | 0.0 | 8.2 | 15.6 [9.5–21.8] | 55 | 27.2 | 29.9 [23.1–37.8] |
| ep18 | T5 input | mean | 0.0 | 8.8 | 17.0 [10.9–23.1] | 60 | 30.6 | 30.6 [23.7–38.5] |
| ep28 | Block 2 | mean | 2.0 | 9.5 | 15.6 [9.5–21.8] | 51 | 34.0 | 32.0 [25.0–39.9] |
| ep28 | Block 4 | mean | 2.0 | 7.5 | 14.3 [8.8–19.7] | 53 | 32.0 | 29.3 [22.5–37.1] |
| ep28 | Bridge GELU | mean | 1.4 | 9.5 | 14.3 [8.8–19.7] | 54 | 29.9 | 29.3 [22.5–37.1] |
| ep28 | T5 input | mean | 1.4 | 9.5 | 15.0 [9.5–21.1] | 53 | 29.9 | 29.3 [22.5–37.1] |
| ep18 | Block 2 | mean+std | 0.7 | 7.5 | 15.6 [10.2–21.8] | 57 | 30.6 | 33.3 [26.2–41.3] |
| ep18 | Block 4 | mean+std | 2.0 | 8.2 | 14.3 [8.8–20.4] | 52 | 24.5 | 27.9 [21.3–35.6] |
| ep18 | T5 input | mean+std | 2.7 | 7.5 | 12.2 [6.8–17.7] | 53 | 28.6 | 29.9 [23.1–37.8] |
| ep28 | Block 2 | mean+std | 2.7 | 8.8 | 14.3 [8.8–20.4] | 55 | 34.0 | 29.3 [22.5–37.1] |
| ep28 | Block 4 | mean+std | 1.4 | 10.2 | 15.0 [8.8–21.1] | 52 | 31.3 | 27.9 [21.3–35.6] |
| ep28 | T5 input | mean+std | 2.0 | 10.2 | 15.0 [9.5–20.4] | 60 | 29.3 | 30.6 [23.7–38.5] |
| nuisance | length (log raw frames, log model-input T) | - | 1.4 | 5.4 | 13.6 [8.2–19.0] | 50 | 34.7 | 24.5 [18.2–32.0] |
| nuisance | normalised landmarks: mean over time (501) | - | 2.0 | 8.2 | 17.0 [11.6–23.8] | 51 | 36.7 | 34.7 [27.5–42.7] |
| nuisance | normalised landmarks: mean+std over time (1002) | - | 2.7 | 7.5 | 12.2 [7.5–17.0] | 43 | 38.8 | 32.0 [25.0–39.9] |

## tfidf — val (gallery 366; chance R@1 0.3%, R@5 1.4%, R@10 2.7%, median rank 184, 4-way 25%)

| State | Representation | Pool | R@1 | R@5 | R@10 [95% CI] | Med. rank | 4-way random | 4-way len-matched [95% CI] |
|---|---|---|---:|---:|---:|---:|---:|---:|
| init | Block 2 | mean | 1.4 | 4.4 | 7.9 [5.2–10.9] | 98 | 42.6 | 37.2 [32.4–42.2] |
| init | Block 4 | mean | 1.4 | 5.5 | 7.1 [4.6–9.8] | 94 | 42.3 | 32.8 [28.2–37.8] |
| init | Bridge GELU | mean | 1.4 | 4.4 | 7.4 [4.9–10.1] | 115 | 39.6 | 28.1 [23.8–33.0] |
| init | T5 input | mean | 1.6 | 4.6 | 7.7 [4.9–10.7] | 116 | 38.0 | 29.0 [24.6–33.8] |
| ep5 | Block 2 | mean | 1.4 | 4.6 | 6.6 [4.4–9.0] | 111 | 38.8 | 31.4 [26.9–36.3] |
| ep5 | Block 4 | mean | 1.6 | 3.8 | 6.0 [3.8–8.5] | 115 | 39.3 | 30.9 [26.4–35.8] |
| ep5 | Bridge GELU | mean | 1.4 | 3.0 | 5.7 [3.6–7.9] | 118 | 39.1 | 26.5 [22.2–31.3] |
| ep5 | T5 input | mean | 1.4 | 3.3 | 5.5 [3.3–7.9] | 119 | 39.3 | 27.0 [22.8–31.8] |
| ep18 | Block 2 | mean | 1.1 | 3.0 | 6.3 [3.8–8.7] | 109 | 39.3 | 32.0 [27.4–36.9] |
| ep18 | Block 4 | mean | 0.5 | 2.7 | 5.2 [3.0–7.4] | 114 | 38.0 | 27.9 [23.5–32.7] |
| ep18 | Bridge GELU | mean | 0.5 | 2.7 | 5.7 [3.6–8.2] | 123 | 38.5 | 24.9 [20.7–29.5] |
| ep18 | T5 input | mean | 0.8 | 3.3 | 5.7 [3.6–8.2] | 120 | 38.3 | 24.0 [19.9–28.7] |
| ep28 | Block 2 | mean | 1.6 | 4.4 | 6.3 [3.8–8.7] | 110 | 37.4 | 30.9 [26.4–35.8] |
| ep28 | Block 4 | mean | 1.1 | 4.4 | 6.8 [4.4–9.3] | 116 | 36.6 | 29.2 [24.8–34.1] |
| ep28 | Bridge GELU | mean | 1.1 | 3.0 | 5.5 [3.3–7.9] | 112 | 35.0 | 29.0 [24.6–33.8] |
| ep28 | T5 input | mean | 0.8 | 3.6 | 5.2 [3.3–7.7] | 113 | 36.6 | 29.5 [25.1–34.4] |
| ep18 | Block 2 | mean+std | 0.8 | 3.8 | 6.0 [3.8–8.5] | 104 | 38.5 | 28.7 [24.3–33.5] |
| ep18 | Block 4 | mean+std | 0.5 | 2.7 | 4.6 [2.7–6.8] | 108 | 39.3 | 27.3 [23.0–32.1] |
| ep18 | T5 input | mean+std | 0.5 | 3.0 | 4.9 [2.7–7.4] | 109 | 38.8 | 27.3 [23.0–32.1] |
| ep28 | Block 2 | mean+std | 1.1 | 4.9 | 8.7 [6.0–11.5] | 116 | 37.7 | 28.4 [24.0–33.2] |
| ep28 | Block 4 | mean+std | 0.8 | 2.7 | 6.3 [4.1–8.7] | 108 | 40.2 | 27.9 [23.5–32.7] |
| ep28 | T5 input | mean+std | 0.5 | 3.3 | 6.3 [4.1–8.7] | 112 | 37.2 | 30.1 [25.6–34.9] |
| nuisance | length (log raw frames, log model-input T) | - | 0.8 | 3.0 | 6.3 [3.8–8.7] | 110 | 37.4 | 24.9 [20.7–29.5] |
| nuisance | normalised landmarks: mean over time (501) | - | 1.1 | 6.6 | 11.5 [8.2–14.8] | 98 | 43.7 | 45.1 [40.1–50.2] |
| nuisance | normalised landmarks: mean+std over time (1002) | - | 2.7 | 7.7 | 12.3 [9.3–15.6] | 91 | 47.0 | 43.2 [38.2–48.3] |

## Model-native decoder scoring (frozen, no probe)

| State | Scoring | R@1 | R@5 | R@10 | Med. rank | 4-way random | 4-way len-matched |
|---|---|---:|---:|---:|---:|---:|---:|
| init | raw -NLL | 0.7 | 2.0 | 7.5 | 77 | 32.0 | 25.2 |
| init | -NLL minus text prior (column-centred) | 0.0 | 1.4 | 1.4 | 79 | 24.5 | 23.8 |
| ep5 | raw -NLL | 0.7 | 3.4 | 6.8 | 72 | 23.8 | 25.2 |
| ep5 | -NLL minus text prior (column-centred) | 1.4 | 6.1 | 11.6 | 50 | 30.6 | 28.6 |
| ep18 | raw -NLL | 0.0 | 4.1 | 7.5 | 71 | 25.9 | 27.2 |
| ep18 | -NLL minus text prior (column-centred) | 1.4 | 6.8 | 12.9 | 45 | 42.2 | 32.0 |
| ep28 | raw -NLL | 0.0 | 3.4 | 8.2 | 66 | 25.9 | 27.2 |
| ep28 | -NLL minus text prior (column-centred) | 1.4 | 6.8 | 16.3 | 41 | 42.2 | 31.3 |

## Video identity (nuisance): frozen clips whose nearest neighbour (standardised, cosine) is a different clip from the same source video

| State | Representation | NN same video | approx. chance |
|---|---|---:|---:|
| init | Block 2 | 15.8% (n=38) | 0.7% |
| init | Block 4 | 15.8% (n=38) | 0.7% |
| init | Bridge GELU | 15.8% (n=38) | 0.7% |
| init | T5 input | 15.8% (n=38) | 0.7% |
| ep5 | Block 2 | 13.2% (n=38) | 0.7% |
| ep5 | Block 4 | 7.9% (n=38) | 0.7% |
| ep5 | Bridge GELU | 7.9% (n=38) | 0.7% |
| ep5 | T5 input | 7.9% (n=38) | 0.7% |
| ep18 | Block 2 | 10.5% (n=38) | 0.7% |
| ep18 | Block 4 | 7.9% (n=38) | 0.7% |
| ep18 | Bridge GELU | 7.9% (n=38) | 0.7% |
| ep18 | T5 input | 7.9% (n=38) | 0.7% |
| ep28 | Block 2 | 7.9% (n=38) | 0.7% |
| ep28 | Block 4 | 10.5% (n=38) | 0.7% |
| ep28 | Bridge GELU | 13.2% (n=38) | 0.7% |
| ep28 | T5 input | 13.2% (n=38) | 0.7% |
| nuisance | length (log raw frames, log model-input T) | 0.0% (n=38) | 0.7% |
| nuisance | normalised landmarks: mean over time (501) | 18.4% (n=38) | 0.7% |
| nuisance | normalised landmarks: mean+std over time (1002) | 23.7% (n=38) | 0.7% |
