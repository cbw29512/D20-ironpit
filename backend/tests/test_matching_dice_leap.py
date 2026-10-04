from app.combat.dice import FixedDiceProvider
from app.combat.spell_attack_sequence import resolve_spell_attack_sequence
from app.combat.state import build_combatant_state
from app.content.audited_fighter import build_karnok_stoneward
from app.content.monsters import build_commoner
from app.content.sorcerer_2024_spells import chromatic_orb_2024
from app.domain.combatants import ResourceDefinition
from app.domain.encounters import EncounterCombatant, EncounterSetup


def _caster(slot_level: int = 1) -> EncounterCombatant:
    template = build_karnok_stoneward().model_copy(deep=True)
    template.id = "nyra"
    template.name = "Nyra"
    template.spell_attack_actions = [chromatic_orb_2024(8)]
    template.resources = [
        ResourceDefinition(id=f"spell-slot-{slot_level}", name=f"Level {slot_level} Slot", max_uses=1),
    ]
    return EncounterCombatant(
        combatant_id="caster",
        side="heroes",
        position_ft=0,
        state=build_combatant_state(template),
    )


def _enemy(combatant_id: str, position: int) -> EncounterCombatant:
    template = build_commoner().model_copy(update={"max_hp": 40, "armor_class": 10})
    return EncounterCombatant(
        combatant_id=combatant_id,
        side="monsters",
        position_ft=position,
        state=build_combatant_state(template),
    )


def _setup(caster: EncounterCombatant, *enemies: EncounterCombatant) -> EncounterSetup:
    return EncounterSetup(
        heroes=[caster],
        monsters=list(enemies),
        hero_total_levels=1,
        monster_total_cr="0",
        ruleset="2024",
    )


def test_chromatic_orb_2024_binds_matching_dice_leap() -> None:
    spell = chromatic_orb_2024(8)
    assert spell.matching_dice_leap_range_ft == 30
    assert spell.damage_dice_count == 3
    assert spell.damage_dice_size == 8


def test_matching_d8s_leap_once_at_first_level() -> None:
    caster = _caster(1)
    first = _enemy("first", 30)
    second = _enemy("second", 60)
    third = _enemy("third", 90)
    setup = _setup(caster, first, second, third)
    spell = caster.state.template.spell_attack_actions[0]
    events, _ = resolve_spell_attack_sequence(
        1, 1, caster, first, spell, setup, "1:caster",
        FixedDiceProvider([12, 4, 4, 1, 12, 5, 5, 2, 12, 1, 2, 3]),
        slot_level=1,
    )
    targets = [event.target_id for event in events if event.event_type == "attack"]
    assert targets == ["first", "second"]
    assert all(event.hit for event in events if event.event_type == "attack")
    assert first.state.current_hp == 31
    assert second.state.current_hp == 28
    assert third.state.current_hp == 40


def test_unmatched_d8s_do_not_leap() -> None:
    caster = _caster(1)
    first = _enemy("first", 30)
    second = _enemy("second", 60)
    setup = _setup(caster, first, second)
    spell = caster.state.template.spell_attack_actions[0]
    events, _ = resolve_spell_attack_sequence(
        1, 1, caster, first, spell, setup, "1:caster",
        FixedDiceProvider([12, 1, 2, 3]),
        slot_level=1,
    )
    assert [event.target_id for event in events if event.event_type == "attack"] == ["first"]
    assert second.state.current_hp == 40


def test_missed_orb_does_not_leap() -> None:
    caster = _caster(1)
    first = _enemy("first", 30)
    first.state.template.armor_class = 20
    second = _enemy("second", 60)
    setup = _setup(caster, first, second)
    spell = caster.state.template.spell_attack_actions[0]
    events, _ = resolve_spell_attack_sequence(
        1, 1, caster, first, spell, setup, "1:caster",
        FixedDiceProvider([5]),
        slot_level=1,
    )
    assert events[0].hit is False
    assert [event.target_id for event in events if event.event_type == "attack"] == ["first"]
    assert second.state.current_hp == 40


def test_higher_slot_allows_two_leaps() -> None:
    caster = _caster(2)
    first = _enemy("first", 30)
    second = _enemy("second", 60)
    third = _enemy("third", 90)
    setup = _setup(caster, first, second, third)
    spell = caster.state.template.spell_attack_actions[0]
    events, _ = resolve_spell_attack_sequence(
        1, 1, caster, first, spell, setup, "1:caster",
        FixedDiceProvider([12, 4, 4, 1, 12, 5, 5, 2, 12, 1, 2, 3]),
        slot_level=2,
    )
    assert [event.target_id for event in events if event.event_type == "attack"] == [
        "first", "second", "third",
    ]
    assert third.state.current_hp == 34


def test_leap_can_leave_the_casters_spell_range() -> None:
    caster = _caster(1)
    first = _enemy("first", 90)
    second = _enemy("second", 120)
    setup = _setup(caster, first, second)
    spell = caster.state.template.spell_attack_actions[0]
    events, _ = resolve_spell_attack_sequence(
        1, 1, caster, first, spell, setup, "1:caster",
        FixedDiceProvider([12, 8, 8, 1, 12, 2, 3, 4]),
        slot_level=1,
    )
    assert [event.target_id for event in events if event.event_type == "attack"] == ["first", "second"]
    assert second.state.current_hp == 31
