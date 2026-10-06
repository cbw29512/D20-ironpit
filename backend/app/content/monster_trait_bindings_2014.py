from __future__ import annotations

import logging
import re

from app.content.environment_context_reactions import sunlight_sensitivity_2014
from app.content.monster_damage_absorption import damage_absorptions_from_source
from app.content.monster_condition_auras import condition_auras_from_source
from app.content.monster_definition_adapter_support_2014 import attack_id_2014
from app.content.monster_legendary_resistance_2014 import legendary_resistance_trait_name_2014
from app.content.monster_passive_grants_2014 import (
    aggressive_tactical_grants_2014,
    bound_passive_trait_names_2014,
    saving_throw_advantage_grants_2014,
)
from app.content.monster_regeneration_2014 import supports_regeneration_2014
from app.content.monster_source_2014 import SourceAttack2014, SourceMonster2014
from app.content.monster_zero_hp_prevention_2014 import bound_zero_hp_trait_names_2014
from app.domain.bonus_attacks import BonusAttackGrant
from app.domain.environment_contexts import EnvironmentContextReaction
from app.domain.progression import ProgressionCombatFeatures
from app.domain.weapons import ConditionalAttackAdvantage

logger = logging.getLogger(__name__)
_BLOOD_FRENZY = "Blood Frenzy"
_RECKLESS = "Reckless"
_CUNNING_ACTION = "Cunning Action"
_SNEAK_ATTACK = "Sneak Attack (1/Turn)"
_MAGIC_WEAPONS = "Magic Weapons"
_INNATE_SPELLCASTING = "Innate Spellcasting"
_SUNLIGHT_SENSITIVITY = "Sunlight Sensitivity"
_RAMPAGE = "Rampage"
_FINESSE_WEAPON_NAMES_2014 = frozenset({"Dagger", "Rapier", "Scimitar", "Shortsword", "Whip"})
_SNEAK_ATTACK_D6 = re.compile(
    r"Sneak Attack \(1/Turn\).*?extra\s+\d+\s+\((\d+)d6\)",
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


def sneak_attack_d6_2014(monster: SourceMonster2014) -> int:
    """Parse printed Sneak Attack dice from pinned SRD trait text."""
    try:
        if _SNEAK_ATTACK not in monster.trait_names:
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


def progression_features_2014(monster: SourceMonster2014) -> ProgressionCombatFeatures:
    """Translate printed 2014 traits into reusable progression feature fields."""
    try:
        return ProgressionCombatFeatures(
            cunning_action=supports_cunning_action_2014(monster),
            sneak_attack_d6=sneak_attack_d6_2014(monster),
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
        if sneak_attack_d6_2014(monster) > 0:
            bound.add(_SNEAK_ATTACK)
        bound.update(bound_passive_trait_names_2014(monster))
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
