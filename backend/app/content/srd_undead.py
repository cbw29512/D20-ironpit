from __future__ import annotations

import logging

from app.content.srd_undead_attacks import build_ghoul_bite_attack, build_ghoul_claw_attack
from app.domain.models import (
    Ability,
    CombatantTemplate,
    ConditionType,
    CreatureType,
    DamageType,
    MultiattackDefinition,
    SizeCategory,
    VisualLoadout,
)

logger = logging.getLogger(__name__)


def build_ghoul() -> CombatantTemplate:
    try:
        return CombatantTemplate(
            id="srd-ghoul",
            name="Ghoul",
            archetype="Ghoul",
            challenge_rating="1",
            kind="monster",
            creature_type=CreatureType.UNDEAD,
            size=SizeCategory.MEDIUM,
            armor_class=12,
            max_hp=22,
            speed_ft=30,
            initiative_bonus=2,
            proficiency_bonus=2,
            ability_modifiers={
                Ability.STRENGTH: 1,
                Ability.DEXTERITY: 2,
                Ability.CONSTITUTION: 0,
                Ability.INTELLIGENCE: -2,
                Ability.WISDOM: 0,
                Ability.CHARISMA: -2,
            },
            damage_immunities=[DamageType.POISON],
            condition_immunities=[
                ConditionType.CHARMED,
                ConditionType.EXHAUSTION,
                ConditionType.POISONED,
            ],
            weapon_attack=build_ghoul_bite_attack(),
            alternate_weapon_attacks=[build_ghoul_claw_attack()],
            multiattack=MultiattackDefinition(
                id="ghoul-multiattack",
                name="Multiattack",
                attack_count=2,
                allowed_attack_ids=["ghoul-bite"],
            ),
            visual=VisualLoadout(armor="none", main_hand="bite", body_style="humanoid"),
            source="SRD 5.2.1 Ghoul",
        )
    except Exception as exc:
        logger.exception("Failed to build SRD Ghoul.")
        raise RuntimeError("Ghoul could not be created.") from exc
