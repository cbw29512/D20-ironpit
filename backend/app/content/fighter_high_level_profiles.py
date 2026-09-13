from __future__ import annotations

from collections.abc import Callable

from app.content.canonical_progression import advance_profile_data
from app.content.fighter_asi_progression_profile import build_karnok_stoneward_level12_profile
from app.content.fighter_profile_from_levels import apply_fighter_level_to_profile_data
from app.domain.character_builds import CharacterBuildProfile, FeatureAudit

ProfileBuilder = Callable[[], CharacterBuildProfile]


def _advance(previous: ProfileBuilder, level: int, audits: list[FeatureAudit], refs: list[str]) -> CharacterBuildProfile:
    data = advance_profile_data(previous(), level)
    apply_fighter_level_to_profile_data(data, level)
    data.update(
        feature_audits=[*data["feature_audits"], *(audit.model_dump() for audit in audits)],
        source_references=[*data["source_references"], *refs],
    )
    return CharacterBuildProfile.model_validate(data)


def build_karnok_stoneward_level13_profile() -> CharacterBuildProfile:
    source = "D&D Beyond Basic Rules 2024: Fighter Level 13"
    return _advance(build_karnok_stoneward_level12_profile, 13, [FeatureAudit(
        feature_id="studied-attacks", feature_name="Studied Attacks", source_reference=source,
        category="class", combat_relevant=True, automated=True,
        notes="A missed attack marks that target for Advantage on Karnok's next attack against it until another target is attacked.",
    )], [source, "Basic Rules 2024: Fighter — Level 13 Studied Attacks and Indomitable"])


def build_karnok_stoneward_level14_profile() -> CharacterBuildProfile:
    source = "D&D Beyond Basic Rules 2024: Fighter Level 14 Ability Score Improvement"
    return _advance(build_karnok_stoneward_level13_profile, 14, [FeatureAudit(
        feature_id="ability-score-improvement-l14", feature_name="Ability Score Improvement",
        source_reference=source, category="feat", combat_relevant=True, automated=True,
        notes="Deterministic ranged-defense progression: +2 Dexterity, DEX 13→15.",
    )], [source, "Basic Rules 2024: Feats — Ability Score Improvement (+2 Dexterity)"])


def build_karnok_stoneward_level15_profile() -> CharacterBuildProfile:
    source = "D&D Beyond Basic Rules 2024: Champion Level 15 Superior Critical"
    return _advance(build_karnok_stoneward_level14_profile, 15, [FeatureAudit(
        feature_id="superior-critical", feature_name="Superior Critical", source_reference=source,
        category="subclass", combat_relevant=True, automated=True,
        notes="Champion weapon attacks score a critical hit on an 18–20, replacing Improved Critical's 19–20 threshold.",
    )], [source])


def build_karnok_stoneward_level16_profile() -> CharacterBuildProfile:
    source = "D&D Beyond Basic Rules 2024: Fighter Level 16 Ability Score Improvement"
    return _advance(build_karnok_stoneward_level15_profile, 16, [FeatureAudit(
        feature_id="ability-score-improvement-l16", feature_name="Ability Score Improvement",
        source_reference=source, category="feat", combat_relevant=True, automated=True,
        notes="Deterministic ranged-defense progression: +2 Dexterity, DEX 15→17.",
    )], [source, "Basic Rules 2024: Feats — Ability Score Improvement (+2 Dexterity)"])


def build_karnok_stoneward_level17_profile() -> CharacterBuildProfile:
    source = "D&D Beyond Basic Rules 2024: Fighter Level 17"
    return _advance(
        build_karnok_stoneward_level16_profile, 17, [],
        [source, "Basic Rules 2024: Fighter — Level 17 Action Surge and Indomitable use increases"],
    )


def build_karnok_stoneward_level18_profile() -> CharacterBuildProfile:
    source = "D&D Beyond Basic Rules 2024: Champion Level 18 Survivor"
    audits = [
        FeatureAudit(
            feature_id="survivor-defy-death", feature_name="Survivor: Defy Death",
            source_reference=source, category="subclass", combat_relevant=True, automated=True,
            notes="Generic death-save progression grants Advantage and treats 18-20 as recovery rolls.",
        ),
        FeatureAudit(
            feature_id="survivor-heroic-rally", feature_name="Survivor: Heroic Rally",
            source_reference=source, category="subclass", combat_relevant=True, automated=True,
            notes="Generic start-turn recovery heals 5 + Constitution modifier while alive and Bloodied.",
        ),
    ]
    return _advance(build_karnok_stoneward_level17_profile, 18, audits, [source])
