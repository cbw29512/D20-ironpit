# Monster Capability Attrition Roadmap

Status source: latest generated 123-ready / 207-blocked certification analysis from the active runtime-derived certification tranche.

## Strategy

Iron Pit does not certify monsters one by one when several monsters share the same missing mechanic.

For every tranche:

1. Group blocked monsters by shared capability signature.
2. Pick the highest-yield reusable engine primitive.
3. Classify primitive versus trigger/configuration before coding.
4. Implement the primitive once in Python and browser runtimes.
5. Bind source-derived monster data to the primitive.
6. Run focused parity tests.
7. Regenerate certification artifacts.
8. Recompute blocker yields and repeat.

Monster names never select combat behavior. Names are only source/catalog identifiers.

## Current blocker families

| Family | Blocked monsters containing family | Engine work |
| --- | ---: | --- |
| save-or-complex-action | 122 | Expand declarative SavingThrowAction outcomes/targeting/source compilation |
| limited-use | 113 | Universal Recharge and X/Day resource lifecycle |
| condition-or-control | 106 | Complete condition payloads, forced movement, swallow/engulf/control lifecycle |
| trait | 99 | Convert recurring trait patterns into reusable triggers/effects |
| spellcasting | 66 | Universal source-derived monster spell packages and action selection |
| bonus-action | 57 | Generic action-cost binding and source compilation |
| legendary | 30 | Legendary Resistance plus legendary action pool/timing |
| reaction | 16 | Generic trigger/interrupt grammar beyond existing Parry/Redirect/OA |
| unsupported-action-rider | 15 | Reusable attack rider payloads such as speed changes, granted Advantage, attachment, and extra typed damage |

Counts overlap. A monster can contribute to several families.

## Highest-value signatures

### Tier 1 — Recharge + SavingThrowAction

15 monsters are blocked only by `limited-use + save-or-complex-action`:

- Black Dragon Wyrmling
- Blue Dragon Wyrmling
- Copper Dragon Wyrmling
- Gold Dragon Wyrmling
- Green Dragon Wyrmling
- Red Dragon Wyrmling
- White Dragon Wyrmling
- Young Black Dragon
- Young Blue Dragon
- Young Copper Dragon
- Young Gold Dragon
- Young Green Dragon
- Young Red Dragon
- Young White Dragon
- Hell Hound

Shared shape: a Recharge action, a Saving Throw, typed damage on failure, and half damage on success.

**First primitive:** universal Recharge resource lifecycle. Saving Throw, typed damage, half-on-success, and shared damage rolls already exist.

### Tier 2 — Recharge + SavingThrowAction + condition/control

12 monsters share `condition-or-control + limited-use + save-or-complex-action`, including metallic breath/control effects and several recharge-based monster powers. After Tier 1, add declarative failed-save condition/control payloads instead of a second save engine.

### Tier 3 — SavingThrowAction + condition/control

10 monsters have `condition-or-control + save-or-complex-action` without limited-use. Once Tier 2 condition payloads exist, these become lower-cost source bindings.

### Tier 4 — Trait-only attrition

13 monsters currently have only `trait` as a blocker. Repeated trait primitives include:

- Fire Aura
- Incorporeal Movement
- Magic Resistance
- Blood/Bloodied Frenzy
- Regeneration

Implement repeated trait primitives first; isolated trait headings wait until their underlying engine primitive is identified.

## Later shared primitives

- complete condition semantics: Charmed, Frightened, Invisible, Exhaustion, Petrified staging;
- forced push/pull and source-driven movement;
- ongoing start/end-turn damage;
- regeneration and conditional healing;
- proximity auras;
- generic reactions and interrupts;
- Legendary Resistance;
- legendary action pools and after-turn timing;
- generic monster spellcasting;
- dynamic summons/forms/splitting only when required by remaining roster blockers.

## Completion rule

A capability tranche is finished only when the exact branch head passes Python/browser parity, source audit, generated-artifact parity, and certification regeneration. Progress is reported only from the generated monster certification manifest.