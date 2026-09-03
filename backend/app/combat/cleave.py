from __future__ import annotations

import logging

from app.combat.encounter_attacks import resolve_encounter_attack
from app.combat.encounter_targeting import combatant_distance
from app.combat.weapon_mastery import weapon_mastery_active
from app.combat.dice import DiceProvider
from app.domain.encounters import EncounterCombatant, EncounterSetup
from app.domain.models import BattleEvent, WeaponAttack
from app.domain.weapons import WeaponAttackKind

logger = logging.getLogger(__name__)
CLEAVE_FEATURE_ID = "weapon-mastery-cleave"


def cleave_attack_profile(attack: WeaponAttack) -> WeaponAttack:
    """Return the same weapon attack with only a positive attack ability modifier removed from damage."""
    try:
        modifier = attack.attack_ability_modifier
        if modifier is None:
            raise ValueError(f"Cleave attack {attack.id!r} requires an explicit attack ability modifier.")
        if attack.fixed_damage is not None:
            raise ValueError(f"Cleave attack {attack.id!r} requires rolled weapon damage.")
        return attack.model_copy(update={"damage_bonus": attack.damage_bonus - max(modifier, 0)}, deep=True)
    except ValueError:
        raise
    except Exception as exc:
        logger.exception("Cleave damage profile failed for %s.", attack.id)
        raise RuntimeError("Cleave damage profile could not be built.") from exc


def select_cleave_target(
    attacker: EncounterCombatant,
    first_target: EncounterCombatant,
    attack: WeaponAttack,
    setup: EncounterSetup,
) -> EncounterCombatant | None:
    """Choose a deterministic legal enemy adjacent to the first target; ordinary closing is abstracted."""
    try:
        opponents = setup.monsters if attacker.side == "heroes" else setup.heroes
        others = [member for member in opponents if member.combatant_id != first_target.combatant_id]
        active = [member for member in others if member.state.is_alive and not member.state.is_dead and member.state.current_hp > 0]
        downed = [
            member for member in others
            if member.state.template.kind == "character" and member.state.is_alive
            and not member.state.is_dead and member.state.current_hp == 0
        ]
        candidates = [
            member for member in (active or downed)
            if combatant_distance(first_target, member) <= 5
        ]
        return min(candidates, key=lambda member: (combatant_distance(attacker, member), member.combatant_id), default=None)
    except Exception as exc:
        logger.exception("Cleave target selection failed for %s.", attacker.combatant_id)
        raise RuntimeError("Cleave target could not be selected.") from exc


def resolve_cleave_extra_attack(
    sequence: int,
    round_number: int,
    attacker: EncounterCombatant,
    triggering_event: BattleEvent,
    attack: WeaponAttack,
    setup: EncounterSetup,
    dice: DiceProvider,
    turn_key: str,
) -> tuple[list[BattleEvent], int]:
    """Resolve the optional Cleave attack when the fixed formation has a legal adjacent second enemy."""
    try:
        if not triggering_event.hit or attack.weapon.attack_kind != WeaponAttackKind.MELEE:
            return [], sequence
        if not weapon_mastery_active(attacker.state, attack, "Cleave"):
            return [], sequence
        if attacker.state.feature_last_turn_keys.get(CLEAVE_FEATURE_ID) == turn_key:
            return [], sequence
        members = [*setup.heroes, *setup.monsters]
        first_target = next((member for member in members if member.combatant_id == triggering_event.target_id), None)
        if first_target is None:
            raise ValueError(f"Cleave triggering target {triggering_event.target_id!r} is not in the encounter.")
        second_target = select_cleave_target(attacker, first_target, attack, setup)
        if second_target is None:
            return [], sequence
        attacker.state.feature_last_turn_keys[CLEAVE_FEATURE_ID] = turn_key
        cleave_attack = cleave_attack_profile(attack)
        event = resolve_encounter_attack(
            sequence, round_number, attacker, second_target, cleave_attack,
            attack.weapon.reach_ft, dice, setup,
            spend_action=False, feature_id=CLEAVE_FEATURE_ID, turn_key=turn_key, allow_reckless=False,
        )
        event.description += " Cleave makes the once-per-turn extra attack."
        return [event], sequence + 1
    except ValueError:
        raise
    except Exception as exc:
        logger.exception("Cleave resolution failed for %s.", attacker.combatant_id)
        raise RuntimeError("Cleave mastery could not be resolved.") from exc
