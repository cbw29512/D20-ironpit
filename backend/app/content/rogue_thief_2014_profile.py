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
    milestones = (
        (4, "dexterity", 2), (8, "dexterity", 2),
        (10, "charisma", 1), (10, "wisdom", 1),
        (12, "constitution", 2), (16, "constitution", 2), (19, "constitution", 2),
    )
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
    if level >= 11:
        audits.append(_audit(
            "reliable-talent", "Reliable Talent", "class", combat=False, automated=False,
            notes=("Audited RAW. The standard arena currently executes no qualifying proficient "
                   "ability check, so no runtime roll-floor primitive is exercised by this snapshot."),
        ))
    if level >= 12:
        audits.append(_audit(
            "ability-score-improvement-l12", "Ability Score Improvement (+2 Constitution)", "class",
            notes="Canonical Iron Pit progression decision: Constitution 14→16 for survivability and Constitution checks/saves.",
        ))
    if level >= 13:
        audits.append(_audit(
            "use-magic-device", "Use Magic Device", "subclass", combat=False, automated=False,
            notes="Audited RAW; arena-inert while Mara uses the canonical mundane loadout.",
        ))
    if level >= 14:
        audits.append(_audit(
            "blindsense", "Blindsense", "class", combat=False, automated=False,
            notes=(
                "Audited RAW: Blindsense provides location awareness within 10 feet while Mara can hear; "
                "it does not grant sight. The certified arena currently has no Hide/location-guess loop "
                "or certified opponent path that creates unresolved creature-location state, so no runtime "
                "awareness primitive is exercised by this snapshot."
            ),
        ))
    if level >= 15:
        audits.append(_audit(
            "slippery-mind", "Slippery Mind", "class",
            notes="Uses the existing saving-throw proficiency compiler; Wisdom proficiency begins at level 15.",
        ))
    if level >= 16:
        audits.append(_audit(
            "ability-score-improvement-l16", "Ability Score Improvement (+2 Constitution)", "class",
            notes="Canonical Iron Pit progression decision: Constitution 16→18 for survivability and Constitution checks/saves.",
        ))
    if level >= 17:
        audits.append(_audit(
            "thiefs-reflexes", "Thief's Reflexes", "subclass",
            notes="Uses the shared first-round extra-turn scheduler at Mara's rolled initiative count minus 10.",
        ))
    return audits


def build_mara_quickstep_2014_profile(level: int) -> CharacterBuildProfile:
    try:
        if level not in range(1, 18): raise ValueError("2014 Mara candidate profile covers levels 1 through 17.")
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
            weapon_masteries=[], combat_loadout_kind="dual-wield",
            feature_audits=_audits(level), source_references=[
                "D&D Basic Rules 2014: Human", "D&D Basic Rules 2014: Rogue",
                "D&D Basic Rules 2014: Thief", "D&D Basic Rules 2014: Criminal",
                "D&D Basic Rules 2014: Equipment",
            ],
        )
    except Exception:
        logger.exception("Failed to compile 2014 Mara Quickstep profile at level %s", level)
        raise
