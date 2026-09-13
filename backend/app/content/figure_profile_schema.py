from __future__ import annotations

import logging
from typing import Literal, TypedDict

logger = logging.getLogger(__name__)

FigureForm = Literal[
    "aquatic-mammal", "aquatic-reptile", "bat", "bear", "bird", "brute", "centipede", "crab", "fish", "frog",
    "gargoyle", "hippogriff", "hoofed", "humanoid", "insect", "plant", "primate", "pterosaur", "quadruped",
    "reptile", "scorpion", "snake", "spider", "swarm", "theropod", "weapon", "winged-insect",
]


class FigureProfile(TypedDict):
    form: FigureForm
    detail: str


def figure_profile(form: FigureForm, detail: str) -> FigureProfile:
    try:
        return {"form": form, "detail": detail}
    except Exception:
        logger.exception("Failed to build figure profile for %s/%s.", form, detail)
        raise
