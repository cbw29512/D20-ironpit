# Current operating status

Updated 2026-10-12. Latest merged whole-monster promotion: Invisible Stalker [PR #754](https://github.com/cbw29512/D20-ironpit/pull/754), squash `9909139c12b0bdf690a9c312c7b28933a90fa4e2`. All five checks succeeded on exact PR head `518449075869c77140cc7c965af145b9c5e23ab6`. Production Netlify remains locked.

**AUTHORITATIVE CURRENT CURSOR:** [2014 monster ability work queue](MONSTER_ABILITY_WORK_QUEUE.md). **GENERATOR-OWNED REMAINING BLOCKERS:** [2014 blocker list](MONSTER_BLOCKERS_2014.md). **MECHANIC LOOKUP:** [universal inventory](UNIVERSAL_MECHANIC_INVENTORY.md). Older PR titles, this file's dated snapshots, and chat memories are not certified evidence.

## Verified source classification

- **2014 source-admitted: 210/327; blocked: 117** on the current `main` generated source report. Previous baseline was 209/327; Grimlock Blind Senses now source-bound and merged (#755).
- These figures are source-classifier admission, **not** a claim of independent runtime certification for all 327 cards. PR #755's exact-head Python/browser/2014 Basic Roster/Hero/Paired Edition/artifact sync passed before merge. Recompute from current main when it advances.
- Pregens remain outside the active 2014-monster lane. Prior baselines: 240/240 canonical heroes each edition and 141/330 native 2024 monster public-ready; these are not newly re-certified by this doc edit.
- Earlier core 2014 fixes (Bugbear #751, Black Pudding #749/#750, Bearded Devil #746/#748, Chain grapple #752, Steadfast #745) are merged. Do **not** reimplement them from stale task notes.

## Immediate execution order

1. **Move complete 2014 monsters into source admission.** Filter current generated blocker report for monsters with one remaining blocker; select the smallest reusable semantic family that can remove an entire monster's blocker set. A PR that merely checks off a trait with no roster movement must have cross-monster primitive reuse value.
2. **NEXT whole-monster source candidate: Barbed Devil, Barbed Hide ([issue #688](https://github.com/cbw29512/D20-ironpit/issues/688)).** Only `source:trait` remains in generated blockers. Source reads: at the start of the devil's own turn, every living creature currently grappling the devil takes 1d10 Piercing; no Action/Reaction/save. Bind source-specific parameters into a universal source-turn-to-current-grappler damage capability, reuse existing grapple-source relationships and typed-damage/HP event path; 2014 differs from 2024, so preserve edition isolation. Test 0/1/multiple grapplers, death/release, defenses, parity, and reset. Source Hurl Flame uses already merged universal range semantics; don't redo.
3. Distinct parked Chain Devil blockers are Animate Chains #699 (absent unattended-chain objects in standard arena) and Unnerving Mask #700 (start-of-target-turn reaction). Chain #698 is **done**. The issue queue already contains decisions; do not re-ask.
4. For each family: exact source -> semantic reuse from heroes and monsters -> define immutable schema/mutable fight state -> Python oracle -> browser parity -> focused tests -> regenerate source-owned artifacts -> full exact-head gates -> merge -> re-audit 2014 + 2024 reuse -> update **same** queue. Preserve printed source ability names in logs, not dispatch keys.
5. Prefer a single final-head CI suite after targeted checks and generated artifacts. Existing roster count assertions remain strict and must match the new canonical source roster; do not weaken checks to increase totals.

## Anti-drift / product rules

- The browser is the live combat engine, Python its parity/certification reference. Cards are immutable. Effects mutate only live fight state and reset at match end.
- Reuse universal Prone, Grappled, Invisible, Frightened, saving throws, damage, advantage/resistance and all other primitives. Source cards supply exact values and named log attribution. No monster/ability-name combat routing.
- All source-affecting changes are 2014-first, then inspect equivalent 2024 source without copying source parameters.
- No lair actions, separate summoned entities, ethereal/incorporeal escape, invented terrain, or Netlify publishing from development runs.
- Do not promote a monster with an unsupported outcome-changing source action merely to increment counts. Resolve or explicitly park the named semantic blocker and move to another monster.

## Verification truth

Use current exact-commit evidence: **implemented** means current code exists, **tested** means tests ran on that SHA, **CI green** means all exact-head jobs passed, **certified** requires independent generated source/manifest and Python/browser gates. This doc can become stale; regenerators/source reports outrank it.
