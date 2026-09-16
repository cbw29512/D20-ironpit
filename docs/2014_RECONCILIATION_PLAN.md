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

## Canonical pregen edition contract

This section is mandatory for every Iron Pit pregen now and in future content tooling.

- The persistent named hero and class/subclass concept may be shared across editions, but the actual 2014 and 2024 character builds are separate legal builds.
- A 2014 pregen must be legal under 2014 RAW at every certified level. A 2024 pregen must be legal under 2024 RAW at every certified level.
- Class progression, subclass timing, species/race traits, backgrounds, feats, Ability Score Improvements, spell choices/slots, equipment, weapon rules, resources, action economy, and derived combat statistics come only from the selected edition.
- 2024-only systems such as Weapon Mastery, origin feats, Tactical Mind, Tactical Shift, and Tactical Master must never leak into a 2014 build.
- 2014-only feature wording or parameters must never be grafted onto a 2024 build merely because the class/subclass name matches.
- Shared engine primitives are reused only when the actual rules semantics match. Edition differences are expressed through ruleset-specific source data or policy parameters, not duplicated engines or class-name branches.
- The canonical addition pipeline is: edition source rules -> edition-specific character/profile data -> universal combat primitives -> edition-specific certification -> generated browser artifact -> browser/reference parity tests.
- A pregen is not READY because it parses, renders, or has plausible AC/HP/damage. Every combat-relevant feature through that level must be either correctly implemented and tested or explicitly proven arena-neutral; unsupported outcome-changing mechanics fail closed.
- Certification must reject mixed-edition content, including a 2014 character carrying any 2024-only weapon mastery or feature and a 2024 character carrying legacy-only semantics where the 2024 rule changed.
- The initial testing floor is one canonical class/subclass progression through levels 1-10 in each edition. Expansion continues toward all 12 canonical classes after the cross-edition fight lane is proven.

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
