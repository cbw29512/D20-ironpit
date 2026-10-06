from app.content.capability_compiler import compile_combatant
from app.content.monster_basic_candidates_2014 import basic_blockers_2014, unsupported_traits_2014
from app.content.monster_definition_adapter_2014 import adapt_basic_monster_2014
from app.content.monster_inactive_pit_abilities import (
    is_inactive_pit_action,
    is_inactive_pit_trait,
)
from app.content.monster_source_2014 import load_monster_source_2014


def _by_id():
    return {monster.id: monster for monster in load_monster_source_2014()}


def test_inactive_form_and_communication_do_not_block() -> None:
    source = _by_id()
    mimic = source["mimic"]
    assert "Shapechanger" in mimic.trait_names
    assert "Adhesive (Object Form Only)" in mimic.trait_names
    assert "False Appearance (Object Form Only)" in mimic.trait_names
    assert "Shapechanger" not in unsupported_traits_2014(mimic)
    assert "Adhesive (Object Form Only)" not in unsupported_traits_2014(mimic)
    assert "Grappler" in unsupported_traits_2014(mimic)

    otyugh = source["otyugh"]
    assert "Limited Telepathy" not in unsupported_traits_2014(otyugh)
    assert is_inactive_pit_trait("Limited Telepathy") is True

    bronze = source["adult-bronze-dragon"]
    assert "Change Shape" in bronze.action_names
    assert is_inactive_pit_action("Change Shape") is True


def test_inactive_names_stay_printed_on_ready_cards() -> None:
    source = _by_id()
    for monster_id, trait in (
        ("awakened-shrub", "False Appearance"),
        ("animated-armor", "Antimagic Susceptibility"),
        ("grimlock", "Blind Senses"),
        ("adult-silver-dragon", "Legendary Resistance (3/Day)"),
    ):
        monster = source[monster_id]
        assert basic_blockers_2014(monster) == ()
        template = compile_combatant(adapt_basic_monster_2014(monster))
        assert trait in template.source_trait_names
        if monster_id == "adult-silver-dragon":
            assert template.save_success_overrides[0].source_name == "Legendary Resistance (3/Day)"


def test_combat_math_traits_are_not_inactive() -> None:
    assert is_inactive_pit_trait("Gnome Cunning") is False
    assert is_inactive_pit_trait("Grappler") is False
    assert is_inactive_pit_trait("Assassinate") is False
    assert is_inactive_pit_action("Scare") is False
    assert is_inactive_pit_action("Etherealness") is False
    assert is_inactive_pit_action("Children of the Night (1/Day)") is True
