from __future__ import annotations

import logging

from app.domain.character_builds import AbilityIncrease, AbilityScores, CharacterBuildProfile, FeatureAudit

logger = logging.getLogger(__name__)
_ABILITIES = ("strength", "dexterity", "constitution", "intelligence", "wisdom", "charisma")


def _audit(feature_id: str, feature_name: str, category: str, *, source: str,
           weapon_id: str | None = None) -> FeatureAudit:
    return FeatureAudit(feature_id=feature_id, feature_name=feature_name, source_reference=source,
                        category=category, combat_relevant=True, automated=True,
                        runtime_attack_weapon_id=weapon_id)


def _base_scores() -> AbilityScores:
    return AbilityScores(strength=15, dexterity=13, constitution=14, intelligence=8, wisdom=12, charisma=10)


def _species_increases() -> list[AbilityIncrease]:
    return [AbilityIncrease(ability=ability, amount=1) for ability in _ABILITIES]


def _advancement_increases(level: int) -> list[AbilityIncrease]:
    increases: list[AbilityIncrease] = []
    milestones = (
        (4, "strength", 2), (6, "strength", 2), (8, "dexterity", 1), (8, "constitution", 1),
        (12, "constitution", 2), (14, "dexterity", 1), (14, "constitution", 1),
        (16, "dexterity", 2), (19, "constitution", 1), (19, "wisdom", 1),
    )
    for required_level, ability, amount in milestones:
        if level >= required_level:
            increases.append(AbilityIncrease(ability=ability, amount=amount))
    return increases


def _final_scores(base: AbilityScores, species: list[AbilityIncrease],
                  advancements: list[AbilityIncrease]) -> AbilityScores:
    values = base.model_dump()
    for increase in [*species, *advancements]:
        values[increase.ability] += increase.amount
    return AbilityScores(**values)


def _feature_audits(level: int) -> list[FeatureAudit]:
    fighter = "D&D Basic Rules 2014: Fighter"; champion = "D&D Basic Rules 2014: Champion"
    audits = [
        _audit("human-ability-increase", "Human Ability Score Increase", "species", source="D&D Basic Rules 2014: Human"),
        _audit("defense-style", "Defense Fighting Style", "class", source=fighter),
        _audit("second-wind", "Second Wind", "class", source=fighter),
        _audit("chain-mail", "Chain Mail", "equipment", source="D&D Basic Rules 2014: Equipment"),
        _audit("greatsword", "Greatsword", "equipment", source="D&D Basic Rules 2014: Equipment", weapon_id="greatsword"),
        _audit("longbow", "Longbow", "equipment", source="D&D Basic Rules 2014: Equipment", weapon_id="longbow"),
        _audit("soldier-athletics", "Soldier Athletics Proficiency", "background", source="D&D Basic Rules 2014: Soldier"),
    ]
    if level >= 2: audits.append(_audit("action-surge", "Action Surge", "class", source=fighter))
    if level >= 3: audits.append(_audit("improved-critical", "Improved Critical", "subclass", source=champion))
    if level >= 5: audits.append(_audit("extra-attack", "Extra Attack", "class", source=fighter))
    if level >= 7: audits.append(_audit("remarkable-athlete", "Remarkable Athlete", "subclass", source=champion))
    if level >= 9: audits.append(_audit("indomitable", "Indomitable", "class", source=fighter))
    if level >= 10: audits.append(_audit("additional-fighting-style", "Additional Fighting Style", "subclass", source=champion))
    if level >= 11: audits.append(_audit("extra-attack-2", "Extra Attack (2)", "class", source=fighter))
    if level >= 13: audits.append(_audit("indomitable-2", "Indomitable (two uses)", "class", source=fighter))
    if level >= 15: audits.append(_audit("superior-critical", "Superior Critical", "subclass", source=champion))
    if level >= 17:
        audits.extend([_audit("action-surge-2", "Action Surge (two uses)", "class", source=fighter),
                       _audit("indomitable-3", "Indomitable (three uses)", "class", source=fighter)])
    if level >= 18: audits.append(_audit("survivor", "Survivor", "subclass", source=champion))
    if level >= 20: audits.append(_audit("extra-attack-3", "Extra Attack (3)", "class", source=fighter))
    return audits


def build_karnok_stoneward_2014_profile(level: int) -> CharacterBuildProfile:
    try:
        if level not in range(1, 21):
            raise ValueError("2014 Karnok profile certification covers levels 1 through 20.")
        base = _base_scores(); species = _species_increases(); advancements = _advancement_increases(level)
        styles = ["Defense", *(["Archery"] if level >= 10 else [])]
        return CharacterBuildProfile(
            id=f"build-karnok-stoneward-2014-l{level}", template_id=f"karnok-stoneward-2014-l{level}",
            character_name="Karnok Stoneward", class_id="fighter", class_name="Fighter", level=level,
            ruleset="2014", subclass_id="champion" if level >= 3 else None,
            subclass_name="Champion" if level >= 3 else None, build_id="champion-greatsword",
            species_id="human", species_name="Human", background_id="soldier", background_name="Soldier",
            base_ability_scores=base, species_increases=species, advancement_increases=advancements,
            final_ability_scores=_final_scores(base, species, advancements), class_equipment_option="package",
            class_equipment=["Chain Mail", "Greatsword", "Longbow", "20 Arrows", "Two Handaxes", "Explorer's Pack"],
            background_equipment_option="package",
            background_equipment=["Rank Insignia", "Trophy", "Gaming Set", "Common Clothes", "10 gp"],
            skill_proficiencies=["Athletics", "Intimidation", "Perception", "Survival"], weapon_masteries=[],
            fighting_style=styles[0], fighting_styles=styles, combat_loadout_kind="two-handed",
            feature_audits=_feature_audits(level), source_references=[
                "D&D Basic Rules 2014: Human", "D&D Basic Rules 2014: Fighter",
                "D&D Basic Rules 2014: Champion", "D&D Basic Rules 2014: Soldier",
                "D&D Basic Rules 2014: Equipment",
            ],
        )
    except Exception:
        logger.exception("Failed to compile 2014 Karnok build profile at level %s", level)
        raise
