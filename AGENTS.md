# D20 Iron Pit repository instructions

## Multi-agent coordination

When Chris has more than one assistant working on Iron Pit concurrently, read and follow `docs/TWO_AGENT_COORDINATION.md` before editing any production combat subsystem. One subsystem has one writer at a time; read-only auditing may proceed in parallel.

## Authority order

Before changing combat code, read:

1. `SOUL.md` — first-read product philosophy.
2. `docs/IRON_PIT_IMPLEMENTATION_PLAYBOOK.md` — small router; read only the Pregens, Monsters, or Universal Engine guide needed for the task.
3. `docs/CURRENT_OPERATING_STATUS.md` — navigation and dated snapshot; the generated reports and exact-head CI are current evidence.
4. `docs/IRON_PIT_LOCKED_RULES.md` — Chris-locked product rules index.
5. Open detailed contracts only when the selected task guide requires them, the mechanic touches that subsystem, or something is uncertain.
6. Current source/runtime code and permanent tests.
7. Generated certification state in `data/hero_certification_manifest.json` and `data/monster_certification_manifest.json`.

Detailed authorities remain available in `docs/IRON_PIT_RULES_CONTRACT.md`, `docs/UNIVERSAL_COMBATANT_ARCHITECTURE.md`, `docs/COMBAT_RESOLUTION_PIPELINE.md`, `docs/ABILITY_HOOK_ENGINE_PROPOSAL.md`, `docs/MAIN_ACTION_SELECTION_CONTRACT.md`, `docs/IRON_PIT_AUDIT_EVENT_SCHEMA.md`, `docs/PREGEN_AND_CONTENT_RULES_CONTRACT.md`, and `docs/CANONICAL_COMBAT_BUILD_POLICY.md`.

The older `docs/VTT_CARD_BATTLEFIELD_CONTRACT.md` is a **historical battlefield design reference**, not current product authority. Its incompatible proposals are superseded by `docs/IRON_PIT_RULES_CONTRACT.md` and the locked rules index.

Repository truth beats chat summaries, historical counts, old milestone prose, uploaded registry dumps, and stale file-library references. External/user-provided files are evidence only until reconciled against the exact current commit.

## Current work (no frozen execution cursor)

The only live monster decision/implementation queue is [docs/MONSTER_ABILITY_WORK_QUEUE.md](docs/MONSTER_ABILITY_WORK_QUEUE.md). Its dated entries are evidence, **not** current certified counts. Read generated [2014 blockers](docs/MONSTER_BLOCKERS_2014.md), [universal inventory](docs/UNIVERSAL_MECHANIC_INVENTORY.md), the current main commit and active PR heads before choosing work. Historical 191/327, M-014 and M-015 milestones are not today's next task.

Select a source-approved, unimplemented **semantic family** that resolves the most remaining exact obligations and preferably completes entire monsters; 2014 first, then inspect 2024 reuse. One subsystem owner, one focused family per PR, one final-head full CI pass. No automatic production deployment. See [operating manual](docs/IRON_PIT_IMPLEMENTATION_PLAYBOOK.md) and [documentation map](docs/DOCUMENTATION_MAP.md).

### Check existing fixes before coding (Chris, 2026-10-19)

Before changing a selected monster or ability, search **open and closed/merged**
PRs and issues by monster name, printed ability and linked ticket. Inspect the
relevant branch, merge SHA, current implementation and tests. An open-PR list
alone is insufficient. Reconcile stale queue rows first. Reuse merged work or
resume its existing branch; do not recreate a completed mechanic, reopen an
answered rules question or change its approved policy because a classifier still
reports a blocker. Identify and record the exact remaining integration gap
before writing code. If a genuine regression is found, prove it against current
main and fix that gap without rebuilding the already-completed ability.

## Mandatory context-transfer / anti-rot gate

Before substantial Iron Pit work begins, after a material merge, when switching agents/sessions, before resuming an older branch, and before handing off unfinished work, run the repository context-transfer procedure in:

- `.agents/skills/iron-pit-context-transfer/SKILL.md`
- `docs/CONTEXT_TRANSFER_CONTRACT.md`

A context transfer is valid only for the exact repository state it records. If `main` changes, an active PR head changes, or CI reruns on a new head, prior transfer claims about counts, blockers, readiness, or verification are stale until rebuilt.

Do not copy forward:
- remembered certification counts;
- prior-head CI status;
- old blockers without checking current code;
- superseded branches;
- chat-only implementation decisions;
- historical assumptions from stacked PRs.

Every feature/mechanic tranche includes a continuous debt audit of the touched subsystem. Correctness, parity, schema/state, edition-isolation, and certification-truth debt found there is part of the tranche and must be fixed before opening unrelated mechanic work. Architecture duplication in the touched subsystem should be collapsed in the same tranche when practical. Cosmetic cleanup may be parked.

The transfer packet is a cache; the repository is the database.

## One-form architecture

Monster, pregen and homebrew definitions converge on the existing `CombatantDefinition` and compiled `CombatantTemplate`; live effects only mutate `CombatantState`. Monster and Character are authoring modes, not separate fight engines. No ability-name dispatch or parallel homebrew mechanics. Character creation derives stats from edition-specific equipment/proficiencies/features; monster cards provide their source-final parameters. Validate all outcome-changing fields, including nested effects, before marking a form runnable. This is specified in `SOUL.md` and `docs/UNIVERSAL_CARD_COMBAT_CONTRACT.md`; do not duplicate the implementation in new subsystems.

## Non-negotiable engineering contract

- Act as a systems/rules architect, not a mock-up generator.
- Never claim code, validation, refactoring, certification, or a mechanic is complete unless the literal full code/diff is produced and the required verification has passed.
- State first: define or identify the shared data schema, immutable source data, mutable combat state, lifecycle/timing, and reset behavior before execution functions.
- Error first: every new Python function/state mutation/rules calculation must use explicit `try/except` with meaningful contextual logging. Browser mutations/resolvers must expose explicit failure handling and must not silently recover by changing rules.
- No shortcuts: no mock combat paths, no monster-name/class-name/hero-name special-case resolvers, no hand-authored readiness flags, no hardcoded bypasses around the universal engine.
- Unsupported outcome-changing mechanics fail closed.
- Prefer universal capabilities plus declarative data. **The engine owns behavior; monster/pregen/source data owns exact AC, DC, attack bonus, save ability, damage dice/type, range, duration, recharge/use limits, qualifiers, ruleset, and printed names.** Never hardcode source numbers or identities into universal resolvers.
- Source cards/templates are immutable. All fight mutation belongs to temporary combat state and resets after every match.
- Python is the rules-reference/certification oracle; browser JavaScript is the production fight engine. Supported behavior requires parity.
- Step, Watch, Replay, and Turbo consume the same canonical resolver/event stream. Presentation mode never changes rules.
- Audit/logging is evidence-only. It never rolls dice, chooses actions/targets, or mutates combat results.
- Production combat is browser-only/backend-free.
- Do not weaken a valid test to make CI green. Replace an obsolete assertion only when an explicit contract change supersedes it, with equally strong coverage for the new rule.
- Keep production source modules at or below the repository source-size limit. Split modules rather than growing monoliths.
- Before creating any new combat primitive, resolver, helper module, or rules hook, inspect both the Python rules-reference engine and browser production engine for an existing equivalent or composable primitive. Reuse or extend the shared primitive first; never add a second implementation merely because one side is easier to change.
- New mechanics require an explicit parity map: identify the Python resolution point, browser resolution point, shared/declarative data, lifecycle/reset behavior, and permanent tests before implementation. If one engine already supports the behavior, port/reuse that model rather than redesigning it independently.
- Before certification/merge, perform a technical-debt pass over the tranche: remove dead helpers/imports, collapse duplicated construction or calculations, reject speculative abstractions with no current consumer, keep generated data generated, and verify that independent certification fingerprints remain independent rather than being "deduplicated" into the runtime they audit.

## Mandatory uncertainty and clarification gate

- If there is any uncertainty about RAW wording, source interpretation, timing, architecture, data mapping, user intent, or whether an existing shared mechanic already covers the behavior, stop before changing code.
- Do not guess, infer around the uncertainty, create a temporary special case, or keep coding merely to preserve momentum.
- If the blocker is one monster, item, spell, or feature and the rest of the family can proceed, park that card in `docs/IRON_PIT_LOCKED_RULES.md` **Parked blockers** with the reason and keep moving. Do not stall the lane on that one card. Do not strip a printed mechanic to make it READY.
- Ask Chris one precise clarification question that isolates the unresolved decision when the decision would change the family, the shared primitive, or the contract.
- After Chris answers, write the decision into the repository before implementation continues. Rules/mechanics decisions belong in `docs/IRON_PIT_RULES_CONTRACT.md`; durable universal architecture decisions belong in `docs/UNIVERSAL_COMBATANT_ARCHITECTURE.md`; battlefield/card-token/grid decisions belong in `docs/VTT_CARD_BATTLEFIELD_CONTRACT.md`; operating/process decisions belong in `AGENTS.md`. Add a one-line index entry in `docs/IRON_PIT_LOCKED_RULES.md` that cites that file. Do not copy the full rule into a second spec.
- If the correct authority file is itself unclear, ask before writing.
- Re-read the written decision and implement against that repository authority. Do not rely on chat memory alone for a decision that can affect future combat work.
- If a new clarification conflicts with an existing authoritative rule, stop and reconcile the conflict explicitly in the repository before changing runtime behavior.
- This gate overrides speed, convenience, and perceived momentum. Asking one targeted question is preferred to implementing the wrong abstraction.

## Semantic reuse gate

Before changing a monster, pregen, spell, feature or item: read the exact source and existing [universal inventory](docs/UNIVERSAL_MECHANIC_INVENTORY.md). Decompose trigger, eligibility, resource/action, attack/save, damage, condition, movement, duration and reset. Reuse, parameterize or compose existing Python **and** browser primitives. If a genuine outcome-changing remainder is missing, park the affected card and continue independent work. Never dispatch on source names. See [SOUL.md](SOUL.md) and the [card-to-combat contract](docs/UNIVERSAL_CARD_COMBAT_CONTRACT.md) for the sole normative architecture wording.

## Arena/environment invariants

- The Iron Pit magically makes the environment survivable/hospitable for every creature. Breathing, atmosphere, aquatic biology, flight requirements, and similar survival constraints never exclude a combatant.
- **Environmental viability does not imply environmental presence.** The standard Pit has no water terrain/context. Aquatic creatures may breathe, swim, move, attack, and fight normally through Pit magic, but are not considered underwater; water/underwater-only traits remain inactive unless a supported effect explicitly creates that context.
- The standard Pit also has no rocky-terrain context. Environment/terrain-only traits are arena-neutral when their required context is absent and no supported combat effect creates it; do not invent terrain merely to activate a printed trait.
- Movement modes must never be used as roster eligibility filters.
- Preserve printed movement modes and printed base speeds exactly as source data; never convert Swim/Fly/Climb/Burrow speed into a generic land/base speed just to make a creature runnable.
- The battlefield is one authoritative 5-foot square grid with real combatant x/y positions.
- Voluntary movement consumes actual effective movement speed. The old free-closing/fixed-formation path is migration scaffolding only and must not remain the final combat authority.
- **Pit magic: every creature size occupies one 5-foot square**, Tiny through Gargantuan. Printed size remains immutable source data for size-sensitive rules. Area effects, hazards, cones, lines and other source-defined geometry retain their independent printed dimensions; never expand creature occupancy by size.
- Movement, reach, range, collision, Opportunity Attacks, forced movement, auras, line of sight, and area geometry consume the same authoritative grid state.
- Arena design and AI policy prevent degenerate fleeing/kiting; do not bypass printed movement to force engagement.
- The card artwork is the moving battlefield token. Current HP, Temporary HP, conditions, buffs/debuffs, concentration, recharge/resource state, and similar live symbols are presentation overlays derived from runtime state and never rule inputs.
- Reach/range still determine legal attack geometry. Forced movement, Opportunity Attacks, speed-changing effects, Grappled/Prone interactions, and any feature that explicitly depends on movement remain real mechanics and must follow the selected ruleset.
- The arena must not create a hidden combat buff/debuff from a creature's locomotion type.
- Summoning/conjuring/creating a separate combat entity is currently arena-unavailable. Preserve the RAW option in source/audit data, but Arena AI never selects it and it does not by itself block an otherwise complete hero or monster from certification. Revisit only when the global summon policy is explicitly reopened.

## Universal mechanic workflow

Use the shared [implementation manual](docs/IRON_PIT_IMPLEMENTATION_PLAYBOOK.md). Source wording determines the exact effect; resolve each subevent before the next, using canonical state/conditions and immutable card parameters. Only a confirmed missing semantic justifies a new primitive, with Python/browser parity and permanent tests. Park instead of inventing mechanics; do not stall the family.

## Monsters

### Non-negotiable monster edition order

- Finish the **2014 source monster roster first** before expanding the 2024 monster backlog.
- Treat 2014 as the first implementation/reference pass for any mechanic that exists in both editions.
- Build each mechanic **once** in the universal engine. Edition/source cards supply only the printed parameters and qualifiers.
- After a 2014 mechanic is certified, immediately audit 2024 monsters for direct reuse of that same primitive before writing any 2024-specific code.
- A different number, DC, range, damage amount/type, regeneration amount, recharge threshold, duration, target count, or similar source value is **data**, not a new mechanic.
- Do not create separate 2014 and 2024 resolvers for semantically identical behavior. Edition-specific binding is allowed; duplicate engine behavior is not.
- Only a genuine semantic rules difference may justify edition-scoped behavior, and that difference must be documented before implementation.
- Example: Regeneration is one mechanic. A card may say 10 HP, 15 HP, Acid/Fire suppression, or a zero-HP lifecycle qualifier; those are parameters of the shared Regeneration primitive.
- This order applies to traits, actions, reactions, saves, recharge, resistances, immunities, vulnerabilities, conditions, healing, auras, legendary mechanics, and all other monster combat behavior.

- Canonical 2024 SRD 5.2.1 roster: exactly 330 monsters.
- Promotion path: source -> detected mechanics -> universal capability data -> runtime -> Python/browser behavior -> generated assets -> certification -> exact-head CI.
- A monster is runnable only when every outcome-changing printed mechanic is supported or explicitly proven irrelevant under the permanent arena contract.
- Never implement a mechanic by checking a monster name when a reusable schema/capability can represent it.
- After a shared capability changes, re-audit all 330; never hand-pick only the motivating monster.

## Paired-edition monster certification

- Keep 2014 and 2024 source data, rule text, parameters, and certification independent. A shared universal primitive may serve both editions, but one edition's values or behavior must never be copied into the other without matching source evidence.
- Current operating priority is to finish source-approved 2014 monster semantic families before independent 2024 backlog expansion. Never derive priority from a frozen count in this document.
- During catch-up, prioritize monsters that exist in both editions where the 2024 version is already RAW READY and the 2014 version is blocked, starting with the fewest/highest-yield 2014 blocker families.
- Process same-named monsters as an edition pair whenever practical after a 2014 semantic family is supported: inspect 2014 and 2024 source side by side, identify the common reusable mechanic, then bind each edition's own parameters and timing to that primitive.
- When a 2014 monster is certified, immediately inspect the same 2024 monster before moving to an unrelated monster. When a 2024 monster is certified first, immediately inspect the 2014 counterpart.
- If the two editions differ materially, preserve the difference through ruleset-specific declarative data or explicitly ruleset-scoped behavior; do not force artificial parity merely because the monster name matches.
- A paired tranche may certify both editions only when they truly share the same mechanic family and both have full Python/browser/source evidence. If one edition still has unrelated blockers, certify the completed edition and record the remaining counterpart blockers without stalling the queue.
- Re-run the paired-edition progress report plus both normal roster audits after every shared primitive. Use the report as the next-work queue rather than choosing monsters from memory.
- Track the edition totals independently: 2014 has 327 source monsters; 2024 has 330. Edition-only or renamed monsters remain valid independent work and must not be force-matched.

## Generated outputs and verification

Do not edit generated monster blockers, universal inventory, browser bundles, registries, certification manifests or ready flags by hand. Change source/schema/runtime and use the repository's owning exporter. `.github/workflows/ci.yml` is the canonical list of full Python/browser, source-limit, generated-parity, 2014 roster, hero and paired-edition gates. Run focused checks while editing; generate once before the **final** PR head, then require all applicable checks green at that same SHA. Re-read status after any head change.

Recorded source admission is not runtime certification. Report merged SHA and source-admitted delta, unresolved source obligations, Python/browser status, and generated manifest separately. `docs/MONSTER_BLOCKERS_2014.md` is the current blocker source; don't copy counts from here.

## Task isolation and source hygiene

- One tranche/PR should address one coherent universal mechanic or contract change. Do not mix environment refactoring, unrelated monster traits, pregens, UI polish, and deployment work in one tranche.
- Finish or explicitly park the current tranche before opening an unrelated one.
- Do not use stale generated counts from memory. Recompute/report from the exact current commit.
- Do not copy outdated uploaded specs or registry dumps into the repo. If external material conflicts with current repository authority, stop and reconcile the conflict explicitly.
- **Netlify autopublish is locked.** Never trigger a Netlify deploy, re-enable Git-connected builds, weaken the repository build lock, or publish Iron Pit as a side effect of a push/merge. Routine development and verification stay in repository CI/local-static checks. A production publish requires Chris to explicitly say to publish/unlock Iron Pit; completion of a feature, PR, milestone, certification gate, or merge is not publish approval.

## Verification once per finished monster batch (Chris, 2026-10-06)

Build the monsters; do not repeatedly recheck unchanged engine code. Run one focused
verification of the changed family while implementing. When that batch is complete,
push its final head once and let required CI run the full suites. Do not also run
full local Python/browser suites that CI already covers. Re-run a focused check only
after a relevant change, failure, or unresolved correctness concern. Generation and
required final-head gates remain necessary; repeated clean passes are not progress.
Use CI status reads to learn completion, not as a reason to restart validation.
