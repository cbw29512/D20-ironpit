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
| `turnFinalize` | No | Post-action finalization for a normal resolved turn |
| `turnEndLifecycle` | No | End-turn lifecycle that must run even when no normal action turn occurred |
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

The browser production `bonusActionWindow` is migrated at the same checkpoints used by the pre-existing turn policy:

- `beforeEscape`: Rage entry first, including Instinctive Pounce as a Rage-owned rider; then Second Wind, with Tactical Shift remaining a Second Wind rider;
- grapple escape remains between the early and late pre-action Bonus Action checkpoints;
- `afterEscape`: Adrenaline Rush;
- `postAction`: 2014 Monk bonus attacks, then 2014 Frenzy, then 2024 Rage maintenance.

The preserved pre-action Arena order is `Rage -> Second Wind -> grapple escape -> Adrenaline Rush`. The preserved post-action order is `Monk -> Frenzy -> Rage maintenance`. Hook priority records those existing deterministic orders; it does not create a new tactical policy.

Rage expiration is deliberately **not** part of the exclusive Bonus Action claim. It is registered in nonexclusive `turnFinalize` cleanup so Rage can still expire after Monk, Frenzy, or another feature spends the Bonus Action.

The Python certification oracle intentionally retains its existing orchestration for this tranche. Permanent parity tests lock its current Bonus Action policy while browser regressions prove the equivalent hook-driven order. No Python combat rule is changed merely to mirror browser source structure.

The browser production `onHit` / `onMiss` phases now preserve the existing single-attack audit event through a typed mutable `attackOutcome` accumulator. Outcome hooks may mutate that accumulator and combat state, but they must return the normal hook result shape with an empty `events` array; they may not emit separate battle events for effects that historically belong to the aggregate attack event.

The preserved hit order is `Topple -> Sap/Tactical Master -> Vex`. The preserved miss order is `Graze -> Studied Attacks`. Generic hit damage, printed control effects, condition-save handling, zero-HP lifecycle, Rage incapacitation cleanup, and concentration cleanup remain in the shared attack primitive rather than being mislabeled as named ability hooks.

The Python oracle retains its existing attack orchestration for this tranche. Dedicated parity coverage proves that Graze and Studied Attacks still coexist on one miss, that Tactical Master/Sap correctly replaces a weapon's native mastery on a hit, and that an unreplaced Vex hit still primes the next attack. Browser hook regressions lock the equivalent order and aggregate-event behavior.

`turnFinalize` and `turnEndLifecycle` are intentionally separate. `turnFinalize` covers post-action normal-turn work such as Rage expiry after Bonus Action resolution. `turnEndLifecycle` runs from the encounter engine after every turn slot, including 0-HP/death-save-only turns that never enter `resolveTurn()`.

2014 Intimidating Presence invalidation belongs to `turnEndLifecycle`, matching the Python encounter engine's `end_invalid_presence()` ordering before target/source end-turn condition timing. This fixes the previous browser gap where a 0-HP creature could skip the cleanup because browser cleanup lived only inside `resolveTurn().finalize()`.

## Migration order

Migrate one coherent phase per PR.

1. Land this dispatcher, its tests, documentation, HTML wiring, and CI wiring with zero callers.
2. Migrate `bonusActionWindow` first. Preserve current Bonus Action policy exactly. Rage, Second Wind, Adrenaline Rush, and other genuine competing actions register; Tactical Shift remains a rider on Second Wind.
3. Migrate `onHit` / `onMiss` after the first phase is certified.
4. Separate `turnFinalize` from `turnEndLifecycle` and migrate lifecycle-only cleanup such as 2014 Intimidating Presence invalidation.
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
