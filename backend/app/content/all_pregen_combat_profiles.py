from __future__ import annotations

from app.content.barbarian_berserker_2014_combat_profile import build_rokhan_2014_combat_profiles
from app.content.fighter_champion_2014_combat_profile import build_karnok_2014_combat_profiles
from app.content.monk_open_hand_2014_combat_profile import build_kael_2014_combat_profiles
from app.content.paladin_devotion_2014_combat_profile import build_aurelia_2014_combat_profiles
from app.content.pregen_combat_profiles import PregenCombatProfile, build_pregen_combat_profiles
from app.content.rogue_thief_2014_combat_profile import build_mara_2014_combat_profiles


def build_all_pregen_combat_profiles() -> dict[str, PregenCombatProfile]:
    """Return validated combat fingerprints across every supported ruleset."""
    profiles = build_pregen_combat_profiles()
    edition_profiles = [
        *build_karnok_2014_combat_profiles(),
        *build_rokhan_2014_combat_profiles(),
        *build_mara_2014_combat_profiles(),
        *build_kael_2014_combat_profiles(),
        *build_aurelia_2014_combat_profiles(),
    ]
    for profile in edition_profiles:
        if profile.template_id in profiles:
            raise ValueError(f"Duplicate pregen combat profile: {profile.template_id}.")
        profiles[profile.template_id] = profile
    return profiles
