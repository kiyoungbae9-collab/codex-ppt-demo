#!/usr/bin/env python3
"""Synthesize the verbatim presenter script with Kokoro (male voice) and measure word timings.

Reads  script/narration.json
Writes assets/audio/narration.wav   one continuous voice track for the whole film
       script/timings.json          slide/sentence/word times (seconds) used by tools/build.py

Needs a Python with kokoro-onnx + soundfile, and the Kokoro ONNX export that reports phoneme
durations (release model-files-v1.1/kokoro-v1.0.onnx of thewh1teagle/kokoro-onnx). Paths:
  KOKORO_MODEL  (default ~/.cache/gpm-tts/kokoro-v1.0-timed.onnx)
  KOKORO_VOICES (default ~/.cache/gpm-tts/voices-v1.0.bin)
"""
import json
import os
import re
import subprocess
import sys
import tempfile

import numpy as np
import soundfile as sf
import kokoro_onnx

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MODEL = os.environ.get("KOKORO_MODEL", os.path.expanduser("~/.cache/gpm-tts/kokoro-v1.0-timed.onnx"))
VOICES = os.environ.get("KOKORO_VOICES", os.path.expanduser("~/.cache/gpm-tts/voices-v1.0.bin"))

SR = 24000
SENTENCE_GAP = 0.35      # silence added between sentences (s)
LEAD = {"s01": 2.4}      # silence before the first sentence of a slide (s)
DEFAULT_LEAD = 1.2
TAIL = {"s12": 4.0}      # silence after the last sentence of a slide (s)
DEFAULT_TAIL = 1.3


def split_sentences(text):
    return [s.strip() for s in re.split(r"(?<=[.?!])\s+", text.strip()) if s.strip()]


def tts_tokens(word):
    """Spoken form of one script word, as one or more tokens (dash-joined words are read apart)."""
    w = word.replace("’", "'").replace("‘", "'")
    w = w.replace("–", " ").replace("—", " ")
    w = re.sub(r"(?<=\w)-(?=\w)", " ", w)
    return w.split()


MARKS = set(",.;:!?—…\"'()ˈˌ ")


def phoneme_words(timings):
    """Phoneme timings grouped into space-separated phoneme words, marks removed."""
    groups, cur = [], []
    for t in timings:
        if t.phoneme == " ":
            if cur:
                groups.append(cur)
            cur = []
        elif t.phoneme not in MARKS:
            cur.append(t)
    if cur:
        groups.append(cur)
    return groups


_single_cache = {}


def single_len(model, token):
    """Phoneme count of one token spoken alone (stress and punctuation removed)."""
    if token not in _single_cache:
        ph = model.tokenizer.phonemize(token, "en-us")
        _single_cache[token] = max(1, sum(1 for c in ph if c not in MARKS))
    return _single_cache[token]


def align(model, tokens, groups):
    """Map tokens to phoneme words. espeak joins function words ("of the" -> one word), so a
    phoneme word may cover 1-3 tokens, and a token may span 1-2 phoneme words. Dynamic programming
    on phoneme counts; returns (start, end) per token."""
    n, m = len(tokens), len(groups)
    tl = [single_len(model, t) for t in tokens]
    gl = [len(g) for g in groups]
    INF = float("inf")
    dp = [[INF] * (m + 1) for _ in range(n + 1)]
    back = [[None] * (m + 1) for _ in range(n + 1)]
    dp[0][0] = 0
    for i in range(n + 1):
        for j in range(m + 1):
            if dp[i][j] == INF:
                continue
            for k in (1, 2, 3):  # k tokens -> 1 phoneme word
                if i + k <= n and j + 1 <= m:
                    c = dp[i][j] + abs(gl[j] - sum(tl[i:i + k])) + (k - 1) * 0.5
                    if c < dp[i + k][j + 1]:
                        dp[i + k][j + 1], back[i + k][j + 1] = c, (i, j, k, 1)
            if i + 1 <= n and j + 2 <= m:  # 1 token -> 2 phoneme words
                c = dp[i][j] + abs(gl[j] + gl[j + 1] - tl[i]) + 0.5
                if c < dp[i + 1][j + 2]:
                    dp[i + 1][j + 2], back[i + 1][j + 2] = c, (i, j, 1, 2)
    if dp[n][m] == INF:
        return None
    spans = [None] * n
    i, j = n, m
    while i > 0:
        pi, pj, k, g = back[i][j]
        phones = [t for grp in groups[pj:pj + g] for t in grp]
        if k == 1:
            spans[pi] = (phones[0].start, phones[-1].end)
        else:  # split the joined phoneme word by each token's share of phonemes
            total = sum(tl[pi:pi + k])
            acc = 0
            for q in range(k):
                a = int(round(acc / total * len(phones)))
                acc += tl[pi + q]
                b = max(a + 1, int(round(acc / total * len(phones))))
                b = min(b, len(phones))
                a = min(a, len(phones) - 1)
                spans[pi + q] = (phones[a].start, phones[b - 1].end)
        i, j = pi, pj
    return spans


def main():
    data = json.load(open(os.path.join(ROOT, "script/narration.json"), encoding="utf-8"))
    voice, speed = data["voice"], data["speed"]
    model = kokoro_onnx.Kokoro(MODEL, VOICES)
    if not model.has_timings:
        sys.exit("This Kokoro export reports no durations; use model-files-v1.1/kokoro-v1.0.onnx")

    chunks, slides_out, t_abs = [], [], 0.0
    warnings = 0
    for slide in data["slides"]:
        sid = slide["id"]
        lead = LEAD.get(sid, DEFAULT_LEAD)
        tail = TAIL.get(sid, DEFAULT_TAIL)
        t_local = lead
        chunks.append(np.zeros(int(round(lead * SR)), dtype=np.float32))
        sentences_out = []
        sents = split_sentences(slide["text"])
        for si, sentence in enumerate(sents):
            words = sentence.split()
            tokens, owner = [], []
            for wi, w in enumerate(words):
                for tok in tts_tokens(w):
                    tokens.append(tok)
                    owner.append(wi)
            audio, sr, timings = model.create_timed(" ".join(tokens), voice, speed, "en-us")
            assert sr == SR
            audio = np.asarray(audio, dtype=np.float32)
            groups = phoneme_words(timings)
            spans = align(model, tokens, groups) if groups else None
            dur = len(audio) / SR
            word_times = []
            if spans:
                per_word = {}
                for ti, (s, e) in enumerate(spans):
                    wi = owner[ti]
                    if wi in per_word:
                        per_word[wi] = (per_word[wi][0], e)
                    else:
                        per_word[wi] = (s, e)
                word_times = [per_word[wi] for wi in range(len(words))]
            else:
                warnings += 1
                print(f"  ! {sid} sentence {si}: alignment failed; proportional timing", file=sys.stderr)
                s0 = groups[0][0].start if groups else 0.1
                e0 = groups[-1][-1].end if groups else dur - 0.1
                weights = np.array([len(w) + 1.0 for w in words])
                edges = s0 + (e0 - s0) * np.concatenate([[0], np.cumsum(weights)]) / weights.sum()
                word_times = [(edges[i], edges[i + 1]) for i in range(len(words))]

            sentences_out.append({
                "text": sentence,
                "start": round(t_local + word_times[0][0], 3),
                "end": round(t_local + word_times[-1][1], 3),
                "words": [
                    {"text": w, "start": round(t_local + s, 3), "end": round(t_local + e, 3)}
                    for w, (s, e) in zip(words, word_times)
                ],
            })
            chunks.append(audio)
            t_local += dur
            if si < len(sents) - 1:
                chunks.append(np.zeros(int(round(SENTENCE_GAP * SR)), dtype=np.float32))
                t_local += SENTENCE_GAP
            print(f"  {sid}.{si}  {dur:5.2f}s  {sentence[:60]}")
        chunks.append(np.zeros(int(round(tail * SR)), dtype=np.float32))
        t_local += tail
        # Snap each slide to whole frames (30 fps) so scene seams land on frames.
        frames = int(np.ceil(t_local * 30))
        pad = frames / 30 - t_local
        if pad > 0:
            chunks.append(np.zeros(int(round(pad * SR)), dtype=np.float32))
        duration = frames / 30
        slides_out.append({
            "id": sid,
            "title": slide["title"],
            "start": round(t_abs, 4),
            "duration": round(duration, 4),
            "sentences": sentences_out,
        })
        t_abs += duration

    voice_track = np.concatenate(chunks)
    os.makedirs(os.path.join(ROOT, "assets/audio"), exist_ok=True)
    out_wav = os.path.join(ROOT, "assets/audio/narration.mp3")
    with tempfile.TemporaryDirectory() as tmp:
        raw = os.path.join(tmp, "raw.wav")
        sf.write(raw, voice_track, SR)
        # 48 kHz, loudness for speech: about -16 LUFS integrated, true peak under -1.5 dBTP.
        subprocess.run([
            "ffmpeg", "-y", "-loglevel", "error", "-i", raw,
            "-af", "loudnorm=I=-16:TP=-1.5:LRA=11,aresample=48000",
            "-ar", "48000", "-ac", "1", "-c:a", "libmp3lame", "-b:a", "192k", out_wav,
        ], check=True)
    total = len(voice_track) / SR
    json.dump({"fps": 30, "duration": round(t_abs, 4), "voice": voice, "speed": speed, "slides": slides_out},
              open(os.path.join(ROOT, "script/timings.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    nwords = sum(len(s["words"]) for sl in slides_out for s in sl["sentences"])
    speech = sum(s["end"] - s["start"] for sl in slides_out for s in sl["sentences"])
    print(f"total {total:.2f}s ({total/60:.2f} min), words {nwords}, {nwords / speech * 60:.0f} wpm while speaking, warnings {warnings}")


if __name__ == "__main__":
    main()
