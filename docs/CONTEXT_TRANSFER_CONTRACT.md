# Context Transfer Contract

Iron Pit context transfers are disposable, evidence-backed snapshots. They are not repository authority.

## Non-negotiable

A transfer must be reconstructed from current repository state whenever its recorded `main` SHA or any active PR head SHA changes.

The transfer process is defined in:

`.agents/skills/iron-pit-context-transfer/SKILL.md`

## Required use

Run the context-transfer skill:
- before substantial work begins;
- when switching agents/sessions;
- before resuming stale work;
- after material merges;
- before handing off unfinished work.

## Drift prevention

The transfer must never elevate these to current truth without re-verification:
- chat summaries;
- remembered certification counts;
- prior-head CI;
- stale PR descriptions;
- old blockers;
- historical branch assumptions.

Current contracts, exact source, exact tests, current PR metadata, and exact-head CI are authoritative.

## Continuous cleanup rule

Context transfer is paired with continuous technical-debt auditing. New work must audit the subsystem it touches and repair correctness/parity/schema debt as part of the tranche rather than deferring it until the project becomes difficult to reason about.
