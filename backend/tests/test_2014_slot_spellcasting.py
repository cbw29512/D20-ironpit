from app.combat.landing_offense_policy import decide_post_move_offense
from app.combat.spell_policy import choose_spell
from app.combat.state import build_combatant_state
from app.content.capability_compiler import compile_combatant
from app.content.monster_basic_candidates_2014 import basic_blockers_2014
from app.content.monster_definition_adapter_2014 import adapt_basic_monster_2014
from app.content.monster_roster_2014 import build_basic_2014_monsters
from app.content.monster_slot_spells_2014 import supports_slot_spellcasting_2014
from app.content.monster_source_2014 import load_monster_source_2014
from app.content.arena_map import build_standard_iron_pit_map
from app.content.monsters import build_commoner
from app.domain.encounters import EncounterCombatant, EncounterSetup
from app.domain.grid import GridPosition


def _source(monster_id: str):
    return next(item for item in load_monster_source_2014() if item.id == monster_id)


def _acolyte_template():
    return compile_combatant(adapt_basic_monster_2014(_source("acolyte")))


def test_acolyte_is_the_first_fully_covered_2014_slot_caster() -> None:
    acolyte = _source("acolyte")
    assert supports_slot_spellcasting_2014(acolyte) is True
    assert basic_blockers_2014(acolyte) == ()
    leftover = [
        monster.id
        for monster in load_monster_source_2014()
        if monster.spellcasting and supports_slot_spellcasting_2014(monster)
    ]
    assert leftover == ["acolyte"]


def test_acolyte_reuses_existing_cleric_constructors_and_slots() -> None:
    template = _acolyte_template()
    assert template.id == "2014-acolyte"
    sacred = next(item for item in template.spell_save_actions if item.id == "sacred-flame")
    assert (sacred.dc, sacred.damage_dice_count, sacred.damage_dice_size, sacred.level) == (12, 1, 8, 0)
    assert {item.id for item in template.defensive_spell_actions} == {"bless", "sanctuary"}
    sanctuary = next(item for item in template.defensive_spell_actions if item.id == "sanctuary")
    assert sanctuary.modifier_effects[0].save_dc == 12
    cure = next(item for item in template.healing_actions if item.id == "cure-wounds")
    assert (cure.healing_bonus, cure.resource_id, cure.resource_cost) == (2, "spell-slot-1", 1)
    assert any(item.id == "spell-slot-1" and item.max_uses == 3 for item in template.resources)
    assert {item.id for item in template.spell_save_actions} == {"sacred-flame"}


def test_acolyte_damage_first_prefers_sacred_flame_over_club() -> None:
    caster = EncounterCombatant(
        combatant_id="acolyte",
        side="monsters",
        position_ft=0,
        state=build_combatant_state(_acolyte_template()),
    )
    caster.state.position = GridPosition(x=4, y=4)
    target = EncounterCombatant(
        combatant_id="commoner",
        side="heroes",
        position_ft=5,
        state=build_combatant_state(build_commoner()),
    )
    target.state.position = GridPosition(x=10, y=4)
    setup = EncounterSetup(
        heroes=[target],
        monsters=[caster],
        hero_total_levels=1,
        monster_total_cr="1/4",
        ruleset="2014",
        map_definition=build_standard_iron_pit_map(),
    )
    choice = choose_spell(caster, setup, "1:acolyte")
    assert choice is not None and choice.action.id == "sacred-flame"
    pick = decide_post_move_offense(caster, setup, "1:acolyte")
    assert pick.family == "spell"


def test_incomplete_2014_slot_lists_stay_fail_closed() -> None:
    for monster_id in ("cult-fanatic", "mage", "priest", "archmage", "spirit-naga"):
        monster = _source(monster_id)
        assert supports_slot_spellcasting_2014(monster) is False
        assert "mechanic:spellcasting" in basic_blockers_2014(monster)


def test_2014_roster_includes_acolyte_at_155() -> None:
    roster = build_basic_2014_monsters()
    assert len(roster) == 155
    assert any(item.id == "2014-acolyte" for item in roster)
