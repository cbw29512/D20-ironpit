import pytest

from app.combat.dice import FixedDiceProvider
from app.combat.encounter_combat_turn import resolve_combat_turn
from app.combat.encounter_setup import build_encounter_setup
from app.combat.resources import resource_state
from app.content.capability_registry import build_combatant_from_capabilities
from app.content.monster_catalog import load_monster_rows
from app.content.monster_source_audit import audit_monster_source
from app.domain.grid import GridPosition
from app.domain.models import EncounterSelection


CASES = [
    ("srd-black-dragon-wyrmling", "Black Dragon Wyrmling", "dexterity", 11, "line", 15, 5, 5, 8, "acid"),
    ("srd-blue-dragon-wyrmling", "Blue Dragon Wyrmling", "dexterity", 12, "line", 30, 5, 6, 6, "lightning"),
    ("srd-green-dragon-wyrmling", "Green Dragon Wyrmling", "constitution", 11, "cone", 15, None, 6, 6, "poison"),
    ("srd-red-dragon-wyrmling", "Red Dragon Wyrmling", "dexterity", 13, "cone", 15, None, 7, 6, "fire"),
    ("srd-white-dragon-wyrmling", "White Dragon Wyrmling", "constitution", 12, "cone", 15, None, 5, 8, "cold"),
]


@pytest.mark.parametrize("template_id,name,ability,dc,shape,length,width,count,size,damage_type", CASES)
def test_chromatic_wyrmling_bindings_match_srd(
    template_id, name, ability, dc, shape, length, width, count, size, damage_type,
) -> None:
    wyrmling = build_combatant_from_capabilities(template_id)
    row = next(row for row in load_monster_rows() if row["name"] == name)
    assert audit_monster_source(wyrmling, row) == []
    assert wyrmling.attack_action is not None
    assert len(wyrmling.attack_action.slots) == 2
    breath = wyrmling.saving_throw_actions[0]
    assert (breath.save_ability, breath.dc, breath.success_damage) == (ability, dc, "half")
    assert breath.area is not None
    assert (breath.area.shape, breath.area.origin, breath.area.length_ft) == (shape, "self", length)
    assert breath.area.width_ft == width
    assert (breath.damage_dice_count, breath.damage_dice_size, breath.damage_type) == (count, size, damage_type)
    assert breath.resource_id is not None


def test_black_wyrmling_line_breath_then_failed_recharge_falls_back_to_two_rends() -> None:
    setup = build_encounter_setup(EncounterSelection(
        hero_ids=["karnok-stoneward-l1"], monster_ids=["srd-black-dragon-wyrmling"],
    ))
    hero, dragon = setup.heroes[0], setup.monsters[0]
    hero.state.position = GridPosition(x=0, y=6)
    dragon.state.position = GridPosition(x=1, y=6)
    hero.state.initiative_total = 10
    dragon.state.initiative_total = 20
    resource = resource_state(dragon.state, "black-dragon-wyrmling-acid-breath-recharge")
    assert resource.current_uses == 1

    first_turn, sequence = resolve_combat_turn(
        1, 1, dragon, hero, setup, FixedDiceProvider([20, 1, 1, 1, 1, 1]),
    )
    saves = [event for event in first_turn if event.event_type == "saving_throw"]
    assert len(saves) == 1 and saves[0].feature_id == "black-dragon-wyrmling-acid-breath"
    assert resource.current_uses == 0

    second_turn, _ = resolve_combat_turn(
        sequence, 2, dragon, hero, setup,
        FixedDiceProvider([4, 19, 1, 1, 19, 1, 1]),
    )
    recharge = [event for event in second_turn if event.resource_roll is not None]
    assert len(recharge) == 1 and recharge[0].resource_roll.selected_roll == 4
    attacks = [event for event in second_turn if event.event_type == "attack"]
    assert [event.weapon_id for event in attacks] == [
        "black-dragon-wyrmling-rend", "black-dragon-wyrmling-rend",
    ]
