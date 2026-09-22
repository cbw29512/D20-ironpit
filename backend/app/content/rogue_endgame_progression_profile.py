from __future__ import annotations

from app.content.audited_rogue_profile import _feature
from app.content.canonical_progression import advance_profile_data
from app.content.rogue_high_progression_profile import build_mara_quickstep_level12_profile
from app.domain.character_builds import AbilityIncrease, AbilityScores, CharacterBuildProfile


def build_mara_quickstep_level13_profile() -> CharacterBuildProfile:
    """Level 13 inherits level 12; Use Magic Device is loadout-dependent."""
    try:
        previous = build_mara_quickstep_level12_profile()
        data = advance_profile_data(previous, 13)
        data.update(
            feature_audits=[
                *data["feature_audits"],
                _feature(
                    "thief-use-magic-device", "Use Magic Device", "subclass",
                    combat_relevant=False, automated=False,
                    notes=(
                        "Mara's certified loadout has no qualifying attunement overflow, "
                        "charge-using magic item, or Spell Scroll. Preserve the feature without "
                        "faking item behavior; treasure integration can activate it later."
                    ),
                ).model_dump(),
            ],
            source_references=[
                *data["source_references"],
                "Basic Rules 2024: Thief 13 — Use Magic Device",
            ],
        )
        return CharacterBuildProfile.model_validate(data)
    except Exception as exc:
        raise RuntimeError("Mara Rogue level 13 profile could not be created.") from exc

def build_mara_quickstep_level14_profile() -> CharacterBuildProfile:
    """Level 14 inherits level 13 and adds Devious Strikes."""
    try:
        previous = build_mara_quickstep_level13_profile()
        data = advance_profile_data(previous, 14)
        data.update(
            feature_audits=[
                *data["feature_audits"],
                _feature(
                    "devious-strikes", "Devious Strikes", "class",
                    combat_relevant=True, automated=True,
                    notes=(
                        "Canonical arena automation selects Obscure when Blinded can affect the target. "
                        "The 3d6 Sneak Attack trade is source data; the Dexterity save and Blinded condition "
                        "use shared universal mechanics."
                    ),
                ).model_dump(),
            ],
            source_references=[
                *data["source_references"],
                "Basic Rules 2024: Rogue 14 — Devious Strikes",
            ],
        )
        return CharacterBuildProfile.model_validate(data)
    except Exception as exc:
        raise RuntimeError("Mara Rogue level 14 profile could not be created.") from exc

def build_mara_quickstep_level15_profile() -> CharacterBuildProfile:
    """Level 15 inherits level 14 and adds Slippery Mind."""
    try:
        previous = build_mara_quickstep_level14_profile()
        data = advance_profile_data(previous, 15)
        data.update(
            feature_audits=[
                *data["feature_audits"],
                _feature(
                    "slippery-mind", "Slippery Mind", "class",
                    combat_relevant=True, automated=True,
                    notes=(
                        "Reuses the universal progression saving-throw proficiency grant. "
                        "The 2024 source grants Wisdom and Charisma proficiency; 2014 uses the same "
                        "primitive with Wisdom only."
                    ),
                ).model_dump(),
            ],
            source_references=[
                *data["source_references"],
                "Basic Rules 2024: Rogue 15 — Slippery Mind",
            ],
        )
        return CharacterBuildProfile.model_validate(data)
    except Exception as exc:
        raise RuntimeError("Mara Rogue level 15 profile could not be created.") from exc

def build_mara_quickstep_level16_profile() -> CharacterBuildProfile:
    """Level 16 inherits level 15 and takes the canonical +2 Wisdom ASI."""
    try:
        previous = build_mara_quickstep_level15_profile()
        data = advance_profile_data(previous, 16)
        data.update(
            advancement_increases=[
                *[item.model_dump() for item in previous.advancement_increases],
                AbilityIncrease(ability="wisdom", amount=2).model_dump(),
            ],
            final_ability_scores=AbilityScores(
                strength=13, dexterity=20, constitution=20,
                intelligence=10, wisdom=12, charisma=10,
            ).model_dump(),
            feature_audits=[
                *data["feature_audits"],
                _feature(
                    "ability-score-improvement-l16", "Ability Score Improvement (+2 Wisdom)", "class",
                    combat_relevant=True, automated=True,
                    notes=(
                        "Canonical progression decision: Wisdom 10→12 after Dexterity and Constitution "
                        "have reached 20. Derived Wisdom saves update through shared character math."
                    ),
                ).model_dump(),
            ],
            source_references=[
                *data["source_references"],
                "Basic Rules 2024: Rogue 16 — Ability Score Improvement",
            ],
        )
        return CharacterBuildProfile.model_validate(data)
    except Exception as exc:
        raise RuntimeError("Mara Rogue level 16 profile could not be created.") from exc
