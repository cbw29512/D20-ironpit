# The Iron Pit — rules-first combat MVP

**The Iron Pit** is a server-resolved SRD 5.2.1 combat prototype built around auditable character-vs.-monster rules slices.

## Current production boundary

- Python/FastAPI resolves live battles server-side.
- Production dice use the operating-system CSPRNG through Python `secrets`.
- The Netlify-ready frontend replays structured battle events.
- Static preview mode uses browser Web Crypto and mirrors supported demo rules.
- GitHub Actions gates Python tests, source-size limits, rules-contract synchronization, frontend syntax, preview behavior, Netlify configuration, and Docker.
- Production Python and JavaScript modules are limited to 150 lines.

## Implemented rules

The engine supports initiative, Surprise, pre-combat Hide, melee/ranged attacks, natural 1/20 behavior, critical damage dice, HP/healing/arena defeat, movement, Dash, ranges, Advantage/Disadvantage cancellation, Second Wind, Opportunity Attacks, Disengage, Sap, Vex, Light extra attacks, Two-Weapon Fighting, Nick, and the solo/Advantage route of Rogue Sneak Attack.

### Pre-combat stealth and Surprise

A scenario may let a creature attempt **Hide before combat** when the battlefield actually provides valid concealment and removes enemy line of sight. A successful pre-combat Hide does not spend the creature's first combat Action or Bonus Action. While Invisible from hiding, it has Advantage on Initiative; an explicitly unaware ambush target has Surprise and therefore Disadvantage on Initiative. Failed Hide does not grant Surprise.

The Hide/Invisible implementation remains deliberately partial: attack-roll reveal and Search discovery are implemented, but loud-noise and Verbal-spell reveal triggers await sound/spell systems, and Invisible's broader seen-target restrictions await generalized effect targeting.

### Rogue ambush demo

**Mara Vale** is an original level-1 Rogue combat slice built from SRD 5.2.1 combat rules rather than an official stat block. The demo uses leather armor, a Shortsword, a Shortbow, two weapon masteries, Stealth Expertise (+7), and 1d6 Sneak Attack.

The Rogue ambush scenario starts 60 feet away with valid concealment and an unaware Goblin Warrior. Mara still has to pass the normal Hide check. On success, the battle sequence is rules-driven: pre-combat Hide → Initiative Advantage / Surprise Disadvantage → hidden Shortbow attack with Advantage → eligible Sneak Attack → reveal after the attack roll.

Sneak Attack currently implements the solo Advantage route, Finesse/Ranged weapon gating, weapon-matching damage type, critical-dice doubling, and **once per turn rather than once per round** timing. The per-turn state resets when any creature's new turn begins, so a qualifying Opportunity Attack on another creature's turn can Sneak Attack again. The alternate ally-within-5-feet route remains partial until the engine has ally-position context.

### Light weapons and Nick

A Light-weapon Attack-action attack can enable one extra attack with a different configured Light weapon. Normally the extra attack spends the Bonus Action and omits a positive ability modifier from damage. Negative modifiers and other damage bonuses remain. Two-Weapon Fighting restores the ability modifier. Nick moves that same one-per-turn Light attack into the Attack action for a mastered Nick weapon; it does not create a third attack.

### Goblin tactics

The SRD Goblin Warrior can use either option of Nimble Escape. In melee it prioritizes Disengage, retreats without provoking, and can switch to its Shortbow. At range, valid concealment can allow Bonus Action Hide. The open arena never fabricates concealment.

## Rules coverage API

`GET /api/rules/coverage` is the source of truth for scope. Each tracked rule is `implemented`, `partial`, `unsupported`, or `arena_assumption`. `frontend/rules-coverage.json` must match the FastAPI contract exactly, and CI fails on drift.

Current deliberate gaps include the ally-position route of Sneak Attack, the complete general condition framework, full Cover AC/Dexterity-save and line-of-effect behavior, spells, death saving throws, and Reaction features beyond Opportunity Attacks.

## Demo battle endpoints

- `POST /api/battles/demo` — Aldric Vane vs. Goblin Warrior at 5 ft.
- `POST /api/battles/demo-ranged` — Aldric Vane vs. Goblin Warrior at 90 ft.
- `POST /api/battles/demo-rogue-ambush` — Mara Vale attempts a concealed pre-combat ambush from 60 ft.

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

```bash
python -m http.server 8080 --directory frontend
```

### Docker API

```bash
docker compose up --build
```

## Deployment

The API uses `render.yaml` and `backend/Dockerfile`. The frontend uses `netlify.toml`. Production Netlify should set `IRON_PIT_API_BASE` to the Render API URL; a blank value intentionally selects secure browser-preview mode instead of silently targeting localhost.

## Security boundary

- No application secrets are stored in the repository.
- `.env` files are ignored.
- Demo battle endpoints are public and unauthenticated.
- Authentication, accounts, rankings, and payments are outside the current combat-engine slice.
- CORS/API authorization must be tightened before account-backed features.

## Next rules milestones

1. Complete the full SRD 5.2.1 audit of every rule currently claimed by the coverage API and attach explicit source sections to those claims.
2. Add the ally-position route of Sneak Attack when multi-creature battlefield context exists.
3. Add Rogue Cunning Action at level 2 using the existing Dash/Disengage/Hide paths.
4. Add full Cover AC/Dexterity-save bonuses and line-of-effect.
5. Run a deployed Render + Netlify end-to-end release gate before promoting the combat milestone to `main`.
