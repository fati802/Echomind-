# EchoMind

**An AI-powered visual memory assistant for dementia patients and forgetful everyday moments.**

EchoMind watches a room through a camera, detects everyday objects (glasses, medicine box,
keys, remote, mug), and converts what it sees into structured events — never raw video. You
can then ask plain-language questions like *"Where are my glasses?"* or *"Did I take my
medicine today?"* and get an answer grounded strictly in what was actually observed.

Built for the **AMD Developer Hackathon Act II — Unicorn Track**.

---

## What it does

- **Detects objects** in uploaded video using a custom fine-tuned YOLOv8 model (trained on
  glasses, medicine box, keys, remote, and mug — not just generic COCO classes).
- **Extracts structured events** (`placed`, `picked_up`, `handed_over`, `observed`) with
  timestamp, zone/location, actor, and confidence — discarding the raw video afterward.
- **Answers questions conversationally**, grounded only in logged events via an AMD-hosted
  LLM. If there's no matching event, it says so honestly instead of guessing.
- **Surfaces a timeline** of the day's events, grouped and readable.
- **Raises alerts** when an object has been picked up and not returned within a
  per-object time threshold (e.g. medicine: 60 minutes) — useful for catching a missed
  medication or a misplaced item before it becomes a problem.

## Project structure

```
EchoMind/
├── backend/          # FastAPI app — routes, models, retrieval, LLM integration
│   └── models/         # best.pt — the trained YOLO weights the backend loads
├── frontend/         # Next.js + Tailwind chat, timeline, and upload UI
├── perception/       # Object detection pipeline: training data, labeling tools,
│                      # fine-tuning scripts, and event-extraction logic
├── docs/              # Ground-truth Q&A set, reference docs
└── docker-compose.yml
```

## Tech stack

| Layer | Technology |
|---|---|
| Frontend | Next.js + Tailwind CSS (deployed on Vercel) |
| Backend | FastAPI + Uvicorn (deployed on Render) |
| Object detection | Custom fine-tuned YOLOv8 (Ultralytics) |
| Reasoning / Q&A | AMD Developer Cloud LLM, with Fireworks AI and a rule-based responder as cascading fallbacks |
| Storage | SQLite |

## API endpoints

| Endpoint | Method | Purpose |
|---|---|---|
| `/api/health` | GET | Liveness check |
| `/api/upload-video` | POST | Upload a video — runs detection, extracts events, saves them |
| `/api/events` | GET | List logged events, filterable by date/object/actor |
| `/api/timeline` | GET | Day summary grouped into morning/afternoon/evening |
| `/api/query` (alias `/api/ask`) | POST | Ask a natural-language question, get a grounded answer + referenced events |
| `/api/alerts` | GET | Objects picked up and not returned past their time threshold |
| `/api/llm-status` | GET | Shows which LLM provider is currently active (amd / fireworks / mock) |

## Quick start

### Prerequisites
- Python 3.10+
- Node.js 18+

### Backend

```bash
cd backend
python -m venv venv
# Windows:
.\venv\Scripts\Activate.ps1
# macOS/Linux:
source venv/bin/activate

pip install -r requirements.txt
cp .env.example .env   # fill in your own keys — see note below
uvicorn main:app --reload
```

Backend runs at `http://localhost:8000`.

> **Note:** the trained object-detection model is expected at `backend/models/best.pt`.
> It's already committed in this repo. If it's ever missing, detection silently falls
> back to a generic untrained YOLOv8 model, which won't reliably recognize the 5 tracked
> objects.

### Frontend

```bash
cd frontend
npm install
npm run dev
```

Frontend runs at `http://localhost:3000`.

### Environment variables (backend `.env`)

```
DATABASE_URL=sqlite:///./data/echomind.db
LLM_PROVIDER=amd                  # amd | fireworks | mock
AMD_DEV_CLOUD_API_URL=...
AMD_DEV_CLOUD_API_KEY=...
AMD_DEV_CLOUD_MODEL=...           # e.g. meta-llama/Meta-Llama-3-8B-Instruct
FIREWORKS_API_KEY=...             # used only if AMD is unreachable
```

If no keys are configured, `LLM_PROVIDER=mock` runs a rule-based responder instead of a
hosted LLM — useful for local testing without any API keys.

## The perception pipeline

The `perception/` folder contains everything used to train and run the object detector
independently of the backend:

- `scripts/label_server.py` + `scripts/labeler.html` — a small local browser-based tool
  for drawing bounding boxes and exporting YOLO-format labels (no third-party account
  needed).
- `scripts/prepare_dataset.py` — builds a train/val split and `data.yaml` from labeled
  images.
- `scripts/train_model.py` — fine-tunes YOLOv8n, automatically resuming from the most
  recent previous round's weights if one exists.
- `scripts/zone_timeline.py` — a manually authored mapping of scene timestamps to
  real-world zones and actions, since the camera follows the action rather than staying
  fixed on one wide shot.
- `scripts/extract_events.py` — runs the trained model across scene frames, cross-checks
  detections against the zone timeline, collapses repeated frame hits into discrete
  events, and posts them to `/api/ingest`.

To retrain on new footage or photos: drop files into `perception/data/raw_footage/`,
extract frames, label them via the browser tool, then run `prepare_dataset.py` followed
by `train_model.py`.

## Privacy principles

- Raw video is never persisted — processed transiently, then discarded.
- Only structured event metadata (object, zone, timestamp, identity tag) is retained.
- Face/identity recognition, where used, is scoped to a small registered set only;
  unregistered people get a generic "unknown person" label.
- No biometric data leaves the local processing environment.

## Known limitations

- Zone-level location accuracy, not exact spatial coordinates.
- Detection is trained on a small custom dataset — best accuracy on the specific objects
  and rooms it was trained on, not a general-purpose object detector.
- Designed around uploaded video clips, not a continuous live camera feed.
