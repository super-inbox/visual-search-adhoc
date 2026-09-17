"""COCO-WholeBody 133-keypoint index layout, as emitted by rtmlib's
Wholebody() call (to_openpose=False, the default — the raw (133,2)/(133,)
keypoints/scores arrays it returns, not its own optional to_openpose
PoseResult reformatting). This is the standard COCO-WholeBody ordering,
confirmed empirically against rtmlib 0.0.13 on a real How2Sign frame in
this repo's own smoke test (left_wrist landed adjacent to the left hand's
root point, right wrist adjacent to the right hand's root point).

Index ranges:
  0:17   body (COCO-17: nose, l_eye, r_eye, l_ear, r_ear, l_shoulder,
         r_shoulder, l_elbow, r_elbow, l_wrist, r_wrist, l_hip, r_hip,
         l_knee, r_knee, l_ankle, r_ankle)
  17:23  feet (6: l_big_toe, l_small_toe, l_heel, r_big_toe, r_small_toe,
         r_heel)
  23:91  face (68)
  91:112 left_hand (21)
  112:133 right_hand (21)

No ASL-specific meaning is attached to any of this — these are the
tracker's own generic anatomical landmark names, not gloss/handshape
labels.
"""

BODY_NAMES = [
    "nose", "left_eye", "right_eye", "left_ear", "right_ear",
    "left_shoulder", "right_shoulder", "left_elbow", "right_elbow",
    "left_wrist", "right_wrist", "left_hip", "right_hip",
    "left_knee", "right_knee", "left_ankle", "right_ankle",
]
FEET_NAMES = [
    "left_big_toe", "left_small_toe", "left_heel",
    "right_big_toe", "right_small_toe", "right_heel",
]

BODY_START, BODY_END = 0, 17
FEET_START, FEET_END = 17, 23
FACE_START, FACE_END = 23, 91
LEFT_HAND_START, LEFT_HAND_END = 91, 112
RIGHT_HAND_START, RIGHT_HAND_END = 112, 133
N_KEYPOINTS = 133

LEFT_WRIST_IDX = BODY_NAMES.index("left_wrist")           # 9
RIGHT_WRIST_IDX = BODY_NAMES.index("right_wrist")          # 10
LEFT_SHOULDER_IDX = BODY_NAMES.index("left_shoulder")       # 5
RIGHT_SHOULDER_IDX = BODY_NAMES.index("right_shoulder")     # 6
NOSE_IDX = BODY_NAMES.index("nose")                         # 0

# rtmlib's own internal visibility convention (wholebody.py's
# format_result: `Keypoint(x, y, score, i) if score >= 0.3 else None`) —
# reused here rather than inventing a new threshold.
KPT_DETECTED_THRESHOLD = 0.3
