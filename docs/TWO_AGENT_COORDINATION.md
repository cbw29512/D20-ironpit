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

## 3. Default agent split

Unless Chris assigns otherwise:

### Grok
Owns:
- active combat/content implementation;
- the current feature PR;
- code/tests directly required by that feature;
- exact-head certification for that tranche.

### ChatGPT
Owns:
- repository-state audits;
- current-main correctness review;
- stale PR cleanup;
- operating-status/documentation truth;
- identifying universal-engine defects;
- opening narrowly scoped issues for defects found;
- non-overlapping implementation only when no active owner holds that subsystem.

Either agent may switch roles after an explicit handoff.

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

## 7. Universal-mechanic gate

Before implementing any class, subclass, feat, spell, item, monster, legendary action, reaction, trait, or combat ability:

1. Ignore the printed source name.
2. Describe the actual mechanical behavior.
3. Decompose it into:
   - trigger/timing;
   - action/resource cost;
   - attack/check/save;
   - damage/healing;
   - condition/state change;
   - duration;
   - range/geometry;
   - movement;
   - recharge/use limit;
   - lifecycle/reset.
4. Search hero and monster implementations for equivalent mechanics.
5. Reuse existing primitives when behavior matches.
6. Parameterize source differences.
7. Compose multi-effect abilities from existing primitives.
8. Add a new universal primitive only when existing mechanics cannot represent the behavior accurately.
9. Preserve the printed source ability name for UI/log/audit evidence.

A different ability name is never enough reason for a new resolver.

## 8. State identity rule

Universal state identity is absolute.

- Prone is Prone.
- Grappled is Grappled.
- Restrained is Restrained.
- Blinded is Blinded.
- Charmed is Charmed.
- Frightened is Frightened.
- Poisoned is Poisoned.
- Advantage is Advantage.
- Disadvantage is Disadvantage.
- Resistance is Resistance.
- A saving throw is a saving throw.

Source data supplies parameters. The engine supplies behavior.

## 9. Cross-edition rule

2014 and 2024 source data remain isolated.

Reuse one engine primitive only when the actual mechanics are equivalent.

Never copy same-name spell/feature behavior across editions without source-equivalence evidence.

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

## 13. Current coordination snapshot

At the time this contract was introduced:

- current audited main: `1676a9a3bf8ba41e6c845561f027abc8217e3346`;
- 2014 pregens: 240/240;
- 2024 pregens: 240/240;
- 2024 monsters: 140/330;
- Grok owns active combat/content work in PR #530;
- ChatGPT owns audit/repository-hygiene work in PR #531;
- Issue #532 records the current-main 2014 Flyby / Opportunity Attack defect;
- Netlify production publishing remains manual/locked.

This snapshot becomes stale whenever main changes. Rebuild ownership and status from repository truth rather than copying it forward.
