# Devyn — Tech Trend Research

Type a tech topic (e.g. "Android + AI"). Devyn researches what's trending right now
across the web, Hacker News, and GitHub, then returns trends, what to learn, and a
3–4 week learning plan. Every claim links to a real retrieved source.

## How it works

Single-pass pipeline: `plan → search → synthesize → validate`

1. **plan** — LLM generates 4–6 search queries (news, tools, discussion, learning).
2. **search** — Tavily web + HN Algolia + GitHub Search APIs save `Item` rows. Network only, no LLM.
3. **synthesize** — LLM cites items by numeric ID only (never URLs). Pydantic-validated, one retry.
4. **validate** — strips citations not in the DB, drops emptied entries, adds `meta`.

## Local setup

Requirements: Python 3.12, Node 18+, API keys (DeepSeek + Tavily; GitHub token optional).

```bash
cp .env.example backend/.env   # fill in keys (or export env vars)
```

### Backend

```bash
cd backend
python3.12 -m venv .venv && .venv/bin/pip install -r requirements.txt
.venv/bin/python manage.py migrate
.venv/bin/python manage.py runserver
```

### Worker (separate terminal)

```bash
cd backend
.venv/bin/python manage.py qcluster
```

### Frontend

```bash
cd frontend
cp .env.example .env   # VITE_API_BASE_URL=http://localhost:8000
npm install && npm run dev
```

Open http://localhost:5173, enter a topic, and watch the run page poll to `done`.

## Debug command

Runs the full pipeline synchronously and prints the validated report:

```bash
cd backend && .venv/bin/python manage.py research_debug "Android + AI"
```

## Tests

```bash
cd backend && .venv/bin/python -m pytest research/tests/ -q
```

- `test_validate.py` — unknown IDs stripped, empty entries dropped, roadmap weeks kept, `dropped_citations` correct.
- `test_pipeline.py` — recorded fixture + mocked `llm.json_call`, no network; `synthesize → validate` yields a valid `Report`.
- `test_api.py` — POST validation (400 on empty/too-long topic), GET 404.

## API

- `POST /api/runs` `{"topic": "..."}` → `201 {"id", "status"}`
- `GET /api/runs/{id}` → run + `report` + `sources` (only cited items, keyed by ID string)

## Config

See `.env.example`. Secrets stay server-side; the frontend only gets `VITE_API_BASE_URL`.
`DATABASE_URL` (postgres) switches off SQLite; otherwise SQLite is used.
