# Iron Pit Audit Event Schema

## Objective

Iron Pit must make a resolved fight mechanically auditable without creating a second combat engine. Audit metadata is evidence produced from combat resolution; it must never change targeting, dice, damage, conditions, resources, timing, or outcomes.

## State model

The canonical combat engine remains the only writer of combat state. A resolved `BattleEvent` is immutable mechanical history. The audit layer may attach structured metadata to that event after resolution, and the presentation layer may format it for Step, Watch, Replay, Turbo replay, or export.

Execution modes therefore remain:

`canonical resolver -> resolved event stream -> audit envelope -> Step/Watch presentation`

Turbo suppresses presentation, but any selected Turbo fight can be regenerated from its seed and passed through the same audit envelope.

## Timing phases

Audit steps use these universal phases:

1. `precombat`
2. `initiative`
3. `action_selection`
4. `before_roll`
5. `roll`
6. `reroll_or_replacement`
7. `hit_or_save_check`
8. `damage_roll`
9. `damage_applied`
10. `state_change`
11. `resource_change`
12. `turn_end`
13. `combat_end`

A single resolved event may contain several ordered audit steps. The phase labels document when evidence belongs in the resolution chain; they do not create new mechanical timing hooks by themselves.

## Roll revision schema

Any mechanic that changes or compares a roll preserves both candidates:

```text
source_effect_id      stable feature/rule id
kind                  die_replacement | full_reroll | roll_twice_choose
original_rolls        dice before the revision
replacement_rolls     replacement/alternate dice
original_modifier     modifier before revision
replacement_modifier  modifier after revision
original_selected     selected natural die before revision, if applicable
replacement_selected  selected natural die after revision, if applicable
original_total        total before revision
replacement_total     total after revision
accepted              original | replacement
replaced_die_index    zero-based die index for a single-die replacement, otherwise null
```

The final `DiceRoll` or damage component still contains the accepted result exactly as combat used it. `revisions` only preserves provenance.

## Audit envelope

A resolved browser event may add:

```text
audit.schema_version = 1
audit.steps[]
```

Each audit step contains:

```text
phase       one universal timing phase
kind        roll | revision | check | damage | defense | hp | temp_hp |
            condition | concentration | resource | outcome | rule
label       concise human-readable evidence
```

Optional structured values may be added later, but the audit formatter must never infer a mechanic that is not already represented by the resolved event.

## Rules-lawyer guarantees

- Advantage/disadvantage shows every rolled d20 and the selected die.
- Rerolls and replacements show original and replacement candidates.
- Attack checks show the accepted total and AC.
- Saving throws show the accepted total and DC.
- Damage shows component rolls, damage type, pre-defense value, and applied value when available.
- Temporary HP and regular HP are shown as separate state transitions.
- Conditions, concentration, resources, 0-HP state, death saves, death, victory, and draw remain explicit.
- Missing evidence must be reported as missing; the audit layer must not invent it.
- RAW/Iron Pit policy decisions should eventually carry stable rule identifiers rather than relying only on prose descriptions.
