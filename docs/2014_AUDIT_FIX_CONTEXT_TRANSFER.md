IRON PIT CONTEXT TRANSFER

generated_at: 2026-09-30
main_sha: d64f549ea7b3de3ff5776fd0f6070691801b7047
active_lane: user-authorized 2014 audit repairs; isolated from other window's Druid 17 work

AUTHORITATIVE STATUS
- 2014 hero progression 240/240; certified monsters 129/327.
- 2024 hero progression 116/240; certified monsters 140/330 at recorded main.
- Production is browser-only and Netlify publishing remains locked.

ACTIVE PRS
- #472 | ee1166f3abfa8a913b8500678b44998640b9e6b1 | ACTIVE in other window | fetched exact-head CI and 2014 certification failed; paired-edition report succeeded | Druid 17/Foresight. This audit does not own or modify that PR.
- This corrective branch | fix/2014-audit-website-parity | local verification passed, remote exact-head CI UNKNOWN until PR creation.
- Shared exporter/workflow files contain independent additions; regenerate native artifacts when reconciling merge order.

RECENT MERGES
- #471: Druid 16, recorded main above.

VERIFIED CERTIFICATION
- base commit: recorded main above.
- counts: recomputed using report_certification_progress and generated manifest verification.
- working repair tree: 1,999 Python tests passed; 201 standalone browser tests passed; 960 encounter probes for each entry point passed; source/registry/checklist/parity/wiring guards passed locally.
- Do not call this remote CI-certified until exact-head Actions complete.

CURRENT SUBSYSTEM
- source data: 2014 Warlock/Wizard HP-threshold sight flags and defensive spell durations.
- runtime state: existing action/resources, visibility conditions, source-owned modifiers and TimedEffects; fresh per fight.
- Python path: hp_threshold legality/outcome, spell_modifiers, encounter_combat_turn/encounter_main_action.
- browser path: equivalent threshold/modifier modules, Main Action selector profile and production HTML order.
- generated path: hero/template serializers and prepare_static_site.
- tests: test_2014_audit_fixes, browser-2014-audit-fixes, repaired standalone fixtures and existing full suites.

OPEN A-CLASS CORRECTNESS DEBT
- The two confirmed RAW audit findings are fixed in this branch with permanent regressions.
- Full RAW sign-off for every source clause remains outside this targeted tranche; the original audit did not establish exhaustive coverage.

OPEN B-CLASS ARCHITECTURE DEBT
- Re-anchor/regenerate after other window's PR changes main; shared generated outputs are not merge authorities.

PARKED C-CLASS CLEANUP
- No unrelated class, visual design, or deployment work included.

LOCKED RULE/ARCHITECTURE DECISIONS
- IRON_PIT_RULES_CONTRACT: legality first, strongest useful legal source-defined actions, opening buff costs/durations.
- MAIN_ACTION_SELECTION_CONTRACT: explicit signatureThreshold policy; Action Surge attack-only.
- UNIVERSAL_COMBATANT_ARCHITECTURE: declarative sight requirement; finite modifier spells reuse timed source groups.
- AGENTS: Netlify publishing lock, exact-head verification, no source-name resolvers.

NEXT EXACT ACTION
- Create and verify the isolated repair PR against this exact branch head.

DO NOT CARRY FORWARD
- Prior-head CI, old counts, exhaustive RAW claims, assumed live deployment, or Druid 17 ownership.
