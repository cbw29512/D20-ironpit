# Iron Pit Implementation Playbook

This is the **small first-read implementation guide** for combat work. It distills the
rules in `SOUL.md`, the locked rules, universal architecture, content contracts, and
verification policy into one execution path. Those deeper files remain authoritative
when this playbook points to them or when a conflict/uncertainty appears.

## One rule above all

**Implement what the ability does, not what it is called.**

Printed names are for source provenance, cards, logs, and certification. They are not
combat dispatch keys. Prone is Prone. Grappled is Grappled. Unconscious is Unconscious.
Damage, healing, saves, Advantage, Resistance, recharge, resources, movement, and timing
are universal mechanics regardless of source.

## Fast implementation loop

For every monster, pregen feature, spell, feat, item, or homebrew ability:

1. Read the exact source behavior and edition.
2. Ignore the printed name and write the mechanic as:
   **trigger/timing -> cost/resource -> attack/check/save -> effect -> duration -> exits/reset**.
3. Search existing monster **and** pregen code for each semantic piece.
4. Reuse existing primitives. Compose several primitives when needed.
5. Add source-only parameters: name, DC, dice, type, range/area, duration, resource,
   recharge, target rules, timing, edition, and qualifiers.
6. Add a new universal primitive only when existing mechanics cannot represent the behavior.
7. Prove one smallest representative card first.
8. Expand the same binding to the rest of the mechanically identical family.
9. Run one focused changed-family verification, regenerate required artifacts, then use
   one exact-head CI pass. Do not repeatedly retest unchanged systems.
10. Update the blocker/tracker docs and move immediately to the next real blocker.

If source wording, timing, or semantic equivalence is uncertain, stop that card/family,
record the blocker, and resolve the rule before inventing engine behavior.

## State-first map

| Layer | Owns |
|---|---|
| Immutable source/card | printed name and RAW parameters |
| Universal capability schema | generic mechanic inputs |
| Combat state | temporary buffs, debuffs, conditions, resources, recharge, timers |
| Resolver | universal behavior only |
| Audit/log | printed source name + generic outcome evidence |
| Certification | proves source -> schema -> Python/browser parity |

Cards/templates never mutate in combat. Fight state resets after the fight.

## Monster example — 2014 Brass Dragon Sleep Breath

**RAW behavior, stripped of the name:**

`Action -> shared breath recharge -> cone -> CON save -> failed save applies timed
Unconscious -> ends on damage OR ally spends an Action to wake -> otherwise expires`.

**Correct universal composition:**

- Area save primitive: existing `SavingThrowAction`.
- Geometry: existing cone targeting.
- Recharge/resource: existing shared breath resource + Recharge 5–6.
- Condition: existing universal `unconscious`.
- Duration: existing failed-save timed-effect lifecycle.
- Damage exit: existing `ends_on_damage`.
- Wake exit: existing Action-based condition-removal machinery with generic
  `wake-sleeper` removal action.
- Source logs: keep **Sleep Breath** as the displayed ability name.

**Do not create:** `SleepBreathResolver`, Brass-Dragon condition code, or a
monster-name check.

**Sample-first order:**

1. Brass Dragon Wyrmling — prove DC 11, 15-ft cone, 1 minute, shared breath resource.
2. Reuse the same capability for Young — bind its own DC/range/duration.
3. Reuse for Adult — bind its own DC/range/duration.
4. Ancient reuses the same Sleep primitive but remains independently blocked if another
   printed action such as Change Shape is still unsupported.

A successful Wyrmling implementation does **not** justify copying its parameters to
other ages or editions.

## Universal-engine change example

Suppose source data already contains:

- `effect_id = unconscious`
- `ends_on_damage = true`
- `allowed_removal_action_ids = ["wake-sleeper"]`

but the runtime drops `allowed_removal_action_ids`.

That is **not a new Sleep mechanic**. Widen the existing generic timed-effect path:

`source data -> generic schema -> Python apply -> browser serialization/apply ->
existing condition-removal resolver`.

Then audit other monsters/pregens that already carry the same generic field. A universal
engine change must be source-neutral and usable by future homebrew cards.

## Pregen example — Lay on Hands across editions

Strip the class/feature name away:

`resource-backed healing and/or condition removal with a printed action cost`.

Reuse the universal:

- resource primitive;
- healing action;
- condition-removal action;
- targeting/range rules.

Bind edition-specific facts as data. If 2014 uses an Action and 2024 uses a Bonus Action,
that timing difference belongs in the edition-specific content binding, not in duplicate
healing/condition-removal engines.

**Pregen order:** build/reconcile 2014 first, reuse every compatible primitive in 2024,
then implement only genuine 2024 semantic differences.

## When a new universal primitive is allowed

Only after this checklist is all **No**:

- Can an existing condition represent it?
- Can an existing save/check/attack represent it?
- Can existing damage/healing/resource/recharge mechanics represent it?
- Can existing timing/timed-effect lifecycle represent it?
- Can existing targeting/area/movement represent it?
- Can two or more existing primitives be composed to represent it accurately?
- Does an equivalent behavior already exist in a monster or pregen under another name?

If all are No, define the new primitive **state/schema first**, then Python oracle,
browser parity, serialization, lifecycle/reset, focused tests, and family re-audit.

## Batch Definition of Done

A mechanic family is done only when:

- exact source behavior and edition parameters are bound;
- no source-name/class-name/monster-name combat dispatch was added;
- mutable effects live only in combat state;
- Python and browser use the same semantic model;
- the smallest representative sample is proven;
- all equivalent family members are rebound without duplicated engine code;
- generated files are regenerated rather than hand-edited;
- blocker/certification truth is updated;
- one focused verification and one final-head CI pass succeed.

## Read deeper only when needed

Open the detailed authority when this playbook is insufficient:

- rules/product behavior: `docs/IRON_PIT_RULES_CONTRACT.md`
- engine/state architecture: `docs/UNIVERSAL_COMBATANT_ARCHITECTURE.md`
- resolver ordering: `docs/COMBAT_RESOLUTION_PIPELINE.md`
- pregens/content binding: `docs/PREGEN_AND_CONTENT_RULES_CONTRACT.md`
- canonical pregen construction: `docs/CANONICAL_COMBAT_BUILD_POLICY.md`
- current queue/counts: `docs/CURRENT_OPERATING_STATUS.md`

Repository source and permanent tests remain the final implementation truth.
