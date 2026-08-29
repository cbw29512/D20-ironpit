# The Iron Pit

**Pick D&D cards. Watch stick figures close into melee and fight to the death.**

Iron Pit is a rules-first browser combat game built against the D&D 2024 / SRD 5.2.1 rules. The production fight path runs entirely in the browser; Python remains the reference rules implementation used by CI.

## Locked product goal

1. Choose a party size of 1–6 characters.
2. For each character slot, choose one of the 12 core classes, a level from 1–20, and an available build/card.
3. Add RAW-ready monster cards from a catalog sorted numerically by Challenge Rating.
4. Start in the standard flat Pit, normally 30 feet apart.
5. Combatants use legal ranged/thrown attacks while closing when available.
6. They continue closing and do not kite, retreat, flee, or disengage to preserve range.
7. Once engaged, legal melee attacks are preferred. Ranged-only combatants can still attack in melee with the normal rules penalties.
8. The fight continues until one side is dead, not merely reduced to 0 HP.
9. The browser replays the event stream as a stick-figure battle while preserving the detailed combat log for rules auditing.

See `docs/ARENA_POLICY.md` for the exact arena assumptions.

## Encounter builder

The character side uses dropdown menus instead of a single long card picker:

- **How many characters?** 1–6.
- **Class:** all 12 core classes.
- **Level:** 1–20.
- **Build / Card:** the three planned build tracks for that class/level.
- Uncertified class/level/build combinations remain visible but are marked unavailable for fighting; the app never substitutes an approximate build.

The monster side is ordered by numeric CR, not alphabetically. A CR filter narrows the 330-monster catalog, and **Add Monster** places the chosen RAW-ready creature into the encounter rotation. Multiple copies can be added up to the Pit encounter limit.

## Current content model

- 330 unique SRD 5.2.1 monsters are cataloged with source metadata.
- Unsupported outcome-changing mechanics fail closed instead of being approximated.
- 63 monster templates are currently certified runnable in the browser combat engine.
- The hero catalog contains 720 planned cards across the 12 core classes, levels 1–20, and three build slots per level. Only explicitly audited builds are runnable; the current RAW-ready browser heroes are the level-1 Fighter and Barbarian builds.

## Combat foundation already represented

The certified subset includes core d20 attack resolution, AC, HP, initiative, natural 1/20 behavior, critical weapon dice, typed and mixed damage defenses, temporary HP hooks, advantage/disadvantage, range penalties, ordered Multiattack including mixed weapon/save steps, movement, Charge, Pack Tactics, Prone, Grappled, Restrained, Poisoned, timed conditions, condition immunities, Rage, Savage Attacker, Second Wind, Orc Adrenaline Rush/Relentless Endurance, zero-HP handling, Death Saving Throws, and deathmatch targeting of downed player characters.

A mechanic is considered ready only when both the Python reference and browser production path are covered by regression tests where applicable.

## Production architecture

- **GitHub:** source of truth and CI.
- **GitHub Pages / Netlify:** static deployment targets.
- **Browser engine:** authoritative production fight execution; no production `/api/` dependency.
- **Python rules reference:** CI oracle and test bed, not required by the deployed site.

Non-production Netlify builds are intentionally skipped to protect deploy credits.

## Run locally

### Browser app

```bash
python -m http.server 8080 --directory frontend
```

Open `http://localhost:8080`.

The checked-in source catalog is copied into `frontend/data/` by the static-site preparation script used for production/CI.

### Python reference tests

```bash
cd backend
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -e '.[dev]'
pytest -q
```

## Certification gate

GitHub Actions must pass on the exact head before a roster count or UI build is called certified. The gate checks:

- production source-size limits;
- the full Python rules-reference suite;
- static browser packaging and the 330-monster data artifact;
- JavaScript syntax;
- deterministic browser combat regressions;
- numeric monster-CR sorting and the character dropdown model;
- the melee-deathmatch contract;
- the animated Pit wiring;
- backend-free production execution;
- the production-only Netlify credit guard.

## Next product priorities

Continue expanding the RAW rules engine and monster-specific animation vocabulary. New monsters and heroes become runnable only after every outcome-changing mechanic they depend on is implemented and certified; unsupported rules are never approximated just to increase the card count.
