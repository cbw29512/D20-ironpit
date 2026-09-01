from __future__ import annotations

from app.combat.dice import DiceProvider
from app.domain.models import CombatantState, DamageRollComponent, DamageType
from app.domain.traits import CombatTrait

FEATURE_ID = CombatTrait.SAVAGE_ATTACKER.value


def savage_attacker_available(state: CombatantState, turn_key: str | None) -> bool:
    return (
        turn_key is not None
        and CombatTrait.SAVAGE_ATTACKER in state.template.combat_traits
        and state.feature_last_turn_keys.get(FEATURE_ID) != turn_key
    )


def roll_weapon_component(
    state: CombatantState,
    dice: DiceProvider,
    *,
    source: str,
    dice_count: int,
    dice_size: int,
    modifier: int,
    damage_type: DamageType,
    critical: bool,
    turn_key: str | None,
    damage_die_minimum: int | None = None,
) -> DamageRollComponent:
    count = dice_count * (2 if critical else 1)

    def candidate() -> DamageRollComponent:
        raw_rolls = [dice.roll(dice_size) for _ in range(count)]
        rolls = [max(roll, damage_die_minimum) for roll in raw_rolls] if damage_die_minimum else raw_rolls
        return DamageRollComponent(
            source=source,
            notation=f"{count}d{dice_size}+{modifier}",
            rolls=rolls,
            modifier=modifier,
            damage_type=damage_type,
            total=sum(rolls) + modifier,
        )

    first = candidate()
    if not savage_attacker_available(state, turn_key):
        return first

    second = candidate()
    state.feature_last_turn_keys[FEATURE_ID] = turn_key
    chosen = second if second.total > first.total else first
    return chosen.model_copy(update={"source": f"{source} (Savage Attacker)"})
