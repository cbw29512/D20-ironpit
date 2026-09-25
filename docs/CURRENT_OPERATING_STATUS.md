# Current operating status

Recorded 2026-09-25 against `main` after PR #380 merged.

This file is operating authority for *what to work on next*. Combat rules still live in `docs/IRON_PIT_RULES_CONTRACT.md`. If this file and a chat summary disagree, this file wins until it is updated on `main`.

## Owner split

- **Iron Pit (`cbw29512/D20-ironpit`)** is the only combat-engine lane. One agent at a time.
- **Blackink Bestiary / coloring-book local AI** is a separate product. Do not mix PRs, CI, or GPU loops into this repository.

## What is already certified on `main`

From `backend/app/content/certified_hero_progressions.py`:

| Edition | Class | Registered levels |
|---|---|---|
| 2014 | Fighter (Champion) | 1–20 |
| 2014 | Barbarian (Berserker) | 1–20 |
| 2014 | Rogue (Thief) | 1–20 |
| 2014 | Monk (Open Hand) | 1–20 |
| 2014 | Paladin (Devotion) | 1–20 |
| 2024 | Fighter | 1–18 |
| 2024 | Rogue | 1–20 |
| 2024 | Cleric (Life) | 1–12 |
| 2024 | Barbarian | 1–7 |

2024 public-ready hero slots in `data/hero_certification_manifest.json`: **57 / 240**.
2014 browser monster roster asserted in tests: **129** certified.

Holy Nimbus (2014 Paladin 20) is a timed self-buff plus timed emanation primitive. Do not add a Paladin-named combat resolver.

## Active lane

**Finish remaining 2014 canonical pregens before any new 2024 class expansion.**

Next class: **2014 Life Cleric, one persistent 1–20 progression.**
Relevant open work to rebase onto current `main` rather than stacking new PRs:

- #361 Build 2014 Life Cleric as one persistent level 1-20 progression
- #364 / #366 later 2014 Cleric completion slices
- #363 approved spell upcasting + 2014 Turn Undead
- #355 2014-first sequencing lock (merge or close once this file is the lock)

After 2014 Cleric 1–20: Bard, Druid, Ranger, Sorcerer, Warlock, Wizard (2014), then 240/240 2014 re-audit.

Do **not** open or merge 2024 Cleric 13+, 2024 Fighter 19+, or 2024 Barbarian 8+ until that 2014 gate.

## Parked / superseded

Stale stacked PRs whose work already landed on `main` (2014 Paladin 20, 2014 Rogue 20, 2014 Monk 20, 2024 Rogue 20, 2024 Cleric through 12) are to be closed as superseded. Do not rebase them.

Universal-engine PRs that are still current against `main` may stay open only if they are required by the 2014 Cleric lane (healing, conditions, save tags, upcasting).

## CI / spend

September 2026 included Actions usage was exhausted by Iron Pit volume (~$197 gross on this repo).

Heavy workflows are gated:

- `2014-hero-certification.yml` — `main`, PRs into `main`, or `workflow_dispatch`
- `sync-generated.yml` — `main` or `workflow_dispatch` only (never `feat/2014-*`)
- `ci.yml` — `main` + pull_request (unchanged)

Do not restore per-push certification on feature branches. Run generators locally; commit owned outputs; use **Run workflow** when a cert pass is required.

## Agent rules for this repo

1. One coherent tranche per PR. Rebase on current `main` or close.
2. Never hand-edit generated artifacts.
3. Never implement a class-named resolver when a universal primitive exists.
4. Ask one clarification question rather than guessing RAW.
5. Do not start a second class while 2014 Cleric is open.
