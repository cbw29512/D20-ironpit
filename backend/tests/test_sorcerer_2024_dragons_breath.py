from __future__ import annotations

from app.combat.concentration_repeat_saves import (
    choose_concentration_repeat_save,
    resolve_concentration_repeat_save,
)
from app.combat.dice import FixedDiceProvider
from app.combat.spell_policy import choose_spell
from app.combat.state import build_combatant_state
from app.combat.timed_self_buff_policy import choose_timed_self_buff_action
from app.combat.timed_self_buffs import resolve_timed_self_buff
from app.content.arena_map import build_standard_iron_pit_map
from app.content.monsters import build_commoner
from app.content.sorcerer_draconic_2024_runtime import build_nyra_emberveil_2024
from app.domain.encounters import EncounterCombatant, EncounterSetup
from app.domain.grid import GridPosition


def _member(template, combatant_id: str, side: str, x: int, y: int) -> EncounterCombatant:
    member = EncounterCombatant(
        combatant_id=combatant_id,
        side=side,
        position_ft=abs(x) * 5,
        state=build_combatant_state(template),
    )
    member.state.position = GridPosition(x=x, y=y)
    return member


def _setup(nyra: EncounterCombatant, enemy: EncounterCombatant) -> EncounterSetup:
    return EncounterSetup(
        heroes=[nyra],
        monsters=[enemy],
        hero_total_levels=nyra.state.template.level,
        monster_total_cr="0",
        ruleset="2024",
        map_definition=build_standard_iron_pit_map(),
    )


def _slot(member: EncounterCombatant, level: int):
    return next(item for item in member.state.resources if item.id == f"spell-slot-{level}")


def test_dragons_breath_cast_starts_slot_concentration_and_later_exhales() -> None:
    nyra = _member(build_nyra_emberveil_2024(3), "nyra", "heroes", 2, 2)
    enemy = _member(build_commoner(), "enemy", "monsters", 4, 2)
    setup = _setup(nyra, enemy)
    breath = next(item for item in nyra.state.template.spell_save_actions if item.id == "dragons-breath")
    cast = next(item for item in nyra.state.template.timed_self_buff_actions if item.id == "dragons-breath")
    assert breath.repeat_only is True
    assert breath.damage_type == "fire"
    assert breath.damage_dice_count == 3
    assert choose_spell(nyra, setup, "1:nyra") is None or choose_spell(nyra, setup, "1:nyra").action.id != "dragons-breath"
    assert choose_concentration_repeat_save(nyra, setup) is None

    grant_only = nyra.state.template.model_copy(update={
        "timed_self_buff_actions": [cast],
    })
    isolated = _member(grant_only, "nyra-grant", "heroes", 2, 2)
    isolated_setup = _setup(isolated, enemy)
    assert choose_timed_self_buff_action(isolated, isolated_setup) is None

    slot_before = _slot(nyra, 2).current_uses
    event = resolve_timed_self_buff(1, 1, nyra, cast, setup=setup, turn_key="1:nyra")
    assert event.concentration_started_effect_id == "dragons-breath"
    assert nyra.state.concentration is not None
    assert nyra.state.concentration.effect_id == "dragons-breath"
    assert nyra.state.concentration.slot_level == 2
    assert _slot(nyra, 2).current_uses == slot_before - 1
    chosen = choose_spell(nyra, setup, "2:nyra")
    assert chosen is None or chosen.action.id != "dragons-breath"

    nyra.state.action_available = True
    repeat = choose_concentration_repeat_save(nyra, setup)
    assert repeat is not None
    assert repeat.action.id == "dragons-breath-exhale"
    assert repeat.spell_choice.action.id == "dragons-breath"
    assert repeat.spell_choice.slot_level == 2
    events, _ = resolve_concentration_repeat_save(
        2, 2, nyra, setup, repeat, "2:nyra", FixedDiceProvider([1, 20, 6, 6, 6]),
    )
    save_event = next(item for item in events if item.event_type == "saving_throw")
    assert save_event.damage_roll is not None
    assert save_event.damage_roll.total == 18
    assert _slot(nyra, 2).current_uses == slot_before - 1
    assert nyra.state.concentration is not None
    assert nyra.state.concentration.effect_id == "dragons-breath"
