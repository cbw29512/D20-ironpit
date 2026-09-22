from __future__ import annotations

from app.content.audited_rogue_profile import _feature
from app.content.canonical_progression import advance_profile_data
from app.content.rogue_progression_profile import build_mara_quickstep_level5_profile
from app.domain.character_builds import CharacterBuildProfile


def build_mara_quickstep_level6_profile() -> CharacterBuildProfile:
    """Level 6 inherits level 5; its added Expertise choices are arena-inert."""
    try:
        previous = build_mara_quickstep_level5_profile()
        data = advance_profile_data(previous, 6)
        data.update(
            feature_audits=[
                *data["feature_audits"],
                _feature(
                    "expertise-l6", "Expertise", "class",
                    combat_relevant=False, automated=False,
                    notes=(
                        "Canonical additional Expertise choices are Perception and Intimidation. "
                        "They do not alter the current Iron Pit combat runtime."
                    ),
                ).model_dump(),
            ],
            source_references=[
                *data["source_references"],
                "Basic Rules 2024: Rogue 6 — Expertise",
            ],
        )
        return CharacterBuildProfile.model_validate(data)
    except Exception as exc:
        raise RuntimeError("Mara Rogue level 6 profile could not be created.") from exc


def build_mara_quickstep_level7_profile() -> CharacterBuildProfile:
    """Level 7 inherits level 6, adds shared Evasion, and audits Reliable Talent as arena-inert."""
    try:
        previous = build_mara_quickstep_level6_profile()
        data = advance_profile_data(previous, 7)
        data.update(
            feature_audits=[
                *data["feature_audits"],
                _feature(
                    "evasion", "Evasion", "class",
                    combat_relevant=True, automated=True,
                    notes="Reuses the shared Dexterity-save damage reduction primitive.",
                ).model_dump(),
                _feature(
                    "reliable-talent", "Reliable Talent", "class",
                    combat_relevant=False, automated=False,
                    notes=(
                        "Audited RAW. The standard Iron Pit arena currently executes no qualifying "
                        "proficient ability-check path, so no d20-floor mutation is exercised."
                    ),
                ).model_dump(),
            ],
            source_references=[
                *data["source_references"],
                "Basic Rules 2024: Rogue 7 — Evasion and Reliable Talent",
            ],
        )
        return CharacterBuildProfile.model_validate(data)
    except Exception as exc:
        raise RuntimeError("Mara Rogue level 7 profile could not be created.") from exc
