from app.content.capability_compiler import compile_combatant
from app.content.monster_catalog import load_monster_rows
from app.content.monster_source_audit import audit_monster_source
from app.content.simple_monster_source_definitions import build_simple_source_definitions
from app.content.simple_save_damage_spells import SIMPLE_SAVE_DAMAGE_SPELLS


def _row(name: str) -> dict[str, object]:
    return next(row for row in load_monster_rows() if row["name"] == name)


def test_thunderwave_is_one_shared_simple_spell_effect() -> None:
    spell = SIMPLE_SAVE_DAMAGE_SPELLS["thunderwave"]
    assert (spell.level, spell.save_ability, spell.dice_count, spell.dice_size) == (1, "constitution", 2, 8)
    assert spell.damage_type == "thunder"
    assert (spell.area_shape, spell.area_size_ft, spell.success_damage) == ("cube", 15, "half")


def test_druid_binds_printed_thunderwave_to_shared_save_and_two_daily_uses() -> None:
    definition = build_simple_source_definitions()["srd-druid"]
    action = next(action for action in definition.save_actions if action.id == "thunderwave")
    assert (action.dc, action.range_ft, action.damage.count, action.damage.size) == (13, 15, 2, 8)
    assert action.damage_type.value == "thunder"
    assert action.area is not None and (action.area.shape, action.area.size_ft) == ("cube", 15)
    resource = next(item for item in definition.resources if item.id == action.resource_id)
    assert resource.max_uses == 2

    template = compile_combatant(definition)
    assert audit_monster_source(template, _row("Druid")) == []
