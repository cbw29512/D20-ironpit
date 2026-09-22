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
                        "Reuses the universal source-tagged first-round extra-turn grant: "
                        "a second turn at normal Initiative minus 10 during round 1."
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
    """Level 18 inherits level 17 and gains Elusive through the shared advantage-suppression primitive."""
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
                        "Reuses the universal attack-advantage suppression primitive already used by "
                        "the certified 2014 Rogue: attackers cannot gain Advantage while Mara is not Incapacitated."
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
            ability_score_maximums={
                **previous.ability_score_maximums,
                "strength": 30,
            },
            feature_audits=[
                *data["feature_audits"],
                _feature(
                    "boon-combat-prowess", "Boon of Combat Prowess", "feat",
                    combat_relevant=True, automated=True,
                    notes=(
                        "Peerless Aim reuses the universal source-tagged miss-to-hit override. "
                        "Its usage window refreshes at Mara's own turn start, including after off-turn attacks."
                    ),
                ).model_dump(),
            ],
            source_references=[
                *data["source_references"],
                "Basic Rules 2024: Rogue 19 — Epic Boon; Feats — Boon of Combat Prowess",
            ],
        )
        return CharacterBuildProfile.model_validate(data)
    except Exception as exc:
        raise RuntimeError("Mara Rogue level 19 profile could not be created.") from exc

def build_mara_quickstep_level20_profile() -> CharacterBuildProfile:
    """Level 20 inherits level 19 and gains the 2024 Stroke of Luck D20 replacement."""
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
                        "Uses the universal resource-backed failed-D20 replacement primitive. "
                        "Unlike the 2014 version, the 2024 feature replaces a failed eligible D20 Test roll with 20, "
                        "so failed attacks can become critical hits and failed saving throws can become successes."
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
