from __future__ import annotations

from app.content.barbarian_progression_profile import build_rokhan_stonefury_level5_profile
from app.content.canonical_progression import advance_profile_data
from app.domain.character_builds import CharacterBuildProfile, FeatureAudit


def build_rokhan_stonefury_level6_profile() -> CharacterBuildProfile:
    previous = build_rokhan_stonefury_level5_profile()
    data = advance_profile_data(previous, 6)
    feature = FeatureAudit(
        feature_id="mindless-rage",
        feature_name="Mindless Rage",
        source_reference="D&D Beyond Basic Rules 2024: Path of the Berserker Level 6",
        category="subclass",
        combat_relevant=True,
        automated=True,
        notes=("While Rage is active, Rokhan is immune to Charmed and Frightened. Entering Rage ends either "
               "condition already affecting him; ending Rage removes only the immunity, not previously ended conditions."),
    )
    data.update(
        feature_audits=[*data["feature_audits"], feature.model_dump()],
        source_references=[*data["source_references"], "Basic Rules 2024: Path of the Berserker — Level 6 Mindless Rage"],
    )
    return CharacterBuildProfile.model_validate(data)
