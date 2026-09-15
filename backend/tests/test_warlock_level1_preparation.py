import pytest

from app.content.audited_warlock import build_varek_ashenmark_level
from app.content.audited_warlock_profile import build_varek_ashenmark_profile
from app.content.canonical_class_combat_spines import canonical_combat_features
from app.content.canonical_spell_packages import build_class_spell_package
from app.content.certified_hero_progressions import CERTIFIED_HERO_PROGRESSIONS
from app.content.hero_combat_feature_registry import unsupported_hero_engine_features
from app.content.offensive_spell_effects import build_eldritch_blast
from app.content.warlock_combat_fingerprint import build_varek_ashenmark_combat_profile


def test_varek_level1_recovered_data_matches_current_combat_math() -> None:
    fingerprint = build_varek_ashenmark_combat_profile()
    profile = build_varek_ashenmark_profile()
    blast = build_eldritch_blast(5, 1)

    assert fingerprint.template_id == "varek-ashenmark-l1"
    assert fingerprint.abilities.charisma == 17
    assert fingerprint.attacks[0].ability == "charisma"
    assert fingerprint.resources == (
        ("pact-slot-1", 1), ("adrenaline-rush", 2), ("relentless-endurance", 1),
    )
    assert profile.template_id == fingerprint.template_id
    assert blast.attack_bonus == 5
    assert blast.range_ft == 120
    assert (blast.damage_dice_count, blast.damage_dice_size, blast.damage_type) == (1, 10, "force")


def test_current_warlock_package_is_not_the_old_arena_neutral_package() -> None:
    package = build_class_spell_package("warlock", 1)

    assert [spell.id for spell in package.spells] == ["charm-person", "hex"]
    audits = {item.feature_id: item for item in build_varek_ashenmark_profile().feature_audits}
    assert audits["charm-person"].automated is False
    assert audits["hex"].automated is False
    assert audits["pact-magic"].automated is False


def test_warlock_one_remains_fail_closed_until_current_package_is_supported() -> None:
    blockers = unsupported_hero_engine_features(canonical_combat_features("warlock", 1))

    assert blockers == ("eldritch-invocations", "pact-magic")
    assert all(item.class_id != "warlock" for item in CERTIFIED_HERO_PROGRESSIONS)
    with pytest.raises(ValueError, match="eldritch-invocations, pact-magic"):
        build_varek_ashenmark_level(1)
