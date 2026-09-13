from app.combat.dice import FixedDiceProvider
from app.combat.saving_throw_rolls import resolve_saving_throw
from app.combat.state import build_combatant_state
from app.content.demo import build_goblin_warrior
from app.domain.traits import CombatTrait


def _state():
    template = build_goblin_warrior().model_copy(
        update={
            "combat_traits": [CombatTrait.MAGIC_RESISTANCE],
            "saving_throw_bonuses": {"wisdom": 0},
        }
    )
    return build_combatant_state(template)


def test_magic_resistance_advantage_only_applies_to_magical_effects() -> None:
    magical_roll, magical_success = resolve_saving_throw(
        _state(), "wisdom", 12, FixedDiceProvider([4, 14]), magical_effect=True
    )
    mundane_roll, mundane_success = resolve_saving_throw(
        _state(), "wisdom", 12, FixedDiceProvider([4]), magical_effect=False
    )

    assert magical_roll is not None and magical_roll.rolls == [4, 14]
    assert magical_success is True
    assert mundane_roll is not None and mundane_roll.rolls == [4]
    assert mundane_success is False
