# Iron Pit Resolution Ladder Contract

This document is a normative rules supplement to `docs/IRON_PIT_RULES_CONTRACT.md` for the universal combat-resolution ladder. It records clarified edge cases that must be preserved by Python, browser runtime, Step, Watch, Replay, Turbo, permanent tests, and audit logging.

## 1. Resolution model

Iron Pit resolves combat as a deterministic ladder of universal primitives. Creature-specific data supplies attacks, saves, damage, damage types, ranges, areas, conditions, prerequisites, resources, and timing. The engine does not create monster-name-specific shortcuts.

Each branch stops when its prerequisite fails. A miss prevents hit-only damage, hit-only riders, and hit-triggered saves, but explicit Miss, Hit-or-Miss, or otherwise independent source clauses still resolve through their own branches.

Resolve source clauses in their logical/source order unless a more specific RAW rule changes that order. Resolve each event completely and update state before moving to the next dependent event.

## 2. Attack and save audit requirements

Every attack/save must log enough information to function as an actual combat record, including:

- die result(s);
- all modifiers and their sources;
- final total;
- AC or DC checked;
- success/hit or failure/miss;
- exact margin, such as `21 vs AC 25: miss by 4` or `17 vs DC 15: success by 2`;
- reactions/interrupts that changed the check;
- the downstream branches that did or did not execute and why.

If Shield, Parry, or another legal interrupt changes AC so an otherwise-hit attack becomes a miss, the final result is a miss caused by that interrupt. Hit-only branches do not execute. Explicit miss branches still can.

A hit followed by a separate saving throw remains a hit. A successful save changes only the effects governed by that save unless the source explicitly says it also changes earlier damage or other prior effects.

If a saving-throw effect lists only a Failure result and no Success effect, success means the listed Failure effect does not occur unless another source clause says otherwise.

## 3. Trigger distinctions

`targeted`, `hit`, `damaged`, `takes <type> damage`, `reduced to 0 HP`, and similar trigger windows are distinct facts.

Example: an attack can hit, roll 15 Fire damage, encounter Fire Immunity, and apply 0 damage. In that case:

- `targeted` is true;
- `hit` is true;
- raw Fire damage is 15;
- Fire Immunity is evaluated;
- applied Fire damage is 0;
- HP loss from that component is 0;
- `when hit` triggers may still qualify;
- `when damaged` / `when taking Fire damage` do not qualify from that zero-applied component unless specific wording says otherwise.

The log must preserve the raw result and the defense that reduced the applied result instead of rewriting history as if no damage had been rolled.

## 4. Damage components and packet construction

Every damage component is resolved independently through its relevant defenses/modifiers. A single attack/effect can contain any number of damage components.

For each component, record at least:

1. raw damage amount;
2. damage type and relevant qualifiers;
3. save or other source-defined reduction, if that reduction applies to the component;
4. immunity/resistance/vulnerability and other applicable modifiers in RAW order;
5. final component damage.

Example: `12 Slashing + 10 Fire` can become `6 Slashing + 10 Fire` if only Slashing Resistance applies. Fire Immunity, Fire Resistance, or Fire Vulnerability affects only the Fire component.

When multiple reductions apply sequentially, each intermediate value is logged. Example: raw Fireball 31 -> successful save 15 -> Fire Resistance 7 -> final component 7, with each halving rounded according to RAW at the point it occurs.

After all components of one damage event are independently resolved, combine their final component values into that event's final incoming damage packet unless the source specifically requires separate damage events or a component bypasses a later layer.

## 5. Independent targets

Each target resolves its own complete ladder independently.

For an area effect, geometry determines the affected targets, but each affected target separately resolves its own save, modifiers, defenses, conditions, damage, Temporary HP, HP, concentration, and follow-up state.

One creature's immunity, resistance, vulnerability, save result, or condition never leaks to another creature. A Fire Elemental can take 0 Fire damage from the same Fireball that damages a nonimmune creature normally.

## 6. Temporary HP state and card display

Combatant cards must display these as separate numeric state values:

- current HP;
- maximum HP;
- Temporary HP.

Recommended card presentation: `HP 42 / 60 | Temp HP 8`.

Temporary HP is a separate pool, not current HP, maximum HP, or healing.

For a normal damage event, after all component defenses/modifiers produce the final incoming damage packet:

1. Temporary HP absorbs damage first;
2. any remainder reduces current HP;
3. a specific source rule that bypasses or alters Temporary HP overrides this generic step.

Example: final packet 16, Temp HP 9, current HP 42 -> Temp HP 0, remaining damage 7, current HP 35.

The log must separately record final incoming damage, Temporary HP absorbed, remaining damage, and current-HP loss.

## 7. Temporary HP replacement

Temporary HP pools do not stack unless a specific rule explicitly says otherwise.

Iron Pit deterministic retention policy:

- new Temporary HP greater than current -> replace current pool;
- new Temporary HP less than current -> keep current pool;
- equal amounts from different sources -> keep the existing pool;
- never allow a smaller/equal new pool to overwrite the larger/existing pool under this policy.

Preserve source identity and any source-specific expiry/rules needed for the retained pool. Log the offered amount, existing amount, comparison, and retention/replacement result.

## 8. Damage taken, HP loss, and maximum HP are separate facts

Do not conflate:

- final damage taken/applied by the damage event;
- Temporary HP absorbed;
- current HP lost;
- maximum HP changes.

Example: 13 Necrotic damage after defenses, Temp HP 10, current HP 40/60:

- final Necrotic damage event: 13;
- Temp HP absorbed: 10;
- current HP lost: 3;
- current HP becomes 37;
- a separate rider that reduces maximum HP by the damage taken can still reduce max HP by 13 if that is what the source says.

Source wording controls which value a rider references. Effects tied to `damage taken` use the applicable final damage value; effects tied to HP lost use actual HP loss; specific wording wins.

If maximum HP is reduced below current HP, clamp current HP to the new maximum. That clamp is a state adjustment, not additional damage and does not itself trigger `when damaged` effects.

If a maximum-HP reduction later ends, maximum HP increases but current HP does not automatically increase. Missing current HP must be healed by a healing effect unless the source explicitly restores it.

Healing changes current HP only up to the current maximum and does not restore/spend Temporary HP unless a specific effect says otherwise.

## 9. Recharge is availability, not an action type

Recharge is a universal resource/availability lifecycle. It does not define an ability's attack type, save type, damage, range, area, condition, action slot, trigger, or tactical mechanics. Those come from the creature's source-derived ability data.

Examples:

- a Recharge ranged attack is still the normal ranged-attack primitive;
- a Recharge melee attack is still the normal melee-attack primitive;
- a Recharge cone/line/emanation uses the normal area/save primitives;
- a Recharge Bonus Action still consumes/uses the normal Bonus Action slot;
- a Recharge Reaction still requires its normal trigger and Reaction availability.

Iron Pit AI policy: if a Recharge ability is available, prioritize using it in its appropriate action slot when its normal target, trigger, range/area, prerequisites, and action-economy requirements are satisfied. If it is unavailable or cannot legally be used, fall back to the creature's other legal actions. Recharge never bypasses printed prerequisites or action economy.

Successful Recharge only restores availability. It never changes the underlying ability's mechanics.

## 10. Concentration and damage events

Concentration checks are driven by damage events, not by the number of damage types inside one event.

If one attack/effect creates one damage event containing multiple components, resolve every component independently, combine the final components into that event's final damage packet, and make one concentration check if that event legally requires one.

Example: one hit that resolves `8 Slashing + 6 Fire + 4 Necrotic` is one damage event and therefore produces one concentration check after the complete damage event is resolved, not three checks merely because three damage types were present.

If the source actually creates separate damage events, including damage at different timing windows, each separate event can independently trigger its own concentration check according to RAW.

The audit log must identify the damage event that caused each concentration check and preserve the applicable final damage value, derived DC, roll, modifiers, total, margin, and result.

## 11. Implementation invariant

The universal resolver should be modeled as small, composable conditional branches rather than monster-specific scripts:

`availability -> legality -> attack/save/automatic primitive -> interrupts -> branch result -> damage/effects -> defenses/counters -> Temporary HP -> HP/state -> downstream triggers`

Every node must preserve enough structured evidence for the audit-grade combat log and Replay Mode. A failed branch prevents only its dependent children; independent source clauses continue according to RAW/source order.
