from app.combat.dice import FixedDiceProvider
from app.combat.encounter_setup import build_encounter_setup
from app.combat.saving_throws import resolve_save_action
from app.domain.actions import SavingThrowAction
from app.domain.models import EncounterSelection, RollMode
from app.domain.traits import CombatTrait


def _setup():
    setup = build_encounter_setup(EncounterSelection(
        hero_ids=["karnok-stoneward-l1"], monster_ids=["srd-commoner"],
    ))
    return setup, setup.monsters[0], setup.heroes[0]


def _blast() -> SavingThrowAction:
    return SavingThrowAction(
        id="evasion-probe", name="Evasion Probe", save_ability="dexterity", dc=10,
        range_ft=30, damage_dice_count=2, damage_dice_size=6,
        damage_type="fire", success_damage="half",
    )


def test_evasion_success_takes_no_damage() -> None:
    setup, actor, target = _setup()
    target.state.template.combat_traits.append(CombatTrait.EVASION)
    before = target.state.current_hp
    event = resolve_save_action(1, 1, actor, target, _blast(), 5, FixedDiceProvider([20]), affected_states=[target.state])
    assert event.saving_throw_roll is not None and event.saving_throw_roll.mode is RollMode.NORMAL
    assert event.save_succeeded is True
    assert event.damage_roll is None and event.damage_components == []
    assert target.state.current_hp == before
    assert "Evasion modifies the damage" in event.description


def test_evasion_failure_takes_half_damage() -> None:
    setup, actor, target = _setup()
    target.state.template.combat_traits.append(CombatTrait.EVASION)
    before = target.state.current_hp
    event = resolve_save_action(1, 1, actor, target, _blast(), 5, FixedDiceProvider([1, 6, 4]), affected_states=[target.state])
    assert event.save_succeeded is False
    assert event.damage_roll is not None and event.damage_roll.total == 5
    assert event.damage_components[0].total == 5
    assert target.state.current_hp == before - 5


def test_evasion_does_not_change_non_dex_or_no_half_save_damage() -> None:
    setup, actor, target = _setup()
    target.state.template.combat_traits.append(CombatTrait.EVASION)
    before = target.state.current_hp
    action = _blast().model_copy(update={"save_ability": "constitution", "success_damage": "none"})
    event = resolve_save_action(1, 1, actor, target, action, 5, FixedDiceProvider([1, 6, 4]), affected_states=[target.state])
    assert event.save_succeeded is False
    assert event.damage_roll is not None and event.damage_roll.total == 10
    assert target.state.current_hp == before - 10
