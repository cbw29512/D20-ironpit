from __future__ import annotations

import logging

from app.content.character_math import fixed_hit_points, proficiency_bonus, saving_throw_bonuses
from app.content.progression_saves import saving_throw_proficiencies
from app.content.weapon_catalog import build_weapon
from app.domain.character_builds import AbilityScores
from app.domain.models import CombatantTemplate, ResourceDefinition, VisualLoadout, WeaponAttack, WeaponAttackKind
from app.domain.progression import ProgressionCombatFeatures

logger = logging.getLogger(__name__)


def _scores(level: int) -> AbilityScores:
    dexterity = 16 + (2 if level >= 4 else 0) + (2 if level >= 8 else 0)
    charisma = 15 + (1 if level >= 10 else 0)
    wisdom = 13 + (1 if level >= 10 else 0)
    constitution = 14 + (2 if level >= 12 else 0) + (2 if level >= 16 else 0) + (2 if level >= 19 else 0)
    return AbilityScores(strength=9, dexterity=dexterity, constitution=constitution,
                         intelligence=11, wisdom=wisdom, charisma=charisma)


def _attack(level: int, weapon_id: str, scores: AbilityScores) -> WeaponAttack:
    weapon = build_weapon(weapon_id).model_copy(update={"mastery_property": None})
    modifier = scores.modifier("dexterity")
    return WeaponAttack(
        id=f"mara-2014-{weapon_id}", weapon=weapon,
        attack_bonus=proficiency_bonus(level) + modifier, damage_bonus=modifier,
        attack_ability="dexterity", attack_ability_modifier=modifier,
        sneak_attack_eligible=weapon.finesse or weapon.attack_kind is WeaponAttackKind.RANGED,
    )


def _skill_bonuses(level: int, scores: AbilityScores) -> dict[str, int]:
    pb = proficiency_bonus(level)
    expertise2 = 2 * pb
    return {
        "acrobatics": scores.modifier("dexterity") + (expertise2 if level >= 6 else pb),
        "stealth": scores.modifier("dexterity") + expertise2,
        "perception": scores.modifier("wisdom") + expertise2,
        "deception": scores.modifier("charisma") + (expertise2 if level >= 6 else pb),
    }


def build_mara_quickstep_2014(level: int) -> CombatantTemplate:
    """Compile the 2014 Human Thief Rogue through level 20 from Basic Rules data.

    Reliable Talent, Use Magic Device, and Blindsense remain arena-inert for the
    current certified combat path. Slippery Mind reuses the shared saving-throw
    proficiency compiler; no Rogue-specific resolver is required.
    """
    try:
        if level not in range(1, 21):
            raise ValueError("2014 Thief Rogue candidate covers levels 1 through 20.")
        scores = _scores(level); dex = scores.modifier("dexterity")
        progression = ProgressionCombatFeatures(
            sneak_attack_d6=(level + 1) // 2, cunning_action=level >= 2,
            uncanny_dodge=level >= 5, evasion=level >= 7,
            saving_throw_proficiency_grants=(
                [{"source_id": "slippery-mind", "abilities": ["wisdom"]}]
                if level >= 15 else []
            ),
            first_round_extra_turn_grants=(
                [{"source_id": "thiefs-reflexes", "source_name": "Thief's Reflexes", "initiative_offset": -10}]
                if level >= 17 else []
            ),
            suppress_attack_advantage_while_not_incapacitated=level >= 18,
            miss_to_hit_override_grants=(
                [{
                    "source_id": "stroke-of-luck",
                    "source_name": "Stroke of Luck",
                    "usage_policy": "resource",
                    "resource_id": "stroke-of-luck",
                }]
                if level >= 20 else []
            ),
        )
        save_proficiencies = saving_throw_proficiencies(("dexterity", "intelligence"), progression)
        rapier = _attack(level, "rapier", scores); shortbow = _attack(level, "shortbow", scores)
        return CombatantTemplate(
            id=f"mara-quickstep-2014-l{level}", name="Mara Quickstep", archetype="Rogue",
            level=level, kind="character", ruleset="2014", ability_scores=scores,
            armor_class=11 + dex, max_hp=fixed_hit_points(level, 8, scores.modifier("constitution")),
            speed_ft=30, initiative_bonus=dex, weapon_attack=rapier,
            alternate_weapon_attacks=[shortbow],
            saving_throw_bonuses=saving_throw_bonuses(scores, level, save_proficiencies),
            skill_bonuses=_skill_bonuses(level, scores), weapon_masteries=[],
            progression_features=progression,
            resources=(
                [ResourceDefinition(id="stroke-of-luck", name="Stroke of Luck", max_uses=1)]
                if level >= 20 else []
            ),
            visual=VisualLoadout(armor="leather", main_hand="rapier", body_style="humanoid"),
            source="D&D Basic Rules 2014: Human; Rogue; Thief; Criminal; Equipment",
        )
    except Exception:
        logger.exception("Failed to compile 2014 Mara Quickstep at level %s", level)
        raise
