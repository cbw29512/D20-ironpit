from app.content.certified_hero_progressions import CERTIFIED_HERO_PROGRESSIONS
from app.content.fighter_high_level_profiles import build_karnok_stoneward_level18_profile
from app.content.fighter_progression import build_karnok_stoneward_level


def test_fighter_level18_profile_is_fully_automated() -> None:
    profile = build_karnok_stoneward_level18_profile()
    survivor = {
        audit.feature_id: audit
        for audit in profile.feature_audits
        if audit.feature_id.startswith("survivor-")
    }

    assert profile.level == 18
    assert profile.template_id == "karnok-stoneward-l18"
    assert set(survivor) == {"survivor-defy-death", "survivor-heroic-rally"}
    assert all(audit.combat_relevant for audit in survivor.values())
    assert all(audit.automated for audit in survivor.values())


def test_fighter_level18_remains_registered_after_level20_certification() -> None:
    template = build_karnok_stoneward_level(18)
    fighter = next(item for item in CERTIFIED_HERO_PROGRESSIONS if item.class_id == "fighter")
    certified_levels = list(fighter.levels)

    assert template.level == 18
    assert template.max_hp == 202
    assert 18 in certified_levels
    assert certified_levels[-1] == 20
    assert fighter.profile(18).template_id == template.id
