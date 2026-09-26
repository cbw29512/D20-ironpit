from __future__ import annotations

import logging

from app.content.sorcerer_draconic_2014_audits import build_sorcerer_draconic_2014_feature_audits
from app.domain.character_builds import AbilityIncrease, AbilityScores, CharacterBuildProfile

logger = logging.getLogger(__name__)


def build_nyra_emberveil_2014_profile(level: int) -> CharacterBuildProfile:
    try:
        if level != 1:
            raise ValueError("2014 Nyra profile currently covers level 1.")
        base = AbilityScores(strength=8, dexterity=12, constitution=10, intelligence=13, wisdom=14, charisma=15)
        species = [
            AbilityIncrease(ability="charisma", amount=2),
            AbilityIncrease(ability="dexterity", amount=1),
            AbilityIncrease(ability="constitution", amount=1),
        ]
        final = AbilityScores(strength=8, dexterity=13, constitution=11, intelligence=13, wisdom=14, charisma=17)
        return CharacterBuildProfile(
            id="build-nyra-emberveil-2014-l1",
            template_id="nyra-emberveil-2014-l1",
            character_name="Nyra Emberveil",
            class_id="sorcerer", class_name="Sorcerer", level=1, ruleset="2014",
            subclass_id="draconic-bloodline", subclass_name="Draconic Bloodline", build_id="fire-damage",
            species_id="half-elf", species_name="Half-Elf",
            background_id="charlatan", background_name="Charlatan",
            base_ability_scores=base, species_increases=species,
            advancement_increases=[], final_ability_scores=final,
            class_equipment_option="package",
            class_equipment=["Light Crossbow", "20 Bolts", "Component Pouch", "Dungeoneer's Pack", "Dagger", "Dagger"],
            background_equipment_option="package",
            background_equipment=["Fine Clothes", "Disguise Kit", "Tools of the Con", "15 gp"],
            skill_proficiencies=["Arcana", "Persuasion", "Perception", "Stealth", "Deception", "Sleight of Hand"],
            weapon_masteries=[], combat_loadout_kind=None,
            feature_audits=build_sorcerer_draconic_2014_feature_audits(1),
            source_references=[
                "D&D Basic Rules 2014: Half-Elf",
                "D&D Basic Rules 2014: Charlatan",
                "D&D Basic Rules 2014: Sorcerer",
                "D&D Basic Rules 2014: Draconic Bloodline",
                "D&D Basic Rules 2014: Equipment",
            ],
        )
    except Exception:
        logger.exception("Failed to compile 2014 Nyra Emberveil profile at level %s.", level)
        raise
