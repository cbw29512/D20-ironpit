from __future__ import annotations

import logging

from app.content.canonical_progression import advance_profile_data
from app.domain.character_builds import AbilityIncrease, AbilityScores, CharacterBuildProfile, FeatureAudit

logger = logging.getLogger(__name__)


def _scores() -> AbilityScores:
    return AbilityScores(strength=12, dexterity=15, constitution=14, intelligence=10, wisdom=13, charisma=8)


def _species_increases() -> list[AbilityIncrease]:
    return [AbilityIncrease(ability="dexterity", amount=2), AbilityIncrease(ability="wisdom", amount=1)]


def _apply(scores: AbilityScores, increases: list[AbilityIncrease]) -> AbilityScores:
    values = scores.model_dump()
    for increase in increases:
        values[increase.ability] += increase.amount
    return AbilityScores(**values)


def _audits(level: int) -> list[FeatureAudit]:
    rows = [
        FeatureAudit(
            feature_id="wood-elf", feature_name="Wood Elf",
            source_reference="D&D Basic Rules 2014: Wood Elf",
            category="species", combat_relevant=True, automated=True,
            notes="DEX +2, WIS +1, 35-foot speed, Keen Senses, and Fey Ancestry reuse shared character/save mechanics.",
        ),
        FeatureAudit(
            feature_id="favored-enemy", feature_name="Favored Enemy",
            source_reference="D&D Basic Rules 2014: Ranger 1",
            category="class", combat_relevant=False, automated=True,
            notes="Tracking and information-recall benefits do not alter standard Iron Pit combat at level 1.",
        ),
        FeatureAudit(
            feature_id="natural-explorer", feature_name="Natural Explorer",
            source_reference="D&D Basic Rules 2014: Ranger 1",
            category="class", combat_relevant=False, automated=True,
            notes="Travel and exploration benefits are outside an in-progress Iron Pit fight.",
        ),
    ]
    if level >= 2:
        rows += [
            FeatureAudit(
                feature_id="fighting-style", feature_name="Fighting Style (Archery)",
                source_reference="D&D Basic Rules 2014: Ranger 2",
                category="class", combat_relevant=True, automated=True,
                notes="Reuses the universal Archery ranged-weapon attack-bonus compiler.",
            ),
            FeatureAudit(
                feature_id="spellcasting", feature_name="Spellcasting",
                source_reference="D&D Basic Rules 2014: Ranger 2",
                category="class", combat_relevant=True, automated=True,
                notes="Known-spell count, slots, healing, and buffs use shared 2014 spell primitives.",
            ),
        ]
    if level >= 3:
        rows += [
            FeatureAudit(
                feature_id="colossus-slayer", feature_name="Colossus Slayer",
                source_reference="D&D Basic Rules 2014: Hunter 3",
                category="subclass", combat_relevant=True, automated=True,
                notes=(
                    "Uses the shared once-per-turn weapon-hit damage rider with a target-below-max-HP "
                    "qualification and weapon damage-type inheritance."
                ),
            ),
            FeatureAudit(
                feature_id="primeval-awareness", feature_name="Primeval Awareness",
                source_reference="D&D Basic Rules 2014: Ranger 3",
                category="class", combat_relevant=False, automated=True,
                notes="Presence sensing reveals neither location nor number and does not alter standard arena combat.",
            ),
        ]
    if level >= 4:
        rows.append(
            FeatureAudit(
                feature_id="ability-score-improvement-4",
                feature_name="Ability Score Improvement",
                source_reference="D&D Basic Rules 2014: Ranger 4",
                category="class", combat_relevant=True, automated=True,
                notes="Canonical archer progression raises Dexterity from 17 to 19 and recomputes derived combat values.",
            )
        )
    if level >= 5:
        rows.append(
            FeatureAudit(
                feature_id="extra-attack",
                feature_name="Extra Attack",
                source_reference="D&D Basic Rules 2014: Ranger 5",
                category="class", combat_relevant=True, automated=True,
                notes="Uses the universal Attack action with two weapon-attack slots.",
            )
        )
    if level >= 6:
        rows += [
            FeatureAudit(
                feature_id="favored-enemy-improvement-6",
                feature_name="Favored Enemy Improvement",
                source_reference="D&D Basic Rules 2014: Ranger 6",
                category="class", combat_relevant=False, automated=True,
                notes="Adds another favored enemy/language choice; the RAW tracking/recall benefit remains arena-neutral.",
            ),
            FeatureAudit(
                feature_id="natural-explorer-improvement-6",
                feature_name="Natural Explorer Improvement",
                source_reference="D&D Basic Rules 2014: Ranger 6",
                category="class", combat_relevant=False, automated=True,
                notes="Adds another favored terrain; overland travel benefits remain outside an in-progress Iron Pit fight.",
            ),
        ]
    if level >= 7:
        rows.append(
            FeatureAudit(
                feature_id="steel-will",
                feature_name="Defensive Tactics (Steel Will)",
                source_reference="D&D Basic Rules 2014: Hunter 7",
                category="subclass", combat_relevant=True, automated=True,
                notes=(
                    "Canonical Hunter choice is Steel Will. It reuses universal saving-throw Advantage "
                    "tagged to frightened effects; no Ranger-specific resolver."
                ),
            )
        )
    if level >= 8:
        rows += [
            FeatureAudit(
                feature_id="ability-score-improvement-8",
                feature_name="Ability Score Improvement",
                source_reference="D&D Basic Rules 2014: Ranger 8",
                category="class", combat_relevant=True, automated=True,
                notes=(
                    "Canonical archer progression raises Dexterity from 19 to 20 and Wisdom from 14 to 15; "
                    "shared character math recomputes derived values."
                ),
            ),
            FeatureAudit(
                feature_id="lands-stride",
                feature_name="Land's Stride",
                source_reference="D&D Basic Rules 2014: Ranger 8",
                category="class", combat_relevant=True, automated=True,
                notes=(
                    "Reuses the same shared 2014 Land's Stride binding as Circle of the Land Druid: "
                    "nonmagical Difficult Terrain counter plus save Advantage against magical plant impediments."
                ),
            ),
        ]
    if level >= 10:
        rows += [
            FeatureAudit(
                feature_id="natural-explorer-improvement-10",
                feature_name="Natural Explorer Improvement",
                source_reference="D&D Basic Rules 2014: Ranger 10",
                category="class", combat_relevant=False, automated=True,
                notes="Adds another favored terrain; overland travel benefits remain outside an in-progress Iron Pit fight.",
            ),
            FeatureAudit(
                feature_id="hide-in-plain-sight",
                feature_name="Hide in Plain Sight",
                source_reference="D&D Basic Rules 2014: Ranger 10",
                category="class", combat_relevant=False, automated=False,
                notes=(
                    "Requires one minute of camouflage preparation using natural materials and then a qualifying "
                    "solid surface. The standard open Pit provides neither setup requirement, so Arena AI cannot "
                    "activate the feature; no fake stealth modifier is created."
                ),
            ),
        ]
    return rows


def _level_one() -> CharacterBuildProfile:
    base = _scores()
    species = _species_increases()
    final = base.model_copy(update={"dexterity": 17, "wisdom": 14})
    return CharacterBuildProfile(
        id="build-rowan-ashtrail-2014-l1",
        template_id="rowan-ashtrail-2014-l1",
        character_name="Rowan Ashtrail",
        class_id="ranger", class_name="Ranger", level=1, ruleset="2014",
        subclass_id=None, subclass_name=None, build_id="archer",
        species_id="wood-elf", species_name="Wood Elf",
        background_id="outlander", background_name="Outlander",
        base_ability_scores=base, species_increases=species,
        advancement_increases=[], final_ability_scores=final,
        class_equipment_option="package",
        class_equipment=["Leather Armor", "Shortsword", "Shortsword", "Explorer's Pack", "Longbow", "20 Arrows"],
        background_equipment_option="package",
        background_equipment=["Staff", "Hunting Trap", "Traveler's Clothes", "10 gp"],
        skill_proficiencies=["Athletics", "Survival", "Perception", "Stealth", "Insight", "Investigation"],
        weapon_masteries=[], combat_loadout_kind="dual-wield",
        feature_audits=_audits(1),
        source_references=[
            "D&D Basic Rules 2014: Wood Elf",
            "D&D Basic Rules 2014: Outlander",
            "D&D Basic Rules 2014: Ranger",
            "D&D Basic Rules 2014: Equipment",
        ],
    )


def build_rowan_ashtrail_2014_profile(level: int) -> CharacterBuildProfile:
    try:
        if level not in range(1, 11):
            raise ValueError("2014 Rowan profile currently covers levels 1 through 10.")
        profile = _level_one()
        if level == 1:
            return profile
        data = advance_profile_data(profile, 2)
        data.update(
            fighting_style="Archery",
            fighting_styles=["Archery"],
            feature_audits=_audits(2),
            source_references=[*profile.source_references, "D&D Basic Rules 2014: Ranger 2"],
        )
        profile = CharacterBuildProfile(**data)
        if level == 2:
            return profile
        data = advance_profile_data(profile, 3)
        data.update(
            subclass_id="hunter",
            subclass_name="Hunter",
            feature_audits=_audits(3),
            source_references=[
                *profile.source_references,
                "D&D Basic Rules 2014: Ranger 3",
                "D&D Basic Rules 2014: Hunter 3",
            ],
        )
        profile = CharacterBuildProfile(**data)
        if level == 3:
            return profile
        increase = AbilityIncrease(ability="dexterity", amount=2)
        data = advance_profile_data(profile, 4)
        data.update(
            advancement_increases=[*profile.advancement_increases, increase],
            final_ability_scores=_apply(profile.final_ability_scores, [increase]),
            feature_audits=_audits(4),
            source_references=[*profile.source_references, "D&D Basic Rules 2014: Ranger 4"],
        )
        profile = CharacterBuildProfile(**data)
        if level == 4:
            return profile
        data = advance_profile_data(profile, 5)
        data.update(
            feature_audits=_audits(5),
            source_references=[*profile.source_references, "D&D Basic Rules 2014: Ranger 5"],
        )
        profile = CharacterBuildProfile(**data)
        if level == 5:
            return profile
        data = advance_profile_data(profile, 6)
        data.update(
            feature_audits=_audits(6),
            source_references=[*profile.source_references, "D&D Basic Rules 2014: Ranger 6"],
        )
        profile = CharacterBuildProfile(**data)
        if level == 6:
            return profile
        data = advance_profile_data(profile, 7)
        data.update(
            feature_audits=_audits(7),
            source_references=[
                *profile.source_references,
                "D&D Basic Rules 2014: Ranger 7",
                "D&D Basic Rules 2014: Hunter 7",
            ],
        )
        profile = CharacterBuildProfile(**data)
        if level == 7:
            return profile
        increases = [
            AbilityIncrease(ability="dexterity", amount=1),
            AbilityIncrease(ability="wisdom", amount=1),
        ]
        data = advance_profile_data(profile, 8)
        data.update(
            advancement_increases=[*profile.advancement_increases, *increases],
            final_ability_scores=_apply(profile.final_ability_scores, increases),
            feature_audits=_audits(8),
            source_references=[*profile.source_references, "D&D Basic Rules 2014: Ranger 8"],
        )
        profile = CharacterBuildProfile(**data)
        if level == 8:
            return profile
        data = advance_profile_data(profile, 9)
        data.update(
            feature_audits=_audits(9),
            source_references=[*profile.source_references, "D&D Basic Rules 2014: Ranger 9"],
        )
        profile = CharacterBuildProfile(**data)
        if level == 9:
            return profile
        data = advance_profile_data(profile, 10)
        data.update(
            feature_audits=_audits(10),
            source_references=[*profile.source_references, "D&D Basic Rules 2014: Ranger 10"],
        )
        return CharacterBuildProfile(**data)
    except Exception:
        logger.exception("Failed to compile 2014 Rowan Ashtrail profile at level %s.", level)
        raise
