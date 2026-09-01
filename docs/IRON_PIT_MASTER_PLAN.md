# D20 Iron Pit master program

This document is durable program memory for finite Codex goals. Machine-readable status lives in `data/hero_certification_manifest.json` and `data/monster_certification_manifest.json`; calculate current totals with `python scripts/report_certification_progress.py` rather than editing totals here.

## Authority and constraints

1. Repository source, audits, generated artifacts, and permanent tests are authoritative.
2. `AGENTS.md` contains permanent RAW, arena, CI, Git, and hosting rules.
3. PR #32 stays draft and unmerged. Its base remains `feat/browser-combat-engine` unless the user explicitly changes it.
4. Unsupported outcome-changing mechanics remain fail-closed.
5. Netlify is reserved for deliberate release/checkpoint hosting validation.
6. Production monster onboarding is data-first through the Universal Combat Capability registry; bespoke monster builders are migration/parity oracles, not the production roster source.

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

### Capability registry

`backend/app/content/data/combatant_capabilities_v1.json` is the generated legacy compatibility snapshot. Native data-first additions live in `backend/app/content/data/native_combatant_capabilities_v1.json`. `backend/app/content/capability_registry.py` merges those layers with duplicate-ID fail-closed protection and compiles definitions into the same `CombatantTemplate` runtime used by Python and browser export. `backend/app/content/legacy_monster_roster.py` exists only as a migration/parity oracle. `scripts/export_runtime_monster_capabilities.py --check` and permanent CI prevent generated-registry drift or a return to production `monster_*`/`monsters_*` builder imports.

### Commands

```text
python scripts/prepare_static_site.py
python scripts/export_runtime_monster_capabilities.py --check
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
- The generated manifests establish exact current hero and monster certification counts. Use the report command as authority.
- Netlify was not invoked and is not required for routine development certification.

## Fighter 5 / Champion checkpoint

Karnok Stoneward is promoted through Fighter 5 using finite, fail-closed progression snapshots.

Certified progression behavior includes:

- Fighter 1 baseline, Fighter 2 Action Surge/Tactical Mind, Fighter 3 Champion behavior, and Fighter 4 explicit Ability Score Improvement inheritance;
- Champion Improved Critical at 19-20 without turning a natural 19 into an automatic hit;
- Remarkable Athlete Initiative Advantage and Athletics Advantage;
- post-critical half-Speed closing that does not provoke Opportunity Attacks and is not used to kite or retreat;
- Fighter 4 split advancement of +1 Strength and +1 Constitution, producing Strength 18 and Constitution 16;
- Fighter 5 proficiency-bonus scaling to +3, producing 49 HP, Greatsword +7 to hit / +4 damage, Shortbow +4 / +1, Strength save +7, Constitution save +6, and Athletics +7;
- Fighter 5 Extra Attack represented by the generic two-slot Attack action; Action Surge reuses the same Attack action and therefore grants another two attacks rather than a special-cased Fighter path;
- Fighter 5 Tactical Shift: activating Second Wind with a Bonus Action can provide up to half-Speed extra movement. Iron Pit AI uses that movement only to close toward the nearest enemy, does not spend normal movement, and does not provoke Opportunity Attacks. Effective Speed 0 correctly yields no Tactical Shift movement;
- three Second Wind uses, one Action Surge, three Adrenaline Rush uses, and one Relentless Endurance use at the certified level-5 snapshot;
- four selected Weapon Masteries: Flail, Javelin, Spear, and Longsword. The standard Greatsword/Shortbow arena loadout intentionally does not invoke unsupported selected mastery effects;
- structural build audit, combat fingerprint audit, resource audit, public readiness, generated browser-card parity, deterministic Python behavior, and generated-card browser behavior.

Permanent browser certification loads the real generated Fighter 5 card and checks Second Wind `1d10+5`, 15-foot Tactical Shift, no Opportunity Attack/reaction spend, no normal-movement spend, speed-zero denial, two normal Attack-action attacks, and two additional Action Surge attacks.

Exact-head permanent CI run 2775 on `3e9c703361d40b905da82759967d4e38b61686e4` passed all production gates with 423 Python tests. The generated status report at that checkpoint was Fighter 5/20, 6/240 certified hero snapshots, and 99/330 certified monsters.

Do not regress this checkpoint by weakening generated-static parity, capability-registry parity, source audits, or by adding a mastery/feature effect that the runtime and browser paths do not actually support.

## Universal Combat Capability Engine v1 checkpoint

Production monsters now follow:

`declarative combat data -> universal capability compiler -> CombatantTemplate -> Python/browser runtime`

The compatibility path is also preserved:

`legacy runtime template -> capability definition -> compiler -> equivalent template`

The entire migrated runtime monster corpus is used as the compatibility oracle. Tests require legacy-order semantic equivalence and source-audit result parity, so intentionally blocked candidates remain blocked rather than being silently promoted. Production `roster.py` consumes only compiled capability definitions.

The v1 grammar already carries existing runtime structures for attacks, damage, save actions, conditions/control, traits, reactions, resources, Multiattack, movement, defenses, spells, and lifecycle metadata. New shared mechanics should extend this grammar/compiler and browser/Python behavior once, then unlock matching monsters through data rather than adding another production monster builder.

## First native data-only monster checkpoint

The first production monsters added without a bespoke monster builder are:

- Swarm of Insects;
- Swarm of Venomous Snakes.

They live in the native declarative capability layer and reuse existing shared mechanics: Swarm behavior, bloodied replacement damage, movement/defense/source fingerprints, and ordinary on-hit poison damage. Cross-layer duplicate IDs fail closed.

Promotion gate run `33462673589` certified the complete tranche before persistence:

- 429 Python tests passed;
- generated browser monster regression passed with 101 RAW-certified templates;
- browser Swarm HP/Temporary-HP behavior passed;
- certification manifests matched authoritative runtime/source/browser/catalog state;
- generated capability snapshot remained deterministic;
- 102 explicit reviewed figure profiles were exported, covering all 101 RAW-ready monsters plus the intentionally blocked Commoner profile;
- generated progress reported Fighter 5/20, 6/240 certified hero snapshots, Monsters 101/330, Blocked 229.

Promotion persisted as commit `2775103b6fdbf55b469dd2d8ad7090d1a68048c7`. As with every bot-authored promotion commit, it is not a final immutable checkpoint until a subsequent normal connector commit triggers and passes permanent exact-head CI.

Current top monster blocker families after the 101-monster promotion are:

- save-or-complex-action: 122;
- condition-or-control: 115;
- limited-use: 113;
- trait: 111;
- spellcasting: 66;
- bonus-action: 57;
- legendary: 30;
- reaction: 16;
- unsupported-action-rider: 15;
- trait-parse: 10.

## Priority queue

### Goal 1 — High-yield capability blocker tranche

Use the 330-monster blocker analyzer to select a shared mechanic with the largest safe certification yield. Prefer a capability that can be expressed once in schema/compiler/Python/browser and reused across many monsters. Implement source-audit support and deterministic regressions, rerun all 330 records, then certify every newly unlocked monster as one bounded batch. Do not add a bespoke production monster builder to increase the count.

### Goal 2 — Zero-engine/native data tranche

After each shared capability improvement, review monsters whose remaining outcome-changing mechanics are already represented. Onboard those as native declarative definitions only, with full SRD source reconciliation and generated browser parity. Native entries must extend—not reorder or mutate—the generated legacy compatibility snapshot.

### Goal 3 — Certify Karnok Fighter 6

Resume Fighter progression only after the capability-engine tranche reaches a stable exact-head checkpoint. Derive Fighter 6 from the certified Fighter 5 snapshot; source-audit every new level-6 class/subclass/resource/action-economy/scaling rule; preserve Fighter 1-5 behavior; promote only after structural audit, combat/resource fingerprints, generated-card parity, public readiness, permanent regressions, and exact-head CI pass.

### Goal 4 — Continue Karnok in finite progression tranches

Advance through coherent Fighter milestones rather than claiming levels 7-20 at once. Each goal must explicitly cover all new class/subclass/feat/resource/action-economy/scaling rules introduced by its selected level range and preserve all previously certified Fighter levels. Ability-score/feat advancements remain explicit audit data rather than hidden stat mutations.

### Goal 5 — Next canonical hero

After Fighter progression is complete or reaches a genuine prerequisite decision, complete one other canonical hero progression in finite, level-bounded goals. Preserve the one-identity-per-class architecture and derive every level from canonical progression data. Reuse the same declarative capability concepts where they improve hero progression without weakening class-specific source audits.

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
