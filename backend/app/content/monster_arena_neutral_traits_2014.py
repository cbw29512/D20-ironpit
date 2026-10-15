"""2014 traits that cannot change an Iron Pit combat outcome.

Flyby stays listed: the pit forbids leaving an existing melee engagement, and Flyby
does not grant a leave-reach opportunity-attack exemption. Sunlight Sensitivity is
not listed; it binds to the shared sunlight environment-context reaction.
Devil's Sight stays listed: the standard Pit has no Dim Light/Darkness state and no
Darkness-producing combat effect, so magical-darkness sight cannot change a fight.
Wakeful stays listed: Iron Pit fights do not start with a sleeper head, so a second
awake head cannot change surprise or sleep. Two Heads save-Advantage is bound separately.
Ethereal Jaunt and Incorporeal Movement stay listed because the Pit forbids entering
an ethereal/incorporeal movement state; those movement-only benefits never activate.
Earth Glide, Tunneler, and Treasure Sense stay listed: the Pit has no destructible
earth/rock or hidden metal/treasure for those traits to act on.
Immutable Form stays listed while the supported combat surface has no hostile form-alter
effect. Existing replacement-form support changes only the acting combatant's own form.
"""
from __future__ import annotations

import logging

from app.content.monster_source_2014 import SourceMonster2014
from app.content.monster_informational_trait_proofs_2014 import verified_nonactionable_information_2014

logger = logging.getLogger(__name__)

ARENA_NEUTRAL_TRAITS_2014 = frozenset({
    "Siege Monster", "Amorphous", "Standing Leap", "Amphibious", "Beast of Burden", "Echolocation", "False Appearance", "Flyby", "Hold Breath",
    "Ice Walk", "Illumination", "Keen Hearing", "Keen Hearing and Smell", "Keen Hearing and Sight",
    "Keen Sight", "Keen Sight and Smell", "Keen Smell", "Labyrinthine Recall", "Limited Amphibiousness",
    "Mimicry", "Earth Glide", "Running Leap", "Shark Telepathy", "Snow Camouflage", "Stone Camouflage",
    "Spider Climb", "Treasure Sense", "Tunneler", "Water Breathing", "Devil's Sight",
    "Underwater Camouflage", "Web Sense", "Web Walker", "Rejuvenation", "Hellish Rejuvenation",
    "Wakeful", "Ethereal Jaunt", "Incorporeal Movement", "Immutable Form",
})

def verified_arena_inert_trait_2014(monster: SourceMonster2014, trait_name: str) -> bool:
    """Accept only the pinned noncombat summoner/quarry tracking semantics."""
    try:
        if trait_name not in monster.trait_names:
            return False
        source = monster.source_traits or ""
        # Context-driven exclusion: this trait only operates underwater, a
        # context absent from the standard Iron Pit. Keep the printed trait.
        if trait_name == "Mucous Cloud":
            return (
                "<strong>Mucous Cloud.</strong>" in source
                and "While underwater" in source
                and "transformative mucus" in source
            )
        # Source-verified informational traits never grant combat coordinates,
        # actions, saves or targeting. Names validate provenance only.
        informational_clauses = {
            "Detect Life": (
                "<strong>Detect Life.</strong>",
                "general direction",
                "exact locations",
            ),
            "Shielded Mind": (
                "<strong>Shielded Mind.</strong>",
                "immune to scrying",
                "sense its emotions",
                "read its thoughts",
                "detect its location",
            ),
        }
        if trait_name in informational_clauses:
            folded = source.casefold()
            return all(clause.casefold() in folded for clause in informational_clauses[trait_name])
        if trait_name == "Sense Magic":
            # This only reports magic's presence. It never grants visibility,
            # target location, Advantage, a save, or a combat action.
            # Isolate the printed paragraph: no other trait may prove it.
            from app.content.monster_source_sections_2014 import source_sections_2014

            printed = source_sections_2014(source).get("Sense Magic", "")
            normalized = printed.casefold().replace("’", "'")
            return all(clause in normalized for clause in (
                "senses magic within 120 feet",
                "at will",
                "detect magic",
                "isn't itself magical",
            ))
        # Source-verified absent-environment clauses.
        # Keep these separate from any attack or active combat-effect resolver.
        if trait_name in {"Water Susceptibility", "Sunlight Weakness"}:
            from app.content.monster_source_sections_2014 import source_sections_2014

            printed = source_sections_2014(source).get(trait_name, "").casefold()
            phrases = {
                "Water Susceptibility": (
                    "moves in water", "gallon of water", "1 cold damage",
                ),
                "Sunlight Weakness": (
                    "while in sunlight", "disadvantage on attack rolls",
                    "ability checks", "saving throws",
                ),
            }
            return all(phrase in printed for phrase in phrases[trait_name])
        # Pinned source must prove both the printed trait and its
        # arena-inert semantics. Other effects remain blocked independently.
        additional_inert_clauses = {
            "Elemental Demise": ("dies", "disintegrates"),
            "Divine Awareness": ("hears", "lie"),
            "Speak with Beasts and Plants": ("communicate", "beasts", "plants"),
            "Tree Stride": ("tree", "movement"),
            "Ethereal Sight": ("ethereal plane",),
            "Telepathic Bond": ("telepathically",),
            "Limited Telepathy": ("telepathically",),
        }
        if trait_name in additional_inert_clauses:
            heading = f"<strong>{trait_name}.</strong>"
            match_start = source.casefold().find(heading.casefold())
            if match_start < 0:
                return False
            remainder = source[match_start + len(heading):]
            next_heading = remainder.find("<strong>")
            clause = (remainder[:next_heading] if next_heading >= 0 else remainder).casefold()
            return all(token in clause for token in additional_inert_clauses[trait_name])
        if verified_nonactionable_information_2014(monster, trait_name):
            return True
        if trait_name != "Faultless Tracker":
            return False
        clauses = (
            "<strong>Faultless Tracker.</strong>",
            "given a quarry by its summoner",
            "knows the direction and distance to its quarry",
            "same plane of existence",
            "knows the location of its summoner",
        )
        return all(clause in source for clause in clauses)
    except Exception:
        logger.exception("2014 noncombat tracking classification failed for %s.", monster.name)
        raise
