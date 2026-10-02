## t5enc: length-matched 4-way (chance 25%) and R@10 (chance val 2.7%, frozen 6.8%)

| Group | Feature | Control | d | Val 4-way [95% CI] | Frozen 4-way [95% CI] | Val R@10 | Frozen R@10 | Frozen R@1 / R@5 / med. rank | Δ vs all/pos, val 4-way | Δ vs all/pos, frozen 4-way |
|---|---|---|---:|---:|---:|---:|---:|---:|---:|---:|
| left_hand | pos | none | 126 | 31.7 [27.1–36.6] | 32.7 [25.6–40.6] | 8.2 | 12.2 | 0.7 / 6.1 / 43 | -11.2 [-17.2, -5.2]* | -10.2 [-18.4, -2.0]* |
| left_hand | vel | none | 126 | 28.7 [24.3–33.5] | 29.3 [22.5–37.1] | 6.3 | 17.0 | 2.7 / 8.8 / 49 | -14.2 [-20.8, -8.2]* | -13.6 [-23.1, -4.1]* |
| left_hand | pos+vel | none | 252 | 32.0 [27.4–36.9] | 35.4 [28.1–43.4] | 7.4 | 17.7 | 1.4 / 7.5 / 38 | -10.9 [-17.2, -4.9]* | -7.5 [-17.0, +2.7] |
| right_hand | pos | none | 126 | 39.3 [34.5–44.4] | 32.7 [25.6–40.6] | 10.1 | 17.0 | 2.0 / 10.2 / 44 | -3.6 [-9.6, +2.5] | -10.2 [-19.7, +0.0] |
| right_hand | vel | none | 126 | 30.1 [25.6–34.9] | 26.5 [20.1–34.2] | 6.6 | 15.6 | 0.7 / 7.5 / 41 | -12.8 [-19.4, -6.6]* | -16.3 [-26.5, -6.1]* |
| right_hand | pos+vel | none | 252 | 39.6 [34.7–44.7] | 32.0 [25.0–39.9] | 12.8 | 17.7 | 0.7 / 8.8 / 35 | -3.3 [-9.6, +2.7] | -10.9 [-19.7, -1.4]* |
| hands | pos | none | 252 | 39.9 [35.0–45.0] | 40.1 [32.6–48.2] | 11.5 | 19.0 | 1.4 / 10.9 / 37 | -3.0 [-8.7, +2.7] | -2.7 [-11.6, +6.8] |
| hands | vel | none | 252 | 30.3 [25.8–35.2] | 30.6 [23.7–38.5] | 7.1 | 17.0 | 2.7 / 8.2 / 43 | -12.6 [-18.9, -6.6]* | -12.2 [-22.4, -2.7]* |
| hands | pos+vel | none | 504 | 38.5 [33.7–43.6] | 33.3 [26.2–41.3] | 12.6 | 18.4 | 1.4 / 10.2 / 38 | -4.4 [-10.4, +1.1] | -9.5 [-18.4, -0.7]* |
| upper_body | pos | none | 72 | 38.0 [33.2–43.1] | 36.1 [28.7–44.1] | 9.0 | 17.7 | 0.7 / 8.2 / 40 | -4.9 [-10.9, +1.1] | -6.8 [-15.0, +2.0] |
| upper_body | vel | none | 72 | 32.2 [27.7–37.2] | 38.1 [30.6–46.2] | 7.1 | 17.7 | 1.4 / 9.5 / 44 | -10.7 [-17.5, -3.8]* | -4.8 [-15.0, +5.4] |
| upper_body | pos+vel | none | 144 | 35.8 [31.1–40.8] | 41.5 [33.8–49.6] | 9.3 | 21.8 | 2.7 / 12.9 / 35 | -7.1 [-13.7, -0.8]* | -1.4 [-10.2, +7.5] |
| face | pos | none | 552 | 37.7 [32.9–42.8] | 34.0 [26.8–42.0] | 9.6 | 16.3 | 1.4 / 10.9 / 45 | -5.2 [-10.9, +0.8] | -8.8 [-18.4, +0.7] |
| face | vel | none | 552 | 31.4 [26.9–36.3] | 33.3 [26.2–41.3] | 5.5 | 13.6 | 0.7 / 8.8 / 38 | -11.5 [-18.0, -5.2]* | -9.5 [-20.4, +0.7] |
| face | pos+vel | none | 1104 | 38.5 [33.7–43.6] | 34.7 [27.5–42.7] | 9.6 | 18.4 | 2.7 / 9.5 / 35 | -4.4 [-10.7, +1.4] | -8.2 [-18.4, +1.4] |
| lower_body | pos | none | 60 | 30.6 [26.1–35.5] | 29.9 [23.1–37.8] | 6.3 | 15.0 | 2.0 / 9.5 / 46 | -12.3 [-18.9, -6.3]* | -12.9 [-21.1, -4.1]* |
| lower_body | vel | none | 60 | 27.6 [23.3–32.4] | 18.4 [12.9–25.4] | 5.5 | 11.6 | 2.0 / 5.4 / 41 | -15.3 [-22.1, -9.0]* | -24.5 [-34.0, -14.9]* |
| lower_body | pos+vel | none | 120 | 26.5 [22.2–31.3] | 33.3 [26.2–41.3] | 8.5 | 18.4 | 2.7 / 7.5 / 39 | -16.4 [-23.0, -10.1]* | -9.5 [-19.7, +0.0] |
| pose_head_0-10 | pos | none | 66 | 32.0 [27.4–36.9] | 25.9 [19.5–33.5] | 8.7 | 10.9 | 0.7 / 6.1 / 46 | -10.9 [-16.7, -4.9]* | -17.0 [-26.5, -7.5]* |
| pose_head_0-10 | vel | none | 66 | 28.7 [24.3–33.5] | 36.1 [28.7–44.1] | 6.6 | 16.3 | 0.7 / 6.1 / 41 | -14.2 [-20.5, -7.9]* | -6.8 [-16.3, +3.4] |
| pose_head_0-10 | pos+vel | none | 132 | 31.7 [27.1–36.6] | 31.3 [24.4–39.2] | 9.0 | 12.9 | 2.0 / 6.8 / 36 | -11.2 [-17.5, -5.5]* | -11.6 [-21.1, -2.0]* |
| hands+upper | pos | none | 324 | 42.1 [37.1–47.2] | 46.3 [38.4–54.3] | 16.1 | 21.1 | 2.7 / 11.6 / 30 | -0.8 [-6.0, +4.1] | +3.4 [-3.4, +10.9] |
| hands+upper | vel | none | 324 | 34.7 [30.0–39.7] | 32.0 [25.0–39.9] | 7.7 | 19.0 | 1.4 / 11.6 / 40 | -8.2 [-14.8, -2.2]* | -10.9 [-19.7, -2.0]* |
| hands+upper | pos+vel | none | 648 | 37.7 [32.9–42.8] | 36.1 [28.7–44.1] | 12.3 | 20.4 | 2.0 / 9.5 / 32 | -5.2 [-10.9, +0.3] | -6.8 [-15.0, +2.0] |
| hands+upper+face | pos | none | 876 | 44.5 [39.5–49.7] | 42.2 [34.5–50.3] | 14.8 | 24.5 | 2.0 / 12.2 / 32 | +1.6 [-2.5, +5.7] | -0.7 [-6.1, +4.8] |
| hands+upper+face | vel | none | 876 | 37.4 [32.6–42.5] | 32.0 [25.0–39.9] | 9.0 | 19.0 | 2.7 / 10.2 / 37 | -5.5 [-12.3, +0.8] | -10.9 [-20.4, -1.4]* |
| hands+upper+face | pos+vel | none | 1752 | 47.5 [42.5–52.7] | 40.8 [33.2–48.9] | 14.2 | 24.5 | 3.4 / 15.0 / 28 | +4.6 [-0.3, +9.3] | -2.0 [-8.8, +4.8] |
| all | pos | none | 1002 | 42.9 [37.9–48.0] | 42.9 [35.1–50.9] | 14.8 | 27.9 | 1.4 / 15.0 / 25 | baseline | baseline |
| all | vel | none | 1002 | 37.4 [32.6–42.5] | 33.3 [26.2–41.3] | 9.8 | 17.0 | 0.7 / 10.2 / 35 | -5.5 [-12.3, +1.1] | -9.5 [-19.0, +0.0] |
| all | pos+vel | none | 2004 | 45.9 [40.9–51.0] | 44.2 [36.4–52.3] | 13.9 | 30.6 | 2.0 / 12.9 / 22 | +3.0 [-1.6, +7.7] | +1.4 [-4.1, +7.5] |
| hands | acc | none | 252 | 27.9 [23.5–32.7] | 27.9 [21.3–35.6] | 6.6 | 15.0 | 0.7 / 9.5 / 43 | -15.0 [-21.0, -9.6]* | -15.0 [-25.2, -4.1]* |
| hands | pos+vel+acc | none | 756 | 36.3 [31.6–41.4] | 30.6 [23.7–38.5] | 12.0 | 16.3 | 2.0 / 6.8 / 36 | -6.6 [-12.3, -1.1]* | -12.2 [-22.4, -2.0]* |
| hands | pos+vel | frames shuffled | 504 | 37.2 [32.4–42.2] | 41.5 [33.8–49.6] | 12.6 | 23.1 | 2.7 / 12.2 / 37 | -5.7 [-11.2, -0.3]* | -1.4 [-10.2, +7.5] |
| hands | pos | length-residualised | 252 | 41.8 [36.9–46.9] | 39.5 [31.9–47.5] | 11.2 | 18.4 | 2.0 / 10.9 / 44 | -1.1 [-6.8, +4.4] | -3.4 [-12.9, +5.4] |
| hands | pos+vel | length-residualised | 504 | 40.2 [35.3–45.3] | 40.1 [32.6–48.2] | 9.0 | 17.7 | 1.4 / 8.2 / 43 | -2.7 [-8.5, +2.5] | -2.7 [-11.6, +6.1] |
| upper_body | acc | none | 72 | 33.3 [28.7–38.3] | 33.3 [26.2–41.3] | 6.0 | 17.7 | 1.4 / 9.5 / 40 | -9.6 [-16.1, -3.3]* | -9.5 [-19.7, +1.4] |
| upper_body | pos+vel+acc | none | 216 | 33.9 [29.2–38.9] | 38.8 [31.3–46.8] | 9.6 | 25.2 | 3.4 / 16.3 / 30 | -9.0 [-15.6, -3.0]* | -4.1 [-13.6, +5.4] |
| upper_body | pos+vel | frames shuffled | 144 | 32.5 [27.9–37.5] | 33.3 [26.2–41.3] | 8.5 | 19.0 | 2.0 / 10.2 / 32 | -10.4 [-16.7, -4.4]* | -9.5 [-19.0, -0.7]* |
| upper_body | pos | length-residualised | 72 | 38.5 [33.7–43.6] | 34.7 [27.5–42.7] | 8.2 | 20.4 | 1.4 / 8.8 / 37 | -4.4 [-10.7, +1.9] | -8.2 [-16.3, +0.0] |
| upper_body | pos+vel | length-residualised | 144 | 38.5 [33.7–43.6] | 36.7 [29.4–44.8] | 7.1 | 19.7 | 1.4 / 10.2 / 42 | -4.4 [-10.9, +1.9] | -6.1 [-15.0, +2.7] |
| hands+upper | acc | none | 324 | 28.1 [23.8–33.0] | 30.6 [23.7–38.5] | 7.4 | 17.0 | 1.4 / 8.2 / 38 | -14.8 [-21.0, -9.0]* | -12.2 [-22.4, -2.0]* |
| hands+upper | pos+vel+acc | none | 972 | 36.3 [31.6–41.4] | 38.8 [31.3–46.8] | 12.8 | 19.0 | 1.4 / 11.6 / 30 | -6.6 [-12.3, -0.8]* | -4.1 [-12.9, +5.4] |
| hands+upper | pos+vel | frames shuffled | 648 | 37.2 [32.4–42.2] | 38.1 [30.6–46.2] | 12.0 | 21.1 | 0.0 / 10.9 / 28 | -5.7 [-10.9, -0.5]* | -4.8 [-12.9, +4.1] |
| hands+upper | pos | length-residualised | 324 | 42.6 [37.7–47.7] | 45.6 [37.7–53.6] | 13.7 | 21.8 | 3.4 / 13.6 / 38 | -0.3 [-5.7, +4.9] | +2.7 [-4.1, +9.5] |
| hands+upper | pos+vel | length-residualised | 648 | 45.4 [40.3–50.5] | 41.5 [33.8–49.6] | 12.0 | 21.8 | 1.4 / 12.9 / 41 | +2.5 [-3.0, +7.9] | -1.4 [-9.5, +6.8] |
| hands+upper+face | acc | none | 876 | 31.7 [27.1–36.6] | 33.3 [26.2–41.3] | 8.2 | 19.0 | 3.4 / 10.9 / 39 | -11.2 [-17.8, -5.5]* | -9.5 [-19.0, +0.7] |
| hands+upper+face | pos+vel+acc | none | 2628 | 43.4 [38.5–48.6] | 36.7 [29.4–44.8] | 14.5 | 21.1 | 3.4 / 10.9 / 31 | +0.5 [-4.9, +5.5] | -6.1 [-14.3, +2.0] |
| hands+upper+face | pos+vel | frames shuffled | 1752 | 41.5 [36.6–46.6] | 42.2 [34.5–50.3] | 15.8 | 21.8 | 2.0 / 10.9 / 28 | -1.4 [-6.3, +3.3] | -0.7 [-8.2, +6.8] |
| hands+upper+face | pos | length-residualised | 876 | 45.6 [40.6–50.8] | 43.5 [35.8–51.6] | 13.4 | 23.8 | 4.1 / 17.0 / 36 | +2.7 [-1.9, +7.7] | +0.7 [-4.8, +5.4] |
| hands+upper+face | pos+vel | length-residualised | 1752 | 47.3 [42.2–52.4] | 46.3 [38.4–54.3] | 13.4 | 25.2 | 3.4 / 12.9 / 35 | +4.4 [-0.8, +9.3] | +3.4 [-3.4, +10.2] |
| all | acc | none | 1002 | 31.7 [27.1–36.6] | 29.9 [23.1–37.8] | 6.3 | 18.4 | 0.7 / 10.9 / 35 | -11.2 [-17.5, -5.5]* | -12.9 [-21.8, -3.4]* |
| all | pos+vel+acc | none | 3006 | 42.1 [37.1–47.2] | 38.8 [31.3–46.8] | 13.1 | 25.2 | 4.8 / 17.0 / 29 | -0.8 [-6.6, +4.4] | -4.1 [-11.6, +3.4] |
| all | pos+vel | frames shuffled | 2004 | 39.3 [34.5–44.4] | 40.1 [32.6–48.2] | 14.2 | 26.5 | 0.7 / 14.3 / 28 | -3.6 [-7.9, +1.1] | -2.7 [-10.2, +4.8] |
| all | pos | length-residualised | 1002 | 45.9 [40.9–51.0] | 40.1 [32.6–48.2] | 12.3 | 24.5 | 4.8 / 15.6 / 38 | +3.0 [-1.6, +7.4] | -2.7 [-8.2, +2.7] |
| all | pos+vel | length-residualised | 2004 | 48.9 [43.8–54.0] | 46.9 [39.1–55.0] | 13.1 | 24.5 | 3.4 / 13.6 / 33 | +6.0 [+0.8, +10.9]* | +4.1 [-2.0, +10.9] |
| hands | pos+velu | velocity not divided by stride | 504 | 38.3 [33.4–43.3] | 28.6 [21.9–36.3] | 13.4 | 15.6 | 2.0 / 10.9 / 37 | -4.6 [-10.7, +0.8] | -14.3 [-23.8, -4.8]* |
| all | pos+velu | velocity not divided by stride | 2004 | 44.0 [39.0–49.1] | 44.2 [36.4–52.3] | 14.8 | 27.9 | 2.0 / 13.6 / 21 | +1.1 [-3.6, +5.7] | +1.4 [-4.8, +7.5] |
| - | length only | none | 3 | 24.6 [20.5–29.3] | 32.0 [25.0–39.9] | 6.3 | 18.4 | 2.0 / 8.2 / 34 | -18.3 [-24.6, -12.0]* | -10.9 [-21.1, -0.7]* |

## tfidf: length-matched 4-way (chance 25%) and R@10 (chance val 2.7%, frozen 6.8%)

| Group | Feature | Control | d | Val 4-way [95% CI] | Frozen 4-way [95% CI] | Val R@10 | Frozen R@10 | Frozen R@1 / R@5 / med. rank | Δ vs all/pos, val 4-way | Δ vs all/pos, frozen 4-way |
|---|---|---|---:|---:|---:|---:|---:|---:|---:|---:|
| left_hand | pos | none | 126 | 33.6 [29.0–38.6] | 32.7 [25.6–40.6] | 7.9 | 13.6 | 1.4 / 8.2 / 53 | -9.6 [-15.3, -3.6]* | +0.7 [-8.2, +9.5] |
| left_hand | vel | none | 126 | 30.1 [25.6–34.9] | 27.2 [20.7–34.9] | 7.7 | 14.3 | 1.4 / 6.8 / 53 | -13.1 [-19.7, -6.3]* | -4.8 [-15.6, +4.8] |
| left_hand | pos+vel | none | 252 | 35.5 [30.8–40.5] | 32.7 [25.6–40.6] | 7.4 | 19.0 | 2.7 / 11.6 / 47 | -7.7 [-13.7, -1.9]* | +0.7 [-8.2, +9.5] |
| right_hand | pos | none | 126 | 40.4 [35.5–45.5] | 32.0 [25.0–39.9] | 11.5 | 10.2 | 0.0 / 6.1 / 54 | -2.7 [-9.0, +3.0] | +0.0 [-10.2, +8.8] |
| right_hand | vel | none | 126 | 27.3 [23.0–32.1] | 24.5 [18.2–32.0] | 3.3 | 11.6 | 0.7 / 4.8 / 60 | -15.8 [-22.1, -9.6]* | -7.5 [-17.7, +2.0] |
| right_hand | pos+vel | none | 252 | 36.1 [31.3–41.1] | 32.7 [25.6–40.6] | 8.5 | 17.0 | 2.0 / 6.8 / 37 | -7.1 [-13.4, -1.1]* | +0.7 [-8.8, +10.2] |
| hands | pos | none | 252 | 41.0 [36.1–46.1] | 39.5 [31.9–47.5] | 11.2 | 14.3 | 2.0 / 8.8 / 46 | -2.2 [-7.9, +3.3] | +7.5 [-1.4, +15.7] |
| hands | vel | none | 252 | 28.4 [24.0–33.2] | 27.2 [20.7–34.9] | 4.9 | 11.6 | 2.0 / 6.8 / 50 | -14.8 [-21.3, -8.2]* | -4.8 [-15.0, +4.8] |
| hands | pos+vel | none | 504 | 41.3 [36.3–46.4] | 36.7 [29.4–44.8] | 9.6 | 21.1 | 1.4 / 12.9 / 32 | -1.9 [-7.1, +3.6] | +4.8 [-4.8, +14.3] |
| upper_body | pos | none | 72 | 30.6 [26.1–35.5] | 32.7 [25.6–40.6] | 7.7 | 13.6 | 2.0 / 7.5 / 52 | -12.6 [-18.0, -7.1]* | +0.7 [-7.5, +9.5] |
| upper_body | vel | none | 72 | 29.5 [25.1–34.4] | 20.4 [14.7–27.6] | 5.5 | 11.6 | 0.7 / 5.4 / 55 | -13.7 [-19.9, -7.4]* | -11.6 [-21.8, -2.0]* |
| upper_body | pos+vel | none | 144 | 30.1 [25.6–34.9] | 29.3 [22.5–37.1] | 7.4 | 10.9 | 2.0 / 5.4 / 46 | -13.1 [-19.4, -7.1]* | -2.7 [-12.2, +6.8] |
| face | pos | none | 552 | 33.1 [28.4–38.0] | 30.6 [23.7–38.5] | 5.2 | 15.6 | 3.4 / 8.2 / 59 | -10.1 [-15.6, -4.6]* | -1.4 [-10.9, +7.5] |
| face | vel | none | 552 | 29.5 [25.1–34.4] | 28.6 [21.9–36.3] | 5.7 | 12.2 | 0.7 / 6.8 / 51 | -13.7 [-20.2, -7.1]* | -3.4 [-12.2, +6.8] |
| face | pos+vel | none | 1104 | 32.5 [27.9–37.5] | 29.3 [22.5–37.1] | 5.2 | 17.0 | 3.4 / 9.5 / 45 | -10.7 [-16.9, -4.6]* | -2.7 [-11.6, +6.1] |
| lower_body | pos | none | 60 | 23.2 [19.2–27.8] | 24.5 [18.2–32.0] | 4.6 | 9.5 | 1.4 / 5.4 / 71 | -19.9 [-25.4, -14.2]* | -7.5 [-16.3, +1.4] |
| lower_body | vel | none | 60 | 26.2 [22.0–31.0] | 25.2 [18.8–32.8] | 3.3 | 10.2 | 0.7 / 5.4 / 50 | -16.9 [-23.2, -10.7]* | -6.8 [-16.3, +2.7] |
| lower_body | pos+vel | none | 120 | 23.5 [19.4–28.1] | 28.6 [21.9–36.3] | 3.6 | 12.2 | 2.0 / 7.5 / 54 | -19.7 [-25.7, -13.7]* | -3.4 [-12.2, +5.4] |
| pose_head_0-10 | pos | none | 66 | 27.0 [22.8–31.8] | 27.9 [21.3–35.6] | 5.5 | 8.8 | 0.7 / 4.8 / 58 | -16.1 [-21.9, -9.8]* | -4.1 [-12.9, +4.8] |
| pose_head_0-10 | vel | none | 66 | 25.7 [21.5–30.4] | 29.3 [22.5–37.1] | 6.0 | 4.8 | 1.4 / 3.4 / 49 | -17.5 [-23.8, -11.2]* | -2.7 [-11.6, +6.8] |
| pose_head_0-10 | pos+vel | none | 132 | 27.9 [23.5–32.7] | 25.9 [19.5–33.5] | 8.2 | 11.6 | 0.7 / 4.8 / 47 | -15.3 [-21.0, -9.3]* | -6.1 [-15.6, +3.4] |
| hands+upper | pos | none | 324 | 43.7 [38.7–48.8] | 35.4 [28.1–43.4] | 12.8 | 13.6 | 0.7 / 7.5 / 43 | +0.5 [-4.9, +5.7] | +3.4 [-3.4, +10.2] |
| hands+upper | vel | none | 324 | 31.1 [26.6–36.1] | 27.2 [20.7–34.9] | 4.1 | 10.9 | 1.4 / 6.1 / 42 | -12.0 [-18.6, -5.7]* | -4.8 [-15.0, +5.4] |
| hands+upper | pos+vel | none | 648 | 40.4 [35.5–45.5] | 39.5 [31.9–47.5] | 10.9 | 19.0 | 2.7 / 9.5 / 31 | -2.7 [-8.2, +2.7] | +7.5 [-1.4, +15.6] |
| hands+upper+face | pos | none | 876 | 44.8 [39.8–49.9] | 37.4 [30.0–45.5] | 13.4 | 14.3 | 3.4 / 7.5 / 45 | +1.6 [-2.2, +5.5] | +5.4 [-0.0, +10.9] |
| hands+upper+face | vel | none | 876 | 30.1 [25.6–34.9] | 29.9 [23.1–37.8] | 6.3 | 11.6 | 1.4 / 4.8 / 48 | -13.1 [-19.4, -6.8]* | -2.0 [-11.6, +7.5] |
| hands+upper+face | pos+vel | none | 1752 | 41.8 [36.9–46.9] | 40.1 [32.6–48.2] | 10.7 | 21.8 | 1.4 / 11.6 / 40 | -1.4 [-6.3, +3.6] | +8.2 [+0.0, +16.3] |
| all | pos | none | 1002 | 43.2 [38.2–48.3] | 32.0 [25.0–39.9] | 12.3 | 12.2 | 2.7 / 7.5 / 43 | baseline | baseline |
| all | vel | none | 1002 | 31.1 [26.6–36.1] | 34.7 [27.5–42.7] | 4.9 | 15.6 | 0.7 / 5.4 / 47 | -12.0 [-18.6, -5.5]* | +2.7 [-7.5, +12.9] |
| all | pos+vel | none | 2004 | 40.2 [35.3–45.3] | 35.4 [28.1–43.4] | 10.7 | 20.4 | 2.0 / 12.9 / 36 | -3.0 [-7.7, +1.6] | +3.4 [-3.4, +11.6] |
| hands | acc | none | 252 | 28.1 [23.8–33.0] | 28.6 [21.9–36.3] | 4.6 | 12.2 | 2.0 / 7.5 / 56 | -15.0 [-21.0, -8.5]* | -3.4 [-13.6, +6.1] |
| hands | pos+vel+acc | none | 756 | 39.9 [35.0–45.0] | 42.2 [34.5–50.3] | 9.6 | 23.1 | 2.7 / 13.6 / 39 | -3.3 [-8.5, +1.9] | +10.2 [+0.7, +19.0]* |
| hands | pos+vel | frames shuffled | 504 | 38.5 [33.7–43.6] | 32.7 [25.6–40.6] | 11.2 | 19.7 | 2.0 / 10.2 / 39 | -4.6 [-10.4, +0.5] | +0.7 [-8.2, +9.5] |
| hands | pos | length-residualised | 252 | 41.0 [36.1–46.1] | 37.4 [30.0–45.5] | 9.8 | 11.6 | 2.0 / 6.8 / 55 | -2.2 [-7.7, +3.6] | +5.4 [-2.7, +12.9] |
| hands | pos+vel | length-residualised | 504 | 39.6 [34.7–44.7] | 37.4 [30.0–45.5] | 8.7 | 16.3 | 2.7 / 8.2 / 42 | -3.6 [-9.3, +1.6] | +5.4 [-4.1, +15.0] |
| upper_body | acc | none | 72 | 31.7 [27.1–36.6] | 29.9 [23.1–37.8] | 3.3 | 17.7 | 1.4 / 10.9 / 43 | -11.5 [-18.0, -5.2]* | -2.0 [-11.6, +6.8] |
| upper_body | pos+vel+acc | none | 216 | 29.8 [25.3–34.7] | 27.9 [21.3–35.6] | 8.5 | 15.6 | 2.7 / 10.2 / 40 | -13.4 [-19.7, -7.4]* | -4.1 [-14.3, +5.4] |
| upper_body | pos+vel | frames shuffled | 144 | 28.7 [24.3–33.5] | 28.6 [21.9–36.3] | 5.2 | 12.2 | 3.4 / 9.5 / 43 | -14.5 [-21.0, -8.5]* | -3.4 [-12.9, +5.4] |
| upper_body | pos | length-residualised | 72 | 30.6 [26.1–35.5] | 32.0 [25.0–39.9] | 6.8 | 11.6 | 0.7 / 6.8 / 59 | -12.6 [-18.3, -6.8]* | +0.0 [-8.2, +8.2] |
| upper_body | pos+vel | length-residualised | 144 | 33.1 [28.4–38.0] | 30.6 [23.7–38.5] | 6.3 | 10.9 | 1.4 / 4.8 / 56 | -10.1 [-16.4, -4.1]* | -1.4 [-10.2, +8.2] |
| hands+upper | acc | none | 324 | 30.9 [26.4–35.8] | 28.6 [21.9–36.3] | 6.6 | 15.0 | 2.7 / 7.5 / 44 | -12.3 [-18.9, -6.0]* | -3.4 [-12.9, +6.8] |
| hands+upper | pos+vel+acc | none | 972 | 39.6 [34.7–44.7] | 40.1 [32.6–48.2] | 10.9 | 22.4 | 3.4 / 10.9 / 31 | -3.6 [-8.7, +1.9] | +8.2 [-0.7, +17.0] |
| hands+upper | pos+vel | frames shuffled | 648 | 41.5 [36.6–46.6] | 36.1 [28.7–44.1] | 11.5 | 20.4 | 1.4 / 9.5 / 39 | -1.6 [-7.1, +3.8] | +4.1 [-4.1, +12.2] |
| hands+upper | pos | length-residualised | 324 | 43.7 [38.7–48.8] | 40.8 [33.2–48.9] | 12.0 | 13.6 | 2.7 / 6.1 / 48 | +0.5 [-4.6, +5.5] | +8.8 [+0.7, +16.3]* |
| hands+upper | pos+vel | length-residualised | 648 | 41.5 [36.6–46.6] | 42.2 [34.5–50.3] | 9.8 | 16.3 | 0.7 / 6.8 / 39 | -1.6 [-7.4, +3.3] | +10.2 [+0.7, +19.7]* |
| hands+upper+face | acc | none | 876 | 29.5 [25.1–34.4] | 23.8 [17.6–31.3] | 4.6 | 9.5 | 1.4 / 8.2 / 52 | -13.7 [-20.2, -7.4]* | -8.2 [-18.4, +2.0] |
| hands+upper+face | pos+vel+acc | none | 2628 | 38.8 [33.9–43.9] | 32.7 [25.6–40.6] | 10.1 | 20.4 | 1.4 / 12.9 / 41 | -4.4 [-9.3, +0.6] | +0.7 [-6.8, +8.2] |
| hands+upper+face | pos+vel | frames shuffled | 1752 | 39.9 [35.0–45.0] | 40.8 [33.2–48.9] | 10.7 | 22.4 | 1.4 / 10.2 / 36 | -3.3 [-8.2, +1.9] | +8.8 [+1.4, +16.3]* |
| hands+upper+face | pos | length-residualised | 876 | 45.6 [40.6–50.8] | 41.5 [33.8–49.6] | 11.5 | 19.0 | 2.0 / 7.5 / 54 | +2.5 [-1.6, +6.8] | +9.5 [+2.7, +16.3]* |
| hands+upper+face | pos+vel | length-residualised | 1752 | 44.0 [39.0–49.1] | 41.5 [33.8–49.6] | 12.0 | 19.0 | 1.4 / 10.2 / 47 | +0.8 [-4.4, +6.0] | +9.5 [+2.0, +17.0]* |
| all | acc | none | 1002 | 29.5 [25.1–34.4] | 31.3 [24.4–39.2] | 5.2 | 10.9 | 2.0 / 6.8 / 44 | -13.7 [-20.2, -7.1]* | -0.7 [-10.2, +9.5] |
| all | pos+vel+acc | none | 3006 | 40.7 [35.8–45.8] | 33.3 [26.2–41.3] | 11.2 | 20.4 | 3.4 / 12.2 / 38 | -2.5 [-7.1, +2.2] | +1.4 [-6.1, +8.2] |
| all | pos+vel | frames shuffled | 2004 | 37.7 [32.9–42.8] | 39.5 [31.9–47.5] | 9.8 | 20.4 | 2.7 / 10.2 / 35 | -5.5 [-10.1, -0.8]* | +7.5 [+0.0, +15.0] |
| all | pos | length-residualised | 1002 | 41.8 [36.9–46.9] | 33.3 [26.2–41.3] | 10.9 | 11.6 | 2.0 / 8.8 / 52 | -1.4 [-3.8, +1.1] | +1.4 [-2.7, +5.4] |
| all | pos+vel | length-residualised | 2004 | 40.2 [35.3–45.3] | 36.7 [29.4–44.8] | 9.8 | 19.0 | 1.4 / 10.9 / 48 | -3.0 [-8.2, +1.9] | +4.8 [-2.0, +12.2] |
| hands | pos+velu | velocity not divided by stride | 504 | 37.7 [32.9–42.8] | 36.7 [29.4–44.8] | 9.8 | 20.4 | 0.7 / 8.8 / 38 | -5.5 [-10.9, +0.0] | +4.8 [-4.8, +13.6] |
| all | pos+velu | velocity not divided by stride | 2004 | 39.3 [34.5–44.4] | 34.7 [27.5–42.7] | 11.7 | 21.1 | 2.0 / 12.2 / 37 | -3.8 [-9.0, +1.4] | +2.7 [-4.8, +10.2] |
| - | length only | none | 3 | 24.9 [20.7–29.5] | 24.5 [18.2–32.0] | 6.3 | 13.6 | 1.4 / 5.4 / 50 | -18.3 [-24.6, -11.7]* | -7.5 [-16.3, +2.0] |

## Paired comparisons (A − B, pp; 95% paired bootstrap; * = CI excludes 0)

| Emb. | Comparison | A | B | Val 4-way | Frozen 4-way | Val R@10 | Frozen R@10 |
|---|---|---|---|---:|---:|---:|---:|
| t5enc | pos+vel vs pos | left_hand/pos+vel/none | left_hand/pos/none | +0.3 [-4.4, +4.6] | +2.7 [-5.4, +10.9] | -0.8 [-3.3, +1.4] | +5.4 [+1.4, +10.2]* |
| t5enc | vel vs pos | left_hand/vel/none | left_hand/pos/none | -3.0 [-9.8, +3.3] | -3.4 [-13.6, +6.8] | -1.9 [-5.5, +1.4] | +4.8 [-1.4, +11.6] |
| t5enc | pos+vel vs pos | right_hand/pos+vel/none | right_hand/pos/none | +0.3 [-4.9, +5.5] | -0.7 [-8.2, +6.8] | +2.7 [-0.3, +5.7] | +0.7 [-4.1, +5.4] |
| t5enc | vel vs pos | right_hand/vel/none | right_hand/pos/none | -9.3 [-15.8, -3.0]* | -6.1 [-16.3, +4.1] | -3.6 [-6.8, +0.0] | -1.4 [-8.2, +5.4] |
| t5enc | pos+vel vs pos | hands/pos+vel/none | hands/pos/none | -1.4 [-6.3, +3.6] | -6.8 [-15.0, +2.0] | +1.1 [-1.6, +3.8] | -0.7 [-6.8, +6.1] |
| t5enc | vel vs pos | hands/vel/none | hands/pos/none | -9.6 [-15.6, -3.3]* | -9.5 [-19.7, +0.7] | -4.4 [-7.9, -0.5]* | -2.0 [-8.8, +4.8] |
| t5enc | pos+vel vs pos | upper_body/pos+vel/none | upper_body/pos/none | -2.2 [-7.1, +2.5] | +5.4 [-1.4, +12.2] | +0.3 [-2.5, +3.0] | +4.1 [-2.0, +10.9] |
| t5enc | vel vs pos | upper_body/vel/none | upper_body/pos/none | -5.7 [-11.7, +0.3] | +2.0 [-6.1, +10.9] | -1.9 [-4.9, +0.8] | +0.0 [-6.8, +6.8] |
| t5enc | pos+vel vs pos | face/pos+vel/none | face/pos/none | +0.8 [-4.1, +5.5] | +0.7 [-6.1, +7.5] | +0.0 [-3.3, +3.3] | +2.0 [-2.7, +6.1] |
| t5enc | vel vs pos | face/vel/none | face/pos/none | -6.3 [-12.6, -0.3]* | -0.7 [-9.5, +8.8] | -4.1 [-7.4, -1.1]* | -2.7 [-8.8, +3.4] |
| t5enc | pos+vel vs pos | lower_body/pos+vel/none | lower_body/pos/none | -4.1 [-8.7, +0.8] | +3.4 [-3.4, +10.2] | +2.2 [-0.5, +4.9] | +3.4 [-1.4, +8.8] |
| t5enc | vel vs pos | lower_body/vel/none | lower_body/pos/none | -3.0 [-9.0, +3.0] | -11.6 [-21.1, -2.0]* | -0.8 [-3.6, +1.9] | -3.4 [-8.8, +2.7] |
| t5enc | pos+vel vs pos | pose_head_0-10/pos+vel/none | pose_head_0-10/pos/none | -0.3 [-5.2, +4.6] | +5.4 [-1.4, +12.9] | +0.3 [-2.5, +2.7] | +2.0 [-3.4, +7.5] |
| t5enc | vel vs pos | pose_head_0-10/vel/none | pose_head_0-10/pos/none | -3.3 [-9.0, +2.2] | +10.2 [+2.0, +18.4]* | -2.2 [-5.2, +0.8] | +5.4 [-1.4, +12.2] |
| t5enc | pos+vel vs pos | hands+upper/pos+vel/none | hands+upper/pos/none | -4.4 [-9.6, +0.5] | -10.2 [-17.7, -2.0]* | -3.8 [-7.4, -0.3]* | -0.7 [-7.5, +6.1] |
| t5enc | vel vs pos | hands+upper/vel/none | hands+upper/pos/none | -7.4 [-13.7, -1.4]* | -14.3 [-23.1, -5.4]* | -8.5 [-12.6, -4.6]* | -2.0 [-9.5, +5.4] |
| t5enc | pos+vel vs pos | hands+upper+face/pos+vel/none | hands+upper+face/pos/none | +3.0 [-1.9, +7.7] | -1.4 [-7.5, +4.8] | -0.5 [-3.8, +2.7] | +0.0 [-6.1, +6.1] |
| t5enc | vel vs pos | hands+upper+face/vel/none | hands+upper+face/pos/none | -7.1 [-13.4, -0.8]* | -10.2 [-19.7, +0.0] | -5.7 [-9.6, -2.2]* | -5.4 [-13.6, +2.0] |
| t5enc | pos+vel vs pos | all/pos+vel/none | all/pos/none | +3.0 [-1.6, +7.7] | +1.4 [-4.1, +7.5] | -0.8 [-4.1, +2.2] | +2.7 [-4.1, +10.2] |
| t5enc | vel vs pos | all/vel/none | all/pos/none | -5.5 [-12.3, +1.1] | -9.5 [-19.0, +0.0] | -4.9 [-8.7, -1.4]* | -10.9 [-19.7, -2.7]* |
| t5enc | shuffled vs ordered pos+vel | hands/pos+vel/frames shuffled | hands/pos+vel/none | -1.4 [-6.6, +3.8] | +8.2 [+0.7, +15.6]* | +0.0 [-3.6, +3.3] | +4.8 [-1.4, +11.6] |
| t5enc | pos+vel+acc vs pos+vel | hands/pos+vel+acc/none | hands/pos+vel/none | -2.2 [-6.0, +1.6] | -2.7 [-10.2, +4.8] | -0.5 [-3.3, +1.9] | -2.0 [-6.8, +2.7] |
| t5enc | length-residualised vs raw | hands/pos/length-residualised | hands/pos/none | +1.9 [-1.4, +5.5] | -0.7 [-5.4, +4.1] | -0.3 [-3.3, +2.7] | -0.7 [-7.5, +5.4] |
| t5enc | length-residualised vs raw | hands/pos+vel/length-residualised | hands/pos+vel/none | +1.6 [-3.8, +7.1] | +6.8 [-2.0, +15.0] | -3.6 [-7.1, +0.3] | -0.7 [-8.2, +6.1] |
| t5enc | shuffled vs ordered pos+vel | upper_body/pos+vel/frames shuffled | upper_body/pos+vel/none | -3.3 [-7.7, +1.4] | -8.2 [-15.6, -0.7]* | -0.8 [-3.3, +1.6] | -2.7 [-8.8, +2.7] |
| t5enc | pos+vel+acc vs pos+vel | upper_body/pos+vel+acc/none | upper_body/pos+vel/none | -1.9 [-4.7, +0.8] | -2.7 [-8.8, +3.4] | +0.3 [-1.6, +2.2] | +3.4 [-0.7, +8.2] |
| t5enc | length-residualised vs raw | upper_body/pos/length-residualised | upper_body/pos/none | +0.5 [-4.1, +5.2] | -1.4 [-7.5, +4.8] | -0.8 [-4.1, +2.5] | +2.7 [-3.4, +8.9] |
| t5enc | length-residualised vs raw | upper_body/pos+vel/length-residualised | upper_body/pos+vel/none | +2.7 [-3.6, +8.2] | -4.8 [-12.2, +3.4] | -2.2 [-5.5, +1.4] | -2.0 [-10.2, +5.4] |
| t5enc | shuffled vs ordered pos+vel | hands+upper/pos+vel/frames shuffled | hands+upper/pos+vel/none | -0.5 [-5.5, +4.6] | +2.0 [-6.8, +10.9] | -0.3 [-3.8, +3.3] | +0.7 [-5.4, +6.8] |
| t5enc | pos+vel+acc vs pos+vel | hands+upper/pos+vel+acc/none | hands+upper/pos+vel/none | -1.4 [-5.7, +3.0] | +2.7 [-4.8, +10.9] | +0.5 [-2.2, +3.3] | -1.4 [-6.8, +4.1] |
| t5enc | length-residualised vs raw | hands+upper/pos/length-residualised | hands+upper/pos/none | +0.5 [-2.7, +3.8] | -0.7 [-5.4, +4.1] | -2.5 [-5.5, +0.5] | +0.7 [-5.4, +6.1] |
| t5enc | length-residualised vs raw | hands+upper/pos+vel/length-residualised | hands+upper/pos+vel/none | +7.7 [+2.2, +13.4]* | +5.4 [-3.4, +14.3] | -0.3 [-4.1, +3.6] | +1.4 [-6.1, +8.2] |
| t5enc | shuffled vs ordered pos+vel | hands+upper+face/pos+vel/frames shuffled | hands+upper+face/pos+vel/none | -6.0 [-11.2, -0.5]* | +1.4 [-6.8, +9.5] | +1.6 [-2.2, +5.7] | -2.7 [-8.8, +3.4] |
| t5enc | pos+vel+acc vs pos+vel | hands+upper+face/pos+vel+acc/none | hands+upper+face/pos+vel/none | -4.1 [-8.2, +0.0] | -4.1 [-11.6, +2.7] | +0.3 [-2.7, +3.3] | -3.4 [-7.5, +0.7] |
| t5enc | length-residualised vs raw | hands+upper+face/pos/length-residualised | hands+upper+face/pos/none | +1.1 [-3.8, +5.7] | +1.4 [-4.1, +6.8] | -1.4 [-4.7, +2.2] | -0.7 [-7.5, +6.1] |
| t5enc | length-residualised vs raw | hands+upper+face/pos+vel/length-residualised | hands+upper+face/pos+vel/none | -0.3 [-5.5, +4.9] | +5.4 [-2.0, +13.6] | -0.8 [-4.4, +2.7] | +0.7 [-6.1, +7.5] |
| t5enc | shuffled vs ordered pos+vel | all/pos+vel/frames shuffled | all/pos+vel/none | -6.6 [-11.7, -1.1]* | -4.1 [-12.2, +4.1] | +0.3 [-3.0, +3.8] | -4.1 [-11.6, +3.4] |
| t5enc | pos+vel+acc vs pos+vel | all/pos+vel+acc/none | all/pos+vel/none | -3.8 [-8.5, +1.1] | -5.4 [-11.6, +0.7] | -0.8 [-3.8, +1.9] | -5.4 [-10.2, -0.7]* |
| t5enc | length-residualised vs raw | all/pos/length-residualised | all/pos/none | +3.0 [-1.6, +7.4] | -2.7 [-8.2, +2.7] | -2.5 [-6.0, +0.5] | -3.4 [-10.9, +3.4] |
| t5enc | length-residualised vs raw | all/pos+vel/length-residualised | all/pos+vel/none | +3.0 [-1.4, +7.1] | +2.7 [-3.4, +8.8] | -0.8 [-4.1, +2.7] | -6.1 [-14.3, +2.0] |
| t5enc | add upper body to hands | hands+upper/pos/none | hands/pos/none | +2.2 [-1.6, +6.3] | +6.1 [-1.4, +13.6] | +4.6 [+1.9, +7.7]* | +2.0 [-2.7, +7.5] |
| t5enc | add hands to upper body | hands+upper/pos/none | upper_body/pos/none | +4.1 [-0.5, +9.0] | +10.2 [+1.4, +18.4]* | +7.1 [+3.8, +10.7]* | +3.4 [-4.1, +10.2] |
| t5enc | add face to hands+upper | hands+upper+face/pos/none | hands+upper/pos/none | +2.5 [-2.5, +7.7] | -4.1 [-11.6, +3.4] | -1.4 [-4.9, +1.9] | +3.4 [-2.7, +9.5] |
| t5enc | add lower body + pose head (= all) | all/pos/none | hands+upper+face/pos/none | -1.6 [-5.7, +2.5] | +0.7 [-4.8, +6.1] | +0.0 [-2.7, +2.7] | +3.4 [-2.0, +8.8] |
| t5enc | add upper body to hands | hands+upper/pos+vel/none | hands/pos+vel/none | -0.8 [-4.6, +3.3] | +2.7 [-3.4, +8.8] | -0.3 [-3.0, +2.7] | +2.0 [-3.4, +7.5] |
| t5enc | add hands to upper body | hands+upper/pos+vel/none | upper_body/pos+vel/none | +1.9 [-4.1, +7.9] | -5.4 [-15.0, +4.1] | +3.0 [-0.5, +6.6] | -1.4 [-8.2, +5.4] |
| t5enc | add face to hands+upper | hands+upper+face/pos+vel/none | hands+upper/pos+vel/none | +9.8 [+5.2, +14.5]* | +4.8 [-2.0, +12.2] | +1.9 [-0.8, +4.6] | +4.1 [-2.0, +10.2] |
| t5enc | add lower body + pose head (= all) | all/pos+vel/none | hands+upper+face/pos+vel/none | -1.6 [-6.3, +3.0] | +3.4 [-3.4, +10.2] | -0.3 [-3.3, +2.7] | +6.1 [+0.7, +11.6]* |
| tfidf | pos+vel vs pos | left_hand/pos+vel/none | left_hand/pos/none | +1.9 [-3.0, +7.1] | +0.0 [-8.2, +7.5] | -0.5 [-3.8, +2.5] | +5.4 [+0.0, +11.6] |
| tfidf | vel vs pos | left_hand/vel/none | left_hand/pos/none | -3.6 [-9.6, +2.5] | -5.4 [-15.6, +4.1] | -0.3 [-4.1, +3.6] | +0.7 [-6.8, +8.2] |
| tfidf | pos+vel vs pos | right_hand/pos+vel/none | right_hand/pos/none | -4.4 [-9.0, +0.0] | +0.7 [-6.8, +7.5] | -3.0 [-6.3, +0.3] | +6.8 [+0.7, +12.9]* |
| tfidf | vel vs pos | right_hand/vel/none | right_hand/pos/none | -13.1 [-19.1, -7.1]* | -7.5 [-17.0, +2.7] | -8.2 [-11.7, -4.6]* | +1.4 [-6.1, +8.8] |
| tfidf | pos+vel vs pos | hands/pos+vel/none | hands/pos/none | +0.3 [-4.4, +4.9] | -2.7 [-10.2, +4.8] | -1.6 [-4.9, +1.4] | +6.8 [+0.7, +13.6]* |
| tfidf | vel vs pos | hands/vel/none | hands/pos/none | -12.6 [-18.9, -6.0]* | -12.2 [-22.4, -2.0]* | -6.3 [-9.8, -2.7]* | -2.7 [-9.5, +4.8] |
| tfidf | pos+vel vs pos | upper_body/pos+vel/none | upper_body/pos/none | -0.5 [-4.9, +4.1] | -3.4 [-10.2, +4.1] | -0.3 [-3.0, +2.5] | -2.7 [-8.2, +2.7] |
| tfidf | vel vs pos | upper_body/vel/none | upper_body/pos/none | -1.1 [-6.8, +4.7] | -12.2 [-21.8, -3.4]* | -2.2 [-5.7, +1.1] | -2.0 [-9.5, +5.4] |
| tfidf | pos+vel vs pos | face/pos+vel/none | face/pos/none | -0.5 [-4.7, +3.6] | -1.4 [-8.2, +4.8] | +0.0 [-2.5, +2.5] | +1.4 [-4.8, +7.5] |
| tfidf | vel vs pos | face/vel/none | face/pos/none | -3.6 [-9.6, +2.5] | -2.0 [-10.2, +6.1] | +0.5 [-2.2, +3.6] | -3.4 [-10.9, +4.1] |
| tfidf | pos+vel vs pos | lower_body/pos+vel/none | lower_body/pos/none | +0.3 [-3.8, +4.6] | +4.1 [-3.4, +11.6] | -1.1 [-3.6, +1.1] | +2.7 [-2.0, +7.5] |
| tfidf | vel vs pos | lower_body/vel/none | lower_body/pos/none | +3.0 [-2.7, +8.7] | +0.7 [-8.2, +9.5] | -1.4 [-4.1, +1.4] | +0.7 [-5.4, +6.1] |
| tfidf | pos+vel vs pos | pose_head_0-10/pos+vel/none | pose_head_0-10/pos/none | +0.8 [-3.6, +4.9] | -2.0 [-8.9, +4.8] | +2.7 [+0.3, +5.2]* | +2.7 [-2.7, +8.2] |
| tfidf | vel vs pos | pose_head_0-10/vel/none | pose_head_0-10/pos/none | -1.4 [-7.1, +4.4] | +1.4 [-6.8, +9.5] | +0.5 [-2.5, +3.6] | -4.1 [-9.5, +1.4] |
| tfidf | pos+vel vs pos | hands+upper/pos+vel/none | hands+upper/pos/none | -3.3 [-8.5, +1.9] | +4.1 [-4.1, +12.2] | -1.9 [-5.5, +1.6] | +5.4 [-0.7, +11.6] |
| tfidf | vel vs pos | hands+upper/vel/none | hands+upper/pos/none | -12.6 [-18.6, -6.0]* | -8.2 [-17.7, +1.4] | -8.7 [-12.3, -5.2]* | -2.7 [-10.2, +4.1] |
| tfidf | pos+vel vs pos | hands+upper+face/pos+vel/none | hands+upper+face/pos/none | -3.0 [-7.9, +1.6] | +2.7 [-4.8, +9.5] | -2.7 [-5.5, +0.3] | +7.5 [+1.4, +14.3]* |
| tfidf | vel vs pos | hands+upper+face/vel/none | hands+upper+face/pos/none | -14.8 [-21.3, -8.5]* | -7.5 [-16.3, +1.4] | -7.1 [-10.9, -3.3]* | -2.7 [-10.2, +4.1] |
| tfidf | pos+vel vs pos | all/pos+vel/none | all/pos/none | -3.0 [-7.7, +1.6] | +3.4 [-3.4, +11.6] | -1.6 [-4.9, +1.6] | +8.2 [+2.7, +14.3]* |
| tfidf | vel vs pos | all/vel/none | all/pos/none | -12.0 [-18.6, -5.5]* | +2.7 [-7.5, +12.9] | -7.4 [-11.2, -3.8]* | +3.4 [-4.1, +10.9] |
| tfidf | shuffled vs ordered pos+vel | hands/pos+vel/frames shuffled | hands/pos+vel/none | -2.7 [-7.4, +1.9] | -4.1 [-11.6, +3.4] | +1.6 [-1.6, +4.9] | -1.4 [-8.2, +5.4] |
| tfidf | pos+vel+acc vs pos+vel | hands/pos+vel+acc/none | hands/pos+vel/none | -1.4 [-5.2, +2.2] | +5.4 [-1.4, +11.6] | +0.0 [-2.2, +2.5] | +2.0 [-1.4, +5.4] |
| tfidf | length-residualised vs raw | hands/pos/length-residualised | hands/pos/none | +0.0 [-3.3, +3.0] | -2.0 [-5.4, +1.4] | -1.4 [-3.6, +0.8] | -2.7 [-6.1, +0.7] |
| tfidf | length-residualised vs raw | hands/pos+vel/length-residualised | hands/pos+vel/none | -1.6 [-5.5, +1.9] | +0.7 [-5.4, +6.8] | -0.8 [-3.0, +1.4] | -4.8 [-10.9, +1.4] |
| tfidf | shuffled vs ordered pos+vel | upper_body/pos+vel/frames shuffled | upper_body/pos+vel/none | -1.4 [-6.3, +3.3] | -0.7 [-7.5, +6.1] | -2.2 [-4.6, +0.5] | +1.4 [-4.1, +6.8] |
| tfidf | pos+vel+acc vs pos+vel | upper_body/pos+vel+acc/none | upper_body/pos+vel/none | -0.3 [-4.6, +4.1] | -1.4 [-7.5, +4.8] | +1.1 [-0.8, +3.0] | +4.8 [-0.7, +10.2] |
| tfidf | length-residualised vs raw | upper_body/pos/length-residualised | upper_body/pos/none | +0.0 [-3.8, +3.8] | -0.7 [-6.8, +5.4] | -0.8 [-3.3, +1.4] | -2.0 [-6.1, +2.0] |
| tfidf | length-residualised vs raw | upper_body/pos+vel/length-residualised | upper_body/pos+vel/none | +3.0 [-0.8, +6.6] | +1.4 [-4.8, +8.8] | -1.1 [-3.3, +1.1] | +0.0 [-4.8, +4.8] |
| tfidf | shuffled vs ordered pos+vel | hands+upper/pos+vel/frames shuffled | hands+upper/pos+vel/none | +1.1 [-3.3, +5.5] | -3.4 [-10.2, +3.4] | +0.5 [-2.7, +4.1] | +1.4 [-4.8, +7.5] |
| tfidf | pos+vel+acc vs pos+vel | hands+upper/pos+vel+acc/none | hands+upper/pos+vel/none | -0.8 [-4.1, +2.5] | +0.7 [-4.8, +6.1] | +0.0 [-2.5, +2.5] | +3.4 [-2.0, +8.8] |
| tfidf | length-residualised vs raw | hands+upper/pos/length-residualised | hands+upper/pos/none | +0.0 [-3.6, +3.6] | +5.4 [+0.0, +10.9] | -0.8 [-3.3, +1.4] | +0.0 [-3.4, +4.1] |
| tfidf | length-residualised vs raw | hands+upper/pos+vel/length-residualised | hands+upper/pos+vel/none | +1.1 [-3.0, +5.2] | +2.7 [-2.0, +8.2] | -1.1 [-3.8, +1.6] | -2.7 [-8.2, +3.4] |
| tfidf | shuffled vs ordered pos+vel | hands+upper+face/pos+vel/frames shuffled | hands+upper+face/pos+vel/none | -1.9 [-6.6, +3.0] | +0.7 [-6.8, +8.2] | +0.0 [-3.3, +3.3] | +0.7 [-6.1, +7.5] |
| tfidf | pos+vel+acc vs pos+vel | hands+upper+face/pos+vel+acc/none | hands+upper+face/pos+vel/none | -3.0 [-6.8, +0.8] | -7.5 [-13.6, -1.4]* | -0.5 [-2.7, +1.6] | -1.4 [-6.1, +3.4] |
| tfidf | length-residualised vs raw | hands+upper+face/pos/length-residualised | hands+upper+face/pos/none | +0.8 [-3.0, +4.9] | +4.1 [-2.0, +10.2] | -1.9 [-4.6, +0.8] | +4.8 [+0.0, +10.2] |
| tfidf | length-residualised vs raw | hands+upper+face/pos+vel/length-residualised | hands+upper+face/pos+vel/none | +2.2 [-1.9, +6.3] | +1.4 [-4.8, +8.2] | +1.4 [-1.4, +4.1] | -2.7 [-7.5, +2.7] |
| tfidf | shuffled vs ordered pos+vel | all/pos+vel/frames shuffled | all/pos+vel/none | -2.5 [-6.6, +1.9] | +4.1 [-2.7, +10.9] | -0.8 [-3.8, +2.2] | +0.0 [-6.1, +6.1] |
| tfidf | pos+vel+acc vs pos+vel | all/pos+vel+acc/none | all/pos+vel/none | +0.5 [-2.5, +3.8] | -2.0 [-7.5, +2.7] | +0.5 [-1.9, +3.0] | +0.0 [-3.4, +4.1] |
| tfidf | length-residualised vs raw | all/pos/length-residualised | all/pos/none | -1.4 [-3.8, +1.1] | +1.4 [-2.7, +5.4] | -1.4 [-3.3, +0.3] | -0.7 [-3.4, +2.0] |
| tfidf | length-residualised vs raw | all/pos+vel/length-residualised | all/pos+vel/none | +0.0 [-3.6, +3.8] | +1.4 [-2.0, +5.4] | -0.8 [-3.3, +1.6] | -1.4 [-6.1, +3.4] |
| tfidf | add upper body to hands | hands+upper/pos/none | hands/pos/none | +2.7 [-1.6, +7.1] | -4.1 [-10.9, +3.4] | +1.6 [-1.1, +4.4] | -0.7 [-6.8, +5.4] |
| tfidf | add hands to upper body | hands+upper/pos/none | upper_body/pos/none | +13.1 [+7.9, +18.0]* | +2.7 [-6.1, +11.6] | +5.2 [+1.6, +8.7]* | +0.0 [-6.1, +6.1] |
| tfidf | add face to hands+upper | hands+upper+face/pos/none | hands+upper/pos/none | +1.1 [-3.8, +6.3] | +2.0 [-4.8, +8.8] | +0.5 [-2.5, +3.6] | +0.7 [-5.4, +6.1] |
| tfidf | add lower body + pose head (= all) | all/pos/none | hands+upper+face/pos/none | -1.6 [-5.5, +2.2] | -5.4 [-10.9, +0.0] | -1.1 [-3.6, +1.6] | -2.0 [-6.1, +2.0] |
| tfidf | add upper body to hands | hands+upper/pos+vel/none | hands/pos+vel/none | -0.8 [-4.9, +3.0] | +2.7 [-4.1, +10.2] | +1.4 [-1.4, +4.1] | -2.0 [-8.2, +4.8] |
| tfidf | add hands to upper body | hands+upper/pos+vel/none | upper_body/pos+vel/none | +10.4 [+4.9, +15.8]* | +10.2 [+1.4, +18.4]* | +3.6 [+0.3, +6.8]* | +8.2 [+2.7, +13.6]* |
| tfidf | add face to hands+upper | hands+upper+face/pos+vel/none | hands+upper/pos+vel/none | +1.4 [-3.3, +6.0] | +0.7 [-6.1, +7.5] | -0.3 [-3.0, +2.5] | +2.7 [-4.8, +10.2] |
| tfidf | add lower body + pose head (= all) | all/pos+vel/none | hands+upper+face/pos+vel/none | -1.6 [-5.7, +2.5] | -4.8 [-10.9, +2.0] | +0.0 [-2.7, +2.5] | -1.4 [-6.1, +4.1] |
