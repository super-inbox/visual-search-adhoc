"""Build model_case_analysis.csv and model_case_analysis.html for the 45-clip ASL review package.

The per-case analysis below was written by a model (Claude Opus 5.5, claude-opus-5-5) from timestamped 4 fps contact
sheets of each clip (scripts/build_contact_sheets.py) plus the ground truth, the provisional our/old output, the official
Uni-Sign output and the existing automatic weak labels. It is model_review / unverified: not an ASL-fluent human
verification. Human-review columns are copied through unchanged (blank, review_status = not_started).

    python3 -I scripts/build_model_case_analysis.py
"""
import csv
import html
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent.parent
SHEET = HERE.parent.parent / "10.18" / "asl-review-inspection-sheet"
MODEL = "claude-opus-5-5"
INPUT = "contact_sheets_4fps_center_crop_720px (timestamped stills; no motion, no audio)"

CATEGORIES = ["fingerspelling", "name", "number", "negation", "question", "spatial_relation", "repetition",
              "general_semantic"]

# d = physical description (only what is visible in the stills), dc = its confidence,
# our / off = ground-truth-vs-output error, sh = shared failure (yes / partial / no) + note,
# p = primary category, a = all categories, ev = evidence (timestamps are clip seconds), c = diagnosis confidence,
# amb = unresolved ambiguity, fl = model observation flags, rep = repetition analysis (official loops + any loop)
A = {
    "R01": dict(
        d="0.25-0.75 s single-hand handshapes near the shoulder; 1.5-2.0 s an upright index-type handshape held while "
          "the other index points at it; 2.5-3.0 s index near the chin; 3.25-3.75 s raised L/index-up handshape "
          "again with the other index pointing at it.",
        dc="medium",
        our="substitution: keeps 'ball' and 'D' but turns the letter-replacement explanation into 'ball knife with a "
            "D red tail'; 'replace', 'say', 'dall' lost.",
        off="degenerate loop: 'I'm going to use a D,' then 'a D,' x22; keeps only the letter D.",
        sh="partial", shn="both keep the letter D; both lose the B->D substitution meaning ('dall').",
        p="fingerspelling", a="fingerspelling;repetition;general_semantic",
        ev="The held-handshape-plus-pointing configuration occurs twice with different handshapes (1.5-2.0 s, "
           "3.25-3.75 s), consistent with contrasting two letters, but the letters are not legible at 4 fps. The "
           "video shows two contrasted references, not 20+ repetitions.",
        c="low",
        amb="Which letters are shown; whether 'dall' is fingerspelled or mouthed.",
        fl="official_text_loop_not_in_automatic_9",
        rep="Official output loops on 'a D,' but its automatic primary type is hallucination, so it is not one of the "
            "9 automatic repetition_loop cases. No visible repeated sign sequence supports the loop.",
    ),
    "R02": dict(
        d="0-1.5 s the right hand alone at shoulder height forms a rapid series of different handshapes "
          "(fingerspelling-like); 1.75-4.0 s two-handed signing at chest/chin height.",
        dc="medium",
        our="wrong name ('Amelia') and occupation ('rescue fighter'); keeps the greeting frame 'Hi, I'm'.",
        off="wrong name ('Dr. Erica Millian'), invents 'Red Sox', 'full moon in Spanish'; keeps 'Hello, I'm ... with'.",
        sh="yes", shn="both keep a greeting + invented name; both lose every name/place (Mike Camelin, SunState, "
                      "Kissimmee, Florida).",
        p="fingerspelling", a="fingerspelling;name;general_semantic",
        ev="Fingerspelling-like run at 0-1.5 s sits where the name would be. A 4.19 s clip with ~1.5 s of single-hand "
           "spelling seems too short for two spelled names + organisation + city + state, so part of the reference is "
           "probably outside this window.",
        c="medium",
        amb="Letters are not legible in 300 px stills; cannot tell which names are spelled or whether the place names "
            "are in this clip at all.",
        fl="reference_longer_than_visible_signing",
        rep="",
    ),
    "R03": dict(
        d="0-2.75 s hands clasped at rest (no signing); signing 2.75-4.0 s and 5.0-7.25 s; right hand drops to the lap "
          "7.25-8.0 s and 13.5-13.75 s; hand at the temple 12.5-13.0 s; two thumb-and-pinky-extended handshapes "
          "14.25-14.5 s.",
        dc="high",
        our="'degree of a cochlea' then 'a cochlea,' x5; professor, CV, '25 years ago' all lost.",
        off="keeps 'full', 'teacher/instructor', 'still', 'C.V.'; repeats 'fellow instructor' and 'I always refer to my "
            "C.V.'; loses 'where did he go to school 25 years ago'.",
        sh="partial", shn="both drop the number 25 and the final clause; both repeat (ours much worse).",
        p="number", a="number;repetition;general_semantic",
        ev="No clear number handshape identified at 4 fps; the Y-like two-handed shapes at 14.25-14.5 s are not "
           "readable as 25. The first ~2.75 s are idle.",
        c="low",
        amb="Where (or whether) '25' is signed in this window; the official input (19.52 s) is longer than this clip "
            "(15.26 s), so the official model saw material that is not in this video.",
        fl="idle_start_2.75s;official_window_differs_from_clip",
        rep="Official loop (rep3 0.156) is mild: a repeated clause about the CV, not a token loop. The visible signing "
            "is varied, with no repeated sign sequence. Our output loops harder on 'a cochlea'.",
    ),
    "R04": dict(
        d="0-1.0 s hands at rest; 1.25 s hand raised; 1.5-2.75 s the right hand alone at the shoulder forms a series of "
          "handshapes (fingerspelling-like); 3.0-3.25 s hand sweep. Only ~2.3 s of signing.",
        dc="high",
        our="generic 'talk to you ... what it looks like'; no name, no Spanish, no negation, no question.",
        off="invents name 'Brandon Daniels', keeps 'Spanish'; loses 'didn't know' and 'did you?'.",
        sh="yes", shn="both lose the name, the negation and the question.",
        p="name", a="name;fingerspelling;negation;question;general_semantic",
        ev="Fingerspelling-like run 1.5-2.75 s is where 'Bobby Larew' would be. With 1 s idle at the start, the ~2.3 s "
           "of signing cannot plausibly contain 'Buenos Dias' + name + negated clause + tag question.",
        c="medium",
        amb="Whether the negation and tag question are inside this window at all; headshake/brow marking cannot be "
            "judged from stills.",
        fl="idle_start_1.0s;reference_longer_than_visible_signing",
        rep="",
    ),
    "R05": dict(
        d="0.25-2.75 s the right hand alone near the face/shoulder forms a series of handshapes (fingerspelling-like; "
          "V-like shape near the cheek ~1.0-1.25 s); 3.0-5.0 s two-handed signing at chest height.",
        dc="medium",
        our="invents 'Chris Rudy', 'heartwarming dancer'; keeps 'Hi, I'm' and a heart concept.",
        off="invents 'Lisa Richey', 'heart runner trainer'; keeps 'Hi, I'm', heart, trainer.",
        sh="yes", shn="both substitute a plausible-looking invented name; both keep 'heart' (cardio).",
        p="name", a="name;fingerspelling;general_semantic",
        ev="The fingerspelling-like run aligns with the name slot. Official 'Lisa' shares the initial L with 'Les', "
           "which is weak evidence of partial letter recognition.",
        c="medium",
        amb="Letters not legible; whether 'Whitley' is fully spelled.",
        fl="",
        rep="",
    ),
    "R06": dict(
        d="0.25-1.5 s the right hand held up produces successive distinct handshapes (L-like, flat, index-up) - "
          "fingerspelling-like; 2.25-2.5 s bent-finger hand at the temple/eye; 3.0-4.0 s two-handed signing.",
        dc="medium",
        our="'For Alburn's new onion' - 'Albondigas' becomes 'Alburn's new'; keeps 'onion'.",
        off="'alburna's new' twice + 'onion'.",
        sh="yes", shn="both emit an 'Albur(n)-' fragment for 'Albondigas' and keep 'onion'.",
        p="fingerspelling", a="fingerspelling;name;general_semantic",
        ev="Two independently prepared inputs give the same 'Albur-' fragment, consistent with partial recovery of a "
           "spelled word from the 0.25-1.5 s run. Hand at the temple/eye at 2.25-2.5 s is where ONION is usually "
           "signed (unverified).",
        c="medium",
        amb="Whether 'Albondigas' is fully spelled or abbreviated.",
        fl="",
        rep="",
    ),
    "R07": dict(
        d="Signing throughout; 1.5-2.75 s both palms up, held ~1 s; 3.25-3.5 s two flat hands side by side; "
          "6.0-6.5 s index at the mouth/chin; 7.75-8.0 s hands lowering.",
        dc="medium",
        our="keeps 'buy', 'few books', 'show you toys', 'Barbie's'; loses 'prices', 'listed'.",
        off="keeps 'first', 'buy', 'few books', 'toy prices', 'Barbie'; 'slow book' error.",
        sh="partial", shn="both keep the gist and the name; both lose 'listed in here'.",
        p="general_semantic", a="general_semantic",
        ev="Name is NOT missed: our output has 'Barbie's'. The automatic 'names MISSED by prod' label is a "
           "tokenisation false positive (possessive).",
        c="medium",
        amb="",
        fl="weak_label_false_positive_name",
        rep="",
    ),
    "R08": dict(
        d="0-0.75 s hands at rest; from ~1.0 s two hands raised with closed/hooked handshapes; 2.5-4.25 s the left hand "
          "held in a fist while the right index points to/works at it; 4.5-5.5 s further two-handed signing.",
        dc="medium",
        our="'connect the wire'; 'thread'->'wire', 'hook' and 'secure' lost.",
        off="'connect the wire and how to get it secure'; keeps 'secure', loses 'hook'.",
        sh="yes", shn="both render 'thread' as 'wire' and drop 'hook'.",
        p="general_semantic", a="general_semantic",
        ev="'ALVIN DEDEUX:' is a transcript speaker label, not content; no extended fingerspelling run is visible. The "
           "automatic fingerspelling label comes from this label and is very likely an annotation artifact.",
        c="medium",
        amb="",
        fl="gt_speaker_label_artifact;idle_start_0.75s",
        rep="",
    ),
    "R09": dict(
        d="Only 5 frames (1.24 s); 0.75 s a thumb-and-pinky (Y-like, possibly with index) handshape; 1.0 s a "
          "two-finger extended handshape; continuous movement.",
        dc="low",
        our="'talk about now is the juices' - name lost.",
        off="'talk about IgG today' - a letter-like acronym in place of 'Yu-Gi-Oh'.",
        sh="partial", shn="both keep 'talk about'; both lose the name; official produces a letter-level token.",
        p="fingerspelling", a="fingerspelling;name;general_semantic",
        ev="Y-like handshape at 0.75 s would fit a Y-initial spelling, but 5 stills are not enough.",
        c="low",
        amb="Clip too short to judge; spelled vs lexical sign for 'Yu-Gi-Oh' unknown.",
        fl="very_short_clip",
        rep="",
    ),
    "R10": dict(
        d="Signing 0-4.25 s (left hand held upright while the right index points to it 0-2.5 s); 4.5-19.5 s hands "
          "resting in the lap, no signing (~15 s; signer yawns ~9.75-10.75 s); signing resumes 19.5-25.3 s.",
        dc="high",
        our="keeps G / low G / D / low D; 'double-stops' -> 'two parts'; keeps 'choices'.",
        off="keeps G, low G, D with the low D, 'unlike some of the double ...'; loses 'you have a choice'.",
        sh="partial", shn="both get the note names; both garble 'double-stop'.",
        p="general_semantic", a="general_semantic;number",
        ev="~60 % of the clip is idle. The automatic 'number inserted by prod' is our 'two parts' for 'double-stops' - "
           "an English-side artifact, not a signed number. Pointing at the held hand 0-2.5 s fits referencing items "
           "(strings) on a list.",
        c="medium",
        amb="",
        fl="long_idle_segment_4.5-19.5s;weak_label_false_positive_number",
        rep="",
    ),
    "R11": dict(
        d="0-2.5 s repeated cyclic motion of the right hand over the cupped left hand; 3.0-6.0 s two-handed signing, "
          "spread hands raised; 8.0-8.75 s raised fists at shoulder height; 10.5-11.25 s and 15.25-15.75 s hands "
          "clasped (pauses); 12.25-14.0 s both hands raised with spread fingers; 17.0-18.5 s two-handed signing.",
        dc="medium",
        our="'They're ready to go,' x6.",
        off="'You're ready to go,' x6+.",
        sh="yes", shn="near-identical 'ready to go' loop in both; Morris, festive, Christmas, mash all lost.",
        p="repetition", a="repetition;name;general_semantic",
        ev="Only 0-2.5 s is visibly repetitive (fits 'mash'); the rest is varied signing. The reference mixes "
           "narration with a parenthetical lyric '(Ready to rock and roll today)' - both models lock onto 'ready to'.",
        c="medium",
        amb="Whether 'Morris sings' / the lyric is signed or is audio-described content added to the transcript.",
        fl="gt_contains_parenthetical_lyric",
        rep="OFFICIAL LOOP (rep3 0.826). The same loop appears with both input preparations (official 18.20 s vs ours "
            "18.67 s), so preprocessing does not explain it. The visible signing does not repeat a sign 6 times; the "
            "loop looks like decoder lock-in after a partially correct prefix ('ready to').",
    ),
    "R12": dict(
        d="Continuous signing for 23 s, no long pauses; 1.75-4.75 s repeated palms-up two-handed gestures; "
          "12.0-13.5 s hand repeatedly at the mouth/chin; 15.0-16.25 s open hand at the mouth with the other hand "
          "spread; 18.0-19.75 s left hand held up with changing handshapes while the right index points to it.",
        dc="medium",
        our="unrelated: installing a door, waiting for a camera; 'you're going to' loop.",
        off="'The other thing ...' (~'What else'), '... a bottle of red powder' (~red pepper); chicken wings, Cajun, "
            "chili, negation lost.",
        sh="partial", shn="both lose wings/Cajun/chili and the negated clause; official keeps 'other thing' and 'red'.",
        p="general_semantic", a="general_semantic;negation;name;repetition",
        ev="Palms-up gestures at the start fit a 'what else' framing, which the official partly recovers. The "
           "18.0-19.75 s pointing-at-held-hand run could be a list or a spelling (e.g. 'Cajun') - unverified. No "
           "identifiable negation in the stills.",
        c="low",
        amb="Where 'didn't want to use those chili peppers' is signed; headshake not visible in stills.",
        fl="",
        rep="Our output loops ('repetition_loop' label); official does not. No repeated visible sequence.",
    ),
    "R13": dict(
        d="0-0.75 s single-hand handshapes at the shoulder (L/V-like); 1.0-1.25 s hands together; 1.75-2.0 s "
          "thumb-up handshapes; 3.75 s two thumb-up hands. No extended fingerspelling run.",
        dc="medium",
        our="'This is a new set of cheaters' - card name lost.",
        off="'Hi, I'm Michael Handler, and I'm a new cold set collector' - invents a self-introduction; keeps "
            "'new cold set'.",
        sh="partial", shn="both lose 'Whalebone Glider'; both keep 'new ... set'.",
        p="name", a="name;general_semantic",
        ev="The official inserts a 'Hi, I'm <name>' template where the reference has none - same pattern as R02, R04, "
           "R05 and R35, i.e. a decoder prior for introductions.",
        c="medium",
        amb="Whether 'Whalebone Glider' is spelled in the short 0-0.75 s segment.",
        fl="official_intro_template_hallucination",
        rep="",
    ),
    "R14": dict(
        d="0.25-1.25 s single hand at the mouth/chin with changing handshapes; 1.5-2.25 s wrists crossed, then pinched "
          "hands at the throat; 3.25-4.25 s fist at the temple while the other hand is flat, palm out; 5.0-7.0 s hands "
          "at rest (~2 s); 10.5-12.5 s two flat hands moving together at chest height.",
        dc="medium",
        our="'Aces are defenders ... morning suction ... etiquette at the wedding'.",
        off="'A compost butterfly ... with a morning suit ... formal night wedding'.",
        sh="yes", shn="both keep morning suit/wedding; both garble 'ascot tie' into an A-initial word; both drop "
                      "'European', 'English' and 'didn't use a lot of these'.",
        p="fingerspelling", a="fingerspelling;negation;name;general_semantic",
        ev="Both outputs start with an A-word (Aces / A compost) where the reference has 'ascot', fitting partial "
           "letter recovery from the 0.25-1.25 s run. Pinched hands at the throat 1.5-2.25 s fit a necktie "
           "depiction.",
        c="low",
        amb="Whether 'ascot' is spelled; whether the closing negation is inside the window (no negation sign "
            "identified; final 12.25-13 s unclear).",
        fl="idle_mid_5.0-7.0s",
        rep="",
    ),
    "R15": dict(
        d="5 frames (1.15 s): closed hand at the chin/mouth (0.25 s, 0.75 s) while the other hand rests flat on the "
          "chest; squint at 1.0 s.",
        dc="low",
        our="'Is it a fish?' - keeps question form, wrong content.",
        off="'It doesn't have to be English.' - keeps 'English', loses the question, inserts negation.",
        sh="no", shn="complementary errors: ours keeps the question, official keeps 'English'.",
        p="question", a="question;negation;general_semantic",
        ev="Hand at the mouth fits a speech/language sign (SPEAK or ENGLISH-related) - unverified.",
        c="low",
        amb="Question marking (brows) cannot be judged from 5 stills.",
        fl="very_short_clip",
        rep="",
    ),
    "R16": dict(
        d="0-1.0 s left palm-up hand held while the right hand points/pinches above it; 1.25 s hand at the temple; "
          "3.75 s hand at the forehead; 4.0-4.5 s index-up handshape at the cheek; 4.75 s and 6.5-7.0 s both palms "
          "up; 5.25-5.5 s hands clasped; 7.75-8.0 s clawed hands at the cheeks.",
        dc="medium",
        our="'know where they are and to know where they are' - repetition.",
        off="'It doesn't matter where you are,' x2 + 'it doesn't matter' - loop; inserts negation.",
        sh="yes", shn="both loop on a 'where ... are' frame; both lose bedding, 'every six months', feces.",
        p="repetition", a="repetition;number;negation;general_semantic",
        ev="Palms-up gesture occurs at least twice (4.75 s, 6.5-7.0 s) - a possible visual trigger for a repeated "
           "'where/doesn't matter' phrase. No SIX handshape identified; the index-up at 4.0-4.5 s is not six.",
        c="low",
        amb="Where 'every six months' is signed; whether the palms-up gestures are lexical.",
        fl="",
        rep="OFFICIAL LOOP (rep3 0.462). Official input = our input = 8.32 s (medium), so neither length nor window "
            "explains it. The visible signing is mostly varied; only the palms-up gesture recurs.",
    ),
    "R17": dict(
        d="Left hand held in a closed/O-like shape for nearly the whole clip; 0.5-1.25 s right hand flat/thumb "
          "pointing; 1.5-1.75 s right hand raised with the thumb extended up at shoulder height; 2.0-4.5 s right hand "
          "repeatedly placed onto/around the held left hand.",
        dc="medium",
        our="'a little groove in it' x2 - number lost.",
        off="'big ball ... twist the ball' - keeps 'big', number lost.",
        sh="yes", shn="both lose 'ten' and 'line the whole thing'.",
        p="number", a="number;general_semantic",
        ev="Thumb-up handshape at 1.5-1.75 s is consistent with ASL TEN (thumb-up + shake; the shake is not visible in "
           "stills). Repeated placing at 2.0-4.5 s fits 'put ten of these on it, line the whole thing'.",
        c="low",
        amb="Whether 1.5-1.75 s is TEN or another A/thumb-handshape sign.",
        fl="",
        rep="",
    ),
    "R18": dict(
        d="0.75 s index at the lips; 1.0-1.25 s stacked fists; 1.5-2.75 s left hand raised while the right hand moves; "
          "3.0 s right hand with four fingers extended, thumb folded; 3.25-3.5 s bent spread fingers; 3.75-4.25 s left "
          "hand raised in a grip while the right hand is at the body.",
        dc="medium",
        our="'not actually a guitar, it's got four screws on it' - keeps 'four', inserts negation.",
        off="'four sleeves' x2, 'one of these' - keeps 'four', repeats.",
        sh="partial", shn="both get 'four'; both miss 'stringed instrument' and 'head stock'.",
        p="repetition", a="repetition;negation;general_semantic",
        ev="FOUR-like handshape is visible once at 3.0 s - both outputs recover 'four', so the number is not the "
           "failure. The posture at 3.75-4.25 s looks like holding an instrument neck.",
        c="medium",
        amb="Official input (5.91 s) is longer than this clip (4.40 s); it may contain a second FOUR not visible here.",
        fl="official_window_differs_from_clip",
        rep="OFFICIAL LOOP (rep3 0.333). 'four sleeves' twice; only one FOUR is visible in this clip. Our output does "
            "not loop. Medium-length input, so not a long-input failure.",
    ),
    "R19": dict(
        d="1.0-1.75 s right index touching the left thumb; 6.25-7.5 s index touching successive fingers of the other "
          "hand; 9.0 s two-finger handshape near the face; 12.0 s three-finger handshape.",
        dc="medium",
        our="'first thing ... learn the parts ... practicing ... blue brew'.",
        off="'first thing ... learn the parts of the brush, the brew, the brew, the brew, the brew'.",
        sh="yes", shn="both map 'bow' to 'brew/brush'; both drop the list of positions (first..sixth).",
        p="number", a="number;repetition;general_semantic",
        ev="Index-to-thumb then index-to-successive-fingers (1.0-1.75 s, 6.25-7.5 s) is the shape of a list on the "
           "non-dominant hand; number-like handshapes at 9.0 s and 12.0 s fit ordinal positions. Both outputs omit "
           "the list.",
        c="low",
        amb="Which ordinals are signed; why both models produce 'brew' for 'bow' (mouthing?).",
        fl="",
        rep="Official repeats 'the brew' x4 (automatic type hallucination, not one of the 9). No repeated visible sign.",
    ),
    "R20": dict(
        d="Continuous signing; 7.75-8.0 s right hand with thumb-index contact and the other fingers extended at "
          "shoulder height; 12.0-17.5 s both flat hands, palms down, held horizontally and moved side to side "
          "repeatedly.",
        dc="medium",
        our="'about 15 minutes ... fully cooked ... the rat in the rest of the rest of the rat in the nine' - loop; "
            "has 'nine'.",
        off="'next 10 minutes and for the last 9 minutes ... bounce back and forth' x3.",
        sh="partial", shn="both partly recover 9 (with spurious 15/10); both lose freezer / lay flat / single layer; "
                          "both loop.",
        p="repetition", a="repetition;number;general_semantic",
        ev="Thumb-index contact with three fingers extended (7.75-8.0 s) is consistent with NINE. Repeated lateral "
           "flat-hand movement at 12.0-17.5 s fits 'lay it flat in a single layer'.",
        c="low",
        amb="Whether the lateral flat-hand movement is a depicting verb for laying flat, or something else.",
        fl="",
        rep="OFFICIAL LOOP (rep3 0.188). The repeated 'bounce back and forth' coincides with a visibly repeated "
            "side-to-side flat-hand movement (12.0-17.5 s): the loop may be a mis-lexicalised but genuinely repetitive "
            "depicting movement, not only a decoder failure. Long input (16.42 s).",
    ),
    "R21": dict(
        d="1.0 s right hand fully spread at the shoulder; 2.25-2.5 s index pointing; 5.25-5.75 s fists at the mouth; "
          "6.75-7.75 s both open hands raised high; 8.25-8.5 s fists at the chest; 9.0-9.5 s two-finger handshape "
          "near the face.",
        dc="medium",
        our="'catching the ball ... stretch, open, and lift, and lift, and lift...' - loop.",
        off="'once you've done that with your last one ... holding on to it ... finding depth'.",
        sh="yes", shn="both lose 'forty-five seconds' and 'eight deep counts'.",
        p="number", a="number;repetition;general_semantic",
        ev="Raised open hands at 6.75-7.75 s fit 'come up to the sky' (neither output has it; ours has 'lift'). "
           "Spread hand at 1.0 s could be FIVE (part of 45) - unverified. Official 'depth' is a near-miss for 'deep'.",
        c="low",
        amb="Where 45 and 8 are signed.",
        fl="",
        rep="Our output loops ('and lift'); official does not.",
    ),
    "R22": dict(
        d="0-0.25 s both palms up; 0.5-0.75 s thumb/closed hand under the chin; signing ends ~1.0 s, hands at rest "
          "1.25-1.75 s.",
        dc="medium",
        our="'trying to get rid of that plant'.",
        off="'It doesn't grow well.' - negation inserted (reference has none).",
        sh="partial", shn="both move into a plant/garden domain; both lose 'at least put it in your garden'.",
        p="negation", a="negation;general_semantic",
        ev="Thumb under the chin at 0.5-0.75 s is the location/handshape of ASL NOT. If that is what is signed, the "
           "official negation may be grounded in the signing and the English reference is a free translation; then "
           "the automatic 'negation inserted' label would not be an error.",
        c="low",
        amb="Is 0.5-0.75 s NOT, or another chin-located sign? Needs an ASL-fluent reviewer.",
        fl="weak_label_may_be_false_positive",
        rep="",
    ),
    "R23": dict(
        d="Signing 0-3.25 s; rest 3.5-4.25 s; 4.5-9.0 s clawed hands held low near the lap with gaze down; rest "
          "9.25-11.5 s; 12.5-15 s clawed hands low again; 16-20 s open hands spreading outward; rest 21.25-25.8 s "
          "(~4.5 s).",
        dc="high",
        our="'get that rolling pin ... push it down'.",
        off="'take this hole ... open this hole' - keeps 'hole'.",
        sh="yes", shn="both lose the wall / 'I'm not going to let it' / hands-there content.",
        p="general_semantic", a="general_semantic;negation;spatial_relation",
        ev="Much of the clip is mimed action at lap height plus ~7 s of rest; lexical content is sparse. The final "
           "~4.5 s are idle, so the reference's last clause (with the negation) may be outside the signing.",
        c="medium",
        amb="Whether the negation is signed at all in this window.",
        fl="idle_segments_~7s;constructed_action_dominant",
        rep="",
    ),
    "R24": dict(
        d="1.0-1.25 s index at the chin; 1.5-2.0 s index touching index; 2.25-2.75 s pinched/spread hand near the cheek "
          "while the other index points; 3.25 s index at the chin again; 3.5-4.0 s index tapping the fingers of a "
          "V-hand.",
        dc="medium",
        our="'nice red pair and a cat's going to have a red pair' - keeps 'cat'.",
        off="'say either a guy or a cat' - keeps 'say', 'cat', 'either' (for 'neither').",
        sh="partial", shn="both lose the negation ('doesn't', 'neither'); both keep 'cat'.",
        p="negation", a="negation;general_semantic",
        ev="Index-from-chin (1.0 s, 3.25 s) fits SAY; hand near the cheek 2.25-2.75 s fits CAT; V-hand tapping at "
           "3.5-4.0 s fits an EITHER/NEITHER-type sign - the official gets 'either' but not the negation, which may be "
           "carried by a headshake that stills cannot show.",
        c="low",
        amb="Headshake / negative marking not visible in stills.",
        fl="",
        rep="",
    ),
    "R25": dict(
        d="0-1.0 s hands sweeping/laying out in front; 2.0-2.75 s index up near the face; 3.0-3.5 s hand at the other "
          "wrist; 4.0-4.25 s hands together.",
        dc="medium",
        our="'You don't want to have too much mud on the ground' - negation inserted.",
        off="'it won't teach you to soak it ... ready to transplant it into a container' - negation inserted; keeps "
            "'ready'.",
        sh="yes", shn="both insert a negation the reference does not have; both lose mulch/weeds/bed.",
        p="negation", a="negation;general_semantic",
        ev="No negation sign identified. 'keep the weeds down' (suppression) might be read as negative, but that is "
           "speculative.",
        c="low",
        amb="What the 2.0-2.75 s and 3.0-3.5 s signs are.",
        fl="",
        rep="",
    ),
    "R26": dict(
        d="1.85 s: both arms raised high above the head; index pointing and hands overhead throughout; hands partly "
          "leave the top of the crop.",
        dc="high",
        our="'It's going to go up and down.' - keeps vertical movement only.",
        off="'The enemy's going to negotiate.'",
        sh="yes", shn="both lose 'which ... reverse' and the question.",
        p="question", a="question;spatial_relation;general_semantic",
        ev="Very high signing space with hands at/over the frame edge (matches the existing out-of-frame and pose "
           "disagreement flags): the pose input is probably degraded.",
        c="low",
        amb="Question marking not judgeable; what the overhead movement depicts.",
        fl="hands_above_frame",
        rep="",
    ),
    "R27": dict(
        d="0.5-0.75 s the hand grasps the nose; 1.0-1.25 s the hand moves away from the face (blurred pull-off motion); "
          "raised brows / open mouth at 0.0-0.25 s and 1.25-1.5 s.",
        dc="high",
        our="'take the mask off' - removal action kept, nose and question lost.",
        off="'You just pop it off.' - removal action kept, nose and question lost.",
        sh="yes", shn="both capture the pulling-off action; both lose 'nose' and the question.",
        p="question", a="question;general_semantic",
        ev="Nose grasp at 0.5-0.75 s directly shows 'nose'; both outputs lose it. Raised brows fit a yes/no question but "
           "are not verifiable from stills.",
        c="medium",
        amb="Brow raise vs. surprise affect.",
        fl="",
        rep="",
    ),
    "R28": dict(
        d="0-0.5 s index pointing at the back of the other hand; 0.75-1.25 s hand at the chest/face; 1.75-3.0 s both "
          "hands bent with fingers pointing down, held at waist height.",
        dc="medium",
        our="'the knees are going to be rounded' - lower-body vocabulary, wrong content.",
        off="'It's going to come out like this.' - generic.",
        sh="yes", shn="both lose boots / tied tight.",
        p="general_semantic", a="general_semantic;spatial_relation",
        ev="Downward bent hands at 1.75-3.0 s fit a lower-body/feet classifier; our 'knees' is partly consistent. "
           "Reference contains mojibake 'you?re' (already marked as a likely false-positive question).",
        c="low",
        amb="What the downward-hand classifier represents.",
        fl="gt_mojibake",
        rep="",
    ),
    "R29": dict(
        d="0 s hand at the nose; 0.25-1.25 s hands at rest on the knees (no signing); signing starts only at ~1.5 s.",
        dc="high",
        our="'do a couple of drills here' - generic.",
        off="'talk about what we're talking about right now' - generic.",
        sh="yes", shn="both lose the whole question.",
        p="question", a="question;spatial_relation;general_semantic",
        ev="At most ~0.5 s of signing in a 1.83 s clip; the reference question cannot fit. Strong sign of misalignment "
           "between the reference and this clip window.",
        c="medium",
        amb="",
        fl="mostly_idle_clip;reference_longer_than_visible_signing",
        rep="",
    ),
    "R30": dict(
        d="0-1.0 s two fists stacked as if gripping an object; 1.5-1.75 s two index fingers; 2.0 s two open hands; "
          "2.25-3.0 s flat hands together at the face/forehead moving down; 3.25-3.5 s palms up; 4.0-4.25 s fists.",
        dc="medium",
        our="'follow through as well as your overall' + 'overall' x30 - degenerate loop.",
        off="'It's also a great way to break down keeping your hair moving.' (chrF 40.6) - near-miss for 'parting'.",
        sh="no", shn="official mostly right; ours degenerate.",
        p="repetition", a="repetition;general_semantic",
        ev="No repeated visible sign sequence; our loop is decoder degeneration. Hands at the forehead moving down "
           "(2.25-3.0 s) fit 'parting'; official 'break down' is a near-miss.",
        c="medium",
        amb="",
        fl="",
        rep="Our output loops; official does not.",
    ),
    "R31": dict(
        d="0.5-1.25 s both spread hands raised; 2.0-2.5 s flat hands beside the face/eyes; 3.25-4.0 s fist near the "
          "nose/face; 4.5-4.75 s hands near the cheeks with pinched fingers.",
        dc="medium",
        our="'focus on that and then the interesting way to tell'.",
        off="'Once you've done that, you're going to focus on interesting ways of taking care of your cat.'",
        sh="partial", shn="both keep focus/interesting; both lose 'lighting'.",
        p="general_semantic", a="general_semantic",
        ev="Flat hands beside the eyes (2.0-2.5 s) fit FOCUS/CONCENTRATE - both outputs have 'focus'. Official 'cat' "
           "may come from the cheek-located pinched handshape at 4.5-4.75 s resembling CAT (speculative).",
        c="medium",
        amb="What is signed for 'lighting'.",
        fl="",
        rep="",
    ),
    "R32": dict(
        d="0.25-0.5 s index at the mouth; 0.75-1.25 s successive handshapes near the face with different numbers of "
          "fingers extended; 1.5 s two hands approaching each other.",
        dc="medium",
        our="'One, two, three, four.' - counting hallucination.",
        off="'Okay, while you see how I'm close.' (chrF 57) - loses the question mark and 'gap'.",
        sh="no", shn="official close; ours unrelated counting.",
        p="number", a="number;question;general_semantic",
        ev="Successive multi-finger handshapes at 0.75-1.25 s plausibly triggered our counting output; the closing "
           "hands at 1.5 s fit 'closing the gap'. The reference question is rhetorical.",
        c="medium",
        amb="",
        fl="",
        rep="",
    ),
    "R33": dict(
        d="0-1.25 s fist held at/rubbing the other wrist; 1.5-1.75 s hands low; 2.0-2.25 s index up; 2.5 s both index "
          "fingers; 2.75 s pointing.",
        dc="medium",
        our="'a lot of safety when you're shooting' - unrelated.",
        off="'For the purpose of a cartoon ... show you what happens' (chrF 35) - 'comedy'->'cartoon' near-miss.",
        sh="no", shn="official close; ours unrelated.",
        p="general_semantic", a="general_semantic",
        ev="Wrist-contact sign at 0-1.25 s might be confusable with SAFE (speculative).",
        c="low",
        amb="What 0-1.25 s is.",
        fl="",
        rep="",
    ),
    "R34": dict(
        d="0-0.5 s two open hands; 1.75-2.5 s index pointing at the mouth/teeth; 3.0-4.25 s hand at the chin/mouth "
          "with the index tracing around the mouth; 4.5-5.25 s hand at the mouth.",
        dc="high",
        our="'great way to do your lipstick ... lipstick brush'.",
        off="'fit your lips ... beautiful outline on each of those teeth' - keeps fit/beautiful/each/teeth.",
        sh="partial", shn="both fixate on mouth vocabulary; neither renders 'wraps around'.",
        p="spatial_relation", a="spatial_relation;general_semantic",
        ev="Sustained pointing/tracing at the mouth and teeth explains the mouth vocabulary in both; 'wraps around each "
           "tooth' is likely a tracing path (3.0-4.25 s) that neither output turns into 'around'. Our 'lipstick' is a "
           "location-driven confusion (lips vs teeth).",
        c="medium",
        amb="",
        fl="",
        rep="",
    ),
    "R35": dict(
        d="0-0.5 s two open hands, palms out; 1.0-5.0 s left flat palm held horizontally while the right hand rests on "
          "it and repeatedly rises and returns.",
        dc="medium",
        our="'squeeze down a little bit more' x2 - repetition.",
        off="'Hi, I'm Colin and I'm going to show you how to improve as you can.' (chrF 45) - 'Colin' for 'CarolAnn'.",
        sh="partial", shn="both lose 'Studio Group X' and 'push ups'.",
        p="name", a="name;fingerspelling;repetition;general_semantic",
        ev="No clear extended fingerspelling run in this window. The repeated up-down hand-on-palm movement (push-up "
           "depiction) plausibly underlies our repeated 'squeeze down'. 'Colin' shares the initial C with 'CarolAnn'.",
        c="low",
        amb="Whether 'CarolAnn' / 'Studio Group X' are spelled inside this window.",
        fl="",
        rep="Our output repeats ('repetition_loop' label) in step with a visibly repeated movement; official does not "
            "loop.",
    ),
    "R36": dict(
        d="Signing 0-13.25 s; 3.0-5.0 s hands forming ring/C shapes held in front; 7.5-10.0 s right hand near the "
          "chin/shoulder making successive handshapes (fingerspelling-like); 12.0-13.0 s O-shaped hand at the eye; "
          "13.5-15.75 s hands at rest (~2.3 s); 16.0-19.0 s successive single-hand handshapes near the chin/shoulder; "
          "19.25-20.5 s two-handed signing.",
        dc="medium",
        our="'a really nice drill ... really nice drill ... really good drill' - unrelated, repetitive.",
        off="'We're going to use a typical' + 'typical' x29 - single-token loop.",
        sh="yes", shn="both unrelated to the telescope/finder content; both repetitive.",
        p="repetition", a="repetition;fingerspelling;general_semantic",
        ev="Varied content (ring shapes, an O-hand at the eye like looking through an eyepiece, two fingerspelling-like "
           "runs); no repeated sign sequence.",
        c="medium",
        amb="What the fingerspelling-like runs spell (e.g. 'red dot', 'finder').",
        fl="official_window_differs_from_clip;idle_mid_13.5-15.75s",
        rep="OFFICIAL LOOP (rep3 0.818). Official input 32.54 s - the longest of the 9, far beyond the 256-frame cap "
            "and longer than this 20.78 s clip. A single-token degenerate loop, the clearest long-input case.",
    ),
    "R37": dict(
        d="0-2.75 s one hand held flat while the other moves along/across it; 3.0-3.75 s fingers interlocked/bent.",
        dc="medium",
        our="'load it up a little bit more' - unrelated.",
        off="'And that's how you do it.' - generic closing phrase (omission).",
        sh="yes", shn="both lose 'this part of my hand' and 'into center'.",
        p="spatial_relation", a="spatial_relation;general_semantic",
        ev="Hand moving across the held palm (0-2.75 s) is the spatial content (moving something to the centre); "
           "neither output encodes it.",
        c="medium",
        amb="",
        fl="",
        rep="",
    ),
    "R38": dict(
        d="0-2.0 s signing (hand at the mouth/chin); 2.25-6.0 s hands at rest (~3.75 s); 6.25-13.25 s signing (9.0 s "
          "index at the forehead/brow; 10.75-12.25 s successive single-hand handshapes near the chin); 13.5-14.0 s "
          "rest; 14.25-16.75 s single-hand handshapes near the chin.",
        dc="high",
        our="'very sensitive to color ... blacks ... non-colored, yellows' - keeps 'black'.",
        off="'main value of a snake ... a black sweater with some kind of fringe' - keeps 'main', 'black'.",
        sh="partial", shn="both keep 'black'; both lose 'referee', 'neon green or pink', the introduction.",
        p="general_semantic", a="general_semantic;fingerspelling",
        ev="Index at the forehead at 9.0 s fits BLACK (both outputs have 'black'). Single-hand runs near the chin may "
           "be spelled words (e.g. 'referee', 'neon') - unverified. ~4.3 s idle; the long reference likely exceeds "
           "this clip's signing.",
        c="low",
        amb="What the single-hand runs are.",
        fl="idle_mid_2.25-6.0s;reference_longer_than_visible_signing",
        rep="",
    ),
    "R39": dict(
        d="0-0.5 s a flat vertical hand resting on a horizontal palm; 0.75-1.0 s two fists; 1.5-2.25 s one fist held "
          "forward; 2.5 s hand at the nose; 3.0-4.5 s again a vertical index/flat hand held on a horizontal palm "
          "(~1.5 s); 5.0-5.75 s hands together.",
        dc="medium",
        our="'show you how to make this a little bit easier ... a little bit faster'.",
        off="'hit the ball with your index finger' x3.",
        sh="yes", shn="both lose uphill / downhill / flat / air speed.",
        p="repetition", a="repetition;spatial_relation;general_semantic",
        ev="The same hand-on-palm configuration appears twice (0-0.5 s, 3.0-4.5 s); 'with your index finger' may "
           "partly reflect the vertical index on the palm. Uphill/downhill/flat is probably depicted on the palm as a "
           "surface; neither output renders it.",
        c="low",
        amb="What the hand-on-palm configuration depicts.",
        fl="",
        rep="OFFICIAL LOOP (rep3 0.516). Official input 5.76 s ~ ours 5.88 s (medium): not a long-input or window "
            "issue. A repeated visible configuration may seed the repetition, but three repeats of a long clause go "
            "beyond what is visible.",
    ),
    "R40": dict(
        d="0-0.5 s vertical hand on a horizontal hand; 0.75-1.25 s two fists; 2.25-2.75 s raised index-up handshape(s); "
          "3.0-3.75 s fist held; 4.25-4.5 s hand at the head; 4.75-5.5 s hand pointing/moving downward.",
        dc="medium",
        our="'take my matching screw ... screw that in there' - number lost, repetition.",
        off="'So from here, one, two, three, and then down on your stomach.' (chrF 72).",
        sh="no", shn="official nearly right; ours unrelated.",
        p="number", a="number;repetition;general_semantic",
        ev="Counting-like index handshapes at 2.25-2.75 s and the downward movement at 4.75-5.5 s support the "
           "official's 'one, two, three ... down'.",
        c="medium",
        amb="Individual count handshapes are not all distinguishable at 4 fps.",
        fl="",
        rep="Our output loops ('repetition_loop' label); official does not.",
    ),
    "R41": dict(
        d="0-0.75 s thumb-up hand resting on a flat palm; 1.0-1.25 s index raised; 1.5-2.0 s hands crossing at the "
          "chest; 2.25 s fist at the chin; 2.5-3.25 s flat hands crossed on the chest.",
        dc="medium",
        our="'You're going to recycle these boats.' - unrelated.",
        off="'We always save these drawings and that's where they always come from.' (chrF 63).",
        sh="no", shn="official nearly right; ours unrelated.",
        p="general_semantic", a="general_semantic",
        ev="Raised index at 1.0-1.25 s is consistent with ALWAYS (circling not visible in stills); official has "
           "'always'.",
        c="low",
        amb="",
        fl="",
        rep="",
    ),
    "R42": dict(
        d="0.5 s both hands on top of the head; 0.75-1.25 s C-shaped hands at the cheeks; 1.5-2.5 s large two-handed "
          "movements across the face; 2.75 s V-shaped hands at the eyes; 3.0-3.5 s clawed hands at the chest; "
          "4.0-4.5 s hands crossing in front of the face; 5.0-5.75 s V-hands near the face.",
        dc="high",
        our="'keep her eyes on her ears ... on her face ... look at her face' - loop.",
        off="'There's a lot of that in literacy' x2 - loop.",
        sh="yes", shn="both fail and both repeat; reference about writing a drama screenplay.",
        p="repetition", a="repetition;general_semantic",
        ev="Much of the signing is at the head/face (hands on the head, at the cheeks, V at the eyes), which explains "
           "our output's eyes/ears/face vocabulary. Official 'literacy' is a near-miss for writing.",
        c="medium",
        amb="",
        fl="official_window_differs_from_clip",
        rep="OFFICIAL LOOP (rep3 0.308). Official input is 4.02 s - SHORTER than this 6.53 s clip - and still loops: "
            "the clearest evidence that official repetition is not a long-input failure.",
    ),
    "R43": dict(
        d="0-0.5 s hands at rest; 1.0 s palms up; 1.25 s index up; 1.5-1.75 s hands crossed with thumbs hooked; "
          "2.25-3.25 s fingers on the other palm; 3.5-4.25 s thumb-up handshapes.",
        dc="medium",
        our="'It's a nice way to start adding exercises.' - keeps 'nice way to start'.",
        off="'nice way to start getting up and practice ... yoga with a butterfly and take it out of your chest' - "
            "over-generation; keeps practice, yoga, butterfly.",
        sh="partial", shn="both keep 'nice way to start'; both lose 'prenatal' and 'breath flow'.",
        p="general_semantic", a="general_semantic",
        ev="Crossed hands with hooked thumbs at 1.5-1.75 s fit BUTTERFLY - official recovers it, ours does not.",
        c="medium",
        amb="",
        fl="",
        rep="",
    ),
    "R44": dict(
        d="0.75-2.0 s hands at rest; 3.75-4.25 s rest; 6.0-8.5 s hand at the eyebrow/forehead, open hand spread on the "
          "forehead 7.0-8.0 s; 12.0-14.5 s crossed hands held still (~2.5 s); 15.0-15.5 s index at the temple; 16.5 s "
          "index at the eye; 17.0-18.0 s both index/L hands at the sides of the face; 19.25-20.0 s circling hands.",
        dc="high",
        our="'help if the eye goes all the way around ... mascara ... help your eye look'.",
        off="'base of the color ... keep the eye on the top of the eye ... more coverage on the top of the eye ... make "
            "the eye look a lot more'.",
        sh="yes", shn="both fixate on 'eye'; both lose brow, seal, tame, frames the face, polished.",
        p="repetition", a="repetition;general_semantic",
        ev="Brow/eye-region signing recurs (6.0-8.5 s, 15-18 s), so the repeated 'top of the eye' is grounded in "
           "repeatedly visible locations, but 'brow' is mis-lexicalised as 'eye'. Index hands at the sides of the face "
           "(17.0-18.0 s) fit 'frames the face'.",
        c="medium",
        amb="",
        fl="idle_segments",
        rep="OFFICIAL LOOP (rep3 0.174). Mild phrase-level repetition tied to repeated eye-region locations; long input "
            "(23.39 s).",
    ),
    "R45": dict(
        d="0-0.25 s index raised at the face; 0.5 s hand moving downward (chop-like); 0.75-1.0 s both hands pointing "
          "down; 1.5-2.0 s hands at the face; 2.25-3.25 s fists at the chest.",
        dc="medium",
        our="'a black one here and that's a nice Easter throw' - unrelated.",
        off="'have your hands up down on the side of the boat' - keeps hand(s), down, side.",
        sh="no", shn="official partially aligned; ours unrelated.",
        p="spatial_relation", a="spatial_relation;general_semantic",
        ev="Downward chop at 0.5 s and downward-pointing hands at 0.75-1.0 s fit 'cuts down'; the step to the side is "
           "not identifiable.",
        c="low",
        amb="Which side / direction of stepping is shown.",
        fl="",
        rep="",
    ),
}

HUMAN = ["reviewer", "reviewer_asl_background", "reviewer_verified_category", "verified_label_source",
         "reviewer_comment", "review_status", "reviewed_at"]
COLS = (["review_id", "clip_id", "duration_s", "ground_truth", "prod_output", "prod_output_source", "unisign_output",
         "auto_error_type_prod", "auto_error_type_unisign", "initial_error_category", "initial_label_source",
         "initial_label_status", "official_repetition_loop_auto", "official_input_duration_s",
         "model_visible_description", "model_visible_description_confidence", "model_gt_vs_our_error",
         "model_gt_vs_official_error", "model_shared_failure", "model_shared_failure_note",
         "model_primary_error_category", "model_error_categories_all", "model_evidence", "model_confidence",
         "model_unresolved_ambiguity", "model_observation_flags", "model_repetition_analysis", "model_label_source",
         "model_label_status", "model_reviewer", "model_input"] + HUMAN)


def build_rows():
    sheet = list(csv.DictReader(open(SHEET / "inspection_sheet.csv", encoding="utf-8")))
    rep = {r["review_id"]: r for r in csv.DictReader(open(SHEET / "repetition_audit.csv", encoding="utf-8"))}
    assert len(sheet) == 45 and set(A) == {r["review_id"] for r in sheet}
    rows = []
    for r in sheet:
        a = A[r["review_id"]]
        assert a["p"] in CATEGORIES and all(x in CATEGORIES for x in a["a"].split(";"))
        assert a["p"] == a["a"].split(";")[0]
        assert all(r[h] == "" for h in HUMAN if h != "review_status") and r["review_status"] == "not_started"
        rows.append({
            **{k: r[k] for k in COLS if k in r},
            "official_repetition_loop_auto": "yes" if r["review_id"] in rep else "no",
            "official_input_duration_s": rep[r["review_id"]]["official_input_duration_s"] if r["review_id"] in rep else "",
            "model_visible_description": a["d"], "model_visible_description_confidence": a["dc"],
            "model_gt_vs_our_error": a["our"], "model_gt_vs_official_error": a["off"],
            "model_shared_failure": a["sh"], "model_shared_failure_note": a["shn"],
            "model_primary_error_category": a["p"], "model_error_categories_all": a["a"], "model_evidence": a["ev"],
            "model_confidence": a["c"], "model_unresolved_ambiguity": a["amb"], "model_observation_flags": a["fl"],
            "model_repetition_analysis": a["rep"], "model_label_source": "model_review",
            "model_label_status": "unverified", "model_reviewer": MODEL, "model_input": INPUT,
            **{h: r[h] for h in HUMAN},
        })
    assert not any(x["verified_label_source"] for x in rows)
    return rows


def write_html(rows, path):
    def esc(s):
        return html.escape(s or "")
    cards = []
    for x in rows:
        loop = '<span class="tag rep">official loop (auto)</span>' if x["official_repetition_loop_auto"] == "yes" else ""
        rep = (f'<p><b>Repetition:</b> {esc(x["model_repetition_analysis"])}</p>' if x["model_repetition_analysis"]
               else "")
        cards.append(f"""
<article class="card" data-cat="{esc(x['model_primary_error_category'])}" data-conf="{esc(x['model_confidence'])}" data-loop="{x['official_repetition_loop_auto']}">
  <h3>{esc(x['review_id'])} <span class="muted">{esc(x['clip_id'])} &middot; {esc(x['duration_s'])} s</span> {loop}</h3>
  <div class="grid">
    <video controls preload="none" src="../../10.18/asl-review-inspection-sheet/videos/{esc(x['clip_id'])}.mp4"></video>
    <dl class="texts">
      <dt>Ground truth</dt><dd>{esc(x['ground_truth'])}</dd>
      <dt>Our/old output <span class="muted">(provisional, B_ours_5p39)</span></dt><dd>{esc(x['prod_output'])}</dd>
      <dt>Official Uni-Sign output</dt><dd>{esc(x['unisign_output'])}</dd>
    </dl>
  </div>
  <section class="panel auto"><h4>AUTO weak label <span class="muted">automatic_weak / candidate_unverified</span></h4>
    <p>initial category <b>{esc(x['initial_error_category'])}</b> &middot; error type our {esc(x['auto_error_type_prod'])} / official {esc(x['auto_error_type_unisign'])}</p></section>
  <section class="panel model"><h4>MODEL review <span class="muted">model_review / unverified &middot; {esc(x['model_reviewer'])} &middot; confidence {esc(x['model_confidence'])}</span></h4>
    <p><b>Visible ({esc(x['model_visible_description_confidence'])}):</b> {esc(x['model_visible_description'])}</p>
    <p><b>GT vs our:</b> {esc(x['model_gt_vs_our_error'])}</p>
    <p><b>GT vs official:</b> {esc(x['model_gt_vs_official_error'])}</p>
    <p><b>Shared failure:</b> {esc(x['model_shared_failure'])} &mdash; {esc(x['model_shared_failure_note'])}</p>
    <p><b>Category:</b> {esc(x['model_primary_error_category'])} <span class="muted">({esc(x['model_error_categories_all'])})</span></p>
    <p><b>Evidence:</b> {esc(x['model_evidence'])}</p>
    {rep}<p><b>Unresolved:</b> {esc(x['model_unresolved_ambiguity']) or '&mdash;'}</p>
    <p class="muted">flags: {esc(x['model_observation_flags']) or '&mdash;'}</p></section>
  <section class="panel human"><h4>HUMAN verification <span class="muted">not started &middot; fill in inspection_sheet.html (10.18)</span></h4>
    <p>review_status <b>{esc(x['review_status'])}</b> &middot; verified category: {esc(x['reviewer_verified_category']) or '&mdash;'}</p></section>
</article>""")
    opts = "".join(f'<option value="{c}">{c}</option>' for c in CATEGORIES)
    path.write_text(f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>ASL Model Case Analysis</title>
<style>
:root {{
  --bg: #f7f7f5; --surface: #ffffff; --text: #1d1d1b; --muted: #6b6b66; --border: #dcdcd6;
  --auto: #8a6d1f; --auto-bg: #fbf4e0; --model: #5b3fb0; --model-bg: #efeafb; --human: #1f7a4d; --human-bg: #e4f4ea;
  --rep: #b3261e;
}}
@media (prefers-color-scheme: dark) {{
  :root:not([data-theme="light"]) {{
    --bg: #161615; --surface: #1f1f1d; --text: #ecece8; --muted: #a3a39c; --border: #3a3a36;
    --auto: #e3c46f; --auto-bg: #3a3220; --model: #c3b2ff; --model-bg: #2b2540; --human: #7fd3a6; --human-bg: #1d3528;
    --rep: #ff8a80;
  }}
}}
:root[data-theme="dark"] {{
  --bg: #161615; --surface: #1f1f1d; --text: #ecece8; --muted: #a3a39c; --border: #3a3a36;
  --auto: #e3c46f; --auto-bg: #3a3220; --model: #c3b2ff; --model-bg: #2b2540; --human: #7fd3a6; --human-bg: #1d3528;
  --rep: #ff8a80;
}}
* {{ box-sizing: border-box; }}
body {{ margin: 0; background: var(--bg); color: var(--text); font: 14px/1.5 system-ui, -apple-system, "Segoe UI", sans-serif; }}
header {{ position: sticky; top: 0; z-index: 5; background: var(--surface); border-bottom: 1px solid var(--border); padding: 10px 16px; }}
h1 {{ font-size: 17px; margin: 0 0 4px; }}
h3 {{ font-size: 15px; margin: 0 0 8px; }}
h4 {{ font-size: 13px; margin: 0 0 4px; }}
main {{ padding: 16px; max-width: 1200px; margin: 0 auto; }}
.muted {{ color: var(--muted); font-weight: normal; }}
.banner {{ background: var(--model-bg); color: var(--text); border-left: 4px solid var(--model); padding: 8px 12px; margin: 8px 0; }}
.card {{ background: var(--surface); border: 1px solid var(--border); border-radius: 8px; padding: 12px; margin: 0 0 16px; }}
.grid {{ display: grid; grid-template-columns: minmax(0, 360px) minmax(0, 1fr); gap: 12px; }}
@media (max-width: 720px) {{ .grid {{ grid-template-columns: minmax(0, 1fr); }} }}
video {{ width: 100%; background: #000; border-radius: 4px; }}
dl.texts {{ margin: 0; }} dl.texts dt {{ font-weight: 600; }} dl.texts dd {{ margin: 0 0 6px; }}
.panel {{ border-radius: 6px; padding: 8px 10px; margin-top: 8px; }}
.panel p {{ margin: 2px 0; }}
.auto {{ background: var(--auto-bg); border-left: 4px solid var(--auto); }}
.model {{ background: var(--model-bg); border-left: 4px solid var(--model); }}
.human {{ background: var(--human-bg); border-left: 4px solid var(--human); }}
.tag {{ font-size: 12px; border-radius: 4px; padding: 1px 6px; }}
.tag.rep {{ color: var(--rep); border: 1px solid var(--rep); }}
select, label {{ font: inherit; }}
.controls {{ display: flex; flex-wrap: wrap; gap: 12px; align-items: center; }}
</style>
</head>
<body>
<header>
  <h1>ASL model case analysis &middot; 45 clips</h1>
  <div class="controls">
    <label>Model category <select id="cat"><option value="">all</option>{opts}</select></label>
    <label>Confidence <select id="conf"><option value="">all</option><option>low</option><option>medium</option><option>high</option></select></label>
    <label><input type="checkbox" id="loop"> official repetition loops only (9)</label>
    <span id="count" class="muted"></span>
  </div>
</header>
<main>
  <div class="banner"><b>MODEL review is not human verification.</b> Purple panels are a model's frame-by-frame
  reading of 4 fps stills (no motion, no audio). Nothing here is <code>human_verified</code>; human fields are blank
  and live in the 10.18 inspection sheet. Yellow = existing automatic weak labels. Videos play from
  <code>../../10.18/asl-review-inspection-sheet/videos/</code> (local only).</div>
  {''.join(cards)}
</main>
<script>
const cat = document.getElementById('cat'), conf = document.getElementById('conf'), loop = document.getElementById('loop');
function apply() {{
  let n = 0;
  document.querySelectorAll('.card').forEach(c => {{
    const ok = (!cat.value || c.dataset.cat === cat.value) && (!conf.value || c.dataset.conf === conf.value)
      && (!loop.checked || c.dataset.loop === 'yes');
    c.hidden = !ok; if (ok) n++;
  }});
  document.getElementById('count').textContent = n + ' shown';
}}
[cat, conf, loop].forEach(e => e.addEventListener('change', apply));
apply();
</script>
</body>
</html>
""", encoding="utf-8")


def main():
    rows = build_rows()
    with open(HERE / "model_case_analysis.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=COLS, lineterminator="\n")
        w.writeheader()
        w.writerows(rows)
    write_html(rows, HERE / "model_case_analysis.html")
    counts = {}
    for x in rows:
        counts[x["model_primary_error_category"]] = counts.get(x["model_primary_error_category"], 0) + 1
    print(json.dumps({"rows": len(rows), "primary": counts,
                      "confidence": {c: sum(x["model_confidence"] == c for x in rows) for c in ("low", "medium", "high")},
                      "shared": {s: sum(x["model_shared_failure"] == s for x in rows) for s in ("yes", "partial", "no")}}))


if __name__ == "__main__":
    main()
