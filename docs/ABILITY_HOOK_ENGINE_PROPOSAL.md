# Ability Hook Engine — Sequencing Contract

Status: accepted sequencing extension to `UNIVERSAL_COMBATANT_ARCHITECTURE.md`.

PR 1 installs the dispatcher, tests, documentation, and static wiring only. It does **not** migrate an ability or change combat outcomes. Every behavior-changing phase migration still requires Python/browser parity evidence on the exact commit.

## Objective

Iron Pit already treats Advantage, Damage, Saving Throws, Conditions, resources, and movement as shared primitives. Turn and attack sequencing must follow the same rule.

`resolveTurn()` and `resolveAttack()` must not grow indefinitely as ordered lists of named abilities. Sequencing becomes a shared primitive: the engine exposes a fixed set of timing phases, and ability modules register into those phases.

The dispatcher decides **when a registered resolver is allowed to participate**. It does not roll dice, calculate rules, choose targets, or replace the ability's own module.

## Data schema

### Fixed phases

The canonical browser phases are:

| Phase | Exclusive claim? | Intended timing |
|---|---:|---|
| `turnStart` | No | Start-of-turn effects before an action choice |
| `bonusActionWindow` | Yes | Competing uses of the single Bonus Action |
| `mainAction` | Yes | Competing uses of the current Action |
| `turnFinalize` | No | Post-action/end-of-turn follow-up and cleanup |
| `beforeAttackRoll` | No | Attack-roll sources before the d20 is resolved |
| `onHit` | No | Effects triggered by a confirmed hit |
| `onMiss` | No | Effects triggered by a confirmed miss |

These names are closed schema. Unknown phase strings fail immediately. If real RAW timing requires another phase, change this architecture deliberately rather than registering a typo or inventing a one-off hook.

### Ability descriptor

Every registration declares:

```text
AbilityHookDescriptor
  id: non-empty stable string, unique within the phase
  rulesets: non-empty subset of ["2014", "2024"]
  priority: finite number, default 100
  appliesTo(member, ctx): optional eligibility predicate
  resolve(ctx): resolver returning null or HookResult
```

`rulesets` is mandatory. A genuinely shared ability must explicitly declare both editions. This preserves the hard 2014/2024 boundary.

`priority` is **deterministic evaluation order only**. It is not an AI preference score and must not silently become tactical decision policy. If multiple independent legal actions compete, the existing policy/selection logic must determine which option is eligible to claim the window.

### Hook result

Resolvers have one accepted result shape:

```text
HookResult
  events: BattleEvent-like objects produced by this resolver
  sequence: authoritative next sequence integer
  claimed: boolean
```

`null` means the hook did nothing.

A returned event does **not** automatically mean an action window was consumed. `claimed=true` is explicit and is valid only in an exclusive phase. In an exclusive phase, the dispatcher stops only after the specific resolver currently running returns `claimed=true`.

This replaces the earlier `handled` / `stopOnHandled` design, which allowed cumulative state from an earlier hook to stop a later hook incorrectly.

## Mutable state and lifecycle

The hook registry is process/static-module state. It contains descriptors only; it is not combat state and must not store HP, conditions, resource counts, targets, or per-match choices.

All fight mutation remains in the existing temporary `CombatantState` / browser state objects and resets under the normal match lifecycle. A resolver receives current context and delegates to existing ability/rules modules.

The dispatcher clones the caller's event array before resolution so hook evaluation cannot mutate the caller's list through an alias.

## Ruleset isolation

`runPhase()` requires a combat member whose template has `ruleset` equal to `2014` or `2024`. A hook is skipped unless that ruleset appears in its descriptor.

The dispatcher never converts one edition into the other and never infers edition from an ability name.

## Error contract

The dispatcher fails closed.

- Unknown phases are rejected.
- Invalid descriptors and invalid results are rejected.
- Duplicate IDs within a phase are rejected.
- Invalid member/ruleset context is rejected.
- Exceptions in `appliesTo` or `resolve` are logged with phase, ability ID, combatant ID, ruleset, and stage, then rethrown with contextual error information.
- No failure path substitutes a different rule or silently skips an outcome-changing resolver.

## Riders are not competing actions

Not every feature should register independently.

For example, Tactical Shift is triggered by Second Wind. It is a rider on the Second Wind resolution, not another competing Bonus Action. The parent action can call the rider from its own existing module flow.

This keeps the hook registry focused on genuine timing participants rather than forcing every nested feature into a phase.

## Python/browser parity map

PR 1 is inert: no ability uses the dispatcher, so Python behavior is unchanged and browser combat behavior is unchanged.

Before each later phase migration:

1. identify the current Python reference resolution point;
2. identify the current browser resolution point;
3. identify shared/declarative eligibility data and ruleset scope;
4. define action/bonus-action/reaction consumption and reset semantics;
5. preserve the existing tactical decision policy rather than using hook priority as a substitute;
6. add permanent parity/regression evidence;
7. require the exact intended commit to pass GitHub Actions.

The browser and Python implementations do not need identical source structure, but supported behavior must remain equivalent.

## Current migration status

The pre-action `bonusActionWindow` is now migrated in the browser production engine for:

- Rage entry, including Instinctive Pounce as a Rage-owned rider;
- Second Wind, with Tactical Shift remaining a Second Wind rider;
- Adrenaline Rush.

The preserved Arena decision order is `Rage -> Second Wind -> Adrenaline Rush`. Hook priority records that existing order; it does not create a new tactical policy.

The Python certification oracle intentionally retains its existing orchestration for this tranche. Permanent parity tests assert the same choice order there. Post-action Bonus Action features such as Monk bonus attacks, Frenzy attacks, and Rage maintenance remain in the existing turn-finalization path and are **not** part of this pre-action migration.

## Migration order

Migrate one coherent phase per PR.

1. Land this dispatcher, its tests, documentation, HTML wiring, and CI wiring with zero callers.
2. Migrate `bonusActionWindow` first. Preserve current Bonus Action policy exactly. Rage, Second Wind, Adrenaline Rush, and other genuine competing actions register; Tactical Shift remains a rider on Second Wind.
3. Migrate `onHit` / `onMiss` after the first phase is certified.
4. Migrate `turnFinalize`.
5. Migrate `mainAction` and `turnStart` last because they are the most structural.
6. After a phase is migrated, `resolveTurn()` / `resolveAttack()` may not name individual abilities from that phase. A new named special case is evidence that the phase model or shared policy needs review.

## Non-negotiable invariants

- One dispatcher owns phase sequencing.
- Ability rules/math stay in ability/shared-rule modules.
- Hooks contain no monster-name, hero-name, or class-name branches.
- Ruleset scope is explicit on every registration.
- An event is not the same thing as consuming an action opportunity.
- `claimed` is valid only for exclusive phases.
- Priority is ordering, not tactical intelligence.
- Phase additions are architecture changes, not ad hoc strings.
- One phase migration per tranche; never combine it with unrelated rules work.
