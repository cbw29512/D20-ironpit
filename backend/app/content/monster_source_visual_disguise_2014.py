"""Exact 2014 source proof for visual disguises; no runtime identity dispatch.

A printed illusion can conceal the appearance needed to trigger another
source's visual passive. Runtime action, dismissal, inspection and owner-death
lifecycle are provided by shared visual-disguise primitives; admission may
recognize this Action only when the complete source proof below succeeds.
"""
from __future__ import annotations

from dataclasses import dataclass
import logging
import re

from app.content.monster_source_2014 import SourceMonster2014
from app.content.monster_source_sections_2014 import source_sections_2014

logger = logging.getLogger(__name__)

_ILLUSION = re.compile(
    r"The hag covers herself and anything she is wearing or carrying with a "
    r"magical illusion that makes her look like an ugly creature of her general "
    r"size and humanoid shape\. The effect ends if the hag takes a bonus "
    r"action to end it or if she dies\. The changes wrought by this effect "
    r"fail to hold up to physical inspection\. For example, the hag could "
    r"appear to have no claws, but someone touching her hand might feel the "
    r"claws\. Otherwise, a creature must take an action to visually inspect "
    r"the illusion and succeed on a DC (?P<dc>\d+) Intelligence "
    r"\(Investigation\) check to discern that the hag is disguised\.",
    flags=re.IGNORECASE,
)


@dataclass(frozen=True)
class VisualDisguiseSourceFacts:
    source_name: str
    activation_cost: str
    magical_illusion: bool
    conceals_true_form: bool
    ends_on_owner_bonus_action: bool
    ends_if_owner_dead: bool
    physical_inspection_inconsistent: bool
    investigation_action_cost: str
    investigation_ability: str
    investigation_skill: str
    investigation_dc: int
    # Successful Investigation reveals a disguise, NOT the form behind it.
    investigation_reveals_true_form: bool = False


def source_proven_visual_disguise_2014(
    monster: SourceMonster2014,
) -> VisualDisguiseSourceFacts | None:
    """Strictly bind the complete action text without recognizing combat names."""
    try:
        name = "Illusory Appearance"  # Printed heading selector, not runtime dispatch.
        if name not in monster.action_names:
            return None
        printed = source_sections_2014(
            monster.source_actions, include_continuations=True,
        ).get(name, "")
        printed = " ".join(printed.replace("’", "'").split())
        match = _ILLUSION.fullmatch(printed)
        if match is None:
            return None
        dc = int(match["dc"])
        if not 1 <= dc <= 40:
            return None
        return VisualDisguiseSourceFacts(
            source_name=name, activation_cost="action",
            magical_illusion=True, conceals_true_form=True,
            ends_on_owner_bonus_action=True, ends_if_owner_dead=True,
            physical_inspection_inconsistent=True,
            investigation_action_cost="action", investigation_ability="intelligence",
            investigation_skill="investigation", investigation_dc=dc,
        )
    except Exception:
        logger.exception("Failed 2014 visual-disguise source proof for %s", monster.id)
        raise
