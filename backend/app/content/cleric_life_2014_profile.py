from __future__ import annotations

import logging

from app.content.canonical_progression import advance_profile_data
from app.domain.character_builds import AbilityIncrease, AbilityScores, CharacterBuildProfile, FeatureAudit

logger = logging.getLogger(__name__)


def _audit(
    feature_id: str,
    feature_name: str,
    category: str,
    *,
    source: str,
    automated: bool = True,
    combat_relevant: bool = True,
    weapon_id: str | None = None,
    notes: str | None = None,
) -> FeatureAudit:
    return FeatureAudit(
        feature_id=feature_id,
        feature_name=feature_name,
        source_reference=source,
        category=category,
        combat_relevant=combat_relevant,
        automated=automated,
        runtime_attack_weapon_id=weapon_id,
        notes=notes,
    )


def _base_scores() -> AbilityScores:
    # One permanent 2014 Seraphine base: standard array, Wisdom/Constitution first.
    return AbilityScores(
        strength=13,
        dexterity=10,
        constitution=14,
        intelligence=8,
        wisdom=15,
        charisma=12,
    )


def _species_increases() -> list[AbilityIncrease]:
    # 2014 Hill Dwarf: Dwarf +2 Constitution, Hill Dwarf +1 Wisdom.
    return [
        AbilityIncrease(ability="constitution", amount=2),
        AbilityIncrease(ability="wisdom", amount=1),
    ]


def _advancement_delta(level: int) -> list[AbilityIncrease]:
    """Return only the ASI gained at this exact level."""
    milestones = {
        4: ("wisdom", 2),
        8: ("wisdom", 2),
        12: ("constitution", 2),
        16: ("constitution", 2),
        19: ("strength", 2),
    }
    choice = milestones.get(level)
    return [] if choice is None else [AbilityIncrease(ability=choice[0], amount=choice[1])]


def _apply_increases(scores: AbilityScores, increases: list[AbilityIncrease]) -> AbilityScores:
    values = scores.model_dump()
    for increase in increases:
        values[increase.ability] += increase.amount
    return AbilityScores(**values)

def _feature_audits(level: int) -> list[FeatureAudit]:
    cleric = "D&D Basic Rules 2014: Cleric"
    life = "D&D Basic Rules 2014: Life Domain"
    dwarf = "D&D Basic Rules 2014: Hill Dwarf"
    equipment = "D&D Basic Rules 2014: Equipment"
    audits = [
        _audit("hill-dwarf-constitution", "Dwarf Ability Score Increase", "species", source=dwarf),
        _audit("hill-dwarf-wisdom", "Hill Dwarf Ability Score Increase", "species", source=dwarf),
        _audit(
            "dwarven-resilience",
            "Dwarven Resilience",
            "species",
            source=dwarf,
            automated=False,
            notes=(
                "Poison resistance exists in the universal damage engine; contextual Advantage "
                "on saving throws against poison must bind through the universal contextual-save primitive."
            ),
        ),
        _audit("dwarven-toughness", "Dwarven Toughness", "species", source=dwarf),
        _audit("spellcasting", "Spellcasting", "class", source=cleric),
        _audit("life-domain", "Life Domain", "subclass", source=life),
        _audit("life-domain-heavy-armor", "Bonus Proficiency", "subclass", source=life),
        _audit("disciple-of-life", "Disciple of Life", "subclass", source=life),
        _audit("warhammer", "Warhammer", "equipment", source=equipment, weapon_id="warhammer"),
        _audit("scale-mail-shield", "Scale Mail and Shield", "equipment", source=equipment),
    ]
    if level >= 2:
        audits.extend([
            _audit("channel-divinity", "Channel Divinity", "class", source=cleric),
            _audit(
                "turn-undead",
                "Turn Undead",
                "class",
                source=cleric,
                automated=False,
                notes="Awaiting the universal Turned/forced-retreat condition primitive.",
            ),
            _audit(
                "preserve-life",
                "Channel Divinity: Preserve Life",
                "subclass",
                source=life,
                automated=False,
                notes=(
                    "Awaiting universal divisible healing-pool allocation with a half-maximum-HP cap "
                    "and undead/construct exclusions."
                ),
            ),
        ])
    if level >= 4:
        audits.append(_audit("asi-4", "Ability Score Improvement", "class", source=cleric))
    if level >= 5:
        audits.append(_audit(
            "destroy-undead-half",
            "Destroy Undead (CR 1/2)",
            "class",
            source=cleric,
            automated=False,
            notes="Depends on the universal Turn Undead resolution path.",
        ))
    if level >= 6:
        audits.extend([
            _audit("channel-divinity-2", "Channel Divinity (2/rest)", "class", source=cleric),
            _audit("blessed-healer", "Blessed Healer", "subclass", source=life),
        ])
    if level >= 8:
        audits.extend([
            _audit("asi-8", "Ability Score Improvement", "class", source=cleric),
            _audit(
                "destroy-undead-1",
                "Destroy Undead (CR 1)",
                "class",
                source=cleric,
                automated=False,
                notes="Depends on the universal Turn Undead resolution path.",
            ),
            _audit(
                "divine-strike",
                "Divine Strike",
                "subclass",
                source=life,
                automated=False,
                notes="Requires audit/binding to a generic once-per-turn weapon-hit damage rider.",
            ),
        ])
    if level >= 10:
        audits.append(_audit(
            "divine-intervention",
            "Divine Intervention",
            "class",
            source=cleric,
            automated=False,
            notes="Requires deterministic Iron Pit policy over the RAW deity-intervention result.",
        ))
    if level >= 11:
        audits.append(_audit(
            "destroy-undead-2",
            "Destroy Undead (CR 2)",
            "class",
            source=cleric,
            automated=False,
            notes="Depends on the universal Turn Undead resolution path.",
        ))
    if level >= 12:
        audits.append(_audit("asi-12", "Ability Score Improvement", "class", source=cleric))
    if level >= 14:
        audits.extend([
            _audit(
                "destroy-undead-3",
                "Destroy Undead (CR 3)",
                "class",
                source=cleric,
                automated=False,
                notes="Depends on the universal Turn Undead resolution path.",
            ),
            _audit(
                "divine-strike-2d8",
                "Divine Strike (2d8)",
                "subclass",
                source=life,
                automated=False,
                notes="Scaling delta of the level-8 once-per-turn weapon-hit damage rider.",
            ),
        ])
    if level >= 16:
        audits.append(_audit("asi-16", "Ability Score Improvement", "class", source=cleric))
    if level >= 17:
        audits.extend([
            _audit(
                "destroy-undead-4",
                "Destroy Undead (CR 4)",
                "class",
                source=cleric,
                automated=False,
                notes="Depends on the universal Turn Undead resolution path.",
            ),
            _audit(
                "supreme-healing",
                "Supreme Healing",
                "subclass",
                source=life,
                notes="Candidate binding to the existing universal healing-maximize semantic.",
            ),
        ])
    if level >= 18:
        audits.append(_audit("channel-divinity-3", "Channel Divinity (3/rest)", "class", source=cleric))
    if level >= 19:
        audits.append(_audit("asi-19", "Ability Score Improvement", "class", source=cleric))
    if level >= 20:
        audits.append(_audit(
            "divine-intervention-improvement",
            "Divine Intervention Improvement",
            "class",
            source=cleric,
            automated=False,
            notes="Requires the same universal Divine Intervention policy as level 10.",
        ))
    return audits


def _level_one_profile() -> CharacterBuildProfile:
    """Construct the one and only 2014 Seraphine base character."""
    base = _base_scores()
    species = _species_increases()
    return CharacterBuildProfile(
        id="build-seraphine-dawnshield-2014-l1",
        template_id="seraphine-dawnshield-2014-l1",
        character_name="Seraphine Dawnshield",
        class_id="cleric",
        class_name="Cleric",
        level=1,
        ruleset="2014",
        subclass_id="life-domain",
        subclass_name="Life Domain",
        build_id="life-healer",
        species_id="hill-dwarf",
        species_name="Hill Dwarf",
        background_id="acolyte",
        background_name="Acolyte",
        base_ability_scores=base,
        species_increases=species,
        advancement_increases=[],
        final_ability_scores=_apply_increases(base, species),
        class_equipment_option="package",
        class_equipment=[
            "Warhammer", "Scale Mail", "Light Crossbow", "20 Bolts",
            "Priest's Pack", "Shield", "Holy Symbol",
        ],
        background_equipment_option="package",
        background_equipment=[
            "Holy Symbol", "Prayer Book", "5 Sticks of Incense",
            "Vestments", "Common Clothes", "15 gp",
        ],
        skill_proficiencies=["Insight", "Religion", "Medicine", "Persuasion"],
        weapon_masteries=[],
        combat_loadout_kind=None,
        feature_audits=_feature_audits(1),
        source_references=[
            "D&D Basic Rules 2014: Hill Dwarf",
            "D&D Basic Rules 2014: Acolyte",
            "D&D Basic Rules 2014: Cleric",
            "D&D Basic Rules 2014: Life Domain",
            "D&D Basic Rules 2014: Equipment",
        ],
    )


def _advance_one_level(previous: CharacterBuildProfile, next_level: int) -> CharacterBuildProfile:
    """Advance the existing Seraphine exactly one level; never rebuild a fresh snapshot."""
    data = advance_profile_data(previous, next_level)
    asi_delta = _advancement_delta(next_level)
    data.update(
        advancement_increases=[*previous.advancement_increases, *asi_delta],
        final_ability_scores=_apply_increases(previous.final_ability_scores, asi_delta),
        feature_audits=[*previous.feature_audits, *_feature_audits(next_level)[len(_feature_audits(next_level - 1)):]],
        source_references=[
            *previous.source_references,
            f"D&D Basic Rules 2014: Cleric level {next_level}",
        ],
    )
    return CharacterBuildProfile(**data)


def build_seraphine_dawnshield_2014_profile(level: int) -> CharacterBuildProfile:
    """Level one persistent 2014 Seraphine forward from level 1 to the requested level."""
    try:
        if level not in range(1, 21):
            raise ValueError("2014 Seraphine profile covers levels 1 through 20.")
        profile = _level_one_profile()
        for next_level in range(2, level + 1):
            profile = _advance_one_level(profile, next_level)
        return profile
    except Exception:
        logger.exception("Failed to advance 2014 Seraphine Dawnshield to level %s", level)
        raise
