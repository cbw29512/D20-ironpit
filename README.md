# The Iron Pit

**Pick D&D cards. Watch stick figures close into melee and fight to the death.**

Iron Pit is a rules-first browser combat game built against the D&D 2024 / SRD 5.2.1 rules. The production fight path runs entirely in the browser; Python remains the reference rules implementation used by CI.

## Locked product goal

1. Pick 1–8 RAW-ready hero cards.
2. Pick 1–8 RAW-ready monster cards.
3. Start in the standard flat Pit, normally 30 feet apart.
4. Combatants use legal ranged/thrown attacks while closing when available.
5. They continue closing and do not kite, retreat, flee, or disengage to preserve range.
6. Once engaged, legal melee attacks are preferred. Ranged-only combatants can still attack in melee with the normal rules penalties.
7. The fight continues until one side is dead, not merely reduced to 0 HP.
8. The browser replays the event stream as a stick-figure battle while preserving the detailed combat log for rules auditing.

See `docs/ARENA_POLICY.md` for the exact arena assumptions.

## Current content model

- 330 unique SRD 5.2.1 monsters are cataloged with source metadata.
- Unsupported outcome-changing mechanics fail closed instead of being approximated.
- The current feature branch is expanding the RAW-ready runtime roster in certified batches; 55 monster templates are presently linked as certification candidates.
- The hero catalog contains 720 planned cards across the 12 core classes, levels 1–20, and three build slots per level. Only explicitly audited builds are runnable; the current RAW-ready browser heroes are the level-1 Fighter and Barbarian builds.

## Combat foundation already represented

The certified subset includes core d20 attack resolution, AC, HP, initiative, natural 1/20 behavior, critical weapon dice, typed damage defenses, temporary HP hooks, advantage/disadvantage, range penalties, Multiattack/Extra Attack sequencing, movement, Charge, Pack Tactics, Prone, Rage, Savage Attacker, Second Wind, Orc Adrenaline Rush/Relentless Endurance, zero-HP handling, Death Saving Throws, and deathmatch targeting of downed player characters when no standing enemy remains.

A mechanic is considered ready only when both the Python reference and browser production path are covered by regression tests where applicable.

## Production architecture

- **GitHub:** source of truth and CI.
- **Netlify:** static production site.
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

GitHub Actions must pass on the exact head before a roster count is called certified. The gate checks:

- production source-size limits;
- the full Python rules-reference suite;
- static browser packaging and the 330-monster data artifact;
- JavaScript syntax;
- deterministic browser combat regressions;
- the melee-deathmatch contract;
- the animated Pit wiring;
- backend-free production execution;
- the production-only Netlify credit guard.

## Next product priorities

After the current exact head is green: continue strengthening the watchable stick-figure fight loop, then add outcome-changing mechanics such as saving throws, Grappled, Restrained, additional conditions/riders, reactions, recharge actions, and later spellcasting. Monster and hero coverage expands only when the mechanics they depend on are correctly supported.
