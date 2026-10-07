# Iron Pit Implementation Manual

Purpose: let a fresh AI begin productive Iron Pit work with minimal context and no guessing.

## Start here

1. Read `SOUL.md`.
2. Read `docs/CURRENT_OPERATING_STATUS.md`.
3. Read exactly one task guide:
   - Pregens: `docs/playbooks/PREGENS.md`
   - Monsters: `docs/playbooks/MONSTERS.md`
   - Universal engine: `docs/playbooks/UNIVERSAL_ENGINE.md`
4. Read `docs/UNIVERSAL_MECHANIC_INVENTORY.md` to identify existing engine IDs and all current monster/pregen demand.
5. Read the exact source/card and current code/tests for the mechanic being touched.
6. Open the long contracts only when the selected guide points to them, the mechanic touches that subsystem, or something is uncertain.

## Core ownership rule

**The universal engine owns behavior. Content owns exact source parameters.**

The engine defines what Blinded, Prone, an attack roll, a saving throw, damage, healing, resistance, recharge, movement, and similar mechanics do.

The monster/pregen/source defines the exact AC, DC, attack bonus, save ability, damage dice/type, range, duration, target count, recharge threshold, resource count, qualifiers, ruleset, and printed name.

Never hardcode source numbers or source identity into a universal resolver.

## Non-negotiable RAW rule

Iron Pit implements combat behavior exactly. The only deviations from ordinary tabletop assumptions are the explicit Iron Pit arena/environment policies already recorded in `docs/IRON_PIT_RULES_CONTRACT.md` and indexed in `docs/IRON_PIT_LOCKED_RULES.md`.

Never invent, approximate, silently omit, or infer an unsupported combat mechanic.

If exact behavior cannot be represented:

- park the affected card/feature;
- record the exact missing semantic or RAW question;
- continue the rest of the current family/pass;
- return to parked technical debt after the pass is exhausted;
- ask Chris one precise question whenever interpretation or architecture is uncertain.

Unsupported outcome-changing mechanics fail closed.

## Standard implementation path

`source -> decompose behavior -> inventory lookup -> search/reuse primitives -> bind source parameters -> fight state -> Python oracle -> browser parity -> regenerate inventory/artifacts -> certification`

Printed names and complete source abilities belong on cards/source data and player logs. A unique monster or homebrew ability must still be created/bound correctly even when the engine has no same-named capability. Engine dispatch uses universal mechanics underneath it; only a genuinely new semantic remainder justifies adding a new reusable primitive.

Repository source and permanent tests are the final implementation truth.
