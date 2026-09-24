from app.combat.dice import FixedDiceProvider
from app.combat.saving_throws import resolve_save_action
from app.combat.state import build_combatant_state
from app.content.audited_fighter import build_karnok_stoneward
from app.content.demo import build_goblin_warrior
from app.domain.actions import SaveDamageComponent, SavingThrowAction
from app.domain.encounters import EncounterCombatant
from app.domain.models import DamageType


def _member(template, combatant_id: str, side: str, position: int) -> EncounterCombatant:
    return EncounterCombatant(
        combatant_id=combatant_id,
        side=side,
        position_ft=position,
        state=build_combatant_state(template),
    )


def test_split_save_damage_applies_each_damage_type_defense_independently() -> None:
    actor = _member(build_goblin_warrior(), "caster", "monsters", 0)
    target_template = build_karnok_stoneward().model_copy(deep=True)
    target_template.damage_resistances = [DamageType.FIRE]
    target = _member(target_template, "target", "heroes", 30)

    action = SavingThrowAction(
        id="split-damage",
        name="Split Damage",
        save_ability="dexterity",
        dc=20,
        range_ft=60,
        damage_components=[
            SaveDamageComponent(source="Split Damage (Fire)", dice_count=2, dice_size=6, damage_type="fire"),
            SaveDamageComponent(source="Split Damage (Radiant)", dice_count=2, dice_size=6, damage_type="radiant"),
        ],
        success_damage="half",
        magical_effect=True,
    )

    event = resolve_save_action(
        1, 1, actor, target, action, 30,
        FixedDiceProvider([1, 4, 4, 3, 3]),
    )

    assert event.save_succeeded is False
    assert len(event.damage_components) == 2
    fire, radiant = event.damage_components
    assert fire.damage_type is DamageType.FIRE
    assert fire.total == 8
    assert fire.applied_total == 4
    assert radiant.damage_type is DamageType.RADIANT
    assert radiant.total == 6
    assert radiant.applied_total == 6
    assert event.damage_roll is not None
    assert event.damage_roll.total == 10


def test_split_save_damage_halves_each_typed_component_before_defenses() -> None:
    actor = _member(build_goblin_warrior(), "caster", "monsters", 0)
    target_template = build_karnok_stoneward().model_copy(deep=True)
    target_template.damage_resistances = [DamageType.FIRE]
    target = _member(target_template, "target", "heroes", 30)

    action = SavingThrowAction(
        id="split-damage",
        name="Split Damage",
        save_ability="dexterity",
        dc=10,
        range_ft=60,
        damage_components=[
            SaveDamageComponent(source="Split Damage (Fire)", dice_count=2, dice_size=6, damage_type="fire"),
            SaveDamageComponent(source="Split Damage (Radiant)", dice_count=2, dice_size=6, damage_type="radiant"),
        ],
        success_damage="half",
        magical_effect=True,
    )

    event = resolve_save_action(
        1, 1, actor, target, action, 30,
        FixedDiceProvider([20, 5, 4, 5, 4]),
    )

    assert event.save_succeeded is True
    fire, radiant = event.damage_components
    assert fire.total == 4
    assert fire.applied_total == 2
    assert radiant.total == 4
    assert radiant.applied_total == 4
    assert event.damage_roll is not None
    assert event.damage_roll.total == 6
