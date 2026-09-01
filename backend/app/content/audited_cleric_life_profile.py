from __future__ import annotations

from app.content.audited_cleric_profile import build_seraphine_dawnshield_level2_profile
from app.content.canonical_hero_policy import canonical_template_id
from app.domain.character_builds import CharacterBuildProfile, FeatureAudit


def _class_feature(feature_id: str, name: str, *, combat: bool = True, notes: str | None = None) -> FeatureAudit:
    return FeatureAudit(
        feature_id=feature_id,
        feature_name=name,
        source_reference="D&D Beyond Basic Rules 2024: Cleric — Life Domain",
        category="class",
        combat_relevant=combat,
        automated=combat,
        notes=notes,
    )


def build_seraphine_dawnshield_level3_profile() -> CharacterBuildProfile:
    base = build_seraphine_dawnshield_level2_profile()
    additions = [
        _class_feature(
            "life-domain", "Life Domain", combat=False,
            notes="Subclass identity unlocks at Cleric level 3; combat effects are audited separately.",
        ),
        _class_feature("disciple-of-life", "Disciple of Life"),
        _class_feature("aid", "Aid"),
        _class_feature("lesser-restoration", "Lesser Restoration"),
        _class_feature("preserve-life", "Preserve Life"),
    ]
    return base.model_copy(update={
        "id": "build-seraphine-dawnshield-l3",
        "template_id": canonical_template_id("cleric", 3),
        "level": 3,
        "feature_audits": [*base.feature_audits, *additions],
        "source_references": [
            *base.source_references,
            "Basic Rules 2024: Cleric level 3 — Life Domain, Disciple of Life, Preserve Life",
            "Basic Rules 2024: Life Domain Spells — Aid, Bless, Cure Wounds, Lesser Restoration",
            "Basic Rules 2024: Spells — Aid, Lesser Restoration",
        ],
    })
