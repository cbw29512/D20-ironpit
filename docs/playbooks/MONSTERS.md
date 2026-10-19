# Monster implementation — 2014 first

**Operational lane only.** The [execution manual](../IRON_PIT_IMPLEMENTATION_PLAYBOOK.md) owns the universal process, [SOUL](../../SOUL.md) owns architecture, [locked rules](../IRON_PIT_LOCKED_RULES.md) own explicit Pit exceptions, and [this queue](../MONSTER_ABILITY_WORK_QUEUE.md) is the **single** source of previously approved monster decisions. This guide owns **monster-specific implementation order and throughput**.

## Pick the next actionable family

**Default is a card-only integration.** Work the [executable card-field → shared-resolver contract](../UNIVERSAL_CARD_COMBAT_CONTRACT.md#executable-card-field--shared-resolver-contract-chris-2026-10-19) in order: card field → compiled capability → Python primitive → browser primitive → regression. Printed attacks with multiple damage types call one to-hit roll and the same typed-damage resolver once per component; Multiattack and Bonus Actions are action scheduling, not new attack algorithms. Do not write a new monster resolver when this path is already implemented.

1. Recheck current `main`, open PR file overlap, and the [generated 2014 blocker list](../MONSTER_BLOCKERS_2014.md), not a dated queue milestone, chat recollection, or the historical 124-monster worksheet.
2. Advance the queue's implementation cursor past decisions already coded/merged and avoid duplicating open PRs. Start with source-approved one-blocker combat monsters and equivalent abilities on multiple cards; exclude `arena:neutral` and `arena:removed` from playable admission.
3. Read the exact 2014 source clauses, source cards, existing monster **and pregen** adapters, [universal inventory](../UNIVERSAL_MECHANIC_INVENTORY.md), Python rules reference, browser runtime and associated tests.
4. Decompose each printed ability: `trigger/timing → eligibility/geometry → Action/Bonus Action/Reaction/resource → roll/save/automatic outcome → ordered typed damage + conditions/buffs/debuffs/movement → expiry/fight reset`.
5. Bind exact numbers and printed names **only on immutable cards**. Reuse the common engine; combine existing primitives before expanding a primitive. Do not add monster-name/ability-name resolvers. Missing outcome-changing semantics stay blocked; park one card and proceed to another independent task.
6. Prove one representative source, then **batch-bind every mechanically equivalent card**. For widened engine behavior, prove an unrelated synthetic/homebrew card can use the same primitive without source-name dispatch.
7. Check focused Python/browser behavior and lifecycle. Remove duplicate logic and imports in touched files; regenerate the relevant source-owned assets and manifests once. All applicable exact-final-head CI checks must pass before merge.
8. Recompute admitted monster IDs **and** unresolved `(monster, printed ability)` obligations from generator outputs. Update only the **existing** queue with verified implementation/PR/merge evidence and pick the next unblocked family.

## What is not completion

- A written RAW decision, issue, PR, foundation helper, a passing source classifier, or a self-described READY card is **not** complete combat certification.
- An unsupported source Action or trait cannot be dropped, guessed, treated as no-op, or name-special-cased merely to grow the roster.
- A fail-closed arena-neutral classification is not a runnable monster.
- A green result on an older head does not certify a newer commit.
- Source numbers/data for 2014 and 2024 must remain isolated; after 2014 binding, inspect 2024 for **semantic** reuse without copying statistics.

## Measure output, not motion

After a **merged and exact-head certified** batch, compare before/after generated universal-inventory data. One resolved obligation is one source-verified `(monster, printed ability)` no longer unresolved. Report gross/newly introduced/net resolved obligations, net new admitted monsters, separately verified runtime certification and actual elapsed hours.

```bash
python scripts/measure_monster_throughput_2014.py --before /tmp/before-inventory.json --after data/universal_mechanic_inventory_v1.json --hours 2.5
```

The `--hours` argument is an example; use measured actual hours, never PR timestamps as a substitute. If admissions and obligations do not change, record **zero**. One clean final-head suite is preferable to repeated full CI runs on unchanged work.

## Examples and authority

A breath Action is a composition of generic recharge, area targeting, saving throws, typed effects, conditions and expiry—not a dragon-specific resolver. A petrification gaze is a source-declared passive trigger, visibility/range/aversion check, saving throw, staged condition and universal terminal Petrified rule—not a monster-name branch.

For actual RAW interpretation use [the detailed rules contract](../IRON_PIT_RULES_CONTRACT.md); for schema/parity extension use the [engine lane](UNIVERSAL_ENGINE.md); for agent collisions use [coordination](../TWO_AGENT_COORDINATION.md). The Pit is hospitable to aquatic biology but creates neither water nor rocky terrain; no invented terrain exceptions or automatic Netlify publish.
