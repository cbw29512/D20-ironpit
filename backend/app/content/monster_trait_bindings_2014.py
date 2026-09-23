from __future__ import annotations

import logging
import re

from app.content.monster_source_2014 import SourceAttack2014, SourceMonster2014
from app.domain.movement import MovementMode
from app.domain.progression import ProgressionCombatFeatures
from app.domain.weapons import ConditionalAttackAdvantage

logger = logging.getLogger(__name__)
_BLOOD_FRENZY = "Blood Frenzy"
_RECKLESS = "Reckless"
_CUNNING_ACTION = "Cunning Action"
_SNEAK_ATTACK = "Sneak Attack (1/Turn)"
_FLYBY = "Flyby"
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


def opportunity_attack_exempt_modes_2014(monster: SourceMonster2014) -> list[MovementMode]:
    """Bind mover-side OA exemptions by movement semantics, never monster identity."""
    try:
        return ["fly"] if _FLYBY in monster.trait_names else []
    except Exception:
        logger.exception("Failed to bind OA-exempt movement modes for %s.", monster.name)
        raise


def progression_features_2014(monster: SourceMonster2014) -> ProgressionCombatFeatures:
    """Translate printed 2014 traits into reusable progression feature fields."""
    return ProgressionCombatFeatures(
        cunning_action=supports_cunning_action_2014(monster),
        sneak_attack_d6=sneak_attack_d6_2014(monster),
    )


def bound_trait_names_2014(monster: SourceMonster2014) -> frozenset[str]:
    """Return source traits that are fully bound to existing universal primitives."""
    try:
        bound: set[str] = set()
        if _BLOOD_FRENZY in monster.trait_names and any(attack.kind == "melee" for attack in monster.attacks):
            bound.add(_BLOOD_FRENZY)
        if supports_reckless_2014(monster):
            bound.add(_RECKLESS)
        if supports_cunning_action_2014(monster):
            bound.add(_CUNNING_ACTION)
        if sneak_attack_d6_2014(monster) > 0:
            bound.add(_SNEAK_ATTACK)
        if _FLYBY in monster.trait_names:
            bound.add(_FLYBY)
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
