# Universal Card-to-Combat Acceptance Contract

Read alongside [SOUL.md](../SOUL.md). This applies to 2014 and 2024 monsters, pregens, official content, and future homebrew.

## Non-negotiable invariant

**The engine owns the D&D combat mechanics; immutable cards declare source-specific values and behavioral parameters.** A card entirely composed of supported mechanics must work without any new combat code, source-name dispatch, or monster-specific runtime branch.

A card declares: (1) triggers and action economy; (2) target, range, senses, visibility, area, and immunity eligibility; (3) attack/check/save/automatic resolution and exact DC, dice, modifiers; (4) damage, healing, buffs, debuffs, conditions, movement, transformations, and defeat; (5) stacking, duration, concentration, source dependency, exit rules, recharge, and fight reset. Printed ability names are retained for cards and logs only, never runtime dispatch.

## Composable examples

- **Petrifying Gaze:** active source passive → visibility/range/aversion predicate → Constitution saving throw → staged target debuff → Petrified terminal defeat (locked Iron Pit override).
- **Leadership:** action activation → timed friendly aura → attack/save bonus die on eligible recipients → expire by duration or source HP at zero (locked Pit rule).
- **Poisonous strike:** attack hit → damage → saving throw → timed Poisoned debuff.
- **Homebrew aura:** source-provided trigger, geometry, recipients and modifier values → same aura/condition engine as official cards.

## Rules for refactoring and implementation

1. Inventory each existing semantic primitive and its monster/pregen consumers before adding any mechanic.
2. If primitives already exist, bind data and write parity tests; **do not add a monster-specific resolver**.
3. If something is missing, build the smallest source-neutral primitive, prove it with unrelated synthetic card data, then batch-bind all applicable source cards.
4. Compose effects using the same universal order: trigger → eligibility → attack/check/save → damage/healing/conditions/movement → lifecycle/reset.
5. Preserve all printed rules and Pit overrides. Do not mark a creature complete by silently dropping unsupported behaviors.
6. Source templates stay immutable. Changes during battle live exclusively in per-fight state and reset on the next fight.
7. Certify Python and browser behavior, generated artifacts, source-driven blocker count and zero regressions before merging.
8. Refactor **incrementally inside monster implementation batches**, not as a speculative wholesale rewrite.

## Proof of architectural compliance

Create a synthetic homebrew combatant using already-supported effects with different names and parameters. It must execute identically to equivalent official cards in both Python and browser, **with no engine modifications**. A new printed card may require declarative source binding and certification tests; it must not require name-based branching or a new resolver when its semantics are already supported.

**Completion metric:** verified source obligations resolved and certified monster admissions per work session, never PR count or infrastructure changes alone.
