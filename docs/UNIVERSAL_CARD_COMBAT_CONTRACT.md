# Universal Card-to-Combat Acceptance Contract

Read alongside [SOUL.md](../SOUL.md). This applies to 2014 and 2024 monsters, pregens, official content, and future homebrew.

## Non-negotiable invariant

**The engine owns the D&D combat mechanics; immutable cards declare source-specific values and behavioral parameters.** A card entirely composed of supported mechanics must work without any new combat code, source-name dispatch, or monster-specific runtime branch.

A card declares: (1) triggers and action economy; (2) target, range, senses, visibility, area, and immunity eligibility; (3) attack/check/save/automatic resolution and exact DC, dice, modifiers; (4) damage, healing, buffs, debuffs, conditions, movement, transformations, and defeat; (5) stacking, duration, concentration, source dependency, exit rules, recharge, and fight reset. Printed ability names are retained for cards and logs only, never runtime dispatch.

## Shared form contract and editor modes

The canonical runtime is `CombatantDefinition → CombatantTemplate →
CombatantState`. Source cards and user forms bind values to that pipeline;
they do not introduce an alternative combatant engine.

- **Monster editor:** empty fields accept source-level AC, HP, movement,
  attacks, multiattack composition, saves, passive traits, recharge and
  conditions. Attack damage and bonuses are declared, not guessed from a name.
- **Character editor:** empty fields accept edition, scores, level, gear,
  trained proficiencies and selected abilities. The character-building
  rules compute AC, hit/damage bonuses and save DCs before emitting the *same*
  completed combatant schema. No duplicated combat formulas in the editor.
- **Ability editor:** exact display name plus typed trigger, action/resource
  cost, area/target rule, DC source or explicit DC, ordered effects,
  success/failure outcomes, duration and reset. A monster ability can belong
  to a character when its declared mechanics are valid. User text alone
  cannot authorize executable mechanics.

A default harmful condition save means failed save applies the negative
condition and successful save does not; source-defined partial effects or
half damage on success override the default. Name substitutions only change
presentation and audit labels.

**Fail closed:** unknown/unsupported nested values, broken references,
invalid resources and unimplemented outcome-changing behavior must reject
compilation. Run parity and fight-reset tests for synthetic renamed
monster/character forms before making homebrew available in the browser.

## Executable card-field → shared-resolver contract (Chris, 2026-10-19)

**Monster work is binding work by default, not new combat programming.** CR is copied from
the printed card for identification/audit; it must not modify attack, damage, HP
or save calculations. An immutable monster form supplies source-final AC,
maximum HP, attack bonus, attack components, DC/save ability, attack sequence,
action costs, resources, triggers and typed effects. The existing compiler
validates them and creates new fight state. A character's builder may derive
the same final values, but the resolver does not recalculate the monster's
printed attack from its ability scores.

For **each attempted attack**, use this decision table in order:

| Card entry / input | Existing universal operation | Required outcome |
|---|---|---|
| action cost, remaining uses, target and range | action/resource/eligibility gates | Reject an illegal attack; an attempted legal attack spends its declared resource even when it misses |
| attack bonus, target AC, roll modifiers | shared d20 attack roll | Natural 1 misses **and ends the active Pit turn**; natural 20 hits and uses critical dice; otherwise total >= effective AC hits |
| miss | shared outcome and event stream | No on-hit damage or on-hit effect; proceed to next legal action/turn |
| hit: each *ordered* typed damage component | shared dice + typed-defense resolver | Roll printed dice/bonus; immunity = 0; resistance halves rounded down; vulnerability doubles; resolve each type separately, preserving relevant qualifiers and source-defined exceptions |
| hit: separate printed rider(s) | shared save/condition/timed-effect resolvers | Trigger only those effects specified on the card; poison **damage** never implies the Poisoned **condition** |
| new HP/temporary HP and terminal state | shared HP, zero-HP and condition lifecycle | At 0 HP an ordinary monster is removed as an active enemy; a dying hero follows death-save rules; source-defined zero-HP overrides and terminal Dead/Petrified Pit rules take precedence |
| action sequence and unspent Bonus Action | shared Multiattack/action-economy scheduler | Execute only printed/legal remaining attacks; never invent extra attacks, double-spend an Action, or give a Bonus Action merely because an attack missed |

**An attack is one hit determination, not a separate attack for each damage
type.** Example: a source Bite with +5 to hit, 2d6+3 piercing and 2d6
poison rolls to hit once. On a hit, those are two damage components resolved
by the same typed-damage function, with separate piercing and poison defenses.
A different creature or a renamed attack with the same parameters must yield
the same mechanical outcome. A creature's printed Multiattack only schedules
additional whole attacks; it does not change hit/damage resolution.

**Saves are distinct from attacks.** A card-declared Constitution DC 12
gaze uses the target's Constitution saving-throw modifier, not AC or the
gaze source's attack bonus. The existing sight/visibility, eye-aversion,
turn-start trigger, staged Restrained/Petrified and condition-defeat primitives
must be composed from source parameters; no Basilisk/Medusa-name resolver.
The Pit's small board often makes a printed range cover every *geometrically
eligible* opponent, but range does not cancel walls, darkness, Blindness,
special senses, gaze aversion or timing. Speed is often immaterial but is
never globally ignored when reach, positioning or other supported movement
legality is relevant.

**Before adding a new helper:** find the source field, its compiled capability,
the Python resolver, the browser resolver, and the existing regression. If
all five already exist, **bind the card and test it**. If a link is broken,
repair the smallest link. Only create a new source-neutral primitive when an
exact semantic remainder is proven missing. Remove superseded duplicate
logic in the *touched* subsystem without an unrelated mass rewrite.

**Mandatory proof for a reused attack form:** one hit, one miss, typed
resistance/immunity/vulnerability, source-name/ID renaming, zero-HP behavior,
the printed action sequence and per-fight reset as applicable; verify both
Python and browser paths and source serialization. Report a monster as fully
finished only after source completeness, exact-head CI, merge and actual
webpage-fight evidence, per the [session continuity contract](IRON_PIT_SESSION_CONTINUITY.md).

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
