from __future__ import annotations

from app.content.barbarian_berserker_progression_profile import build_rokhan_stonefury_level6_profile
from app.content.barbarian_combat_levels import BARBARIAN_COMBAT_LEVELS
from app.content.barbarian_profile_from_levels import apply_barbarian_level_to_profile_data
from app.content.canonical_progression import advance_profile_data
from app.domain.character_builds import CharacterBuildProfile, FeatureAudit


def build_rokhan_stonefury_level7_profile() -> CharacterBuildProfile:
    data = advance_profile_data(build_rokhan_stonefury_level6_profile(), 7)
    apply_barbarian_level_to_profile_data(data, 7)
    source = BARBARIAN_COMBAT_LEVELS[7].source
    audits = [
        FeatureAudit(feature_id="feral-instinct", feature_name="Feral Instinct", source_reference=source,
                     category="class", combat_relevant=True, automated=True,
                     notes="Initiative Advantage is resolved by the universal initiative primitive."),
        FeatureAudit(feature_id="instinctive-pounce", feature_name="Instinctive Pounce", source_reference=source,
                     category="class", combat_relevant=False, automated=True,
                     notes="Fixed Iron Pit formation collapses ordinary closing movement, so this movement-only option changes no combat math."),
    ]
    data.update(feature_audits=[*data["feature_audits"], *(item.model_dump() for item in audits)],
                source_references=[*data["source_references"], source])
    return CharacterBuildProfile.model_validate(data)


def build_rokhan_stonefury_level8_profile() -> CharacterBuildProfile:
    data = advance_profile_data(build_rokhan_stonefury_level7_profile(), 8)
    apply_barbarian_level_to_profile_data(data, 8)
    source = BARBARIAN_COMBAT_LEVELS[8].source
    audit = FeatureAudit(feature_id="ability-score-improvement-l8", feature_name="Ability Score Improvement",
                         source_reference=source, category="feat", combat_relevant=True, automated=True,
                         notes="The authoritative Barbarian combat spine raises Strength to 20 and updates all Strength-derived math.")
    data.update(feature_audits=[*data["feature_audits"], audit.model_dump()],
                source_references=[*data["source_references"], source])
    return CharacterBuildProfile.model_validate(data)
