from __future__ import annotations

from app.content.audited_bard import build_lyra_silverstring_level
from app.content.audited_bard_profile import build_lyra_silverstring_profile
from app.content.canonical_spell_policy import canonical_spell_package


def test_2024_bard_level5_font_and_d8_are_wired() -> None:
    profile = build_lyra_silverstring_profile(5)
    hero = build_lyra_silverstring_level(5)

    assert profile.level == 5
    assert hero.max_hp == 28
    assert hero.d20_bonus_die_actions[0].dice_size == 8
    assert hero.reaction_roll_penalty_actions[0].dice_size == 8
    assert hero.skill_bonuses["acrobatics"] == 6
    assert {item.id: item.max_uses for item in hero.resources} == {
        "bardic-inspiration": 4,
        "adrenaline-rush": 3,
        "relentless-endurance": 1,
        "spell-slot-1": 4,
        "spell-slot-2": 3,
        "spell-slot-3": 2,
    }


def test_2024_font_of_inspiration_uses_universal_no_action_conversions() -> None:
    hero = build_lyra_silverstring_level(5)
    actions = hero.resource_conversion_actions

    assert [item.source_resource_id for item in actions] == [
        "spell-slot-1", "spell-slot-2", "spell-slot-3",
    ]
    assert all(item.action_cost == "none" for item in actions)
    assert all(item.target_resource_id == "bardic-inspiration" for item in actions)
    assert all(item.target_gain == 1 for item in actions)
    assert all(item.target_allows_overflow is False for item in actions)


def test_2024_bard_level5_adds_mass_healing_word() -> None:
    hero = build_lyra_silverstring_level(5)
    spell = next(item for item in hero.healing_actions if item.id == "mass-healing-word")

    assert (
        spell.action_cost,
        spell.range_ft,
        spell.max_targets,
        spell.dice_count,
        spell.dice_size,
        spell.resource_id,
    ) == ("bonus_action", 60, 6, 2, 4, "spell-slot-3")
    assert spell.healing_bonus == 4


def test_2024_bard_level5_spell_package_is_complete_and_edition_scoped() -> None:
    package = canonical_spell_package("bard", 5, "2024", 3)

    assert package is not None
    assert len(package.cantrips) == 3
    assert len(package.spells) == 9
    assert [item.id for item in package.spells][-2:] == ["mass-healing-word", "sending"]
