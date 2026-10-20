# Context transfer — freshness contract

A handoff is a disposable **cache**, not a second task queue or authority. It must identify the exact `main` SHA, changed subsystem, PR head SHA, owner, tests, remaining blockers and next executable action.

1. Use the repository [context-transfer skill](../.agents/skills/iron-pit-context-transfer/SKILL.md) before substantial work, agent changes, stale branch resumption and after material merges.
2. Re-fetch main, open PRs and exact-head jobs. Any changed SHA invalidates previous code/test/certification claims. Generated classifier and manifests outrank copied counts; current source/RAW and locked rule contract outrank remembered decisions.
3. State immutable card data, fight-local mutable state, Python/browser resolution points, serializer and permanent tests; confirm the current owner has released the subsystem.
4. List only open **A** correctness/parity risks, **B** touched-architecture duplication, and **C** optional cosmetic debt. Fix A before more combat work; don't let C block the monster lane.
5. Rebuild a fresh transfer packet following the [skill](../.agents/skills/iron-pit-context-transfer/SKILL.md); never append dated claims to an earlier handoff.

The [execution manual](IRON_PIT_IMPLEMENTATION_PLAYBOOK.md) controls implementation. A handoff does not certify combat or authorize a deployment.
