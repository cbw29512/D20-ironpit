# The Iron Pit

A rules-first D&D 2024 / SRD 5.2.1 card-v-card combat simulator.

## Current production architecture

- **GitHub `main`** — source of truth and CI-certified releases.
- **GitHub Pages** — production test mirror published automatically from a successful `main` CI run.
- **Netlify (`ironpit`)** — production static frontend; non-production deploys are intentionally skipped to conserve credits.
- **Render (`iron-pit-d20-api`)** — Dockerized FastAPI combat API.

The browser defaults to `https://iron-pit-d20-api.onrender.com`. Netlify may override that URL with `IRON_PIT_API_BASE` during its production build.

## Arena policy

Iron Pit intentionally simplifies battlefield movement while preserving combat-changing rules:

- fights continue until one side is defeated;
- no fleeing, surrender, kiting, or retreat AI;
- melee-primary cards close and stay engaged;
- a melee-primary card with a ranged option gets one opening ranged attack while closing;
- a melee-only card Dodges while using normal movement to close;
- ranged-primary cards do not kite;
- 2+ active allies satisfy Iron Pit's ally-within-5-feet arena assumption;
- unsupported defining mechanics fail closed instead of being approximated silently.

See `docs/ARENA_POLICY.md` for the exact contract.

## Content coverage

The catalog contains:

- **720 hero build slots** — three builds for each of 12 core classes at levels 1–20;
- **328 SRD 5.2.1 monsters**.

Catalog presence is not the same as automated RAW readiness. A card becomes selectable for a public fight only after its legal build/stat block and all combat-relevant mechanics clear certification.

## Development

### API

```bash
cd backend
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\\Scripts\\activate
pip install -e '.[dev]'
pytest -q
uvicorn app.main:app --reload
```

### Frontend

```bash
python -m http.server 8080 --directory frontend
```

Open `http://localhost:8080`.

## Release gates

Every production candidate must pass:

- production Python/JavaScript source limits and syntax checks;
- full backend test suite;
- deterministic frontend API configuration checks;
- Netlify production-only credit guard;
- GitHub Pages publishing guard;
- Docker image build.

Render is configured with `autoDeployTrigger: checksPass`, so backend production updates wait for linked CI success.
