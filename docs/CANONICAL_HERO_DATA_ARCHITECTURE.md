# Canonical Hero Data Architecture

This is the migration target for mass-producing Iron Pit pregens.

## Decision

Canonical heroes are data first. Python profile builders are migration scaffolding, not the long-term authoring surface.

The authoritative hero pipeline is:

`hero JSON -> edition class progression JSON -> subclass delta JSON -> build/loadout JSON -> universal capability registry -> compiled combatant -> Python/browser runtime -> certification`

A level snapshot is generated output. It is never the primary source.

## Data files

Use edition-scoped data so 2014 and 2024 can never silently bleed into each other:

- `data/heroes/2024/heroes.json` and `data/heroes/2014/heroes.json`: identity, species/race, background, class, subclass, build/loadout references.
- `data/heroes/<edition>/class_progressions/<class>.json`: levels 1-20, containing only level deltas and derived-rule inputs.
- `data/heroes/<edition>/subclasses/<subclass>.json`: sparse subclass feature deltas.
- `data/heroes/<edition>/builds/<build>.json`: ability priorities, equipment, masteries, Fighting Styles, feats, deterministic spell package/policy.
- shared capability IDs point at the same universal combat capability registry used by monsters.

## Level compiler

Compilation starts with level 1 and folds deltas through the requested level. Each delta may change only declared fields such as:

- proficiency bonus and HP;
- ability/feat increases;
- resources/use counts;
- attacks/Extra Attack;
- spell slots and prepared/known package deltas;
- feature/capability IDs;
- movement/defense changes;
- equipment/mastery changes when the build explicitly changes them.

After applying a delta, one shared derived-stat compiler recalculates values whose inputs changed. Unchanged state carries forward automatically.

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
1. export its current audited progression into edition-scoped JSON;
2. prove JSON compilation matches existing certified fingerprints;
3. switch runtime/certification to the JSON compiler;
4. delete redundant hand-authored per-level builders only after parity is permanent;
5. proceed to the next class.

Fighter is the first 2024 migration target. Its current 1-17 work becomes the parity oracle for the JSON compiler, not additional permanent per-level architecture.

## Monster alignment

The hero compiler and monster loader must converge on one finished-combatant schema: stats + actions + resources + defenses + spells + universal capability IDs. Source format may differ because heroes level and monsters do not, but combat consumes the same compiled shape.

## Performance goal

Adding an already-supported class level should be data-only. Adding twenty straightforward levels should be one batch data change plus generated tests/artifacts. Code work is reserved for genuinely missing universal capabilities.
