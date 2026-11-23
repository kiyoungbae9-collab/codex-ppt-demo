#!/usr/bin/env python3
"""Build the HyperFrames project from the scene templates and the measured narration timings.

  src/scenes/sNN.html   scene templates (one per slide) with timing tokens
  src/chrome.html       persistent header (logo area + brand line)
  script/timings.json   from tools/build_narration.py
->
  compositions/sNN.html, compositions/chrome.html, compositions/captions.html, index.html

Tokens inside templates (times are seconds from the scene start):
  {{at:phrase}}          start of the first spoken occurrence of `phrase` in this slide
  {{at:phrase#2}}        second occurrence;  {{at:phrase+0.3}} / {{at:phrase-0.2}} offsets
  {{end:phrase}}         end of the phrase's last word
  {{S:n}} / {{SE:n}}     start / end of sentence n (1-based)
  {{DUR}} {{EXIT}}       scene duration / start of the scene's exit (DUR - 0.36)
  {{TITLE}}              slide title as per-word spans
  {{PAGE}}               two-digit slide number
  {{icon:name}}          inline Lucide icon (tools/icons/name.svg)
  {{BASE_CSS}} {{HELPERS}}
"""
import html
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
W, H, FPS = 1920, 1080, 30


def rel(*p):
    return os.path.join(ROOT, *p)


def read(*p):
    with open(rel(*p), encoding="utf-8") as f:
        return f.read()


def write(path, text):
    os.makedirs(os.path.dirname(rel(path)), exist_ok=True)
    with open(rel(path), "w", encoding="utf-8") as f:
        f.write(text)


def norm(w):
    w = w.lower().replace("’", "'")
    return re.sub(r"[^a-z0-9]", "", w)


TIMINGS = json.load(open(rel("script/timings.json"), encoding="utf-8"))
BASE_CSS = read("tools/partials/base.css")
HELPERS = read("tools/partials/helpers.js")


def icon(name):
    svg = read("tools/icons", f"{name}.svg")
    svg = re.sub(r"<!--.*?-->", "", svg, flags=re.S).strip()
    svg = re.sub(r'\s*class="[^"]*"', "", svg)
    svg = re.sub(r'\s*width="24"\s*height="24"', "", svg)
    svg = svg.replace("<svg", '<svg class="ic" aria-hidden="true"', 1)
    return re.sub(r"\s*\n\s*", " ", svg)


class Slide:
    def __init__(self, data):
        self.id = data["id"]
        self.data = data
        self.words = []
        for s in data["sentences"]:
            for w in s["words"]:
                self.words.append((norm(w["text"]), w["start"], w["end"]))
        self.dur = data["duration"]

    def find(self, phrase, occurrence=1):
        toks = [norm(t) for t in phrase.split()]
        toks = [t for t in toks if t]
        n = len(toks)
        seen = 0
        for i in range(len(self.words) - n + 1):
            if all(self.words[i + k][0] == toks[k] for k in range(n)):
                seen += 1
                if seen == occurrence:
                    return self.words[i][1], self.words[i + n - 1][2]
        sys.exit(f"[{self.id}] phrase not spoken: {phrase!r} (#{occurrence})")


TOKEN = re.compile(r"\{\{(at|end):\s*(.+?)(?:#(\d+))?\s*(?:([+-])\s*(\d+(?:\.\d+)?))?\}\}")


def render_template(text, slide, number):
    def timing(m):
        kind, phrase, occ, sign, off = m.groups()
        s, e = slide.find(phrase.strip(), int(occ or 1))
        t = s if kind == "at" else e
        if off:
            t += float(off) * (1 if sign == "+" else -1)
        t = max(0.0, min(t, slide.dur - 0.05))
        return f"{t:.3f}"

    text = text.replace("{{BASE_CSS}}", BASE_CSS).replace("{{HELPERS}}", HELPERS)
    text = TOKEN.sub(timing, text)
    sents = slide.data["sentences"]
    text = re.sub(r"\{\{S:(\d+)\}\}", lambda m: f"{sents[int(m.group(1)) - 1]['start']:.3f}", text)
    text = re.sub(r"\{\{SE:(\d+)\}\}", lambda m: f"{sents[int(m.group(1)) - 1]['end']:.3f}", text)
    text = text.replace("{{DUR}}", f"{slide.dur:.3f}").replace("{{EXIT}}", f"{slide.dur - 0.36:.3f}")
    title_words = slide.data["title"].split()
    spans = " ".join(f'<span class="w">{html.escape(w)}</span>' for w in title_words)
    text = text.replace("{{TITLE}}", spans).replace("{{PAGE}}", f"{number:02d}")
    text = re.sub(r"\{\{icon:([a-z0-9-]+)\}\}", lambda m: icon(m.group(1)), text)
    text = text.replace("{{ID}}", slide.id)
    left = re.findall(r"\{\{[^}]*\}\}", text)
    if left:
        sys.exit(f"[{slide.id}] unresolved tokens: {left[:5]}")
    return text


# ---------------------------------------------------------------- captions
def caption_groups(slide, offset):
    """Calm reading groups: 3-6 words, broken at punctuation and pauses, never across sentences."""
    groups = []
    for s in slide.data["sentences"]:
        words = s["words"]
        cur = []
        for i, w in enumerate(words):
            cur.append(w)
            last = i == len(words) - 1
            nxt = words[i + 1] if not last else None
            rest = len(words) - i - 1
            punct = w["text"][-1] in ",;:"
            pause = nxt is not None and nxt["start"] - w["end"] >= 0.18
            if last:
                groups.append(cur)
                cur = []
            elif len(cur) >= 6 and rest >= 2:
                groups.append(cur)
                cur = []
            elif (punct or pause) and len(cur) >= 3 and rest >= 2:
                groups.append(cur)
                cur = []
        if cur:
            groups.append(cur)
    out = []
    for g in groups:
        out.append({
            "text": " ".join(w["text"] for w in g),
            "start": offset + g[0]["start"],
            "end": offset + g[-1]["end"],
        })
    return out


def build_captions(slides):
    groups = []
    for sl in slides:
        groups += caption_groups(sl, sl.data["start"])
    # Open slightly before the first word; stay until the next group opens if the gap is short.
    for i, g in enumerate(groups):
        g["open"] = max(g["start"] - 0.08, groups[i - 1]["close"] if i else 0.1)
        nxt = groups[i + 1]["start"] - 0.08 if i + 1 < len(groups) else None
        close = g["end"] + 0.35
        if nxt is not None and nxt - g["end"] < 0.9:
            close = nxt
        if nxt is not None:
            close = min(close, nxt)
        g["close"] = close
    items, tweens = [], []
    for i, g in enumerate(groups):
        cid = f"cg{i + 1:03d}"
        start = round(g["open"], 3)
        dur = round(g["close"] - g["open"], 3)
        items.append(
            f'    <div id="{cid}" class="cg clip" data-start="{start}" data-duration="{dur}">'
            f'<span class="cbox" id="{cid}-t">{html.escape(g["text"])}</span></div>'
        )
        tweens.append(
            f'  tl.fromTo("#{cid}-t", {{ opacity: 0 }}, {{ opacity: 1, duration: 0.12, ease: "power2.out" }}, {start});\n'
            f'  tl.to("#{cid}-t", {{ opacity: 0, duration: 0.1, ease: "power2.in" }}, {round(start + dur - 0.1, 3)});'
        )
    total = TIMINGS["duration"]
    return f"""<template>
  <style>
    #root {{ position: absolute; inset: 0; pointer-events: none; font-family: "Inter", sans-serif; }}
    .cg {{ position: absolute; left: 0; right: 0; bottom: 120px; text-align: center; overflow: visible; }}
    .cbox {{
      display: inline-block; white-space: nowrap; font-size: 40px; line-height: 1.25; font-weight: 400;
      color: #ffffff; background: rgba(28, 37, 40, 0.88); padding: 10px 22px; border-radius: 8px;
    }}
  </style>
  <div id="root" data-composition-id="captions" data-width="{W}" data-height="{H}" data-duration="{total}">
{chr(10).join(items)}
  </div>
  <script>
  const tl = gsap.timeline({{ paused: true }});
{chr(10).join(tweens)}
  window.__timelines["captions"] = tl;
  </script>
</template>
""", len(groups)


# ---------------------------------------------------------------- sound
SFX = [
    # (slide, phrase or None for the scene change, file, volume)
    ("s06", "They are checkpoints", "pop.mp3", 0.22),
    ("s07", "is a conceptual model", "pop.mp3", 0.22),
    ("s12", "hear about your product", "pop.mp3", 0.18),
    ("s12", "your business plans", "pop.mp3", 0.18),
    ("s12", "a preliminary discussion", "pop.mp3", 0.18),
]


def main():
    slides = [Slide(s) for s in TIMINGS["slides"]]
    total = TIMINGS["duration"]
    hosts = []
    for n, sl in enumerate(slides, 1):
        src = rel("src/scenes", f"{sl.id}.html")
        if not os.path.exists(src):
            print(f"  (no template for {sl.id}, skipped)")
            continue
        write(f"compositions/{sl.id}.html", render_template(read("src/scenes", f"{sl.id}.html"), sl, n))
        hosts.append(
            f'      <div id="{sl.id}" data-composition-id="{sl.id}" data-composition-src="compositions/{sl.id}.html"\n'
            f'        data-start="{sl.data["start"]:.4f}" data-duration="{sl.dur:.4f}" data-track-index="1"\n'
            f'        data-track-kind="graphics" data-label="{n:02d} {html.escape(sl.data["title"])}"\n'
            f'        data-width="{W}" data-height="{H}" style="z-index: 1"></div>'
        )
    write("compositions/chrome.html", read("src/chrome.html").replace("{{BASE_CSS}}", BASE_CSS))
    captions, ncap = build_captions(slides)
    write("compositions/captions.html", captions)

    # Scene-change whooshes (two takes, alternating) peak on the cut; pops on stamp/tick landings.
    sfx = []
    for n, sl in enumerate(slides[1:], 2):
        f = "whoosh-short.mp3" if n % 2 == 0 else "whoosh.mp3"
        sfx.append((sl.data["start"] - 0.22, f, 0.16))
    by_id = {sl.id: sl for sl in slides}
    for sid, phrase, f, vol in SFX:
        sl = by_id[sid]
        sfx.append((sl.data["start"] + sl.find(phrase)[0] + 0.03, f, vol))
    sfx.sort()
    durs = {"whoosh-short.mp3": 0.57, "whoosh.mp3": 0.57, "pop.mp3": 0.72}
    sfx_tags = []
    for i, (t, f, vol) in enumerate(sfx, 1):
        sfx_tags.append(
            f'      <audio id="sfx{i:02d}" class="clip" src="assets/sfx/{f}" data-start="{t:.3f}" '
            f'data-duration="{durs[f]}" data-track-index="5" data-volume="{vol}"></audio>'
        )

    index = f"""<!doctype html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width={W}, height={H}" />
    <title>GPM — Korea–Ghana Industrial Partnership</title>
    <script src="assets/vendor/gsap.min.js"></script>
    <style>
      * {{ margin: 0; padding: 0; box-sizing: border-box; }}
      html, body {{ margin: 0; width: {W}px; height: {H}px; overflow: hidden; background: #ffffff; }}
      #root {{ position: relative; width: {W}px; height: {H}px; overflow: hidden; font-family: "Inter", sans-serif; }}
      #ground {{ position: absolute; inset: 0; background: #ffffff; }}
    </style>
  </head>
  <body>
    <!-- Generated by tools/build.py from src/ and script/timings.json. Edit the sources, then rebuild. -->
    <div id="root" data-composition-id="main" data-start="0" data-duration="{total:.4f}" data-width="{W}" data-height="{H}">
      <div id="ground"></div>
{chr(10).join(hosts)}
      <div id="chrome" data-composition-id="chrome" data-composition-src="compositions/chrome.html"
        data-start="0" data-duration="{total:.4f}" data-track-index="2" data-track-kind="graphics"
        data-label="Header: logo area + brand" data-width="{W}" data-height="{H}" style="z-index: 2"></div>
      <div id="captions" data-composition-id="captions" data-composition-src="compositions/captions.html"
        data-start="0" data-duration="{total:.4f}" data-track-index="3" data-track-kind="captions"
        data-label="English captions" data-width="{W}" data-height="{H}" style="z-index: 3"></div>
      <audio id="narration" class="clip" src="assets/audio/narration.mp3" data-start="0"
        data-duration="{total:.4f}" data-track-index="4" data-volume="1"></audio>
{chr(10).join(sfx_tags)}
    </div>
    <script>
      window.__timelines = window.__timelines || {{}};
      window.__timelines["main"] = gsap.timeline({{ paused: true }});
    </script>
  </body>
</html>
"""
    write("index.html", index)
    print(f"built {len(hosts)} scenes, {ncap} caption groups, {len(sfx)} sfx, {total:.2f}s")


if __name__ == "__main__":
    main()
