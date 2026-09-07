from __future__ import annotations

from app.content.audited_rogue_profile import build_mara_quickstep_profile
from app.content.canonical_progression import advance_profile_data
from app.content.hero_progressions import HERO_BY_CLASS
from app.domain.character_builds import AbilityIncrease, AbilityScores, CharacterBuildProfile, FeatureAudit


def _audit(feature_id: str, name: str, category: str, *, relevant: bool, notes: str) -> FeatureAudit:
    return FeatureAudit(
        feature_id=feature_id,
        feature_name=name,
        source_reference="D&D Beyond Basic Rules 2024: Rogue and Thief",
        category=category,
        combat_relevant=relevant,
        automated=True,
        notes=notes,
    )


def build_mara_quickstep_level2_profile() -> CharacterBuildProfile:
    data = advance_profile_data(build_mara_quickstep_profile(), 2)
    data.update(
        feature_audits=[*data["feature_audits"], _audit(
            "cunning-action", "Cunning Action", "class", relevant=False,
            notes="Dash, Disengage, and tactical Hide do not alter the fixed open Iron Pit's attack opportunities.",
        ).model_dump()],
        source_references=[*data["source_references"], "Basic Rules 2024: Rogue 2 — Cunning Action"],
    )
    return CharacterBuildProfile.model_validate(data)


def build_mara_quickstep_level3_profile() -> CharacterBuildProfile:
    data = advance_profile_data(build_mara_quickstep_level2_profile(), 3)
    hero = HERO_BY_CLASS["rogue"]
    audits = [
        _audit(
            "steady-aim", "Steady Aim", "class", relevant=True,
            notes="The Bonus Action grants Advantage to Mara's next attack; its Speed restriction is arena-neutral.",
        ),
        _audit(
            "thief-fast-hands", "Fast Hands", "subclass", relevant=False,
            notes="The standard Iron Pit has no tactical object inventory or Sleight-of-Hand objective to exploit.",
        ),
    ]
    data.update(
        subclass_id=hero.subclass_id,
        subclass_name=hero.subclass_name,
        feature_audits=[*data["feature_audits"], *(item.model_dump() for item in audits)],
        source_references=[*data["source_references"], "Basic Rules 2024: Rogue 3; Thief 3"],
    )
    return CharacterBuildProfile.model_validate(data)


def build_mara_quickstep_level4_profile() -> CharacterBuildProfile:
    data = advance_profile_data(build_mara_quickstep_level3_profile(), 4)
    increases = [AbilityIncrease(ability="dexterity", amount=1), AbilityIncrease(ability="constitution", amount=1)]
    data.update(
        advancement_increases=[item.model_dump() for item in increases],
        final_ability_scores=AbilityScores(
            strength=13, dexterity=18, constitution=16, intelligence=10, wisdom=10, charisma=10,
        ).model_dump(),
        feature_audits=[*data["feature_audits"], _audit(
            "ability-score-improvement-l4", "Ability Score Improvement", "feat", relevant=True,
            notes="Split +1 Dexterity/+1 Constitution rounds both odd scores and updates AC, attacks, saves, skills, and HP.",
        ).model_dump()],
        source_references=[*data["source_references"], "Basic Rules 2024: Rogue 4 — Ability Score Improvement"],
    )
    return CharacterBuildProfile.model_validate(data)
