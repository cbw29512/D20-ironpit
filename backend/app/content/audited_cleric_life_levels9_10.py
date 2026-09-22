from __future__ import annotations

from app.content.audited_cleric_life_levels7_8 import build_seraphine_dawnshield_level8_profile
from app.content.audited_cleric_life_profile_support import life_class_feature as _class_feature
from app.content.canonical_progression import advance_profile_data
from app.content.cleric_profile_from_levels import apply_cleric_level_to_profile_data
from app.domain.character_builds import CharacterBuildProfile

def build_seraphine_dawnshield_level9_profile() -> CharacterBuildProfile:
    base = build_seraphine_dawnshield_level8_profile()
    data = advance_profile_data(base, 9)
    apply_cleric_level_to_profile_data(data, 9)
    additions = [
        _class_feature(
            "cleric-combat-spells-5",
            "Level 5 Cleric Spells",
            notes=(
                "Iron Pit caster policy prefers simple proven actions: Seraphine uses "
                "Inflict Wounds upcast with a level-5 slot for damage and Mass Cure Wounds "
                "for healing. Complex fifth-level options remain legal prepared spells but "
                "are not preferred arena actions."
            ),
        ),
        _class_feature(
            "mass-cure-wounds",
            "Mass Cure Wounds",
            notes=(
                "Always-prepared Life Domain spell; shared group-healing primitive heals "
                "up to six legal creatures for 5d8 + Wisdom + Disciple of Life."
            ),
        ),
        _class_feature(
            "greater-restoration",
            "Greater Restoration",
            combat=False,
            notes=(
                "Always prepared for RAW Life Domain progression; broad restoration semantics "
                "remain outside the simple arena action set."
            ),
        ),
        _class_feature(
            "inflict-wounds-upcast-l5",
            "Inflict Wounds — 5th-Level Slot",
            notes=(
                "RAW upcast of the existing simple damage spell: 6d10 Necrotic damage, "
                "Constitution save for half. Reuses the existing spell-save pipeline."
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
                "D&D Beyond Basic Rules 2024: Cleric level 9 — 14 prepared spells, "
                "4/3/3/3/1 spell slots"
            ),
            "D&D Beyond Basic Rules 2024: Life Domain Spells — Greater Restoration, Mass Cure Wounds",
            "D&D Beyond Basic Rules 2024: Spells — Inflict Wounds higher-level casting",
        ],
    )
    return CharacterBuildProfile.model_validate(data)


def build_seraphine_dawnshield_level10_profile() -> CharacterBuildProfile:
    base = build_seraphine_dawnshield_level9_profile()
    data = advance_profile_data(base, 10)
    apply_cleric_level_to_profile_data(data, 10)
    additions = [
        _class_feature(
            "divine-intervention",
            "Divine Intervention",
            notes=(
                "Once per Long Rest, Iron Pit exposes two simple RAW choices using the same "
                "generic resource: a free 5th-level Inflict Wounds damage cast or a free "
                "Mass Cure Wounds healing cast. Neither expends a spell slot."
            ),
        ),
        _class_feature(
            "spare-the-dying",
            "Spare the Dying",
            combat=False,
            notes=(
                "Fifth Cleric cantrip at level 10; retained for RAW progression but not "
                "needed in the 1v1 arena action set."
            ),
        ),
        _class_feature(
            "contagion",
            "Contagion",
            combat=False,
            notes=(
                "Legal prepared fifth-level damage spell retained on the sheet; Iron Pit "
                "prefers the simpler 5th-level Inflict Wounds upcast for arena damage."
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
                "D&D Beyond Basic Rules 2024: Cleric level 10 — Divine Intervention, "
                "15 prepared spells, 5 cantrips"
            ),
            "D&D Beyond Basic Rules 2024: Spells — Spare the Dying, Contagion",
        ],
    )
    return CharacterBuildProfile.model_validate(data)
