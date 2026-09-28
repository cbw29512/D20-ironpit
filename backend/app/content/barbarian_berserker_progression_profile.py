from __future__ import annotations

from app.content.barbarian_progression_profile import build_rokhan_stonefury_level5_profile
from app.content.barbarian_profile_from_levels import apply_barbarian_level_to_profile_data
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


def build_rokhan_stonefury_level7_profile() -> CharacterBuildProfile:
    """Audit the two Barbarian 7 combat features now backed by shared engine primitives."""
    previous = build_rokhan_stonefury_level6_profile()
    data = advance_profile_data(previous, 7)
    features = (
        FeatureAudit(
            feature_id="feral-instinct",
            feature_name="Feral Instinct",
            source_reference="D&D Beyond Basic Rules 2024: Barbarian Level 7",
            category="class",
            combat_relevant=True,
            automated=True,
            notes="Advantage on Initiative reuses the universal initiative-advantage capability.",
        ),
        FeatureAudit(
            feature_id="instinctive-pounce",
            feature_name="Instinctive Pounce",
            source_reference="D&D Beyond Basic Rules 2024: Barbarian Level 7",
            category="class",
            combat_relevant=True,
            automated=True,
            notes=("When Rage is activated as a Bonus Action, the activation-movement primitive may move Rokhan "
                   "up to half his Speed as the Rage-owned rider; browser and Python use the same policy."),
        ),
    )
    data.update(
        feature_audits=[*data["feature_audits"], *(feature.model_dump() for feature in features)],
        source_references=[*data["source_references"], "D&D Beyond Basic Rules 2024: Barbarian Level 7 Feral Instinct and Instinctive Pounce"],
    )
    return CharacterBuildProfile.model_validate(data)


def build_rokhan_stonefury_level8_profile() -> CharacterBuildProfile:
    """Advance the certified 2024 Berserker from level 7 to level 8 with the RAW Strength ASI."""
    try:
        previous = build_rokhan_stonefury_level7_profile()
        data = advance_profile_data(previous, 8)
        apply_barbarian_level_to_profile_data(data, 8)
        asi = FeatureAudit(
            feature_id="ability-score-improvement-l8",
            feature_name="Ability Score Improvement",
            source_reference="D&D Beyond Basic Rules 2024: Barbarian Level 8; Feats — Ability Score Improvement",
            category="feat",
            combat_relevant=True,
            automated=True,
            notes=(
                "Canonical damage-first progression raises Strength from 18 to 20. "
                "Existing shared stat math updates attacks, damage, Strength saves, and Athletics; "
                "no new combat primitive is introduced."
            ),
        )
        data.update(
            feature_audits=[*data["feature_audits"], asi.model_dump()],
            source_references=[
                *data["source_references"],
                "D&D Beyond Basic Rules 2024: Barbarian Level 8 Ability Score Improvement (+2 Strength)",
            ],
        )
        return CharacterBuildProfile.model_validate(data)
    except Exception as exc:
        raise RuntimeError("Rokhan Stonefury level 8 profile could not be built.") from exc
