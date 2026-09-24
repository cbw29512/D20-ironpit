from __future__ import annotations

import logging

from app.content.character_math import fixed_hit_points, proficiency_bonus, saving_throw_bonuses
from app.content.ranger_hunter_2014_data import ability_scores
from app.content.ranger_hunter_2014_progression import ranger_hunter_2014_level
from app.content.weapon_catalog import build_weapon
from app.domain.actions import AttackActionDefinition, AttackActionSlot
from app.domain.damage_riders import OncePerTurnWeaponHitDamageRider
from app.domain.models import CombatantTemplate, ResourceDefinition, VisualLoadout, WeaponAttack
from app.domain.progression import ProgressionCombatFeatures

logger = logging.getLogger(__name__)


def _attack(level: int, weapon_id: str, attack_id: str, *, archery: bool = False) -> WeaponAttack:
    try:
        scores = ability_scores(level)
        dexterity = scores.modifier("dexterity")
        weapon = build_weapon(weapon_id).model_copy(update={"mastery_property": None})
        return WeaponAttack(
            id=attack_id, weapon=weapon,
            attack_bonus=proficiency_bonus(level) + dexterity + (2 if archery and level >= 2 else 0),
            damage_bonus=dexterity,
            attack_ability="dexterity", attack_ability_modifier=dexterity,
        )
    except Exception:
        logger.exception("Failed to build Rowan's %s attack at level %s.", weapon_id, level)
        raise


def _resources(level: int) -> list[ResourceDefinition]:
    try:
        row = ranger_hunter_2014_level(level)
        return [
            ResourceDefinition(
                id=f"spell-slot-{spell_level}",
                name=f"Level {spell_level} Spell Slot",
                max_uses=uses,
            )
            for spell_level, uses in enumerate(row.spell_slots, start=1)
            if uses
        ]
    except Exception:
        logger.exception("Failed to compile Rowan's resources at level %s.", level)
        raise


def _skills(level: int) -> dict[str, int]:
    try:
        scores = ability_scores(level)
        pb = proficiency_bonus(level)
        return {
            "athletics": scores.modifier("strength") + pb,
            "investigation": scores.modifier("intelligence") + pb,
            "perception": scores.modifier("wisdom") + pb,
            "stealth": scores.modifier("dexterity") + pb,
            "survival": scores.modifier("wisdom") + pb,
        }
    except Exception:
        logger.exception("Failed to compile Rowan's skills at level %s.", level)
        raise


def _attack_action(level: int) -> AttackActionDefinition | None:
    try:
        if level < 5:
            return None
        choices = ["rowan-2014-longbow", "rowan-2014-shortsword"]
        return AttackActionDefinition(
            id="extra-attack", name="Extra Attack",
            slots=[AttackActionSlot(attack_ids=choices), AttackActionSlot(attack_ids=choices)],
            is_attack_action=True,
        )
    except Exception:
        logger.exception("Failed to compile Rowan's Extra Attack at level %s.", level)
        raise


def build_rowan_ashtrail_2014(level: int) -> CombatantTemplate:
    try:
        if level not in range(1, 21):
            raise ValueError("2014 Hunter Ranger build support covers levels 1 through 20.")
        scores = ability_scores(level)
        colossus = (
            OncePerTurnWeaponHitDamageRider(
                source_id="colossus-slayer", source_name="Colossus Slayer",
                dice_count=1, dice_size=8, damage_type="piercing",
                requires_target_below_max_hp=True,
            )
            if level >= 3 else None
        )
        return CombatantTemplate(
            id=f"rowan-ashtrail-2014-l{level}", name="Rowan Ashtrail",
            archetype="Ranger", level=level, kind="character", ruleset="2014",
            ability_scores=scores, armor_class=16,
            max_hp=fixed_hit_points(level, 10, scores.modifier("constitution")),
            speed_ft=30, initiative_bonus=scores.modifier("dexterity"),
            weapon_attack=_attack(level, "longbow", "rowan-2014-longbow", archery=True),
            alternate_weapon_attacks=[_attack(level, "shortsword", "rowan-2014-shortsword")],
            attack_action=_attack_action(level),
            saving_throw_bonuses=saving_throw_bonuses(scores, level, ("strength", "dexterity")),
            skill_bonuses=_skills(level),
            progression_features=ProgressionCombatFeatures(
                once_per_turn_weapon_hit_damage_rider=colossus,
                evasion=level >= 15,
            ),
            resources=_resources(level),
            weapon_masteries=[],
            fighting_style="Archery" if level >= 2 else None,
            fighting_styles=["Archery"] if level >= 2 else [],
            wearing_heavy_armor=False,
            visual=VisualLoadout(armor="scale-mail", main_hand="longbow", off_hand=None),
            source="D&D Basic Rules 2014: Human, Outlander, Equipment; D&D SRD 5.1 (2014): Ranger, Hunter",
        )
    except Exception:
        logger.exception("Failed to compile 2014 Rowan Ashtrail at level %s.", level)
        raise
