from __future__ import annotations

from app.content.bard_2014_spell_package import build_bard_2014_spell_package
from app.content.bard_lore_2014_combat_profile import build_lyra_2014_combat_profile
from app.content.bard_lore_2014_profile import build_lyra_silverstring_2014_profile
from app.content.bard_lore_2014_runtime import build_lyra_silverstring_2014
from app.content.build_audit import assert_character_build_raw_ready
from app.content.character_resource_audit import assert_character_resources_raw_ready
from app.content.pregen_combat_audit import assert_pregen_combat_stats


def test_level_nine_learns_mass_cure_wounds_as_a_bard_spell() -> None:
    package = build_bard_2014_spell_package(9)
    known = {spell.id: spell for spell in package.spells}

    assert "mass-cure-wounds" in known
    assert known["mass-cure-wounds"].spell_level == 5
    assert "magical-secrets" not in known["mass-cure-wounds"].required_capabilities
    assert "greater-restoration" not in known


def test_level_nine_mass_cure_wounds_uses_bard_modifier_without_life_bonus() -> None:
    profile = build_lyra_silverstring_2014_profile(9)
    hero = build_lyra_silverstring_2014(9)
    combat = build_lyra_2014_combat_profile(9)

    mass = next(item for item in hero.healing_actions if item.id == "mass-cure-wounds")
    assert (mass.max_targets, mass.dice_count, mass.dice_size) == (6, 3, 8)
    assert mass.healing_bonus == 5
    assert mass.resource_id == "spell-slot-5"
    assert mass.excluded_creature_types == ["undead", "construct"]

    assert {item.id: item.max_uses for item in hero.resources} == {
        "bardic-inspiration": 5,
        "spell-slot-1": 4,
        "spell-slot-2": 3,
        "spell-slot-3": 3,
        "spell-slot-4": 3,
        "spell-slot-5": 1,
    }
    assert_character_build_raw_ready(profile, hero)
    assert_pregen_combat_stats(hero, combat)
    assert_character_resources_raw_ready(hero, profile, combat)
