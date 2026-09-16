# 2014 Monster Throughput Mode

## Reconciliation status — authoritative operating gate

The existing `beta/2014-playtest` lineage is valuable candidate implementation work, but it predates the hard-edition-isolation contract now carried in `docs/IRON_PIT_HOMEBREW_RULESET_CONTRACT.md`.

Until the lineage is reconciled through `reconcile/2014-ruleset-isolation`:

- Do **not** add new shared-engine behavior directly to `beta/2014-playtest` or descendant `feat/2014-*` / `fix/2014-*` branches.
- 2014-specific source data, catalog corrections, generated ledger refreshes, and ruleset-scoped regression tests may be preserved, but they are candidate assets rather than merge authority.
- Never merge the beta lineage wholesale into `main`.
- Shared-engine changes from the beta lineage must be reviewed and ported individually only when they are universal or explicitly parameterized by the selected ruleset profile.
- The existing 2014 catalog should be reused where it satisfies the new contract. Do not rebuild equivalent source conversion work from scratch.
- The required thin slice is a **reconciliation/acceptance gate**, not a second independent 2014 implementation. Prove representative existing 2014 content against the new ruleset boundary first, then admit the remaining catalog in audited batches.
- Current `main` contracts and current exact-head tests win over older branch assumptions.

The 2014 monster-loading work otherwise uses a throughput-first development loop once the relevant tranche has passed the reconciliation gate.

## Objective

Increase the runnable roster in batches while preserving source fidelity, universal-engine architecture, and hard edition isolation.

## Iteration loop

1. Run the blocker-yield report and rank unresolved mechanics by immediate monster unlock count.
2. Pick the highest-yield reusable mechanic family.
3. Implement the smallest universal data/policy capability that expresses that family on the reconciliation branch/current main architecture.
4. Run only the parser/unit/browser tests directly related to the changed mechanic while iterating.
5. Re-run the blocker-yield report and continue the same family while it is still producing useful roster gains.
6. If an individual monster has an isolated edge case, leave that monster fail-closed and move to the next monster in the family.
7. Run the full 327-monster source-fidelity, Python, browser-parity, generated-artifact, and general CI sweep only at a certification milestone.

## Non-negotiable guards

- No monster-name-specific combat branches when a reusable mechanic can represent the behavior.
- Unsupported outcome-changing mechanics remain fail-closed.
- Source fidelity remains exact.
- Python/browser parity remains required for certification.
- Production source files remain at or below 150 lines.
- A roster number is called certified only after the milestone full sweep is green.
- 2014 and 2024 content/options never mix in one fight or one ruleset-specific builder/catalog.

## Batch target

Prefer mechanics that unlock multiple monsters. A one-monster edge case must not stall a larger blocker family.
