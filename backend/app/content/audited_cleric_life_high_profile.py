from __future__ import annotations

from app.content.audited_cleric_life_profile import build_seraphine_dawnshield_level6_profile
from app.content.canonical_progression import advance_profile_data
from app.content.cleric_profile_from_levels import apply_cleric_level_to_profile_data
from app.domain.character_builds import CharacterBuildProfile, FeatureAudit


def _class_feature(
    feature_id: str,
    name: str,
    *,
    combat: bool = True,
    notes: str | None = None,
) -> FeatureAudit:
    return FeatureAudit(
        feature_id=feature_id,
        feature_name=name,
        source_reference="D&D Beyond Basic Rules 2024: Cleric — Life Domain",
        category="class",
        combat_relevant=combat,
        automated=combat,
        notes=notes,
    )


def build_seraphine_dawnshield_level7_profile() -> CharacterBuildProfile:
    base = build_seraphine_dawnshield_level6_profile()
    data = advance_profile_data(base, 7)
    apply_cleric_level_to_profile_data(data, 7)
    additions = [
        _class_feature(
            "blessed-strikes",
            "Blessed Strikes — Potent Spellcasting",
            notes=(
                "Canonical caster choice: add Wisdom modifier to damaging Cleric "
                "cantrips; Sacred Flame is 2d8 + Wisdom at level 7."
            ),
        ),
        _class_feature(
            "cleric-combat-spells-4",
            "Level 4 Cleric Spells",
            combat=False,
            notes=(
                "Iron Pit simplicity policy: mandatory Aura of Life and Death Ward "
                "remain prepared; complex persistent level-4 effects are not preferred arena actions."
            ),
        ),
        _class_feature(
            "prayer-of-healing",
            "Prayer of Healing",
            combat=False,
            notes=(
                "Prepared healing spell retained for RAW progression; its 10-minute "
                "casting time keeps it outside arena turns."
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
                "D&D Beyond Basic Rules 2024: Cleric level 7 — Blessed Strikes, "
                "11 prepared spells, 4/3/3/1 spell slots"
            ),
            "D&D Beyond Basic Rules 2024: Life Domain Spells — Aura of Life, Death Ward",
            "D&D Beyond Basic Rules 2024: Spells — Prayer of Healing",
        ],
    )
    return CharacterBuildProfile.model_validate(data)


def build_seraphine_dawnshield_level8_profile() -> CharacterBuildProfile:
    base = build_seraphine_dawnshield_level7_profile()
    data = advance_profile_data(base, 8)
    apply_cleric_level_to_profile_data(data, 8)
    additions = [
        FeatureAudit(
            feature_id="ability-score-improvement-l8",
            feature_name="Ability Score Improvement",
            source_reference=(
                "D&D Beyond Basic Rules 2024: Cleric Level 8; "
                "Feats — Ability Score Improvement"
            ),
            category="feat",
            combat_relevant=True,
            automated=True,
            notes=(
                "+1 Wisdom and +1 Charisma: WIS 19→20, CHA 14→15; spell save DC "
                "and Wisdom-based damage/healing increase by 1."
            ),
        ),
        _class_feature(
            "guardian-of-faith",
            "Guardian of Faith",
            combat=False,
            notes=(
                "Prepared as the damage-side level-8 addition, but persistent positional "
                "guardian bookkeeping is intentionally outside the simple arena action set."
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
                "D&D Beyond Basic Rules 2024: Cleric level 8 — Ability Score Improvement, "
                "12 prepared spells, 4/3/3/2 spell slots"
            ),
            "D&D Beyond Basic Rules 2024: Spells — Guardian of Faith",
        ],
    )
    return CharacterBuildProfile.model_validate(data)


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
