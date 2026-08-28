# The Iron Pit — rules-first combat MVP

**The Iron Pit** is a server-resolved SRD 5.2.1 duel prototype: Aldric Vane, a level-1 Fighter, against the SRD Goblin Warrior.

## Current production boundary

- Python/FastAPI resolves live battles server-side.
- Production dice use the operating-system CSPRNG through Python `secrets`.
- The Netlify-ready frontend replays structured battle events.
- Static preview mode uses browser Web Crypto and mirrors supported demo rules.
- GitHub Actions gates Python tests, source-size limits, frontend syntax, preview behavior, Netlify configuration, and the Docker build.
- Production source modules are limited to 150 lines to keep the combat engine modular.

## Implemented rules

The current engine supports initiative, melee and ranged attacks, AC, natural 1/20 behavior, critical weapon dice, HP, healing, 0-HP arena defeat, movement, retreat movement, Dash, weapon ranges, close-ranged Disadvantage, Advantage/Disadvantage cancellation, Fighter Second Wind, Goblin conditional Advantage damage, Longsword Sap, and the reusable Vex mastery effect.

The Goblin Warrior also uses the **Disengage option** of Nimble Escape as a Bonus Action when trapped in melee, retreats, and can switch to its Shortbow. The Hide option of Nimble Escape is not implemented yet because the arena does not yet model visibility, concealment, or Stealth.

Weapon mastery data currently records:

- Longsword — Sap
- Scimitar — Nick
- Shortbow — Vex

A weapon having mastery metadata does **not** grant mastery to its wielder. Aldric currently masters Longsword. The SRD Goblin Warrior does not receive player weapon mastery features. Vex is implemented as reusable engine capability for a combatant that actually has Shortbow mastery; Nick remains unsupported until the engine has a canonical Light-property extra-attack model.

## Rules coverage API

`GET /api/rules/coverage` returns a machine-readable SRD 5.2.1 subset report. Every tracked rule is classified as:

- `implemented`
- `partial`
- `unsupported`
- `arena_assumption`

This endpoint is the source of truth for scope. It explicitly records incomplete areas such as Hide, Opportunity Attacks, conditions, cover, spells, death saves, and Nick instead of silently approximating them.

The arena currently uses Initiative bonus as a deterministic tie-breaker and models combat as one-dimensional distance in an open arena. Both are reported as arena assumptions.

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

Open `http://localhost:8080` and choose a starting distance.

### Docker API

```bash
docker compose up --build
```

## Deployment

### Render API

The repository contains `render.yaml` using `backend/Dockerfile`.

1. Create a Render Blueprint from `cbw29512/github-D20`.
2. Deploy the default `render.yaml` Blueprint.
3. Copy the public API URL.
4. Confirm `GET /health` returns `{"status":"ok"}`.
5. Confirm `GET /api/rules/coverage` returns the current rules contract.

The free Render tier can spin down after inactivity. That is acceptable for the prototype but should be upgraded before meaningful production traffic.

### Netlify frontend

`netlify.toml` publishes `frontend/` and generates browser configuration during the build.

1. Import the GitHub repository in Netlify.
2. Keep `main` as the production branch.
3. Set `IRON_PIT_API_BASE` to the deployed Render API URL for live-server mode.
4. Deploy and run both the 5-foot and 90-foot fights.

If `IRON_PIT_API_BASE` is blank, the site intentionally runs the secure browser preview rather than silently pointing to localhost.

## Security boundary

- No application secrets are stored in the repository.
- `.env` files are ignored; `.env.example` documents browser/API configuration.
- The demo battle endpoint is public and unauthenticated.
- Authentication, saved accounts, rankings, and payments are deliberately outside this combat-engine slice.
- CORS and API authorization must be tightened before account-backed features are introduced.

## Next rules milestones

1. Add canonical reactions and Opportunity Attacks so Disengage prevention is fully exercised.
2. Add visibility/concealment and Hide before enabling the Hide option of Nimble Escape.
3. Add a proper Light-property extra-attack model before implementing Nick.
4. Surface the machine-readable rules coverage report in the arena UI.
5. Run a final deployed Render + Netlify end-to-end release gate before merging the combat milestone to `main`.
