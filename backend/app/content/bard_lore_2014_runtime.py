from __future__ import annotations

import logging

from app.content.bard_lore_2014_data import SPELL_SLOTS, ability_scores, bardic_inspiration_die
from app.content.character_math import fixed_hit_points, proficiency_bonus, saving_throw_bonuses
from app.domain.initiative_resources import InitiativeResourceRefillGrant
from app.domain.models import CombatantTemplate, DamageType, ResourceDefinition, VisualLoadout, Weapon, WeaponAttack, WeaponAttackKind
from app.domain.progression import ProgressionCombatFeatures, SavingThrowAdvantageGrant

logger = logging.getLogger(__name__)
_ALL_ABILITIES = ["strength", "dexterity", "constitution", "intelligence", "wisdom", "charisma"]


def _attack(level: int, weapon_id: str, name: str, dice_size: int, *, ranged: bool = False) -> WeaponAttack:
    try:
        scores = ability_scores(level)
        dexterity = scores.modifier("dexterity")
        weapon = Weapon(
            id=weapon_id,
            name=name,
            attack_kind=WeaponAttackKind.RANGED if ranged else WeaponAttackKind.MELEE,
            dice_count=1,
            dice_size=dice_size,
            damage_type=DamageType.PIERCING,
            animation="projectile" if ranged else "thrust",
            reach_ft=5,
            normal_range_ft=20 if ranged else None,
            long_range_ft=60 if ranged else None,
            projectile="dagger" if ranged else None,
            mastery_property=None,
        )
        return WeaponAttack(
            id=f"{weapon_id}-attack",
            weapon=weapon,
            attack_bonus=proficiency_bonus(level) + dexterity,
            damage_bonus=dexterity,
            attack_ability="dexterity",
            attack_ability_modifier=dexterity,
        )
    except Exception:
        logger.exception("Failed to build 2014 Lyra attack %s at level %s", weapon_id, level)
        raise


def _resources(level: int) -> list[ResourceDefinition]:
    try:
        scores = ability_scores(level)
        resources = [
            ResourceDefinition(
                id="bardic-inspiration",
                name=f"Bardic Inspiration d{bardic_inspiration_die(level)}",
                max_uses=max(1, scores.modifier("charisma")),
            )
        ]
        for spell_level, uses in enumerate(SPELL_SLOTS[level], start=1):
            resources.append(ResourceDefinition(
                id=f"spell-slot-{spell_level}",
                name=f"Level {spell_level} Spell Slot",
                max_uses=uses,
            ))
        return resources
    except Exception:
        logger.exception("Failed to compile 2014 Lyra resources at level %s", level)
        raise


def _skill_bonuses(level: int) -> dict[str, int]:
    try:
        scores = ability_scores(level)
        pb = proficiency_bonus(level)
        skills = {
            "acrobatics": "dexterity", "deception": "charisma", "history": "intelligence",
            "insight": "wisdom", "perception": "wisdom", "performance": "charisma",
            "persuasion": "charisma",
        }
        if level >= 3:
            skills.update({"arcana": "intelligence", "investigation": "intelligence", "medicine": "wisdom"})
        expertise = {"performance", "persuasion"} if level >= 3 else set()
        if level >= 10:
            expertise.update({"perception", "insight"})
        return {
            skill: scores.modifier(ability) + pb * (2 if skill in expertise else 1)
            for skill, ability in skills.items()
        }
    except Exception:
        logger.exception("Failed to compile 2014 Lyra skill bonuses at level %s", level)
        raise


def build_lyra_silverstring_2014(level: int) -> CombatantTemplate:
    try:
        if level not in range(1, 21):
            raise ValueError("2014 Lore Bard build support covers levels 1 through 20.")
        scores = ability_scores(level)
        initiative_bonus = scores.modifier("dexterity")
        if level >= 2:
            initiative_bonus += proficiency_bonus(level) // 2
        superior = (
            [InitiativeResourceRefillGrant(
                source_id="superior-inspiration",
                source_name="Superior Inspiration",
                resource_id="bardic-inspiration",
                when_at_or_below=0,
                restore_amount=1,
            )]
            if level >= 20 else []
        )
        fey_ancestry = SavingThrowAdvantageGrant(
            source_id="fey-ancestry",
            source_name="Fey Ancestry",
            abilities=list(_ALL_ABILITIES),
            against_effect_tags=["charmed"],
        )
        return CombatantTemplate(
            id=f"lyra-silverstring-2014-l{level}",
            name="Lyra Silverstring",
            archetype="Bard",
            level=level,
            kind="character",
            ruleset="2014",
            creature_type="humanoid",
            ability_scores=scores,
            armor_class=11 + scores.modifier("dexterity"),
            max_hp=fixed_hit_points(level, 8, scores.modifier("constitution")),
            speed_ft=30,
            initiative_bonus=initiative_bonus,
            weapon_attack=_attack(level, "lyra-2014-rapier", "Rapier", 8),
            alternate_weapon_attacks=[_attack(level, "lyra-2014-dagger", "Dagger", 4, ranged=True)],
            saving_throw_bonuses=saving_throw_bonuses(scores, level, ("dexterity", "charisma")),
            skill_bonuses=_skill_bonuses(level),
            progression_features=ProgressionCombatFeatures(
                saving_throw_advantage_grants=[fey_ancestry],
            ),
            initiative_resource_refill_grants=superior,
            resources=_resources(level),
            weapon_masteries=[],
            visual=VisualLoadout(armor="leather", main_hand="rapier", off_hand="lute"),
            source="D&D SRD 5.1 (2014): Half-Elf, Bard, College of Lore; Basic Rules 2014: Noble and Equipment",
        )
    except Exception:
        logger.exception("Failed to compile 2014 Lyra Silverstring at level %s", level)
        raise
