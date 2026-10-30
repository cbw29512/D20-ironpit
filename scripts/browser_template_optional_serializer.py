from __future__ import annotations

import logging
from typing import Any

from app.domain.models import CombatantTemplate
from browser_template_action_fields_serializer import extend_action_rows
from browser_template_common_serializer import legendary_action_row
from browser_template_damage_rule_serializer import damage_taken_disadvantage_rows
from browser_template_effect_serializer import (
    aura_row,
    death_trigger_row,
    grapple_contact_row,
    regeneration_row,
    roll_advantage_aura_row,
    start_turn_aura_row,
    swallow_row,
)

logger = logging.getLogger(__name__)


def extend_optional_rows(row: dict[str, Any], template: CombatantTemplate) -> None:
    try:
        legendary = legendary_action_row(template)
        if legendary is not None:
            row["legendary_actions"] = legendary
        if template.regeneration:
            row["regeneration"] = regeneration_row(template.regeneration)
        if template.forced_movement_actions:
            row["forced_movement_actions"] = [
                {
                    "id": action.id, "name": action.name,
                    "direction": action.direction, "distanceFt": action.distance_ft,
                    "targetMode": action.target_mode, "animation": action.animation,
                }
                for action in template.forced_movement_actions
            ]
        if template.swallow_actions:
            row["swallow_actions"] = [swallow_row(action) for action in template.swallow_actions]
        if template.support_actions:
            row["support_actions"] = [
                {
                    "id": action.id,
                    "name": action.name,
                    "actionCost": action.action_cost,
                    "range": action.range_ft,
                    "targetMode": action.target_mode,
                    "temporaryHpDiceCount": action.temporary_hp_dice_count,
                    "temporaryHpDiceSize": action.temporary_hp_dice_size,
                    "temporaryHpBonus": action.temporary_hp_bonus,
                    "attackRollAdvantageUntilSourceTurnStart":
                        action.attack_roll_advantage_until_source_turn_start,
                    "resourceId": action.resource_id,
                    "resourceCost": action.resource_cost,
                    "animation": action.animation,
                }
                for action in template.support_actions
            ]
        if template.death_trigger_effects:
            row["death_trigger_effects"] = [
                death_trigger_row(effect) for effect in template.death_trigger_effects
            ]
        if template.damage_taken_disadvantage_rules:
            row["damage_taken_disadvantage_rules"] = damage_taken_disadvantage_rows(template)
        _extend_auras(row, template)
        _extend_triggered_actions(row, template)
        _extend_source_fingerprints(row, template)
        _extend_reactions(row, template)
        extend_action_rows(row, template)
    except Exception:
        logger.exception("Failed optional browser template serialization for %s.", template.id)
        raise


def _extend_auras(row: dict[str, Any], template: CombatantTemplate) -> None:
    try:
        if template.end_turn_damage_auras:
            row["end_turn_damage_auras"] = [aura_row(aura) for aura in template.end_turn_damage_auras]
        if template.start_turn_grapple_contact_damage is not None:
            row["start_turn_grapple_contact_damage"] = grapple_contact_row(
                template.start_turn_grapple_contact_damage
            )
        if template.start_turn_save_condition_auras:
            row["start_turn_save_condition_auras"] = [
                start_turn_aura_row(aura) for aura in template.start_turn_save_condition_auras
            ]
        if template.roll_advantage_auras:
            row["roll_advantage_auras"] = [
                roll_advantage_aura_row(aura) for aura in template.roll_advantage_auras
            ]
    except Exception:
        logger.exception("Failed aura serialization for %s.", template.id)
        raise


def _extend_triggered_actions(row: dict[str, Any], template: CombatantTemplate) -> None:
    try:
        if template.triggered_bonus_attacks:
            row["triggered_bonus_attacks"] = [
                {
                    "id": feature.id, "name": feature.name,
                    "trigger": feature.trigger, "attackId": feature.attack_id,
                    "resourceId": feature.resource_id, "resourceCost": feature.resource_cost,
                }
                for feature in template.triggered_bonus_attacks
            ]
    except Exception:
        logger.exception("Failed triggered-action serialization for %s.", template.id)
        raise


def _extend_source_fingerprints(row: dict[str, Any], template: CombatantTemplate) -> None:
    try:
        if template.kind != "monster":
            return
        row["source_trait_names"] = list(template.source_trait_names)
        row["source_reaction_names"] = list(template.source_reaction_names)
        row["source_bonus_action_names"] = list(template.source_bonus_action_names)
        row["source_limited_use_names"] = list(template.source_limited_use_names)
        row["source_legendary_action_names"] = list(template.source_legendary_action_names)
        row["source_spellcasting_fingerprint"] = template.source_spellcasting_fingerprint
    except Exception:
        logger.exception("Failed monster source fingerprint serialization for %s.", template.id)
        raise


def _extend_reactions(row: dict[str, Any], template: CombatantTemplate) -> None:
    try:
        if template.parry_reaction:
            parry = template.parry_reaction
            row["parry_reaction"] = {
                "ac_bonus": parry.ac_bonus,
                "source_feature": parry.source_feature,
                "counterattack_attack_id": parry.counterattack_attack_id,
                "counterattack_range_ft": parry.counterattack_range_ft,
            }
        if template.reaction_refresh_each_turn:
            row["reaction_refresh_each_turn"] = True
        if template.redirect_attack_reaction:
            row["redirect_attack_reaction"] = {
                "ally_range_ft": template.redirect_attack_reaction.ally_range_ft,
                "ally_max_size": template.redirect_attack_reaction.ally_max_size.value,
            }
    except Exception:
        logger.exception("Failed reaction serialization for %s.", template.id)
        raise
