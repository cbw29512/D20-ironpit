# Iron Pit Markdown document map

This is a **directory and ownership map**, not a new task queue, certification source or rules spec. Every tracked Markdown document at the initial 2026-10-15 audit is assigned one role below. Generated files, legal notices, historical audit evidence and locked rule contracts are intentionally not bulk-rewritten: doing so would erase evidence, conflict with generator output, or change approved combat policy without a new decision.

## Fast path

1. [SOUL](../SOUL.md) and the [universal card contract](UNIVERSAL_CARD_COMBAT_CONTRACT.md) — engine owns mechanics; immutable source cards own parameters.
2. [Execution manual](IRON_PIT_IMPLEMENTATION_PLAYBOOK.md) — one workflow and exact-head certification.
3. Select only one guide: [monsters](playbooks/MONSTERS.md), [pregens](playbooks/PREGENS.md), [engine](playbooks/UNIVERSAL_ENGINE.md).
4. For monsters, [live decision queue](MONSTER_ABILITY_WORK_QUEUE.md) + [generated blockers](MONSTER_BLOCKERS_2014.md) + [mechanic inventory](UNIVERSAL_MECHANIC_INVENTORY.md) — no competing backlog.
5. [Ownership and handoff](TWO_AGENT_COORDINATION.md) — avoid concurrent edits. For locked policies read [rules index](IRON_PIT_LOCKED_RULES.md) and its exact cited contract.

**Important:** a document marked historical may contain old counts or a superseded "next" instruction. That text is audit evidence, not a current work order. The live queue also includes dated entries; reconcile its cursor with generated current-main reports and PR status before implementation.

## Document roles

- **Operating:** navigational instructions, live workflow and deployment lock.
- **Live queue:** approved monster decisions and implementation cursor; not a generated classifier.
- **Generated:** produced by scripts; never hand-edit.
- **Rules/technical contract:** retains source-specific and approved RAW/Pit policy, changed only with an explicit rule/architecture decision.
- **Historical evidence:** audits, prior handoffs, checklists and proposals; preserve unchanged even when milestones become obsolete.
- **Asset evidence:** card-art inventories and fixtures, not combat source truth.
- **Legal:** retain notices verbatim.

This map covers **63** Markdown files at its creation (3 asset evidence, 2 generated, 31 historical evidence, 1 legal, 1 live queue, 13 operating, 12 rules/technical contract). New documents should have a clear unique owner, not duplicate a current cursor.

| File | Role |
|---|---|
| `.agents/skills/iron-pit-context-transfer/SKILL.md` | operating |
| `AGENTS.md` | operating |
| `README.md` | operating |
| `SOUL.md` | operating |
| `THIRD_PARTY_NOTICES.md` | legal |
| `docs/2014_AUDIT_FIX_CONTEXT_TRANSFER.md` | historical evidence |
| `docs/2014_AUDIT_FIX_VERIFICATION.md` | historical evidence |
| `docs/2014_BARBARIAN_11_20_AUDIT.md` | historical evidence |
| `docs/2014_BETA_COMBAT_PRESETS.md` | historical evidence |
| `docs/2014_BETA_UI_FIX.md` | historical evidence |
| `docs/2014_DRUID_CANONICAL_WILD_SHAPE_FORMS.md` | historical evidence |
| `docs/2014_LAND_DRUID_CAPABILITY_AUDIT.md` | historical evidence |
| `docs/2014_LORE_BARD_CAPABILITY_AUDIT.md` | historical evidence |
| `docs/2014_MONK_18_20_CAPABILITY_AUDIT.md` | historical evidence |
| `docs/2014_RECONCILIATION_PLAN.md` | historical evidence |
| `docs/2014_ROGUE_11_20_ENGINE_AUDIT.md` | historical evidence |
| `docs/2024_BARBARIAN_NEXT_AUDIT.md` | historical evidence |
| `docs/ABILITY_HOOK_ENGINE_PROPOSAL.md` | rules/technical contract |
| `docs/ANTIMAGIC_SUSCEPTIBILITY_AUDIT.md` | historical evidence |
| `docs/BATTLECAST_MOVEMENT_PROVENANCE.md` | historical evidence |
| `docs/BRONZE_REPULSION_AUDIT.md` | historical evidence |
| `docs/CANONICAL_COMBAT_BUILD_POLICY.md` | rules/technical contract |
| `docs/COMBAT_RESOLUTION_PIPELINE.md` | rules/technical contract |
| `docs/CONTEXT_TRANSFER_CONTRACT.md` | operating |
| `docs/CURRENT_OPERATING_STATUS.md` | operating |
| `docs/DEPLOYMENT.md` | operating |
| `docs/DOCUMENTATION_MAP.md` | operating |
| `docs/FUNGUS_SEQUENCE_AUDIT.md` | historical evidence |
| `docs/GRICK_SEQUENCE_AUDIT.md` | historical evidence |
| `docs/INCLUDED_WEAPON_DAMAGE_AUDIT.md` | historical evidence |
| `docs/IRON_PIT_AUDIT_EVENT_SCHEMA.md` | rules/technical contract |
| `docs/IRON_PIT_HOMEBREW_RULESET_CONTRACT.md` | rules/technical contract |
| `docs/IRON_PIT_IMPLEMENTATION_PLAYBOOK.md` | operating |
| `docs/IRON_PIT_LOCKED_RULES.md` | rules/technical contract |
| `docs/IRON_PIT_RULES_CONTRACT.md` | rules/technical contract |
| `docs/MAIN_ACTION_SELECTION_CONTRACT.md` | rules/technical contract |
| `docs/MONSTER_ABILITY_WORK_QUEUE.md` | live queue |
| `docs/MONSTER_BLOCKERS_2014.md` | generated |
| `docs/MONSTER_CONTEXT_TRANSFER.md` | historical evidence |
| `docs/MONSTER_FIX_TRACKER.md` | historical evidence |
| `docs/MONSTER_REMAINING_2014_WORKSHEET.md` | historical evidence |
| `docs/MONSTER_UNBOUND_TRAITS_2014_AUDIT.md` | historical evidence |
| `docs/MULTIATTACK_SEQUENCE_AUDIT.md` | historical evidence |
| `docs/PREGEN_AND_CONTENT_RULES_CONTRACT.md` | rules/technical contract |
| `docs/STENCH_REUSE_AUDIT.md` | historical evidence |
| `docs/TURNING_SAVE_BUFF_AUDIT.md` | historical evidence |
| `docs/TWO_AGENT_COORDINATION.md` | operating |
| `docs/UNIVERSAL_CARD_COMBAT_CONTRACT.md` | rules/technical contract |
| `docs/UNIVERSAL_COMBATANT_ARCHITECTURE.md` | rules/technical contract |
| `docs/UNIVERSAL_MECHANIC_INVENTORY.md` | generated |
| `docs/UNIVERSAL_TACTICAL_FORM_SELECTION.md` | rules/technical contract |
| `docs/VTT_CARD_BATTLEFIELD_CONTRACT.md` | historical evidence |
| `docs/artifacts/card-art/ART_SHOPPING_LIST.md` | asset evidence |
| `docs/artifacts/card-art/REAL_ART_INVENTORY.md` | asset evidence |
| `docs/artifacts/card-art/fixtures/README.md` | asset evidence |
| `docs/audits/2014-paladin-levels-12-20-capability-audit.md` | historical evidence |
| `docs/audits/2014-warlock-capability-audit.md` | historical evidence |
| `docs/audits/2024-fighter-level17-engine-inventory.md` | historical evidence |
| `docs/audits/2024-monk5-hit-rider-integration.md` | historical evidence |
| `docs/audits/2024-paladin12-derived-stats.md` | historical evidence |
| `docs/playbooks/MONSTERS.md` | operating |
| `docs/playbooks/PREGENS.md` | operating |
| `docs/playbooks/UNIVERSAL_ENGINE.md` | operating |
