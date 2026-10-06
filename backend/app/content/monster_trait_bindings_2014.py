from __future__ import annotations

import logging
import re

from app.content.environment_context_reactions import sunlight_sensitivity_2014
from app.content.monster_damage_absorption import damage_absorptions_from_source
from app.content.monster_condition_auras import condition_auras_from_source
from app.content.monster_definition_adapter_support_2014 import attack_id_2014
from app.content.monster_legendary_resistance_2014 import legendary_resistance_trait_name_2014
from app.content.monster_heat_traits_2014 import bound_heat_trait_names_2014
from app.content.monster_passive_grants_2014 import (
    aggressive_tactical_grants_2014,
    bound_passive_trait_names_2014,
    saving_throw_advantage_grants_2014,
)
from app.content.monster_regeneration_2014 import supports_regeneration_2014
from app.content.monster_source_2014 import SourceAttack2014, SourceMonster2014
from app.content.monster_zero_hp_prevention_2014 import bound_zero_hp_trait_names_2014
from app.domain.bonus_attacks import BonusAttackGrant
from app.domain.damage_riders import OncePerTurnWeaponHitDamageRider
from app.domain.environment_contexts import EnvironmentContextReaction
from app.domain.progression import ProgressionCombatFeatures
from app.domain.weapons import ConditionalAttackAdvantage

logger = logging.getLogger(__name__)
_BLOOD_FRENZY = "Blood Frenzy"
_RECKLESS = "Reckless"
_CUNNING_ACTION = "Cunning Action"
_ASSASSINATE = "Assassinate"
_EVASION = "Evasion"
_SNEAK_ATTACK_NAMES = frozenset({"Sneak Attack", "Sneak Attack (1/Turn)"})
_MARTIAL_ADVANTAGE = "Martial Advantage"
_POOR_DEPTH_PERCEPTION = "Poor Depth Perception"
_INVISIBILITY = "Invisibility"
_MAGIC_WEAPONS = "Magic Weapons"
_INNATE_SPELLCASTING = "Innate Spellcasting"
_SUNLIGHT_SENSITIVITY = "Sunlight Sensitivity"
_RAMPAGE = "Rampage"
_FINESSE_WEAPON_NAMES_2014 = frozenset({"Dagger", "Rapier", "Scimitar", "Shortsword", "Whip"})
_SNEAK_ATTACK_D6 = re.compile(
    r"Sneak Attack(?: \(1/Turn\))?.*?extra\s+\d+\s+\((\d+)d6\)",
    re.IGNORECASE | re.DOTALL,
)
_MARTIAL_ADVANTAGE_DAMAGE = re.compile(
    r"Martial Advantage\..*?extra\s+\d+\s+\((\d+)d(\d+)\)\s+damage",
    re.IGNORECASE | re.DOTALL,
)


def supports_reckless_2014(monster: SourceMonster2014) -> bool:
    """Return whether printed Reckless can use the shared 2014 melee-Strength resolver."""
    try:
        if _RECKLESS not in monster.trait_names:
            return False
        melee = [attack for attack in monster.attacks if attack.kind == "melee"]
        return bool(melee) and all(attack.attack_ability == "strength" for attack in melee)
    except Exception:
        logger.exception("Failed to classify 2014 Reckless support for %s.", monster.name)
        raise


def supports_cunning_action_2014(monster: SourceMonster2014) -> bool:
    """Bind printed Cunning Action to the shared bonus-action Dash decision path."""
    return _CUNNING_ACTION in monster.trait_names


def _base_sneak_attack_eligible(attack: SourceAttack2014) -> bool:
    return attack.kind == "ranged" or (
        attack.kind == "melee" and attack.name in _FINESSE_WEAPON_NAMES_2014
    )


def _sneak_attack_trait_name(monster: SourceMonster2014) -> str | None:
    names = [name for name in monster.trait_names if name in _SNEAK_ATTACK_NAMES]
    if len(names) > 1:
        raise ValueError(f"{monster.name} declares duplicate Sneak Attack headings.")
    return names[0] if names else None


def sneak_attack_d6_2014(monster: SourceMonster2014) -> int:
    """Parse printed Sneak Attack dice from pinned SRD trait text."""
    try:
        if _sneak_attack_trait_name(monster) is None:
            return 0
        if not any(_base_sneak_attack_eligible(attack) for attack in monster.attacks):
            return 0
        source = monster.source_traits or ""
        match = _SNEAK_ATTACK_D6.search(source)
        if match is None:
            raise ValueError(f"{monster.name} has Sneak Attack without a parseable d6 payload.")
        dice_count = int(match.group(1))
        if not 1 <= dice_count <= 20:
            raise ValueError(f"{monster.name} has invalid Sneak Attack dice count {dice_count}.")
        return dice_count
    except Exception:
        logger.exception("Failed to parse 2014 Sneak Attack for %s.", monster.name)
        raise


def sneak_attack_eligible_2014(monster: SourceMonster2014, attack: SourceAttack2014) -> bool:
    """Mark only attacks that satisfy the shared ranged-or-Dexterity Sneak Attack profile."""
    return sneak_attack_d6_2014(monster) > 0 and _base_sneak_attack_eligible(attack)


def martial_advantage_rider_2014(
    monster: SourceMonster2014,
) -> OncePerTurnWeaponHitDamageRider | None:
    """Bind adjacency-gated once-per-turn weapon damage to the shared hit-rider primitive."""
    try:
        if _MARTIAL_ADVANTAGE not in monster.trait_names:
            return None
        match = _MARTIAL_ADVANTAGE_DAMAGE.search(monster.source_traits or "")
        if match is None:
            raise ValueError(f"{monster.name} Martial Advantage damage is not parseable.")
        return OncePerTurnWeaponHitDamageRider(
            source_id=f"{monster.id}-martial-advantage",
            source_name=_MARTIAL_ADVANTAGE,
            dice_count=int(match.group(1)),
            dice_size=int(match.group(2)),
            requires_ally_within_5_ft_of_target=True,
        )
    except Exception:
        logger.exception("Failed to bind 2014 Martial Advantage for %s.", monster.name)
        raise


def supports_poor_depth_perception_2014(monster: SourceMonster2014) -> bool:
    """Existing range rules already impose the printed beyond-30-foot Disadvantage."""
    try:
        if _POOR_DEPTH_PERCEPTION not in monster.trait_names:
            return False
        ranged = [attack for attack in monster.attacks if attack.kind == "ranged"]
        return bool(ranged) and all(
            attack.normal_range_ft is not None and attack.normal_range_ft <= 30
            for attack in ranged
        )
    except Exception:
        logger.exception("Failed Poor Depth Perception classification for %s.", monster.name)
        raise


def starting_condition_ids_2014(monster: SourceMonster2014) -> list[str]:
    """Return permanent source-owned conditions present when a fight state is created."""
    return ["invisible"] if _INVISIBILITY in monster.trait_names else []


def progression_features_2014(monster: SourceMonster2014) -> ProgressionCombatFeatures:
    """Translate printed 2014 traits into reusable progression feature fields."""
    try:
        martial = martial_advantage_rider_2014(monster)
        return ProgressionCombatFeatures(
            cunning_action=supports_cunning_action_2014(monster),
            first_turn_attack_advantage_against_unacted_target=_ASSASSINATE in monster.trait_names,
            sneak_attack_d6=sneak_attack_d6_2014(monster),
            evasion=_EVASION in monster.trait_names,
            once_per_turn_weapon_hit_damage_riders=[martial] if martial is not None else [],
            saving_throw_advantage_grants=saving_throw_advantage_grants_2014(monster),
        )
    except Exception:
        logger.exception("Failed to compile 2014 progression features for %s.", monster.name)
        raise



def bonus_attack_grants_2014(monster: SourceMonster2014) -> list[BonusAttackGrant]:
    """Bind printed kill-triggered Bonus Action attacks to the shared grant primitive."""
    try:
        if _RAMPAGE not in monster.trait_names:
            return []
        bites = [attack for attack in monster.attacks if attack.kind == "melee" and attack.name == "Bite"]
        if len(bites) != 1:
            raise ValueError(f"{monster.name} Rampage requires exactly one melee Bite attack.")
        return [BonusAttackGrant(
            id=f"{monster.id}-rampage",
            name=_RAMPAGE,
            attack_ids=[attack_id_2014(monster, bites[0].id)],
            attack_count=1,
            trigger="source_melee_zero_hp_this_turn",
            priority=10,
        )]
    except Exception:
        logger.exception("Failed to bind 2014 Rampage for %s.", monster.name)
        raise

def environment_context_reactions_2014(
    monster: SourceMonster2014,
) -> list[EnvironmentContextReaction]:
    """Bind printed Sunlight Sensitivity to the shared sunlight context reaction."""
    try:
        if _SUNLIGHT_SENSITIVITY not in monster.trait_names:
            return []
        return [sunlight_sensitivity_2014()]
    except Exception:
        logger.exception(
            "Failed to bind 2014 environment-context reactions for %s.",
            monster.name,
        )
        raise


def bound_trait_names_2014(monster: SourceMonster2014) -> frozenset[str]:
    """Return source traits that are fully bound to existing universal primitives."""
    try:
        bound: set[str] = set()
        bound.update(action.name for action in condition_auras_from_source(monster.source_traits, "2014"))
        bound.update(rule.source_name for rule in damage_absorptions_from_source(
            monster.source_traits, {item.lower() for item in monster.damage_immunities},
        ))
        if _BLOOD_FRENZY in monster.trait_names and any(attack.kind == "melee" for attack in monster.attacks):
            bound.add(_BLOOD_FRENZY)
        if supports_reckless_2014(monster):
            bound.add(_RECKLESS)
        if supports_cunning_action_2014(monster):
            bound.add(_CUNNING_ACTION)
        sneak_name = _sneak_attack_trait_name(monster)
        if sneak_name is not None and sneak_attack_d6_2014(monster) > 0:
            bound.add(sneak_name)
        if _ASSASSINATE in monster.trait_names:
            bound.add(_ASSASSINATE)
        if _EVASION in monster.trait_names:
            bound.add(_EVASION)
        if martial_advantage_rider_2014(monster) is not None:
            bound.add(_MARTIAL_ADVANTAGE)
        if supports_poor_depth_perception_2014(monster):
            bound.add(_POOR_DEPTH_PERCEPTION)
        if starting_condition_ids_2014(monster):
            bound.add(_INVISIBILITY)
        bound.update(bound_passive_trait_names_2014(monster))
        bound.update(bound_heat_trait_names_2014(monster))
        bound.update(bound_zero_hp_trait_names_2014(monster))
        if _MAGIC_WEAPONS in monster.trait_names:
            bound.add(_MAGIC_WEAPONS)
        if _INNATE_SPELLCASTING in monster.trait_names:
            from app.content.monster_innate_support_2014 import supports_innate_spellcasting_2014
            if supports_innate_spellcasting_2014(monster):
                bound.add(_INNATE_SPELLCASTING)
        if _SUNLIGHT_SENSITIVITY in monster.trait_names:
            bound.add(_SUNLIGHT_SENSITIVITY)
        if bonus_attack_grants_2014(monster):
            bound.add(_RAMPAGE)
        if supports_regeneration_2014(monster):
            bound.add("Regeneration")
        resistance = legendary_resistance_trait_name_2014(monster)
        if resistance:
            bound.add(resistance)
        return frozenset(bound)
    except Exception:
        logger.exception("Failed to classify bound 2014 traits for %s.", monster.name)
        raise


def conditional_attack_advantage_2014(
    monster: SourceMonster2014,
    attack: SourceAttack2014,
) -> list[ConditionalAttackAdvantage]:
    """Bind Blood Frenzy to the shared target-not-full-HP Advantage primitive."""
    try:
        if _BLOOD_FRENZY not in bound_trait_names_2014(monster) or attack.kind != "melee":
            return []
        return [ConditionalAttackAdvantage(trigger="target_not_full_hp")]
    except Exception:
        logger.exception(
            "Failed to bind conditional attack Advantage for %s / %s.",
            monster.name,
            attack.name,
        )
        raise
