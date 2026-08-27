# Iron Pit D20 Roadmap

## Milestone 0 — Deployed vertical slice

- Fighter vs Goblin duel deployed end to end.
- CI green.
- Netlify frontend connected to the public FastAPI service.
- Deployment smoke test completed.

## Milestone 1 — Reusable combat content

- Extract reusable weapon, shield, and armor records.
- Add weapon animation families (`slash`, `chop`, `thrust`, `smash`).
- Keep final AC and attack resolution server-authoritative.

## Milestone 2 — First RAW expansion

- Advantage and disadvantage.
- Goblin conditional bonus damage.
- Fighter Second Wind.
- Longsword Sap Weapon Mastery.
- Published rules-coverage status for each feature.

## Milestone 3 — Ranged combat

- Distance/range state.
- Shortbow attack option.
- Projectile battle events.
- Directional arrow animation.

## Milestone 4 — Character and monster catalogs

- Pregenerated character progression data for levels 1–20.
- SRD-licensed monster catalog with source/license metadata.
- Character and monster selection UI.

## Milestone 5 — Spell and condition event system

- Saving throws.
- Spell slots and concentration.
- Spell visual/icon metadata.
- Conditions and visual state transforms.
- Petrified state can render a combatant gray/frozen.
- Breath-weapon area-effect event/animation family.

## Milestone 6 — Accounts and persistence

- Supabase Auth.
- Profiles and battle history.
- Server-side auth validation.
- Postgres battle persistence.
- Rate limiting and abuse controls.

## Deferred product experiments

Prediction points, rankings, tournaments, cosmetics, and any collectible system are intentionally deferred until the combat/watch loop is proven. Anything involving staking money or prizes of value requires separate legal/product review before implementation.
