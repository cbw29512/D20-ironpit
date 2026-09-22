from __future__ import annotations

from dataclasses import dataclass

from app.combat.d20_outcome_override import replace_failed_d20_with_natural_20
from app.combat.miss_to_hit import resolve_miss_to_hit
from app.combat.parry import resolve_parry_hit
from app.combat.state import terminate_turn
from app.domain.models import CombatantState, DiceRoll, WeaponAttack


@dataclass(frozen=True)
class PostRollAttackOutcome:
    roll: DiceRoll
    hit: bool
    target_ac: int
    natural: int
    parry_used: bool
    miss_to_hit_used: bool
    d20_override_used: bool
    natural_1_ends_turn: bool


def resolve_post_roll_attack_outcome(
    attacker: CombatantState,
    defender: CombatantState,
    attack: WeaponAttack,
    roll: DiceRoll,
    target_ac: int,
    turn_key: str,
    *,
    off_turn: bool,
) -> PostRollAttackOutcome:
    natural = roll.selected_roll or 0
    natural_1 = natural == 1
    hit = not natural_1 and (natural == 20 or roll.total >= target_ac)

    hit, parry_used = resolve_parry_hit(defender, attack, roll.total, natural, hit)
    if parry_used:
        target_ac += defender.template.parry_reaction.ac_bonus

    hit, miss_to_hit_used = resolve_miss_to_hit(attacker, hit, turn_key)
    d20_override_used = False
    if not hit:
        roll, d20_override_used = replace_failed_d20_with_natural_20(attacker, roll, target_ac)
        natural = roll.selected_roll or 0
        natural_1 = natural == 1
        hit = not natural_1 and (natural == 20 or roll.total >= target_ac)

    natural_1_ends_turn = natural_1 and not off_turn and not hit
    if natural_1_ends_turn:
        terminate_turn(attacker, "iron-pit-natural-1-attack")

    return PostRollAttackOutcome(
        roll=roll,
        hit=hit,
        target_ac=target_ac,
        natural=natural,
        parry_used=parry_used,
        miss_to_hit_used=miss_to_hit_used,
        d20_override_used=d20_override_used,
        natural_1_ends_turn=natural_1_ends_turn,
    )
