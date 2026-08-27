from __future__ import annotations

from app.combat.d20_tests import ability_modifier, choose_best_save, resolve_saving_throw
from app.combat.dice import DiceProvider
from app.domain.models import Ability, BattleEvent, CombatantState, SizeCategory

_SIZE_ORDER = list(SizeCategory)
_SAVE_OPTIONS = (Ability.STRENGTH, Ability.DEXTERITY)


def validate_unarmed_control(
    attacker: CombatantState,
    defender: CombatantState,
    distance_ft: int,
    require_free_hand: bool,
) -> None:
    if distance_ft > 5:
        raise ValueError("Unarmed Strike target must be within 5 feet.")
    attacker_size = _SIZE_ORDER.index(attacker.template.size)
    defender_size = _SIZE_ORDER.index(defender.template.size)
    if defender_size > attacker_size + 1:
        raise ValueError("Target is too large for this Unarmed Strike option.")
    if require_free_hand and attacker.template.free_hands < 1:
        raise ValueError("Grapple requires a free hand.")


def unarmed_control_dc(attacker: CombatantState) -> int:
    return 8 + ability_modifier(attacker, Ability.STRENGTH) + attacker.template.proficiency_bonus


def resolve_control_save(
    sequence: int,
    round_number: int,
    attacker: CombatantState,
    defender: CombatantState,
    feature_id: str,
    dc: int,
    dice: DiceProvider,
) -> tuple[BattleEvent, bool]:
    ability = choose_best_save(defender, _SAVE_OPTIONS)
    roll, success = resolve_saving_throw(defender, ability, dc, dice)
    return BattleEvent(
        sequence=sequence,
        round_number=round_number,
        event_type="saving_throw",
        actor_id=defender.instance_id,
        actor_name=defender.template.name,
        target_id=attacker.instance_id,
        target_name=attacker.template.name,
        saving_throw=roll,
        test_dc=dc,
        test_ability=ability,
        test_success=success,
        feature_id=feature_id,
        animation="saving-throw",
        description=(
            f"{defender.template.name} makes a {ability.value.title()} save "
            f"against {feature_id}: {'success' if success else 'failure'}."
        ),
    ), success
