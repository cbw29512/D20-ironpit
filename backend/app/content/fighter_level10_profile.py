from __future__ import annotations

from app.content.canonical_progression import advance_profile_data
from app.content.fighter_level9_profile import build_karnok_stoneward_level9_profile
from app.content.fighter_profile_from_levels import apply_fighter_level_to_profile_data
from app.domain.character_builds import CharacterBuildProfile, FeatureAudit


def build_karnok_stoneward_level10_profile() -> CharacterBuildProfile:
    previous = build_karnok_stoneward_level9_profile()
    data = advance_profile_data(previous, 10)
    apply_fighter_level_to_profile_data(data, 10)
    source = "D&D Beyond Basic Rules 2024: Fighter 10 Champion Heroic Warrior"
    heroic_warrior = FeatureAudit(
        feature_id="heroic-warrior",
        feature_name="Heroic Warrior",
        source_reference=source,
        category="subclass",
        combat_relevant=True,
        automated=True,
        notes=("At the start of each combat turn, the arena grants Heroic Inspiration if Karnok lacks it. "
               "The deterministic combat policy spends it on the first missed attack where one legal die reroll can recover the attack."),
    )
    data.update(
        feature_audits=[*data["feature_audits"], heroic_warrior.model_dump()],
        source_references=[*data["source_references"], source],
    )
    return CharacterBuildProfile.model_validate(data)
