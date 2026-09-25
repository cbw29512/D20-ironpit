from app.combat.dice import FixedDiceProvider
from app.combat.saving_throws import resolve_save_action
from app.combat.state import build_combatant_state
from app.content.audited_fighter import build_karnok_stoneward
from app.content.demo import build_goblin_warrior
from app.domain.encounters import EncounterCombatant
from app.domain.models import DamageType, SavingThrowAction
from app.domain.save_damage import SaveDamageComponent


def _action(dc: int) -> SavingThrowAction:
    return SavingThrowAction(
        id="split-save", name="Split Save", save_ability="dexterity", dc=dc, range_ft=60,
        success_damage="half", magical_effect=True,
        damage_components=[
            SaveDamageComponent(dice_count=1, dice_size=6, damage_type="fire"),
            SaveDamageComponent(dice_count=1, dice_size=6, damage_type="radiant"),
        ],
    )


def _actor() -> EncounterCombatant:
    return EncounterCombatant(
        combatant_id="actor", side="heroes", position_ft=0,
        state=build_combatant_state(build_karnok_stoneward()),
    )


def test_one_save_resolves_typed_damage_components_independently() -> None:
    target_template = build_goblin_warrior().model_copy(
        update={
            "damage_resistances": [DamageType.FIRE],
            "saving_throw_bonuses": {"dexterity": 2},
        },
    )
    target = EncounterCombatant(
        combatant_id="target", side="monsters", position_ft=30,
        state=build_combatant_state(target_template),
    )

    event = resolve_save_action(
        1, 1, _actor(), target, _action(40), 30, FixedDiceProvider([1, 6, 4]),
    )

    assert event.save_succeeded is False
    assert [(part.damage_type, part.total, part.applied_total) for part in event.damage_components] == [
        (DamageType.FIRE, 6, 3),
        (DamageType.RADIANT, 4, 4),
    ]
    assert event.damage_roll is not None
    assert event.damage_roll.total == 7


def test_successful_save_halves_each_typed_component_before_defenses() -> None:
    target_template = build_goblin_warrior().model_copy(
        update={"damage_resistances": [DamageType.FIRE]},
    )
    target = EncounterCombatant(
        combatant_id="target", side="monsters", position_ft=30,
        state=build_combatant_state(target_template),
    )

    event = resolve_save_action(
        1, 1, _actor(), target, _action(1), 30, FixedDiceProvider([20, 5, 3]),
    )

    assert event.save_succeeded is True
    assert [(part.damage_type, part.total, part.applied_total) for part in event.damage_components] == [
        (DamageType.FIRE, 2, 1),
        (DamageType.RADIANT, 1, 1),
    ]
    assert event.damage_roll is not None
    assert event.damage_roll.total == 2
