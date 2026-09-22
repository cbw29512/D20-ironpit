from __future__ import annotations

from app.content.audited_rogue_profile import _feature, build_mara_quickstep_profile
from app.content.canonical_hero_policy import canonical_template_id
from app.content.canonical_progression import advance_profile_data
from app.domain.character_builds import AbilityIncrease, AbilityScores, CharacterBuildProfile


def build_mara_quickstep_level2_profile() -> CharacterBuildProfile:
    """Level 2 preserves Mara's build and adds Cunning Action."""
    try:
        base = build_mara_quickstep_profile()
        return base.model_copy(update={
            "id": "build-mara-quickstep-l2",
            "template_id": canonical_template_id("rogue", 2),
            "level": 2,
            "feature_audits": [
                *base.feature_audits,
                _feature(
                    "cunning-action", "Cunning Action", "class",
                    combat_relevant=True, automated=True,
                    notes="Uses the shared bonus-action Dash/Disengage/Hide engine.",
                ),
            ],
            "source_references": [
                *base.source_references,
                "Basic Rules 2024: Rogue 2 — Cunning Action",
            ],
        })
    except Exception as exc:
        raise RuntimeError("Mara Rogue level 2 profile could not be created.") from exc


def build_mara_quickstep_level3_profile() -> CharacterBuildProfile:
    """Level 3 adds Steady Aim and the Thief subclass."""
    try:
        base = build_mara_quickstep_level2_profile()
        return base.model_copy(update={
            "id": "build-mara-quickstep-l3",
            "template_id": canonical_template_id("rogue", 3),
            "level": 3,
            "subclass_id": "thief",
            "subclass_name": "Thief",
            "feature_audits": [
                *base.feature_audits,
                _feature(
                    "steady-aim", "Steady Aim", "class",
                    combat_relevant=True, automated=True,
                    notes="Shared stationary Bonus Action grants Advantage on the next legal attack this turn.",
                ),
                _feature(
                    "thief-fast-hands", "Fast Hands", "subclass",
                    combat_relevant=False, automated=False,
                    notes="Loadout-inert: Mara has no qualifying combat item action modeled.",
                ),
                _feature(
                    "thief-second-story-work", "Second-Story Work", "subclass",
                    combat_relevant=False, automated=False,
                    notes="Arena-inert in the standard Iron Pit battlefield.",
                ),
            ],
            "source_references": [
                *base.source_references,
                "Basic Rules 2024: Rogue 3 — Steady Aim; Thief — Fast Hands and Second-Story Work",
            ],
        })
    except Exception as exc:
        raise RuntimeError("Mara Rogue level 3 profile could not be created.") from exc


def build_mara_quickstep_level4_profile() -> CharacterBuildProfile:
    """Level 4 takes the canonical ASI as +1 Dexterity / +1 Constitution."""
    try:
        previous = build_mara_quickstep_level3_profile()
        data = advance_profile_data(previous, 4)
        data.update(
            advancement_increases=[
                AbilityIncrease(ability="dexterity", amount=1).model_dump(),
                AbilityIncrease(ability="constitution", amount=1).model_dump(),
            ],
            final_ability_scores=AbilityScores(
                strength=13, dexterity=18, constitution=16,
                intelligence=10, wisdom=10, charisma=10,
            ).model_dump(),
            feature_audits=[
                *data["feature_audits"],
                _feature(
                    "ability-score-improvement-l4", "Ability Score Improvement", "feat",
                    combat_relevant=True, automated=True,
                    notes="Canonical choice splits +1 Dexterity / +1 Constitution: DEX 17→18 and CON 15→16.",
                ).model_dump(),
            ],
            source_references=[
                *data["source_references"],
                "Basic Rules 2024: Rogue 4 — Ability Score Improvement",
                "Basic Rules 2024: Feats — Ability Score Improvement (+1 Dexterity, +1 Constitution)",
            ],
        )
        return CharacterBuildProfile.model_validate(data)
    except Exception as exc:
        raise RuntimeError("Mara Rogue level 4 profile could not be created.") from exc



def build_mara_quickstep_level5_profile() -> CharacterBuildProfile:
    """Level 5 inherits level 4, then adds Cunning Strike and Uncanny Dodge."""
    try:
        previous = build_mara_quickstep_level4_profile()
        data = advance_profile_data(previous, 5)
        data.update(
            feature_audits=[
                *data["feature_audits"],
                _feature(
                    "cunning-strike", "Cunning Strike", "class",
                    combat_relevant=True, automated=True,
                    notes=(
                        "Canonical automation uses Trip when a Large-or-smaller target can be affected, "
                        "trading 1d6 Sneak Attack before rolling. Poison is unavailable without a Poisoner's Kit."
                    ),
                ).model_dump(),
                _feature(
                    "uncanny-dodge", "Uncanny Dodge", "class",
                    combat_relevant=True, automated=True,
                    notes="Reuses the shared visible-attacker Reaction that halves attack damage.",
                ).model_dump(),
            ],
            source_references=[
                *data["source_references"],
                "Basic Rules 2024: Rogue 5 — Cunning Strike and Uncanny Dodge",
            ],
        )
        return CharacterBuildProfile.model_validate(data)
    except Exception as exc:
        raise RuntimeError("Mara Rogue level 5 profile could not be created.") from exc
