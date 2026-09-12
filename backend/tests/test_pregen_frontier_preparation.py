from __future__ import annotations

import pytest

from app.content.audited_cleric import build_seraphine_dawnshield_level
from app.content.audited_cleric_life_profile import build_seraphine_dawnshield_level5_profile
from app.content.barbarian_high_level_profiles import build_rokhan_stonefury_level9_profile
from app.content.barbarian_progression import build_rokhan_stonefury_level
from app.content.rogue_progression_profile import build_mara_quickstep_level3_profile


def _audit(profile, feature_id: str):
    return next(audit for audit in profile.feature_audits if audit.feature_id == feature_id)


def test_rogue_level3_profile_is_ready_behind_steady_aim_blocker() -> None:
    profile = build_mara_quickstep_level3_profile()
    audit = _audit(profile, "steady-aim")

    assert profile.template_id == "mara-quickstep-l3"
    assert profile.level == 3
    assert audit.combat_relevant is True
    assert audit.automated is False


def test_barbarian_level9_profile_is_ready_behind_brutal_strike_blocker() -> None:
    profile = build_rokhan_stonefury_level9_profile()
    audit = _audit(profile, "brutal-strike")

    assert profile.template_id == "rokhan-stonefury-l9"
    assert profile.level == 9
    assert audit.combat_relevant is True
    assert audit.automated is False
    with pytest.raises(ValueError, match="brutal-strike"):
        build_rokhan_stonefury_level(9)


def test_cleric_level5_profile_tracks_both_real_blockers() -> None:
    profile = build_seraphine_dawnshield_level5_profile()
    sear_undead = _audit(profile, "sear-undead")
    spells = _audit(profile, "cleric-combat-spells-3")

    assert profile.template_id == "seraphine-dawnshield-l5"
    assert profile.level == 5
    assert sear_undead.automated is False
    assert spells.automated is False
    with pytest.raises(ValueError, match="sear-undead|cleric-combat-spells-3"):
        build_seraphine_dawnshield_level(5)
