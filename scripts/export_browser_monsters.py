from __future__ import annotations

import json
import logging
from pathlib import Path

from app.content.monster_catalog import build_monster_catalog
from app.content.roster import build_arena_roster
from app.domain.catalog import CoverageStatus
from browser_template_serializer import template_row

logger = logging.getLogger(__name__)
ROOT = Path(__file__).resolve().parents[1]
DESTINATION = ROOT / "frontend" / "browser-monsters-generated.js"


def _certified_monsters():
    catalog = build_monster_catalog()
    ready_ids = {card.runnable_template_id for card in catalog if card.coverage_status is CoverageStatus.RAW_READY and card.runnable_template_id is not None}
    monsters = [template for template in build_arena_roster().monsters if template.id in ready_ids]
    if {template.id for template in monsters} != ready_ids: raise RuntimeError("RAW-ready catalog and canonical monster roster disagree.")
    return monsters


def _area_row(area):
    if area is None: return None
    row = {"shape": area.shape, "origin": area.origin}
    if area.radius_ft is not None: row["radiusFt"] = area.radius_ft
    if area.length_ft is not None: row["lengthFt"] = area.length_ft
    if area.width_ft is not None: row["widthFt"] = area.width_ft
    return row


def _policy_row(policy):
    if policy is None: return None
    return {"distinctAttackIds": policy.distinct_attack_ids, "repeatSlotIndex": policy.repeat_slot_index, "repeatDiceCount": policy.repeat_dice_count, "repeatDiceSize": policy.repeat_dice_size, "requiresPreviousHitSlots": list(policy.requires_previous_hit_slots), "sameTargetAsPreviousSlots": list(policy.same_target_as_previous_slots)}


def _automatic_spell_row(action):
    return {
        "id": action.id, "name": action.name, "level": action.level,
        "actionCost": action.action_cost, "range": action.range_ft,
        "baseProjectiles": action.base_projectiles,
        "projectilesPerSlotAbove": action.projectiles_per_slot_above,
        "damageDiceCountPerProjectile": action.damage_dice_count_per_projectile,
        "damageDiceSize": action.damage_dice_size,
        "damageBonusPerProjectile": action.damage_bonus_per_projectile,
        "damageType": action.damage_type, "animation": action.animation,
    }


def _timed_control_row(effect):
    if effect is None: return None
    row = {}
    if effect.condition_id: row["conditionId"] = effect.condition_id
    if effect.effect_id: row["effectId"] = effect.effect_id
    if effect.expires_at_start_of_source_turn: row["expiresAtStartOfSourceTurn"] = True
    if effect.expiry_timing: row["expiryTiming"] = effect.expiry_timing
    if effect.duration_rounds is not None: row["durationRounds"] = effect.duration_rounds
    if effect.repeat_save_ability:
        row["repeatSaveAbility"] = effect.repeat_save_ability
        row["repeatSaveDc"] = effect.repeat_save_dc
        row["repeatSaveTiming"] = effect.repeat_save_timing
    if effect.allowed_removal_action_ids: row["allowedRemovalActionIds"] = list(effect.allowed_removal_action_ids)
    if effect.ends_on_damage: row["endsOnDamage"] = True
    if effect.source_effect_immunity_on_end: row["sourceEffectImmunityOnEnd"] = True
    if effect.speed_multiplier != 1.0: row["speedMultiplier"] = effect.speed_multiplier
    if effect.blocks_reactions: row["blocksReactions"] = True
    if effect.action_bonus_exclusive: row["actionBonusExclusive"] = True
    if effect.max_attacks_per_turn is not None: row["maxAttacksPerTurn"] = effect.max_attacks_per_turn
    return row or None


def _attach_source_fingerprint(row, template) -> None:
    row["source_trait_names"] = list(template.source_trait_names); row["source_reaction_names"] = list(template.source_reaction_names)
    row["source_bonus_action_names"] = list(template.source_bonus_action_names); row["source_limited_use_names"] = list(template.source_limited_use_names)
    row["source_legendary_action_names"] = list(template.source_legendary_action_names); row["source_spellcasting_fingerprint"] = template.source_spellcasting_fingerprint
    if template.parry_reaction: row["parry_reaction"] = {"ac_bonus": template.parry_reaction.ac_bonus}
    if template.redirect_attack_reaction: row["redirect_attack_reaction"] = {"ally_range_ft": template.redirect_attack_reaction.ally_range_ft, "ally_max_size": template.redirect_attack_reaction.ally_max_size.value}


def _attach_monster_actions(row, template) -> None:
    save_by_id = {action.id: action for action in template.saving_throw_actions}
    for action_row in row.get("saving_throw_actions", []):
        action = save_by_id.get(action_row["id"])
        if action is None: continue
        if action.area is not None: action_row["area"] = _area_row(action.area)
        if action.failure_push_ft: action_row["failurePushFt"] = action.failure_push_ft
        control = _timed_control_row(action.failure_control_effect)
        if control: action_row["failureControlEffect"] = control
    attack_by_id = {attack.id: attack for attack in [template.weapon_attack, *template.alternate_weapon_attacks]}
    for attack_row in row.get("attacks", []):
        attack = attack_by_id.get(attack_row["id"]); effect = attack.on_hit_save_effect if attack else None
        if effect and effect.zero_hp_stable:
            rider = attack_row.setdefault("onHitSaveEffect", {}); rider["zeroHpStable"] = True
            rider["zeroHpConditionIds"] = list(effect.zero_hp_condition_ids); rider["zeroHpDurationRounds"] = effect.zero_hp_duration_rounds
    if template.automatic_damage_spell_actions:
        row["automatic_damage_spell_actions"] = [_automatic_spell_row(action) for action in template.automatic_damage_spell_actions]
    if "Poor Depth Perception" in template.source_trait_names:
        for attack_row in row.get("attacks", []): attack_row["disadvantageBeyondFt"] = 30
    if template.attack_action and template.attack_action.policy: row.setdefault("attack_action", {})["policy"] = _policy_row(template.attack_action.policy)
    if template.zero_hp_prevention: row["zeroHpPrevention"] = {"resourceId": template.zero_hp_prevention.resource_id, "maxTriggerDamage": template.zero_hp_prevention.max_trigger_damage, "resultingHp": template.zero_hp_prevention.resulting_hp}
    if template.regeneration:
        row["regeneration"] = {"amount": template.regeneration.amount, "requiresPositiveHp": template.regeneration.requires_positive_hp, "suppressedByDamageTypes": [item.value for item in template.regeneration.suppressed_by_damage_types], "survivesZeroUntilTurn": template.regeneration.survives_zero_until_turn}


def render() -> str:
    try:
        rows = []
        for template in _certified_monsters():
            row = template_row(template); row["creature_type"] = template.creature_type
            _attach_source_fingerprint(row, template); _attach_monster_actions(row, template); rows.append(row)
        ids = {row["id"] for row in rows}
        if len(rows) != len(ids): raise RuntimeError("Certified browser monster export contains duplicate template IDs.")
        payload = json.dumps(rows, separators=(",", ":"), sort_keys=True)
        return "/* GENERATED from canonical Python RAW-ready monster templates. Do not hand-edit. */\n(() => {\n  \"use strict\";\n" + f"  const monsters = {payload};\n" + "  window.IRON_PIT_BROWSER_MONSTERS = Object.fromEntries(monsters.map((item) => [item.id, item]));\n  window.IRON_PIT_CANONICAL_MONSTERS_READY = true;\n})();\n"
    except Exception:
        logger.exception("Certified browser monster rendering failed."); raise


def main() -> None:
    try:
        DESTINATION.write_text(render(), encoding="utf-8"); logger.info("Exported canonical browser monsters to %s.", DESTINATION)
    except Exception:
        logger.exception("Certified browser monster export failed."); raise


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO); main()
