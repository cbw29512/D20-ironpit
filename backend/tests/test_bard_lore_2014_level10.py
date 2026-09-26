from __future__ import annotations

from app.content.bard_2014_spell_package import build_bard_2014_spell_package
from app.content.bard_lore_2014_combat_profile import build_lyra_2014_combat_profile
from app.content.bard_lore_2014_profile import build_lyra_silverstring_2014_profile
from app.content.bard_lore_2014_runtime import build_lyra_silverstring_2014
from app.content.build_audit import assert_character_build_raw_ready
from app.content.character_resource_audit import assert_character_resources_raw_ready
from app.content.pregen_combat_audit import assert_pregen_combat_stats


def test_level_ten_magical_secrets_use_shared_flame_strike_and_death_ward() -> None:
    package = build_bard_2014_spell_package(10)
    known = {spell.id: spell for spell in package.spells}

    assert len(package.spells) == 14
    assert set(known["flame-strike"].required_capabilities) >= {
        "save-damage", "area-damage", "multi-component-damage", "magical-secrets",
    }
    assert "magical-secrets" in known["death-ward"].required_capabilities
    assert "magical-secrets" not in known["mass-cure-wounds"].required_capabilities


def test_level_ten_binds_d10_inspiration_expertise_and_magical_secrets() -> None:
    profile = build_lyra_silverstring_2014_profile(10)
    hero = build_lyra_silverstring_2014(10)
    combat = build_lyra_2014_combat_profile(10)

    inspiration = hero.d20_bonus_die_actions[0]
    assert inspiration.id == "bardic-inspiration"
    assert inspiration.dice_size == 10

    assert hero.skill_bonuses == {
        "acrobatics": 10,
        "perception": 10,
        "performance": 13,
        "persuasion": 13,
    }

    assert {item.id: item.max_uses for item in hero.resources} == {
        "bardic-inspiration": 5,
        "spell-slot-1": 4,
        "spell-slot-2": 3,
        "spell-slot-3": 3,
        "spell-slot-4": 3,
        "spell-slot-5": 2,
    }
    assert "death-ward" in {item.id for item in hero.defensive_spell_actions}

    flame_strike = next(
        action for action in hero.spell_save_actions if action.id == "flame-strike"
    )
    assert flame_strike.dc == 17
    assert flame_strike.success_damage == "half"
    assert [
        (item.dice_count, item.dice_size, item.damage_type)
        for item in flame_strike.damage_components
    ] == [(4, 6, "fire"), (4, 6, "radiant")]

    assert_character_build_raw_ready(profile, hero)
    assert_pregen_combat_stats(hero, combat)
    assert_character_resources_raw_ready(hero, profile, combat)
