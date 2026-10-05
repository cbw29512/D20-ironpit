from __future__ import annotations

from app.combat.dice import FixedDiceProvider
from app.combat.saving_throws import resolve_save_action
from app.combat.state import build_combatant_state
from app.content.audited_fighter import build_karnok_stoneward
from app.content.capability_compiler import compile_combatant
from app.content.monster_basic_candidates_2014 import basic_blockers_2014
from app.content.monster_definition_adapter_2014 import adapt_basic_monster_2014
from app.content.monster_roster_2014 import build_basic_2014_monsters
from app.content.monster_source_2014 import load_monster_source_2014
from app.domain.encounters import EncounterCombatant, EncounterSetup
from app.domain.grid import BattleMapDefinition, GridPosition

_UNLOCKED = {
    "silver-dragon-wyrmling": {
        "dc": 13, "cone_ft": 15, "cold_dice": (4, 8),
    },
    "young-silver-dragon": {
        "dc": 17, "cone_ft": 30, "cold_dice": (12, 8),
    },
}


def _source(monster_id: str):
    return next(item for item in load_monster_source_2014() if item.id == monster_id)


def _compile(monster_id: str):
    try:
        return compile_combatant(adapt_basic_monster_2014(_source(monster_id)))
    except Exception:
        raise


def _member(template, combatant_id: str, side: str, x: int) -> EncounterCombatant:
    try:
        state = build_combatant_state(template.model_copy(deep=True))
        state.position = GridPosition(x=x, y=0)
        return EncounterCombatant(
            combatant_id=combatant_id, side=side, position_ft=x * 5, state=state,
        )
    except Exception:
        raise


def test_silver_paralyzing_breath_family_unlocks() -> None:
    roster_ids = {item.id for item in build_basic_2014_monsters()}
    for monster_id, expected in _UNLOCKED.items():
        source = _source(monster_id)
        assert basic_blockers_2014(source) == ()
        assert f"2014-{monster_id}" in roster_ids
        template = _compile(monster_id)
        breaths = {action.id: action for action in template.saving_throw_actions}
        cold = breaths["cold-breath"]
        paralyze = breaths["paralyzing-breath"]
        assert cold.name == "Cold Breath"
        assert (cold.save_ability, cold.dc, cold.success_damage) == ("constitution", expected["dc"], "half")
        assert cold.area is not None and cold.area.length_ft == expected["cone_ft"]
        assert (cold.damage_dice_count, cold.damage_dice_size) == expected["cold_dice"]
        assert paralyze.name == "Paralyzing Breath"
        assert (paralyze.save_ability, paralyze.dc) == ("constitution", expected["dc"])
        rider = paralyze.failed_save_timed_effect
        assert rider is not None
        assert rider.effect_id == "paralyzed"
        assert rider.duration_rounds == 10
        assert (rider.repeat_save_ability, rider.repeat_save_dc, rider.repeat_save_timing) == (
            "constitution", expected["dc"], "target_turn_end",
        )
        assert cold.resource_id == paralyze.resource_id == "breath-weapons"
        assert template.recharge_rules[0].resource_id == "breath-weapons"
        assert template.recharge_rules[0].minimum_roll == 5


def test_paralyzing_breath_applies_printed_name() -> None:
    dragon = _member(_compile("silver-dragon-wyrmling"), "monster:silver-wyrmling", "monsters", 2)
    hero = _member(build_karnok_stoneward(), "hero:karnok", "heroes", 4)
    EncounterSetup(
        heroes=[hero], monsters=[dragon], hero_total_levels=1, monster_total_cr="2",
        ruleset="2014",
        map_definition=BattleMapDefinition(id="paralyzing-breath", width_squares=24, height_squares=24),
    )
    action = next(item for item in dragon.state.template.saving_throw_actions if item.id == "paralyzing-breath")
    event = resolve_save_action(1, 1, dragon, hero, action, 10, FixedDiceProvider([1]))
    assert event.save_succeeded is False
    assert event.applied_condition_ids == ["paralyzed"]
    assert "paralyzed" in hero.state.active_effect_ids
    assert "Paralyzing Breath" in event.description
