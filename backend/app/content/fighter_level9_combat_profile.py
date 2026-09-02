from __future__ import annotations

from app.content.pregen_combat_profiles import PregenCombatProfile, _karnok_profile


def build_karnok_stoneward_level9_combat_profile() -> PregenCombatProfile:
    """Private certification candidate; not part of the public arena profile collection."""
    return _karnok_profile(9, 94)
