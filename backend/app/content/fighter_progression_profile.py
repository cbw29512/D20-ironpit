from __future__ import annotations

from app.content.audited_fighter_profile import build_karnok_stoneward_profile
from app.content.canonical_progression import advance_profile_data
from app.domain.character_builds import AbilityIncrease, AbilityScores, CharacterBuildProfile, FeatureAudit


def _level_two_features() -> list[FeatureAudit]:
    source = "D&D Beyond Basic Rules 2024: Fighter Level 2"
    return [
        FeatureAudit(
            feature_id="action-surge", feature_name="Action Surge", source_reference=source,
            category="class", combat_relevant=True, automated=True,
            notes="Iron Pit spends Action Surge only when the additional non-Magic Action can immediately make a legal Attack.",
        ),
        FeatureAudit(
            feature_id="tactical-mind", feature_name="Tactical Mind", source_reference=source,
            category="class", combat_relevant=True, automated=True,
            notes="Applied after failed automated ability checks; the current combat engine exposes grapple escape checks.",
        ),
    ]


def _level_three_features() -> list[FeatureAudit]:
    source = "D&D Beyond Basic Rules 2024: Champion Level 3"
    return [
        FeatureAudit(
            feature_id="improved-critical", feature_name="Improved Critical", source_reference=source,
            category="class", combat_relevant=True, automated=True,
            notes="Weapon and Unarmed Strike attacks score a Critical Hit on 19-20; only natural 20 is an automatic hit.",
        ),
        FeatureAudit(
            feature_id="remarkable-athlete", feature_name="Remarkable Athlete", source_reference=source,
            category="class", combat_relevant=True, automated=True,
            notes=("Advantage on Initiative and Strength (Athletics); after a Critical Hit, Iron Pit may use the granted "
                   "half-Speed movement only to close, never retreat, and it provokes no Opportunity Attacks."),
        ),
    ]


def _level_four_features() -> list[FeatureAudit]:
    source = "D&D Beyond Basic Rules 2024: Fighter Level 4; Feats — Ability Score Improvement"
    return [
        FeatureAudit(
            feature_id="ability-score-improvement-l4", feature_name="Ability Score Improvement", source_reference=source,
            category="feat", combat_relevant=True, automated=True,
            notes=("Split +1 Strength / +1 Constitution: STR 17→18 and CON 15→16. Runtime attack, damage, "
                   "Strength save, Athletics, and retroactive Constitution-based HP are updated."),
        ),
    ]


def _level_five_features() -> list[FeatureAudit]:
    source = "D&D Beyond Basic Rules 2024: Fighter Level 5"
    return [
        FeatureAudit(
            feature_id="extra-attack", feature_name="Extra Attack", source_reference=source,
            category="class", combat_relevant=True, automated=True,
            notes="The Attack action resolves two legal weapon attacks; Action Surge reuses the same two-slot Attack action.",
        ),
        FeatureAudit(
            feature_id="tactical-shift", feature_name="Tactical Shift", source_reference=source,
            category="class", combat_relevant=True, automated=True,
            notes="After Second Wind, Iron Pit uses the granted half-Speed OA-free movement to close toward the nearest enemy.",
        ),
    ]


def _level_four_feature_audits(data: dict[str, object]) -> list[dict[str, object]]:
    audits = data.get("feature_audits")
    if not isinstance(audits, list):
        raise ValueError("Karnok Fighter 4 profile has an unexpected feature-audit schema.")
    for audit in audits:
        if isinstance(audit, dict) and audit.get("feature_id") == "weapon-mastery":
            audit["notes"] = (
                "Legal masteries are Flail, Javelin, Spear, and Longsword. The standard arena loadout deliberately "
                "uses Greatsword and Shortbow, so no selected mastery is invoked."
            )
    return [*audits, *(item.model_dump() for item in _level_four_features())]


def build_karnok_stoneward_level2_profile() -> CharacterBuildProfile:
    previous = build_karnok_stoneward_profile()
    data = advance_profile_data(previous, 2)
    data.update(
        feature_audits=[*data["feature_audits"], *(item.model_dump() for item in _level_two_features())],
        source_references=[*data["source_references"], "Basic Rules 2024: Fighter — Level 2 Action Surge and Tactical Mind"],
    )
    return CharacterBuildProfile.model_validate(data)


def build_karnok_stoneward_level3_profile() -> CharacterBuildProfile:
    previous = build_karnok_stoneward_level2_profile()
    data = advance_profile_data(previous, 3)
    data.update(
        feature_audits=[*data["feature_audits"], *(item.model_dump() for item in _level_three_features())],
        source_references=[*data["source_references"], "Basic Rules 2024: Champion — Level 3 Improved Critical and Remarkable Athlete"],
    )
    return CharacterBuildProfile.model_validate(data)


def build_karnok_stoneward_level4_profile() -> CharacterBuildProfile:
    previous = build_karnok_stoneward_level3_profile()
    data = advance_profile_data(previous, 4)
    data.update(
        advancement_increases=[
            AbilityIncrease(ability="strength", amount=1).model_dump(),
            AbilityIncrease(ability="constitution", amount=1).model_dump(),
        ],
        final_ability_scores=AbilityScores(
            strength=18, dexterity=13, constitution=16, intelligence=10, wisdom=10, charisma=10,
        ).model_dump(),
        weapon_masteries=[*data["weapon_masteries"], "longsword"],
        feature_audits=_level_four_feature_audits(data),
        source_references=[
            *data["source_references"],
            "Basic Rules 2024: Fighter — Level 4 Ability Score Improvement, 3 Second Wind uses, 4 Weapon Masteries",
            "Basic Rules 2024: Feats — Ability Score Improvement (+1 Strength, +1 Constitution)",
        ],
    )
    return CharacterBuildProfile.model_validate(data)


def build_karnok_stoneward_level5_profile() -> CharacterBuildProfile:
    previous = build_karnok_stoneward_level4_profile()
    data = advance_profile_data(previous, 5)
    data.update(
        feature_audits=[*data["feature_audits"], *(item.model_dump() for item in _level_five_features())],
        source_references=[*data["source_references"], "Basic Rules 2024: Fighter — Level 5 Extra Attack and Tactical Shift"],
    )
    return CharacterBuildProfile.model_validate(data)
