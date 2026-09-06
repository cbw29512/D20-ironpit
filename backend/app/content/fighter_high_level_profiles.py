from __future__ import annotations

from app.content.canonical_progression import advance_profile_data
from app.content.fighter_asi_progression_profile import build_karnok_stoneward_level12_profile
from app.content.fighter_combat_levels import FIGHTER_COMBAT_LEVELS
from app.content.fighter_profile_from_levels import apply_fighter_level_to_profile_data
from app.domain.character_builds import CharacterBuildProfile, FeatureAudit


def _audit(level: int) -> list[FeatureAudit]:
    source = FIGHTER_COMBAT_LEVELS[level].source
    specs = {
        13: [("studied-attacks", "Studied Attacks", "class")],
        14: [("ability-score-improvement-l14", "Ability Score Improvement", "feat")],
        15: [("superior-critical", "Superior Critical", "subclass")],
        16: [("ability-score-improvement-l16", "Ability Score Improvement", "feat")],
        17: [("action-surge-indomitable-l17", "Action Surge and Indomitable Uses", "class")],
    }
    return [FeatureAudit(
        feature_id=feature_id,
        feature_name=name,
        source_reference=source,
        category=category,
        combat_relevant=True,
        automated=True,
        notes=f"Canonical Fighter level {level} progression is compiled from the authoritative 1-20 combat spine.",
    ) for feature_id, name, category in specs[level]]


def _build(level: int) -> CharacterBuildProfile:
    if not 13 <= level <= 17:
        raise ValueError("High-level Fighter profile supports levels 13 through 17.")
    previous = build_karnok_stoneward_level12_profile() if level == 13 else _build(level - 1)
    data = advance_profile_data(previous, level)
    apply_fighter_level_to_profile_data(data, level)
    audits = _audit(level)
    data.update(
        feature_audits=[*data["feature_audits"], *(item.model_dump() for item in audits)],
        source_references=[*data["source_references"], FIGHTER_COMBAT_LEVELS[level].source],
    )
    return CharacterBuildProfile.model_validate(data)


def build_karnok_stoneward_level13_profile() -> CharacterBuildProfile: return _build(13)
def build_karnok_stoneward_level14_profile() -> CharacterBuildProfile: return _build(14)
def build_karnok_stoneward_level15_profile() -> CharacterBuildProfile: return _build(15)
def build_karnok_stoneward_level16_profile() -> CharacterBuildProfile: return _build(16)
def build_karnok_stoneward_level17_profile() -> CharacterBuildProfile: return _build(17)
