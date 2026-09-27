from app.content.warlock_2014_progression import warlock_2014_level
from app.content.warlock_fiend_2014_profile import build_varek_ashenmark_2014_profile
from app.content.warlock_fiend_2014_runtime import build_varek_ashenmark_2014


def test_2014_warlock_progression_uses_edition_correct_pact_magic() -> None:
    assert warlock_2014_level(1).pact_slots == 1
    assert warlock_2014_level(1).pact_slot_level == 1
    assert warlock_2014_level(1).invocations_known == 0
    assert warlock_2014_level(2).invocations_known == 2
    assert warlock_2014_level(3).pact_slot_level == 2
    assert warlock_2014_level(11).pact_slots == 3
    assert warlock_2014_level(17).pact_slots == 4
    assert warlock_2014_level(20).pact_slot_level == 5
    assert warlock_2014_level(17).mystic_arcanum_levels == (6, 7, 8, 9)


def test_varek_level_one_is_a_fiend_blaster_not_2024_warlock_data() -> None:
    profile = build_varek_ashenmark_2014_profile(1)
    varek = build_varek_ashenmark_2014(1)

    assert profile.ruleset == "2014"
    assert profile.subclass_id == "fiend-patron"
    assert profile.build_id == "eldritch-blaster"
    assert varek.ruleset == "2014"
    assert varek.level == 1
    assert varek.armor_class == 13
    assert varek.max_hp == 10

    resources = {item.id: item.max_uses for item in varek.resources}
    assert resources == {"spell-slot-1": 1}

    blast = varek.spell_attack_actions[0]
    assert blast.id == "eldritch-blast"
    assert blast.range_ft == 120
    assert blast.damage_dice_count == 1
    assert blast.damage_dice_size == 10
    assert blast.damage_type == "force"
    assert blast.damage_bonus == 0

    blessing = varek.progression_features.source_reduces_hostile_to_zero_hp_temporary_hp
    assert blessing is not None
    assert blessing.source_id == "dark-ones-blessing"
    assert blessing.ability == "charisma"
    assert blessing.per_level == 1


def test_varek_level_one_keeps_hex_visible_as_the_next_shared_damage_primitive() -> None:
    profile = build_varek_ashenmark_2014_profile(1)
    audits = {item.feature_id: item for item in profile.feature_audits}

    assert audits["hex"].combat_relevant is True
    assert audits["hex"].automated is False
    assert "Hunter's Mark" in audits["hex"].notes
