# D20 Iron Pit repository instructions

Read this file, `docs/IRON_PIT_MVP_SCOPE.md`, `docs/IRON_PIT_MASTER_PLAN.md`, `docs/CANONICAL_COMBAT_BUILD_POLICY.md`, and the structured certification manifests before changing code. The repository and its permanent tests are authoritative; prompts and historical counts are not. Where an older master-plan checkpoint conflicts with a later explicit policy in this file, `docs/IRON_PIT_MVP_SCOPE.md`, or `docs/CANONICAL_COMBAT_BUILD_POLICY.md`, the later explicit policy controls until the master-plan text is reconciled.

## Iron Pit MVP outcome filter — highest priority

- The base engine models only mechanics that can directly change the mathematical outcome of an Iron Pit fight. `docs/IRON_PIT_MVP_SCOPE.md` is authoritative for this filter.
- A mechanic may block MVP readiness only when it changes attack/save/initiative math, AC, damage or damage type, Resistance/Immunity/Vulnerability, HP/Temporary HP/healing/death, action economy, an outcome-changing condition, target legality, or another explicitly in-scope combat result.
- **Movement-only mechanics are deferred and non-blocking for the MVP.** This includes Speed changes, movement modes, jumping, difficult terrain, teleport/repositioning, push/pull, and Grappled when its only consequence is movement/Speed.
- Exploration, environmental, sensory, language, illumination, compression/squeezing, and flavor rules are likewise non-blocking when they cannot change current Iron Pit combat math.
- A normally deferred relationship becomes relevant only when an in-scope mechanic explicitly depends on it. Example: plain Grappled is deferred; `while Grappled, Restrained` requires the relationship because Restrained changes combat math.
- Do not create engine code merely to make deferred source text disappear from an audit. Classify it as MVP out of scope. A later scope expansion should re-audit all 330 monsters and implement only the newly activated shared primitives.
- Saving throws are universal comparisons: shared d20/save modifiers/bonuses versus DC, then the feature declares success/failure consequences. A save whose only consequence is deferred movement is non-blocking.
- Typed damage is universal: compare each damage component's type to the target's Immunity, Resistance, and Vulnerability collections. Do not implement per-damage-type or per-monster defense resolvers.

## Product and RAW rules

- D20 Iron Pit is a D&D 2024 / SRD 5.2.1 rules-first card-vs-card combat simulator.
- Every exposed combat mechanic must be rules-as-written (RAW).
- Unsupported outcome-changing mechanics must fail closed.
- Never approximate, silently ignore, invent, or hand-wave a combat-relevant rule to make a hero or monster runnable.
- **Reuse-first gate:** before adding any combat handler, search the existing shared engine for an equivalent primitive/resolver. If the mechanic already exists, the new feature must reference that primitive and supply only its trigger, scope, duration/range, target rules, values, and source name.
- A feature, spell, trait, mastery, class, monster, or aura name is source/logging metadata, not permission to create another implementation of an existing mechanic. Advantage is Advantage, Disadvantage is Disadvantage, Resistance is Resistance, Immunity is Immunity, and the shared resolver remains authoritative regardless of the named source.
- New mechanic code is justified only when no existing primitive can represent an outcome-changing RAW effect. When a new primitive is genuinely required, implement it once at the natural shared resolution point and re-audit every hero and monster that can use it.
- Prefer reusable engine mechanics over hero-, monster-, or level-specific hacks.
- Keep the Python reference engine and browser production engine behaviorally equivalent.
- Preserve deterministic combat regression coverage, source auditing and references, generated-static parity, exact-head CI certification, and repository-enforced production source-size limits.
- Never weaken, delete, bypass, or rewrite a test merely to make CI green. Fix the underlying defect. If an assertion is genuinely obsolete after an intentional architecture change, replace it with an equally strong assertion for the new contract.

## Arena policy

Iron Pit simplifies battlefield formation without changing RAW combat mechanics. `docs/ARENA_POLICY.md` is authoritative except where the narrower MVP outcome filter explicitly defers movement-only mechanics.

- There is no public user-selected starting-distance control.
- Frontline/melee combatants begin engaged at the standard Pit melee distance.
- Dedicated ranged/support combatants begin behind their allied frontline and hold that rear position while an active allied frontline remains.
- Once the frontline is gone, exposed backliners use the existing RAW movement and range rules already supported by the engine; unsupported movement-only refinements do not block MVP certification.
- If an enemy reaches a ranged combatant, normal RAW close-combat ranged Disadvantage applies.
- There is no kiting AI or voluntary retreat behavior.
- Do not alter weapon reach or range, action economy, reactions, conditions, or other in-scope RAW math to implement formation.
- Low-level tests may explicitly position combatants to test already-supported geometry, range, movement, and reactions. Do not reintroduce a public starting-distance selector.

## Canonical hero architecture

`docs/CANONICAL_COMBAT_BUILD_POLICY.md` is authoritative for canonical hero construction and mass production.

The product contains 12 persistent named canonical heroes, one per core class, across levels 1 through 20: exactly 240 hero level snapshots. The user selects `Hero -> Level -> Fight`; identity persists across progression.

- Each class has exactly one canonical progression identity. Leveling never swaps to a different same-class build, spellbook, subclass, or combat concept unless the user explicitly authorizes a new architecture.
- Each level must derive from the previous certified canonical progression by applying only that level's RAW combat delta. Do not hand-build 20 separate versions of the same hero.
- Per-level research is a delta triage, not a full rebuild: identify only what the class/subclass/feat/resource tables add or scale at the new level, then ask whether each change can alter an Iron Pit MVP combat outcome.
- If a new or scaled feature changes an in-scope outcome defined by `docs/IRON_PIT_MVP_SCOPE.md`, it must be implemented or remain an explicit certification blocker. Movement-only changes do not qualify merely because they appear in combat rules text.
- If a feature cannot change an Iron Pit MVP combat outcome under the arena model, classify it as noncombat or arena-out-of-scope and do not build engine logic for it. Do not repeatedly research or reimplement inherited features that are already certified.
- The universal legal base array is the 27-point-buy `15 / 14 / 13 / 10 / 10 / 10` before legal Background increases and later feats/ASIs.
- Strength-primary melee defaults to STR 15 / CON 14 / DEX 13 with INT/WIS/CHA 10. Dexterity-primary melee/ranged defaults to DEX 15 / CON 14 / STR 13 with INT/WIS/CHA 10.
- Primary casters keep STR/DEX/CON at 10 and assign 15/14/13 to mental abilities by the deterministic class priorities in `docs/CANONICAL_COMBAT_BUILD_POLICY.md`.
- Use only legal 2024 Background ability increases. Prefer +2 to the canonical primary ability and +1 to the highest-ranked other allowed canonical ability. Never invent species ability-score bonuses.
- Existing certified hero profiles that predate the canonical array are migration debt and must be migrated to this policy before extending that progression further.
- Iron Pit runtime scope is combat-only. Noncombat features may remain in source/legal-build metadata, but they do not require runtime implementation and must not block combat certification unless they can change an MVP combat outcome.
- Legal noncombat choices that cannot affect Iron Pit may be chosen deterministically or randomized among equivalent class-relevant options; do not add custom combat-engine logic for them.
- Progression must update every applicable in-scope combat datum: level, proficiency bonus, HP, ability score improvements or feats, subclass, AC, attacks, attack and damage bonuses, saves, equipment, weapon masteries, resources, species resources, action economy, Extra Attack, spellcasting and slots, concentration, reactions, Bonus Actions, conditions, class and subclass combat features, and scaling. Movement-only progression is deferred unless a supported in-scope rule depends on it.
- Only explicitly certified levels may be selectable or runnable.
- Preserve already-certified reusable mechanics while migrating duplicated build data to the canonical pipeline.
- Karnok Stoneward is the Fighter progression. Rokhan Stonefury is the Barbarian progression. The remaining identities are defined by `backend/app/content/hero_progressions.py`.
- Caster classes reuse one deterministic canonical class spell package. Character level controls prepared/known count, available spell levels, and slots; a new level extends the same package instead of creating a new caster-specific spellbook.
- Every caster level must receive its full class-appropriate prepared/known spell count and full spell-slot allotment before that level can be promoted. A level-20 caster is not flattened to a low-level package; higher-level spells and slots remain required progression work when their Iron Pit effects are in scope.
- Spell upcasting is deliberately deferred. Until explicitly reactivated and separately certified, a leveled spell may consume only a slot of its printed spell level and resolves only its printed/base-level effect. A higher-level slot must not increase targets, damage, healing, duration, or any other spell outcome and must not be spent as a substitute slot for a lower-level spell.
- Cantrip scaling by character level is separate from slot upcasting and remains required wherever the cantrip's RAW progression scales.
- Generic friendly multi-target buffs prioritize non-caster melee/front-line allies first, then the caster, then remaining ranged/back-line allies. Range and legal-target checks always apply; ties among line-holders use deterministic battlefield position and stable IDs rather than spell-specific branches.
- Spell packages favor combat-relevant spells. Healing classes retain healing plus damage/support options. Unsupported in-scope spell mechanics remain listed with explicit capability requirements and fail closed until the shared engine supports them; movement/exploration-only spell semantics are deferred.
- Melee loadouts use one repeatable policy: DEX-primary favors dual wielding; STR-primary with shield training favors one-hander plus shield; STR power builds favor a two-hander. Do not invent bespoke loadout logic per hero level.
- Hero and monster behavior must reuse the same Universal Combat Capability whenever their RAW behavior is equivalent. If a capability already exists, a new hero level should be data plus generated certification rather than new bespoke resolver code.
- One authoritative canonical definition should generate runtime/browser/catalog/certification state wherever practical. Repeated hand-authored ready lists and duplicated level facts are migration debt, not a desired architecture.
- Certification is derived from audited build/profile data, runtime templates, Python gates, browser-generated parity, and public catalog readiness. Never certify by editing a manifest alone.

## Monster architecture

The canonical SRD 5.2.1 catalog contains exactly 330 monsters. Treat certification as a source-driven capability pipeline, not 330 unrelated handcrafted projects:

`SRD source -> MVP scope filter -> parser/audit -> supported-mechanics analysis -> runtime template -> Python certification -> browser parity -> generated assets -> public readiness -> exact-head CI`

- A monster using only already-supported in-scope mechanics should require minimal bespoke implementation.
- A monster with an unsupported outcome-changing MVP mechanic remains blocked with explicit machine-readable blockers.
- A monster must not remain blocked for source text that is deferred by `docs/IRON_PIT_MVP_SCOPE.md`.
- After adding a shared mechanic or changing MVP scope, rerun analysis for all 330 monsters and identify everything newly unlocked.
- Prefer capability tranches such as damage/defenses, attack modifiers, saves, outcome-changing conditions, HP/healing, reactions/action economy, target legality, and other direct-math effects. Do not create tranches merely to implement movement-only source text.
- Monster runtime data should contain only stats, attacks, defenses, resources, spells, and capability IDs needed to resolve an Iron Pit MVP fight. Deferred stat-block text remains source metadata and does not need an engine implementation.

## Durable certification state

- `data/hero_certification_manifest.json` and `data/monster_certification_manifest.json` are generated snapshots, not hand-authored claims.
- Regenerate them with `python scripts/verify_certification_manifests.py --write` only after authoritative source/runtime/generated state is correct.
- Verify them with `python scripts/verify_certification_manifests.py` and report progress with `python scripts/report_certification_progress.py`.
- Do not maintain hundreds of duplicate Markdown checkboxes or hand-edited totals.
- CI must independently prove identity/slot counts, catalog counts, runtime readiness, source references, Python/browser parity, generated-static parity, blocker presence, and exact checked head.

## Validation and checkpoint policy

Before claiming a capability or certification tranche complete:

1. Run `python scripts/check_source_limits.py`.
2. Run `python scripts/prepare_static_site.py` and prove generated-static parity is clean.
3. Run `python scripts/verify_certification_manifests.py`.
4. Run the full Python suite from `backend` with `pytest -q`.
5. Run JavaScript syntax checks and every permanent browser `*.test.cjs` regression.
6. Confirm the exact intended commit is the commit certified by GitHub Actions.
7. Record exact certification counts and remaining blocker families using the generated report.

Work in coherent, reviewable commits. Code existence is not completion; every defined permanent gate must pass on the exact intended commit.

## Netlify resource policy

Do not hammer Netlify.

- Do not trigger Netlify deployments for routine commits or iterative testing.
- Prefer local Python/browser tests, generated-static validation, and GitHub CI.
- Batch work before any hosting verification.
- Use Netlify only at deliberate release/checkpoint validations where production hosting itself must be tested.
- Do not repeatedly poll or redeploy Netlify, and avoid unnecessary build-token or credit use.
- A green local/GitHub certification cycle does not automatically require Netlify. If a claim can be proven without Netlify, prove it without Netlify.

## Goal-mode policy

The full 240-hero/330-monster program is an open-ended master program, not one `/goal`. Use `docs/IRON_PIT_MASTER_PLAN.md` as durable program memory and choose finite goals with verifiable stopping conditions. A normal sequence is:

1. Complete one canonical hero progression tranche.
2. Run a zero-blocker monster certification tranche under the MVP scope filter.
3. Implement one reusable in-scope engine capability.
4. Re-audit all 330 monsters and certify everything that capability unlocks.
5. Continue until the master program criteria are satisfied.

Stop only for a genuine RAW ambiguity that affects MVP combat math, security/permission issue, usage limit, or a decision that materially requires human input. Movement-only and other explicitly deferred semantics are not stopping conditions.
