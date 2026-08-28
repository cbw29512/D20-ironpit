# The Iron Pit — rules-first combat MVP

**The Iron Pit** is a server-resolved SRD 5.2.1 duel prototype: Aldric Vane, a level-1 Fighter, against the SRD Goblin Warrior.

## Current production boundary

- Python/FastAPI resolves live battles server-side.
- Production dice use the operating-system CSPRNG through Python `secrets`.
- The Netlify-ready frontend replays structured battle events.
- Static preview mode uses browser Web Crypto and mirrors supported demo rules.
- GitHub Actions gates Python tests, source-size limits, rules-contract synchronization, frontend syntax, preview behavior, Netlify configuration, and the Docker build.
- Production Python and JavaScript modules are limited to 150 lines to keep the combat engine modular.

## Implemented rules

The current engine supports initiative, Surprise, pre-combat Hide, melee and ranged attacks, AC, natural 1/20 behavior, critical weapon dice, HP, healing, 0-HP arena defeat, movement, retreat movement, Dash, weapon ranges, close-ranged Disadvantage, Advantage/Disadvantage cancellation, Fighter Second Wind, Goblin conditional Advantage damage, Opportunity Attacks, Disengage, Longsword Sap, reusable Vex, the Light weapon extra attack, Two-Weapon Fighting, and Nick.

### Pre-combat stealth and Surprise

Combatants are no longer forced to materialize in an open arena and immediately roll Initiative. A scenario can declare that an actor attempts **Hide before combat** when the battlefield actually provides Heavy Obscurement, Three-Quarters Cover, or Total Cover and removes enemy line of sight.

A successful pre-combat Hide:

- uses the normal DC 15 Dexterity (Stealth) Hide rule,
- grants the supported Invisible condition state,
- does not spend the character's first combat Action or Bonus Action,
- grants Advantage on Initiative while Invisible,
- can impose Surprise Disadvantage on explicitly unaware ambush targets,
- grants Advantage on the hidden creature's first attack roll,
- ends after that attack roll under the currently supported Hide-ending triggers.

If the Hide check fails, the attempted ambush does **not** automatically produce Surprise. Advantage and Disadvantage on Initiative use the same canonical cancellation rule as other d20 rolls.

The Hide/Invisible implementation remains deliberately **partial**: attack-roll reveal and Search discovery are implemented, but loud-noise and Verbal-spell reveal triggers await sound/spell systems, and Invisible's broader seen-target restrictions await generalized spell/effect targeting.

### Light weapons and Nick

The **Light** rule uses a canonical Attack-action path: an Attack-action attack with a Light weapon can enable one extra attack with a different configured Light weapon. The normal extra attack spends the Bonus Action, is limited to once per turn, and omits a positive ability modifier from damage while retaining a negative modifier and any separate damage bonus. **Two-Weapon Fighting** restores the ability modifier. **Nick** moves that same Light extra attack into the Attack action for a mastered Nick weapon and does not create another Light extra attack.

### Goblin tactics

The Goblin Warrior can use either option of **Nimble Escape** as a Bonus Action. In melee it prioritizes Disengage, retreats without provoking an Opportunity Attack, and can switch to its Shortbow. At range, when valid concealment exists, it can Hide and attack with the resulting Advantage. The open arena does not fabricate concealment, so Hide is unavailable there unless the scenario supplies it.

Weapon mastery data currently records:

- Longsword — Sap
- Scimitar — Nick
- Shortsword — Vex
- Shortbow — Vex

A weapon having mastery metadata does **not** grant mastery to its wielder. Aldric currently masters Longsword. The SRD Goblin Warrior does not receive player weapon mastery features merely from carrying a weapon with a mastery property.

## Rules coverage API

`GET /api/rules/coverage` returns a machine-readable SRD 5.2.1 subset report. Every tracked rule is classified as:

- `implemented`
- `partial`
- `unsupported`
- `arena_assumption`

The API contract is the source of truth for scope. `frontend/rules-coverage.json` must match it exactly, and CI fails if the static and FastAPI contracts drift apart. The arena renders this coverage report for direct inspection.

Current deliberate gaps include the complete general condition framework, full Cover AC/Dexterity-save and line-of-effect behavior, spells, death saving throws, and Reaction features other than Opportunity Attacks.

The arena currently uses Initiative bonus as a deterministic tie-breaker and models combat as one-dimensional distance. Open-arena visibility is the default, with explicit per-actor concealment overrides for terrain-aware scenarios.

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

1. Add a level-1 Rogue combatant and canonical once-per-turn Sneak Attack, using pre-combat Hide/Surprise to prove the solo ambush path.
2. Add Rogue Cunning Action at level 2 on the existing Dash/Disengage/Hide action paths.
3. Add full Cover AC/Dexterity-save bonuses and line-of-effect on top of the battlefield visibility model.
4. Expand the reusable condition framework only as concrete attacks, spells, or features require it.
5. Run a final deployed Render + Netlify end-to-end release gate before promoting the combat milestone to `main`.
