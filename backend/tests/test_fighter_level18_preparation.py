from __future__ import annotations

import pytest

from app.content.certified_hero_progressions import CERTIFIED_HERO_PROGRESSIONS
from app.content.fighter_high_level_profiles import build_karnok_stoneward_level18_profile
from app.content.fighter_progression import build_karnok_stoneward_level


def test_fighter_level18_profile_is_prepared_but_not_automated() -> None:
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
    assert all(not audit.automated for audit in survivor.values())


def test_fighter_level18_remains_fail_closed_until_survivor_is_implemented() -> None:
    with pytest.raises(ValueError, match="survivor"):
        build_karnok_stoneward_level(18)

    fighter = next(item for item in CERTIFIED_HERO_PROGRESSIONS if item.class_id == "fighter")
    assert list(fighter.levels)[-1] == 17
