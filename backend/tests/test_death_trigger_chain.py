"""Integration proof that Death Trigger cascades drain before combat removal."""
from app.combat.death_trigger_dispatch import resolve_pending_death_triggers
from app.combat.state import build_combatant_state
from app.content.capability_compiler import compile_combatant
from app.content.monster_death_triggers_2014 import death_trigger_actions_2014
from app.content.monster_definition_adapter_2014 import adapt_basic_monster_2014
from app.content.monster_source_2014 import load_monster_source_2014
from app.content.roster import build_arena_roster
from app.domain.encounters import EncounterCombatant, EncounterSetup


class _OnesDice:
    def roll(self, sides: int) -> int:
        assert sides >= 2
        return 1


def _member(template, combatant_id: str, side: str, position_ft: int):
    return EncounterCombatant(
        combatant_id=combatant_id,
        side=side,
        position_ft=position_ft,
        state=build_combatant_state(template),
    )


def _short_range_damage_trigger():
    """Compile a source card selected only by the shared effect contract."""
    candidates = (
        (card, death_trigger_actions_2014(card))
        for card in load_monster_source_2014()
    )
    card, actions = next(
        (card, actions) for card, actions in candidates
        if any(action.range_ft == 5 and action.damage is not None for action in actions)
    )
    definition = adapt_basic_monster_2014(card).model_copy(update={
        "death_trigger_effect_ids": [action.id for action in actions],
        "death_trigger_actions": actions,
    })
    return compile_combatant(definition)


def test_death_trigger_dispatch_drains_a_newly_killed_source() -> None:
    roster = build_arena_roster("2014")
    magmin = _short_range_damage_trigger()
    hero = roster.characters[0]
    source = _member(magmin, "source", "monsters", 0)
    chained = _member(magmin, "chained", "monsters", 5)
    target = _member(hero, "target", "heroes", 10)

    source.state.current_hp = 0
    source.state.is_alive = False
    source.state.is_dead = True
    chained.state.current_hp = 1
    target_hp = target.state.current_hp
    setup = EncounterSetup(
        heroes=[target],
        monsters=[source, chained],
        hero_total_levels=1,
        monster_total_cr="1",
    )

    events, sequence = resolve_pending_death_triggers(
        1, 1, setup, _OnesDice(),
    )

    saves = [event for event in events if event.event_type == "saving_throw"]
    assert len(saves) == 2
    assert sequence > 1
    assert chained.state.is_dead is True
    assert target.state.current_hp < target_hp
    assert source.state.feature_use_counts["death-trigger"] == 1
    assert chained.state.feature_use_counts["death-trigger"] == 1


def test_death_trigger_consumption_resets_with_new_fight_state() -> None:
    roster = build_arena_roster("2014")
    magmin = _short_range_damage_trigger()
    hero = roster.characters[0]

    for fight_number in (1, 2):
        source = _member(magmin, f"source-{fight_number}", "monsters", 0)
        target = _member(hero, f"target-{fight_number}", "heroes", 5)
        source.state.current_hp = 0
        source.state.is_alive = False
        source.state.is_dead = True
        setup = EncounterSetup(
            heroes=[target],
            monsters=[source],
            hero_total_levels=1,
            monster_total_cr="1/2",
        )

        events, _ = resolve_pending_death_triggers(
            1, 1, setup, _OnesDice(),
        )

        assert any(event.event_type == "saving_throw" for event in events)
        assert source.state.feature_use_counts["death-trigger"] == 1
        assert "death-trigger" in source.state.active_buff_effect_ids

    assert magmin.death_trigger_effect_ids == [
        action.id for action in magmin.death_trigger_actions
    ]
