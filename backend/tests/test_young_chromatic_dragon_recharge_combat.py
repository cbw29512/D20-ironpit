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
    ("srd-young-black-dragon", "Young Black Dragon", "dexterity", 14, "line", 30, 5, 14, 6, "acid"),
    ("srd-young-blue-dragon", "Young Blue Dragon", "dexterity", 16, "line", 60, 5, 10, 10, "lightning"),
    ("srd-young-green-dragon", "Young Green Dragon", "constitution", 14, "cone", 30, None, 12, 6, "poison"),
    ("srd-young-red-dragon", "Young Red Dragon", "dexterity", 17, "cone", 30, None, 16, 6, "fire"),
    ("srd-young-white-dragon", "Young White Dragon", "constitution", 15, "cone", 30, None, 9, 8, "cold"),
]


@pytest.mark.parametrize("template_id,name,ability,dc,shape,length,width,count,size,damage_type", CASES)
def test_young_chromatic_dragon_bindings_match_srd(
    template_id, name, ability, dc, shape, length, width, count, size, damage_type,
) -> None:
    dragon = build_combatant_from_capabilities(template_id)
    row = next(row for row in load_monster_rows() if row["name"] == name)
    assert audit_monster_source(dragon, row) == []
    assert dragon.speed_ft == 80
    assert dragon.attack_action is not None
    assert len(dragon.attack_action.slots) == 3
    assert all(slot.attack_ids == [f"{template_id.removeprefix('srd-')}-rend"] for slot in dragon.attack_action.slots)
    breath = dragon.saving_throw_actions[0]
    assert (breath.save_ability, breath.dc, breath.success_damage) == (ability, dc, "half")
    assert breath.area is not None
    assert (breath.area.shape, breath.area.origin, breath.area.length_ft) == (shape, "self", length)
    assert breath.area.width_ft == width
    assert (breath.damage_dice_count, breath.damage_dice_size, breath.damage_type) == (count, size, damage_type)
    assert breath.resource_id is not None


def test_young_black_dragon_line_breath_then_failed_recharge_falls_back_to_three_rends() -> None:
    setup = build_encounter_setup(EncounterSelection(
        hero_ids=["karnok-stoneward-l1"], monster_ids=["srd-young-black-dragon"],
    ))
    hero, dragon = setup.heroes[0], setup.monsters[0]
    hero.state.position = GridPosition(x=0, y=6)
    dragon.state.position = GridPosition(x=1, y=6)
    hero.state.initiative_total = 10
    dragon.state.initiative_total = 20
    resource = resource_state(dragon.state, "young-black-dragon-acid-breath-recharge")
    assert resource.current_uses == 1

    first_turn, sequence = resolve_combat_turn(
        1, 1, dragon, hero, setup, FixedDiceProvider([20] + [1] * 14),
    )
    saves = [event for event in first_turn if event.event_type == "saving_throw"]
    assert len(saves) == 1
    assert saves[0].feature_id == "young-black-dragon-acid-breath"
    assert resource.current_uses == 0

    second_turn, _ = resolve_combat_turn(
        sequence, 2, dragon, hero, setup,
        # Force ordinary misses so this proof is independent of target HP and critical expansion.
        FixedDiceProvider([4] + [2] * 12),
    )
    recharge = [event for event in second_turn if event.resource_roll is not None]
    assert len(recharge) == 1
    assert recharge[0].resource_roll.selected_roll == 4
    attacks = [event for event in second_turn if event.event_type == "attack"]
    assert [event.weapon_id for event in attacks] == ["young-black-dragon-rend"] * 3
