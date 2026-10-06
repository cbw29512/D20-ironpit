from __future__ import annotations

import logging
import re

from app.content.monster_passive_grants_2014 import saving_throw_advantage_grants_2014
from app.content.monster_source_2014 import SourceAttack2014, SourceMonster2014
from app.domain.damage_riders import OncePerTurnWeaponHitDamageRider
from app.domain.progression import ProgressionCombatFeatures

logger = logging.getLogger(__name__)

_CUNNING_ACTION = "Cunning Action"
_ASSASSINATE = "Assassinate"
_EVASION = "Evasion"
_SNEAK_ATTACK_NAMES = frozenset({"Sneak Attack", "Sneak Attack (1/Turn)"})
_MARTIAL_ADVANTAGE, _INVISIBILITY = "Martial Advantage", "Invisibility"
_FINESSE_WEAPON_NAMES_2014 = frozenset({"Dagger", "Rapier", "Scimitar", "Shortsword", "Whip"})
_SNEAK_ATTACK_D6 = re.compile(
    r"Sneak Attack(?: \(1/Turn\))?.*?extra\s+\d+\s+\((\d+)d6\)",
    re.IGNORECASE | re.DOTALL,
)
_MARTIAL_ADVANTAGE_DAMAGE = re.compile(
    r"Martial Advantage\..*?extra\s+\d+\s+\((\d+)d(\d+)\)\s+damage",
    re.IGNORECASE | re.DOTALL,
)

def supports_cunning_action_2014(monster: SourceMonster2014) -> bool:
    try:
        return _CUNNING_ACTION in monster.trait_names
    except Exception:
        logger.exception("Failed to classify 2014 Cunning Action for %s.", monster.name)
        raise

def _base_sneak_attack_eligible(attack: SourceAttack2014) -> bool:
    try:
        return attack.kind == "ranged" or (
            attack.kind == "melee" and attack.name in _FINESSE_WEAPON_NAMES_2014
        )
    except Exception:
        logger.exception("Failed to classify Sneak Attack eligibility for %s.", attack.name)
        raise

def _sneak_attack_trait_name(monster: SourceMonster2014) -> str | None:
    try:
        names = [name for name in monster.trait_names if name in _SNEAK_ATTACK_NAMES]
        if len(names) > 1:
            raise ValueError(f"{monster.name} declares duplicate Sneak Attack headings.")
        return names[0] if names else None
    except Exception:
        logger.exception("Failed to classify Sneak Attack heading for %s.", monster.name)
        raise

def sneak_attack_d6_2014(monster: SourceMonster2014) -> int:
    """Parse printed Sneak Attack dice from pinned SRD trait text."""
    try:
        if _sneak_attack_trait_name(monster) is None:
            return 0
        if not any(_base_sneak_attack_eligible(attack) for attack in monster.attacks):
            return 0
        match = _SNEAK_ATTACK_D6.search(monster.source_traits or "")
        if match is None:
            raise ValueError(f"{monster.name} has Sneak Attack without a parseable d6 payload.")
        dice_count = int(match.group(1))
        if not 1 <= dice_count <= 20:
            raise ValueError(f"{monster.name} has invalid Sneak Attack dice count {dice_count}.")
        return dice_count
    except Exception:
        logger.exception("Failed to parse 2014 Sneak Attack for %s.", monster.name)
        raise

def sneak_attack_eligible_2014(
    monster: SourceMonster2014,
    attack: SourceAttack2014,
) -> bool:
    try:
        return sneak_attack_d6_2014(monster) > 0 and _base_sneak_attack_eligible(attack)
    except Exception:
        logger.exception(
            "Failed to bind 2014 Sneak Attack eligibility for %s / %s.",
            monster.name,
            attack.name,
        )
        raise

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

def starting_condition_ids_2014(monster: SourceMonster2014) -> list[str]:
    """Return source-owned conditions present when a fight state is created."""
    try:
        return ["invisible"] if _INVISIBILITY in monster.trait_names else []
    except Exception:
        logger.exception("Failed to bind starting conditions for %s.", monster.name)
        raise

def progression_features_2014(monster: SourceMonster2014) -> ProgressionCombatFeatures:
    """Translate printed traits into existing universal progression feature fields."""
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

def bound_progression_trait_names_2014(monster: SourceMonster2014) -> frozenset[str]:
    try:
        bound: set[str] = set()
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
        if starting_condition_ids_2014(monster):
            bound.add(_INVISIBILITY)
        return frozenset(bound)
    except Exception:
        logger.exception("Failed to classify progression traits for %s.", monster.name)
        raise
