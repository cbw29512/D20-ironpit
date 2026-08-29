# Iron Pit Deployment Checklist

## Cost and branch policy

Netlify is reserved for deliberate production deployment and real production bandwidth testing.

- [ ] Production branch is `main`.
- [ ] Deploy Previews are disabled.
- [ ] Branch deploys are disabled.
- [ ] GitHub Actions handles branch/PR certification.
- [ ] `netlify.toml` keeps the production-only build guard enabled.
- [ ] Feature work merges to `main` only after exact-head CI passes.

The repository guard skips Netlify builds whenever `CONTEXT` is not `production`.

## Production architecture

Iron Pit production is a **static browser application**.

- Netlify serves `frontend/`.
- `scripts/prepare_static_site.py` copies the SRD catalog artifact required by the browser catalog.
- The browser combat engine resolves fights locally.
- Production must not depend on `IRON_PIT_API_BASE`, `/api/`, Render, Docker, or a running FastAPI service.
- The Python implementation remains in the repository as a rules-reference/CI oracle.

## Production smoke test

- [ ] The page loads without a backend service.
- [ ] The catalog reports 330 SRD monster records.
- [ ] Only RAW-ready cards can be added to a fight.
- [ ] 1–8 Hero Cards and 1–8 Monster Cards can be selected.
- [ ] Duplicate monster cards remain independent combatants.
- [ ] Party Total Levels and Monster Total CR update correctly.
- [ ] The standard 30-foot Pit and 5-foot engaged start are available.
- [ ] **FIGHT** resolves through `IRON_PIT_BROWSER_ENGINE.runEncounter`.
- [ ] The animated stick-figure Pit appears and replays the battle event stream.
- [ ] Ranged/thrown attacks can occur while combatants close; nobody holds range or kites.
- [ ] Multiattack/Extra Attack uses its legal action economy.
- [ ] HP, criticals, healing, movement, death saves, downed states, and deaths visibly update.
- [ ] A player character reaching 0 HP does not automatically end the fight.
- [ ] The result appears only after the deathmatch reaches a winner or the safety round limit.
- [ ] The DM Details log matches the replayed event sequence.

## CI requirements before production

- [ ] Python reference tests pass.
- [ ] Production source-size limits pass.
- [ ] Static site preparation produces the SRD catalog artifact.
- [ ] All production JavaScript passes syntax validation.
- [ ] Deterministic browser engine, Rage, monster-batch, and melee-deathmatch regressions pass.
- [ ] CI proves the active production path contains no API dependency.
- [ ] CI proves the animated Pit is wired into the active fight path.
- [ ] Netlify production-only credit guard passes.

## Future services

Accounts, persistence, rankings, or other server-backed features may introduce a service later. They are not dependencies of the combat MVP and must not be added to the fight path without a deliberate architecture decision and new certification gates.
