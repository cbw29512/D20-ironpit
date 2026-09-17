from __future__ import annotations

import logging

from app.domain.character_builds import AbilityIncrease, AbilityScores, CharacterBuildProfile, FeatureAudit

logger = logging.getLogger(__name__)
_ABILITIES = ("strength", "dexterity", "constitution", "intelligence", "wisdom", "charisma")


def _audit(feature_id: str, name: str, category: str, *, combat: bool = True, automated: bool = True,
           weapon_id: str | None = None, notes: str | None = None) -> FeatureAudit:
    source = "D&D Basic Rules 2014: Thief" if category == "subclass" else "D&D Basic Rules 2014: Rogue"
    return FeatureAudit(feature_id=feature_id, feature_name=name, source_reference=source,
                        category=category, combat_relevant=combat, automated=automated,
                        runtime_attack_weapon_id=weapon_id, notes=notes)


def _base() -> AbilityScores:
    return AbilityScores(strength=8, dexterity=15, constitution=13, intelligence=10, wisdom=12, charisma=14)


def _species() -> list[AbilityIncrease]:
    return [AbilityIncrease(ability=ability, amount=1) for ability in _ABILITIES]


def _advancements(level: int) -> list[AbilityIncrease]:
    milestones = ((4, "dexterity", 2), (8, "dexterity", 2), (10, "charisma", 1), (10, "wisdom", 1))
    return [AbilityIncrease(ability=ability, amount=amount)
            for required, ability, amount in milestones if level >= required]


def _final(base: AbilityScores, species: list[AbilityIncrease], advances: list[AbilityIncrease]) -> AbilityScores:
    values = base.model_dump()
    for increase in [*species, *advances]: values[increase.ability] += increase.amount
    return AbilityScores(**values)


def _audits(level: int) -> list[FeatureAudit]:
    audits = [
        _audit("human-ability-increase", "Human Ability Score Increase", "species", combat=False, automated=False),
        _audit("expertise", "Expertise", "class"), _audit("sneak-attack", "Sneak Attack", "class"),
        _audit("rapier", "Rapier", "equipment", weapon_id="rapier"),
        _audit("shortbow", "Shortbow", "equipment", weapon_id="shortbow"),
        _audit("leather-armor", "Leather Armor", "equipment"),
    ]
    if level >= 2: audits.append(_audit("cunning-action", "Cunning Action", "class"))
    if level >= 3:
        audits.extend([
            _audit("fast-hands", "Fast Hands", "subclass", combat=False, automated=False,
                   notes="Trap, lock, Sleight of Hand, and object-use utility is outside the standard arena."),
            _audit("second-story-work", "Second-Story Work", "subclass", combat=False, automated=False,
                   notes="Standard arena terrain does not require climbing or running jumps."),
        ])
    if level >= 5: audits.append(_audit("uncanny-dodge", "Uncanny Dodge", "class"))
    if level >= 6: audits.append(_audit("expertise-2", "Expertise (two additional proficiencies)", "class"))
    if level >= 7: audits.append(_audit("evasion", "Evasion", "class"))
    if level >= 9:
        audits.append(_audit("supreme-sneak", "Supreme Sneak", "subclass", combat=False, automated=False,
                             notes="The open standard arena has no automatic legal Hide position."))
    return audits


def build_mara_quickstep_2014_profile(level: int) -> CharacterBuildProfile:
    try:
        if level not in range(1, 11): raise ValueError("2014 Mara profile covers levels 1 through 10.")
        base = _base(); species = _species(); advances = _advancements(level)
        return CharacterBuildProfile(
            id=f"build-mara-quickstep-2014-l{level}", template_id=f"mara-quickstep-2014-l{level}",
            character_name="Mara Quickstep", class_id="rogue", class_name="Rogue", level=level,
            ruleset="2014", subclass_id="thief" if level >= 3 else None,
            subclass_name="Thief" if level >= 3 else None, build_id="thief-rapier",
            species_id="human", species_name="Human", background_id="criminal", background_name="Criminal",
            base_ability_scores=base, species_increases=species, advancement_increases=advances,
            final_ability_scores=_final(base, species, advances), class_equipment_option="package",
            class_equipment=["Rapier", "Shortbow", "20 Arrows", "Burglar's Pack", "Leather Armor", "Two Daggers", "Thieves' Tools"],
            background_equipment_option="package",
            background_equipment=["Crowbar", "Dark Common Clothes with Hood", "Pouch", "15 gp"],
            skill_proficiencies=["Acrobatics", "Deception", "Investigation", "Perception", "Persuasion", "Stealth"],
            weapon_masteries=[], combat_loadout_kind="finesse-ranged",
            feature_audits=_audits(level), source_references=[
                "D&D Basic Rules 2014: Human", "D&D Basic Rules 2014: Rogue",
                "D&D Basic Rules 2014: Thief", "D&D Basic Rules 2014: Criminal",
                "D&D Basic Rules 2014: Equipment",
            ],
        )
    except Exception:
        logger.exception("Failed to compile 2014 Mara Quickstep profile at level %s", level)
        raise
