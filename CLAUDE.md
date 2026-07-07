# EchoMind — Project Reference

AI-powered visual memory assistant for dementia patients. Built for AMD Developer 
Hackathon Act II — Unicorn Track. Submission deadline: July 11, 2026, 15:00 UTC.

## What it does
EchoMind observes a patient's environment via pre-recorded footage, detects objects 
and people, converts detections into structured events (never raw video), and answers 
natural-language questions strictly grounded in those logged events via retrieval-
augmented generation (RAG). No hallucinated answers — if no matching event exists, 
the system says so explicitly.

## Team roles
- **Person A** — AI & Computer Vision Engineer: owns object detection (YOLOv8), face 
  recognition (opt-in), event extraction/de-duplication logic, demo footage, AMD 
  Developer Cloud CV workload integration.
- **Person B** — Backend, Frontend & AI Integration Engineer: owns FastAPI backend, 
  event log database, retrieval engine, Fireworks AI LLM integration, Next.js chat 
  frontend, Docker/deployment, final demo + pitch deck.
- Shared: event schema definition, daily standups, demo rehearsal, submission materials.

## Tech stack
- Frontend: Next.js + Tailwind CSS
- Backend: FastAPI + Uvicorn (Python)
- CV/ML: YOLOv8 (Ultralytics), OpenCV, open-source face recognition library
- LLM: Fireworks AI hosted inference (optionally AMD Developer Cloud acceleration), 
  Gemma model for bonus challenge
- Database: SQLite (MVP) — event log
- Deployment: Docker + Docker Compose, Vercel (frontend), Render or AMD Developer 
  Cloud (backend)
- Version control: Git/GitHub

## Database schema (DECISION: using flat single-table version)
We are using the simple flat schema, NOT the normalized multi-table version, for 
speed within the 5-day build:

```
events(
  id            INTEGER PRIMARY KEY,
  object        TEXT NOT NULL,       -- glasses, medicine box, keys, remote, mug
  action        TEXT NOT NULL,       -- placed, picked_up, handed_over, observed
  actor         TEXT NULLABLE,       -- patient, caregiver, or null if unidentified
  zone          TEXT NULLABLE,       -- kitchen shelf, dining table, study table
  timestamp     DATETIME NOT NULL,
  confidence    FLOAT NOT NULL,
  source_frame  TEXT NULLABLE        -- frame reference/path
)
```

Note: the original full proposal also described a normalized version (separate 
patients/people/objects/zones tables with foreign keys into events) — that version 
was NOT used for the hackathon build to save time, but is documented here in case 
we reference it for the "future scope" / production roadmap discussion in the pitch.

## API endpoints (FastAPI)
- `GET /api/health` — liveness check
- `GET /api/events` — filtered list of event records (by date, object, person)
- `GET /api/timeline` — day summary grouped into morning/afternoon/evening
- `POST /api/query` (aka /ask) — accepts a natural-language question, returns a 
  grounded answer + referenced event records
- `POST /api/ingest` — internal endpoint used by the CV pipeline to write new 
  structured events into the database (not exposed to frontend)

## Grounding rules for the LLM layer
- Answer only from retrieved event records — never from general knowledge.
- If no relevant event is found, respond: "I don't have a record of that yet" — 
  never guess or fabricate.
- Keep tone warm, plain-language, reassuring — appropriate for a patient who may 
  find technical phrasing confusing.
- Never produce anything resembling medical advice or diagnosis.

## Repo structure
```
echomind/
├── backend/          # FastAPI app, routers/, services/, models/
├── frontend/          # Next.js + Tailwind chat UI
├── vision/            # Person A's CV pipeline (YOLOv8, face recognition, event extraction)
├── demo-video/         # Pre-recorded footage (gitignored)
├── data/               # SQLite db file (gitignored)
├── docs/               # Proposal, architecture diagrams, pitch deck
├── tests/              # Unit + integration tests
├── docker-compose.yml
├── .env.example
└── README.md
```

## 5-Day roadmap
- **Day 1**: Person A — record footage, baseline YOLOv8 detection. Person B — FastAPI 
  + Next.js scaffolds, repo structure, schema decision.
- **Day 2**: Person A — event extractor producing structured events. Person B — event 
  log DB + /api/ingest + /api/events endpoints working against real data.
- **Day 3**: Person A — face recognition + identity tagging integrated into events. 
  Person B — retrieval engine + Fireworks AI /api/query working end-to-end.
- **Day 4**: Person A — full pipeline validation + AMD Developer Cloud setup. Person B 
  — Next.js chat UI wired to backend, Docker containerization of all services.
- **Day 5**: Person A — polish detection accuracy, finalize AMD integration. Person B 
  — deploy (Vercel + Render), record demo video, build pitch deck, rehearse, submit 
  before July 11, 15:00 UTC.

## Demo plan (4 scenes, under 5 minutes total)
1. Silent event logging — patient places glasses + medicine, logged automatically.
2. Caregiver hand-off — caregiver hands medicine to patient, identity-tagged hand-off 
   event logged.
3. Live Q&A — judge types questions live: "Where are my glasses?", "Who gave me the 
   medicine?", "Did I take my medicine today?" — answered live with referenced events 
   shown on request.
4. Closing — privacy-by-architecture explanation, known limitations (zone-level not 
   exact-coordinate accuracy, pre-recorded not live video, small face set), future 
   roadmap.

## Privacy principles (non-negotiable, mention in pitch)
- Raw video is never persisted — processed transiently, discarded after detection.
- Only structured event metadata (object, zone, timestamp, identity tag) is retained.
- Face recognition is opt-in, scoped to a small registered set only; unregistered 
  people get a generic "unknown person" label, never identified.
- No biometric data ever leaves the local processing environment or reaches a 
  third party.

## Submission checklist
- Working end-to-end prototype (object memory, face recognition, event logging, 
  Q&A chat).
- Demo video covering all 4 scenes.
- Docker Compose stack verified to build clean on a fresh machine.
- Full proposal doc, README with quick-start, pitch deck, architecture diagrams in docs/.
- Submitted on lablab.ai team page before July 11, 2026, 15:00 UTC. Both team members 
  registered individually. GitHub repo accessible to judges with correct branch flagged.

## Key risks to watch
- LLM giving vague/ungrounded answers → mitigated by strict retrieval-grounded prompting.
- Frontend/backend integration breaking near demo → integrate against real data from 
  Day 2, not mocks.
- Hosted LLM latency/rate limits during judging → cache common queries, have a backup 
  recorded clip.
- Deployment misconfiguration (env vars, CORS) → full deployed dry run at least a day 
  before submission.
