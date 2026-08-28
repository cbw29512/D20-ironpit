from __future__ import annotations

import logging

from app.content.equipment import build_shortbow, build_shortsword
from app.domain.models import AbilityKind, CombatantTemplate, VisualLoadout, WeaponAttack

logger = logging.getLogger(__name__)


def build_demo_rogue() -> CombatantTemplate:
    """Original level-1 Rogue built from SRD 5.2.1 class and equipment rules."""
    try:
        shortsword_attack = WeaponAttack(
            id="mara-shortsword",
            weapon=build_shortsword(),
            attack_bonus=5,
            ability_damage_modifier=3,
        )
        shortbow_attack = WeaponAttack(
            id="mara-shortbow",
            weapon=build_shortbow(),
            attack_bonus=5,
            ability_damage_modifier=3,
        )
        return CombatantTemplate(
            id="mara-vale-l1",
            name="Mara Vale",
            archetype="Rogue",
            level=1,
            kind="character",
            armor_class=14,
            max_hp=10,
            speed_ft=30,
            initiative_bonus=3,
            proficiency_bonus=2,
            ability_modifiers={
                AbilityKind.STRENGTH: -1,
                AbilityKind.DEXTERITY: 3,
                AbilityKind.CONSTITUTION: 2,
                AbilityKind.INTELLIGENCE: 1,
                AbilityKind.WISDOM: 2,
                AbilityKind.CHARISMA: 0,
            },
            saving_throw_proficiencies={
                AbilityKind.DEXTERITY,
                AbilityKind.INTELLIGENCE,
            },
            weapon_attack=shortsword_attack,
            alternate_weapon_attacks=[shortbow_attack],
            weapon_masteries=["shortsword", "shortbow"],
            sneak_attack_dice_count=1,
            skill_bonuses={"stealth": 7, "perception": 2},
            passive_perception=12,
            visual=VisualLoadout(
                armor="leather",
                main_hand="shortsword",
                off_hand=None,
                body_style="humanoid",
            ),
            source="Original pregen using SRD 5.2.1 Rogue rules",
        )
    except Exception as exc:
        logger.exception("Failed to build demo Rogue.")
        raise RuntimeError("Demo Rogue could not be created.") from exc
