# 2014 beta website wiring repair

## Verified starting state

- Main: `8666f96495602f74c2d8138532d530982686c2fe` (PR #473).
- 2014 certification: 240/240 hero snapshots and 129/327 monsters.
- 2024 certification: 116/240 hero snapshots and 140/330 monsters.
- Druid 17 is parked in PR #474 at `f9f15157981b6b0be7b081dd7bf58e5c936ee779`; its CI is not part of this repair's readiness claim.
- Chris stopped the other window and requested this website repair. No Druid mechanics are changed here.

## Reproduced defects and repair

The live static deployment `6abd8a18989d2ec1d014032f` revealed two blockers:

1. LOAD SAMPLE searched the hero catalog for Brown Bear and Bandit monster template IDs. It now selects the certified 2014 Karnok and Seraphine level-1 pregens against the certified Skeleton and Goblin.
2. Fight and Step/Watch controls called an unexported `writeLog` method. The renderer now replaces its visible log from the existing event stream. The renderer also called nonexistent formatter methods `title` and `detail`; it now uses the existing `format` function. No combat resolver or source data changes.

Removed unused legacy initiative/HP synchronization functions: canonical replay already owns those projections. The touched renderer remains below 150 lines.

## Schema, state and lifecycle

Immutable input remains the generated, independently certified edition catalogs. App state holds the selected cards and the current execution session. The engine resolves one battle; Step and Watch consume that same battle's event stream. The log is a read-only DOM projection: Step renders a prefix, completed Watch/replay renders the full stream, and replacement prevents duplicate rows. Reset/sample selection clears the prior presentation/session through existing app lifecycle functions. Python rules and generated assets are unchanged.

## Permanent regression

`frontend/browser-beta-ui.test.cjs` runs the real catalog, engine, app controls, result renderer, log formatter, audit and Turbo/replay paths. Its DOM and animation fixture is presentation-only; it checks certified character/monster identity, sample loading, successful result display, nonempty logs, replacement without mutation/duplication, rerun availability, Step/Watch session identity without reroll, Turbo and replay completion. The test is included in CI. A separate live browser check is still required for actual DOM/layout/animation and deployment readiness.

## Publishing

Automatic Git-connected publishing stays locked in the repository. Chris authorized the beta release and subsequently requested these live-site bugs be fixed. A deliberate corrected beta upload is separate from routine pushes/merges. Do not promote a build that fails the live smoke check.
