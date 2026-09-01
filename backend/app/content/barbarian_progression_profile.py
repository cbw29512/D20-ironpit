from __future__ import annotations

from app.content.audited_barbarian_profile import build_rokhan_stonefury_profile
from app.content.canonical_progression import advance_profile_data
from app.domain.character_builds import AbilityIncrease, AbilityScores, CharacterBuildProfile, FeatureAudit


def _level_two_features() -> list[FeatureAudit]:
    source = "D&D Beyond Basic Rules 2024: Barbarian Level 2"
    return [
        FeatureAudit(
            feature_id="danger-sense", feature_name="Danger Sense", source_reference=source,
            category="class", combat_relevant=True, automated=True,
            notes="Advantage applies to Dexterity saving throws unless Rokhan is Incapacitated.",
        ),
        FeatureAudit(
            feature_id="reckless-attack", feature_name="Reckless Attack", source_reference=source,
            category="class", combat_relevant=True, automated=True,
            notes=("On Rokhan's first Strength attack roll each turn, Iron Pit chooses Reckless Attack; his Strength "
                   "attack rolls gain Advantage and attacks against him gain Advantage until his next turn starts."),
        ),
    ]


def _level_three_features() -> list[FeatureAudit]:
    source = "D&D Beyond Basic Rules 2024: Barbarian Level 3"
    return [
        FeatureAudit(
            feature_id="frenzy", feature_name="Frenzy", source_reference=source,
            category="subclass", combat_relevant=True, automated=True,
            notes=("While Rage is active, using Reckless Attack adds Rage Damage bonus d6s to the first target "
                   "Rokhan hits on his turn with a Strength-based attack; the extra damage matches the attack type."),
        ),
        FeatureAudit(
            feature_id="primal-knowledge", feature_name="Primal Knowledge", source_reference=source,
            category="class", combat_relevant=False, automated=False,
            notes=("RAW-valid randomized proficiency choice: Nature. Its Rage ability-substitution clause does not "
                   "change Rokhan's certified arena outcomes because grapple escape already selects stronger Athletics."),
        ),
    ]


def _level_four_feature_audits(data: dict[str, object]) -> list[dict[str, object]]:
    audits = data.get("feature_audits")
    if not isinstance(audits, list):
        raise ValueError("Rokhan Barbarian 4 profile has an unexpected feature-audit schema.")
    for audit in audits:
        if isinstance(audit, dict) and audit.get("feature_id") == "weapon-mastery":
            audit["notes"] = (
                "Legal masteries are Flail, Pike, and Longsword. Rokhan's arena loadout deliberately uses Greataxe "
                "and Handaxe, so no selected mastery is invoked."
            )
    asi = FeatureAudit(
        feature_id="ability-score-improvement-l4", feature_name="Ability Score Improvement",
        source_reference="D&D Beyond Basic Rules 2024: Barbarian Level 4; Feats — Ability Score Improvement",
        category="feat", combat_relevant=True, automated=True,
        notes=("Split +1 Strength / +1 Constitution: STR 17→18 and CON 15→16. Runtime attacks, damage, AC, "
               "Strength and Constitution saves, Athletics, and retroactive Constitution-based HP are updated."),
    )
    return [*audits, asi.model_dump()]


def build_rokhan_stonefury_level2_profile() -> CharacterBuildProfile:
    previous = build_rokhan_stonefury_profile()
    data = advance_profile_data(previous, 2)
    data.update(
        feature_audits=[*data["feature_audits"], *(item.model_dump() for item in _level_two_features())],
        source_references=[*data["source_references"], "Basic Rules 2024: Barbarian — Level 2 Danger Sense and Reckless Attack"],
    )
    return CharacterBuildProfile.model_validate(data)


def build_rokhan_stonefury_level3_profile() -> CharacterBuildProfile:
    previous = build_rokhan_stonefury_level2_profile()
    data = advance_profile_data(previous, 3)
    data.update(
        skill_proficiencies=[*data["skill_proficiencies"], "Nature"],
        feature_audits=[*data["feature_audits"], *(item.model_dump() for item in _level_three_features())],
        source_references=[*data["source_references"], "Basic Rules 2024: Barbarian — Level 3 Path of the Berserker, Frenzy, and Primal Knowledge"],
    )
    return CharacterBuildProfile.model_validate(data)


def build_rokhan_stonefury_level4_profile() -> CharacterBuildProfile:
    previous = build_rokhan_stonefury_level3_profile()
    data = advance_profile_data(previous, 4)
    data.update(
        advancement_increases=[
            AbilityIncrease(ability="strength", amount=1).model_dump(),
            AbilityIncrease(ability="constitution", amount=1).model_dump(),
        ],
        final_ability_scores=AbilityScores(
            strength=18, dexterity=13, constitution=16, intelligence=8, wisdom=12, charisma=10,
        ).model_dump(),
        weapon_masteries=[*data["weapon_masteries"], "longsword"],
        feature_audits=_level_four_feature_audits(data),
        source_references=[
            *data["source_references"],
            "Basic Rules 2024: Barbarian — Level 4 Ability Score Improvement and 3 Weapon Masteries",
            "Basic Rules 2024: Feats — Ability Score Improvement (+1 Strength, +1 Constitution)",
        ],
    )
    return CharacterBuildProfile.model_validate(data)
