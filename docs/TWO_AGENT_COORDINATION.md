# Iron Pit Two-Agent Coordination Contract

Purpose: allow Chris to run two assistants on Iron Pit concurrently without duplicated work, conflicting branches, stale assumptions, or overlapping engine edits.

This file governs multi-agent coordination only. It does not override combat rules, architecture contracts, certification rules, or current repository truth.

## 1. Repository truth first

Before any agent starts work:

1. Fetch current `main`.
2. Read:
   - `AGENTS.md`
   - `docs/CURRENT_OPERATING_STATUS.md`
   - `docs/IRON_PIT_RULES_CONTRACT.md`
   - `docs/UNIVERSAL_COMBATANT_ARCHITECTURE.md`
   - `docs/PREGEN_AND_CONTENT_RULES_CONTRACT.md`
   - `docs/CANONICAL_COMBAT_BUILD_POLICY.md`
3. List open PRs and inspect their touched subsystem.
4. Never rely on remembered counts, chat summaries, or stale PR descriptions.

## 2. One subsystem owner at a time

Each active combat subsystem has exactly one owner.

Examples of subsystems:
- attacks / attack roll hooks;
- saves / checks;
- damage / defenses / healing;
- conditions / buffs / debuffs;
- movement / geometry / Opportunity Attacks;
- resources / action economy / recharge;
- reactions / interrupts / timing;
- hero progression for one class;
- monster capability family;
- browser battlefield UI.

If another agent owns a subsystem, do not edit it until ownership is released or Chris explicitly reassigns it.

Read-only auditing is allowed across subsystems. Writing is not.

## 3. Ownership is explicit, never assigned by assistant name

Do not assume Grok, ChatGPT, or another assistant owns combat, art, audits or certification. The current, recorded branch/PR ownership declaration controls. If no current declaration exists, inspect open PR files and handoff evidence before changing that subsystem. Read-only audits may run concurrently; overlapping writers may not.

## 4. Required ownership declaration

Before making code changes, record:

- agent;
- branch;
- PR or issue;
- subsystem;
- exact starting `main` SHA;
- files expected to change;
- status: ACTIVE / PAUSED / HANDOFF / DONE.

A branch without a current ownership declaration must be treated as unsafe to extend.

## 5. Collision gate

STOP before editing when any of these are true:

- another active PR touches the same subsystem;
- another agent is already modifying the same production file;
- the branch is behind a material engine merge;
- the current main SHA differs from the SHA used for the prior handoff;
- the same mechanic is being implemented independently in two branches;
- a stale PR appears to contain similar work but has not been reconciled against current main.

Do not solve collisions by blindly rebasing both branches.

First determine which implementation reflects current architecture, then keep one coherent path.

## 6. Branch rules

Use fresh branches from current `main`.

Recommended prefixes:
- `feat/` — new supported combat behavior;
- `fix/` — correctness/parity repair;
- `audit/` — documentation, status, or audit-only work;
- `refactor/` — behavior-preserving universal-engine cleanup.

Do not revive a stale branch merely because it contains useful historical work.

Extract or reimplement only the still-correct behavior on current main.

### Tranche-size / anti-drift rule

For monster completion, one PR owns **one semantic mechanic family**.

A family may unlock many monsters, but it must share one universal behavior. Do not combine unrelated traits, attack policies, state initialization, generated-data repairs, and engine refactors merely because they were discovered in the same audit.

If a branch needs a second independent primitive family, split it before continuing.

Generated artifacts and count sentinels belong in the same PR only when they are direct outputs of that PR's source changes. Regenerate them from the exact head; never hand-edit generated monster bundles to make a count pass.

A monster tranche is not complete until:
1. source classification/binding is explicit;
2. Python behavior is tested;
3. browser behavior is tested when production execution is affected;
4. generated artifacts are current;
5. 2014 Basic Roster, Paired Edition Monster Report, CI, and 2014 Hero Certification are green on the same exact head.

## 7. Universal mechanic and edition gate

[SOUL.md](../SOUL.md) and the [card-to-combat contract](UNIVERSAL_CARD_COMBAT_CONTRACT.md) own the semantic decomposition, source-neutral dispatch and canonical condition/state rules. One engine, immutable per-edition card parameters, fresh fight state; 2014 before 2024 source binding. This document owns **collisions and handoffs**, not another copy of the engine specification.

## 10. Handoff packet

Before releasing a subsystem, post a handoff containing:

- exact branch/head SHA;
- current main SHA;
- subsystem owned;
- files changed;
- mechanics added or changed;
- Python resolution point;
- browser resolution point;
- generated-data path;
- tests run;
- CI status;
- open blockers;
- known debt;
- next exact action;
- explicit statement that ownership is released.

The receiving agent must revalidate the packet against current main before writing.

## 11. Merge protocol

Before merge:

1. Re-fetch current main.
2. Confirm no newer overlapping PR landed.
3. Confirm exact-head CI.
4. Confirm generated artifacts are generator-owned and current.
5. Confirm Python/browser parity.
6. Confirm no A-class correctness issue remains in the touched subsystem.
7. Merge one coherent implementation.
8. Close superseded branches/PRs.
9. Rebuild the context-transfer packet.

Never carry prior-head CI across a changed head SHA.

## 12. Audit finding protocol

A read-only auditor may inspect any subsystem.

If an A-class issue is found:
- open a narrowly scoped issue;
- cite current-main evidence;
- classify the mechanic semantically;
- describe the required universal behavior;
- identify historical PRs only as evidence;
- do not merge stale historical branches;
- do not start implementation if another agent owns the subsystem.

## 13. Freshness of historical coordination records

The baseline after PR #624 was a historical snapshot, not a current owner or admission count. Recover it from [the prior revision](https://github.com/cbw29512/D20-ironpit/blob/ea26502eca9a4e38a11460b5da36b3482f23ab33/docs/TWO_AGENT_COORDINATION.md) if needed. Never use an old assigned assistant, starting SHA, or roster total to authorize edits today.

Before every write: re-fetch main, inspect existing PR file overlap, declare the subsystem owner, and preserve exact-head certification. After merge: release ownership, close duplicates, regenerate current evidence and resume the single implementation queue.
