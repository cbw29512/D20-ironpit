# Iron Pit context transfer — evidence-backed handoff

Use this skill at the start of substantial work, after material merges, when changing agents, before resuming an old PR, and before handing off a subsystem. A transfer is a **cache**, not the authoritative combat spec or another monster queue.

## Minimum source reads

1. [SOUL](../../../SOUL.md), [execution manual](../../../docs/IRON_PIT_IMPLEMENTATION_PLAYBOOK.md), and **one** task guide: Monsters, Pregens or Universal Engine.
2. Fetch the **exact latest main SHA**, current [generated blockers](../../../docs/MONSTER_BLOCKERS_2014.md) and [universal inventory](../../../docs/UNIVERSAL_MECHANIC_INVENTORY.md). Only read deep rules contracts when relevant.
3. Read current [monster ability queue](../../../docs/MONSTER_ABILITY_WORK_QUEUE.md) when the task concerns monsters; locate its approved decision and next **unfinished implementation**, not the first dated row.
4. Fetch the current open PR list, heads, changed-file scopes and exact-head workflow outcomes. No assumed agent/branch ownership; follow [coordination](../../../docs/TWO_AGENT_COORDINATION.md).

## Freshness and collision checks

- A changed main SHA, PR head SHA or changed source/generated data invalidates old counts and prior test claims. Rebuild the packet.
- Before writing, declare the owner/branch/subsystem/files and check whether another PR owns the same files or semantic family. Read-only audit is safe; concurrent edits are not.
- Distinguish source admission, actual implemented runtime code, completed focused tests, exact-head required CI and independent runtime certification.
- Do not import old message summaries, stale PR descriptions, fixed dates, guessed counts or printed ability names as behavior dispatch.
- Record immutable source parameters, per-fight temporary state/reset, Python resolver, browser resolver, generated serializer, test paths and outstanding RAW ambiguity.

## Debt classification

- **A / fix before further work:** outcome changes, wrong source parameters, Python/browser parity, state lifecycle, edition isolation, or false certification.
- **B / fix in current semantic family:** duplicate resolver, redundant computation, unused compatibility path or inappropriate name dispatch in touched files.
- **C / park:** old prose, obsolete presentation and cosmetic cleanup unrelated to the selected family.

If a single monster is blocked by unknown RAW, record the precise gap and continue other independent family work without guessing.

## Transfer packet

```text
IRON PIT — HANDOFF (NOT A LIVE QUEUE)
recorded_at:
main_sha:
branch + head_sha:
subsystem_owner + disposition:
active_family + source_card/edition:
printed_ability + approved_decision_reference:
immutable_source_schema:
mutable_fight_state + reset:
python_resolution_point:
browser_resolution_point:
serializer/generated_artifacts:
tests + exact_head_ci:
before/after admitted + unresolved obligations (or UNKNOWN):
open_A / open_B / parked_C:
next_exact_action:
ownership_released:
```

Never append a fresh status to an old snapshot. Rebuild from current repository facts, and use the canonical queue to track actual monster progress. See the [context transfer contract](../../../docs/CONTEXT_TRANSFER_CONTRACT.md).
