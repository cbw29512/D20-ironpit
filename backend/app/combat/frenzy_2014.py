from __future__ import annotations

from app.combat.action_economy import is_available, spend
from app.combat.attacks import resolve_attack
from app.combat.barbarian import FRENZY_2014_EFFECT_ID, rage_active
from app.combat.dice import DiceProvider
from app.combat.encounter_targeting import combatant_distance
from app.combat.pit_policy import target_order
from app.domain.encounters import EncounterCombatant, EncounterSetup
from app.domain.events import BattleEvent
from app.domain.weapons import WeaponAttackKind


def _best_melee_attack(attacker: EncounterCombatant, target: EncounterCombatant):
    distance = combatant_distance(attacker, target)
    attacks = [attacker.state.template.weapon_attack, *attacker.state.template.alternate_weapon_attacks]
    legal = [
        attack for attack in attacks
        if attack.weapon.attack_kind is WeaponAttackKind.MELEE and distance <= attack.weapon.reach_ft
    ]
    if not legal:
        return None, distance
    return max(
        legal,
        key=lambda attack: (
            attack.weapon.dice_count * attack.weapon.dice_size + attack.damage_bonus,
            attack.attack_bonus,
        ),
    ), distance


def resolve_frenzy_bonus_attack(
    sequence: int,
    round_number: int,
    attacker: EncounterCombatant,
    setup: EncounterSetup,
    dice: DiceProvider,
    turn_key: str,
) -> tuple[list[BattleEvent], int]:
    """Resolve the 2014 Berserker Frenzy Bonus Action attack when a melee target is legal."""
    state = attacker.state
    if (
        state.template.ruleset != "2014"
        or not state.template.progression_features.frenzy_bonus_attack_2014
        or FRENZY_2014_EFFECT_ID not in state.active_effect_ids
        or not rage_active(state)
        or not is_available(state, "bonus_action")
    ):
        return [], sequence
    for target in target_order(attacker, setup):
        attack, distance = _best_melee_attack(attacker, target)
        if attack is None:
            continue
        spend(state, "bonus_action")
        event = resolve_attack(
            sequence, round_number, state, target.state, attack, distance, dice,
            actor_event_id=attacker.combatant_id, target_event_id=target.combatant_id,
            spend_action=False, feature_id="frenzy", turn_key=turn_key,
            affected_states=[member.state for member in [*setup.heroes, *setup.monsters]],
        )
        return [event], sequence + 1
    return [], sequence
