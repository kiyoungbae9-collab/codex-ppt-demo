# GPM × Ghana Chamber of Commerce — 내레이션 발표 영상 (HyperFrames)

`GPM Chamber Presentation v1.0` 기획안의 12개 장표와 **영어 발표 대본 전문**을 남성 음성(Kokoro `am_michael`)으로 낭독하는 1920×1080, 30fps 영상입니다. 각 항목은 내레이션이 그 단어를 말하는 순간에 나타나거나 청록색(RAL 5018, #008C91)으로 강조됩니다.

- 길이: **9분 16초** (대본 1,062단어, 분당 약 132단어)
- 자막: 영어(낭독 문장과 동일), 한 번에 한 줄
- 로고: 공식 녹색 GPM 로고 자리만 비워 둠(점선 사각형). 로고를 새로 그리거나 생성하지 않음
- 효과음: 장면 전환 시 약한 whoosh, 체크포인트·도장·체크 표시에 pop(Pixabay 라이선스, `assets/sfx/CREDITS.md`). 배경음악 없음

## 폴더 구조

| 경로 | 내용 |
| --- | --- |
| `script/narration.json` | 대본 원문(장표별). **대본 수정은 여기서** |
| `script/timings.json` | 문장·단어별 발화 시각(자동 생성) |
| `src/scenes/s01.html` … `s12.html` | 장면 템플릿. `{{at:단어}}`가 그 단어의 발화 시각으로 치환됨 |
| `src/chrome.html` | 모든 장면 위에 고정되는 머리글(로고 자리 + GLOBAL PARTNER MARKET) |
| `tools/build_narration.py` | Kokoro TTS 생성 + 단어 타이밍 측정 → `assets/audio/narration.mp3` |
| `tools/build.py` | 템플릿 + 타이밍 → `compositions/*.html`, `index.html` |
| `compositions/`, `index.html` | 빌드 결과(HyperFrames가 렌더링하는 파일) |
| `SPEC.md`, `REVIEW.md` | 디자인 기준, 검수 기록 |

## 공식 로고 넣기

1. 로고 파일(투명 배경 PNG 또는 SVG)을 `assets/brand/`에 넣습니다. 예: `assets/brand/gpm-logo.png`
2. `src/chrome.html`(머리글)과 `src/scenes/s12.html`(마지막 장면)의 `src="assets/brand/logo-slot.svg"`를 로고 파일 경로로 바꿉니다.
3. `python3 tools/build.py` 실행 후 다시 렌더링합니다.

## 다시 만들기

```bash
# 1) 대본을 바꿨을 때만: 음성·타이밍 재생성 (kokoro-onnx, soundfile 필요)
#    모델: thewh1teagle/kokoro-onnx 릴리스 model-files-v1.1/kokoro-v1.0.onnx (음소 길이를 출력하는 버전)
KOKORO_MODEL=~/.cache/gpm-tts/kokoro-v1.0-timed.onnx KOKORO_VOICES=~/.cache/gpm-tts/voices-v1.0.bin \
  python3 tools/build_narration.py

# 2) 장면·자막·index.html 빌드
python3 tools/build.py

# 3) 점검, 미리보기, 렌더링 (HyperFrames CLI)
npx hyperframes check
npx hyperframes preview
npx hyperframes render -o renders/GPM_Korea-Ghana_Partnership_EN.mp4 --crf 20
```

`compositions/`와 `index.html`은 빌드할 때마다 덮어쓰므로, 수정은 `src/`와 `script/`에서 하세요.

## 사실관계 원칙(기획안 기준)

미확인 설비 가격·생산량·ROI·계약·MOU는 넣지 않았습니다. 위생용품은 기저귀(유아/성인)·생리대를 별도 품목으로 표시했고, 장비 카탈로그 화면에는 "Conceptual Catalog — Not actual inventory" 표시를 넣었습니다.
