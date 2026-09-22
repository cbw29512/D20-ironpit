from __future__ import annotations

from app.content.audited_cleric_life_levels9_10 import build_seraphine_dawnshield_level10_profile
from app.content.audited_cleric_life_profile_support import life_class_feature as _class_feature
from app.content.canonical_progression import advance_profile_data
from app.content.cleric_profile_from_levels import apply_cleric_level_to_profile_data
from app.domain.character_builds import CharacterBuildProfile, FeatureAudit

def build_seraphine_dawnshield_level11_profile() -> CharacterBuildProfile:
    base = build_seraphine_dawnshield_level10_profile()
    data = advance_profile_data(base, 11)
    apply_cleric_level_to_profile_data(data, 11)
    additions = [
        _class_feature(
            "cleric-combat-spells-6",
            "Level 6 Cleric Spells",
            notes=(
                "Iron Pit simplicity policy uses RAW upcasts instead of adding extra state: "
                "Inflict Wounds at level 6 for damage and Mass Cure Wounds at level 6 for healing."
            ),
        ),
        _class_feature(
            "inflict-wounds-upcast-l6",
            "Inflict Wounds — 6th-Level Slot",
            notes=(
                "RAW upcast through the existing spell-save pipeline: 7d10 Necrotic damage, "
                "Constitution save for half."
            ),
        ),
        _class_feature(
            "mass-cure-wounds-upcast-l6",
            "Mass Cure Wounds — 6th-Level Slot",
            notes=(
                "RAW upcast through the shared group-healing primitive: 6d8 + Wisdom + "
                "Disciple of Life, using one level-6 slot."
            ),
        ),
        _class_feature(
            "heal",
            "Heal",
            combat=False,
            notes=(
                "Legal prepared level-6 Cleric spell retained on the sheet; Iron Pit prefers "
                "the simpler Mass Cure Wounds upcast to avoid adding condition-cleanse coupling."
            ),
        ),
    ]
    data.update(
        feature_audits=[
            *data["feature_audits"],
            *(feature.model_dump() for feature in additions),
        ],
        source_references=[
            *data["source_references"],
            (
                "D&D Beyond Basic Rules 2024: Cleric level 11 — 16 prepared spells, "
                "4/3/3/3/2/1 spell slots"
            ),
            "D&D Beyond Basic Rules 2024: Cleric Spell List — Heal",
            "D&D Beyond Basic Rules 2024: Spells — higher-level Inflict Wounds and Mass Cure Wounds",
        ],
    )
    return CharacterBuildProfile.model_validate(data)


def build_seraphine_dawnshield_level12_profile() -> CharacterBuildProfile:
    base = build_seraphine_dawnshield_level11_profile()
    data = advance_profile_data(base, 12)
    apply_cleric_level_to_profile_data(data, 12)
    addition = FeatureAudit(
        feature_id="ability-score-improvement-l12",
        feature_name="Ability Score Improvement",
        source_reference=(
            "D&D Beyond Basic Rules 2024: Cleric Level 12; "
            "Feats — Ability Score Improvement"
        ),
        category="feat",
        combat_relevant=True,
        automated=True,
        notes=(
            "+2 Charisma: CHA 15→17. Wisdom remains 20, so spell attack/save and "
            "healing output stay unchanged while Charisma saves and Persuasion improve."
        ),
    )
    data.update(
        feature_audits=[*data["feature_audits"], addition.model_dump()],
        source_references=[
            *data["source_references"],
            "D&D Beyond Basic Rules 2024: Cleric level 12 — Ability Score Improvement",
        ],
    )
    return CharacterBuildProfile.model_validate(data)
