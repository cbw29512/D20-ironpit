# Iron Pit Context Transfer Skill

## Purpose

This skill prevents long-running Iron Pit work from drifting away from repository truth.

A context transfer is not a narrative summary. It is a reproducible handoff packet tied to exact repository state. Its purpose is to let a new session, agent, or resumed task reconstruct the current engineering truth before changing code.

Chat memory, old progress reports, stale PR descriptions, and remembered counts are never sufficient authority.

## Core anti-rot rule

**No combat work resumes from conversational context alone.**

Before modifying combat code after a handoff, interruption, branch change, merge, long pause, or agent/session change:

1. identify the exact repository, branch, head SHA, base SHA, and active PR;
2. re-read the repository authority files;
3. validate that the handoff packet still matches the current Git state;
4. inspect the current diff and exact-head CI state;
5. reconcile any mismatch before writing code.

If any of those checks fail, the prior context is **STALE** and must be rebuilt from repository truth.

## Authority order during transfer

Read and reconcile these in order:

1. `AGENTS.md`
2. `docs/CURRENT_OPERATING_STATUS.md`
3. `docs/CONTEXT_TRANSFER_SKILL.md`
4. `docs/IRON_PIT_RULES_CONTRACT.md`
5. `docs/VTT_CARD_BATTLEFIELD_CONTRACT.md`
6. `docs/UNIVERSAL_COMBATANT_ARCHITECTURE.md`
7. `docs/ABILITY_HOOK_ENGINE_PROPOSAL.md`
8. `docs/MAIN_ACTION_SELECTION_CONTRACT.md`
9. `docs/PREGEN_AND_CONTENT_RULES_CONTRACT.md`
10. `docs/CANONICAL_COMBAT_BUILD_POLICY.md`
11. current source/runtime code and permanent tests;
12. generated certification manifests and exact-head CI.

A transfer packet may summarize these authorities but may not override them.

## Mandatory transfer packet

Every meaningful handoff must include the following fields.

### 1. Repository identity

- repository full name;
- current `main` SHA;
- active branch;
- active branch head SHA;
- branch base SHA;
- active PR number and title, if any;
- whether the PR is based directly on current `main`;
- whether the branch has changed since the packet was created.

Exact SHAs are mandatory. Words such as "latest", "current", "green", or "almost done" are not enough.

### 2. Active lane

State exactly one active combat lane.

Include:

- class/content/mechanic currently being worked;
- the reason it is the active lane;
- the exact next unit of work;
- lanes that are explicitly forbidden or parked.

If multiple combat PRs touch the same subsystem, that is a drift warning and must be reconciled before additional implementation.

### 3. Verified truth

Record only facts verified against the exact referenced commit.

Examples:

- certified hero progressions;
- certified monster counts;
- generated manifest state;
- supported universal primitives;
- exact rules decisions already written into repository contracts.

Every count must name its source or generation command. Never copy historical counts forward merely because they were true earlier.

### 4. Changed surface

Describe the semantic change, not only filenames.

For the active tranche, record:

- data/schema fields changed;
- mutable state changed;
- lifecycle/timing changed;
- Python resolution points changed;
- browser resolution points changed;
- serializers/exporters changed;
- generated artifacts affected;
- permanent tests added or changed.

This is the parity map for the handoff.

### 5. Verification state

For every required verification, mark one of:

- `PASS <exact SHA>`
- `FAIL <exact SHA> <failure>`
- `RUNNING <exact SHA>`
- `NOT RUN`

At minimum track:

- targeted Python tests;
- full Python rules-reference suite;
- browser syntax;
- browser permanent regressions;
- generated artifact parity;
- hero certification;
- monster/capability reports when affected;
- GitHub Actions CI on the exact intended head.

A green result from an older SHA is stale evidence.

### 6. Blockers and uncertainties

For each unresolved item include:

- the exact blocker;
- whether it is RAW, architecture, schema, parity, CI, data, or generated-artifact related;
- the evidence that exposed it;
- the exact file/test/PR where it lives;
- whether coding may continue around it.

Outcome-changing uncertainty always blocks certification and must not be approximated.

### 7. Technical-debt ledger

Every transfer packet must classify discovered debt into exactly one category.

#### MUST_FIX_NOW

Use when the debt can:

- change combat outcomes;
- violate RAW or an Iron Pit house rule;
- corrupt runtime state;
- create Python/browser disagreement;
- leak rules between 2014 and 2024;
- create duplicate competing universal mechanics;
- falsely certify unsupported content;
- make generated artifacts disagree with source truth.

Do not advance feature work until these items are resolved or explicitly converted into a repository blocker.

#### FIX_WITH_CURRENT_TRANCHE

Use when the issue is in the subsystem currently being changed and leaving it would increase drift, duplication, or fragility, even if current combat outcomes are still correct.

Examples:

- duplicate slot-selection helpers;
- obsolete compatibility branches in the touched path;
- source/runtime schema misuse in tests;
- dead helper paths replaced by the new universal primitive.

#### PARKED_CLEANUP

Use only when the issue cannot currently alter combat truth and is outside the touched subsystem.

Examples:

- cosmetic naming;
- comments;
- harmless file organization;
- speculative refactors with no current consumer.

Parked cleanup must not be allowed to hide outcome-changing debt.

### 8. PR and branch hygiene

Record:

- active PRs that still contain unique required work;
- stale/superseded PRs closed during the tranche;
- stacked PRs that must not be merged directly;
- branches whose useful changes must be re-anchored on current `main`.

Never preserve an open PR merely because it contains historical work. Repository truth and current-main compatibility decide whether it stays alive.

### 9. Exact next action

The packet must end with one concrete next action.

Good:

- "Fix `test_cleric_four_expected_value_uses_inflict_wounds_in_close_combat` on PR #382 after exact-head CI identifies the remaining dice-consumption mismatch."
- "Re-anchor the 2014 Monk level-18 speed correction on current main and run Python/browser level-18 through level-20 regressions."

Bad:

- "Keep going."
- "Finish Cleric."
- "Clean things up."

The next action must be specific enough that a new session can begin without guessing.

## Freshness gate on resume

Before using a transfer packet, perform these checks.

### Check A — exact Git identity

Compare packet values with:

- current `main` SHA;
- active branch head SHA;
- active PR head/base SHA.

If any SHA differs, the packet is stale until reconciled.

A changed SHA does not automatically mean the work is wrong. It means the old packet no longer proves current truth.

### Check B — authority drift

Re-read the authority files.

If an authority file changed since the packet was produced, identify whether the change affects the active subsystem. If it does, re-audit the active implementation before continuing.

### Check C — diff drift

Inspect the current PR diff.

Stop and reconcile if:

- unrelated files appeared;
- another agent/branch modified the same subsystem;
- a PR accumulated work outside its stated scope;
- generated artifacts were hand-edited;
- a second implementation of an existing primitive appeared.

### Check D — CI drift

Verify the exact PR head.

Never say a branch is green because an earlier head passed.

If a commit was pushed after a CI run started, the older run is evidence only for the older SHA.

### Check E — certification drift

Recompute certification truth whenever the touched change can affect:

- roster legality;
- hero behavior;
- monster behavior;
- generated browser data;
- universal capability support.

Never carry a READY count from memory across a mechanic change.

## Context-rot warning signs

Any one of the following requires reconciliation before more combat implementation:

- no exact commit SHA in the handoff;
- active PR head differs from the recorded head;
- active branch is stacked on a stale feature branch without an explicit reason;
- multiple open PRs implement overlapping versions of the same universal behavior;
- a test uses source-definition objects as runtime state;
- Python and browser use separate rules/calculations for equivalent behavior;
- a named class/monster/spell resolver duplicates a universal mechanic;
- a generated artifact was edited instead of regenerated;
- a certification count cannot be reproduced from the exact commit;
- a rules decision exists only in chat;
- a stale PR remains open even though its behavior already landed another way;
- a test was weakened merely to make CI pass;
- a "temporary" compatibility path has become the live authority;
- a certified source value is discovered to be wrong.

## Continuous audit rule

Context transfer is not only for the end of a session.

For every new tranche:

1. read the relevant contracts and existing implementations;
2. audit the touched subsystem before coding;
3. implement the smallest reusable change;
4. audit the touched subsystem again after implementation;
5. fix MUST_FIX_NOW and FIX_WITH_CURRENT_TRANCHE debt before merge;
6. verify Python/browser parity and edition isolation;
7. update or regenerate evidence;
8. close or reconcile stale branches exposed by the work;
9. produce a fresh transfer packet before changing lanes.

This turns technical-debt cleanup into part of normal feature work instead of a future cleanup project.

## Merge gate

A tranche is not merge-ready until all of the following are true:

- exact intended head is known;
- active scope is coherent;
- no unresolved MUST_FIX_NOW debt remains in the touched subsystem;
- no competing implementation of the same universal mechanic remains active;
- Python/browser parity is proven;
- 2014/2024 differences are explicit;
- generated files come from their generators;
- permanent tests cover the changed behavior;
- exact-head CI/certification required by the repo has passed;
- stale/superseded PRs discovered by the tranche are closed or explicitly documented.

## Handoff packet template

```text
IRON PIT CONTEXT TRANSFER

Repository:
Main SHA:
Active branch:
Head SHA:
Base SHA:
Active PR:

ACTIVE LANE
- Current lane:
- Exact next unit:
- Forbidden/parked lanes:

VERIFIED TRUTH @ <SHA>
- Hero certification:
- Monster certification:
- Universal mechanics relevant to this tranche:
- Repository decisions relied upon:

CHANGED SURFACE
- Schema/data:
- Mutable state:
- Python:
- Browser:
- Exporters/generated artifacts:
- Permanent tests:

VERIFICATION
- Targeted Python:
- Full Python:
- Browser syntax:
- Browser regressions:
- Generated parity:
- Hero certification:
- Monster/capability reports:
- Exact-head CI:

BLOCKERS / UNCERTAINTIES
- ...

TECHNICAL DEBT
MUST_FIX_NOW
- ...

FIX_WITH_CURRENT_TRANCHE
- ...

PARKED_CLEANUP
- ...

PR / BRANCH HYGIENE
- Active required PRs:
- Superseded PRs closed:
- Re-anchor required:

EXACT NEXT ACTION
- ...
```

## Final rule

**The transfer packet is a pointer to repository truth, not a replacement for repository truth.**

If the packet and the repository disagree, discard the packet, rebuild context from the repository, and continue only after the mismatch is understood.
