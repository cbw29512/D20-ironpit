from __future__ import annotations

from app.domain.character_builds import FeatureAudit


def paladin_2024_feature(
    feature_id: str,
    name: str,
    category: str,
    *,
    combat: bool,
    automated: bool,
    weapon_id: str | None = None,
    notes: str | None = None,
) -> FeatureAudit:
    return FeatureAudit(
        feature_id=feature_id,
        feature_name=name,
        source_reference="D&D Beyond Basic Rules 2024",
        category=category,
        combat_relevant=combat,
        automated=automated,
        runtime_attack_weapon_id=weapon_id,
        notes=notes,
    )


def paladin_2024_level5_audits() -> list[FeatureAudit]:
    return [
        paladin_2024_feature(
            "extra-attack",
            "Extra Attack",
            "class",
            combat=True,
            automated=True,
            notes="The universal Attack action resolves two legal weapon attacks.",
        ),
        paladin_2024_feature(
            "faithful-steed",
            "Faithful Steed",
            "class",
            combat=False,
            automated=False,
            notes=(
                "Find Steed is always prepared and retains its one free Long-Rest cast resource, "
                "but Iron Pit's no-summons rule keeps the summon arena-unavailable."
            ),
        ),
        paladin_2024_feature(
            "oath-spells-level5",
            "Oath of Devotion Spells",
            "subclass",
            combat=True,
            automated=True,
            notes=(
                "Aid uses the certified 2024 defensive-spell fingerprint; "
                "Zone of Truth is always prepared but arena-neutral."
            ),
        ),
    ]
