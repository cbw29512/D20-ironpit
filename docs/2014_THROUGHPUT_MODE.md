# 2014 Monster Throughput Mode

The 2014 monster-loading work uses a throughput-first development loop until the canonical roster is complete.

## Objective

Increase the runnable roster in batches while preserving source fidelity and universal-engine architecture.

## Iteration loop

1. Run the blocker-yield report and rank unresolved mechanics by immediate monster unlock count.
2. Pick the highest-yield reusable mechanic family.
3. Implement the smallest universal data/policy capability that expresses that family.
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

## Batch target

Prefer mechanics that unlock multiple monsters. A one-monster edge case must not stall a larger blocker family.
