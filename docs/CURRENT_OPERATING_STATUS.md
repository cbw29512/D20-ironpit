# Current operating status

Recorded 2026-09-25 against `main` after PR #390 merged.

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
| 2014 | Cleric (Life) | 1–20 |
| 2014 | Bard (Lore) | 1–20 |
| 2024 | Fighter | 1–18 |
| 2024 | Rogue | 1–20 |
| 2024 | Cleric (Life) | 1–12 |
| 2024 | Barbarian | 1–7 |

2024 public-ready hero slots in `data/hero_certification_manifest.json`: **57 / 240**.
2014 browser monster roster asserted in tests: **129** certified.

Holy Nimbus (2014 Paladin 20) is a timed self-buff plus timed emanation primitive. Do not add a Paladin-named combat resolver.

## Active lane

**Finish remaining 2014 canonical pregens before any new 2024 class expansion.**

Next class: **2014 Druid, one persistent 1–20 progression.**

2014 Life Cleric 1–20 merged in PR #388. Older Cleric PRs #361, #364, and #366 are superseded and closed.

After 2014 Druid 1–20: Ranger, Sorcerer, Warlock, Wizard (2014), then 240/240 2014 re-audit.

Do **not** open or merge 2024 Cleric 13+, 2024 Fighter 19+, or 2024 Barbarian 8+ until that 2014 gate.

## Parked / superseded

Stale stacked PRs whose work already landed on `main` (2014 Paladin 20, 2014 Rogue 20, 2014 Monk 20, 2024 Rogue 20, 2024 Cleric through 12) are to be closed as superseded. Do not rebase them.

Universal-engine PRs that are still current against `main` may stay open only if they are required by the 2014 Cleric lane (healing, conditions, save tags, upcasting).


## Universal combat refactor plan

Architecture target: **checks -> modifiers -> result -> state mutation -> audit**.

This is now the default refactor direction for the engine. Named abilities remain source/audit metadata; combat resolution depends on universal typed facts.

Current migration sequence:

1. **Conditions / buffs / debuffs**
   - remove class/feature-name immunity branches where an existing condition-immunity or debuff-counter primitive can express the rule;
   - preserve source qualifiers such as creature type, magical/nonmagical origin, effect tags, duration, and resource cost;
   - Nature's Ward is the immediate Druid proving case: poison/disease immunity plus Fey/Elemental-scoped Charmed/Frightened immunity.
2. **Attacks / saves / checks**
   - keep legality, roll-mode modifiers, bonuses, DC/AC comparison, and final result separate;
   - source abilities provide data, not alternate attack/save engines.
3. **Damage / healing**
   - route all components through typed defense/reduction/replacement checks before HP mutation.
4. **Movement**
   - route movement through legality, movement-mode, terrain/debuff/counter, path, and final-position checks.
5. **Resources / action economy / recharge**
   - resolve availability first, then spend only after the action is accepted at the appropriate resolution point.
6. **Hooks / reactions / interrupts**
   - keep timing generic; named sources register declarative behavior into canonical windows.

Refactor discipline:

- preserve behavior while migrating;
- Python reference and browser implementation move together;
- add/regenerate permanent parity tests for every migrated path;
- do not create a new primitive when existing checks/modifiers can compose the rule;
- do not stall the active 2014 Druid lane for unrelated cosmetic rewrites;
- when a named special case is discovered during active work, migrate it if the shared replacement is small and safe; otherwise record it here and continue the canonical lane.

Immediate examples:

- **Nature's Ward (Druid 10):** completed as the proving case for typed checks -> universal modifiers/counters -> result; no Druid-named resolver.
- **Mindless Rage:** known named branch in the condition-immunity path. Do not mechanically collapse it yet; preserve the 2014 vs 2024 difference for already-active Charm/Frighten while migrating it to shared condition/debuff semantics in a dedicated tranche.

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
5. Do not start a second class while the active 2014 class progression is open.
