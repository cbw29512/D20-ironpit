from app.combat.attacks import resolve_attack
from app.combat.concentration import end_concentration_if_expired, resolve_concentration_damage
from app.combat.dice import FixedDiceProvider
from app.combat.precombat_spells import prepare_defenses, select_defensive_targets
from app.combat.saving_throw_rolls import resolve_saving_throw
from app.combat.state import build_combatant_state
from app.content.audited_fighter import build_karnok_stoneward
from app.content.spell_effects import BLESS
from app.domain.combatants import ResourceDefinition, WeaponAttackKind
from app.domain.encounters import EncounterCombatant, EncounterSetup


def _member(
    combatant_id: str,
    side: str,
    position_ft: int,
    *,
    attack_kind: WeaponAttackKind = WeaponAttackKind.MELEE,
    bless_caster: bool = False,
    armor_class: int | None = None,
) -> EncounterCombatant:
    template = build_karnok_stoneward().model_copy(deep=True)
    template.id = f"template-{combatant_id}"
    template.name = combatant_id
    template.weapon_attack.weapon.attack_kind = attack_kind
    template.defensive_spell_actions = [BLESS] if bless_caster else []
    template.resources = [ResourceDefinition(id="spell-slot-1", name="Level 1 Slot", max_uses=1)] if bless_caster else []
    if armor_class is not None:
        template.armor_class = armor_class
    return EncounterCombatant(
        combatant_id=combatant_id,
        side=side,
        position_ft=position_ft,
        state=build_combatant_state(template),
    )


def _bless_setup() -> tuple[EncounterSetup, EncounterCombatant, list[EncounterCombatant]]:
    caster = _member("caster", "heroes", 0, attack_kind=WeaponAttackKind.RANGED, bless_caster=True)
    front_near = _member("front-near", "heroes", 25)
    front_far = _member("front-far", "heroes", 15)
    backline = _member("backline", "heroes", 10, attack_kind=WeaponAttackKind.RANGED)
    out_of_range = _member("out-of-range", "heroes", 35)
    enemy = _member("enemy", "monsters", 40, armor_class=30)
    heroes = [caster, front_far, backline, front_near, out_of_range]
    setup = EncounterSetup(heroes=heroes, monsters=[enemy], hero_total_levels=5, monster_total_cr="1")
    return setup, caster, [front_near, front_far, backline, out_of_range]


def test_bless_prioritizes_melee_line_then_caster_and_enforces_range() -> None:
    setup, caster, allies = _bless_setup()
    front_near, front_far, backline, out_of_range = allies

    targets = select_defensive_targets(caster, setup, BLESS, 1)

    assert [target.combatant_id for target in targets] == ["front-near", "front-far", "caster"]
    assert backline not in targets
    assert out_of_range not in targets
    assert BLESS.target_count == 3
    assert BLESS.range_ft == 30


def test_bless_applies_independent_attack_and_save_d4s_and_expires_cleanly() -> None:
    setup, caster, allies = _bless_setup()
    front_near, front_far, backline, out_of_range = allies
    enemy = setup.monsters[0]

    events, sequence = prepare_defenses(setup)

    assert sequence == 2
    assert len(events) == 1
    assert events[0].feature_id == "bless"
    assert events[0].concentration_started_effect_id == "bless"
    assert caster.state.opening_buff_spell_id == "bless"
    assert caster.state.concentration is not None
    assert caster.state.concentration.effect_id == "bless"
    assert caster.state.concentration.expires_round == 11
    assert next(item for item in caster.state.resources if item.id == "spell-slot-1").current_uses == 0

    for target in (front_near, front_far, caster):
        kinds = {modifier.kind.value for modifier in target.state.active_modifiers}
        assert kinds == {"attack-roll-bonus-die", "saving-throw-bonus-die"}
    assert backline.state.active_modifiers == []
    assert out_of_range.state.active_modifiers == []

    first_attack = resolve_attack(
        2, 1, front_near.state, enemy.state, front_near.state.template.weapon_attack, 5,
        FixedDiceProvider([10, 1]), spend_action=False,
    )
    second_attack = resolve_attack(
        3, 1, front_near.state, enemy.state, front_near.state.template.weapon_attack, 5,
        FixedDiceProvider([10, 4]), spend_action=False,
    )
    assert first_attack.attack_roll is not None and first_attack.attack_roll.rolls[-1] == 1
    assert second_attack.attack_roll is not None and second_attack.attack_roll.rolls[-1] == 4
    assert first_attack.attack_roll.notation.endswith("1d4")
    assert second_attack.attack_roll.notation.endswith("1d4")

    first_save, _ = resolve_saving_throw(caster.state, "constitution", 30, FixedDiceProvider([10, 2]))
    second_save, _ = resolve_saving_throw(caster.state, "constitution", 30, FixedDiceProvider([10, 4]))
    assert first_save.rolls[-1] == 2
    assert second_save.rolls[-1] == 4
    assert first_save.notation.endswith("1d4")
    assert second_save.notation.endswith("1d4")

    states = [member.state for member in [*setup.heroes, *setup.monsters]]
    assert end_concentration_if_expired(caster.state, 10, states) is False
    assert end_concentration_if_expired(caster.state, 11, states) is True
    assert caster.state.concentration is None
    assert all(not member.state.active_modifiers for member in (front_near, front_far, caster))


def test_failed_bless_concentration_save_removes_every_target_modifier() -> None:
    setup, caster, allies = _bless_setup()
    front_near, front_far, _, _ = allies
    prepare_defenses(setup)
    states = [member.state for member in [*setup.heroes, *setup.monsters]]

    check = resolve_concentration_damage(caster.state, 1, FixedDiceProvider([1, 1]), states)

    assert check is not None and check.ended is True
    assert caster.state.concentration is None
    assert all(not member.state.active_modifiers for member in (front_near, front_far, caster))


def test_opening_buff_never_recasts_after_concentration_breaks() -> None:
    setup, caster, _ = _bless_setup()
    events, _ = prepare_defenses(setup)
    assert [event.feature_id for event in events] == ["bless"]
    slot = next(item for item in caster.state.resources if item.id == "spell-slot-1")
    states = [member.state for member in [*setup.heroes, *setup.monsters]]
    assert resolve_concentration_damage(caster.state, 1, FixedDiceProvider([1, 1]), states).ended is True
    slot.current_uses = 1

    second_prep, _ = prepare_defenses(setup, 99)

    assert second_prep == []
    assert slot.current_uses == 1
    assert caster.state.opening_buff_spell_id == "bless"
