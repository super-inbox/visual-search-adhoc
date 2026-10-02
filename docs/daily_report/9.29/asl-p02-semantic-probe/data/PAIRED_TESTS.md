# Paired differences (A − B), 95% paired-bootstrap CI; * = CI excludes 0

## t5enc|frozen

| Comparison | 4-way len-matched | 4-way random | R@10 |
|---|---:|---:|---:|
| ep5 block2 - init block2 | -1.4 [-6.8, +4.8] | +2.7 [-3.4, +8.8] | +3.4 [-2.0, +8.8] |
| ep18 block2 - init block2 | -0.7 [-8.2, +6.8] | +0.0 [-7.5, +7.5] | +4.1 [-2.0, +10.2] |
| ep28 block2 - init block2 | -0.7 [-9.5, +7.5] | +3.4 [-4.8, +11.6] | +3.4 [-2.7, +10.2] |
| ep28 block2 - ep5 block2 (recovered vs collapsed) | +0.7 [-8.2, +8.8] | +0.7 [-7.5, +8.8] | +0.0 [-6.8, +6.8] |
| ep5 block4 - init block4 | -1.4 [-8.8, +6.1] | -4.1 [-10.9, +2.7] | -2.7 [-8.8, +3.4] |
| ep18 block4 - init block4 | -1.4 [-10.2, +8.2] | -2.0 [-9.5, +5.4] | +0.0 [-6.1, +6.8] |
| ep28 block4 - init block4 | -1.4 [-11.6, +8.8] | +0.0 [-8.2, +8.2] | +0.7 [-5.4, +7.5] |
| ep28 block4 - ep5 block4 (recovered vs collapsed) | +0.0 [-9.5, +9.5] | +4.1 [-4.8, +12.9] | +3.4 [-4.1, +10.2] |
| ep5 bridge_ln - init bridge_ln | -1.4 [-7.5, +4.8] | -0.7 [-7.5, +6.1] | -1.4 [-6.1, +4.1] |
| ep18 bridge_ln - init bridge_ln | +0.7 [-8.2, +9.5] | +1.4 [-6.1, +8.8] | -5.4 [-12.2, +0.7] |
| ep28 bridge_ln - init bridge_ln | -4.8 [-13.6, +4.1] | +0.7 [-6.8, +8.8] | -3.4 [-9.5, +2.7] |
| ep28 bridge_ln - ep5 bridge_ln (recovered vs collapsed) | -3.4 [-12.2, +4.8] | +1.4 [-6.8, +9.5] | -2.0 [-8.8, +4.1] |
| init T5 input - init block2 | -1.4 [-7.5, +4.8] | -0.7 [-6.1, +4.8] | +4.1 [-0.7, +8.8] |
| init block4 - init block2 | +2.0 [-3.4, +7.5] | +4.1 [-1.4, +10.2] | +2.7 [-0.7, +6.1] |
| ep5 T5 input - ep5 block2 | -1.4 [-7.5, +4.8] | -4.1 [-10.2, +1.4] | -0.7 [-4.1, +2.7] |
| ep5 block4 - ep5 block2 | +2.0 [-4.1, +8.2] | -2.7 [-8.2, +2.0] | -3.4 [-7.5, +0.7] |
| ep18 T5 input - ep18 block2 | +0.0 [-8.2, +7.5] | +0.7 [-4.8, +6.1] | -5.4 [-10.9, -0.7]* |
| ep18 block4 - ep18 block2 | +1.4 [-4.8, +7.5] | +2.0 [-2.0, +6.1] | -1.4 [-6.1, +3.4] |
| ep28 T5 input - ep28 block2 | -5.4 [-13.6, +2.0] | -3.4 [-8.8, +2.0] | -2.7 [-8.2, +2.7] |
| ep28 block4 - ep28 block2 | +1.4 [-4.8, +7.5] | +0.7 [-4.1, +5.4] | +0.0 [-4.1, +4.1] |
| ep18 block2 - normalised-landmark mean+std input | -6.8 [-16.3, +2.7] | -7.5 [-16.3, +2.0] | -6.8 [-15.0, +0.7] |
| ep18 block4 - normalised-landmark mean+std input | -5.4 [-15.0, +4.8] | -5.4 [-15.0, +3.4] | -8.2 [-15.6, -0.7]* |
| ep18 bridge_ln - normalised-landmark mean+std input | -6.8 [-17.0, +2.0] | -6.8 [-17.0, +3.4] | -12.2 [-21.1, -4.1]* |
| ep28 block2 - normalised-landmark mean+std input | -6.8 [-16.3, +2.7] | -4.1 [-13.6, +4.8] | -7.5 [-15.6, +0.7] |
| ep28 block4 - normalised-landmark mean+std input | -5.4 [-15.6, +3.4] | -3.4 [-12.9, +6.1] | -7.5 [-15.6, +0.7] |
| ep28 bridge_ln - normalised-landmark mean+std input | -12.2 [-21.8, -2.7]* | -7.5 [-17.0, +2.0] | -10.2 [-17.7, -2.7]* |

## t5enc|val

| Comparison | 4-way len-matched | 4-way random | R@10 |
|---|---:|---:|---:|
| ep5 block2 - init block2 | -3.3 [-7.7, +1.1] | -6.3 [-10.1, -2.2]* | -1.6 [-4.4, +1.4] |
| ep18 block2 - init block2 | -4.1 [-9.3, +1.1] | -5.7 [-10.4, -1.1]* | -2.7 [-5.7, +0.5] |
| ep28 block2 - init block2 | -3.6 [-9.0, +1.9] | -4.1 [-8.7, +0.8] | -0.5 [-3.8, +3.0] |
| ep28 block2 - ep5 block2 (recovered vs collapsed) | -0.3 [-5.2, +5.2] | +2.2 [-2.7, +7.1] | +1.1 [-1.9, +4.4] |
| ep5 block4 - init block4 | -0.8 [-5.7, +4.4] | -4.9 [-9.6, -0.8]* | +0.8 [-1.4, +3.3] |
| ep18 block4 - init block4 | -0.8 [-6.3, +4.9] | -2.7 [-7.7, +2.2] | +1.1 [-1.6, +3.8] |
| ep28 block4 - init block4 | -0.3 [-6.0, +5.5] | -4.4 [-9.6, +0.8] | +4.4 [+1.4, +7.7]* |
| ep28 block4 - ep5 block4 (recovered vs collapsed) | +0.5 [-5.2, +6.0] | +0.5 [-4.6, +5.5] | +3.6 [+0.3, +6.8]* |
| ep5 bridge_ln - init bridge_ln | -1.6 [-6.3, +2.7] | -4.1 [-8.5, +0.5] | +0.5 [-1.9, +3.0] |
| ep18 bridge_ln - init bridge_ln | -3.6 [-9.0, +1.9] | -4.4 [-9.3, +0.5] | +0.0 [-3.0, +3.0] |
| ep28 bridge_ln - init bridge_ln | -0.3 [-5.7, +5.2] | -4.9 [-10.1, -0.3]* | +2.2 [-1.1, +5.5] |
| ep28 bridge_ln - ep5 bridge_ln (recovered vs collapsed) | +1.4 [-4.1, +6.8] | -0.8 [-6.0, +4.4] | +1.6 [-1.9, +5.2] |
| init T5 input - init block2 | -0.8 [-4.9, +3.6] | -2.2 [-5.7, +1.4] | -1.4 [-3.8, +0.8] |
| init block4 - init block2 | -0.8 [-4.6, +3.0] | -0.8 [-3.8, +2.2] | -2.7 [-4.6, -0.8]* |
| ep5 T5 input - ep5 block2 | +0.8 [-3.3, +4.9] | +0.0 [-4.1, +3.8] | +0.8 [-1.9, +3.3] |
| ep5 block4 - ep5 block2 | +1.6 [-1.6, +5.2] | +0.5 [-2.7, +3.6] | -0.3 [-2.5, +1.9] |
| ep18 T5 input - ep18 block2 | -0.3 [-5.2, +4.9] | -0.8 [-4.9, +3.6] | +1.4 [-1.4, +3.8] |
| ep18 block4 - ep18 block2 | +2.5 [-1.4, +6.6] | +2.2 [-1.1, +5.7] | +1.1 [-0.8, +3.0] |
| ep28 T5 input - ep28 block2 | +2.5 [-2.5, +7.1] | -3.0 [-6.8, +0.8] | +1.4 [-1.4, +4.1] |
| ep28 block4 - ep28 block2 | +2.5 [-1.6, +6.6] | -1.1 [-4.9, +2.5] | +2.2 [+0.3, +4.4]* |
| ep18 block2 - normalised-landmark mean+std input | -8.7 [-15.3, -2.5]* | -7.4 [-13.1, -1.6]* | -6.8 [-10.7, -3.3]* |
| ep18 block4 - normalised-landmark mean+std input | -6.3 [-12.6, -0.5]* | -5.2 [-10.9, +0.8] | -5.7 [-9.6, -1.9]* |
| ep18 bridge_ln - normalised-landmark mean+std input | -9.0 [-15.6, -2.5]* | -8.2 [-14.2, -2.2]* | -5.5 [-9.3, -1.6]* |
| ep28 block2 - normalised-landmark mean+std input | -8.2 [-14.5, -2.2]* | -5.7 [-11.5, +0.3] | -4.6 [-8.7, -0.8]* |
| ep28 block4 - normalised-landmark mean+std input | -5.7 [-12.0, +0.5] | -6.8 [-12.8, -0.8]* | -2.5 [-6.3, +1.4] |
| ep28 bridge_ln - normalised-landmark mean+std input | -5.7 [-12.6, +0.5] | -8.7 [-15.0, -3.0]* | -3.3 [-7.4, +0.5] |

## tfidf|frozen

| Comparison | 4-way len-matched | 4-way random | R@10 |
|---|---:|---:|---:|
| ep5 block2 - init block2 | -5.4 [-12.2, +2.0] | -2.7 [-8.2, +2.7] | -2.0 [-8.2, +4.1] |
| ep18 block2 - init block2 | -0.7 [-8.2, +6.8] | -4.8 [-12.2, +2.7] | -1.4 [-6.8, +4.1] |
| ep28 block2 - init block2 | -1.4 [-8.8, +6.1] | -2.0 [-10.2, +6.1] | +0.0 [-6.1, +6.1] |
| ep28 block2 - ep5 block2 (recovered vs collapsed) | +4.1 [-3.4, +11.6] | +0.7 [-6.8, +8.2] | +2.0 [-4.8, +9.5] |
| ep5 block4 - init block4 | -6.1 [-12.9, +0.0] | -8.8 [-15.0, -2.7]* | +0.7 [-4.8, +6.1] |
| ep18 block4 - init block4 | +0.0 [-7.5, +7.5] | -5.4 [-13.6, +2.0] | +2.0 [-2.7, +6.8] |
| ep28 block4 - init block4 | -2.0 [-10.2, +6.1] | -1.4 [-9.5, +6.8] | +1.4 [-4.1, +7.5] |
| ep28 block4 - ep5 block4 (recovered vs collapsed) | +4.1 [-3.4, +11.6] | +7.5 [+0.7, +15.0]* | +0.7 [-5.4, +7.5] |
| ep5 bridge_ln - init bridge_ln | -0.7 [-6.8, +6.1] | -2.7 [-10.2, +4.8] | +2.7 [-2.7, +8.8] |
| ep18 bridge_ln - init bridge_ln | +0.7 [-6.8, +8.8] | +1.4 [-6.1, +8.8] | +6.1 [+1.4, +10.9]* |
| ep28 bridge_ln - init bridge_ln | -0.7 [-8.2, +6.8] | +0.7 [-6.8, +8.2] | +4.1 [-1.4, +9.5] |
| ep28 bridge_ln - ep5 bridge_ln (recovered vs collapsed) | +0.0 [-7.5, +7.5] | +3.4 [-4.8, +10.9] | +1.4 [-4.8, +7.5] |
| init T5 input - init block2 | -3.4 [-9.5, +2.7] | -6.8 [-12.9, -0.7]* | -4.8 [-9.5, +0.0] |
| init block4 - init block2 | -2.0 [-6.8, +2.7] | -2.7 [-6.8, +1.4] | -2.7 [-7.5, +2.0] |
| ep5 T5 input - ep5 block2 | +1.4 [-4.1, +6.8] | -6.8 [-13.6, -0.7]* | +0.0 [-4.1, +4.1] |
| ep5 block4 - ep5 block2 | -2.7 [-7.5, +2.0] | -8.8 [-14.3, -3.4]* | +0.0 [-3.4, +4.1] |
| ep18 T5 input - ep18 block2 | -2.0 [-8.8, +4.1] | -0.7 [-7.5, +6.1] | +2.7 [-2.0, +7.5] |
| ep18 block4 - ep18 block2 | -1.4 [-7.5, +4.8] | -3.4 [-9.5, +2.7] | +0.7 [-4.1, +5.4] |
| ep28 T5 input - ep28 block2 | -2.7 [-8.2, +2.7] | -4.1 [-10.2, +2.0] | -0.7 [-5.4, +3.4] |
| ep28 block4 - ep28 block2 | -2.7 [-8.2, +2.7] | -2.0 [-7.5, +3.4] | -1.4 [-3.4, +0.0] |
| ep18 block2 - normalised-landmark mean+std input | +0.7 [-8.8, +10.2] | -7.5 [-16.3, +1.4] | +2.0 [-4.1, +7.5] |
| ep18 block4 - normalised-landmark mean+std input | -0.7 [-10.9, +8.8] | -10.9 [-19.7, -2.0]* | +2.7 [-4.1, +8.8] |
| ep18 bridge_ln - normalised-landmark mean+std input | -1.4 [-11.6, +8.2] | -8.2 [-17.7, +1.4] | +4.8 [-1.4, +10.9] |
| ep28 block2 - normalised-landmark mean+std input | +0.0 [-9.5, +9.5] | -4.8 [-13.6, +4.8] | +3.4 [-2.7, +9.5] |
| ep28 block4 - normalised-landmark mean+std input | -2.7 [-12.2, +7.5] | -6.8 [-16.3, +3.4] | +2.0 [-4.1, +8.2] |
| ep28 bridge_ln - normalised-landmark mean+std input | -2.7 [-12.3, +6.8] | -8.8 [-17.7, +0.7] | +2.7 [-3.4, +8.2] |

## tfidf|val

| Comparison | 4-way len-matched | 4-way random | R@10 |
|---|---:|---:|---:|
| ep5 block2 - init block2 | -5.7 [-10.7, -1.1]* | -3.8 [-9.0, +1.4] | -1.4 [-4.1, +1.4] |
| ep18 block2 - init block2 | -5.2 [-10.9, +0.5] | -3.3 [-8.5, +2.2] | -1.6 [-4.6, +1.4] |
| ep28 block2 - init block2 | -6.3 [-12.0, -0.5]* | -5.2 [-10.4, +0.3] | -1.6 [-4.9, +1.6] |
| ep28 block2 - ep5 block2 (recovered vs collapsed) | -0.5 [-6.0, +5.2] | -1.4 [-6.8, +3.8] | -0.3 [-3.0, +2.5] |
| ep5 block4 - init block4 | -1.9 [-6.3, +2.5] | -3.0 [-7.9, +1.9] | -1.1 [-3.8, +1.6] |
| ep18 block4 - init block4 | -4.9 [-9.8, +0.0] | -4.4 [-9.8, +0.8] | -1.9 [-4.6, +0.8] |
| ep28 block4 - init block4 | -3.6 [-9.0, +1.9] | -5.7 [-11.5, -0.3]* | -0.3 [-3.3, +2.7] |
| ep28 block4 - ep5 block4 (recovered vs collapsed) | -1.6 [-7.1, +3.8] | -2.7 [-8.2, +3.0] | +0.8 [-1.9, +3.8] |
| ep5 bridge_ln - init bridge_ln | -1.9 [-6.6, +2.7] | +1.4 [-3.0, +5.7] | -2.2 [-4.9, +0.5] |
| ep18 bridge_ln - init bridge_ln | -4.9 [-10.1, +0.3] | +0.3 [-5.5, +5.7] | -1.9 [-4.9, +0.8] |
| ep28 bridge_ln - init bridge_ln | +0.5 [-4.9, +6.3] | -1.4 [-6.8, +4.1] | -2.5 [-5.5, +0.3] |
| ep28 bridge_ln - ep5 bridge_ln (recovered vs collapsed) | +2.5 [-2.7, +7.9] | -2.7 [-7.9, +2.7] | -0.3 [-2.7, +2.2] |
| init T5 input - init block2 | -8.2 [-12.3, -3.8]* | -4.6 [-9.0, +0.0] | -0.3 [-3.0, +2.5] |
| init block4 - init block2 | -4.4 [-7.9, -0.8]* | -0.3 [-3.8, +3.3] | -0.8 [-2.5, +0.8] |
| ep5 T5 input - ep5 block2 | -4.4 [-8.2, -0.3]* | +0.5 [-3.6, +4.6] | -1.1 [-3.0, +0.8] |
| ep5 block4 - ep5 block2 | -0.5 [-3.3, +2.2] | +0.5 [-3.3, +4.4] | -0.5 [-2.2, +1.1] |
| ep18 T5 input - ep18 block2 | -7.9 [-12.0, -3.8]* | -1.1 [-5.5, +3.0] | -0.5 [-2.7, +1.4] |
| ep18 block4 - ep18 block2 | -4.1 [-7.9, -0.5]* | -1.4 [-5.5, +2.7] | -1.1 [-2.7, +0.5] |
| ep28 T5 input - ep28 block2 | -1.4 [-5.7, +3.0] | -0.8 [-5.2, +3.8] | -1.1 [-3.3, +0.8] |
| ep28 block4 - ep28 block2 | -1.6 [-5.2, +1.9] | -0.8 [-4.1, +2.7] | +0.5 [-0.5, +1.9] |
| ep18 block2 - normalised-landmark mean+std input | -11.2 [-17.5, -4.9]* | -7.7 [-13.7, -1.1]* | -6.0 [-9.8, -2.5]* |
| ep18 block4 - normalised-landmark mean+std input | -15.3 [-21.9, -8.7]* | -9.0 [-15.3, -2.7]* | -7.1 [-10.9, -3.6]* |
| ep18 bridge_ln - normalised-landmark mean+std input | -19.1 [-25.4, -13.1]* | -8.7 [-15.3, -2.2]* | -6.6 [-10.7, -3.0]* |
| ep28 block2 - normalised-landmark mean+std input | -12.3 [-18.6, -6.0]* | -9.6 [-15.6, -3.6]* | -6.0 [-9.8, -2.2]* |
| ep28 block4 - normalised-landmark mean+std input | -13.9 [-19.9, -7.9]* | -10.4 [-16.7, -4.4]* | -5.5 [-9.3, -1.6]* |
| ep28 bridge_ln - normalised-landmark mean+std input | -13.7 [-20.0, -7.1]* | -10.4 [-16.4, -4.4]* | -7.1 [-10.9, -3.6]* |

