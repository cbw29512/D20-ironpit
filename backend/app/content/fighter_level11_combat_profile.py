from __future__ import annotations

from app.content.pregen_combat_profiles import PregenCombatProfile, _karnok_profile


def build_karnok_stoneward_level11_combat_profile() -> PregenCombatProfile:
    return _karnok_profile(11)
