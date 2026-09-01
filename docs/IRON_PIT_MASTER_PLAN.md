# D20 Iron Pit master program

This document is durable program memory for finite Codex goals. Machine-readable status lives in `data/hero_certification_manifest.json` and `data/monster_certification_manifest.json`; calculate current totals with `python scripts/report_certification_progress.py` rather than editing totals here.

## Authority and constraints

1. Repository source, audits, generated artifacts, and permanent tests are authoritative.
2. `AGENTS.md` contains permanent RAW, arena, CI, Git, and hosting rules.
3. PR #32 stays draft and unmerged. Its base remains `feat/browser-combat-engine` unless the user explicitly changes it.
4. Unsupported outcome-changing mechanics remain fail-closed.
5. Netlify is reserved for deliberate release/checkpoint hosting validation.

## Completion model

The master program is complete only when all of these generated, independently verified contracts hold on the same exact commit:

- 12 canonical hero identities exist, one per core class.
- Every hero exposes levels 1-20, for exactly 240 level slots.
- Every public-ready hero level has an audited canonical progression snapshot, runtime template, source references, expected combat-feature coverage, Python certification, browser certification, generated-static parity, and public catalog readiness.
- The canonical SRD 5.2.1 catalog contains exactly 330 unique monsters with source metadata.
- Every public-ready monster reconciles its full outcome-changing stat block to a runtime template, Python behavior, browser behavior, generated assets, and public catalog state.
- Every non-ready hero or monster has explicit machine-readable blockers.
- Python/browser behavioral parity, deterministic regressions, source audits, generated-static parity, source-size limits, backend-free production behavior, arena policy, and exact-head GitHub CI all pass.
- Production UI, figures, and deployment checkpoints are certified without routine Netlify consumption.

## Structured trackers

### Hero manifest

`data/hero_certification_manifest.json` is generated from canonical hero definitions, the public hero catalog, certified runtime entries, audited sources, and the generated browser hero artifact. Each level records identity, subclass where applicable, runtime template, sources, expected/supported/unsupported mechanics, Python/browser/generated/public status, and blockers.

### Monster manifest

`data/monster_certification_manifest.json` is generated from all 330 canonical SRD rows, runtime/source audit readiness, blocker analysis, and the generated browser monster artifact. Each record contains source/page, runtime template candidate, detected/supported/unsupported mechanics, Python/browser/generated/public status, and blockers.

### Commands

```text
python scripts/prepare_static_site.py
python scripts/verify_certification_manifests.py --write
python scripts/verify_certification_manifests.py
python scripts/report_certification_progress.py
```

Never edit generated counts or certification states to make them agree with a desired claim. Change authoritative implementation/audit state, regenerate, and let verification prove the result.

## Verified takeover baseline

Baseline source head before this control-file tranche: `db4fe6bff688827a67b7322e8111b34812611be9` on `audit/raw-combat-log-figures-20260830`.

- GitHub PR #32 was verified open, draft, unmerged, and based on `feat/browser-combat-engine`.
- GitHub Actions CI run 2599 completed successfully on that exact source head.
- Local permanent baseline passed: production source limits, clean generated-static parity, 396 Python tests, JavaScript syntax, and every checked-in browser regression.
- The generated manifests establish the exact current hero and monster certification counts. Use the report command for the values; do not copy them into future task prompts as authority.
- Netlify was not invoked and is not required for routine development certification.

The Codex-readiness commit that adds this plan must receive its own exact-head CI success before it becomes the new certified checkpoint.

## Fighter 4 / Champion checkpoint

Karnok Stoneward is now promoted through Fighter 4 using finite, fail-closed progression snapshots.

Certified progression behavior includes:

- Fighter 1 baseline, Fighter 2 Action Surge/Tactical Mind, and Fighter 3 Champion behavior inherited by later snapshots;
- Champion Improved Critical at 19-20 without turning a natural 19 into an automatic hit;
- Remarkable Athlete Initiative Advantage and Athletics Advantage;
- post-critical half-Speed movement that closes toward the target, does not provoke Opportunity Attacks, and cannot be used to kite or retreat;
- Fighter 4 Ability Score Improvement represented as explicit advancement data rather than mutating background ability increases;
- the selected Fighter 4 split increase of +1 Strength and +1 Constitution, producing Strength 18 and Constitution 16;
- resulting Fighter 4 runtime scaling: 40 HP, Greatsword +6 to hit / +4 damage, Strength save +6, Constitution save +5, Athletics +6, and three Second Wind uses;
- four selected Weapon Masteries at Fighter 4. The fourth selection is Longsword; the standard arena Greatsword/Shortbow loadout intentionally does not invoke unsupported mastery effects;
- structural build audit, combat fingerprint audit, resource audit, deterministic Python tests, public readiness, generated browser-card parity, and browser behavior tests.

A production-parity hole found during Fighter 4 work was also fixed: the generated browser hero exporter had not serialized Champion progression fields. The exporter now carries critical threshold, Initiative Advantage, Athletics Advantage, critical movement fraction, Fighting Style, and Weapon Masteries from the authoritative Python template. A permanent browser regression loads the real generated Fighter 3 and Fighter 4 cards so future generated-data drift is caught rather than hidden by hand-built test fixtures.

Do not regress this checkpoint by weakening generated-static parity or by adding a mastery effect, feat, or progression feature that the runtime/browser paths do not actually support.

## Priority queue

### Goal 1 — Certify Karnok Fighter 5

Stopping condition: derive Fighter 5 from the certified Fighter 4 snapshot; source-audit every new level-5 class/subclass/resource/action-economy/scaling rule; implement Python and browser behavior where outcome-changing; preserve all Fighter 1-4 behavior; promote only after structural audit, combat/resource fingerprints, generated-card parity, public readiness, permanent regressions, and exact-head CI pass.

### Goal 2 — Continue Karnok in finite progression tranches

Advance through coherent Fighter milestones rather than claiming levels 6-20 at once. Each goal must explicitly cover all new class/subclass/feat/resource/action-economy/scaling rules introduced by its selected level range and preserve all previously certified Fighter levels. Ability-score/feat advancements must remain explicit audit data rather than hidden stat mutations.

### Goal 3 — Zero-engine monster tranche

Run the full blocker analyzer, review monsters with no unsupported outcome-changing mechanics, implement only necessary source-derived runtime templates, then certify Python/browser/generated/public parity as a batch.

### Goal 4 — Shared monster capability

Select one high-yield blocker family. Implement exact reusable RAW mechanics in Python and browser engines, add source audits and regressions, rerun all 330 records, and certify every newly unlocked monster. Initial blocker families are reported dynamically; likely high-yield areas include save/complex actions, conditions/control, limited-use/recharge, traits, spellcasting, Bonus Actions, legendary actions, reactions, and attack riders.

### Goal 5 — Next canonical hero

After Fighter progression is complete or reaches a genuine prerequisite decision, complete one other canonical hero progression in finite, level-bounded goals. Preserve the one-identity-per-class architecture and derive every level from canonical progression data.

## Checkpoint record format

For every substantial tranche, record in the commit/PR history and final task report:

- exact commit SHA;
- finite goal and stopping condition;
- certified hero snapshot count and per-class progress from the report script;
- certified/blocked monster counts and top blocker families;
- Python and browser test results;
- generated-static and source-size results;
- GitHub exact-head CI result;
- whether a deliberate hosting checkpoint was run (normally no).

The commit SHA is the immutable checkpoint identifier. Do not create a self-referential SHA inside the commit being identified.
