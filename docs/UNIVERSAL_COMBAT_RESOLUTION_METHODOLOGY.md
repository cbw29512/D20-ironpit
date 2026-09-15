# Universal Combat Resolution Methodology

This document locks the implementation methodology for Iron Pit combat. It exists to prevent architecture drift while monsters, pregens, spells, traits, actions, and effects are added at scale.

This is not a suggestion. New combat work must follow this methodology unless an explicit product decision changes it.

## 1. Core principle

Iron Pit has one combat engine.

Monsters and pregens do not own bespoke combat logic. They provide declarative source data describing:

- what action is available;
- how it targets;
- what roll or save determines the result;
- its attack bonus or save DC;
- its damage components;
- what generic effects are attached;
- what trigger applies each effect;
- duration and removal rules;
- resource/recharge/usage limits;
- source-specific exceptions when RAW truly requires them.

The engine owns the rules for attack rolls, saving throws, damage, conditions, movement, defenses, resources, timing, reactions, and state transitions.

A Wolf and a Worg may have different attack bonuses, save DCs, damage, or source wording. If both can knock a target Prone, they must use the same universal Prone effect implementation.

## 2. Canonical combat loop

For every available action, the engine follows the same ordered process.

1. **Choose intent.** Determine the preferred action based on the combatant's available actions and current state.
2. **Check availability.** Is the action available under action economy, resources, recharge, conditions, and source limits?
3. **Check targeting.** Are there legal targets?
4. **Check positioning.** Can the action legally affect the intended target or targets from the current position?
5. **Optimize movement if needed.** If movement can make the preferred action legal or improve the number/value of targets, move to the best reachable legal position. Do not move without an action-driven reason.
6. **Revalidate.** After movement, confirm the action is still available and the target or targets are still legal.
7. **Resolve the action's success gate.**
   - Attack-roll action: roll to hit.
   - Save action: affected targets make their saves independently.
   - Automatic action: no attack/save gate unless the source says otherwise.
8. **Stop immediately on an untriggered branch.** A missed attack has no hit effects to resolve unless the source explicitly defines a miss effect. A successful save does not receive failed-save effects unless the source explicitly says otherwise.
9. **Resolve triggered damage and effects.** For every triggered result, resolve the source-defined damage components and attached generic effects.
10. **Apply target defenses.** Check the target's relevant resistance, immunity, vulnerability, condition immunity, save modifiers, active effects, and other legal defenses.
11. **Update authoritative state.** Apply final damage, HP changes, conditions, movement changes, resources, concentration, death/life-state changes, and other resulting state.
12. **Process reactions and triggered follow-ups at the correct timing window.**
13. **Check remaining action economy.** If the acting combatant can legally do more, return to action selection and repeat the same loop. Otherwise end the turn.
14. **Continue initiative.** The next combatant uses the same loop.

The engine should be boring and deterministic in structure. Complexity belongs in the data and in reusable rules primitives, not in bespoke per-creature flow control.

## 3. Success gates

Every action must declare or compile to one of a small number of universal success gates.

### Attack-roll gate

Flow:

`legal action -> legal target -> range/position -> attack roll -> hit or miss`

- **Miss:** stop resolving hit-triggered damage/effects.
- **Hit:** resolve all source-defined hit damage/effects in order.
- Critical behavior remains ruleset-specific and source-specific where required.

### Saving-throw gate

Flow:

`legal action -> affected target set -> each target rolls its own save -> success/failure branch`

- AoE geometry determines **who is evaluated**, not a separate combat engine.
- Each affected creature resolves its own save using its own modifiers, Advantage/Disadvantage, immunities, buffs/debuffs, and other defenses.
- The source defines what happens on save success and failure.
- Shared damage rolls may be used where RAW/source semantics call for one shared roll, while each target still resolves its own save and defenses independently.

### Automatic gate

Flow:

`legal action -> legal target/effect area -> automatic source-defined effects`

Automatic effects still pass through relevant immunities, defenses, timing, and source qualifiers.

## 4. Effects are universal primitives

Conditions and other common combat outcomes are engine capabilities, not creature capabilities.

Examples include:

- Prone
- Grappled
- Restrained
- Frightened
- Poisoned
- Stunned
- Blinded
- Invisible
- movement reduction
- forced movement
- ongoing damage
- max-HP reduction
- healing
- Temporary HP
- Advantage/Disadvantage sources
- buffs/debuffs
- resource gain/loss
- concentration

A source action attaches one or more generic effect instructions to a trigger such as:

- on hit;
- on miss;
- on failed save;
- on successful save;
- on damage dealt;
- on damage taken;
- at start/end of turn;
- on entering/leaving an area;
- automatic/always.

The source provides its own DC, duration, damage dice, source identity, repeat-save timing, stacking semantics, and other parameters. The generic effect resolver provides the shared rule behavior.

## 5. Source identity matters; source-specific code usually does not

The engine must always preserve source identity because source data determines numbers and exceptions.

For example:

- Wolf Bite may trigger a Strength save against the Wolf's printed DC and apply Prone on failure.
- Worg Bite may use a different printed DC and still apply the same Prone effect.
- A target may have a higher or lower Strength save, Advantage/Disadvantage, or immunity that changes the result.

The engine therefore needs to know:

- who caused the effect;
- which action caused it;
- the source-defined DC or attack bonus;
- the exact target;
- the trigger result;
- the universal effect to apply.

It should **not** need `if monster_name == "Wolf"` or `if monster_name == "Worg"` to make Prone work.

## 6. Damage is component-based

Each damage component resolves independently through the universal defense pipeline.

Example: an attack that deals piercing plus fire damage produces two components.

For each component:

1. identify damage amount and damage type;
2. preserve qualifiers such as magical/nonmagical, weapon/spell, melee/ranged, etc.;
3. check the target's applicable immunity, resistance, vulnerability, reduction, absorption, and source-specific defenses in the correct order;
4. compute final component damage;
5. apply the resulting damage through Temporary HP/current HP/life-state rules in the correct order.

Do not merge unlike damage types before defenses are evaluated.

## 7. Movement serves action intent

Movement is not a separate AI objective.

The engine asks:

`What action do I want to use, and can movement make it legal or better?`

Rules:

- If the preferred action is already legal/effective from the current position, do not move without another action-driven reason.
- If the preferred action is not currently legal but reachable this turn, move to enable it.
- If an AoE action can hit more legal enemies from another reachable position, evaluate reachable positions and select the position that maximizes the action's legal result under deterministic tie-breakers.
- If the preferred action cannot be made legal, evaluate the next action.
- Normal ranged attackers do not move merely because movement remains available.
- Melee attackers close only as needed to reach legal melee distance.

This same policy must be shared by monsters and pregens.

## 8. Multiattack, Extra Attack, Bonus Actions, reactions, and follow-ups

Multiple actions/attacks do not create a new combat methodology.

After each resolved component of the acting creature's action economy:

1. fully update state;
2. process mandatory reactions/triggers at the correct timing window;
3. check whether the acting creature still has another legal attack/action/Bonus Action/follow-up;
4. if yes, return to the same universal selection and resolution loop;
5. if no, end the turn.

Each attack within Multiattack or Extra Attack resolves independently unless the source explicitly links results.

## 9. Compiler/binding rule

When adding a monster or pregen, do **not** begin by writing combat behavior for that creature.

Instead:

1. parse/source its action, trait, spell, resource, and effect data;
2. map each mechanic to existing universal capabilities;
3. identify any mechanic that genuinely cannot be represented;
4. if a capability is missing, implement the smallest reusable engine primitive that represents the entire mechanic family;
5. bind the creature's data to that primitive;
6. certify every other creature/pregen that becomes representable from the same capability.

A new engine primitive should normally unlock a **family** of creatures or actions, not one named stat block.

## 10. Anti-patterns that are prohibited

Do not introduce:

- monster-name branches for mechanics that can be expressed as source data;
- duplicate Prone/Grapple/Poison/etc. implementations for different sources;
- a special damage pipeline for one monster family when standard damage components suffice;
- a separate AoE combat engine;
- movement that runs before action intent and then guesses what to do afterward;
- effect resolution after a miss when the source has no miss effect;
- failed-save effects on a successful save unless the source explicitly says so;
- assumed/default DCs when source data is missing;
- silent approximation of unsupported combat-relevant source wording;
- Python/browser rules divergence;
- Step/Watch/Replay/Turbo mechanical divergence.

## 11. Devil's-advocate guardrails

The methodology is simple, but several edge cases must not be oversimplified.

### A. Some abilities have effects on a miss or successful save

The default is "miss means no hit effects," but source wording can explicitly define a miss effect or a successful-save effect. The data model therefore needs explicit trigger branches rather than hardcoding `miss = nothing` globally.

### B. Some actions have multiple sequential gates

An attack can hit and then require a second save for a rider. Example structure:

`attack hits -> damage -> target save -> condition on failed save`

That is still the same engine. The hit simply triggers a second generic save/effect instruction.

### C. Some effects depend on prior or current state

Examples include "if the target is already Grappled," "while Poisoned," "if this damage reduces the target to 0," or "if the creature moved at least X feet." These should compile to reusable predicates/trigger conditions, not named-creature branches.

### D. Some reactions interrupt before the original action fully resolves

Shield-like defenses, Opportunity Attacks, Counterspell-style mechanics, damage reactions, and specific interrupts must execute at their actual timing windows. The universal loop must expose those windows rather than resolving an entire action atomically when RAW does not.

### E. Specific wording can override general rules

The universal engine is the default pipeline. Source-specific rules can alter ordering or behavior where RAW explicitly says they do. Such exceptions should be expressed as reusable qualifiers/policies wherever possible and must remain auditable.

### F. Target selection and effect resolution are separate concerns

AoE optimization may choose the best position/shape, but once targets are established, every target still resolves its own save/defenses/effects independently. Do not conflate targeting AI with rules resolution.

### G. Repeated effects need source-aware lifecycle

Two sources may apply the same universal condition with different durations or removal rules. The condition behavior remains universal, but source instances and expirations must remain distinguishable.

These guardrails do not change the methodology. They define where the data model must be expressive enough to preserve RAW without creating bespoke creature engines.

## 12. Architecture review questions

Before accepting any new combat implementation, ask:

1. Is this actually a new universal mechanic, or only a new source using an existing mechanic?
2. Can the difference be represented as data: DC, dice, damage type, trigger, duration, range, area, resource, qualifier, or predicate?
3. Would this code work unchanged if ten more monsters or pregens used the same mechanic tomorrow?
4. Does a miss/save-success branch terminate immediately when no source effect is attached?
5. Are target defenses resolved from the target's current state rather than encoded into the attacker?
6. Are damage components kept separate through immunity/resistance/vulnerability processing?
7. Does movement exist only to support a chosen action or improve its result?
8. Can Python and browser engines consume the same semantic model?
9. Can Step, Watch, Replay, and Turbo all use the same resolution path?
10. Is every source-specific number or exception traceable back to declarative data/source wording?

If the answer to #3 is no because the code mentions one monster/class/stat-block name, stop and redesign unless the source contains a truly unique rule that cannot be expressed generically.

## 13. Working definition of done for a mechanic

A combat mechanic is not complete merely because one creature can use it.

It is complete when:

- the mechanic exists as a reusable engine capability;
- source data can bind to it without named-creature logic;
- attacker/source parameters remain distinct from target defenses/state;
- attack/save/automatic trigger branches behave correctly;
- damage/effects follow the universal ordered pipeline;
- effect lifecycle/timing is auditable;
- Python and browser behavior match;
- all four execution modes use the same semantics;
- representative permanent regressions prove the capability;
- applicable monsters/pregens can be recertified through the same capability.

The scaling goal is explicit: adding hundreds of monsters and pregens should primarily mean adding and validating data, not writing hundreds of new combat engines.
