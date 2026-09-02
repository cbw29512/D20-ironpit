from __future__ import annotations

from dataclasses import dataclass

from app.domain.character_builds import FeatureAudit


@dataclass(frozen=True)
class ProfileFeature:
    level: int
    feature_id: str
    name: str
    category: str
    automated: bool


_FEATURES = (
    ProfileFeature(1, "second-wind", "Second Wind", "class", True),
    ProfileFeature(1, "weapon-mastery", "Weapon Mastery", "class", True),
    ProfileFeature(1, "savage-attacker", "Savage Attacker", "feat", True),
    ProfileFeature(1, "adrenaline-rush", "Adrenaline Rush", "species", True),
    ProfileFeature(1, "relentless-endurance", "Relentless Endurance", "species", True),
    ProfileFeature(2, "action-surge", "Action Surge", "class", True),
    ProfileFeature(2, "tactical-mind", "Tactical Mind", "class", True),
    ProfileFeature(3, "improved-critical", "Improved Critical", "subclass", True),
    ProfileFeature(3, "remarkable-athlete", "Remarkable Athlete", "subclass", True),
    ProfileFeature(5, "extra-attack", "Extra Attack", "class", True),
    ProfileFeature(5, "tactical-shift", "Tactical Shift", "class", True),
    ProfileFeature(9, "indomitable", "Indomitable", "class", True),
    ProfileFeature(9, "tactical-master", "Tactical Master", "class", True),
    ProfileFeature(10, "heroic-warrior", "Heroic Warrior", "subclass", True),
    ProfileFeature(11, "two-extra-attacks", "Two Extra Attacks", "class", True),
    ProfileFeature(13, "studied-attacks", "Studied Attacks", "class", True),
    ProfileFeature(15, "superior-critical", "Superior Critical", "subclass", False),
    ProfileFeature(17, "action-surge-two-uses", "Action Surge — Two Uses", "class", True),
    ProfileFeature(18, "survivor", "Survivor", "subclass", False),
    ProfileFeature(20, "three-extra-attacks", "Three Extra Attacks", "class", True),
)


def _audit(feature: ProfileFeature) -> FeatureAudit:
    return FeatureAudit(
        feature_id=feature.feature_id,
        feature_name=feature.name,
        source_reference="D&D Beyond Basic Rules 2024: Fighter / Champion",
        category=feature.category,
        combat_relevant=True,
        automated=feature.automated,
    )


def shared_fighter_champion_feature_audits(level: int) -> list[FeatureAudit]:
    if not 1 <= level <= 20:
        raise ValueError("Fighter profile level must be between 1 and 20.")
    return [_audit(feature) for feature in _FEATURES if feature.level <= level]


def fighting_style_audit(style: str, *, additional: bool = False) -> FeatureAudit:
    supported = style in {"Archery", "Defense", "Great Weapon Fighting", "Two-Weapon Fighting"}
    label = "Additional Fighting Style" if additional else "Fighting Style"
    return FeatureAudit(
        feature_id=f"{'additional-' if additional else ''}fighting-style-{style.lower().replace(' ', '-')}",
        feature_name=f"{label} — {style}",
        source_reference="D&D Beyond Basic Rules 2024: Fighter / Champion; Fighting Style Feats",
        category="subclass" if additional else "class",
        combat_relevant=True,
        automated=supported,
        notes=None if supported else "Character choice is authoritative; runtime support remains fail-closed.",
    )


def equipment_audit(build_id: str, weapon_id: str) -> FeatureAudit:
    return FeatureAudit(
        feature_id=f"equipment-{build_id}",
        feature_name=f"{build_id.replace('-', ' ').title()} Loadout",
        source_reference="D&D Beyond Basic Rules 2024: Fighter Starting Equipment; Equipment",
        category="equipment",
        combat_relevant=True,
        automated=True,
        runtime_attack_weapon_id=weapon_id,
    )


def advancement_audit(level: int, description: str) -> FeatureAudit:
    name = "Boon of Combat Prowess" if level == 19 else "Ability Score Improvement"
    return FeatureAudit(
        feature_id=f"{'boon-combat-prowess' if level == 19 else f'ability-score-improvement-l{level}'}",
        feature_name=name,
        source_reference="D&D Beyond Basic Rules 2024: Fighter; Feats",
        category="feat",
        combat_relevant=True,
        automated=level != 19,
        notes=description,
    )
