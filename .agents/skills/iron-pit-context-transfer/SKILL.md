# Iron Pit Context Transfer Skill

## Purpose

Prevent context drift, stale assumptions, and handoff rot between agents/sessions. A context transfer is an evidence-backed reconstruction of current repository truth, not a summary copied from chat memory.

Use this skill:
- at the start of every substantial Iron Pit work session;
- before taking over work from another agent/session;
- before resuming an older branch or PR;
- before claiming a blocker is current;
- before handing work to another agent/session;
- immediately after a merge that materially changes active architecture or lane.

## Authority

Read in this order:
1. `AGENTS.md`
2. `docs/CURRENT_OPERATING_STATUS.md`
3. `docs/IRON_PIT_RULES_CONTRACT.md`
4. `docs/UNIVERSAL_COMBATANT_ARCHITECTURE.md`
5. `docs/PREGEN_AND_CONTENT_RULES_CONTRACT.md`
6. `docs/CANONICAL_COMBAT_BUILD_POLICY.md`
7. current source/runtime/tests on exact `main`
8. exact open PR metadata/diffs/workflow state

Repository truth overrides chat summaries, prior handoff notes, remembered counts, stale PR descriptions, and historical milestone prose.

## Freshness gate

A transfer is INVALID if any of these are unknown or stale:
- exact `main` commit SHA;
- active lane from `CURRENT_OPERATING_STATUS.md`;
- exact head SHA for every active PR;
- exact workflow status for any PR described as tested/green/failing;
- certification counts or READY claims not recomputed from the stated commit;
- blockers copied from a prior transfer without checking whether current code already resolved them.

Never carry CI status across a head change. A new commit invalidates all prior exact-head verification.

Never carry counts across a commit change. Recompute or mark them UNKNOWN.

Never carry a chat-only rule decision as authority. If it affects implementation, first write/reconcile it in the proper repository contract.

## Transfer procedure

### 1. Re-anchor to current main

Record:
- `main_sha`
- latest merged PR/commit message
- current active lane
- classes/rosters already certified according to current repository authority

If an older branch is behind `main`, do not treat its assumptions as current.

### 2. Inventory open work

For each relevant open PR record:
- PR number/title
- base branch and base SHA
- head branch and head SHA
- mergeability
- changed-file scope
- whether it overlaps another active PR
- exact CI/workflow status on that head
- disposition: ACTIVE / BLOCKED / SUPERSEDED / PARKED / NEEDS-REANCHOR

One coherent combat-engine lane at a time. Parallel PRs touching the same universal subsystem must be reconciled before either merges.

### 3. Reconstruct the mechanic state

For the subsystem being touched, identify:
- immutable declarative source data;
- runtime mutable state;
- lifecycle/reset behavior;
- Python oracle resolution point;
- browser production resolution point;
- serializer/generated-artifact path;
- permanent Python/browser tests;
- edition-specific branches or parameters.

Search hero AND monster implementations for semantic equivalents before creating or accepting a new primitive.

### 4. Continuous debt audit

During every tranche, inspect touched code for:
- duplicate rules calculations;
- duplicate slot/resource selection;
- source-name/class-name/monster-name dispatch;
- schema/runtime object misuse;
- Python/browser divergence;
- 2014/2024 leakage;
- hand-edited generated artifacts;
- stale compatibility paths that now duplicate a universal primitive;
- obsolete tests asserting superseded behavior;
- certified source values that disagree with RAW/source data;
- old branches whose useful work has already landed elsewhere.

Classify findings:
- **A / FIX NOW** — can change combat outcome, certification truth, state integrity, edition isolation, or parity.
- **B / FIX IN TRANCHE** — architecture duplication or migration debt in the touched subsystem.
- **C / PARK** — cosmetic/non-risk cleanup unrelated to current subsystem.

Do not open a new mechanic tranche while an A-class finding in the current touched subsystem remains unresolved.

### 5. Verification truth

Only claim:
- **implemented** when code exists on the stated SHA;
- **tested** when the relevant local/permanent tests ran on that exact code;
- **CI green** when exact-head GitHub Actions completed successfully;
- **certified** when repository certification gates/manifests agree on that exact commit.

Use UNKNOWN instead of guessing.

### 6. Produce the transfer packet

Every transfer packet must use this structure:

```text
IRON PIT CONTEXT TRANSFER
generated_at:
main_sha:
active_lane:

AUTHORITATIVE STATUS
- ...

ACTIVE PRS
- #N | head_sha | disposition | CI | scope

RECENT MERGES
- ...

VERIFIED CERTIFICATION
- commit:
- counts/progress:
- evidence source:

CURRENT SUBSYSTEM
- source data:
- runtime state:
- Python path:
- browser path:
- generated path:
- tests:

OPEN A-CLASS CORRECTNESS DEBT
- ...

OPEN B-CLASS ARCHITECTURE DEBT
- ...

PARKED C-CLASS CLEANUP
- ...

LOCKED RULE/ARCHITECTURE DECISIONS
- repository file + section, not chat-only prose

NEXT EXACT ACTION
- one action only

DO NOT CARRY FORWARD
- stale counts, obsolete blockers, superseded branches, prior-head CI, chat-only decisions
```

### 7. Handoff validation

Before accepting a transfer:
- compare its `main_sha` with current `main`;
- compare every active PR head SHA;
- refetch workflow state;
- re-read `CURRENT_OPERATING_STATUS.md`;
- reject any stale packet and rebuild it from repository truth.

A transfer packet is a cache. The repository is the database.

## Anti-rot rules

- Never append indefinitely to an old handoff. Rebuild from current truth.
- Never preserve historical blockers merely because they appeared in a prior summary.
- Never preserve historical READY/certified counts without exact-commit evidence.
- Never merge a stale stacked branch because it contains useful work; extract/re-anchor the coherent work onto current `main`.
- Never let a corrective branch remain open after its behavior is fully superseded by a newer universal implementation.
- Every discovered correctness debt must become either an immediate fix, a tracked blocker with evidence, or an explicitly superseded item. No silent TODOs.
