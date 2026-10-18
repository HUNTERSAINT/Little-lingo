# LittleLingo

LittleLingo is a small English-practice companion for children under seven. It uses Python and FastAPI for the API, with plain HTML, CSS and JavaScript in the browser.

## Design choice

This version uses a deterministic dialogue engine rather than sending every message to an external language model. Lesson content is curated, routing is inspectable, and the API has no external model dependency. The trade-off is that phrase matching is limited and cannot understand every way a child might express an idea.

## Features

- Three stages: early vocabulary, word/phrase practice, and short sentences.
- Four modes: learning, conversation, engagement, and support.
- Hints and breaks that do not count as incorrect answers.
- Encouraging responses and curated lesson prompts.
- Browser-session progress; no transcript database.
- Health endpoint and behavior-focused API tests.

## Run locally

Python 3.10+ recommended.

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Open http://127.0.0.1:8000. Health check: http://127.0.0.1:8000/health.

Run tests: `pip install pytest httpx` then `python -m pytest -q`.

## Deploy to Render

Push this folder to GitHub, create a Render Web Service from the repository, and use:

- Build command: `pip install -r requirements.txt`
- Start command: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
- Health check path: `/health`

`render.yaml` is included for Blueprint deployment.

## Deploy to Railway

The included `Dockerfile` runs the FastAPI app on Railway's assigned `PORT`, and
`railway.json` configures `/health` as the deployment health check.

Install and authenticate the Railway CLI, then run from this directory:

```bash
railway up --new --name LittleLingo --yes
railway domain
```

For automated deploys, supply `RAILWAY_API_TOKEN` through a secure environment
secret. Do not commit the token or put it in application code.

## Notes

See `docs/ARCHITECTURE.md`, `docs/SYSTEM_DESIGN.md`, and `docs/VIDEO_SCRIPT.md`. This is a prototype, not a safeguarding service. Mood and safety handling use a small set of phrases and can miss indirect wording. Adult supervision is recommended. A production version needs specialist review, broader child-language testing, accessibility checks, caregiver controls, and a privacy assessment.
