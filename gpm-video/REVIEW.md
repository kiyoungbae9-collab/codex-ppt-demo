# REVIEW — GPM × Ghana Chamber narrated presentation film

## Creative calls

- **Structure is the brief's, not a new storyline.** The 12 slides and the presenter script of
  `GPM Chamber Presentation v1.0` define the film; no alternative storylines were written. The
  person chose "read the whole script verbatim" over a 5-minute cut, so the film runs 9:16.
- **Voice is the clock.** Every reveal and highlight is keyed to the moment the narrator says the
  word that names it. Word times come from Kokoro's own phoneme durations (export
  `model-files-v1.1/kokoro-v1.0.onnx`), aligned to the script words with a small DP because espeak
  joins function words ("of the", "do not"). 0 of 94 sentences fell back to proportional timing.
- **One diagram that grows per slide**, never a finished slide dropped at once; the item being
  spoken turns teal and the others step back to 38% opacity, then everything returns on the
  slide's closing sentence.
- **Emphasis devices added from the narration, not new claims:** s01 "Not simply selling machines"
  struck through → "Sustainable manufacturing opportunities, together"; s02 example products as
  named; s05 the five operational needs; s08 "Technically functional ≠ Suitable…"; s07
  "CONCEPTUAL CATALOG — Not actual inventory" stamp; s06 decision-checkpoint badges on 04 and 05.
- **Brand master followed:** white ground, RAL 5018 (#008C91) only on rules, connectors and the
  active item; Inter throughout; logo area top-left (empty dashed square — the official green
  logo was not supplied and was not drawn); slide number small and centred at the bottom.
- **Speed:** Kokoro `am_michael` at 1.0 read at 124 wpm (9.9 min); raised to 1.12 (132 wpm while
  speaking) for a normal presentation pace that stays clear for non-native listeners.
- **1920×1080 (16:9)**, not the brief's 15:9 slide ratio: a video player target. The layout keeps
  all content inside the 80% title-safe box, so a 15:9 crop would lose nothing important.

## Measured vs looked at

- `hyperframes check`: lint 0 errors, runtime 0, layout 0, audio 0.
- Looked at: every scene at its completed state, every scene's start and middle, all 11 seams,
  and the phone-width sheet.
- Sound was **measured, not heard** (see below). Nobody has listened to the Kokoro read; proper
  nouns ("Ghanaian", "GPM", "Korea–Ghana") were checked only through the phonemizer output.

## Warnings kept on purpose

- `composition_file_too_large`, `timeline_track_too_dense` on `compositions/captions.html`: all
  218 caption groups live on one captions track, as the captions reference requires.
- `contrast_aa_failure` on two caption boxes and `text_below_floor` on three tags: each sample hit
  the 0.12 s caption fade or the 0.4 s tag spring (scale 0.86 → 1); at rest all pass.

## Weakest shot / with more time

- s11 (five infrastructure areas) is the most static: five cards and a tag row. With more time,
  give each card its own small diagram (cold-chain route, terminal, charger).
- Scene openings hold ~0.3 s of white before the title words arrive (blur swap). Acceptable for a
  formal deck film; a carry-across transition through the title would feel more continuous.
- No music bed: no licensed track or local music model was available here.
- The logo is a placeholder until the official file is supplied (see README).
