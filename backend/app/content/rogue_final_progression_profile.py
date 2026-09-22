from __future__ import annotations

from app.content.audited_rogue_profile import _feature
from app.content.canonical_progression import advance_profile_data
from app.content.rogue_endgame_progression_profile import build_mara_quickstep_level16_profile
from app.domain.character_builds import AbilityIncrease, AbilityScores, CharacterBuildProfile


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



def build_mara_quickstep_level18_profile() -> CharacterBuildProfile:
    """Level 18 inherits level 17 and gains Elusive."""
    try:
        previous = build_mara_quickstep_level17_profile()
        data = advance_profile_data(previous, 18)
        data.update(
            feature_audits=[
                *data["feature_audits"],
                _feature(
                    "elusive", "Elusive", "class",
                    combat_relevant=True, automated=True,
                    notes=(
                        "Uses the generic defender Advantage-suppression capability. "
                        "Attack-roll Advantage sources are suppressed unless Mara is Incapacitated; "
                        "Disadvantage sources remain unchanged."
                    ),
                ).model_dump(),
            ],
            source_references=[
                *data["source_references"],
                "Basic Rules 2024: Rogue 18 — Elusive",
            ],
        )
        return CharacterBuildProfile.model_validate(data)
    except Exception as exc:
        raise RuntimeError("Mara Rogue level 18 profile could not be created.") from exc



def build_mara_quickstep_level19_profile() -> CharacterBuildProfile:
    """Level 19 inherits level 18 and takes Boon of Combat Prowess."""
    try:
        previous = build_mara_quickstep_level18_profile()
        data = advance_profile_data(previous, 19)
        data.update(
            advancement_increases=[
                *[item.model_dump() for item in previous.advancement_increases],
                AbilityIncrease(ability="strength", amount=1).model_dump(),
            ],
            final_ability_scores=AbilityScores(
                strength=14, dexterity=20, constitution=20,
                intelligence=10, wisdom=12, charisma=10,
            ).model_dump(),
            feature_audits=[
                *data["feature_audits"],
                _feature(
                    "boon-combat-prowess", "Boon of Combat Prowess", "feat",
                    combat_relevant=True, automated=True,
                    notes=(
                        "Canonical boon increases Strength 13→14 for an immediate modifier gain. "
                        "Peerless Aim reuses the generic once-per-turn miss-to-hit capability."
                    ),
                ).model_dump(),
            ],
            source_references=[
                *data["source_references"],
                "Basic Rules 2024: Rogue 19 — Epic Boon",
                "Basic Rules 2024: Boon of Combat Prowess — Ability Score Increase; Peerless Aim",
            ],
        )
        return CharacterBuildProfile.model_validate(data)
    except Exception as exc:
        raise RuntimeError("Mara Rogue level 19 profile could not be created.") from exc



def build_mara_quickstep_level20_profile() -> CharacterBuildProfile:
    """Level 20 inherits level 19 and gains Stroke of Luck."""
    try:
        previous = build_mara_quickstep_level19_profile()
        data = advance_profile_data(previous, 20)
        data.update(
            feature_audits=[
                *data["feature_audits"],
                _feature(
                    "stroke-of-luck", "Stroke of Luck", "class",
                    combat_relevant=True, automated=True,
                    notes=(
                        "Uses a generic one-use failed-D20-to-natural-20 resource override. "
                        "Iron Pit initializes the resource fresh each fight, matching a recovered "
                        "Short/Long Rest use for arena combat."
                    ),
                ).model_dump(),
            ],
            source_references=[
                *data["source_references"],
                "Basic Rules 2024: Rogue 20 — Stroke of Luck",
            ],
        )
        return CharacterBuildProfile.model_validate(data)
    except Exception as exc:
        raise RuntimeError("Mara Rogue level 20 profile could not be created.") from exc
