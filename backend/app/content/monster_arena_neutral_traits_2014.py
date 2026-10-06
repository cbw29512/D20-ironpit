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
"""
from __future__ import annotations

ARENA_NEUTRAL_TRAITS_2014 = frozenset({
    "Siege Monster", "Amorphous", "Standing Leap", "Amphibious", "Beast of Burden", "Echolocation", "False Appearance", "Flyby", "Hold Breath",
    "Ice Walk", "Illumination", "Keen Hearing", "Keen Hearing and Smell", "Keen Hearing and Sight",
    "Keen Sight", "Keen Sight and Smell", "Keen Smell", "Labyrinthine Recall", "Limited Amphibiousness",
    "Mimicry", "Earth Glide", "Running Leap", "Shark Telepathy", "Snow Camouflage", "Stone Camouflage",
    "Spider Climb", "Treasure Sense", "Tunneler", "Water Breathing", "Devil's Sight",
    "Underwater Camouflage", "Web Sense", "Web Walker", "Rejuvenation", "Hellish Rejuvenation",
    "Wakeful", "Ethereal Jaunt", "Incorporeal Movement",
})
