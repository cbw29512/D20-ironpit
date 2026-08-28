# The Iron Pit — MVP

A rules-first fantasy duel prototype: **Aldric Vane, Level 1 Fighter vs. the SRD 5.2.1 Goblin Warrior**.

## Locked MVP

- Python/FastAPI combat engine runs server-side.
- OS-backed secure random dice (`secrets`) determine rolls.
- Natural 1 misses; natural 20 hits and doubles weapon damage dice.
- Fighter and monster HP, initiative, attack rolls, damage, victory, and battle events are recorded.
- Static Netlify-ready frontend replays the server event log as stick-figure combat.
- GitHub Actions tests the backend and deployment artifacts.
- Docker packages the API.

## Rules coverage in this first slice

Implemented: initiative modifiers; melee and ranged weapon attacks; normal/long range validation; ranged attacks while an enemy is within 5 feet; movement and Dash; natural 1/20 attack behavior; critical weapon dice; HP and 0 HP defeat; reusable weapon/attack records; Fighter Second Wind; Advantage/Disadvantage roll resolution; Goblin conditional bonus damage when an attack actually has Advantage; and Longsword Sap with its next-attack and start-of-next-turn timing.

Weapon mastery data is recorded for Longsword (Sap), Scimitar (Nick), and Shortbow (Vex). **Only Sap is executed by the combat engine today**; Nick and Vex remain data-only until their own rules and regression tests land.

Not implemented yet: Goblin Nimble Escape, Nick, Vex, general Hide/Disengage behavior, reactions, conditions, spells, death saves, cover, opportunity attacks, and a broader rules-coverage report.

Initiative ties currently use initiative bonus as an arena tiebreaker. This is an explicit arena assumption and will be surfaced in the future rules-coverage report.

## Run locally

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

In a second terminal:

```bash
python -m http.server 8080 --directory frontend
```

Open `http://localhost:8080` and click **Enter the Pit**.

### Docker API

```bash
docker compose up --build
```

## Deployment

### 1. Deploy the FastAPI backend on Render

The repository contains `render.yaml` for a free prototype web service using `backend/Dockerfile`.

1. In Render, choose **New > Blueprint**.
2. Connect `cbw29512/github-D20`.
3. Use the default `render.yaml` Blueprint path and deploy it.
4. Copy the resulting public `https://...onrender.com` API URL.
5. Confirm `GET /health` returns `{"status":"ok"}`.

The free Render instance can spin down after inactivity, so the first battle after an idle period may take longer while the service wakes up. This is acceptable for the MVP and should be upgraded before production traffic.

### 2. Deploy the frontend on Netlify

`netlify.toml` publishes `frontend/` and generates `frontend/config.js` during the Netlify build.

1. In Netlify, import the existing GitHub repository `cbw29512/github-D20`.
2. Keep `main` as the production branch; Netlify reads `netlify.toml` automatically.
3. Add a site environment variable named `IRON_PIT_API_BASE` with the Render API URL from step 1.
4. Trigger the production deploy.
5. Open the Netlify site and click **Enter the Pit**.

The build intentionally fails if `IRON_PIT_API_BASE` is missing or is not an `http://` or `https://` URL. This prevents a deployment that silently points users at localhost.

### 3. Security boundary for the MVP

- No secrets are stored in the repository.
- `.env` files are ignored; `.env.example` documents expected values.
- The current demo battle endpoint is public and unauthenticated.
- Render currently allows all CORS origins for this public MVP endpoint.
- Before Supabase login, saved accounts, rankings, or payments are added, CORS and API authorization must be tightened.

## Architecture direction

- **GitHub:** source of truth + CI.
- **Netlify:** static web frontend.
- **Render:** Dockerized FastAPI combat API for the prototype.
- **Supabase:** Auth/Postgres after the combat slice is stable.

## Next milestone

1. Implement Goblin Nimble Escape and reusable Disengage/Hide action-state rules.
2. Implement Vex on top of the generic temporary attack-roll effect system.
3. Implement Nick only after the engine has a canonical Light-property/extra-attack action model.
4. Surface rule-feature events such as Sap clearly in the frontend replay and battle log.
5. Add an explicit machine-readable rules-coverage report so implemented, assumed, and unsupported mechanics are never ambiguous.
