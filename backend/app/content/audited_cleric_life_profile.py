from __future__ import annotations

from app.content.audited_cleric_profile import build_seraphine_dawnshield_level2_profile
from app.content.canonical_hero_policy import canonical_template_id
from app.content.canonical_progression import advance_profile_data
from app.domain.character_builds import AbilityIncrease, AbilityScores, CharacterBuildProfile, FeatureAudit


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


def build_seraphine_dawnshield_level4_profile() -> CharacterBuildProfile:
    base = build_seraphine_dawnshield_level3_profile()
    data = advance_profile_data(base, 4)
    additions = [
        FeatureAudit(
            feature_id="ability-score-improvement-l4",
            feature_name="Ability Score Improvement",
            source_reference="D&D Beyond Basic Rules 2024: Cleric Level 4; Feats — Ability Score Improvement",
            category="feat",
            combat_relevant=True,
            automated=True,
            notes="+2 Wisdom raises WIS 17→19, spell save DC 13→14, spell attack +5→+6, healing, Wisdom saves, and Medicine.",
        ),
        FeatureAudit(
            feature_id="inflict-wounds",
            feature_name="Inflict Wounds",
            source_reference="D&D Beyond Basic Rules 2024: Spells — Inflict Wounds",
            category="class",
            combat_relevant=True,
            automated=True,
            notes="Touch-range Constitution save; 2d10 Necrotic damage, half on success. No Concentration.",
        ),
        FeatureAudit(
            feature_id="mending",
            feature_name="Mending",
            source_reference="D&D Beyond Basic Rules 2024: Spells — Mending",
            category="class",
            combat_relevant=False,
            automated=False,
            notes="Fourth Cleric cantrip at level 4; arena-irrelevant utility choice.",
        ),
    ]
    data.update(
        advancement_increases=[AbilityIncrease(ability="wisdom", amount=2).model_dump()],
        final_ability_scores=AbilityScores(
            strength=10, dexterity=10, constitution=10, intelligence=14, wisdom=19, charisma=14,
        ).model_dump(),
        feature_audits=[*data["feature_audits"], *(feature.model_dump() for feature in additions)],
        source_references=[
            *data["source_references"],
            "Basic Rules 2024: Cleric level 4 — Ability Score Improvement, 4 cantrips, 7 prepared spells, 4/3 spell slots",
            "Basic Rules 2024: Spells — Mending, Inflict Wounds",
        ],
    )
    return CharacterBuildProfile.model_validate(data)
