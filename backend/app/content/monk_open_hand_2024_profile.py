from __future__ import annotations

import logging

from app.content.canonical_combat_build_policy import (
    canonical_background_increases,
    canonical_base_ability_scores,
)
from app.content.canonical_hero_policy import canonical_template_id
from app.content.hero_progressions import HERO_BY_CLASS
from app.content.monk_open_hand_2024_profile_features import build_monk_2024_feature_audits
from app.domain.character_builds import AbilityIncrease, CharacterBuildProfile

logger = logging.getLogger(__name__)


def build_kael_stillwater_2024_profile(level: int = 1) -> CharacterBuildProfile:
    """Compile the legal persistent 2024 Kael progression through the current level."""
    try:
        if level not in {1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19}:
            raise ValueError("The current 2024 Monk profile tranche supports levels 1-19 only.")
        hero = HERO_BY_CLASS["monk"]
        base = canonical_base_ability_scores("monk")
        background_allowed = ["dexterity", "constitution", "intelligence"]
        background = canonical_background_increases("monk", background_allowed)
        advancement: list[AbilityIncrease] = []
        if level >= 4:
            advancement.append(AbilityIncrease(ability="dexterity", amount=2))
        if level >= 8:
            advancement.extend([
                AbilityIncrease(ability="dexterity", amount=1),
                AbilityIncrease(ability="constitution", amount=1),
            ])
        if level >= 12:
            advancement.append(AbilityIncrease(ability="wisdom", amount=2))
        if level >= 16:
            advancement.append(AbilityIncrease(ability="wisdom", amount=2))
        if level >= 19:
            advancement.append(AbilityIncrease(ability="dexterity", amount=1))
        values = base.model_dump()
        for increase in [*background, *advancement]:
            values[increase.ability] += increase.amount
        final = type(base)(**values)
        return CharacterBuildProfile(
            id=f"build-kael-stillwater-2024-l{level}",
            template_id=canonical_template_id("monk", level),
            character_name=hero.hero_name,
            class_id="monk",
            class_name=hero.class_name,
            level=level,
            ruleset="2024",
            build_id="unarmed-offense",
            subclass_id="warrior-of-the-open-hand" if level >= 3 else None,
            subclass_name="Warrior of the Open Hand" if level >= 3 else None,
            species_id="human",
            species_name="Human",
            background_id="criminal",
            background_name="Criminal",
            origin_feat_id="alert",
            origin_feat_name="Alert",
            base_ability_scores=base,
            background_allowed_abilities=background_allowed,
            background_increases=background,
            advancement_increases=advancement,
            final_ability_scores=final,
            ability_score_maximums={"dexterity": 30} if level >= 19 else {},
            class_equipment_option="package",
            class_equipment=["Spear", "5 Daggers", "Woodcarver's Tools", "Explorer's Pack", "11 GP"],
            background_equipment_option="package",
            background_equipment=[
                "2 Daggers", "Thieves' Tools", "Crowbar", "2 Pouches", "Traveler's Clothes", "16 GP",
            ],
            skill_proficiencies=[
                "Sleight of Hand", "Stealth", "Acrobatics", "Insight",
                "Perception", "History", "Nature", "Religion",
            ],
            weapon_masteries=[],
            combat_loadout_kind="unarmed",
            feature_audits=build_monk_2024_feature_audits(level),
            source_references=[
                "Basic Rules 2024: Monk — Martial Arts, Monk's Focus, Unarmored Movement, Uncanny Metabolism, Deflect Attacks, Extra Attack, Stunning Strike, Empowered Strikes, Evasion, Acrobatic Movement, Heightened Focus, Self-Restoration, Deflect Energy, Disciplined Survivor, Perfect Focus, Superior Defense",
                *(["Basic Rules 2024: Warrior of the Open Hand — Open Hand Technique"] if level >= 3 else []),
                *(["Basic Rules 2024: Warrior of the Open Hand — Wholeness of Body"] if level >= 6 else []),
                *(["Basic Rules 2024: Warrior of the Open Hand — Fleet Step"] if level >= 11 else []),
                *(["Basic Rules 2024: Warrior of the Open Hand — Quivering Palm"] if level >= 17 else []),
                *(
                    ["Basic Rules 2024: Monk Level 19 — Epic Boon; Feats — Boon of Irresistible Offense (+1 Dexterity)"]
                    if level >= 19 else []
                ),
                *(
                    ["Basic Rules 2024: Monk Level 4 — Ability Score Improvement and Slow Fall; Feats — Ability Score Improvement (+2 Dexterity)"]
                    if level >= 4 else []
                ),
                *(
                    ["Basic Rules 2024: Monk Level 8 — Ability Score Improvement; Feats — Ability Score Improvement (+1 Dexterity, +1 Constitution)"]
                    if level >= 8 else []
                ),
                *(
                    ["Basic Rules 2024: Monk Level 12 — Ability Score Improvement; Feats — Ability Score Improvement (+2 Wisdom)"]
                    if level >= 12 else []
                ),
                *(
                    ["Basic Rules 2024: Monk Level 16 — Ability Score Improvement; Feats — Ability Score Improvement (+2 Wisdom)"]
                    if level >= 16 else []
                ),
                "Basic Rules 2024: Character Origins — Criminal and Human",
                "Basic Rules 2024: Feats — Alert and Skilled",
            ],
        )
    except Exception:
        logger.exception("Failed to compile 2024 Kael Stillwater profile at level %s.", level)
        raise
