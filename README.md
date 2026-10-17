# TruVision

**Real-time Indian Sign Language (ISL) accessibility for Google Meet**

TruVision is a Chrome Extension that enables bidirectional communication between ISL users and hearing participants during Google Meet sessions — translating sign gestures to voice and transcribing speech to captions, in real time.

---

## Repository Structure

```
TruVision 1.0/
├── extension/          # Chrome Extension (Vite + React + TypeScript + Tailwind)
│   ├── src/
│   │   ├── background/         # MV3 Service Worker + WebSocket Recovery Manager
│   │   ├── content-script/     # Meet DOM Adapter + Overlay Injection
│   │   ├── offscreen/          # Audio Playback + Tab Capture (Web Audio API)
│   │   └── popup/              # Extension Popup UI (React)
│   └── public/
│       └── manifest.json       # MV3 manifest
│
├── backend/            # FastAPI Backend (Python 3.11+)
│   ├── app/
│   │   ├── api/                # REST + WebSocket routes
│   │   ├── services/           # TTS, Sign, Speech, Auth, Correction services
│   │   ├── core/               # Phrase cache + shared utilities
│   │   └── models/             # Pydantic schemas + DB model references
│   ├── ml/
│   │   ├── sign_model/weights/ # LSTM model weights (not committed)
│   │   └── data/               # Dataset download scripts
│   ├── tests/                  # pytest test suite
│   ├── run.py                  # Dev server entry point
│   └── pyproject.toml          # uv/hatch project config
│
└── .github/
    └── workflows/ci.yml        # GitHub Actions CI
```

---

## Quick Start

### Extension (Development)

```bash
cd extension
npm install
npm run dev       # Start Vite dev server for popup preview
npm run build     # Build all extension bundles (popup + content + background)
npm run typecheck # TypeScript check
npm run lint      # ESLint
npm run format    # Prettier
```

**Load in Chrome:**
1. Run `npm run build`
2. Open `chrome://extensions` → Enable Developer Mode
3. Click **Load unpacked** → select `extension/dist/`

---

### Backend (Development)

Requires Python 3.11+ and [uv](https://docs.astral.sh/uv/).

```bash
cd backend

# Install uv (if not already)
pip install uv

# Create venv and install core dependencies
uv venv
uv pip install -e "."            # core only
uv pip install -e ".[ai,db]"     # include AI + Supabase

# Copy and configure environment
cp .env.example .env
# Edit .env and fill in API keys

# Start server
uv run python run.py
# → http://localhost:8000
# → Swagger UI: http://localhost:8000/docs
```

---

## Environment Variables

Copy `backend/.env.example` → `backend/.env` and fill in:

| Variable | Description |
|---|---|
| `GEMINI_API_KEY` | Gemini Flash for sentence correction |
| `GOOGLE_TTS_KEY` | Google Cloud TTS for voice synthesis |
| `SUPABASE_URL` | Supabase project URL |
| `SUPABASE_SERVICE_KEY` | Supabase service role key |
| `JWT_SECRET` | Secret for JWT session validation |

> ⚠️ Never commit `.env`. Only `.env.example` is tracked.

---

## Tech Stack

| Layer | Technology |
|---|---|
| Extension | Chrome MV3, Vite 8, React 19, TypeScript 6, Tailwind CSS v4 |
| Background | Service Worker, WebSocketRecoveryManager, chrome.alarms |
| Gesture Detection | MediaPipe Holistic WASM (Phase 3) |
| Backend | FastAPI, uvicorn, WebSockets |
| ML Model | TensorFlow 2 / Keras LSTM (INCLUDE dataset) |
| Transcription | faster-whisper (base model) |
| Sentence Correction | Local phrase cache + Gemini 1.5 Flash |
| TTS | Google Cloud Text-to-Speech |
| Auth / DB | Supabase (PostgreSQL + Auth) |

---

## Development Checklist

- [x] Extension boots and popup renders
- [x] Tailwind CSS working
- [x] TypeScript strict mode enabled
- [x] ESLint + Prettier configured
- [x] Background service worker initializes
- [x] Content script injects overlay on meet.google.com
- [x] WebSocket Recovery Manager wired
- [x] Meet DOM Adapter wired
- [x] Backend FastAPI server starts
- [x] `/health` endpoint returns 200
- [x] CI pipeline (lint + typecheck + build) configured
- [ ] LSTM model trained and loaded (Phase 3)
- [ ] MediaPipe WASM integrated (Phase 3)
- [ ] Supabase auth wired (Phase 3)
