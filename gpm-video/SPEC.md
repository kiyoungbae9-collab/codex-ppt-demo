# SPEC — GPM × Ghana Chamber of Commerce, narrated presentation film

GOAL:    A Ghanaian business owner ends the film asking "could GPM and a Korean partner help with *my*
         manufacturing project?" and wants a follow-up meeting (P.04, P.09, P.10, P.12 carry it).
OUTPUT:  HyperFrames, 1920 x 1080, 30 fps, MP4. 12 scenes = the 12 slides of the v1.0 brief.
TIME:    Voice is the clock. Verbatim English script (script/narration.json, 1,062 words), Kokoro
         `am_michael` at speed 1.12 (~132 wpm), 555.93 s = 9:16 = 16,678 frames at 30 fps.
         Each scene = 1.2 s lead (s01: 2.4 s) + its sentences (0.35 s gaps) + 1.3 s tail (s12: 4 s),
         snapped to whole frames. No music bed (no licensed source on this machine).

LOOK:    Swiss corporate editorial, from the brief's design master.
         ground #FFFFFF flat, no texture, no gradient, no shadow.
         ink #1C2528 (charcoal) for every word that must be read; secondary ink #4A5759; quiet #7A898C.
         accent RAL 5018 Türkisblau, screen #008C91: title rule, connector lines, arrows, the ONE active item.
         dark teal #005B62: headings inside diagrams, the GPM hub fill. light teal #E4F2F1: active-card fill.
         hairlines #D3DDDE 2 px; card radius 10 px; card border 2 px #D3DDDE, active 3 px #008C91.
         Type: Inter only (bundled 400/700/900).
           brand line 20 px / 700 / +0.14em caps;  slide title 60 px / 700 / -0.02em;
           headline 34 px / 400 / dark teal;  card heading 30 px / 700;  body 28 px / 400 (floor 28 px);
           captions 40 px / 400 white on charcoal box rgba(28,37,40,0.88), radius 8, padding 10x22.
         Layout grid: title-safe x 192..1728, y 108..972. Header y 56..112 (logo area 56 px square at
         x 120 + brand line). Title top y 150, teal rule 96x6 under it. Content y 280..860.
         Captions bottom edge y 960, one line only. Slide number 22 px #7A898C centred at y ~1000.
OBJECTS: Logo = reserved empty area (dashed 2 px #9FB3B5 square) until the official green GPM logo
         file is supplied; never drawn or invented. Machines, factories, documents = Lucide line icons
         (ISC), 2 px stroke, teal on light-teal tiles. No photos, no invented equipment data.
MOTION:  enter  = blur 8->0 px + opacity in 0.45 s `expo.out` (no translate) for text;
                  lines/arrows draw with scaleX 0->1 in 0.6 s `power2.inOut`;
                  cards open with clip-path inset 0 100% 0 0 -> 0 in 0.5 s `power3.out`;
                  tags/ticks land scale 0.86->1 in 0.4 s `back.out(1.5)` (damping ~0.7, never on opacity).
         focus  = the item the voice names goes active (border+fill teal, 0.3 s `power2.inOut`);
                  others drop to 0.38 opacity; all return to 1 on the scene's closing sentence.
         title  = per-word blur-in 0.13 s, 0.067 s apart; then dead still.
         exit   = whole scene blur 0->8 px + opacity->0, 0.3 s `power3.in`, ending 1 frame before cut.
         Every reveal lands on the word that names it (word times from Kokoro phoneme durations).
SHOTS:   s01 title; Korea and Ghana nodes fill with their three assets as named, GPM links them,
             "sell machines" struck through -> "manufacturing opportunities together".
         s02 question lands; example products appear as named; Equipment / Local Demand /
             Technical Capability arrive; lines converge to POTENTIAL MANUFACTURING PROJECT.
         s03 KOREA box fills, GHANA box fills, GPM hub + arrows, four service functions in sequence.
         s04 2x2 cards, one per "First/Second/Third/Fourth"; hygiene shows 3 separate categories;
             pharma gets a verification flag; all return on the closing question.
         s05 Equipment alone, then four needs, then Engineering, Training, Operation join on one line.
         s06 seven stages light in order; Feasibility and Contracting outlined as decision checkpoints.
         s07 conceptual record: photo + price only -> four structured fields fill; bottom flow draws;
             CONCEPTUAL stamp lands on "conceptual model".
         s08 "functional is not suitable" line; six review areas fill as named; Permits flagged for
             pharma; evidence line lands.
         s09 Korean column, Ghanaian column, GPM centre + two-way arrows, Chambers band, disclaimer.
         s10 One Product / One Local Partner / One Feasibility Review light with steps 1-5;
             Start small / Verify carefully / Scale when ready.
         s11 five cards in turn, relevance tags, "not completed installations" note.
         s12 checklist ticks 1-2-3, logo area + website, "Thank You" holds 3 s.
         Sound: voice; a soft whoosh (two takes, rotated) on each scene change; a soft pop on
             checkpoint and stamp landings only. All SFX at 0.18-0.25 volume under the voice.
BANNED:  dark or navy ground; glow, gradients, glass, particles; bullet-slide lists dropped at once;
         every element fading and sliding up; titles moving after they land; breathing/pulsing loops;
         invented numbers, prices, capacities, ROI, certifications, partners, contracts or MOUs;
         one machine shown making all three hygiene products; a drawn or AI-made GPM logo; Korean text.
QA:      t = each scene at +2 s (title read), at its middle (diagram half-built), and 1 s before its
         end (diagram complete, nothing clipped); captions never overlap content; slide number visible.
