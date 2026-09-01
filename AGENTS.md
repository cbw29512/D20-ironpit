# D20 Iron Pit repository instructions

Read this file, `docs/IRON_PIT_MASTER_PLAN.md`, and the structured certification manifests before changing code. The repository and its permanent tests are authoritative; prompts and historical counts are not.

## Product and RAW rules

- D20 Iron Pit is a D&D 2024 / SRD 5.2.1 rules-first card-vs-card combat simulator.
- Every exposed combat mechanic must be rules-as-written (RAW).
- Unsupported outcome-changing mechanics must fail closed.
- Never approximate, silently ignore, invent, or hand-wave a combat-relevant rule to make a hero or monster runnable.
- Prefer reusable engine mechanics over hero-, monster-, or level-specific hacks.
- Keep the Python reference engine and browser production engine behaviorally equivalent.
- Preserve deterministic combat regression coverage, source auditing and references, generated-static parity, exact-head CI certification, and repository-enforced production source-size limits.
- Never weaken, delete, bypass, or rewrite a test merely to make CI green. Fix the underlying defect. If an assertion is genuinely obsolete after an intentional architecture change, replace it with an equally strong assertion for the new contract.
- PR #32 must remain a draft and unmerged. Do not merge it, merge to `main`, or change its base branch without explicit user authorization.

## Arena policy

Iron Pit simplifies battlefield formation without changing RAW combat mechanics. `docs/ARENA_POLICY.md` is authoritative.

- There is no public user-selected starting-distance control.
- Frontline/melee combatants begin engaged at the standard Pit melee distance.
- Dedicated ranged/support combatants begin behind their allied frontline and hold that rear position while an active allied frontline remains.
- Once the frontline is gone, exposed backliners use the existing RAW movement and range rules.
- If an enemy reaches a ranged combatant, normal RAW close-combat ranged Disadvantage applies.
- There is no kiting AI or voluntary retreat behavior.
- Do not alter weapon reach or range, movement speed, Opportunity Attacks, forced movement, conditions, action economy, reactions, or any other RAW mechanic to implement formation.
- Low-level tests may explicitly position combatants to test RAW geometry, range, movement, and reactions. Do not reintroduce a public starting-distance selector.

## Canonical hero architecture

The product contains 12 persistent named canonical heroes, one per core class, across levels 1 through 20: exactly 240 hero level snapshots. The user selects `Hero -> Level -> Fight`; identity persists across progression.

- Each class has exactly one canonical progression identity. Leveling never swaps to a different same-class build, spellbook, subclass, or combat concept unless the user explicitly authorizes a new architecture.
- Each level must derive from the previous certified canonical progression rather than duplicating a whole character by hand.
- Iron Pit runtime scope is combat-only. Noncombat features may remain in source/legal-build metadata, but they do not require runtime implementation and must not block combat certification unless they can change a combat outcome.
- Progression must update every applicable combat datum: level, proficiency bonus, HP, ability score improvements or feats, subclass, AC, attacks, attack and damage bonuses, saves, equipment, weapon masteries, resources, species resources, action economy, Extra Attack, spellcasting and slots, concentration, reactions, Bonus Actions, conditions, movement, class and subclass combat features, and scaling.
- Only explicitly certified levels may be selectable or runnable.
- Preserve already-certified levels while extending a progression.
- Karnok Stoneward is the Fighter progression. Rokhan Stonefury is the Barbarian progression. The remaining identities are defined by `backend/app/content/hero_progressions.py`.
- Caster classes reuse one deterministic canonical class spell package. Character level controls prepared/known count, available spell levels, and slots; a new level extends the same package instead of creating a new caster-specific spellbook.
- Spell packages favor combat-relevant spells. Healing classes retain healing plus damage/support options. Unsupported spell mechanics remain listed with explicit capability requirements and fail closed until the shared engine supports them.
- Melee loadouts use one repeatable policy: DEX-primary favors dual wielding; STR-primary with shield training favors one-hander plus shield; STR power builds favor a two-hander. Do not invent bespoke loadout logic per hero level.
- Certification is derived from audited build/profile data, runtime templates, Python gates, browser-generated parity, and public catalog readiness. Never certify by editing a manifest alone.

## Monster architecture

The canonical SRD 5.2.1 catalog contains exactly 330 monsters. Treat certification as a source-driven capability pipeline, not 330 unrelated handcrafted projects:

`SRD source -> parser/audit -> supported-mechanics analysis -> runtime template -> Python certification -> browser parity -> generated assets -> public readiness -> exact-head CI`

- A monster using only already-supported mechanics should require minimal bespoke implementation.
- A monster with an unsupported outcome-changing mechanic remains blocked with explicit machine-readable blockers.
- After adding a shared mechanic, rerun analysis for all 330 monsters and identify everything newly unlocked.
- Prefer capability tranches such as recharge, spellcasting families, conditions/control, save actions, reactions, Bonus Actions, legendary actions, limited-use abilities, attack riders, and traits.

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
2. Run a zero-blocker monster certification tranche.
3. Implement one reusable engine capability.
4. Re-audit all 330 monsters and certify everything that capability unlocks.
5. Continue until the master program criteria are satisfied.

Stop only for a genuine RAW ambiguity, security/permission issue, usage limit, or a decision that materially requires human input.
