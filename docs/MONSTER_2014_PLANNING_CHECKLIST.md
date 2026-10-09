# D20 Iron Pit — 2014 Monster Planning Checklist (124 records)

**PURPOSE: finish decisions for every blocked 2014 monster before hourly implementation starts.** This is a decision tracker, **not** a runtime certification report and not authorization to start an automation. Baseline: `main` at `642a6154e99448b31e0427599889724000ad95ec`, **203/327 source-admitted; 124 blocked**. After merges the generated `docs/MONSTER_BLOCKERS_2014.md` supersedes these baseline counts.

## What “one monster, one issue” means

1. **Delta-only review, not replaying the historic list.** Before discussing any entry, consult its printed source, existing implementation PR/merge status, already recorded user decisions, worksheet, and shared-engine inventory. Mark previous decisions **PLANNING COMPLETE** immediately and skip them. Do not ask again about approved or fully specified RAW effects. Only bring the **first genuinely unresolved policy/behavior** to the user. If none remain for this monster, advance without discussion. The printed 2014 source excerpts in [full source-backed blueprint](MONSTER_BLOCKER_FIX_BLUEPRINTS_2014.md) are lookup material, not proof that a decision is still open. No pictures, PR/CI detours, or coding while deciding.
2. **Planning complete** means behavior and its source-backed reuse/exclusion route are specified; **implementation complete** requires actual Python/browser parity, tests, regenerated manifests and green exact-head gates. Never merge these two statuses.
3. If already decided, copy the existing user ruling; **do not ask again**. If the result follows unambiguously from RAW and locked arena rules, document it without inventing a question. If policy is genuinely ambiguous, ask once and record the answer here and in [parent queue #675](https://github.com/cbw29512/D20-ironpit/issues/675).
4. Identical effects use one **universal mechanic** with source parameters (DC, save, roll, trigger, duration, conditions, recharge); names are for cards/logs. Preserve 2014/2024 edition separation. No summons, teleport relocation, vertical flight; the newly approved **Change Shape** exclusion is a specific action policy, not a blanket ban on Wild Shape or Polymorph.
5. Do **not** start or restart hourly implementation before all 124 planning decisions are closed. After that, hourly work takes the next queue item, checks relevant source and contract, implements/validates it in both runtimes, and advances only when done.

**Baseline markers:** `APPROVED` = user policy expressly approved; `PLAN DRAFTED` = concrete route written but coding pending; `PARTIAL` = some rulings fixed, some pending; `REVIEW NEXT` = source-backed packet requires *delta check*, not automatically a new question. **Skip gate:** `DECISION COMPLETE` (approved/reused/source-specified) -> record and advance, even when implementation pending; `IMPLEMENTATION PENDING` -> wait for hourly execution, **never ask as a planning question**; `DECISION NEEDED` -> the only reason to ask user. An unchecked item in an old worksheet does **not** itself mean user decision is needed. Generated report blockers are code readiness, not planning decisions.

**Current source-review cursor:** #017 **Banshee**. This is an assistant-side source audit, **not an automatic question to the user**. Consult prior rulings/PRs; ask only when an actual unrecorded arena-policy choice exists. All documented decisions remain excluded from repeat questioning. See [Review State Index](../data/monster_2014_review_state.json) and the queue helper.

## Source-of-truth decision gate (read this instead of treating an old blocker as a new question)

- **Machine-readable state**: [`data/monster_2014_review_state.json`](../data/monster_2014_review_state.json), with one stable entry per 124 historical blockers, carried-forward settled decisions and implementation notes.
- **Read-only selector**: `python scripts/monster_2014_review_queue.py --verify` validates roster/305 historical blocker-category totals; `--next` chooses the next **assistant source audit** without replaying completed monsters; `--questions` shows **only explicitly identified unanswered user policy choices**.
- If `--questions` is empty, **do not ask a question** just because `--next` selects a source record. Examine the source, apply RAW plus existing Pit constraints, document the reusable fix, close the planning item and advance. Add a question only where a genuine undocumented policy decision remains after this check.
- **Current state at generation**: 22 decision-complete monsters, 1 partially source-reviewed, 101 source audits pending, **0 identified open user-policy questions**. This is not 124 approved implementations; it is explicit separation of review work from user decisions. PRs/CI remain independent.

## Ordered review list

### 001. Aboleth

**Planning:** PARTIAL — Enslave policy approved; other printed effects await review. **Implementation:** pending. **Current blockers:** `attack:incomplete`, `mechanic:legendary`, `source:extra-action`, `source:legendary`, `source:trait`. **Primary family:** RECHARGE / RESOURCES.
- [ ] **attack:incomplete** (**Tentacle**): Recover full printed damage dice/type, saves/DC, conditions, persistent wounds, target restrictions and lifecycle in source attack schema; prove Python/browser hit resolution.
- [ ] **mechanic:legendary**: Use the existing legendary action economy but certify each source choice, turn restriction and exact combat resolution, not just the generic pool.
- [ ] **source:extra-action** (review candidate actions: **Enslave (3/Day)**): Identify each special printed Action, legality, targeting/area, source save, cost, duration, recharge and AI selection. Reuse shared area/save/action/movement/resource capabilities or park the specific missing semantic clause.
- [ ] **source:legendary** (**Psychic Drain**): Implement each printed option and its point cost, target, turn-end timing, spend/refill lifecycle via existing legendary-action system.
- [ ] **source:trait** (**Mucous Cloud; Probing Telepathy**): Decompose every named trait into its genuine event trigger, target eligibility, source-defined values, action/save/damage/condition, duration and exit. Bind shared mechanics; only classify neutral when an existing explicit arena rule permits it.
- [x] Enslave: effective-allegiance control; printed escape triggers; no automatic win; Psychic Drain may hit controlled target; [#681](https://github.com/cbw29512/D20-ironpit/issues/681).
- [ ] Remaining: Mucous Cloud context, Probing Telepathy, Tentacle disease, legendary Psychic Drain runtime integration.

**Source packet:** [#001 in full blueprint](MONSTER_BLOCKER_FIX_BLUEPRINTS_2014.md#1-aboleth-recharge-resources). **Review completion:** fill all above decisions before implementing; existing code readiness is not evidence of planning closure.

### 002. Acolyte

**Planning:** PLAN DRAFTED — no new policy decision identified. **Implementation:** pending. **Current blockers:** `mechanic:spellcasting`, `source:trait`. **Primary family:** SPELLCASTING.
- [ ] **mechanic:spellcasting** (**1-level wisdom caster; 6 printed prepared/at-will spells; printed spell list in full source packet**): Audit the full printed 2014 spells, slots/uses and AI choice. Map to shared edition-specific spell effects. Park every outcome-changing missing spell individually; keep source list and exclude only explicitly approved noncombat options.
- [ ] **source:trait** (**Spellcasting**): Decompose every named trait into its genuine event trigger, target eligibility, source-defined values, action/save/damage/condition, duration and exit. Bind shared mechanics; only classify neutral when an existing explicit arena rule permits it.
- [ ] Bind six source-prepared spells to 2014 universal Actions; Light remains combat-relevant; Thaumaturgy remains source-only; [#682](https://github.com/cbw29512/D20-ironpit/issues/682).

**Previously recorded source-specific decisions/dependencies** (preserved, not new approvals):
- **User decision / queued:** **LOCKED: Light is combat-relevant and remains available**, to illuminate nonmagical darkness, reveal darkness-dependent stealth, or trigger bright-light sensitivity as appropriate. It cannot counter 2014 magical Darkness (overlapping Darkness dispels Light cantrip). Thaumaturgy stays on the original stat block, but AI never casts it because it has no relevant arena combat purpose. Preserve all remaining spells and use existing spell primitives. Not yet implemented/certified.

**Source packet:** [#002 in full blueprint](MONSTER_BLOCKER_FIX_BLUEPRINTS_2014.md#2-acolyte-spellcasting). **Review completion:** fill all above decisions before implementing; existing code readiness is not evidence of planning closure.

### 003. Adult Bronze Dragon

**Planning:** APPROVED — Change Shape source-kept, arena unavailable. **Implementation:** pending. **Current blockers:** `source:extra-action`. **Primary family:** FEAR / CHARM / STATUS.
- [x] **Change Shape — APPROVED FOR ALL MATCHING MONSTERS:** Retain the complete printed Change Shape on card/source; never select it in Iron Pit combat. Other breath, fear, weapon, legendary effects stay intact. This is an explicit arena-only RAW deviation. Scope: [#663](https://github.com/cbw29512/D20-ironpit/pull/663) (stale PR must be rebased/reverified).

**Previously recorded source-specific decisions/dependencies** (preserved, not new approvals):
- **Identified remaining action:** Change Shape; the Bronze Repulsion audit explicitly names this as the independent extra-action blocker.
- **Fix plan:** Read the exact 2014 Change Shape source and compare against existing transformation/replacement-form and arena restrictions. If transformation is allowed and representable, bind it declaratively using the shared form/state primitive and preserve the original dragon's legal capabilities. If Pit policy excludes the action, document the existing rule and classifier consequence rather than invent a replacement. Verify attack choices, stats/HP/form return and browser/Python parity as applicable.
- **Avoid rework:** Do not touch Repulsion Breath or add a dragon-specific transformation resolver. Next classification decision is the permitted scope of Change Shape under the locked Pit rules.

**Source packet:** [#003 in full blueprint](MONSTER_BLOCKER_FIX_BLUEPRINTS_2014.md#3-adult-bronze-dragon-fear-charm-status). **Review completion:** fill all above decisions before implementing; existing code readiness is not evidence of planning closure.

### 004. Adult Gold Dragon

**Planning:** APPROVED — Change Shape source-kept, arena unavailable. **Implementation:** pending. **Current blockers:** `source:extra-action`. **Primary family:** FEAR / CHARM / STATUS.
- [x] **Change Shape — APPROVED FOR ALL MATCHING MONSTERS:** Retain the complete printed Change Shape on card/source; never select it in Iron Pit combat. Other breath, fear, weapon, legendary effects stay intact. This is an explicit arena-only RAW deviation. Scope: [#663](https://github.com/cbw29512/D20-ironpit/pull/663) (stale PR must be rebased/reverified).

**Source packet:** [#004 in full blueprint](MONSTER_BLOCKER_FIX_BLUEPRINTS_2014.md#4-adult-gold-dragon-fear-charm-status). **Review completion:** fill all above decisions before implementing; existing code readiness is not evidence of planning closure.

### 005. Adult Silver Dragon

**Planning:** APPROVED — Change Shape source-kept, arena unavailable. **Implementation:** pending. **Current blockers:** `source:extra-action`. **Primary family:** FEAR / CHARM / STATUS.
- [x] **Change Shape — APPROVED FOR ALL MATCHING MONSTERS:** Retain the complete printed Change Shape on card/source; never select it in Iron Pit combat. Other breath, fear, weapon, legendary effects stay intact. This is an explicit arena-only RAW deviation. Scope: [#663](https://github.com/cbw29512/D20-ironpit/pull/663) (stale PR must be rebased/reverified).

**Source packet:** [#005 in full blueprint](MONSTER_BLOCKER_FIX_BLUEPRINTS_2014.md#5-adult-silver-dragon-fear-charm-status). **Review completion:** fill all above decisions before implementing; existing code readiness is not evidence of planning closure.

### 006. Air Elemental

**Planning:** PLAN DRAFTED — no new policy decision identified. **Implementation:** pending. **Current blockers:** `mechanic:recharge`, `source:extra-action`, `source:trait`. **Primary family:** RECHARGE / RESOURCES.
- [ ] **mechanic:recharge**: Bind Recharge threshold to the exact printed Action and source-owned resource/turn roll. Certification requires the recharged Action to be legal or formally excluded.
- [ ] **source:extra-action** (review candidate actions: **Whirlwind (Recharge 4–6)**): Identify each special printed Action, legality, targeting/area, source save, cost, duration, recharge and AI selection. Reuse shared area/save/action/movement/resource capabilities or park the specific missing semantic clause.
- [ ] **source:trait** (**Air Form**): Decompose every named trait into its genuine event trigger, target eligibility, source-defined values, action/save/damage/condition, duration and exit. Bind shared mechanics; only classify neutral when an existing explicit arena rule permits it.
- [ ] Air Form occupied-space exception, Whirlwind save/prone/fling/collision, Recharge 4–6; [#683](https://github.com/cbw29512/D20-ironpit/issues/683).

**Previously recorded source-specific decisions/dependencies** (preserved, not new approvals):
- **Known directed work:** Air Form: reuse movement, spaces and creature occupancy constraints; do not reduce to presentation.

**Source packet:** [#006 in full blueprint](MONSTER_BLOCKER_FIX_BLUEPRINTS_2014.md#6-air-elemental-recharge-resources). **Review completion:** fill all above decisions before implementing; existing code readiness is not evidence of planning closure.

### 007. Ancient Brass Dragon

**Planning:** APPROVED — Change Shape source-kept, arena unavailable. **Implementation:** pending. **Current blockers:** `source:extra-action`. **Primary family:** FEAR / CHARM / STATUS.
- [x] **Change Shape — APPROVED FOR ALL MATCHING MONSTERS:** Retain the complete printed Change Shape on card/source; never select it in Iron Pit combat. Other breath, fear, weapon, legendary effects stay intact. This is an explicit arena-only RAW deviation. Scope: [#663](https://github.com/cbw29512/D20-ironpit/pull/663) (stale PR must be rebased/reverified).

**Source packet:** [#007 in full blueprint](MONSTER_BLOCKER_FIX_BLUEPRINTS_2014.md#7-ancient-brass-dragon-fear-charm-status). **Review completion:** fill all above decisions before implementing; existing code readiness is not evidence of planning closure.

### 008. Ancient Bronze Dragon

**Planning:** APPROVED — Change Shape source-kept, arena unavailable. **Implementation:** pending. **Current blockers:** `source:extra-action`. **Primary family:** FEAR / CHARM / STATUS.
- [x] **Change Shape — APPROVED FOR ALL MATCHING MONSTERS:** Retain the complete printed Change Shape on card/source; never select it in Iron Pit combat. Other breath, fear, weapon, legendary effects stay intact. This is an explicit arena-only RAW deviation. Scope: [#663](https://github.com/cbw29512/D20-ironpit/pull/663) (stale PR must be rebased/reverified).

**Source packet:** [#008 in full blueprint](MONSTER_BLOCKER_FIX_BLUEPRINTS_2014.md#8-ancient-bronze-dragon-fear-charm-status). **Review completion:** fill all above decisions before implementing; existing code readiness is not evidence of planning closure.

### 009. Ancient Copper Dragon

**Planning:** APPROVED — Change Shape source-kept, arena unavailable. **Implementation:** pending. **Current blockers:** `source:extra-action`. **Primary family:** FEAR / CHARM / STATUS.
- [x] **Change Shape — APPROVED FOR ALL MATCHING MONSTERS:** Retain the complete printed Change Shape on card/source; never select it in Iron Pit combat. Other breath, fear, weapon, legendary effects stay intact. This is an explicit arena-only RAW deviation. Scope: [#663](https://github.com/cbw29512/D20-ironpit/pull/663) (stale PR must be rebased/reverified).

**Source packet:** [#009 in full blueprint](MONSTER_BLOCKER_FIX_BLUEPRINTS_2014.md#9-ancient-copper-dragon-fear-charm-status). **Review completion:** fill all above decisions before implementing; existing code readiness is not evidence of planning closure.

### 010. Ancient Gold Dragon

**Planning:** APPROVED — Change Shape source-kept, arena unavailable. **Implementation:** pending. **Current blockers:** `source:extra-action`. **Primary family:** FEAR / CHARM / STATUS.
- [x] **Change Shape — APPROVED FOR ALL MATCHING MONSTERS:** Retain the complete printed Change Shape on card/source; never select it in Iron Pit combat. Other breath, fear, weapon, legendary effects stay intact. This is an explicit arena-only RAW deviation. Scope: [#663](https://github.com/cbw29512/D20-ironpit/pull/663) (stale PR must be rebased/reverified).

**Source packet:** [#010 in full blueprint](MONSTER_BLOCKER_FIX_BLUEPRINTS_2014.md#10-ancient-gold-dragon-fear-charm-status). **Review completion:** fill all above decisions before implementing; existing code readiness is not evidence of planning closure.

### 011. Ancient Silver Dragon

**Planning:** APPROVED — Change Shape source-kept, arena unavailable. **Implementation:** pending. **Current blockers:** `source:extra-action`. **Primary family:** FEAR / CHARM / STATUS.
- [x] **Change Shape — APPROVED FOR ALL MATCHING MONSTERS:** Retain the complete printed Change Shape on card/source; never select it in Iron Pit combat. Other breath, fear, weapon, legendary effects stay intact. This is an explicit arena-only RAW deviation. Scope: [#663](https://github.com/cbw29512/D20-ironpit/pull/663) (stale PR must be rebased/reverified).

**Source packet:** [#011 in full blueprint](MONSTER_BLOCKER_FIX_BLUEPRINTS_2014.md#11-ancient-silver-dragon-fear-charm-status). **Review completion:** fill all above decisions before implementing; existing code readiness is not evidence of planning closure.

### 012. Androsphinx

**Planning:** PLAN DRAFTED — no new policy decision identified. **Implementation:** pending. **Current blockers:** `mechanic:legendary`, `mechanic:spellcasting`, `source:extra-action`, `source:legendary`, `source:trait`. **Primary family:** FEAR / CHARM / STATUS.
- [ ] **mechanic:legendary**: Use the existing legendary action economy but certify each source choice, turn restriction and exact combat resolution, not just the generic pool.
- [ ] **mechanic:spellcasting** (**12-level wisdom caster; 15 printed prepared/at-will spells; printed spell list in full source packet**): Audit the full printed 2014 spells, slots/uses and AI choice. Map to shared edition-specific spell effects. Park every outcome-changing missing spell individually; keep source list and exclude only explicitly approved noncombat options.
- [ ] **source:extra-action** (review candidate actions: **Roar (3/Day); First Roar; Second Roar; Third Roar**): Identify each special printed Action, legality, targeting/area, source save, cost, duration, recharge and AI selection. Reuse shared area/save/action/movement/resource capabilities or park the specific missing semantic clause.
- [ ] **source:legendary** (**Teleport; Cast a Spell**): Implement each printed option and its point cost, target, turn-end timing, spend/refill lifecycle via existing legendary-action system.
- [ ] **source:trait** (**Inscrutable; Spellcasting**): Decompose every named trait into its genuine event trigger, target eligibility, source-defined values, action/save/damage/condition, duration and exit. Bind shared mechanics; only classify neutral when an existing explicit arena rule permits it.
- [ ] Three sequenced Roars; 2014 prepared spells; source-legal legendary Claw and Cast a Spell (Teleport no-cast); [#684](https://github.com/cbw29512/D20-ironpit/issues/684).

**Source packet:** [#012 in full blueprint](MONSTER_BLOCKER_FIX_BLUEPRINTS_2014.md#12-androsphinx-fear-charm-status). **Review completion:** fill all above decisions before implementing; existing code readiness is not evidence of planning closure.

### 013. Archmage

**Planning:** DECISION-COMPLETE — all printed source spell IDs and previous user-directed arena substitutions/exclusions have a recorded binding/selection policy; 2014 RAW governs ordinary damage/healing/control spells. **No additional user policy question identified.** **Implementation:** pending. **Current blockers:** `mechanic:spellcasting`, `source:trait`. **Primary family:** SPELLCASTING.
- [x] **mechanic:spellcasting** (**18-level intelligence caster; 25 printed prepared/at-will spells; printed spell list in full source packet**): Audit the full printed 2014 spells, slots/uses and AI choice. Map to shared edition-specific spell effects. Park every outcome-changing missing spell individually; keep source list and exclude only explicitly approved noncombat options.
- [x] **source:trait** (**Spellcasting**): Decompose every named trait into its genuine event trigger, target eligibility, source-defined values, action/save/damage/condition, duration and exit. Bind shared mechanics; only classify neutral when an existing explicit arena rule permits it.
- [x] Prepared spell source→Action binding foundation **specified** (slots already exist; not implemented); [#685](https://github.com/cbw29512/D20-ironpit/issues/685).
- [x] **USER-APPROVED 2026-10-08: all printed source pre-casts apply.** The 2014 Archmage begins with **Mind Blank (8th; 24h; no Concentration) + Stoneskin (4th; up to 1h; Concentration) + Mage Armor (1st; 8h; no Concentration)** as real buffs in the free opening phase before initiative. One printed Concentration, normal spell slot expenditures, no additional optional fourth opening buff, and do not double-count Mage Armor's AC. Later Globe may replace Stoneskin Concentration if legally cast. §7.1 rules contract updated; code/CI remains pending.
- [x] **Rest of printed spell list classified for planning:** generic 2014 save-damage/spell-attack/invisibility/defensive/Concentration/counterspell mechanics apply; approved arena-neutral informational spells remain on source/card without casts; approved Wall of Force, Teleport and Time Stop replacements remain confined to the Archmage's arena loadout. The three source-printed pre-casts are mandatory. No more planning questions; **implementation and Python/browser source admission remain pending**.

**Previously recorded source-specific decisions/dependencies** (preserved, not new approvals):
- **Disguise Self — user decision / queued:** Retain printed spell on source/card; Archmage AI never casts it in Iron Pit (appearance-only, no combat impact). Route via shared arena-inert spell selection, not a bespoke Archmage resolver. Not implemented/certified.
- **Detect Magic — user decision / queued:** Preserve printed spell but never select it as an Iron Pit combat action; source remains intact. Not implemented/certified.
- **Identify — user decision / queued:** Keep the printed spell but never cast it in Iron Pit. Implement by shared noncombat-spell choice exclusion; not certified.
- **Detect Thoughts — user decision / queued:** Printed spell retained; AI never casts it in arena. Shared noncombat-spell selection exclusion; not implemented/certified.

**Source packet:** [#013 in full blueprint](MONSTER_BLOCKER_FIX_BLUEPRINTS_2014.md#13-archmage-spellcasting). **Review completion:** fill all above decisions before implementing; existing code readiness is not evidence of planning closure.

### 014. Assassin

**Planning:** COMPLETE — Assassinate, Evasion, Sneak Attack decisions recorded. No further Assassin policy questions. **Implementation:** pending. **Current blockers:** `source:trait`. **Primary family:** ATTACK RIDERS / MULTICOMPONENT DAMAGE.
- [x] **source:trait** (**Assassinate, Evasion, Sneak Attack planning approved**): Decompose every named trait into its genuine event trigger, target eligibility, source-defined values, action/save/damage/condition, duration and exit. Bind shared mechanics; only classify neutral when an existing explicit arena rule permits it.

**Previously recorded source-specific decisions/dependencies** (preserved, not new approvals):
- [x] **ASSASSINATE USER-APPROVED (2026-10-08):** On round one, when Assassin beats the target's Initiative/acts before it, each qualifying attack against that target is an Assassinate attack: attack-roll Advantage and **automatic critical damage on a hit** (not automatic hit). No separate Surprise prerequisite in the Pit. Stops after Assassin's first turn; source 2014 distinction retained as a specifically approved arena override. PR #664 currently only addresses Advantage; crit-on-hit runtime still needed.
- [x] **Evasion approved:** reuse existing Rogue Dexterity save damage modifier: success = zero, failure = half, with existing Incapacitated constraint. PR #665 pending implementation verification.
- [x] **Sneak Attack agreed reuse:** same generic Rogue once-per-turn +4d6 on weapon hit with Advantage or an eligible nearby ally without Disadvantage; printed name is source/log metadata. PR #666 pending implementation verification.

**Source packet:** [#014 in full blueprint](MONSTER_BLOCKER_FIX_BLUEPRINTS_2014.md#14-assassin-attack-riders-multicomponent-damage). **Review completion:** fill all above decisions before implementing; existing code readiness is not evidence of planning closure.

### 015. Azer

**Planning:** COMPLETE — source-semantic fix already recorded in PR #673; no new rule choice needed. **Implementation:** pending. **Current blockers:** `source:trait`. **Primary family:** PASSIVE RETALIATION / DAMAGE AURA.
- [x] **source:trait** (**Heated Body — planning approved, implementation pending**): Decompose every named trait into its genuine event trigger, target eligibility, source-defined values, action/save/damage/condition, duration and exit. Bind shared mechanics; only classify neutral when an existing explicit arena rule permits it.

**Implementation blueprint approved for planning:**
- [x] Source-authored passive **Heated Body** always active. When a creature touches the Azer or hits it with a melee attack while within 5 feet, that creature takes **1d10 fire** (no extra Attack, Reaction, or resource). A miss, ranged attack, noncontact approach or mere proximity does not trigger. Use universal typed damage, resistance/immunity, melee-hit retaliation; independent real physical contact event only. Preserve separate **Heated Weapons** +1d6 fire already included in its warhammer and **Illumination** (10-ft bright + 10-ft dim) source, not mistakenly folded into Heated Body. Reusable heated-body primitive also serves Salamander/Remorhaz with their own printed dice, but do not switch the active monster review. **Existing PR #673** already carries the proposed Python/browser generic implementation and tests; stale PR requires CI/merge before certification.

**Previously recorded source-specific decisions/dependencies** (preserved, not new approvals):
- **Known directed work:** Heated Body: use existing typed retaliatory fire damage and add/reuse generic contact trigger after checking hit-versus-touch distinction.

**Source packet:** [#015 in full blueprint](MONSTER_BLOCKER_FIX_BLUEPRINTS_2014.md#15-azer-passive-retaliation-damage-aura). **Review completion:** fill all above decisions before implementing; existing code readiness is not evidence of planning closure.

### 016. Balor

**Planning:** COMPLETE — Death Throes, Fire Aura, Longsword critical dice, Whip pull, and no-teleport arena policy all source-resolved. No user question. **Implementation:** pending. **Current blockers:** `attack:incomplete`, `source:trait`. **Primary family:** PASSIVE RETALIATION / DAMAGE AURA.
- [x] **attack:incomplete** (**Longsword; Whip**): Recover full printed damage dice/type, saves/DC, conditions, persistent wounds, target restrictions and lifecycle in source attack schema; prove Python/browser hit resolution.
- [x] **source:trait** (**Death Throes documented; Fire Aura remains**): Decompose every named trait into its genuine event trigger, target eligibility, source-defined values, action/save/damage/condition, duration and exit. Bind shared mechanics; only classify neutral when an existing explicit arena rule permits it.

- [x] **Death Throes (2014 RAW, planning complete; implementation pending):** Trigger the shared death-event resolver **when the Balor actually dies**, even if slain outside its own turn. Before final victory evaluation, apply a **30-foot-radius burst to every creature in range (friend or foe)**. Each rolls its own **DC 20 Dexterity save**; failure **20d6 Fire**, success **half**; apply normal typed defenses. Destroy the Balor's own weapons. Ignite unattended flammable arena objects only when present; default arena has none, so do not invent scenery. Never trigger merely because an undying combatant reached 0 HP; resolve the printed death event once only. No extra action, initiative turn, monster-specific explosion resolver, or summoned creature.

- [x] **Fire Aura:** source-bound passive 3d6 Fire to every creature within 5 ft at the start of each Balor turn; independently 3d6 Fire when a creature touches Balor or successfully hits it with a melee attack from within 5 ft. Ordinary typed defenses, no trigger for miss or mere proximity outside start-turn aura. Reuse shared AoE periodic damage and Heated Body/Fire Shield contact retaliation; no duplicate custom resolver.
- [x] **Longsword:** +14 to hit at 10 ft, 3d8+8 Slashing and 3d8 Lightning. On critical hit, roll each damage dice pool *three* times rather than the usual two; flat modifiers once. Universal critical-multiplier/source parameter, no Balor-only engine path.
- [x] **Whip:** +14 to hit at 30 ft, 2d6+8 Slashing and 3d6 Fire; DC 20 Strength save on hit, failure pulls the target up to 25 ft toward Balor using shared forced movement; success no pull. Apply damage regardless of pull-save success. Preserve actual grid bounds, collision and legal placement.
- [x] **Teleport:** printed on original source and card, arena AI never chooses relocation per existing Pit no-teleport policy. No substitute Action. All decisions above are planning-only, not verified runtime implementations.

**Source packet:** [#016 in full blueprint](MONSTER_BLOCKER_FIX_BLUEPRINTS_2014.md#16-balor-passive-retaliation-damage-aura). **Review completion:** fill all above decisions before implementing; existing code readiness is not evidence of planning closure.

### 017. Banshee

**Planning:** REVIEW NEXT — blueprint drafted. **Implementation:** pending. **Current blockers:** `source:extra-action`, `source:trait`. **Primary family:** FEAR / CHARM / STATUS.
- [ ] **source:extra-action** (review candidate actions: **Horrifying Visage; Wail (1/Day)**): Identify each special printed Action, legality, targeting/area, source save, cost, duration, recharge and AI selection. Reuse shared area/save/action/movement/resource capabilities or park the specific missing semantic clause.
- [ ] **source:trait** (**Detect Life**): Decompose every named trait into its genuine event trigger, target eligibility, source-defined values, action/save/damage/condition, duration and exit. Bind shared mechanics; only classify neutral when an existing explicit arena rule permits it.

**Source packet:** [#017 in full blueprint](MONSTER_BLOCKER_FIX_BLUEPRINTS_2014.md#17-banshee-fear-charm-status). **Review completion:** fill all above decisions before implementing; existing code readiness is not evidence of planning closure.

### 018. Barbed Devil

**Planning:** REVIEW NEXT — blueprint drafted. **Implementation:** pending. **Current blockers:** `attack:range`, `source:trait`. **Primary family:** PASSIVE RETALIATION / DAMAGE AURA.
- [ ] **attack:range**: Restore exact reach and ranged normal/long bands from source and use shared range legality/disadvantage.
- [ ] **source:trait** (**Barbed Hide**): Decompose every named trait into its genuine event trigger, target eligibility, source-defined values, action/save/damage/condition, duration and exit. Bind shared mechanics; only classify neutral when an existing explicit arena rule permits it.

**Previously recorded source-specific decisions/dependencies** (preserved, not new approvals):
- **Known directed work:** Barbed Hide: reuse contact retaliation; verify printed trigger and damage.

**Source packet:** [#018 in full blueprint](MONSTER_BLOCKER_FIX_BLUEPRINTS_2014.md#18-barbed-devil-passive-retaliation-damage-aura). **Review completion:** fill all above decisions before implementing; existing code readiness is not evidence of planning closure.

### 019. Basilisk

**Planning:** COMPLETE — 2014 Petrifying Gaze source sequence + previously agreed universal gaze/avert rule; no new policy question. **Implementation:** pending. **Current blockers:** `source:trait`. **Primary family:** GAZE / SIGHT / INVISIBILITY.
- [x] **source:trait** (**Petrifying Gaze**): Decompose every named trait into its genuine event trigger, target eligibility, source-defined values, action/save/damage/condition, duration and exit. Bind shared mechanics; only classify neutral when an existing explicit arena rule permits it.

**Previously recorded source-specific decisions/dependencies** (preserved, not new approvals):
- **Known directed work:** Petrifying Gaze: source-triggered sight/save and staged Restrained/Petrified timing; check generic gaze predicate.

- [x] **Petrifying Gaze:** source start-of-target-turn mutual sight and 30-ft predicate, DC12 CON; fail Restrained, repeat at end of next turn, fail again Petrified until eligible cure; use prior generic 2014 gaze-avoidance decision, which makes source unseen to averter but doesn't confer globally Blinded. Printed self-reflection and incapacitated exceptions remain source binding. Shared with Medusa, no separate implementation branch; #676.

**Source packet:** [#019 in full blueprint](MONSTER_BLOCKER_FIX_BLUEPRINTS_2014.md#19-basilisk-gaze-sight-invisibility). **Review completion:** fill all above decisions before implementing; existing code readiness is not evidence of planning closure.

### 020. Bearded Devil

**Planning:** REVIEW NEXT — blueprint drafted. **Implementation:** pending. **Current blockers:** `attack:complex`, `attack:incomplete`, `source:trait`. **Primary family:** ALLY / AURA.
- [ ] **attack:complex** (**Beard**): Compose base weapon attack with all on-hit and target-specific riders; use shared damage/save/condition code and independent typed components.
- [ ] **attack:incomplete** (**Beard**): Recover full printed damage dice/type, saves/DC, conditions, persistent wounds, target restrictions and lifecycle in source attack schema; prove Python/browser hit resolution.
- [ ] **source:trait** (**Steadfast**): Decompose every named trait into its genuine event trigger, target eligibility, source-defined values, action/save/damage/condition, duration and exit. Bind shared mechanics; only classify neutral when an existing explicit arena rule permits it.

**Previously recorded source-specific decisions/dependencies** (preserved, not new approvals):
- **Known directed work:** M-025 Steadfast: conditional Frightened immunity requires live active ally; PR #654 partially implemented, not certified. Then Beard: save -> Poisoned plus healing restriction; Glaive: stacking 1d10 ongoing wound, cleared on magical healing (Pit globally disallows Medicine checks).

**Source packet:** [#020 in full blueprint](MONSTER_BLOCKER_FIX_BLUEPRINTS_2014.md#20-bearded-devil-ally-aura). **Review completion:** fill all above decisions before implementing; existing code readiness is not evidence of planning closure.

### 021. Behir

**Planning:** REVIEW NEXT — blueprint drafted. **Implementation:** pending. **Current blockers:** `mechanic:recharge`, `source:extra-action`. **Primary family:** RESTRAINT / SWALLOW.
- [ ] **mechanic:recharge**: Bind Recharge threshold to the exact printed Action and source-owned resource/turn roll. Certification requires the recharged Action to be legal or formally excluded.
- [ ] **source:extra-action** (review candidate actions: **Lightning Breath (Recharge 5–6); Swallow**): Identify each special printed Action, legality, targeting/area, source save, cost, duration, recharge and AI selection. Reuse shared area/save/action/movement/resource capabilities or park the specific missing semantic clause.

**Source packet:** [#021 in full blueprint](MONSTER_BLOCKER_FIX_BLUEPRINTS_2014.md#21-behir-restraint-swallow). **Review completion:** fill all above decisions before implementing; existing code readiness is not evidence of planning closure.

### 022. Black Pudding

**Planning:** REVIEW NEXT — blueprint drafted. **Implementation:** pending. **Current blockers:** `attack:incomplete`, `source:trait`. **Primary family:** PASSIVE RETALIATION / DAMAGE AURA.
- [ ] **attack:incomplete** (**Pseudopod**): Recover full printed damage dice/type, saves/DC, conditions, persistent wounds, target restrictions and lifecycle in source attack schema; prove Python/browser hit resolution.
- [ ] **source:trait** (**Corrosive Form**): Decompose every named trait into its genuine event trigger, target eligibility, source-defined values, action/save/damage/condition, duration and exit. Bind shared mechanics; only classify neutral when an existing explicit arena rule permits it.

**Source packet:** [#022 in full blueprint](MONSTER_BLOCKER_FIX_BLUEPRINTS_2014.md#22-black-pudding-passive-retaliation-damage-aura). **Review completion:** fill all above decisions before implementing; existing code readiness is not evidence of planning closure.

### 023. Bugbear

**Planning:** REVIEW NEXT — blueprint drafted. **Implementation:** pending. **Current blockers:** `attack:complex`, `source:trait`. **Primary family:** ATTACK RIDERS / MULTICOMPONENT DAMAGE.
- [ ] **attack:complex**: Compose base weapon attack with all on-hit and target-specific riders; use shared damage/save/condition code and independent typed components.
- [ ] **source:trait** (**Surprise Attack**): Decompose every named trait into its genuine event trigger, target eligibility, source-defined values, action/save/damage/condition, duration and exit. Bind shared mechanics; only classify neutral when an existing explicit arena rule permits it.

**Source packet:** [#023 in full blueprint](MONSTER_BLOCKER_FIX_BLUEPRINTS_2014.md#23-bugbear-attack-riders-multicomponent-damage). **Review completion:** fill all above decisions before implementing; existing code readiness is not evidence of planning closure.

### 024. Bulette

**Planning:** REVIEW NEXT — blueprint drafted. **Implementation:** pending. **Current blockers:** `source:extra-action`. **Primary family:** AREA / SAVE ACTIONS.
- [ ] **source:extra-action** (review candidate actions: **Deadly Leap**): Identify each special printed Action, legality, targeting/area, source save, cost, duration, recharge and AI selection. Reuse shared area/save/action/movement/resource capabilities or park the specific missing semantic clause.

**Previously recorded source-specific decisions/dependencies** (preserved, not new approvals):
- **Deadly Leap queued / approved arena semantics:** Landing occupies a 10×10-foot (2×2 square) AoE; every enemy overlapping a landing square resolves its own DC 16 Strength-or-Dexterity (better available) save. On failure, roll 3d6+4 bludgeoning plus 3d6+4 slashing, apply typed resistance/immunity/vulnerability independently, and inflict shared Prone. On success, half damage per component after the save, apply defenses, no Prone; 5-ft push deliberately omitted in Iron Pit. A legal 15-ft jump remains required. AI prioritizes leap on opening turn when eligible; ability remains available subsequently. **Queued, not implemented/certified.**

**Source packet:** [#024 in full blueprint](MONSTER_BLOCKER_FIX_BLUEPRINTS_2014.md#24-bulette-area-save-actions). **Review completion:** fill all above decisions before implementing; existing code readiness is not evidence of planning closure.

### 025. Chain Devil

**Planning:** REVIEW NEXT — blueprint drafted. **Implementation:** pending. **Current blockers:** `attack:complex`, `source:extra-action`, `source:reaction`. **Primary family:** RECHARGE / RESOURCES.
- [ ] **attack:complex**: Compose base weapon attack with all on-hit and target-specific riders; use shared damage/save/condition code and independent typed components.
- [ ] **source:extra-action** (review candidate actions: **Animate Chains (Recharges after a Short or Long Rest)**): Identify each special printed Action, legality, targeting/area, source save, cost, duration, recharge and AI selection. Reuse shared area/save/action/movement/resource capabilities or park the specific missing semantic clause.
- [ ] **source:reaction** (**Unnerving Mask**): Model genuine triggering event, timing, eligibility, reaction cost, source effect and reset in shared reaction dispatch; prove production Python/browser calls, not helper-only tests.

**Source packet:** [#025 in full blueprint](MONSTER_BLOCKER_FIX_BLUEPRINTS_2014.md#25-chain-devil-recharge-resources). **Review completion:** fill all above decisions before implementing; existing code readiness is not evidence of planning closure.

### 026. Chuul

**Planning:** REVIEW NEXT — blueprint drafted. **Implementation:** pending. **Current blockers:** `attack:incomplete`, `multiattack:complex`, `source:extra-action`, `source:trait`. **Primary family:** RESTRAINT / SWALLOW.
- [ ] **attack:incomplete** (**Pincer**): Recover full printed damage dice/type, saves/DC, conditions, persistent wounds, target restrictions and lifecycle in source attack schema; prove Python/browser hit resolution.
- [ ] **multiattack:complex**: Bind legal attack order, alternative forms, target limitations and conditional count to shared multiattack selector; no invented extra attacks.
- [ ] **source:extra-action** (review candidate actions: **Tentacles**): Identify each special printed Action, legality, targeting/area, source save, cost, duration, recharge and AI selection. Reuse shared area/save/action/movement/resource capabilities or park the specific missing semantic clause.
- [ ] **source:trait** (**Sense Magic**): Decompose every named trait into its genuine event trigger, target eligibility, source-defined values, action/save/damage/condition, duration and exit. Bind shared mechanics; only classify neutral when an existing explicit arena rule permits it.

**Source packet:** [#026 in full blueprint](MONSTER_BLOCKER_FIX_BLUEPRINTS_2014.md#26-chuul-restraint-swallow). **Review completion:** fill all above decisions before implementing; existing code readiness is not evidence of planning closure.

### 027. Clay Golem

**Planning:** REVIEW NEXT — blueprint drafted. **Implementation:** pending. **Current blockers:** `mechanic:recharge`, `source:extra-action`. **Primary family:** RECHARGE / RESOURCES.
- [ ] **mechanic:recharge**: Bind Recharge threshold to the exact printed Action and source-owned resource/turn roll. Certification requires the recharged Action to be legal or formally excluded.
- [ ] **source:extra-action** (review candidate actions: **Haste (Recharge 5–6)**): Identify each special printed Action, legality, targeting/area, source save, cost, duration, recharge and AI selection. Reuse shared area/save/action/movement/resource capabilities or park the specific missing semantic clause.

**Source packet:** [#027 in full blueprint](MONSTER_BLOCKER_FIX_BLUEPRINTS_2014.md#27-clay-golem-recharge-resources). **Review completion:** fill all above decisions before implementing; existing code readiness is not evidence of planning closure.

### 028. Cloaker

**Planning:** REVIEW NEXT — blueprint drafted. **Implementation:** pending. **Current blockers:** `attack:incomplete`, `source:extra-action`, `source:trait`. **Primary family:** GAZE / SIGHT / INVISIBILITY.
- [ ] **attack:incomplete** (**Bite**): Recover full printed damage dice/type, saves/DC, conditions, persistent wounds, target restrictions and lifecycle in source attack schema; prove Python/browser hit resolution.
- [ ] **source:extra-action** (review candidate actions: **Moan; Phantasms (Recharges after a Short or Long Rest)**): Identify each special printed Action, legality, targeting/area, source save, cost, duration, recharge and AI selection. Reuse shared area/save/action/movement/resource capabilities or park the specific missing semantic clause.
- [ ] **source:trait** (**Damage Transfer; Light Sensitivity**): Decompose every named trait into its genuine event trigger, target eligibility, source-defined values, action/save/damage/condition, duration and exit. Bind shared mechanics; only classify neutral when an existing explicit arena rule permits it.

**Source packet:** [#028 in full blueprint](MONSTER_BLOCKER_FIX_BLUEPRINTS_2014.md#28-cloaker-gaze-sight-invisibility). **Review completion:** fill all above decisions before implementing; existing code readiness is not evidence of planning closure.

### 029. Cloud Giant

**Planning:** REVIEW NEXT — blueprint drafted. **Implementation:** pending. **Current blockers:** `mechanic:spellcasting`, `source:trait`. **Primary family:** SPELLCASTING.
- [ ] **mechanic:spellcasting**: Audit the full printed 2014 spells, slots/uses and AI choice. Map to shared edition-specific spell effects. Park every outcome-changing missing spell individually; keep source list and exclude only explicitly approved noncombat options.
- [ ] **source:trait** (**Innate Spellcasting**): Decompose every named trait into its genuine event trigger, target eligibility, source-defined values, action/save/damage/condition, duration and exit. Bind shared mechanics; only classify neutral when an existing explicit arena rule permits it.

**Source packet:** [#029 in full blueprint](MONSTER_BLOCKER_FIX_BLUEPRINTS_2014.md#29-cloud-giant-spellcasting). **Review completion:** fill all above decisions before implementing; existing code readiness is not evidence of planning closure.

### 030. Couatl

**Planning:** REVIEW NEXT — blueprint drafted. **Implementation:** pending. **Current blockers:** `attack:incomplete`, `mechanic:spellcasting`, `source:extra-action`, `source:trait`. **Primary family:** SHAPECHANGE / TRANSFORMATION.
- [ ] **attack:incomplete** (**Bite**): Recover full printed damage dice/type, saves/DC, conditions, persistent wounds, target restrictions and lifecycle in source attack schema; prove Python/browser hit resolution.
- [ ] **mechanic:spellcasting**: Audit the full printed 2014 spells, slots/uses and AI choice. Map to shared edition-specific spell effects. Park every outcome-changing missing spell individually; keep source list and exclude only explicitly approved noncombat options.
- [ ] **source:extra-action** (review candidate actions: **Change Shape**): Identify each special printed Action, legality, targeting/area, source save, cost, duration, recharge and AI selection. Reuse shared area/save/action/movement/resource capabilities or park the specific missing semantic clause.
- [ ] **source:trait** (**Innate Spellcasting; Shielded Mind**): Decompose every named trait into its genuine event trigger, target eligibility, source-defined values, action/save/damage/condition, duration and exit. Bind shared mechanics; only classify neutral when an existing explicit arena rule permits it.

**Source packet:** [#030 in full blueprint](MONSTER_BLOCKER_FIX_BLUEPRINTS_2014.md#30-couatl-shapechange-transformation). **Review completion:** fill all above decisions before implementing; existing code readiness is not evidence of planning closure.

### 031. Cult Fanatic

**Planning:** REVIEW NEXT — blueprint drafted. **Implementation:** pending. **Current blockers:** `mechanic:spellcasting`, `source:trait`. **Primary family:** SPELLCASTING.
- [ ] **mechanic:spellcasting** (**4-level wisdom caster; 8 printed prepared/at-will spells; printed spell list in full source packet**): Audit the full printed 2014 spells, slots/uses and AI choice. Map to shared edition-specific spell effects. Park every outcome-changing missing spell individually; keep source list and exclude only explicitly approved noncombat options.
- [ ] **source:trait** (**Spellcasting**): Decompose every named trait into its genuine event trigger, target eligibility, source-defined values, action/save/damage/condition, duration and exit. Bind shared mechanics; only classify neutral when an existing explicit arena rule permits it.

**Source packet:** [#031 in full blueprint](MONSTER_BLOCKER_FIX_BLUEPRINTS_2014.md#31-cult-fanatic-spellcasting). **Review completion:** fill all above decisions before implementing; existing code readiness is not evidence of planning closure.

### 032. Darkmantle

**Planning:** REVIEW NEXT — blueprint drafted. **Implementation:** pending. **Current blockers:** `attack:incomplete`, `source:extra-action`. **Primary family:** RECHARGE / RESOURCES.
- [ ] **attack:incomplete** (**Crush**): Recover full printed damage dice/type, saves/DC, conditions, persistent wounds, target restrictions and lifecycle in source attack schema; prove Python/browser hit resolution.
- [ ] **source:extra-action** (review candidate actions: **Darkness Aura (1/Day)**): Identify each special printed Action, legality, targeting/area, source save, cost, duration, recharge and AI selection. Reuse shared area/save/action/movement/resource capabilities or park the specific missing semantic clause.

**Source packet:** [#032 in full blueprint](MONSTER_BLOCKER_FIX_BLUEPRINTS_2014.md#32-darkmantle-recharge-resources). **Review completion:** fill all above decisions before implementing; existing code readiness is not evidence of planning closure.

### 033. Deep Gnome (Svirfneblin)

**Planning:** REVIEW NEXT — blueprint drafted. **Implementation:** pending. **Current blockers:** `mechanic:spellcasting`, `source:trait`. **Primary family:** SPELLCASTING.
- [ ] **mechanic:spellcasting**: Audit the full printed 2014 spells, slots/uses and AI choice. Map to shared edition-specific spell effects. Park every outcome-changing missing spell individually; keep source list and exclude only explicitly approved noncombat options.
- [ ] **source:trait** (**Innate Spellcasting**): Decompose every named trait into its genuine event trigger, target eligibility, source-defined values, action/save/damage/condition, duration and exit. Bind shared mechanics; only classify neutral when an existing explicit arena rule permits it.

**Source packet:** [#033 in full blueprint](MONSTER_BLOCKER_FIX_BLUEPRINTS_2014.md#33-deep-gnome-svirfneblin-spellcasting). **Review completion:** fill all above decisions before implementing; existing code readiness is not evidence of planning closure.

### 034. Deva

**Planning:** REVIEW NEXT — blueprint drafted. **Implementation:** pending. **Current blockers:** `mechanic:spellcasting`, `source:extra-action`, `source:trait`. **Primary family:** SHAPECHANGE / TRANSFORMATION.
- [ ] **mechanic:spellcasting**: Audit the full printed 2014 spells, slots/uses and AI choice. Map to shared edition-specific spell effects. Park every outcome-changing missing spell individually; keep source list and exclude only explicitly approved noncombat options.
- [ ] **source:extra-action** (review candidate actions: **Healing Touch (3/Day); Change Shape**): Identify each special printed Action, legality, targeting/area, source save, cost, duration, recharge and AI selection. Reuse shared area/save/action/movement/resource capabilities or park the specific missing semantic clause.
- [ ] **source:trait** (**Innate Spellcasting**): Decompose every named trait into its genuine event trigger, target eligibility, source-defined values, action/save/damage/condition, duration and exit. Bind shared mechanics; only classify neutral when an existing explicit arena rule permits it.

**Source packet:** [#034 in full blueprint](MONSTER_BLOCKER_FIX_BLUEPRINTS_2014.md#34-deva-shapechange-transformation). **Review completion:** fill all above decisions before implementing; existing code readiness is not evidence of planning closure.

### 035. Djinni

**Planning:** REVIEW NEXT — blueprint drafted. **Implementation:** pending. **Current blockers:** `attack:incomplete`, `mechanic:spellcasting`, `source:extra-action`, `source:trait`. **Primary family:** DEATH / HP-LIFECYCLE.
- [ ] **attack:incomplete** (**Scimitar**): Recover full printed damage dice/type, saves/DC, conditions, persistent wounds, target restrictions and lifecycle in source attack schema; prove Python/browser hit resolution.
- [ ] **mechanic:spellcasting**: Audit the full printed 2014 spells, slots/uses and AI choice. Map to shared edition-specific spell effects. Park every outcome-changing missing spell individually; keep source list and exclude only explicitly approved noncombat options.
- [ ] **source:extra-action** (review candidate actions: **Create Whirlwind**): Identify each special printed Action, legality, targeting/area, source save, cost, duration, recharge and AI selection. Reuse shared area/save/action/movement/resource capabilities or park the specific missing semantic clause.
- [ ] **source:trait** (**Elemental Demise; Innate Spellcasting**): Decompose every named trait into its genuine event trigger, target eligibility, source-defined values, action/save/damage/condition, duration and exit. Bind shared mechanics; only classify neutral when an existing explicit arena rule permits it.

**Source packet:** [#035 in full blueprint](MONSTER_BLOCKER_FIX_BLUEPRINTS_2014.md#35-djinni-death-hp-lifecycle). **Review completion:** fill all above decisions before implementing; existing code readiness is not evidence of planning closure.

### 036. Doppelganger

**Planning:** REVIEW NEXT — blueprint drafted. **Implementation:** pending. **Current blockers:** `attack:complex`, `source:extra-action`, `source:trait`. **Primary family:** SHAPECHANGE / TRANSFORMATION.
- [ ] **attack:complex**: Compose base weapon attack with all on-hit and target-specific riders; use shared damage/save/condition code and independent typed components.
- [ ] **source:extra-action** (review candidate actions: **Read Thoughts**): Identify each special printed Action, legality, targeting/area, source save, cost, duration, recharge and AI selection. Reuse shared area/save/action/movement/resource capabilities or park the specific missing semantic clause.
- [ ] **source:trait** (**Shapechanger; Ambusher; Surprise Attack**): Decompose every named trait into its genuine event trigger, target eligibility, source-defined values, action/save/damage/condition, duration and exit. Bind shared mechanics; only classify neutral when an existing explicit arena rule permits it.

**Source packet:** [#036 in full blueprint](MONSTER_BLOCKER_FIX_BLUEPRINTS_2014.md#36-doppelganger-shapechange-transformation). **Review completion:** fill all above decisions before implementing; existing code readiness is not evidence of planning closure.

### 037. Dretch

**Planning:** REVIEW NEXT — blueprint drafted. **Implementation:** pending. **Current blockers:** `source:extra-action`. **Primary family:** FEAR / CHARM / STATUS.
- [ ] **source:extra-action** (review candidate actions: **Fetid Cloud (1/Day)**): Identify each special printed Action, legality, targeting/area, source save, cost, duration, recharge and AI selection. Reuse shared area/save/action/movement/resource capabilities or park the specific missing semantic clause.

**Previously recorded source-specific decisions/dependencies** (preserved, not new approvals):
- **Fetid Cloud user-approved fix queued:** Treat as a source-owned 1/day area poison: shared Poisoned + separate action/bonus exclusivity and reaction suppression, delivered by existing saving throw and timed-effect primitives. Do not change the global Poisoned effect; retain exact printed DC/radius/duration/immunity terms for implementation. Source/card retains the printed name. **Not coded or certified.**

**Source packet:** [#037 in full blueprint](MONSTER_BLOCKER_FIX_BLUEPRINTS_2014.md#37-dretch-fear-charm-status). **Review completion:** fill all above decisions before implementing; existing code readiness is not evidence of planning closure.

### 038. Drider

**Planning:** REVIEW NEXT — blueprint drafted. **Implementation:** pending. **Current blockers:** `mechanic:spellcasting`, `source:trait`. **Primary family:** SPELLCASTING.
- [ ] **mechanic:spellcasting**: Audit the full printed 2014 spells, slots/uses and AI choice. Map to shared edition-specific spell effects. Park every outcome-changing missing spell individually; keep source list and exclude only explicitly approved noncombat options.
- [ ] **source:trait** (**Innate Spellcasting**): Decompose every named trait into its genuine event trigger, target eligibility, source-defined values, action/save/damage/condition, duration and exit. Bind shared mechanics; only classify neutral when an existing explicit arena rule permits it.

**Source packet:** [#038 in full blueprint](MONSTER_BLOCKER_FIX_BLUEPRINTS_2014.md#38-drider-spellcasting). **Review completion:** fill all above decisions before implementing; existing code readiness is not evidence of planning closure.

### 039. Drow

**Planning:** REVIEW NEXT — blueprint drafted. **Implementation:** pending. **Current blockers:** `attack:complex`, `mechanic:spellcasting`, `source:trait`. **Primary family:** SPELLCASTING.
- [ ] **attack:complex**: Compose base weapon attack with all on-hit and target-specific riders; use shared damage/save/condition code and independent typed components.
- [ ] **mechanic:spellcasting**: Audit the full printed 2014 spells, slots/uses and AI choice. Map to shared edition-specific spell effects. Park every outcome-changing missing spell individually; keep source list and exclude only explicitly approved noncombat options.
- [ ] **source:trait** (**Innate Spellcasting**): Decompose every named trait into its genuine event trigger, target eligibility, source-defined values, action/save/damage/condition, duration and exit. Bind shared mechanics; only classify neutral when an existing explicit arena rule permits it.

**Source packet:** [#039 in full blueprint](MONSTER_BLOCKER_FIX_BLUEPRINTS_2014.md#39-drow-spellcasting). **Review completion:** fill all above decisions before implementing; existing code readiness is not evidence of planning closure.

### 040. Druid

**Planning:** REVIEW NEXT — blueprint drafted. **Implementation:** pending. **Current blockers:** `mechanic:spellcasting`, `source:trait`. **Primary family:** SPELLCASTING.
- [ ] **mechanic:spellcasting** (**4-level wisdom caster; 9 printed prepared/at-will spells; printed spell list in full source packet**): Audit the full printed 2014 spells, slots/uses and AI choice. Map to shared edition-specific spell effects. Park every outcome-changing missing spell individually; keep source list and exclude only explicitly approved noncombat options.
- [ ] **source:trait** (**Spellcasting**): Decompose every named trait into its genuine event trigger, target eligibility, source-defined values, action/save/damage/condition, duration and exit. Bind shared mechanics; only classify neutral when an existing explicit arena rule permits it.

**Source packet:** [#040 in full blueprint](MONSTER_BLOCKER_FIX_BLUEPRINTS_2014.md#40-druid-spellcasting). **Review completion:** fill all above decisions before implementing; existing code readiness is not evidence of planning closure.

### 041. Dryad

**Planning:** REVIEW NEXT — blueprint drafted. **Implementation:** pending. **Current blockers:** `mechanic:spellcasting`, `source:extra-action`, `source:trait`. **Primary family:** FEAR / CHARM / STATUS.
- [ ] **mechanic:spellcasting**: Audit the full printed 2014 spells, slots/uses and AI choice. Map to shared edition-specific spell effects. Park every outcome-changing missing spell individually; keep source list and exclude only explicitly approved noncombat options.
- [ ] **source:extra-action** (review candidate actions: **Fey Charm**): Identify each special printed Action, legality, targeting/area, source save, cost, duration, recharge and AI selection. Reuse shared area/save/action/movement/resource capabilities or park the specific missing semantic clause.
- [ ] **source:trait** (**Innate Spellcasting; Speak with Beasts and Plants; Tree Stride**): Decompose every named trait into its genuine event trigger, target eligibility, source-defined values, action/save/damage/condition, duration and exit. Bind shared mechanics; only classify neutral when an existing explicit arena rule permits it.

**Source packet:** [#041 in full blueprint](MONSTER_BLOCKER_FIX_BLUEPRINTS_2014.md#41-dryad-fear-charm-status). **Review completion:** fill all above decisions before implementing; existing code readiness is not evidence of planning closure.

### 042. Duergar

**Planning:** REVIEW NEXT — blueprint drafted. **Implementation:** pending. **Current blockers:** `attack:incomplete`, `source:extra-action`, `source:trait`. **Primary family:** GAZE / SIGHT / INVISIBILITY.
- [ ] **attack:incomplete** (**War Pick; Javelin**): Recover full printed damage dice/type, saves/DC, conditions, persistent wounds, target restrictions and lifecycle in source attack schema; prove Python/browser hit resolution.
- [ ] **source:extra-action** (review candidate actions: **Enlarge (Recharges after a Short or Long Rest); Invisibility (Recharges after a Short or Long Rest)**): Identify each special printed Action, legality, targeting/area, source save, cost, duration, recharge and AI selection. Reuse shared area/save/action/movement/resource capabilities or park the specific missing semantic clause.
- [ ] **source:trait** (**Duergar Resilience**): Decompose every named trait into its genuine event trigger, target eligibility, source-defined values, action/save/damage/condition, duration and exit. Bind shared mechanics; only classify neutral when an existing explicit arena rule permits it.

**Source packet:** [#042 in full blueprint](MONSTER_BLOCKER_FIX_BLUEPRINTS_2014.md#42-duergar-gaze-sight-invisibility). **Review completion:** fill all above decisions before implementing; existing code readiness is not evidence of planning closure.

### 043. Dust Mephit

**Planning:** REVIEW NEXT — blueprint drafted. **Implementation:** pending. **Current blockers:** `mechanic:recharge`, `mechanic:spellcasting`, `source:extra-action`, `source:trait`. **Primary family:** DEATH / HP-LIFECYCLE.
- [ ] **mechanic:recharge**: Bind Recharge threshold to the exact printed Action and source-owned resource/turn roll. Certification requires the recharged Action to be legal or formally excluded.
- [ ] **mechanic:spellcasting**: Audit the full printed 2014 spells, slots/uses and AI choice. Map to shared edition-specific spell effects. Park every outcome-changing missing spell individually; keep source list and exclude only explicitly approved noncombat options.
- [ ] **source:extra-action** (review candidate actions: **Blinding Breath (Recharge 6)**): Identify each special printed Action, legality, targeting/area, source save, cost, duration, recharge and AI selection. Reuse shared area/save/action/movement/resource capabilities or park the specific missing semantic clause.
- [ ] **source:trait** (**Death Burst; Innate Spellcasting**): Decompose every named trait into its genuine event trigger, target eligibility, source-defined values, action/save/damage/condition, duration and exit. Bind shared mechanics; only classify neutral when an existing explicit arena rule permits it.

**Source packet:** [#043 in full blueprint](MONSTER_BLOCKER_FIX_BLUEPRINTS_2014.md#43-dust-mephit-death-hp-lifecycle). **Review completion:** fill all above decisions before implementing; existing code readiness is not evidence of planning closure.

### 044. Efreeti

**Planning:** REVIEW NEXT — blueprint drafted. **Implementation:** pending. **Current blockers:** `attack:range`, `mechanic:spellcasting`, `source:trait`. **Primary family:** DEATH / HP-LIFECYCLE.
- [ ] **attack:range**: Restore exact reach and ranged normal/long bands from source and use shared range legality/disadvantage.
- [ ] **mechanic:spellcasting**: Audit the full printed 2014 spells, slots/uses and AI choice. Map to shared edition-specific spell effects. Park every outcome-changing missing spell individually; keep source list and exclude only explicitly approved noncombat options.
- [ ] **source:trait** (**Elemental Demise; Innate Spellcasting**): Decompose every named trait into its genuine event trigger, target eligibility, source-defined values, action/save/damage/condition, duration and exit. Bind shared mechanics; only classify neutral when an existing explicit arena rule permits it.

**Source packet:** [#044 in full blueprint](MONSTER_BLOCKER_FIX_BLUEPRINTS_2014.md#44-efreeti-death-hp-lifecycle). **Review completion:** fill all above decisions before implementing; existing code readiness is not evidence of planning closure.

### 045. Erinyes

**Planning:** REVIEW NEXT — blueprint drafted. **Implementation:** pending. **Current blockers:** `attack:incomplete`, `source:trait`. **Primary family:** ATTACK RIDERS / MULTICOMPONENT DAMAGE.
- [ ] **attack:incomplete** (**Longbow**): Recover full printed damage dice/type, saves/DC, conditions, persistent wounds, target restrictions and lifecycle in source attack schema; prove Python/browser hit resolution.
- [ ] **source:trait** (**Hellish Weapons**): Decompose every named trait into its genuine event trigger, target eligibility, source-defined values, action/save/damage/condition, duration and exit. Bind shared mechanics; only classify neutral when an existing explicit arena rule permits it.

**Source packet:** [#045 in full blueprint](MONSTER_BLOCKER_FIX_BLUEPRINTS_2014.md#45-erinyes-attack-riders-multicomponent-damage). **Review completion:** fill all above decisions before implementing; existing code readiness is not evidence of planning closure.

### 046. Ettercap

**Planning:** REVIEW NEXT — blueprint drafted. **Implementation:** pending. **Current blockers:** `attack:complex`, `attack:damage-type`, `mechanic:recharge`. **Primary family:** RECHARGE / RESOURCES.
- [ ] **attack:complex**: Compose base weapon attack with all on-hit and target-specific riders; use shared damage/save/condition code and independent typed components.
- [ ] **attack:damage-type**: Preserve each typed damage component and apply defenses separately and save-halving in both engines.
- [ ] **mechanic:recharge**: Bind Recharge threshold to the exact printed Action and source-owned resource/turn roll. Certification requires the recharged Action to be legal or formally excluded.

**Source packet:** [#046 in full blueprint](MONSTER_BLOCKER_FIX_BLUEPRINTS_2014.md#46-ettercap-recharge-resources). **Review completion:** fill all above decisions before implementing; existing code readiness is not evidence of planning closure.

### 047. Fire Elemental

**Planning:** REVIEW NEXT — blueprint drafted. **Implementation:** pending. **Current blockers:** `attack:complex`, `source:trait`. **Primary family:** PASSIVE RETALIATION / DAMAGE AURA.
- [ ] **attack:complex**: Compose base weapon attack with all on-hit and target-specific riders; use shared damage/save/condition code and independent typed components.
- [ ] **source:trait** (**Fire Form; Water Susceptibility**): Decompose every named trait into its genuine event trigger, target eligibility, source-defined values, action/save/damage/condition, duration and exit. Bind shared mechanics; only classify neutral when an existing explicit arena rule permits it.

**Previously recorded source-specific decisions/dependencies** (preserved, not new approvals):
- **Known directed work:** Fire Form/Water Susceptibility: reuse contact/fire application and damage-from-environment primitives; retain Pit environment policy.

**Source packet:** [#047 in full blueprint](MONSTER_BLOCKER_FIX_BLUEPRINTS_2014.md#47-fire-elemental-passive-retaliation-damage-aura). **Review completion:** fill all above decisions before implementing; existing code readiness is not evidence of planning closure.

### 048. Flameskull

**Planning:** REVIEW NEXT — blueprint drafted. **Implementation:** pending. **Current blockers:** `attack:range`, `mechanic:spellcasting`, `source:trait`. **Primary family:** SPELLCASTING.
- [ ] **attack:range**: Restore exact reach and ranged normal/long bands from source and use shared range legality/disadvantage.
- [ ] **mechanic:spellcasting** (**5-level intelligence caster; 6 printed prepared/at-will spells; printed spell list in full source packet**): Audit the full printed 2014 spells, slots/uses and AI choice. Map to shared edition-specific spell effects. Park every outcome-changing missing spell individually; keep source list and exclude only explicitly approved noncombat options.
- [ ] **source:trait** (**Spellcasting**): Decompose every named trait into its genuine event trigger, target eligibility, source-defined values, action/save/damage/condition, duration and exit. Bind shared mechanics; only classify neutral when an existing explicit arena rule permits it.

**Source packet:** [#048 in full blueprint](MONSTER_BLOCKER_FIX_BLUEPRINTS_2014.md#48-flameskull-spellcasting). **Review completion:** fill all above decisions before implementing; existing code readiness is not evidence of planning closure.

### 049. Frog

**Planning:** COMPLETE — original source has no legal damage attack; established arena-neutral classification preserved, no invented attack or policy question. **Implementation:** pending. **Current blockers:** `arena:neutral`. **Primary family:** SOURCE-ONLY / ARENA POLICY.
- [x] **arena:neutral**: Verify existing no-combat-action arena policy and source text; never certify invented offense.

**Previously recorded source-specific decisions/dependencies** (preserved, not new approvals):
- **Known directed work:** No printed meaningful arena attack: preserve arena-neutral status.

- [x] **Noncombat source admission:** retain the printed Frog and arena-neutral classification; no fake Bite, damage dice or combat AI. This is a source rule, not a new user decision. Runtime/source certification independent.

**Source packet:** [#049 in full blueprint](MONSTER_BLOCKER_FIX_BLUEPRINTS_2014.md#49-frog-source-only-arena-policy). **Review completion:** fill all above decisions before implementing; existing code readiness is not evidence of planning closure.

### 050. Gelatinous Cube

**Planning:** REVIEW NEXT — blueprint drafted. **Implementation:** pending. **Current blockers:** `source:extra-action`, `source:trait`. **Primary family:** GAZE / SIGHT / INVISIBILITY.
- [ ] **source:extra-action** (review candidate actions: **Engulf**): Identify each special printed Action, legality, targeting/area, source save, cost, duration, recharge and AI selection. Reuse shared area/save/action/movement/resource capabilities or park the specific missing semantic clause.
- [ ] **source:trait** (**Ooze Cube; Transparent**): Decompose every named trait into its genuine event trigger, target eligibility, source-defined values, action/save/damage/condition, duration and exit. Bind shared mechanics; only classify neutral when an existing explicit arena rule permits it.

**Source packet:** [#050 in full blueprint](MONSTER_BLOCKER_FIX_BLUEPRINTS_2014.md#50-gelatinous-cube-gaze-sight-invisibility). **Review completion:** fill all above decisions before implementing; existing code readiness is not evidence of planning closure.

### 051. Ghost

**Planning:** REVIEW NEXT — blueprint drafted. **Implementation:** pending. **Current blockers:** `mechanic:recharge`, `source:extra-action`, `source:trait`. **Primary family:** GAZE / SIGHT / INVISIBILITY.
- [ ] **mechanic:recharge**: Bind Recharge threshold to the exact printed Action and source-owned resource/turn roll. Certification requires the recharged Action to be legal or formally excluded.
- [ ] **source:extra-action** (review candidate actions: **Etherealness; Horrifying Visage; Possession (Recharge 6)**): Identify each special printed Action, legality, targeting/area, source save, cost, duration, recharge and AI selection. Reuse shared area/save/action/movement/resource capabilities or park the specific missing semantic clause.
- [ ] **source:trait** (**Ethereal Sight**): Decompose every named trait into its genuine event trigger, target eligibility, source-defined values, action/save/damage/condition, duration and exit. Bind shared mechanics; only classify neutral when an existing explicit arena rule permits it.

**Source packet:** [#051 in full blueprint](MONSTER_BLOCKER_FIX_BLUEPRINTS_2014.md#51-ghost-gaze-sight-invisibility). **Review completion:** fill all above decisions before implementing; existing code readiness is not evidence of planning closure.

### 052. Giant Frog

**Planning:** REVIEW NEXT — blueprint drafted. **Implementation:** pending. **Current blockers:** `mechanic:swallow`, `source:extra-action`. **Primary family:** RESTRAINT / SWALLOW.
- [ ] **mechanic:swallow**: Bind source bite/grapple/size prerequisites, swallowed state, confinement, ongoing typed damage, escape, end on death and reset with existing shared grapple/ongoing-damage mechanics.
- [ ] **source:extra-action** (review candidate actions: **Swallow**): Identify each special printed Action, legality, targeting/area, source save, cost, duration, recharge and AI selection. Reuse shared area/save/action/movement/resource capabilities or park the specific missing semantic clause.

**Source packet:** [#052 in full blueprint](MONSTER_BLOCKER_FIX_BLUEPRINTS_2014.md#52-giant-frog-restraint-swallow). **Review completion:** fill all above decisions before implementing; existing code readiness is not evidence of planning closure.

### 053. Giant Spider

**Planning:** REVIEW NEXT — blueprint drafted. **Implementation:** pending. **Current blockers:** `attack:complex`, `attack:damage-type`, `mechanic:recharge`. **Primary family:** RECHARGE / RESOURCES.
- [ ] **attack:complex**: Compose base weapon attack with all on-hit and target-specific riders; use shared damage/save/condition code and independent typed components.
- [ ] **attack:damage-type**: Preserve each typed damage component and apply defenses separately and save-halving in both engines.
- [ ] **mechanic:recharge**: Bind Recharge threshold to the exact printed Action and source-owned resource/turn roll. Certification requires the recharged Action to be legal or formally excluded.

**Source packet:** [#053 in full blueprint](MONSTER_BLOCKER_FIX_BLUEPRINTS_2014.md#53-giant-spider-recharge-resources). **Review completion:** fill all above decisions before implementing; existing code readiness is not evidence of planning closure.

### 054. Giant Toad

**Planning:** REVIEW NEXT — blueprint drafted. **Implementation:** pending. **Current blockers:** `mechanic:swallow`, `source:extra-action`. **Primary family:** RESTRAINT / SWALLOW.
- [ ] **mechanic:swallow**: Bind source bite/grapple/size prerequisites, swallowed state, confinement, ongoing typed damage, escape, end on death and reset with existing shared grapple/ongoing-damage mechanics.
- [ ] **source:extra-action** (review candidate actions: **Swallow**): Identify each special printed Action, legality, targeting/area, source save, cost, duration, recharge and AI selection. Reuse shared area/save/action/movement/resource capabilities or park the specific missing semantic clause.

**Source packet:** [#054 in full blueprint](MONSTER_BLOCKER_FIX_BLUEPRINTS_2014.md#54-giant-toad-restraint-swallow). **Review completion:** fill all above decisions before implementing; existing code readiness is not evidence of planning closure.

### 055. Gibbering Mouther

**Planning:** REVIEW NEXT — blueprint drafted. **Implementation:** pending. **Current blockers:** `multiattack:complex`, `source:extra-action`, `source:trait`. **Primary family:** FEAR / CHARM / STATUS.
- [ ] **multiattack:complex**: Bind legal attack order, alternative forms, target limitations and conditional count to shared multiattack selector; no invented extra attacks.
- [ ] **source:extra-action** (review candidate actions: **Blinding Spittle (Recharge 5–6)**): Identify each special printed Action, legality, targeting/area, source save, cost, duration, recharge and AI selection. Reuse shared area/save/action/movement/resource capabilities or park the specific missing semantic clause.
- [ ] **source:trait** (**Aberrant Ground; Gibbering**): Decompose every named trait into its genuine event trigger, target eligibility, source-defined values, action/save/damage/condition, duration and exit. Bind shared mechanics; only classify neutral when an existing explicit arena rule permits it.

**Source packet:** [#055 in full blueprint](MONSTER_BLOCKER_FIX_BLUEPRINTS_2014.md#55-gibbering-mouther-fear-charm-status). **Review completion:** fill all above decisions before implementing; existing code readiness is not evidence of planning closure.

### 056. Glabrezu

**Planning:** REVIEW NEXT — blueprint drafted. **Implementation:** pending. **Current blockers:** `mechanic:spellcasting`, `source:trait`. **Primary family:** SPELLCASTING.
- [ ] **mechanic:spellcasting**: Audit the full printed 2014 spells, slots/uses and AI choice. Map to shared edition-specific spell effects. Park every outcome-changing missing spell individually; keep source list and exclude only explicitly approved noncombat options.
- [ ] **source:trait** (**Innate Spellcasting**): Decompose every named trait into its genuine event trigger, target eligibility, source-defined values, action/save/damage/condition, duration and exit. Bind shared mechanics; only classify neutral when an existing explicit arena rule permits it.

**Source packet:** [#056 in full blueprint](MONSTER_BLOCKER_FIX_BLUEPRINTS_2014.md#56-glabrezu-spellcasting). **Review completion:** fill all above decisions before implementing; existing code readiness is not evidence of planning closure.

### 057. Gray Ooze

**Planning:** REVIEW NEXT — blueprint drafted. **Implementation:** pending. **Current blockers:** `attack:incomplete`, `source:trait`. **Primary family:** PASSIVE RETALIATION / DAMAGE AURA.
- [ ] **attack:incomplete** (**Pseudopod**): Recover full printed damage dice/type, saves/DC, conditions, persistent wounds, target restrictions and lifecycle in source attack schema; prove Python/browser hit resolution.
- [ ] **source:trait** (**Corrode Metal**): Decompose every named trait into its genuine event trigger, target eligibility, source-defined values, action/save/damage/condition, duration and exit. Bind shared mechanics; only classify neutral when an existing explicit arena rule permits it.

**Source packet:** [#057 in full blueprint](MONSTER_BLOCKER_FIX_BLUEPRINTS_2014.md#57-gray-ooze-passive-retaliation-damage-aura). **Review completion:** fill all above decisions before implementing; existing code readiness is not evidence of planning closure.

### 058. Green Hag

**Planning:** REVIEW NEXT — blueprint drafted. **Implementation:** pending. **Current blockers:** `mechanic:spellcasting`, `source:extra-action`, `source:trait`. **Primary family:** SPELLCASTING.
- [ ] **mechanic:spellcasting**: Audit the full printed 2014 spells, slots/uses and AI choice. Map to shared edition-specific spell effects. Park every outcome-changing missing spell individually; keep source list and exclude only explicitly approved noncombat options.
- [ ] **source:extra-action** (review candidate actions: **Illusory Appearance; Invisible Passage**): Identify each special printed Action, legality, targeting/area, source save, cost, duration, recharge and AI selection. Reuse shared area/save/action/movement/resource capabilities or park the specific missing semantic clause.
- [ ] **source:trait** (**Innate Spellcasting**): Decompose every named trait into its genuine event trigger, target eligibility, source-defined values, action/save/damage/condition, duration and exit. Bind shared mechanics; only classify neutral when an existing explicit arena rule permits it.

**Source packet:** [#058 in full blueprint](MONSTER_BLOCKER_FIX_BLUEPRINTS_2014.md#58-green-hag-spellcasting). **Review completion:** fill all above decisions before implementing; existing code readiness is not evidence of planning closure.

### 059. Grimlock

**Planning:** REVIEW NEXT — blueprint drafted. **Implementation:** pending. **Current blockers:** `source:trait`. **Primary family:** GAZE / SIGHT / INVISIBILITY.
- [ ] **source:trait** (**Blind Senses**): Decompose every named trait into its genuine event trigger, target eligibility, source-defined values, action/save/damage/condition, duration and exit. Bind shared mechanics; only classify neutral when an existing explicit arena rule permits it.

**Previously recorded source-specific decisions/dependencies** (preserved, not new approvals):
- **RAW range locked / queued:** Blindsight **30 feet**, not arena-wide (24×16 five-foot squares). Reuse shared Blindsight/sight and source Blinded immunity; no global Blinded disadvantage within perceivable range, no valid gaze eye contact with Basilisk/Medusa, normal limitations beyond 30 ft. Preserve printed Deafened/smell qualifier for future mechanics. **Specification only: not implemented or certified.**

**Source packet:** [#059 in full blueprint](MONSTER_BLOCKER_FIX_BLUEPRINTS_2014.md#59-grimlock-gaze-sight-invisibility). **Review completion:** fill all above decisions before implementing; existing code readiness is not evidence of planning closure.

### 060. Guardian Naga

**Planning:** REVIEW NEXT — blueprint drafted. **Implementation:** pending. **Current blockers:** `mechanic:spellcasting`, `source:extra-action`, `source:trait`. **Primary family:** FEAR / CHARM / STATUS.
- [ ] **mechanic:spellcasting** (**11-level wisdom caster; 15 printed prepared/at-will spells; printed spell list in full source packet**): Audit the full printed 2014 spells, slots/uses and AI choice. Map to shared edition-specific spell effects. Park every outcome-changing missing spell individually; keep source list and exclude only explicitly approved noncombat options.
- [ ] **source:extra-action** (review candidate actions: **Spit Poison**): Identify each special printed Action, legality, targeting/area, source save, cost, duration, recharge and AI selection. Reuse shared area/save/action/movement/resource capabilities or park the specific missing semantic clause.
- [ ] **source:trait** (**Spellcasting**): Decompose every named trait into its genuine event trigger, target eligibility, source-defined values, action/save/damage/condition, duration and exit. Bind shared mechanics; only classify neutral when an existing explicit arena rule permits it.

**Source packet:** [#060 in full blueprint](MONSTER_BLOCKER_FIX_BLUEPRINTS_2014.md#60-guardian-naga-fear-charm-status). **Review completion:** fill all above decisions before implementing; existing code readiness is not evidence of planning closure.

### 061. Gynosphinx

**Planning:** REVIEW NEXT — blueprint drafted. **Implementation:** pending. **Current blockers:** `mechanic:legendary`, `mechanic:spellcasting`, `source:legendary`, `source:trait`. **Primary family:** SPELLCASTING.
- [ ] **mechanic:legendary**: Use the existing legendary action economy but certify each source choice, turn restriction and exact combat resolution, not just the generic pool.
- [ ] **mechanic:spellcasting** (**9-level intelligence caster; 15 printed prepared/at-will spells; printed spell list in full source packet**): Audit the full printed 2014 spells, slots/uses and AI choice. Map to shared edition-specific spell effects. Park every outcome-changing missing spell individually; keep source list and exclude only explicitly approved noncombat options.
- [ ] **source:legendary** (**Teleport**): Implement each printed option and its point cost, target, turn-end timing, spend/refill lifecycle via existing legendary-action system.
- [ ] **source:trait** (**Inscrutable; Spellcasting**): Decompose every named trait into its genuine event trigger, target eligibility, source-defined values, action/save/damage/condition, duration and exit. Bind shared mechanics; only classify neutral when an existing explicit arena rule permits it.

**Source packet:** [#061 in full blueprint](MONSTER_BLOCKER_FIX_BLUEPRINTS_2014.md#61-gynosphinx-spellcasting). **Review completion:** fill all above decisions before implementing; existing code readiness is not evidence of planning closure.

### 062. Harpy

**Planning:** REVIEW NEXT — blueprint drafted. **Implementation:** pending. **Current blockers:** `source:extra-action`. **Primary family:** FEAR / CHARM / STATUS.
- [ ] **source:extra-action** (review candidate actions: **Luring Song**): Identify each special printed Action, legality, targeting/area, source save, cost, duration, recharge and AI selection. Reuse shared area/save/action/movement/resource capabilities or park the specific missing semantic clause.

**Previously recorded source-specific decisions/dependencies** (preserved, not new approvals):
- **Luring Song user decision / queued:** 300-ft range spans the entire current arena but retain hearing and creature-type eligibility. Failure of DC 11 Wisdom save composes existing Charmed and Incapacitated and moves the victim via existing pathfinding toward Harpy's 5-ft melee reach on its own turns, limited by normal movement (not teleport); retain printed follow-up saves, song continuation and 24-hour success immunity. **No implementation or certification yet.**

**Source packet:** [#062 in full blueprint](MONSTER_BLOCKER_FIX_BLUEPRINTS_2014.md#62-harpy-fear-charm-status). **Review completion:** fill all above decisions before implementing; existing code readiness is not evidence of planning closure.

### 063. Homunculus

**Planning:** REVIEW NEXT — blueprint drafted. **Implementation:** pending. **Current blockers:** `attack:complex`, `source:trait`. **Primary family:** INFORMATION / NONCOMBAT.
- [ ] **attack:complex**: Compose base weapon attack with all on-hit and target-specific riders; use shared damage/save/condition code and independent typed components.
- [ ] **source:trait** (**Telepathic Bond**): Decompose every named trait into its genuine event trigger, target eligibility, source-defined values, action/save/damage/condition, duration and exit. Bind shared mechanics; only classify neutral when an existing explicit arena rule permits it.

**Source packet:** [#063 in full blueprint](MONSTER_BLOCKER_FIX_BLUEPRINTS_2014.md#63-homunculus-information-noncombat). **Review completion:** fill all above decisions before implementing; existing code readiness is not evidence of planning closure.

### 064. Horned Devil

**Planning:** REVIEW NEXT — blueprint drafted. **Implementation:** pending. **Current blockers:** `attack:complex`, `attack:range`. **Primary family:** OTHER / SOURCE BINDING.
- [ ] **attack:complex**: Compose base weapon attack with all on-hit and target-specific riders; use shared damage/save/condition code and independent typed components.
- [ ] **attack:range**: Restore exact reach and ranged normal/long bands from source and use shared range legality/disadvantage.

**Source packet:** [#064 in full blueprint](MONSTER_BLOCKER_FIX_BLUEPRINTS_2014.md#64-horned-devil-other-source-binding). **Review completion:** fill all above decisions before implementing; existing code readiness is not evidence of planning closure.

### 065. Hydra

**Planning:** REVIEW NEXT — blueprint drafted. **Implementation:** pending. **Current blockers:** `multiattack:complex`, `source:extra-action`, `source:trait`. **Primary family:** REACTIONS / TRIGGERS.
- [ ] **multiattack:complex**: Bind legal attack order, alternative forms, target limitations and conditional count to shared multiattack selector; no invented extra attacks.
- [ ] **source:extra-action**: Identify each special printed Action, legality, targeting/area, source save, cost, duration, recharge and AI selection. Reuse shared area/save/action/movement/resource capabilities or park the specific missing semantic clause.
- [ ] **source:trait** (**Multiple Heads; Reactive Heads**): Decompose every named trait into its genuine event trigger, target eligibility, source-defined values, action/save/damage/condition, duration and exit. Bind shared mechanics; only classify neutral when an existing explicit arena rule permits it.

**Previously recorded source-specific decisions/dependencies** (preserved, not new approvals):
- **Known directed work:** Multiple/Reactive Heads: shared head count, sever/regrow triggers, attack count and reactions driven by combat state.

**Source packet:** [#065 in full blueprint](MONSTER_BLOCKER_FIX_BLUEPRINTS_2014.md#65-hydra-reactions-triggers). **Review completion:** fill all above decisions before implementing; existing code readiness is not evidence of planning closure.

### 066. Ice Devil

**Planning:** REVIEW NEXT — blueprint drafted. **Implementation:** pending. **Current blockers:** `mechanic:recharge`, `source:extra-action`. **Primary family:** RECHARGE / RESOURCES.
- [ ] **mechanic:recharge**: Bind Recharge threshold to the exact printed Action and source-owned resource/turn roll. Certification requires the recharged Action to be legal or formally excluded.
- [ ] **source:extra-action** (review candidate actions: **Wall of Ice (Recharge 6)**): Identify each special printed Action, legality, targeting/area, source save, cost, duration, recharge and AI selection. Reuse shared area/save/action/movement/resource capabilities or park the specific missing semantic clause.

**Source packet:** [#066 in full blueprint](MONSTER_BLOCKER_FIX_BLUEPRINTS_2014.md#66-ice-devil-recharge-resources). **Review completion:** fill all above decisions before implementing; existing code readiness is not evidence of planning closure.

### 067. Ice Mephit

**Planning:** REVIEW NEXT — blueprint drafted. **Implementation:** pending. **Current blockers:** `mechanic:death-trigger`, `mechanic:spellcasting`, `source:trait`. **Primary family:** DEATH / HP-LIFECYCLE.
- [ ] **mechanic:death-trigger**: Reuse the zero-HP/death event path with source exact damage, area, saves, exclusions, timing and exactly-once fire.
- [ ] **mechanic:spellcasting**: Audit the full printed 2014 spells, slots/uses and AI choice. Map to shared edition-specific spell effects. Park every outcome-changing missing spell individually; keep source list and exclude only explicitly approved noncombat options.
- [ ] **source:trait** (**Death Burst; Innate Spellcasting**): Decompose every named trait into its genuine event trigger, target eligibility, source-defined values, action/save/damage/condition, duration and exit. Bind shared mechanics; only classify neutral when an existing explicit arena rule permits it.

**Source packet:** [#067 in full blueprint](MONSTER_BLOCKER_FIX_BLUEPRINTS_2014.md#67-ice-mephit-death-hp-lifecycle). **Review completion:** fill all above decisions before implementing; existing code readiness is not evidence of planning closure.

### 068. Imp

**Planning:** REVIEW NEXT — blueprint drafted. **Implementation:** pending. **Current blockers:** `source:extra-action`, `source:trait`. **Primary family:** GAZE / SIGHT / INVISIBILITY.
- [ ] **source:extra-action** (review candidate actions: **Invisibility**): Identify each special printed Action, legality, targeting/area, source save, cost, duration, recharge and AI selection. Reuse shared area/save/action/movement/resource capabilities or park the specific missing semantic clause.
- [ ] **source:trait** (**Shapechanger**): Decompose every named trait into its genuine event trigger, target eligibility, source-defined values, action/save/damage/condition, duration and exit. Bind shared mechanics; only classify neutral when an existing explicit arena rule permits it.

**Source packet:** [#068 in full blueprint](MONSTER_BLOCKER_FIX_BLUEPRINTS_2014.md#68-imp-gaze-sight-invisibility). **Review completion:** fill all above decisions before implementing; existing code readiness is not evidence of planning closure.

### 069. Invisible Stalker

**Planning:** COMPLETE — printed Invisibility uses shared invisibility; user-approved Faultless Tracker arena-inert, no new question. **Implementation:** pending. **Current blockers:** `source:trait`. **Primary family:** GAZE / SIGHT / INVISIBILITY.
- [x] **source:trait** (**Invisibility**): Decompose every named trait into its genuine event trigger, target eligibility, source-defined values, action/save/damage/condition, duration and exit. Bind shared mechanics; only classify neutral when an existing explicit arena rule permits it.

**Previously recorded source-specific decisions/dependencies** (preserved, not new approvals):
- **User-approved arena policy (queued):** Faultless Tracker remains printed on source/card but has no effect in Iron Pit, no combat vision/targeting bonus. Invisibility uses existing universal system; Slam attacks are unaffected. Apply shared arena-inert trait classification and regenerate blockers; not yet implemented/certified.

- [x] **Invisibility / Faultless Tracker:** invisible trait keeps RAW unseen attacker/target eligibility semantics through shared invisibility. Printed quarry/summoner tracking cannot produce combat benefits in Pit; user-approved arena-inert policy. Preserve both source labels; coding/CI pending.

**Source packet:** [#069 in full blueprint](MONSTER_BLOCKER_FIX_BLUEPRINTS_2014.md#69-invisible-stalker-gaze-sight-invisibility). **Review completion:** fill all above decisions before implementing; existing code readiness is not evidence of planning closure.

### 070. Knight

**Planning:** REVIEW NEXT — blueprint drafted. **Implementation:** pending. **Current blockers:** `source:extra-action`. **Primary family:** RECHARGE / RESOURCES.
- [ ] **source:extra-action** (review candidate actions: **Leadership (Recharges after a Short or Long Rest)**): Identify each special printed Action, legality, targeting/area, source save, cost, duration, recharge and AI selection. Reuse shared area/save/action/movement/resource capabilities or park the specific missing semantic clause.

**Previously recorded source-specific decisions/dependencies** (preserved, not new approvals):
- **Leadership user decision / queued:** Activate via Action as a nonspell, short/long-rest recharge, 10-round Bless-style +1d4 to qualifying friendly attack rolls and saves within 30 ft and able to hear. No Concentration. **Iron Pit house simplification:** once activated, buff continues until duration expires or the Knight reaches 0 HP; printed Incapacitated-ending restriction is replaced by HP > 0. Reuse shared roll-bonus mechanics. **Not implemented/certified.**

**Source packet:** [#070 in full blueprint](MONSTER_BLOCKER_FIX_BLUEPRINTS_2014.md#70-knight-recharge-resources). **Review completion:** fill all above decisions before implementing; existing code readiness is not evidence of planning closure.

### 071. Kraken

**Planning:** REVIEW NEXT — blueprint drafted. **Implementation:** pending. **Current blockers:** `attack:incomplete`, `mechanic:legendary`, `mechanic:swallow`, `multiattack:complex`, `source:extra-action`, `source:legendary`, `source:trait`. **Primary family:** RESTRAINT / SWALLOW.
- [ ] **attack:incomplete** (**Tentacle**): Recover full printed damage dice/type, saves/DC, conditions, persistent wounds, target restrictions and lifecycle in source attack schema; prove Python/browser hit resolution.
- [ ] **mechanic:legendary**: Use the existing legendary action economy but certify each source choice, turn restriction and exact combat resolution, not just the generic pool.
- [ ] **mechanic:swallow**: Bind source bite/grapple/size prerequisites, swallowed state, confinement, ongoing typed damage, escape, end on death and reset with existing shared grapple/ongoing-damage mechanics.
- [ ] **multiattack:complex**: Bind legal attack order, alternative forms, target limitations and conditional count to shared multiattack selector; no invented extra attacks.
- [ ] **source:extra-action** (review candidate actions: **Fling**): Identify each special printed Action, legality, targeting/area, source save, cost, duration, recharge and AI selection. Reuse shared area/save/action/movement/resource capabilities or park the specific missing semantic clause.
- [ ] **source:legendary** (**Tentacle Attack or Fling; Lightning Storm; Ink Cloud**): Implement each printed option and its point cost, target, turn-end timing, spend/refill lifecycle via existing legendary-action system.
- [ ] **source:trait** (**Freedom of Movement**): Decompose every named trait into its genuine event trigger, target eligibility, source-defined values, action/save/damage/condition, duration and exit. Bind shared mechanics; only classify neutral when an existing explicit arena rule permits it.

**Source packet:** [#071 in full blueprint](MONSTER_BLOCKER_FIX_BLUEPRINTS_2014.md#71-kraken-restraint-swallow). **Review completion:** fill all above decisions before implementing; existing code readiness is not evidence of planning closure.

### 072. Lamia

**Planning:** REVIEW NEXT — blueprint drafted. **Implementation:** pending. **Current blockers:** `attack:incomplete`, `mechanic:spellcasting`, `multiattack:complex`, `source:extra-action`, `source:trait`. **Primary family:** SPELLCASTING.
- [ ] **attack:incomplete** (**Claws**): Recover full printed damage dice/type, saves/DC, conditions, persistent wounds, target restrictions and lifecycle in source attack schema; prove Python/browser hit resolution.
- [ ] **mechanic:spellcasting**: Audit the full printed 2014 spells, slots/uses and AI choice. Map to shared edition-specific spell effects. Park every outcome-changing missing spell individually; keep source list and exclude only explicitly approved noncombat options.
- [ ] **multiattack:complex**: Bind legal attack order, alternative forms, target limitations and conditional count to shared multiattack selector; no invented extra attacks.
- [ ] **source:extra-action** (review candidate actions: **Intoxicating Touch**): Identify each special printed Action, legality, targeting/area, source save, cost, duration, recharge and AI selection. Reuse shared area/save/action/movement/resource capabilities or park the specific missing semantic clause.
- [ ] **source:trait** (**Innate Spellcasting**): Decompose every named trait into its genuine event trigger, target eligibility, source-defined values, action/save/damage/condition, duration and exit. Bind shared mechanics; only classify neutral when an existing explicit arena rule permits it.

**Source packet:** [#072 in full blueprint](MONSTER_BLOCKER_FIX_BLUEPRINTS_2014.md#72-lamia-spellcasting). **Review completion:** fill all above decisions before implementing; existing code readiness is not evidence of planning closure.

### 073. Lich

**Planning:** REVIEW NEXT — blueprint drafted. **Implementation:** pending. **Current blockers:** `mechanic:legendary`, `mechanic:spellcasting`, `source:legendary`, `source:trait`. **Primary family:** GAZE / SIGHT / INVISIBILITY.
- [ ] **mechanic:legendary**: Use the existing legendary action economy but certify each source choice, turn restriction and exact combat resolution, not just the generic pool.
- [ ] **mechanic:spellcasting** (**18-level intelligence caster; 26 printed prepared/at-will spells; printed spell list in full source packet**): Audit the full printed 2014 spells, slots/uses and AI choice. Map to shared edition-specific spell effects. Park every outcome-changing missing spell individually; keep source list and exclude only explicitly approved noncombat options.
- [ ] **source:legendary** (**Cantrip; Frightening Gaze; Disrupt Life**): Implement each printed option and its point cost, target, turn-end timing, spend/refill lifecycle via existing legendary-action system.
- [ ] **source:trait** (**Spellcasting**): Decompose every named trait into its genuine event trigger, target eligibility, source-defined values, action/save/damage/condition, duration and exit. Bind shared mechanics; only classify neutral when an existing explicit arena rule permits it.

**Source packet:** [#073 in full blueprint](MONSTER_BLOCKER_FIX_BLUEPRINTS_2014.md#73-lich-gaze-sight-invisibility). **Review completion:** fill all above decisions before implementing; existing code readiness is not evidence of planning closure.

### 074. Mage

**Planning:** REVIEW NEXT — blueprint drafted. **Implementation:** pending. **Current blockers:** `mechanic:spellcasting`, `source:trait`. **Primary family:** SPELLCASTING.
- [ ] **mechanic:spellcasting** (**9-level intelligence caster; 16 printed prepared/at-will spells; printed spell list in full source packet**): Audit the full printed 2014 spells, slots/uses and AI choice. Map to shared edition-specific spell effects. Park every outcome-changing missing spell individually; keep source list and exclude only explicitly approved noncombat options.
- [ ] **source:trait** (**Spellcasting**): Decompose every named trait into its genuine event trigger, target eligibility, source-defined values, action/save/damage/condition, duration and exit. Bind shared mechanics; only classify neutral when an existing explicit arena rule permits it.

**Source packet:** [#074 in full blueprint](MONSTER_BLOCKER_FIX_BLUEPRINTS_2014.md#74-mage-spellcasting). **Review completion:** fill all above decisions before implementing; existing code readiness is not evidence of planning closure.

### 075. Magma Mephit

**Planning:** REVIEW NEXT — blueprint drafted. **Implementation:** pending. **Current blockers:** `mechanic:death-trigger`, `mechanic:spellcasting`, `source:trait`. **Primary family:** DEATH / HP-LIFECYCLE.
- [ ] **mechanic:death-trigger**: Reuse the zero-HP/death event path with source exact damage, area, saves, exclusions, timing and exactly-once fire.
- [ ] **mechanic:spellcasting**: Audit the full printed 2014 spells, slots/uses and AI choice. Map to shared edition-specific spell effects. Park every outcome-changing missing spell individually; keep source list and exclude only explicitly approved noncombat options.
- [ ] **source:trait** (**Death Burst; Innate Spellcasting**): Decompose every named trait into its genuine event trigger, target eligibility, source-defined values, action/save/damage/condition, duration and exit. Bind shared mechanics; only classify neutral when an existing explicit arena rule permits it.

**Source packet:** [#075 in full blueprint](MONSTER_BLOCKER_FIX_BLUEPRINTS_2014.md#75-magma-mephit-death-hp-lifecycle). **Review completion:** fill all above decisions before implementing; existing code readiness is not evidence of planning closure.

### 076. Magmin

**Planning:** REVIEW NEXT — blueprint drafted. **Implementation:** pending. **Current blockers:** `attack:incomplete`, `mechanic:death-trigger`, `source:trait`. **Primary family:** DEATH / HP-LIFECYCLE.
- [ ] **attack:incomplete** (**Touch**): Recover full printed damage dice/type, saves/DC, conditions, persistent wounds, target restrictions and lifecycle in source attack schema; prove Python/browser hit resolution.
- [ ] **mechanic:death-trigger**: Reuse the zero-HP/death event path with source exact damage, area, saves, exclusions, timing and exactly-once fire.
- [ ] **source:trait** (**Death Burst; Ignited Illumination**): Decompose every named trait into its genuine event trigger, target eligibility, source-defined values, action/save/damage/condition, duration and exit. Bind shared mechanics; only classify neutral when an existing explicit arena rule permits it.

**Source packet:** [#076 in full blueprint](MONSTER_BLOCKER_FIX_BLUEPRINTS_2014.md#76-magmin-death-hp-lifecycle). **Review completion:** fill all above decisions before implementing; existing code readiness is not evidence of planning closure.

### 077. Manticore

**Planning:** REVIEW NEXT — blueprint drafted. **Implementation:** pending. **Current blockers:** `mechanic:limited-use`, `source:trait`. **Primary family:** RECHARGE / RESOURCES.
- [ ] **mechanic:limited-use**: Bind uses, expenditure, recovery/regrowth roll/interval and reset to generic encounter resources.
- [ ] **source:trait** (**Tail Spike Regrowth**): Decompose every named trait into its genuine event trigger, target eligibility, source-defined values, action/save/damage/condition, duration and exit. Bind shared mechanics; only classify neutral when an existing explicit arena rule permits it.

**Source packet:** [#077 in full blueprint](MONSTER_BLOCKER_FIX_BLUEPRINTS_2014.md#77-manticore-recharge-resources). **Review completion:** fill all above decisions before implementing; existing code readiness is not evidence of planning closure.

### 078. Marilith

**Planning:** REVIEW NEXT — blueprint drafted. **Implementation:** pending. **Current blockers:** `attack:complex`, `source:trait`. **Primary family:** REACTIONS / TRIGGERS.
- [ ] **attack:complex**: Compose base weapon attack with all on-hit and target-specific riders; use shared damage/save/condition code and independent typed components.
- [ ] **source:trait** (**Reactive**): Decompose every named trait into its genuine event trigger, target eligibility, source-defined values, action/save/damage/condition, duration and exit. Bind shared mechanics; only classify neutral when an existing explicit arena rule permits it.

**Source packet:** [#078 in full blueprint](MONSTER_BLOCKER_FIX_BLUEPRINTS_2014.md#78-marilith-reactions-triggers). **Review completion:** fill all above decisions before implementing; existing code readiness is not evidence of planning closure.

### 079. Medusa

**Planning:** COMPLETE — user-approved shared Petrifying Gaze and source-specific immediate-petrification margin; no further policy question. **Implementation:** pending. **Current blockers:** `source:trait`. **Primary family:** GAZE / SIGHT / INVISIBILITY.
- [x] **source:trait** (**Petrifying Gaze**): Decompose every named trait into its genuine event trigger, target eligibility, source-defined values, action/save/damage/condition, duration and exit. Bind shared mechanics; only classify neutral when an existing explicit arena rule permits it.

**Previously recorded source-specific decisions/dependencies** (preserved, not new approvals):
- **Known directed work:** Petrifying Gaze: reuse timed save escalation to Petrified, but verify sight/gaze avoidance and source timing.
- **User decision, queued:** Same shared gaze mechanic and sight/avert policy as Basilisk. Medusa supplies **DC 14 Constitution, 30-ft range** and the special **fail by 5 or more => immediate Petrified** escalation (terminal Iron Pit outcome). Other failed saves follow existing Restrained → repeat-save → Petrified progression; source qualifiers preserved. Not implemented/certified.

- [x] **User-approved Petrifying Gaze:** generic gaze/avert choice shared with Basilisk, but this 2014 source uses DC14 CON at 30 ft; fail by 5 or more triggers immediate Petrified; otherwise failed save Restrained followed by source next-turn repeat and Petrification on further failure. Preserve mutual sight and self-reflection qualifiers. Reuse shared stage/conditional gaze, #676; not certified.

**Source packet:** [#079 in full blueprint](MONSTER_BLOCKER_FIX_BLUEPRINTS_2014.md#79-medusa-gaze-sight-invisibility). **Review completion:** fill all above decisions before implementing; existing code readiness is not evidence of planning closure.

### 080. Mimic

**Planning:** REVIEW NEXT — blueprint drafted. **Implementation:** pending. **Current blockers:** `attack:incomplete`, `source:trait`. **Primary family:** SHAPECHANGE / TRANSFORMATION.
- [ ] **attack:incomplete** (**Pseudopod**): Recover full printed damage dice/type, saves/DC, conditions, persistent wounds, target restrictions and lifecycle in source attack schema; prove Python/browser hit resolution.
- [ ] **source:trait** (**Shapechanger; Adhesive (Object Form Only); False Appearance (Object Form Only); Grappler**): Decompose every named trait into its genuine event trigger, target eligibility, source-defined values, action/save/damage/condition, duration and exit. Bind shared mechanics; only classify neutral when an existing explicit arena rule permits it.

**Source packet:** [#080 in full blueprint](MONSTER_BLOCKER_FIX_BLUEPRINTS_2014.md#80-mimic-shapechange-transformation). **Review completion:** fill all above decisions before implementing; existing code readiness is not evidence of planning closure.

### 081. Mummy

**Planning:** REVIEW NEXT — blueprint drafted. **Implementation:** pending. **Current blockers:** `attack:incomplete`, `source:extra-action`. **Primary family:** OTHER / SOURCE BINDING.
- [ ] **attack:incomplete** (**Rotting Fist**): Recover full printed damage dice/type, saves/DC, conditions, persistent wounds, target restrictions and lifecycle in source attack schema; prove Python/browser hit resolution.
- [ ] **source:extra-action** (review candidate actions: **Dreadful Glare**): Identify each special printed Action, legality, targeting/area, source save, cost, duration, recharge and AI selection. Reuse shared area/save/action/movement/resource capabilities or park the specific missing semantic clause.

**Source packet:** [#081 in full blueprint](MONSTER_BLOCKER_FIX_BLUEPRINTS_2014.md#81-mummy-other-source-binding). **Review completion:** fill all above decisions before implementing; existing code readiness is not evidence of planning closure.

### 082. Mummy Lord

**Planning:** REVIEW NEXT — blueprint drafted. **Implementation:** pending. **Current blockers:** `attack:incomplete`, `mechanic:legendary`, `mechanic:spellcasting`, `source:extra-action`, `source:legendary`, `source:trait`. **Primary family:** AREA / SAVE ACTIONS.
- [ ] **attack:incomplete** (**Rotting Fist**): Recover full printed damage dice/type, saves/DC, conditions, persistent wounds, target restrictions and lifecycle in source attack schema; prove Python/browser hit resolution.
- [ ] **mechanic:legendary**: Use the existing legendary action economy but certify each source choice, turn restriction and exact combat resolution, not just the generic pool.
- [ ] **mechanic:spellcasting** (**10-level wisdom caster; 15 printed prepared/at-will spells; printed spell list in full source packet**): Audit the full printed 2014 spells, slots/uses and AI choice. Map to shared edition-specific spell effects. Park every outcome-changing missing spell individually; keep source list and exclude only explicitly approved noncombat options.
- [ ] **source:extra-action** (review candidate actions: **Dreadful Glare**): Identify each special printed Action, legality, targeting/area, source save, cost, duration, recharge and AI selection. Reuse shared area/save/action/movement/resource capabilities or park the specific missing semantic clause.
- [ ] **source:legendary** (**Attack; Blinding Dust; Blasphemous Word; Channel Negative Energy; Whirlwind of Sand**): Implement each printed option and its point cost, target, turn-end timing, spend/refill lifecycle via existing legendary-action system.
- [ ] **source:trait** (**Spellcasting**): Decompose every named trait into its genuine event trigger, target eligibility, source-defined values, action/save/damage/condition, duration and exit. Bind shared mechanics; only classify neutral when an existing explicit arena rule permits it.

**Source packet:** [#082 in full blueprint](MONSTER_BLOCKER_FIX_BLUEPRINTS_2014.md#82-mummy-lord-area-save-actions). **Review completion:** fill all above decisions before implementing; existing code readiness is not evidence of planning closure.

### 083. Night Hag

**Planning:** REVIEW NEXT — blueprint drafted. **Implementation:** pending. **Current blockers:** `mechanic:spellcasting`, `source:extra-action`, `source:trait`. **Primary family:** SHAPECHANGE / TRANSFORMATION.
- [ ] **mechanic:spellcasting**: Audit the full printed 2014 spells, slots/uses and AI choice. Map to shared edition-specific spell effects. Park every outcome-changing missing spell individually; keep source list and exclude only explicitly approved noncombat options.
- [ ] **source:extra-action** (review candidate actions: **Change Shape; Etherealness; Nightmare Haunting (1/Day)**): Identify each special printed Action, legality, targeting/area, source save, cost, duration, recharge and AI selection. Reuse shared area/save/action/movement/resource capabilities or park the specific missing semantic clause.
- [ ] **source:trait** (**Innate Spellcasting**): Decompose every named trait into its genuine event trigger, target eligibility, source-defined values, action/save/damage/condition, duration and exit. Bind shared mechanics; only classify neutral when an existing explicit arena rule permits it.

**Source packet:** [#083 in full blueprint](MONSTER_BLOCKER_FIX_BLUEPRINTS_2014.md#83-night-hag-shapechange-transformation). **Review completion:** fill all above decisions before implementing; existing code readiness is not evidence of planning closure.

### 084. Nightmare

**Planning:** REVIEW NEXT — blueprint drafted. **Implementation:** pending. **Current blockers:** `source:extra-action`, `source:trait`. **Primary family:** POSITION / MOVEMENT.
- [ ] **source:extra-action** (review candidate actions: **Ethereal Stride**): Identify each special printed Action, legality, targeting/area, source save, cost, duration, recharge and AI selection. Reuse shared area/save/action/movement/resource capabilities or park the specific missing semantic clause.
- [ ] **source:trait** (**Confer Fire Resistance**): Decompose every named trait into its genuine event trigger, target eligibility, source-defined values, action/save/damage/condition, duration and exit. Bind shared mechanics; only classify neutral when an existing explicit arena rule permits it.

**Source packet:** [#084 in full blueprint](MONSTER_BLOCKER_FIX_BLUEPRINTS_2014.md#84-nightmare-position-movement). **Review completion:** fill all above decisions before implementing; existing code readiness is not evidence of planning closure.

### 085. Oni

**Planning:** REVIEW NEXT — blueprint drafted. **Implementation:** pending. **Current blockers:** `attack:incomplete`, `mechanic:spellcasting`, `source:extra-action`, `source:trait`. **Primary family:** SHAPECHANGE / TRANSFORMATION.
- [ ] **attack:incomplete** (**Glaive**): Recover full printed damage dice/type, saves/DC, conditions, persistent wounds, target restrictions and lifecycle in source attack schema; prove Python/browser hit resolution.
- [ ] **mechanic:spellcasting**: Audit the full printed 2014 spells, slots/uses and AI choice. Map to shared edition-specific spell effects. Park every outcome-changing missing spell individually; keep source list and exclude only explicitly approved noncombat options.
- [ ] **source:extra-action** (review candidate actions: **Change Shape**): Identify each special printed Action, legality, targeting/area, source save, cost, duration, recharge and AI selection. Reuse shared area/save/action/movement/resource capabilities or park the specific missing semantic clause.
- [ ] **source:trait** (**Innate Spellcasting**): Decompose every named trait into its genuine event trigger, target eligibility, source-defined values, action/save/damage/condition, duration and exit. Bind shared mechanics; only classify neutral when an existing explicit arena rule permits it.

**Source packet:** [#085 in full blueprint](MONSTER_BLOCKER_FIX_BLUEPRINTS_2014.md#85-oni-shapechange-transformation). **Review completion:** fill all above decisions before implementing; existing code readiness is not evidence of planning closure.

### 086. Otyugh

**Planning:** REVIEW NEXT — blueprint drafted. **Implementation:** pending. **Current blockers:** `attack:incomplete`, `source:extra-action`, `source:trait`. **Primary family:** RESTRAINT / SWALLOW.
- [ ] **attack:incomplete** (**Tentacle**): Recover full printed damage dice/type, saves/DC, conditions, persistent wounds, target restrictions and lifecycle in source attack schema; prove Python/browser hit resolution.
- [ ] **source:extra-action** (review candidate actions: **Tentacle Slam**): Identify each special printed Action, legality, targeting/area, source save, cost, duration, recharge and AI selection. Reuse shared area/save/action/movement/resource capabilities or park the specific missing semantic clause.
- [ ] **source:trait** (**Limited Telepathy**): Decompose every named trait into its genuine event trigger, target eligibility, source-defined values, action/save/damage/condition, duration and exit. Bind shared mechanics; only classify neutral when an existing explicit arena rule permits it.

**Source packet:** [#086 in full blueprint](MONSTER_BLOCKER_FIX_BLUEPRINTS_2014.md#86-otyugh-restraint-swallow). **Review completion:** fill all above decisions before implementing; existing code readiness is not evidence of planning closure.

### 087. Pit Fiend

**Planning:** REVIEW NEXT — blueprint drafted. **Implementation:** pending. **Current blockers:** `attack:incomplete`, `mechanic:spellcasting`, `source:trait`. **Primary family:** FEAR / CHARM / STATUS.
- [ ] **attack:incomplete** (**Bite**): Recover full printed damage dice/type, saves/DC, conditions, persistent wounds, target restrictions and lifecycle in source attack schema; prove Python/browser hit resolution.
- [ ] **mechanic:spellcasting**: Audit the full printed 2014 spells, slots/uses and AI choice. Map to shared edition-specific spell effects. Park every outcome-changing missing spell individually; keep source list and exclude only explicitly approved noncombat options.
- [ ] **source:trait** (**Fear Aura; Innate Spellcasting**): Decompose every named trait into its genuine event trigger, target eligibility, source-defined values, action/save/damage/condition, duration and exit. Bind shared mechanics; only classify neutral when an existing explicit arena rule permits it.

**Source packet:** [#087 in full blueprint](MONSTER_BLOCKER_FIX_BLUEPRINTS_2014.md#87-pit-fiend-fear-charm-status). **Review completion:** fill all above decisions before implementing; existing code readiness is not evidence of planning closure.

### 088. Planetar

**Planning:** REVIEW NEXT — blueprint drafted. **Implementation:** pending. **Current blockers:** `mechanic:spellcasting`, `source:extra-action`, `source:trait`. **Primary family:** SPELLCASTING.
- [ ] **mechanic:spellcasting**: Audit the full printed 2014 spells, slots/uses and AI choice. Map to shared edition-specific spell effects. Park every outcome-changing missing spell individually; keep source list and exclude only explicitly approved noncombat options.
- [ ] **source:extra-action** (review candidate actions: **Healing Touch**): Identify each special printed Action, legality, targeting/area, source save, cost, duration, recharge and AI selection. Reuse shared area/save/action/movement/resource capabilities or park the specific missing semantic clause.
- [ ] **source:trait** (**Divine Awareness; Innate Spellcasting**): Decompose every named trait into its genuine event trigger, target eligibility, source-defined values, action/save/damage/condition, duration and exit. Bind shared mechanics; only classify neutral when an existing explicit arena rule permits it.

**Source packet:** [#088 in full blueprint](MONSTER_BLOCKER_FIX_BLUEPRINTS_2014.md#88-planetar-spellcasting). **Review completion:** fill all above decisions before implementing; existing code readiness is not evidence of planning closure.

### 089. Priest

**Planning:** REVIEW NEXT — blueprint drafted. **Implementation:** pending. **Current blockers:** `mechanic:spellcasting`, `source:trait`. **Primary family:** SPELLCASTING.
- [ ] **mechanic:spellcasting** (**5-level wisdom caster; 10 printed prepared/at-will spells; printed spell list in full source packet**): Audit the full printed 2014 spells, slots/uses and AI choice. Map to shared edition-specific spell effects. Park every outcome-changing missing spell individually; keep source list and exclude only explicitly approved noncombat options.
- [ ] **source:trait** (**Divine Eminence; Spellcasting**): Decompose every named trait into its genuine event trigger, target eligibility, source-defined values, action/save/damage/condition, duration and exit. Bind shared mechanics; only classify neutral when an existing explicit arena rule permits it.

**Source packet:** [#089 in full blueprint](MONSTER_BLOCKER_FIX_BLUEPRINTS_2014.md#89-priest-spellcasting). **Review completion:** fill all above decisions before implementing; existing code readiness is not evidence of planning closure.

### 090. Pseudodragon

**Planning:** REVIEW NEXT — blueprint drafted. **Implementation:** pending. **Current blockers:** `attack:complex`, `source:trait`. **Primary family:** INFORMATION / NONCOMBAT.
- [ ] **attack:complex**: Compose base weapon attack with all on-hit and target-specific riders; use shared damage/save/condition code and independent typed components.
- [ ] **source:trait** (**Limited Telepathy**): Decompose every named trait into its genuine event trigger, target eligibility, source-defined values, action/save/damage/condition, duration and exit. Bind shared mechanics; only classify neutral when an existing explicit arena rule permits it.

**Source packet:** [#090 in full blueprint](MONSTER_BLOCKER_FIX_BLUEPRINTS_2014.md#90-pseudodragon-information-noncombat). **Review completion:** fill all above decisions before implementing; existing code readiness is not evidence of planning closure.

### 091. Purple Worm

**Planning:** REVIEW NEXT — blueprint drafted. **Implementation:** pending. **Current blockers:** `attack:complex`, `mechanic:swallow`. **Primary family:** OTHER / SOURCE BINDING.
- [ ] **attack:complex**: Compose base weapon attack with all on-hit and target-specific riders; use shared damage/save/condition code and independent typed components.
- [ ] **mechanic:swallow**: Bind source bite/grapple/size prerequisites, swallowed state, confinement, ongoing typed damage, escape, end on death and reset with existing shared grapple/ongoing-damage mechanics.

**Source packet:** [#091 in full blueprint](MONSTER_BLOCKER_FIX_BLUEPRINTS_2014.md#91-purple-worm-other-source-binding). **Review completion:** fill all above decisions before implementing; existing code readiness is not evidence of planning closure.

### 092. Quasit

**Planning:** REVIEW NEXT — blueprint drafted. **Implementation:** pending. **Current blockers:** `attack:complex`, `source:extra-action`, `source:trait`. **Primary family:** GAZE / SIGHT / INVISIBILITY.
- [ ] **attack:complex**: Compose base weapon attack with all on-hit and target-specific riders; use shared damage/save/condition code and independent typed components.
- [ ] **source:extra-action** (review candidate actions: **Scare (1/Day); Invisibility**): Identify each special printed Action, legality, targeting/area, source save, cost, duration, recharge and AI selection. Reuse shared area/save/action/movement/resource capabilities or park the specific missing semantic clause.
- [ ] **source:trait** (**Shapechanger**): Decompose every named trait into its genuine event trigger, target eligibility, source-defined values, action/save/damage/condition, duration and exit. Bind shared mechanics; only classify neutral when an existing explicit arena rule permits it.

**Source packet:** [#092 in full blueprint](MONSTER_BLOCKER_FIX_BLUEPRINTS_2014.md#92-quasit-gaze-sight-invisibility). **Review completion:** fill all above decisions before implementing; existing code readiness is not evidence of planning closure.

### 093. Rakshasa

**Planning:** REVIEW NEXT — blueprint drafted. **Implementation:** pending. **Current blockers:** `mechanic:defense`, `mechanic:spellcasting`, `source:trait`. **Primary family:** SPELLCASTING.
- [ ] **mechanic:defense**: Bind printed conditional magic/condition damage defense to universal attack/save/spell predicates without monster-specific code.
- [ ] **mechanic:spellcasting**: Audit the full printed 2014 spells, slots/uses and AI choice. Map to shared edition-specific spell effects. Park every outcome-changing missing spell individually; keep source list and exclude only explicitly approved noncombat options.
- [ ] **source:trait** (**Limited Magic Immunity; Innate Spellcasting**): Decompose every named trait into its genuine event trigger, target eligibility, source-defined values, action/save/damage/condition, duration and exit. Bind shared mechanics; only classify neutral when an existing explicit arena rule permits it.

**Source packet:** [#093 in full blueprint](MONSTER_BLOCKER_FIX_BLUEPRINTS_2014.md#93-rakshasa-spellcasting). **Review completion:** fill all above decisions before implementing; existing code readiness is not evidence of planning closure.

### 094. Remorhaz

**Planning:** REVIEW NEXT — blueprint drafted. **Implementation:** pending. **Current blockers:** `mechanic:swallow`, `source:extra-action`, `source:trait`. **Primary family:** PASSIVE RETALIATION / DAMAGE AURA.
- [ ] **mechanic:swallow**: Bind source bite/grapple/size prerequisites, swallowed state, confinement, ongoing typed damage, escape, end on death and reset with existing shared grapple/ongoing-damage mechanics.
- [ ] **source:extra-action** (review candidate actions: **Swallow**): Identify each special printed Action, legality, targeting/area, source save, cost, duration, recharge and AI selection. Reuse shared area/save/action/movement/resource capabilities or park the specific missing semantic clause.
- [ ] **source:trait** (**Heated Body**): Decompose every named trait into its genuine event trigger, target eligibility, source-defined values, action/save/damage/condition, duration and exit. Bind shared mechanics; only classify neutral when an existing explicit arena rule permits it.

**Previously recorded source-specific decisions/dependencies** (preserved, not new approvals):
- **Known directed work:** Heated Body: contact retaliation with source fire dice and temperature-independent Pit interpretation.

**Source packet:** [#094 in full blueprint](MONSTER_BLOCKER_FIX_BLUEPRINTS_2014.md#94-remorhaz-passive-retaliation-damage-aura). **Review completion:** fill all above decisions before implementing; existing code readiness is not evidence of planning closure.

### 095. Roper

**Planning:** REVIEW NEXT — blueprint drafted. **Implementation:** pending. **Current blockers:** `source:extra-action`, `source:trait`. **Primary family:** RESTRAINT / SWALLOW.
- [ ] **source:extra-action** (review candidate actions: **Tendril; Reel**): Identify each special printed Action, legality, targeting/area, source save, cost, duration, recharge and AI selection. Reuse shared area/save/action/movement/resource capabilities or park the specific missing semantic clause.
- [ ] **source:trait** (**Grasping Tendrils**): Decompose every named trait into its genuine event trigger, target eligibility, source-defined values, action/save/damage/condition, duration and exit. Bind shared mechanics; only classify neutral when an existing explicit arena rule permits it.

**Source packet:** [#095 in full blueprint](MONSTER_BLOCKER_FIX_BLUEPRINTS_2014.md#95-roper-restraint-swallow). **Review completion:** fill all above decisions before implementing; existing code readiness is not evidence of planning closure.

### 096. Rug of Smothering

**Planning:** REVIEW NEXT — blueprint drafted. **Implementation:** pending. **Current blockers:** `attack:none`, `source:extra-action`, `source:trait`. **Primary family:** RESTRAINT / SWALLOW.
- [ ] **attack:none**: Do not invent an attack for a non-offensive source creature. Confirm arena participation policy.
- [ ] **source:extra-action** (review candidate actions: **Smother**): Identify each special printed Action, legality, targeting/area, source save, cost, duration, recharge and AI selection. Reuse shared area/save/action/movement/resource capabilities or park the specific missing semantic clause.
- [ ] **source:trait** (**Damage Transfer**): Decompose every named trait into its genuine event trigger, target eligibility, source-defined values, action/save/damage/condition, duration and exit. Bind shared mechanics; only classify neutral when an existing explicit arena rule permits it.

**Previously recorded source-specific decisions/dependencies** (preserved, not new approvals):
- **Known directed work:** Damage Transfer: reuse distributed incoming damage primitive if exact; integrate grapple/restrain and existing susceptibility.

**Source packet:** [#096 in full blueprint](MONSTER_BLOCKER_FIX_BLUEPRINTS_2014.md#96-rug-of-smothering-restraint-swallow). **Review completion:** fill all above decisions before implementing; existing code readiness is not evidence of planning closure.

### 097. Rust Monster

**Planning:** REVIEW NEXT — blueprint drafted. **Implementation:** pending. **Current blockers:** `source:extra-action`, `source:trait`. **Primary family:** OTHER / SOURCE BINDING.
- [ ] **source:extra-action** (review candidate actions: **Antennae**): Identify each special printed Action, legality, targeting/area, source save, cost, duration, recharge and AI selection. Reuse shared area/save/action/movement/resource capabilities or park the specific missing semantic clause.
- [ ] **source:trait** (**Iron Scent; Rust Metal**): Decompose every named trait into its genuine event trigger, target eligibility, source-defined values, action/save/damage/condition, duration and exit. Bind shared mechanics; only classify neutral when an existing explicit arena rule permits it.

**Source packet:** [#097 in full blueprint](MONSTER_BLOCKER_FIX_BLUEPRINTS_2014.md#97-rust-monster-other-source-binding). **Review completion:** fill all above decisions before implementing; existing code readiness is not evidence of planning closure.

### 098. Salamander

**Planning:** REVIEW NEXT — blueprint drafted. **Implementation:** pending. **Current blockers:** `attack:complex`, `source:trait`. **Primary family:** PASSIVE RETALIATION / DAMAGE AURA.
- [ ] **attack:complex**: Compose base weapon attack with all on-hit and target-specific riders; use shared damage/save/condition code and independent typed components.
- [ ] **source:trait** (**Heated Body**): Decompose every named trait into its genuine event trigger, target eligibility, source-defined values, action/save/damage/condition, duration and exit. Bind shared mechanics; only classify neutral when an existing explicit arena rule permits it.

**Previously recorded source-specific decisions/dependencies** (preserved, not new approvals):
- **Known directed work:** Heated Body: generic touch retaliation; tail: exact own-grapple auto-hit constraint, not mere Advantage.

**Source packet:** [#098 in full blueprint](MONSTER_BLOCKER_FIX_BLUEPRINTS_2014.md#98-salamander-passive-retaliation-damage-aura). **Review completion:** fill all above decisions before implementing; existing code readiness is not evidence of planning closure.

### 099. Sea Hag

**Planning:** REVIEW NEXT — blueprint drafted. **Implementation:** pending. **Current blockers:** `source:extra-action`, `source:trait`. **Primary family:** OTHER / SOURCE BINDING.
- [ ] **source:extra-action** (review candidate actions: **Death Glare; Illusory Appearance**): Identify each special printed Action, legality, targeting/area, source save, cost, duration, recharge and AI selection. Reuse shared area/save/action/movement/resource capabilities or park the specific missing semantic clause.
- [ ] **source:trait** (**Horrific Appearance**): Decompose every named trait into its genuine event trigger, target eligibility, source-defined values, action/save/damage/condition, duration and exit. Bind shared mechanics; only classify neutral when an existing explicit arena rule permits it.

**Source packet:** [#099 in full blueprint](MONSTER_BLOCKER_FIX_BLUEPRINTS_2014.md#99-sea-hag-other-source-binding). **Review completion:** fill all above decisions before implementing; existing code readiness is not evidence of planning closure.

### 100. Sea Horse

**Planning:** COMPLETE — user already approved fielding zero-damage creature; no new question. **Implementation:** pending. **Current blockers:** `attack:none`. **Primary family:** SOURCE-ONLY / ARENA POLICY.
- [x] **attack:none**: Do not invent an attack for a non-offensive source creature. Confirm arena participation policy.

**Previously recorded source-specific decisions/dependencies** (preserved, not new approvals):
- **USER DECISION / QUEUED:** Sea Horse may be selected and fielded in Iron Pit; it simply deals **0 attack damage**. Do not invent a damaging attack or alter the printed source. Change arena-neutral exclusion/certification behavior to allow a valid non-damaging participant; ensure combat can terminate without stalls. Not implemented/certified.
- **Further user suggestion:** Rather than a fabricated 0-damage attack, Sea Horse may repeatedly take the **existing Dodge Action** on its turns, retaining exactly RAW Dodge conditions and no damage output; still arena-selectable. Avoid new machinery; guard against no-damage stalemates. Proposal queued, not implemented/certified.

- [x] **User approval carried forward:** Sea Horse is selectable in Pit despite having no damaging attack; exactly zero attack damage and no fabricated source Action. Permit normal no-damage fight termination/fallback. Runtime integration pending.

**Source packet:** [#100 in full blueprint](MONSTER_BLOCKER_FIX_BLUEPRINTS_2014.md#100-sea-horse-source-only-arena-policy). **Review completion:** fill all above decisions before implementing; existing code readiness is not evidence of planning closure.

### 101. Shadow

**Planning:** REVIEW NEXT — blueprint drafted. **Implementation:** pending. **Current blockers:** `attack:incomplete`, `source:trait`. **Primary family:** ATTACK RIDERS / MULTICOMPONENT DAMAGE.
- [ ] **attack:incomplete** (**Strength Drain**): Recover full printed damage dice/type, saves/DC, conditions, persistent wounds, target restrictions and lifecycle in source attack schema; prove Python/browser hit resolution.
- [ ] **source:trait** (**Sunlight Weakness**): Decompose every named trait into its genuine event trigger, target eligibility, source-defined values, action/save/damage/condition, duration and exit. Bind shared mechanics; only classify neutral when an existing explicit arena rule permits it.

**Source packet:** [#101 in full blueprint](MONSTER_BLOCKER_FIX_BLUEPRINTS_2014.md#101-shadow-attack-riders-multicomponent-damage). **Review completion:** fill all above decisions before implementing; existing code readiness is not evidence of planning closure.

### 102. Shambling Mound

**Planning:** REVIEW NEXT — blueprint drafted. **Implementation:** pending. **Current blockers:** `mechanic:swallow`, `multiattack:complex`, `source:extra-action`. **Primary family:** RESTRAINT / SWALLOW.
- [ ] **mechanic:swallow**: Bind source bite/grapple/size prerequisites, swallowed state, confinement, ongoing typed damage, escape, end on death and reset with existing shared grapple/ongoing-damage mechanics.
- [ ] **multiattack:complex**: Bind legal attack order, alternative forms, target limitations and conditional count to shared multiattack selector; no invented extra attacks.
- [ ] **source:extra-action** (review candidate actions: **Engulf**): Identify each special printed Action, legality, targeting/area, source save, cost, duration, recharge and AI selection. Reuse shared area/save/action/movement/resource capabilities or park the specific missing semantic clause.

**Source packet:** [#102 in full blueprint](MONSTER_BLOCKER_FIX_BLUEPRINTS_2014.md#102-shambling-mound-restraint-swallow). **Review completion:** fill all above decisions before implementing; existing code readiness is not evidence of planning closure.

### 103. Shield Guardian

**Planning:** REVIEW NEXT — blueprint drafted. **Implementation:** pending. **Current blockers:** `source:reaction`, `source:trait`. **Primary family:** RECHARGE / RESOURCES.
- [ ] **source:reaction** (**Shield**): Model genuine triggering event, timing, eligibility, reaction cost, source effect and reset in shared reaction dispatch; prove production Python/browser calls, not helper-only tests.
- [ ] **source:trait** (**Bound; Spell Storing**): Decompose every named trait into its genuine event trigger, target eligibility, source-defined values, action/save/damage/condition, duration and exit. Bind shared mechanics; only classify neutral when an existing explicit arena rule permits it.

**Source packet:** [#103 in full blueprint](MONSTER_BLOCKER_FIX_BLUEPRINTS_2014.md#103-shield-guardian-recharge-resources). **Review completion:** fill all above decisions before implementing; existing code readiness is not evidence of planning closure.

### 104. Shrieker

**Planning:** REVIEW NEXT — blueprint drafted. **Implementation:** pending. **Current blockers:** `attack:none`, `source:reaction`. **Primary family:** OTHER / SOURCE BINDING.
- [ ] **attack:none**: Do not invent an attack for a non-offensive source creature. Confirm arena participation policy.
- [ ] **source:reaction** (**Shriek**): Model genuine triggering event, timing, eligibility, reaction cost, source effect and reset in shared reaction dispatch; prove production Python/browser calls, not helper-only tests.

**Source packet:** [#104 in full blueprint](MONSTER_BLOCKER_FIX_BLUEPRINTS_2014.md#104-shrieker-other-source-binding). **Review completion:** fill all above decisions before implementing; existing code readiness is not evidence of planning closure.

### 105. Solar

**Planning:** REVIEW NEXT — blueprint drafted. **Implementation:** pending. **Current blockers:** `attack:incomplete`, `mechanic:legendary`, `mechanic:spellcasting`, `source:extra-action`, `source:legendary`, `source:trait`. **Primary family:** GAZE / SIGHT / INVISIBILITY.
- [ ] **attack:incomplete** (**Slaying Longbow**): Recover full printed damage dice/type, saves/DC, conditions, persistent wounds, target restrictions and lifecycle in source attack schema; prove Python/browser hit resolution.
- [ ] **mechanic:legendary**: Use the existing legendary action economy but certify each source choice, turn restriction and exact combat resolution, not just the generic pool.
- [ ] **mechanic:spellcasting**: Audit the full printed 2014 spells, slots/uses and AI choice. Map to shared edition-specific spell effects. Park every outcome-changing missing spell individually; keep source list and exclude only explicitly approved noncombat options.
- [ ] **source:extra-action** (review candidate actions: **Flying Sword; Healing Touch (4/Day)**): Identify each special printed Action, legality, targeting/area, source save, cost, duration, recharge and AI selection. Reuse shared area/save/action/movement/resource capabilities or park the specific missing semantic clause.
- [ ] **source:legendary** (**Teleport; Searing Burst; Blinding Gaze**): Implement each printed option and its point cost, target, turn-end timing, spend/refill lifecycle via existing legendary-action system.
- [ ] **source:trait** (**Divine Awareness; Innate Spellcasting**): Decompose every named trait into its genuine event trigger, target eligibility, source-defined values, action/save/damage/condition, duration and exit. Bind shared mechanics; only classify neutral when an existing explicit arena rule permits it.

**Source packet:** [#105 in full blueprint](MONSTER_BLOCKER_FIX_BLUEPRINTS_2014.md#105-solar-gaze-sight-invisibility). **Review completion:** fill all above decisions before implementing; existing code readiness is not evidence of planning closure.

### 106. Spectator

**Planning:** REVIEW NEXT — blueprint drafted. **Implementation:** pending. **Current blockers:** `source:extra-action`, `source:reaction`. **Primary family:** AREA / SAVE ACTIONS.
- [ ] **source:extra-action** (review candidate actions: **Eye Rays; Create Food and Water**): Identify each special printed Action, legality, targeting/area, source save, cost, duration, recharge and AI selection. Reuse shared area/save/action/movement/resource capabilities or park the specific missing semantic clause.
- [ ] **source:reaction** (**Spell Reflection**): Model genuine triggering event, timing, eligibility, reaction cost, source effect and reset in shared reaction dispatch; prove production Python/browser calls, not helper-only tests.

**Source packet:** [#106 in full blueprint](MONSTER_BLOCKER_FIX_BLUEPRINTS_2014.md#106-spectator-area-save-actions). **Review completion:** fill all above decisions before implementing; existing code readiness is not evidence of planning closure.

### 107. Spirit Naga

**Planning:** REVIEW NEXT — blueprint drafted. **Implementation:** pending. **Current blockers:** `mechanic:spellcasting`, `source:trait`. **Primary family:** SPELLCASTING.
- [ ] **mechanic:spellcasting** (**10-level intelligence caster; 13 printed prepared/at-will spells; printed spell list in full source packet**): Audit the full printed 2014 spells, slots/uses and AI choice. Map to shared edition-specific spell effects. Park every outcome-changing missing spell individually; keep source list and exclude only explicitly approved noncombat options.
- [ ] **source:trait** (**Spellcasting**): Decompose every named trait into its genuine event trigger, target eligibility, source-defined values, action/save/damage/condition, duration and exit. Bind shared mechanics; only classify neutral when an existing explicit arena rule permits it.

**Source packet:** [#107 in full blueprint](MONSTER_BLOCKER_FIX_BLUEPRINTS_2014.md#107-spirit-naga-spellcasting). **Review completion:** fill all above decisions before implementing; existing code readiness is not evidence of planning closure.

### 108. Sprite

**Planning:** REVIEW NEXT — blueprint drafted. **Implementation:** pending. **Current blockers:** `attack:complex`, `source:extra-action`. **Primary family:** GAZE / SIGHT / INVISIBILITY.
- [ ] **attack:complex**: Compose base weapon attack with all on-hit and target-specific riders; use shared damage/save/condition code and independent typed components.
- [ ] **source:extra-action** (review candidate actions: **Heart Sight; Invisibility**): Identify each special printed Action, legality, targeting/area, source save, cost, duration, recharge and AI selection. Reuse shared area/save/action/movement/resource capabilities or park the specific missing semantic clause.

**Source packet:** [#108 in full blueprint](MONSTER_BLOCKER_FIX_BLUEPRINTS_2014.md#108-sprite-gaze-sight-invisibility). **Review completion:** fill all above decisions before implementing; existing code readiness is not evidence of planning closure.

### 109. Steam Mephit

**Planning:** REVIEW NEXT — blueprint drafted. **Implementation:** pending. **Current blockers:** `mechanic:death-trigger`, `mechanic:spellcasting`, `source:trait`. **Primary family:** DEATH / HP-LIFECYCLE.
- [ ] **mechanic:death-trigger**: Reuse the zero-HP/death event path with source exact damage, area, saves, exclusions, timing and exactly-once fire.
- [ ] **mechanic:spellcasting**: Audit the full printed 2014 spells, slots/uses and AI choice. Map to shared edition-specific spell effects. Park every outcome-changing missing spell individually; keep source list and exclude only explicitly approved noncombat options.
- [ ] **source:trait** (**Death Burst; Innate Spellcasting**): Decompose every named trait into its genuine event trigger, target eligibility, source-defined values, action/save/damage/condition, duration and exit. Bind shared mechanics; only classify neutral when an existing explicit arena rule permits it.

**Source packet:** [#109 in full blueprint](MONSTER_BLOCKER_FIX_BLUEPRINTS_2014.md#109-steam-mephit-death-hp-lifecycle). **Review completion:** fill all above decisions before implementing; existing code readiness is not evidence of planning closure.

### 110. Stirge

**Planning:** COMPLETE — previously approved arena roster exclusion, not a pending user decision. **Implementation:** pending. **Current blockers:** `arena:removed`. **Primary family:** SOURCE-ONLY / ARENA POLICY.
- [x] **arena:removed**: Retain full source, record approved arena removal, no mechanical substitute.

**Previously recorded source-specific decisions/dependencies** (preserved, not new approvals):
- **USER DECISION — REMOVED FOR NOW:** Retain source/stat block, but exclude Stirge from selectable arena roster. Do not build Blood Drain/attachment until revisited. This is an intentional exclusion, not combat certification.

- [x] **User approved exclusion carried forward:** Stirge remains on immutable source/card but is intentionally not selectable in arena pending later product decision; do not implement attachment/Blood Drain solely for this excluded roster item.

**Source packet:** [#110 in full blueprint](MONSTER_BLOCKER_FIX_BLUEPRINTS_2014.md#110-stirge-source-only-arena-policy). **Review completion:** fill all above decisions before implementing; existing code readiness is not evidence of planning closure.

### 111. Stone Giant

**Planning:** COMPLETE — Rock Catching already approved as generalized one-Reaction ranged-attack save, no policy question. **Implementation:** pending. **Current blockers:** `source:reaction`. **Primary family:** REACTIONS / TRIGGERS.
- [x] **source:reaction** (**Rock Catching**): Model genuine triggering event, timing, eligibility, reaction cost, source effect and reset in shared reaction dispatch; prove production Python/browser calls, not helper-only tests.

**Previously recorded source-specific decisions/dependencies** (preserved, not new approvals):
- **User ruling / queued:** Reuse existing 1 Reaction per round for Rock Catching: when a qualifying ranged attack hits, make DC 10 Dexterity save; pass negates damage, fail resolves ordinary damage and defenses. User broadened rock/similar hurled objects to ranged attacks as Iron Pit simplification; implementation must distinguish ranged attack hits from spells/AoE before activating. Source text remains unchanged. **Not implemented/certified.**

- [x] **User-approved Rock Catching:** when a qualifying ranged attack hits, spend available Reaction, roll DC10 Dexterity save; success negates the damage, failure resolves normal hit/damage. Broad Pit ranged-attack eligibility was already directed; use universal Reaction/save/damage cancellation, not a Stone Giant-only resolver.

**Source packet:** [#111 in full blueprint](MONSTER_BLOCKER_FIX_BLUEPRINTS_2014.md#111-stone-giant-reactions-triggers). **Review completion:** fill all above decisions before implementing; existing code readiness is not evidence of planning closure.

### 112. Storm Giant

**Planning:** REVIEW NEXT — blueprint drafted. **Implementation:** pending. **Current blockers:** `mechanic:spellcasting`, `source:trait`. **Primary family:** RECHARGE / RESOURCES.
- [ ] **mechanic:spellcasting**: Audit the full printed 2014 spells, slots/uses and AI choice. Map to shared edition-specific spell effects. Park every outcome-changing missing spell individually; keep source list and exclude only explicitly approved noncombat options.
- [ ] **source:trait** (**Innate Spellcasting**): Decompose every named trait into its genuine event trigger, target eligibility, source-defined values, action/save/damage/condition, duration and exit. Bind shared mechanics; only classify neutral when an existing explicit arena rule permits it.

**Source packet:** [#112 in full blueprint](MONSTER_BLOCKER_FIX_BLUEPRINTS_2014.md#112-storm-giant-recharge-resources). **Review completion:** fill all above decisions before implementing; existing code readiness is not evidence of planning closure.

### 113. Succubus/Incubus

**Planning:** REVIEW NEXT — blueprint drafted. **Implementation:** pending. **Current blockers:** `source:extra-action`, `source:trait`. **Primary family:** FEAR / CHARM / STATUS.
- [ ] **source:extra-action** (review candidate actions: **Charm; Draining Kiss; Etherealness**): Identify each special printed Action, legality, targeting/area, source save, cost, duration, recharge and AI selection. Reuse shared area/save/action/movement/resource capabilities or park the specific missing semantic clause.
- [ ] **source:trait** (**Telepathic Bond; Shapechanger**): Decompose every named trait into its genuine event trigger, target eligibility, source-defined values, action/save/damage/condition, duration and exit. Bind shared mechanics; only classify neutral when an existing explicit arena rule permits it.

**Source packet:** [#113 in full blueprint](MONSTER_BLOCKER_FIX_BLUEPRINTS_2014.md#113-succubusincubus-fear-charm-status). **Review completion:** fill all above decisions before implementing; existing code readiness is not evidence of planning closure.

### 114. Tarrasque

**Planning:** REVIEW NEXT — blueprint drafted. **Implementation:** pending. **Current blockers:** `mechanic:legendary`, `mechanic:swallow`, `source:extra-action`, `source:legendary`, `source:trait`. **Primary family:** FEAR / CHARM / STATUS.
- [ ] **mechanic:legendary**: Use the existing legendary action economy but certify each source choice, turn restriction and exact combat resolution, not just the generic pool.
- [ ] **mechanic:swallow**: Bind source bite/grapple/size prerequisites, swallowed state, confinement, ongoing typed damage, escape, end on death and reset with existing shared grapple/ongoing-damage mechanics.
- [ ] **source:extra-action** (review candidate actions: **Swallow**): Identify each special printed Action, legality, targeting/area, source save, cost, duration, recharge and AI selection. Reuse shared area/save/action/movement/resource capabilities or park the specific missing semantic clause.
- [ ] **source:legendary** (**Attack; Move; Chomp**): Implement each printed option and its point cost, target, turn-end timing, spend/refill lifecycle via existing legendary-action system.
- [ ] **source:trait** (**Reflective Carapace**): Decompose every named trait into its genuine event trigger, target eligibility, source-defined values, action/save/damage/condition, duration and exit. Bind shared mechanics; only classify neutral when an existing explicit arena rule permits it.

**Source packet:** [#114 in full blueprint](MONSTER_BLOCKER_FIX_BLUEPRINTS_2014.md#114-tarrasque-fear-charm-status). **Review completion:** fill all above decisions before implementing; existing code readiness is not evidence of planning closure.

### 115. Vampire

**Planning:** REVIEW NEXT — blueprint drafted. **Implementation:** pending. **Current blockers:** `attack:incomplete`, `mechanic:legendary`, `multiattack:complex`, `source:extra-action`, `source:legendary`, `source:trait`. **Primary family:** FEAR / CHARM / STATUS.
- [ ] **attack:incomplete** (**Unarmed Strike (Vampire Form Only); Bite. (Bat or Vampire Form Only)**): Recover full printed damage dice/type, saves/DC, conditions, persistent wounds, target restrictions and lifecycle in source attack schema; prove Python/browser hit resolution.
- [ ] **mechanic:legendary**: Use the existing legendary action economy but certify each source choice, turn restriction and exact combat resolution, not just the generic pool.
- [ ] **multiattack:complex**: Bind legal attack order, alternative forms, target limitations and conditional count to shared multiattack selector; no invented extra attacks.
- [ ] **source:extra-action** (review candidate actions: **Multiattack. (Vampire Form Only); Charm; Children of the Night (1/Day)**): Identify each special printed Action, legality, targeting/area, source save, cost, duration, recharge and AI selection. Reuse shared area/save/action/movement/resource capabilities or park the specific missing semantic clause.
- [ ] **source:legendary** (**Move**): Implement each printed option and its point cost, target, turn-end timing, spend/refill lifecycle via existing legendary-action system.
- [ ] **source:trait** (**Shapechanger; Misty Escape; Vampire Weaknesses**): Decompose every named trait into its genuine event trigger, target eligibility, source-defined values, action/save/damage/condition, duration and exit. Bind shared mechanics; only classify neutral when an existing explicit arena rule permits it.

**Previously recorded source-specific decisions/dependencies** (preserved, not new approvals):
- **Known directed work:** Shapechanger + Misty Escape + weaknesses: separate form state, zero-HP escape and environmental/debuff rules before legendary/actions.

**Source packet:** [#115 in full blueprint](MONSTER_BLOCKER_FIX_BLUEPRINTS_2014.md#115-vampire-fear-charm-status). **Review completion:** fill all above decisions before implementing; existing code readiness is not evidence of planning closure.

### 116. Vampire Spawn

**Planning:** REVIEW NEXT — blueprint drafted. **Implementation:** pending. **Current blockers:** `attack:incomplete`, `multiattack:complex`, `source:trait`. **Primary family:** DEATH / HP-LIFECYCLE.
- [ ] **attack:incomplete** (**Claws; Bite**): Recover full printed damage dice/type, saves/DC, conditions, persistent wounds, target restrictions and lifecycle in source attack schema; prove Python/browser hit resolution.
- [ ] **multiattack:complex**: Bind legal attack order, alternative forms, target limitations and conditional count to shared multiattack selector; no invented extra attacks.
- [ ] **source:trait** (**Vampire Weaknesses**): Decompose every named trait into its genuine event trigger, target eligibility, source-defined values, action/save/damage/condition, duration and exit. Bind shared mechanics; only classify neutral when an existing explicit arena rule permits it.

**Previously recorded source-specific decisions/dependencies** (preserved, not new approvals):
- **Known directed work:** Vampire Weaknesses: evaluate environment-derived damage/restrictions plus existing attack riders.

**Source packet:** [#116 in full blueprint](MONSTER_BLOCKER_FIX_BLUEPRINTS_2014.md#116-vampire-spawn-death-hp-lifecycle). **Review completion:** fill all above decisions before implementing; existing code readiness is not evidence of planning closure.

### 117. Vrock

**Planning:** REVIEW NEXT — blueprint drafted. **Implementation:** pending. **Current blockers:** `mechanic:recharge`, `source:extra-action`. **Primary family:** FEAR / CHARM / STATUS.
- [ ] **mechanic:recharge**: Bind Recharge threshold to the exact printed Action and source-owned resource/turn roll. Certification requires the recharged Action to be legal or formally excluded.
- [ ] **source:extra-action** (review candidate actions: **Spores (Recharge 6); Stunning Screech (1/Day)**): Identify each special printed Action, legality, targeting/area, source save, cost, duration, recharge and AI selection. Reuse shared area/save/action/movement/resource capabilities or park the specific missing semantic clause.

**Source packet:** [#117 in full blueprint](MONSTER_BLOCKER_FIX_BLUEPRINTS_2014.md#117-vrock-fear-charm-status). **Review completion:** fill all above decisions before implementing; existing code readiness is not evidence of planning closure.

### 118. Water Elemental

**Planning:** REVIEW NEXT — blueprint drafted. **Implementation:** pending. **Current blockers:** `mechanic:recharge`, `source:extra-action`, `source:trait`. **Primary family:** RESTRAINT / SWALLOW.
- [ ] **mechanic:recharge**: Bind Recharge threshold to the exact printed Action and source-owned resource/turn roll. Certification requires the recharged Action to be legal or formally excluded.
- [ ] **source:extra-action** (review candidate actions: **Whelm (Recharge 4–6)**): Identify each special printed Action, legality, targeting/area, source save, cost, duration, recharge and AI selection. Reuse shared area/save/action/movement/resource capabilities or park the specific missing semantic clause.
- [ ] **source:trait** (**Water Form; Freeze**): Decompose every named trait into its genuine event trigger, target eligibility, source-defined values, action/save/damage/condition, duration and exit. Bind shared mechanics; only classify neutral when an existing explicit arena rule permits it.

**Previously recorded source-specific decisions/dependencies** (preserved, not new approvals):
- **Known directed work:** Water Form/Freeze: reuse space/water traversal and susceptibility/condition with actual trigger.

**Source packet:** [#118 in full blueprint](MONSTER_BLOCKER_FIX_BLUEPRINTS_2014.md#118-water-elemental-restraint-swallow). **Review completion:** fill all above decisions before implementing; existing code readiness is not evidence of planning closure.

### 119. Werebear

**Planning:** REVIEW NEXT — blueprint drafted. **Implementation:** pending. **Current blockers:** `multiattack:complex`, `source:trait`. **Primary family:** SHAPECHANGE / TRANSFORMATION.
- [ ] **multiattack:complex**: Bind legal attack order, alternative forms, target limitations and conditional count to shared multiattack selector; no invented extra attacks.
- [ ] **source:trait** (**Shapechanger**): Decompose every named trait into its genuine event trigger, target eligibility, source-defined values, action/save/damage/condition, duration and exit. Bind shared mechanics; only classify neutral when an existing explicit arena rule permits it.

**Source packet:** [#119 in full blueprint](MONSTER_BLOCKER_FIX_BLUEPRINTS_2014.md#119-werebear-shapechange-transformation). **Review completion:** fill all above decisions before implementing; existing code readiness is not evidence of planning closure.

### 120. Wereboar

**Planning:** REVIEW NEXT — blueprint drafted. **Implementation:** pending. **Current blockers:** `multiattack:complex`, `source:extra-action`, `source:trait`. **Primary family:** SHAPECHANGE / TRANSFORMATION.
- [ ] **multiattack:complex**: Bind legal attack order, alternative forms, target limitations and conditional count to shared multiattack selector; no invented extra attacks.
- [ ] **source:extra-action** (review candidate actions: **Multiattack (Humanoid or Hybrid Form Only)**): Identify each special printed Action, legality, targeting/area, source save, cost, duration, recharge and AI selection. Reuse shared area/save/action/movement/resource capabilities or park the specific missing semantic clause.
- [ ] **source:trait** (**Shapechanger**): Decompose every named trait into its genuine event trigger, target eligibility, source-defined values, action/save/damage/condition, duration and exit. Bind shared mechanics; only classify neutral when an existing explicit arena rule permits it.

**Source packet:** [#120 in full blueprint](MONSTER_BLOCKER_FIX_BLUEPRINTS_2014.md#120-wereboar-shapechange-transformation). **Review completion:** fill all above decisions before implementing; existing code readiness is not evidence of planning closure.

### 121. Wererat

**Planning:** REVIEW NEXT — blueprint drafted. **Implementation:** pending. **Current blockers:** `multiattack:complex`, `source:extra-action`, `source:trait`. **Primary family:** SHAPECHANGE / TRANSFORMATION.
- [ ] **multiattack:complex**: Bind legal attack order, alternative forms, target limitations and conditional count to shared multiattack selector; no invented extra attacks.
- [ ] **source:extra-action** (review candidate actions: **Multiattack (Humanoid or Hybrid Form Only)**): Identify each special printed Action, legality, targeting/area, source save, cost, duration, recharge and AI selection. Reuse shared area/save/action/movement/resource capabilities or park the specific missing semantic clause.
- [ ] **source:trait** (**Shapechanger**): Decompose every named trait into its genuine event trigger, target eligibility, source-defined values, action/save/damage/condition, duration and exit. Bind shared mechanics; only classify neutral when an existing explicit arena rule permits it.

**Source packet:** [#121 in full blueprint](MONSTER_BLOCKER_FIX_BLUEPRINTS_2014.md#121-wererat-shapechange-transformation). **Review completion:** fill all above decisions before implementing; existing code readiness is not evidence of planning closure.

### 122. Weretiger

**Planning:** REVIEW NEXT — blueprint drafted. **Implementation:** pending. **Current blockers:** `multiattack:complex`, `source:extra-action`, `source:trait`. **Primary family:** SHAPECHANGE / TRANSFORMATION.
- [ ] **multiattack:complex**: Bind legal attack order, alternative forms, target limitations and conditional count to shared multiattack selector; no invented extra attacks.
- [ ] **source:extra-action** (review candidate actions: **Multiattack (Humanoid or Hybrid Form Only)**): Identify each special printed Action, legality, targeting/area, source save, cost, duration, recharge and AI selection. Reuse shared area/save/action/movement/resource capabilities or park the specific missing semantic clause.
- [ ] **source:trait** (**Shapechanger; Pounce (Tiger or Hybrid Form Only)**): Decompose every named trait into its genuine event trigger, target eligibility, source-defined values, action/save/damage/condition, duration and exit. Bind shared mechanics; only classify neutral when an existing explicit arena rule permits it.

**Source packet:** [#122 in full blueprint](MONSTER_BLOCKER_FIX_BLUEPRINTS_2014.md#122-weretiger-shapechange-transformation). **Review completion:** fill all above decisions before implementing; existing code readiness is not evidence of planning closure.

### 123. Werewolf

**Planning:** REVIEW NEXT — blueprint drafted. **Implementation:** pending. **Current blockers:** `source:extra-action`, `source:trait`. **Primary family:** SHAPECHANGE / TRANSFORMATION.
- [ ] **source:extra-action** (review candidate actions: **Multiattack. (Humanoid or Hybrid Form Only)**): Identify each special printed Action, legality, targeting/area, source save, cost, duration, recharge and AI selection. Reuse shared area/save/action/movement/resource capabilities or park the specific missing semantic clause.
- [ ] **source:trait** (**Shapechanger**): Decompose every named trait into its genuine event trigger, target eligibility, source-defined values, action/save/damage/condition, duration and exit. Bind shared mechanics; only classify neutral when an existing explicit arena rule permits it.

**Source packet:** [#123 in full blueprint](MONSTER_BLOCKER_FIX_BLUEPRINTS_2014.md#123-werewolf-shapechange-transformation). **Review completion:** fill all above decisions before implementing; existing code readiness is not evidence of planning closure.

### 124. Will-o'-Wisp

**Planning:** REVIEW NEXT — blueprint drafted. **Implementation:** pending. **Current blockers:** `source:extra-action`, `source:trait`. **Primary family:** GAZE / SIGHT / INVISIBILITY.
- [ ] **source:extra-action** (review candidate actions: **Invisibility**): Identify each special printed Action, legality, targeting/area, source save, cost, duration, recharge and AI selection. Reuse shared area/save/action/movement/resource capabilities or park the specific missing semantic clause.
- [ ] **source:trait** (**Consume Life; Ephemeral; Variable Illumination**): Decompose every named trait into its genuine event trigger, target eligibility, source-defined values, action/save/damage/condition, duration and exit. Bind shared mechanics; only classify neutral when an existing explicit arena rule permits it.

**Previously recorded source-specific decisions/dependencies** (preserved, not new approvals):
- **Known directed work:** Consume Life/Ephemeral/Variable Illumination: separate HP-threshold/terminal trigger, movement/material interactions and illumination.

**Source packet:** [#124 in full blueprint](MONSTER_BLOCKER_FIX_BLUEPRINTS_2014.md#124-will-o-wisp-gaze-sight-invisibility). **Review completion:** fill all above decisions before implementing; existing code readiness is not evidence of planning closure.

## Close-out gate

- [ ] Every #001–#124 behavior has a documented source-accurate decision or an explicitly justified arena exclusion. No open policy questions remain.
- [ ] Shared mechanic IDs/dependencies consolidated; no duplicate effects by printed name; 2014 first, 2024 remains separate.
- [ ] User confirms hourly implementation may begin. **Do not start an automation from this checklist alone.**
- [ ] On hourly execution, code one queued shared mechanic/monster blocker, verify both runtimes and exact-head gates, merge green, refresh generated blocker report and update implementation status; keep failed gates visible.