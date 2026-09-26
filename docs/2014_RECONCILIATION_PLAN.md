# 2014 Ruleset Reconciliation Plan

Status: active.

This plan resolves the divergence between the current hard-edition-isolation architecture on `main` and the large pre-existing `beta/2014-playtest` / `feat/2014-*` / `fix/2014-*` lineage.

## Decision

Use **reuse-by-reconciliation**.

- Do not discard the existing 2014 catalog, parsers, tests, or certification work.
- Do not merge the 2014 beta lineage wholesale into `main`.
- Do not rebuild equivalent 2014 source-conversion work from scratch when the existing implementation can satisfy the current contracts.
- Treat `beta/2014-playtest` as candidate source material. Current `main` contracts, current universal-engine architecture, and exact-head verification are merge authority.
- The thin slice required by the newer architecture is an acceptance gate over existing 2014 work, not a competing second 2014 implementation.

## Known compatible evidence

The existing 2014 compiler already creates ruleset-identified combatants (`ruleset="2014"`) and uses 2014-prefixed IDs and 2014-scoped content modules. Preserve that separation where it survives the current contracts.

This evidence is promising but does not certify the branch because the beta lineage also contains extensive shared-engine changes made before the hard-isolation contract.

## Reconciliation branch

Perform reconciliation on:

`reconcile/2014-ruleset-isolation`

Base it on current `main`. Port candidate 2014 work into this branch in audited tranches. Do not make the beta lineage the base of the reconciliation branch.

## Admission classes

### A. 2014 source/catalog/data

Preferred for reuse when all are true:

- source provenance is 2014-specific;
- every runtime combatant has explicit `ruleset="2014"` identity;
- identifiers cannot collide with 2024 content;
- unsupported outcome-changing mechanics still fail closed;
- generated certification remains ruleset-specific;
- no 2024-only source text or option catalog is used as runtime data.

### B. 2014-specific adapters and policy data

Reusable when they configure universal mechanics without creating a second combat engine. Edition-specific semantics must be explicit data/policy selected by the active ruleset profile.

### C. Shared engine changes from the beta lineage

Never import automatically. Review one mechanic family at a time.

A shared-engine change is admissible only when it is:

- genuinely universal, or explicitly parameterized by ruleset;
- free of monster-name/class-name dispatch;
- compatible with current immutable-source/fresh-runtime-state rules;
- implemented in Python and browser runtime with parity;
- audit-log complete;
- covered by permanent regressions;
- compatible with Step, Watch, Replay, and Turbo through the same resolver.

If current main already has an equivalent or newer primitive, keep main and port only missing data/tests.

### D. Generated artifacts

Never hand-port generated outputs as authority. Recreate them from admitted source/schema/runtime code using current exporters.

## Required edition-isolation gates

Before expanding beyond the representative slice, prove all of the following:

1. A fight cannot contain both 2014 and 2024 combatants.
2. 2014 selectors/registries/builders expose only 2014 monsters, pregens, spells, equipment, features, conditions, and homebrew options.
3. 2024 selectors/registries/builders expose only 2024 equivalents.
4. Saved/imported content retains ruleset identity and is revalidated against that same profile.
5. Ruleset-specific certification manifests/ledgers cannot promote content from the other edition.
6. Shared primitives receive edition-specific semantics through the selected profile rather than edition-name branches scattered through the resolver.
7. Browser production combat and Python reference behavior agree for the same selected ruleset.

Any failure blocks further bulk admission until corrected.

## Representative acceptance slice

Use existing 2014 records to prove the architecture across mechanic families. The slice should include, at minimum:

- a simple melee/ranged attacker;
- Multiattack;
- a saving-throw action/condition rider;
- Recharge;
- spellcasting;
- a reaction;
- an area effect;
- a legendary-action/resource example.

The purpose is architectural coverage, not re-authoring these monsters. Once the slice passes the isolation gates and exact-head CI, admit the remaining 2014 catalog in batches grouped by shared mechanic dependency.

## Bulk admission sequence

1. Import/validate 2014 source schema and catalog data.
2. Reuse 2014-scoped parsers/adapters that need no shared-engine change.
3. Run the representative isolation slice.
4. Reconcile shared-engine mechanic families one at a time, preferring current-main implementations when equivalent.
5. Regenerate 2014-specific artifacts from current code.
6. Run the full 327-monster 2014 verification/certification suite plus canonical main CI.
7. Only after those gates pass may 2014 be described as production-ready.

## Coordination rule

While reconciliation is active, new 2014 work that requires a shared-engine change belongs on the reconciliation/current-main architecture, not on the old beta lineage. The beta lineage may preserve ruleset-specific source/catalog/test corrections, but it is not allowed to silently define new universal engine behavior.

## Cross-edition pregen build strategy

This is the default workflow for canonical pregens going forward.

1. **Finish the entire 2014 canonical pregen set first.** Complete and certify all 12 canonical classes through levels 1–20 (240/240 level-slots) before beginning any new 2024 pregen expansion. Existing already-merged 2024 work is preserved, but 2024 is not the active build lane until the 2014 set is complete and re-audited.
2. **Map every 2014 combat feature to the universal engine.** If the mechanic is edition-agnostic in behavior (for example attack rolls, saving throws, resistance, advantage/disadvantage, Sneak Attack, Extra Attack, Evasion, Uncanny Dodge, healing, conditions, rerolls, spell slots, reactions, resource use, or timed effects), implement or reuse one generic engine primitive.
3. **Do not duplicate compatible mechanics in 2024.** When the 2024 version uses the same combat behavior, reuse the same engine primitive and change only ruleset data, parameters, scaling, availability, naming, or resource counts as required by the 2024 rules.
4. **Implement only true 2024 deltas after the compatible 2014 behavior is mapped.** New 2024-only abilities or materially changed semantics get the smallest ruleset-specific extension necessary. Avoid parallel class-specific combat engines.
5. **Prefer data over identity checks.** Shared mechanics must be driven by declarative fields/capabilities rather than class names, character names, monster names, or edition-name conditionals scattered through resolvers.
6. **Use overlap to accelerate both pregens and monsters.** A universal capability added for a pregen should be reused by monsters whenever their underlying combat behavior is equivalent, and vice versa.
7. **Preserve edition isolation at the content layer.** 2014 and 2024 source data, legal options, progression choices, and certification remain ruleset-specific even when they invoke the same universal runtime primitive.
8. **Certify in global edition sequence.** First finish all 12 2014 classes through level 20, run the complete 2014 pregen/universal-engine re-audit, and reach the 240/240 certification gate. Only then begin the 2024 migration pass across the 12 classes, reusing compatible universal mechanics and adding only true 2024 differences before regenerating artifacts and running Python/browser parity plus full CI.
9. **Never rebuild working mechanics from scratch merely because the edition changed.** Reconcile and reuse first; rewrite only when semantics actually differ or the old implementation violates current engine contracts.

### Canonical combat resolution refactor

All current and future 2014 work follows the repository-wide `checks -> modifiers -> result -> state update -> audit event` model defined in `docs/COMBAT_RESOLUTION_PIPELINE.md`.

For each combat feature:

1. identify the shared check it modifies;
2. encode source-specific facts as declarative data;
3. let the shared resolver produce the result;
4. preserve the printed source name only as presentation/audit metadata;
5. reject class-, subclass-, spell-, item-, monster-, or feature-name dispatch when semantic state can express the rule;
6. when a touched shared subsystem still contains source-specific branches, migrate mechanically equivalent behavior into the universal check/modifier pipeline as part of that tranche;
7. keep Python/browser parity and exact-head generated-artifact parity mandatory.

The active Druid lane is the first explicit enforcement example: Nature's Ward must bind poison, disease, Charmed, and Frightened protections into existing damage/debuff/condition checks rather than adding a Druid-specific resolver.

Migration status for this rule:

- **Bound now:** 2014 Land Druid Nature's Ward uses typed damage immunity, generic debuff counters, and source-typed condition immunity.
- **Cleaned now:** the shared condition-immunity resolver no longer recognizes the literal `protection-from-poison` source id; poison protection must arrive through semantic immunity/counter state.
- **Retained semantic rule:** Petrified may block Poisoned because Petrified is itself combat state, not a feature/display-name dispatch.
- **Next legacy migration:** Mindless Rage still has an active-Rage condition-immunity branch. Move that behavior to a reusable effect-conditional modifier binding when the Rage tranche is next touched; preserve edition-specific removal/suppression behavior and prove Python/browser parity before deleting the branch.

### Practical global workflow

The canonical pregen program is executed in this order:

`12 complete 2014 classes (levels 1–20) → 240/240 2014 certification → full 2014 pregen + universal-engine re-audit → shared mechanic inventory → 12-class 2024 migration → compatible universal carryover → 2024-only deltas → 2024 certification`

Within the later 2024 migration pass, each class should reuse the certified 2014 mechanic inventory wherever the underlying combat behavior is equivalent.

The goal is one universal Iron Pit combat engine with two ruleset data layers, not two independently implemented games.
