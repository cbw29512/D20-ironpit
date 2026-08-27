# The Iron Pit — MVP

A rules-first fantasy duel prototype: **Aldric Vane, Level 1 Fighter vs. the SRD 5.2.1 Goblin Warrior**.

## Locked MVP

- Python/FastAPI combat engine runs server-side.
- OS-backed secure random dice (`secrets`) determine rolls.
- Natural 1 misses; natural 20 hits and doubles weapon damage dice.
- Fighter and monster HP, initiative, attack rolls, damage, victory, and battle events are recorded.
- Static Netlify-ready frontend replays the server event log as stick-figure sword attacks.
- GitHub Actions runs the backend tests.
- Docker packages the API.

## Rules coverage in this first slice

Implemented: initiative modifiers, melee attack vs. AC, natural 1/20 attack behavior, critical weapon dice, HP, 0 HP defeat.

Not implemented yet: Fighter Second Wind, Weapon Mastery (including Longsword Sap), Goblin Nimble Escape, advantage/disadvantage bonus damage, movement/range, reactions, conditions, spells, death saves, cover, opportunity attacks.

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

## Deployment direction

- **GitHub:** source of truth + CI.
- **Netlify:** deploy `frontend/` via `netlify.toml`.
- **FastAPI:** deploy `backend/` as a Docker service on a container host.
- **Supabase:** add Auth/Postgres after the combat slice is stable.

For the deployed frontend, set `window.IRON_PIT_API_BASE` in `frontend/config.js` to the public FastAPI URL and allow the Netlify origin in `ALLOWED_ORIGINS`.

## Next milestone

1. Verify this battle end-to-end.
2. Add weapon/armor data as reusable content records.
3. Implement advantage/disadvantage and Goblin Warrior's conditional bonus damage.
4. Implement Fighter Second Wind and Longsword Sap.
5. Add ranged projectile event + shortbow animation.
