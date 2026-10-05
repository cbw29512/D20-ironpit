# Current operating status

Recorded 2026-10-04 after the 2024 canonical-pregen completion and website preset publish work.
Main baseline audited: `1676a9a3bf8ba41e6c845561f027abc8217e3346`.

This file is operating authority for **what to work on next**. Combat rules remain authoritative in `docs/IRON_PIT_RULES_CONTRACT.md`. Generated certification manifests and exact current source/tests determine counts and readiness. Repository truth overrides chat summaries and older milestone prose.

## Owner split / collision rule

- Iron Pit remains the only combat-engine lane in this repository.
- Multiple agents may assist only when their work is deliberately non-overlapping.
- The active combat/content worker owns its touched combat subsystem until handoff or merge.
- Audit/documentation/repository-hygiene work may proceed separately when it does not edit the active combat subsystem.
- Never rebase or merge a stale progression PR merely to preserve its history; reconcile useful behavior against current `main` first.

## Verified current certification

Generated authority on the audited main baseline reports:

| Edition | Content | READY / target |
|---|---|---:|
| 2014 | Canonical pregens | **240 / 240** |
| 2024 | Canonical pregens | **240 / 240** |
| 2024 | SRD monsters | **140 / 330** |
| 2014 | Browser monster roster | **130 certified** (per permanent roster assertion) |

### Canonical pregen status

All twelve canonical classes are complete through level 20 in both editions:

- Fighter (Champion)
- Barbarian (Berserker)
- Bard (Lore)
- Cleric (Life)
- Druid (Land)
- Monk (Open Hand)
- Paladin (Devotion)
- Ranger (Hunter)
- Rogue (Thief)
- Sorcerer (Draconic)
- Warlock (Fiend)
- Wizard (Evoker)

Do **not** reopen class-progression work merely because an older PR or chat summary claims a lower certified count.

## Current completion order

Owner-requested order is now:

1. **Audit and test the universal combat engine.**
2. Fix any A-class correctness/parity/edition-isolation debt found by that audit.
3. Use universal engine improvements to unlock the remaining monster catalog in broad semantic batches.
4. Complete paired-edition monster certification and final RAW audit.
5. Finish website visual/design polish after combat correctness and roster work are stable.

Pregens are complete and are no longer the active expansion lane.

## Active work

At the time of this status refresh:

- **PR #530 — Add Load Combat review for purpose-built test fights** is current work based directly on the audited `main` baseline.
- Do not edit the same combat/runtime files from a second branch while #530 is active.
- Separate repository-hygiene/documentation work may proceed without touching its subsystem.

## Universal-engine audit priorities

Audit by semantic mechanic, not by source ability name:

1. **Attacks / saves / checks**
   - legality and targeting;
   - Advantage/Disadvantage;
   - modifiers;
   - DC/AC comparison;
   - result propagation.

2. **Damage / healing**
   - typed components;
   - resistance/immunity/vulnerability;
   - Temporary HP and replacement effects;
   - critical hits;
   - zero-HP transitions.

3. **Conditions / buffs / debuffs**
   - one universal state identity per condition;
   - source-specific parameters only;
   - duration/expiry;
   - immunity/suppression/removal.

4. **Movement / geometry**
   - authoritative grid position;
   - printed movement modes;
   - reach/range/areas;
   - Opportunity Attacks;
   - forced movement and movement debuffs.

5. **Resources / action economy**
   - availability before spending;
   - Action/Bonus Action/Reaction legality;
   - limited-use/recharge resources;
   - reset semantics.

6. **Hooks / reactions / timing**
   - generic timing windows;
   - no class/monster/ability-name resolver switches;
   - deterministic ordering;
   - Python/browser parity.

7. **Edition isolation**
   - explicit 2014 versus 2024 data/fingerprints;
   - same-name features/spells do not imply same behavior.

## Monster lane after engine audit

2024 currently has **190 blocked monster slots**. Work them by shared blocker families rather than one monster at a time. Current recurring blocker classes include:

- legendary actions;
- limited-use/recharge behavior;
- complex save/action effects;
- spellcasting;
- condition/control mechanics;
- trait parsing/binding.

Before adding any primitive, classify each blocker as:

- `ENGINE_EXISTS_BINDING_MISSING`
- `ENGINE_EXISTS_CERTIFICATION_MISSING`
- `ARENA_NEUTRAL`
- `ENGINE_TRULY_MISSING`

Only `ENGINE_TRULY_MISSING` justifies a new universal engine primitive.

## Stale PR policy

Progression PRs whose completed behavior is already present on current `main` are superseded and should be closed, not rebased. Any older universal-engine PR must be re-audited against current source before reuse because its useful behavior may already have landed through a later implementation.

## Publishing

Chris approved a one-shot roster production publish (2026-10-05). Unlock merge is `2292ba324` (#592); relock merge is `0963fff45` (#594). Git-connected ignore is restored. https://ironpit.netlify.app/ is serving production Git deploy `6ac3e995b21bb000098a0bdd` (`main` `2292ba324`) and that deploy is locked. Do not buy or attach `ironpit.app`.

## Verification truth

Only claim:

- **implemented** when code exists on the stated SHA;
- **tested** when relevant permanent tests ran on that exact code;
- **CI green** when exact-head workflows completed successfully;
- **certified** when current generated manifests, runtime data, and certification gates agree.

Never carry counts or CI status across a commit change without re-verification.
