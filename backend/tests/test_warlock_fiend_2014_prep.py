from app.content.certified_hero_progressions import CERTIFIED_HERO_PROGRESSIONS
from app.content.warlock_fiend_2014_combat_profile import build_varek_ashenmark_2014_combat_profile
from app.content.warlock_fiend_2014_data import ability_scores
from app.content.warlock_fiend_2014_profile import build_varek_ashenmark_2014_profile
from app.content.warlock_fiend_2014_progression import warlock_fiend_2014_level
from app.content.warlock_fiend_2014_runtime import build_varek_ashenmark_2014


def test_varek_persistent_identity_and_asi_progression_are_stable() -> None:
    first = build_varek_ashenmark_2014_profile(1)
    for level in range(1, 21):
        profile = build_varek_ashenmark_2014_profile(level)
        runtime = build_varek_ashenmark_2014(level)
        fingerprint = build_varek_ashenmark_2014_combat_profile(level)
        assert profile.character_name == first.character_name == "Varek Ashenmark"
        assert profile.species_id == first.species_id == "human"
        assert profile.background_id == first.background_id == "charlatan"
        assert profile.subclass_id == first.subclass_id == "fiend-patron"
        assert profile.template_id == runtime.id == fingerprint.template_id
        assert runtime.level == profile.level == fingerprint.level == level
        assert runtime.armor_class == fingerprint.armor_class
        assert runtime.max_hp == fingerprint.max_hp

    assert ability_scores(1).charisma == 16
    assert ability_scores(4).charisma == 18
    assert ability_scores(8).charisma == 20
    assert ability_scores(12).dexterity == 17
    assert ability_scores(19).dexterity == 20


def test_varek_pact_slots_and_mystic_arcanum_resources_match_2014_progression() -> None:
    expected = {
        1: (1, 1, ()),
        2: (2, 1, ()),
        3: (2, 2, ()),
        9: (2, 5, ()),
        11: (3, 5, (6,)),
        13: (3, 5, (6, 7)),
        15: (3, 5, (6, 7, 8)),
        17: (4, 5, (6, 7, 8, 9)),
        20: (4, 5, (6, 7, 8, 9)),
    }
    for level, (slots, slot_level, arcanum) in expected.items():
        row = warlock_fiend_2014_level(level)
        runtime = build_varek_ashenmark_2014(level)
        fingerprint = build_varek_ashenmark_2014_combat_profile(level)
        resources = {item.id: item.max_uses for item in runtime.resources}
        assert row.pact_slots == slots
        assert row.pact_slot_level == slot_level
        assert row.mystic_arcanum_levels == arcanum
        assert resources == dict(fingerprint.resources)
        assert resources[f"spell-slot-{slot_level}"] == slots
        for spell_level in arcanum:
            assert resources[f"mystic-arcanum-{spell_level}"] == 1


def test_varek_fiend_mechanics_remain_explicitly_blocked_and_uncertified() -> None:
    expected = {
        6: "dark-ones-own-luck",
        10: "fiendish-resilience",
        14: "hurl-through-hell",
        20: "eldritch-master",
    }
    for level, feature_id in expected.items():
        profile = build_varek_ashenmark_2014_profile(level)
        audit = next(item for item in profile.feature_audits if item.feature_id == feature_id)
        assert audit.automated is False

    first = build_varek_ashenmark_2014_profile(1)
    pact = next(item for item in first.feature_audits if item.feature_id == "pact-magic")
    blessing = next(item for item in first.feature_audits if item.feature_id == "dark-ones-blessing")
    assert pact.automated is False
    assert blessing.automated is False

    assert all(
        not (
            item.class_id == "warlock"
            and getattr(item.template_builder, "__name__", "") == "build_varek_ashenmark_2014"
        )
        for item in CERTIFIED_HERO_PROGRESSIONS
    )
