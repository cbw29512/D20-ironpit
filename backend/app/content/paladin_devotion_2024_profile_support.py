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
