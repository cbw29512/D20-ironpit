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

- Netlify serves the prepared static browser site.
- `scripts/prepare_static_site.py` generates/copies authoritative browser artifacts from the Python rules/content oracle.
- The browser combat engine resolves fights locally.
- Production has no HTTP API/backend dependency.
- The Python implementation remains in the repository for rules behavior, generation, audits, manifests, and CI only.
- Docker/server deployment files are intentionally absent unless a future server-backed product feature is explicitly approved.

## Production smoke test

- [ ] The page loads with no backend service.
- [ ] The catalog contains exactly 330 canonical 2024 SRD monster records.
- [ ] Only RAW-ready cards can enter automated combat.
- [ ] 1–6 Hero Cards and 1–6 Monster Cards can be selected.
- [ ] Duplicate monster cards remain independent combatants.
- [ ] FIGHT resolves through the canonical browser execution controller/engine.
- [ ] STEP FIGHT can advance one event at a time.
- [ ] WATCH REST continues the same Step session without rerolling/restarting.
- [ ] Turbo uses the same combat engine with presentation overhead suppressed.
- [ ] A selected Turbo fight reproduces from its recorded seed.
- [ ] Engine-rule errors are excluded from Turbo outcome ratios and remain reproducible.
- [ ] HP, conditions, buffs/debuffs, concentration, resources, death saves, down/death states, and other supported state visibly update.
- [ ] A player character reaching 0 HP does not automatically end the fight unless a specific lethal rule overrides the generic 0-HP path.
- [ ] The DM Details log matches the event stream and expandable audit evidence.
- [ ] Unsupported outcome-changing mechanics fail closed.

## CI requirements before production

- [ ] Python reference/certification tests pass.
- [ ] Production source-size limits pass.
- [ ] Capability/source audits pass.
- [ ] Certification manifests regenerate/verify cleanly.
- [ ] Static-site preparation produces deterministic current artifacts.
- [ ] Generated-static parity is clean.
- [ ] All production JavaScript passes syntax validation.
- [ ] Permanent browser combat regressions pass.
- [ ] Step/Watch/Replay/Turbo invariants pass.
- [ ] Audit annotation is proven non-invasive.
- [ ] CI proves the active production path has no required API/backend dependency.
- [ ] Both public static entry points contain all required production modules.
- [ ] Netlify production-only credit guard passes.

## Future services

Accounts, persistence, rankings, or other server-backed features may introduce a service later. They are not dependencies of the combat product and must not be added to the fight path without a deliberate architecture decision and new certification gates.
