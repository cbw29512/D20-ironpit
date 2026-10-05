"""2014 traits that cannot change an Iron Pit combat outcome.

Flyby stays listed: the pit forbids leaving an existing melee engagement, and Flyby
does not grant a leave-reach opportunity-attack exemption. Sunlight Sensitivity is
not listed; it binds to the shared sunlight environment-context reaction.
"""
from __future__ import annotations

ARENA_NEUTRAL_TRAITS_2014 = frozenset({
    "Amphibious", "Beast of Burden", "Echolocation", "False Appearance", "Flyby", "Hold Breath",
    "Ice Walk", "Illumination", "Keen Hearing", "Keen Hearing and Smell", "Keen Hearing and Sight",
    "Keen Sight", "Keen Sight and Smell", "Keen Smell", "Labyrinthine Recall", "Mimicry",
    "Running Leap", "Snow Camouflage", "Stone Camouflage", "Spider Climb", "Water Breathing",
    "Underwater Camouflage", "Web Sense", "Web Walker", "Rejuvenation", "Hellish Rejuvenation",
})
