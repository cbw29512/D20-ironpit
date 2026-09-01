import pytest

from app.combat.attacks import resolve_attack
from app.combat.concentration import concentration_dc, start_concentration
from app.combat.dice import FixedDiceProvider
from app.combat.modifier_stack import add_modifier, effective_armor_class, effective_speed
from app.combat.saving_throw_rolls import resolve_saving_throw
from app.combat.state import begin_turn, build_combatant_state
from app.combat.timed_conditions import apply_timed_condition
from app.combat.zero_hp import apply_damage
from app.content.roster import build_arena_roster
from app.domain.modifiers import CombatModifier, ModifierKind


def _state(template_id: str):
    roster = build_arena_roster()
    template = next(
        item for item in [*roster.characters, *roster.monsters] if item.id == template_id
    ).model_copy(deep=True)
    return build_combatant_state(template)


def _modifier(
    modifier_id: str,
    source_id: str,
    effect_id: str,
    kind: ModifierKind,
    *,
    flat_bonus: int = 0,
    dice_count: int = 0,
    dice_size: int = 0,
    concentration: bool = False,
):
    return CombatModifier(
        id=modifier_id,
        source_id=source_id,
        source_effect_id=effect_id,
        kind=kind,
        flat_bonus=flat_bonus,
        dice_count=dice_count,
        dice_size=dice_size,
        concentration_required=concentration,
    )


def test_modifier_schema_fails_closed_on_invalid_payloads() -> None:
    with pytest.raises(ValueError):
        _modifier("bad-die", "hero", "bless", ModifierKind.ATTACK_ROLL_BONUS_DIE)
    with pytest.raises(ValueError):
        CombatModifier(
            id="bad-ac", source_id="hero", source_effect_id="spell",
            kind=ModifierKind.ARMOR_CLASS, dice_count=1, dice_size=4,
        )


def test_ac_modifier_changes_hit_threshold_without_mutating_template_ac() -> None:
    attacker = _state("karnok-stoneward-l1")
    defender = _state("srd-commoner")
    base_ac = defender.template.armor_class
    add_modifier(defender, _modifier(
        "shield-of-faith", "defender", "shield-of-faith", ModifierKind.ARMOR_CLASS,
        flat_bonus=2, concentration=True,
    ))
    assert effective_armor_class(defender) == base_ac + 2
    event = resolve_attack(
        1, 1, attacker, defender, attacker.template.weapon_attack, 5, FixedDiceProvider([6]),
    )
    assert event.attack_roll is not None and event.attack_roll.total == 11
    assert event.hit is False
    assert defender.template.armor_class == base_ac


def test_attack_and_save_bonus_dice_feed_the_shared_d20_pipeline() -> None:
    attacker = _state("karnok-stoneward-l1")
    defender = _state("srd-commoner")
    add_modifier(attacker, _modifier(
        "bless-attack", "hero", "bless", ModifierKind.ATTACK_ROLL_BONUS_DIE,
        dice_count=1, dice_size=4, concentration=True,
    ))
    add_modifier(defender, _modifier(
        "target-ac", "target", "test", ModifierKind.ARMOR_CLASS, flat_bonus=3,
    ))
    event = resolve_attack(
        1, 1, attacker, defender, attacker.template.weapon_attack, 5,
        FixedDiceProvider([6, 2, 1, 1, 1, 1]),
    )
    assert event.attack_roll is not None and event.attack_roll.total == 13
    assert event.hit is True

    saving = _state("karnok-stoneward-l1")
    add_modifier(saving, _modifier(
        "bless-save", "hero", "bless", ModifierKind.SAVING_THROW_BONUS_DIE,
        dice_count=1, dice_size=4, concentration=True,
    ))
    roll, succeeded = resolve_saving_throw(saving, "constitution", 10, FixedDiceProvider([4, 2]))
    assert roll is not None and roll.total == 10
    assert succeeded is True


def test_speed_modifier_drives_turn_movement_budget() -> None:
    state = _state("karnok-stoneward-l1")
    add_modifier(state, _modifier(
        "slow-speed", "source", "slow", ModifierKind.SPEED, flat_bonus=-10,
    ))
    assert effective_speed(state) == 20
    begin_turn(state)
    assert state.movement_remaining_ft == 20


def test_2024_concentration_dc_rounds_down_and_caps_at_30() -> None:
    assert concentration_dc(1) == 10
    assert concentration_dc(21) == 10
    assert concentration_dc(22) == 11
    assert concentration_dc(60) == 30
    assert concentration_dc(200) == 30


def test_new_concentration_replaces_old_and_removes_linked_modifiers() -> None:
    owner = _state("karnok-stoneward-l1")
    ally = _state("rokhan-stonefury-l1")
    start_concentration(owner, "hero-1", "shield-of-faith", 1, [ally])
    add_modifier(ally, _modifier(
        "shield-ally", "hero-1", "shield-of-faith", ModifierKind.ARMOR_CLASS,
        flat_bonus=2, concentration=True,
    ))
    start_concentration(owner, "hero-1", "bless", 2, [ally])
    assert owner.concentration is not None and owner.concentration.effect_id == "bless"
    assert ally.active_modifiers == []


def test_temp_hp_damage_still_forces_concentration_save_and_failure_removes_modifier() -> None:
    owner = _state("karnok-stoneward-l1")
    owner.temporary_hp = 10
    start_concentration(owner, "hero-1", "shield-of-faith", 1)
    add_modifier(owner, _modifier(
        "shield-self", "hero-1", "shield-of-faith", ModifierKind.ARMOR_CLASS,
        flat_bonus=2, concentration=True,
    ))
    hp_before = owner.current_hp
    apply_damage(owner, 5, dice=FixedDiceProvider([1]))
    assert owner.current_hp == hp_before
    assert owner.temporary_hp == 5
    assert owner.concentration is None
    assert owner.active_modifiers == []


def test_incapacitated_or_unconscious_creature_loses_concentration_without_a_save() -> None:
    owner = _state("karnok-stoneward-l1")
    start_concentration(owner, "hero-1", "shield-of-faith", 1)
    add_modifier(owner, _modifier(
        "shield-self", "hero-1", "shield-of-faith", ModifierKind.ARMOR_CLASS,
        flat_bonus=2, concentration=True,
    ))
    apply_timed_condition(owner, "stunned", "monster-1")
    assert owner.concentration is None
    assert owner.active_modifiers == []

    owner = _state("karnok-stoneward-l1")
    next(item for item in owner.resources if item.id == "relentless-endurance").current_uses = 0
    start_concentration(owner, "hero-1", "shield-of-faith", 1)
    apply_damage(owner, owner.current_hp)
    assert owner.is_unconscious is True
    assert owner.concentration is None
