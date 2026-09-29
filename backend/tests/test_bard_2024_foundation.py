from __future__ import annotations

from app.content.audited_bard import build_lyra_silverstring_level
from app.content.audited_bard_profile import build_lyra_silverstring_profile
from app.content.canonical_spell_policy import canonical_spell_package


def test_2024_bard_level_one_is_legal_support_foundation() -> None:
    profile = build_lyra_silverstring_profile(1)
    hero = build_lyra_silverstring_level(1)

    assert profile.ruleset == "2024"
    assert profile.class_id == "bard"
    assert profile.background_id == "acolyte"
    assert profile.origin_feat_id == "magic-initiate-cleric"
    assert hero.id == "lyra-silverstring-l1"
    assert hero.armor_class == 12
    assert hero.max_hp == 8
    assert hero.weapon_attack is not None
    assert hero.weapon_attack.weapon.id == "dagger"
    assert hero.weapon_attack.weapon.mastery_property is None
    assert {item.id: item.max_uses for item in hero.resources}["bardic-inspiration"] == 3
    assert {item.id: item.max_uses for item in hero.resources}["spell-slot-1"] == 2
    assert [item.id for item in hero.healing_actions] == ["healing-word", "cure-wounds"]


def test_2024_bardic_inspiration_uses_failed_test_universal_grant() -> None:
    hero = build_lyra_silverstring_level(1)
    action = hero.d20_bonus_die_actions[0]

    assert action.id == "bardic-inspiration"
    assert action.action_cost == "bonus_action"
    assert action.range_ft == 60
    assert action.target_mode == "other_ally"
    assert (action.dice_count, action.dice_size) == (1, 6)
    assert set(action.test_kinds) == {"attack", "saving_throw", "ability_check"}
    assert action.duration_rounds == 600
    assert action.exclusive_group == "bardic-inspiration"


def test_2024_bard_level_two_adds_expertise_without_legacy_initiative_bonus() -> None:
    profile = build_lyra_silverstring_profile(2)
    hero = build_lyra_silverstring_level(2)

    assert hero.initiative_bonus == 0
    assert hero.skill_bonuses["acrobatics"] == 4
    assert any(item.feature_id == "expertise" and item.automated for item in profile.feature_audits)
    jack = next(item for item in profile.feature_audits if item.feature_id == "jack-of-all-trades")
    assert jack.combat_relevant is False


def test_2024_bard_foundation_uses_edition_specific_spell_package() -> None:
    level_one = canonical_spell_package("bard", 1, "2024", 3)
    level_two = canonical_spell_package("bard", 2, "2024", 3)

    assert level_one is not None
    assert level_two is not None
    assert [item.id for item in level_one.cantrips] == ["dancing-lights", "mage-hand"]
    assert [item.id for item in level_one.spells] == [
        "healing-word",
        "cure-wounds",
        "detect-magic",
        "comprehend-languages",
    ]
    assert [item.id for item in level_two.spells] == [
        "healing-word",
        "cure-wounds",
        "detect-magic",
        "comprehend-languages",
        "identify",
    ]



def test_2024_lore_bard_level_three_reuses_universal_cutting_words_and_adds_shatter() -> None:
    profile = build_lyra_silverstring_profile(3)
    hero = build_lyra_silverstring_level(3)

    assert profile.subclass_id == "college-lore"
    assert profile.subclass_name == "College of Lore"
    assert hero.max_hp == 18
    assert {item.id: item.max_uses for item in hero.resources}["spell-slot-1"] == 4
    assert {item.id: item.max_uses for item in hero.resources}["spell-slot-2"] == 2

    cutting_words = hero.reaction_roll_penalty_actions[0]
    assert cutting_words.id == "cutting-words"
    assert cutting_words.range_ft == 60
    assert cutting_words.resource_id == "bardic-inspiration"
    assert cutting_words.roll_kinds == ["attack", "ability_check", "damage"]
    assert cutting_words.requires_source_sight is True
    assert cutting_words.requires_target_hearing is False
    assert cutting_words.blocked_target_condition_immunity is None

    shatter = hero.spell_save_actions[0]
    assert shatter.id == "shatter"
    assert shatter.level == 2
    assert shatter.range_ft == 60
    assert shatter.area is not None
    assert (shatter.area.shape, shatter.area.origin, shatter.area.radius_ft) == ("radius", "point", 10)
    assert shatter.save_ability == "constitution"
    assert (shatter.damage_dice_count, shatter.damage_dice_size) == (3, 8)
    assert shatter.damage_type == "thunder"
    assert shatter.success_damage == "half"
    assert shatter.upcast_dice_per_level == 1


def test_2024_bard_level_three_spell_package_adds_shatter() -> None:
    level_three = canonical_spell_package("bard", 3, "2024", 3)

    assert level_three is not None
    assert [item.id for item in level_three.spells] == [
        "healing-word",
        "cure-wounds",
        "detect-magic",
        "comprehend-languages",
        "identify",
        "shatter",
    ]
    shatter = level_three.spells[-1]
    assert (shatter.spell_level, shatter.min_character_level) == (2, 3)



def test_2024_lore_bard_level_four_applies_persistent_charisma_asi() -> None:
    profile = build_lyra_silverstring_profile(4)
    hero = build_lyra_silverstring_level(4)

    assert profile.final_ability_scores.charisma == 19
    assert [(item.ability, item.amount) for item in profile.advancement_increases] == [("charisma", 2)]
    assert hero.ability_scores.charisma == 19
    assert hero.max_hp == 23
    assert hero.saving_throw_bonuses["charisma"] == 6
    assert hero.skill_bonuses["performance"] == 6
    resources = {item.id: item.max_uses for item in hero.resources}
    assert resources["bardic-inspiration"] == 4
    assert resources["spell-slot-1"] == 4
    assert resources["spell-slot-2"] == 3
    shatter = hero.spell_save_actions[0]
    assert shatter.dc == 14
    assert hero.healing_actions[0].healing_bonus == 4
    assert hero.healing_actions[1].healing_bonus == 4


def test_2024_bard_level_four_spell_package_adds_cantrip_and_utility_spell() -> None:
    level_four = canonical_spell_package("bard", 4, "2024", 4)

    assert level_four is not None
    assert [item.id for item in level_four.cantrips] == [
        "dancing-lights",
        "mage-hand",
        "message",
    ]
    assert [item.id for item in level_four.spells] == [
        "healing-word",
        "cure-wounds",
        "detect-magic",
        "comprehend-languages",
        "identify",
        "shatter",
        "knock",
    ]
    knock = level_four.spells[-1]
    assert (knock.spell_level, knock.min_character_level) == (2, 4)
