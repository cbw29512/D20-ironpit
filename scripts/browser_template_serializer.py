from __future__ import annotations

import logging
from typing import Any

from app.domain.models import CombatantTemplate
from browser_action_serializer import save_row
from browser_attack_serializer import attack_row
from browser_template_common_serializer import progression_features, resource_definitions
from browser_template_optional_serializer import extend_optional_rows

logger = logging.getLogger(__name__)


def template_row(template: CombatantTemplate) -> dict[str, Any]:
    try:
        traits = {item.value for item in template.combat_traits}
        attacks = [template.weapon_attack, *template.alternate_weapon_attacks]
        row: dict[str, Any] = {
            "id": template.id,
            "name": template.name,
            "archetype": template.archetype,
            "level": template.level,
            "challenge_rating": template.challenge_rating,
            "kind": template.kind,
            "creature_type": template.creature_type,
            "creature_tags": list(template.creature_tags),
            "size": template.size.value,
            "armor_class": template.armor_class,
            "max_hp": template.max_hp,
            "speed_ft": template.speed_ft,
            "movement_modes": template.movement_modes.model_dump(),
            "initiative_bonus": template.initiative_bonus,
            "saving_throw_bonuses": template.saving_throw_bonuses,
            "skill_bonuses": template.skill_bonuses,
            "attacks": [attack_row(item, traits) for item in attacks],
            "primary_attack_id": template.weapon_attack.id,
            "saving_throw_actions": [save_row(item) for item in template.saving_throw_actions],
            "traits": sorted(traits),
            "resources": {item.id: item.max_uses for item in template.resources},
            "resourceDefinitions": resource_definitions(template),
            "magic_resistance": template.magic_resistance,
            "damage_resistances": [item.value for item in template.damage_resistances],
            "damage_vulnerabilities": [item.value for item in template.damage_vulnerabilities],
            "damage_immunities": [item.value for item in template.damage_immunities],
            "condition_immunities": list(template.condition_immunities),
            "visual": {
                "armor": template.visual.armor,
                "main_hand": template.visual.main_hand,
                "off_hand": template.visual.off_hand,
                "body_style": template.visual.body_style,
            },
            "source": template.source,
            **progression_features(template),
        }
        extend_optional_rows(row, template)
        return row
    except Exception:
        logger.exception("Failed to serialize combatant template %s.", template.id)
        raise
