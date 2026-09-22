from __future__ import annotations

from app.content.audited_rogue_profile import _feature
from app.content.canonical_progression import advance_profile_data
from app.content.rogue_mid_progression_profile import build_mara_quickstep_level8_profile
from app.domain.character_builds import AbilityIncrease, AbilityScores, CharacterBuildProfile


def build_mara_quickstep_level9_profile() -> CharacterBuildProfile:
    """Level 9 inherits level 8; Supreme Sneak is inert until Hide is an arena path."""
    try:
        previous = build_mara_quickstep_level8_profile()
        data = advance_profile_data(previous, 9)
        data.update(
            feature_audits=[
                *data["feature_audits"],
                _feature(
                    "thief-supreme-sneak", "Supreme Sneak", "subclass",
                    combat_relevant=False, automated=False,
                    notes=(
                        "Stealth Attack requires the Hide action's Invisible condition. "
                        "The standard Iron Pit arena currently executes no Hide/Stealth path."
                    ),
                ).model_dump(),
            ],
            source_references=[
                *data["source_references"],
                "Basic Rules 2024: Thief 9 — Supreme Sneak / Stealth Attack",
            ],
        )
        return CharacterBuildProfile.model_validate(data)
    except Exception as exc:
        raise RuntimeError("Mara Rogue level 9 profile could not be created.") from exc



def build_mara_quickstep_level10_profile() -> CharacterBuildProfile:
    """Level 10 inherits level 9 and applies the canonical +2 Constitution ASI."""
    try:
        previous = build_mara_quickstep_level9_profile()
        data = advance_profile_data(previous, 10)
        data.update(
            advancement_increases=[
                *[item.model_dump() for item in previous.advancement_increases],
                AbilityIncrease(ability="constitution", amount=2).model_dump(),
            ],
            final_ability_scores=AbilityScores(
                strength=13, dexterity=20, constitution=18,
                intelligence=10, wisdom=10, charisma=10,
            ).model_dump(),
            feature_audits=[
                *data["feature_audits"],
                _feature(
                    "ability-score-improvement-l10", "Ability Score Improvement", "feat",
                    combat_relevant=True, automated=True,
                    notes="Canonical combat choice increases Constitution 16→18 after Dexterity reached 20.",
                ).model_dump(),
            ],
            source_references=[
                *data["source_references"],
                "Basic Rules 2024: Rogue 10 — Ability Score Improvement",
                "Basic Rules 2024: Feats — Ability Score Improvement (+2 Constitution)",
            ],
        )
        return CharacterBuildProfile.model_validate(data)
    except Exception as exc:
        raise RuntimeError("Mara Rogue level 10 profile could not be created.") from exc
