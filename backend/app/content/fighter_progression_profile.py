from __future__ import annotations

from app.content.audited_fighter_profile import build_karnok_stoneward_profile
from app.domain.character_builds import CharacterBuildProfile, FeatureAudit


def _level_two_features() -> list[FeatureAudit]:
    source = "D&D Beyond Basic Rules 2024: Fighter Level 2"
    return [
        FeatureAudit(
            feature_id="action-surge", feature_name="Action Surge", source_reference=source,
            category="class", combat_relevant=True, automated=True,
            notes="Iron Pit spends Action Surge only when the additional non-Magic Action can immediately make a legal Attack.",
        ),
        FeatureAudit(
            feature_id="tactical-mind", feature_name="Tactical Mind", source_reference=source,
            category="class", combat_relevant=True, automated=True,
            notes="Applied after failed automated ability checks; the current combat engine exposes grapple escape checks.",
        ),
    ]


def _level_three_features() -> list[FeatureAudit]:
    source = "D&D Beyond Basic Rules 2024: Champion Level 3"
    return [
        FeatureAudit(
            feature_id="improved-critical", feature_name="Improved Critical", source_reference=source,
            category="class", combat_relevant=True, automated=True,
            notes="Weapon and Unarmed Strike attacks score a Critical Hit on 19-20; only natural 20 is an automatic hit.",
        ),
        FeatureAudit(
            feature_id="remarkable-athlete", feature_name="Remarkable Athlete", source_reference=source,
            category="class", combat_relevant=True, automated=True,
            notes=("Advantage on Initiative and Strength (Athletics); after a Critical Hit, Iron Pit may use the granted "
                   "half-Speed movement only to close, never retreat, and it provokes no Opportunity Attacks."),
        ),
    ]


def build_karnok_stoneward_level2_profile() -> CharacterBuildProfile:
    data = build_karnok_stoneward_profile().model_dump()
    data.update(
        id="build-karnok-stoneward-l2", template_id="karnok-stoneward-l2", level=2,
        feature_audits=[*data["feature_audits"], *(item.model_dump() for item in _level_two_features())],
        source_references=[*data["source_references"], "Basic Rules 2024: Fighter — Level 2 Action Surge and Tactical Mind"],
    )
    return CharacterBuildProfile.model_validate(data)


def build_karnok_stoneward_level3_profile() -> CharacterBuildProfile:
    data = build_karnok_stoneward_level2_profile().model_dump()
    data.update(
        id="build-karnok-stoneward-l3", template_id="karnok-stoneward-l3", level=3,
        feature_audits=[*data["feature_audits"], *(item.model_dump() for item in _level_three_features())],
        source_references=[*data["source_references"], "Basic Rules 2024: Champion — Level 3 Improved Critical and Remarkable Athlete"],
    )
    return CharacterBuildProfile.model_validate(data)
