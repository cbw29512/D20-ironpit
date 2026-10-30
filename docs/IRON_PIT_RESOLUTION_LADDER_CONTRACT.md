# Iron Pit Resolution Ladder Contract

This document is a normative supplement to `docs/IRON_PIT_RULES_CONTRACT.md`.
It records the universal combat-resolution decisions that Python, browser runtime,
Step, Watch, Replay, Turbo, tests, and audit logging must preserve.

## 1. Universal resolution ladder

Resolve combat through shared primitives, not creature-name code:

`availability -> legality -> attack/save/automatic effect -> interrupts -> branch result -> effects -> defenses/counters -> Temporary HP -> HP/state -> downstream triggers`

Creature data supplies the values: attack type, DC, damage dice/types, areas,
conditions, resources, timing, durations, and prerequisites.

A failed prerequisite terminates only dependent branches. A miss prevents hit-only
damage, hit-only riders, and hit-triggered saves. Printed Miss, Hit-or-Miss, or
otherwise independent clauses continue through their own branches.

Resolve source clauses in source/logical order unless a more specific RAW rule
changes the order. Resolve each event completely before dependent events.

## 2. Audit-grade combat log

The log is an actual combat record, not a summary. Preserve enough structured
evidence to explain every state change, including:

- every die result, accepted die, reroll, modifier, and modifier source;
- AC/DC checked, final total, result, and exact success/failure margin;
- interrupts such as Shield or Parry and the value they changed;
- every raw damage component and damage type;
- every save reduction, immunity, resistance, vulnerability, reduction, and
  other defense applied to each component in exact order;
- the final damage packet, Temporary HP absorbed, current HP lost, and HP/max-HP
  changes as separate facts;
- resources spent/recharged and action-economy costs;
- conditions/effects applied, rejected, removed, or expired;
- concentration checks and their triggering damage event;
- target/range/area/position facts needed to prove legality;
- skipped downstream branches and why they did not execute.

Never rewrite history to show only the final number.

## 3. Hit, damage, and trigger distinctions

`targeted`, `hit`, `damaged`, `takes <type> damage`, `HP lost`,
`reduced to 0 HP`, and similar trigger windows are distinct facts.

Example: an attack hits and rolls 15 Fire damage against Fire Immunity:

- attack result remains HIT;
- raw Fire damage remains 15;
- Fire Immunity changes applied Fire damage to 0;
- current-HP loss is 0;
- a `when hit` trigger can still qualify;
- a `when damaged` trigger does not qualify from that zero-damage event unless
  specific wording says otherwise.

If an interrupt raises AC and turns an apparent hit into a miss, the final result
is a miss and hit-only branches do not execute.

## 4. Damage components and packet construction

Resolve every damage component independently.

For each component record raw amount, type/qualifiers, save or other reduction,
immunity/resistance/vulnerability, other applicable modifiers, and final
component damage.

A hit containing four damage types can therefore produce four separately
modified final components. After those components are resolved, combine the
components belonging to the same damage event into one final incoming damage
packet unless the source explicitly creates separate damage events.

Apply sequential reductions in RAW order and round at each step where RAW
requires it. Example: 31 Fire -> successful half-damage save 15 -> Fire
Resistance 7.

Each affected creature resolves its own complete ladder independently. One
target's save, immunity, resistance, vulnerability, condition, or other defense
never leaks to another target.

## 5. Temporary HP

Cards display current HP, maximum HP, and Temporary HP as separate numbers.

For ordinary damage:

1. resolve all component defenses/modifiers;
2. construct the final damage packet;
3. Temporary HP absorbs that packet first;
4. remaining damage reduces current HP;
5. specific source text that bypasses or changes Temporary HP overrides this
   general rule.

Temporary HP is not healing and does not stack unless a specific rule says so.
Iron Pit deterministic retention policy:

- new Temporary HP greater than current -> replace current pool;
- new Temporary HP lower than current -> keep current pool;
- equal amount -> keep the existing pool.

Preserve the retained pool's source identity and source-specific expiry/effects.

Damage taken, Temporary HP absorbed, current HP lost, and maximum HP changes are
separate facts. If a rider keys off damage taken, use the value named by its
source wording even when Temporary HP absorbed some or all of that damage.

If maximum HP falls below current HP, clamp current HP to the new maximum. That
clamp is a state adjustment, not additional damage. When a max-HP reduction
ends, current HP does not automatically increase; missing HP must be healed
unless source text explicitly restores it.

## 6. Saving throws and concentration

A hit followed by a saving throw remains a hit. The save changes only the
effects governed by that save unless source text says otherwise.

If an effect lists only a Failure result, success means that listed Failure
effect does not occur unless another clause supplies a success effect.

One damage event produces one concentration check even if it contains multiple
damage types. Separate damage events can each produce their own check.

Temporary HP absorbing all positive damage does not erase the damage event, so
concentration still checks when RAW requires it. If defenses reduce final
damage to 0, no damage was taken and that zero-damage event does not trigger a
concentration check.

## 7. Recharge

Recharge is a universal availability/resource lifecycle, never an action type.

The underlying ability remains its normal Action, Bonus Action, Reaction,
attack, Saving Throw, spell, movement, area, condition, or other primitive.

If a Recharge ability is available, Arena AI prioritizes it in its proper action
slot whenever its normal RAW target, trigger, range/area, prerequisites, and
action-economy requirements are satisfied. If it is unavailable or illegal,
fall back to other legal choices.

Recharge never bypasses action economy or printed prerequisites. Successful
Recharge restores availability only; it does not automatically execute the
ability or grant an extra action.

## 8. RAW default

When source text and the selected ruleset already answer a question, follow RAW.
Do not create an Iron Pit exception merely for implementation convenience.
Only genuine source/policy ambiguities require a new product ruling.
