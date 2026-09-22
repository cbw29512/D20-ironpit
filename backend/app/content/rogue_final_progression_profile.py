from __future__ import annotations

from app.content.audited_rogue_profile import _feature
from app.content.canonical_progression import advance_profile_data
from app.content.rogue_endgame_progression_profile import build_mara_quickstep_level16_profile
from app.domain.character_builds import CharacterBuildProfile


def build_mara_quickstep_level17_profile() -> CharacterBuildProfile:
    """Level 17 inherits level 16 and gains Thief's Reflexes."""
    try:
        previous = build_mara_quickstep_level16_profile()
        data = advance_profile_data(previous, 17)
        data.update(
            feature_audits=[
                *data["feature_audits"],
                _feature(
                    "thiefs-reflexes", "Thief's Reflexes", "subclass",
                    combat_relevant=True, automated=True,
                    notes=(
                        "Uses the generic first-round extra-turn scheduler: a second turn "
                        "at normal Initiative minus 10, only during round 1."
                    ),
                ).model_dump(),
            ],
            source_references=[
                *data["source_references"],
                "Basic Rules 2024: Thief 17 — Thief's Reflexes",
            ],
        )
        return CharacterBuildProfile.model_validate(data)
    except Exception as exc:
        raise RuntimeError("Mara Rogue level 17 profile could not be created.") from exc
