# Canonical Hero Data Architecture

This is the migration target for mass-producing Iron Pit pregens.

## Decision

Canonical heroes are data first. Python profile builders are migration scaffolding, not the long-term authoring surface.

The authoritative hero pipeline is:

```text
identity JSON
+ species JSON
+ class progression JSON
+ subclass delta JSON
+ character track JSON (ASIs, canonical HP, origin feats, mastery picks)
+ build/loadout JSON
→ fold to source facts
→ universal capability registry
→ compiled combatant
→ Python/browser runtime
→ certification
```

A level snapshot is generated output. It is never the primary source.

A class progression file MUST NOT contain a character. Ability scores, HP, species traits, origin feats, and this hero's weapon-mastery picks do not belong in `class_progressions/fighter.json`. That was the defect on `feat/2024-fighter-15-reanchored`.

## Data files

Use edition-scoped data so 2014 and 2024 can never silently bleed into each other:

- `data/heroes/<edition>/heroes.json`: identity pointers (species, class, subclass, build, track).
- `data/heroes/<edition>/species/<species>.json`: species combat facts and resources.
- `data/heroes/<edition>/class_progressions/<class>.json`: class-only level deltas.
- `data/heroes/<edition>/subclasses/<subclass>.json`: sparse subclass feature deltas.
- `data/heroes/<edition>/tracks/<hero>.json`: one persistent character (scores, ASIs, canonical HP, origin feats, mastery picks).
- `data/heroes/<edition>/builds/<build>.json`: equipment, Fighting Style, attacks, visual loadout.
- shared capability IDs point at the same universal combat capability registry used by monsters.

`hp_by_level` on the track is canonical fingerprint evidence until hit-die derivation is proven to match it. Do not silently replace those numbers.

## Level compiler

Compilation starts with level 1 and folds deltas through the requested level. Species and origin capabilities are applied once, then each class/subclass row, then that level's ASI and mastery pick from the track.

After applying a delta, one shared derived-stat compiler recalculates attack/damage/save/initiative from ability scores and proficiency. Unchanged state carries forward automatically.

## Capability contract

Hero JSON does not implement rules. It names universal capability IDs.

If a monster and hero have equivalent RAW behavior, both records reference the same capability. A new class/subclass feature is therefore normally one of:

1. an existing capability ID with parameters;
2. an existing primitive with a new declarative trigger/configuration;
3. a genuinely new universal capability implemented once in Python and browser.

Never create a hero-name, class-name, subclass-name, or level-specific combat resolver.

## Batch certification

Certification runs by track, not by manually registering individual levels.

For each canonical track:

1. compile levels 1-20 in order;
2. validate RAW/source metadata and schema;
3. resolve every combat capability against the universal registry;
4. fail closed at the first unsupported outcome-changing capability;
5. continue auditing later levels and other tracks so one blocker does not stop the batch;
6. generate runtime/browser records and certification artifacts for every clean level.

The certification report must state the first blocker for each track and all later levels transitively blocked by it.

## Migration

Do not rewrite already-working universal mechanics.

Migrate one class at a time:
1. export its current audited progression into the split JSON files above;
2. prove JSON compilation matches existing certified fingerprints;
3. switch runtime/certification to the JSON compiler;
4. delete redundant hand-authored per-level builders only after parity is permanent;
5. proceed to the next class.

Fighter is the first 2024 migration target. Existing certified Python Karnok 1–N on `main` is the parity oracle, not additional permanent per-level architecture.
