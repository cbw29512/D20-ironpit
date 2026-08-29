from __future__ import annotations

from app.combat.dice import DiceProvider
from app.domain.models import CombatantState, DamageRollComponent, DamageType
from app.domain.traits import CombatTrait

FEATURE_ID = CombatTrait.SAVAGE_ATTACKER.value


def savage_attacker_available(state: CombatantState, turn_key: str) -> bool:
    return (
        CombatTrait.SAVAGE_ATTACKER in state.template.combat_traits
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
    turn_key: str,
) -> DamageRollComponent:
    count = dice_count * (2 if critical else 1)

    def candidate() -> DamageRollComponent:
        rolls = [dice.roll(dice_size) for _ in range(count)]
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
