"""Source proofs for 2014 Actions that yield only out-of-arena information.

An information-only or source-proven equipment-only Action stays printed; it is not cast
in Iron Pit and never acquires a fabricated combat roll, resource, or buff.
These checks classify *source text*, not combat resolution by ability name.
"""
from __future__ import annotations

import logging

from app.content.monster_equipment_only_action_2014 import (
    verified_arena_inert_equipment_action_2014,
)
from app.content.monster_source_2014 import SourceMonster2014
from app.content.monster_source_sections_2014 import source_sections_2014
from app.content.monster_read_thoughts_neutral_2014 import (
    source_proven_noncombat_read_thoughts_2014,
)

logger = logging.getLogger(__name__)

# Whole, inspected printed clauses. Extra combat-effective riders must fail
# closed instead of inheriting a permissive name-based exclusion.
_NONCOMBAT_ACTION_CLAUSES_2014 = {
    "Create Food and Water": (
        "The spectator magically creates enough food and water to sustain itself for 24 hours."
    ),
    "Heart Sight": (
        "The sprite touches a creature and magically knows the creature's current "
        "emotional state. If the target fails a DC 10 Charisma saving throw, the "
        "sprite also knows the creature's alignment. Celestials, fiends, and "
        "undead automatically fail the saving throw."
    ),
    "Change Shape": (
        "The hag magically polymorphs into a Small or Medium female humanoid, or back "
        "into her true form. Her statistics are the same in each form. Any equipment "
        "she is wearing or carrying isn't transformed. She reverts to her true form if "
        "she dies."
    ),
    "Nightmare Haunting (1/Day)": (
        "While on the Ethereal Plane, the hag magically touches a sleeping humanoid on "
        "the Material Plane. A protection from evil and good spell cast on the target "
        "prevents this contact, as does a magic circle. As long as the contact "
        "persists, the target has dreadful visions. If these visions last for at least "
        "1 hour, the target gains no benefit from its rest, and its hit point maximum "
        "is reduced by 5 (1d10). If this effect reduces the target's hit point maximum "
        "to 0, the target dies, and if the target was evil, its soul is trapped in the "
        "hag's soul bag. The reduction to the target's hit point maximum lasts until "
        "removed by the greater restoration spell or similar magic."
    ),
}


def verified_nonactionable_action_2014(monster: SourceMonster2014, action_name: str) -> bool:
    """Allow a source Action only if its *entire* effect is proven informational."""
    try:
        if action_name not in monster.action_names:
            return False
        if verified_arena_inert_equipment_action_2014(monster, action_name):
            return True
        if source_proven_noncombat_read_thoughts_2014(monster, action_name):
            return True
        expected = _NONCOMBAT_ACTION_CLAUSES_2014.get(action_name)
        if expected is None:
            return False
        printed = source_sections_2014(
            monster.source_actions, include_continuations=True,
        ).get(action_name)
        if printed is None:
            return False
        normalize = lambda text: " ".join(text.casefold().replace("’", "'").split())
        return normalize(printed) == normalize(expected)
    except Exception:
        logger.exception(
            "2014 noncombat action proof failed for %s / %s",
            monster.id, action_name,
        )
        raise
