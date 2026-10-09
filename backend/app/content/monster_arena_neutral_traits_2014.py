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

ARENA_NEUTRAL_TRAITS_2014 = frozenset({
    "Siege Monster", "Amorphous", "Standing Leap", "Amphibious", "Beast of Burden", "Echolocation", "False Appearance", "Flyby", "Hold Breath",
    "Ice Walk", "Illumination", "Keen Hearing", "Keen Hearing and Smell", "Keen Hearing and Sight",
    "Keen Sight", "Keen Sight and Smell", "Keen Smell", "Labyrinthine Recall", "Limited Amphibiousness",
    "Mimicry", "Earth Glide", "Running Leap", "Shark Telepathy", "Snow Camouflage", "Stone Camouflage",
    "Spider Climb", "Treasure Sense", "Tunneler", "Water Breathing", "Devil's Sight",
    "Underwater Camouflage", "Web Sense", "Web Walker", "Rejuvenation", "Hellish Rejuvenation",
    "Wakeful", "Ethereal Jaunt", "Incorporeal Movement", "Immutable Form",
})

import logging

from app.content.monster_source_2014 import SourceMonster2014

logger = logging.getLogger(__name__)


def verified_arena_inert_trait_2014(monster: SourceMonster2014, trait_name: str) -> bool:
    """Accept only the pinned noncombat summoner/quarry tracking semantics."""
    try:
        if trait_name != "Faultless Tracker" or trait_name not in monster.trait_names:
            return False
        source = monster.source_traits or ""
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
