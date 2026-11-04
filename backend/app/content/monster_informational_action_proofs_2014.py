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

logger = logging.getLogger(__name__)

# Whole, inspected printed clauses. Extra combat-effective riders must fail
# closed instead of inheriting a permissive name-based exclusion.
_NONCOMBAT_ACTION_CLAUSES_2014 = {
    "Heart Sight": (
        "The sprite touches a creature and magically knows the creature's current "
        "emotional state. If the target fails a DC 10 Charisma saving throw, the "
        "sprite also knows the creature's alignment. Celestials, fiends, and "
        "undead automatically fail the saving throw."
    ),
    "Change Shape": (
        # Per-monster exact text is checked below; this entry is a placeholder
        # so the name is recognized. Real match is in the function.
        None
    ),
    "Etherealness": (
        None
    ),
}


def verified_nonactionable_action_2014(monster: SourceMonster2014, action_name: str) -> bool:
    """Allow a source Action only if its *entire* effect is proven informational."""
    try:
        if action_name not in monster.action_names:
            return False
        if verified_arena_inert_equipment_action_2014(monster, action_name):
            return True
        printed = source_sections_2014(monster.source_actions).get(action_name)
        if printed is None:
            return False
        normalize = lambda text: " ".join(text.casefold().replace("’", "'").split())
        printed_n = normalize(printed)
        if action_name == "Change Shape":
            expected = {
                "night-hag": normalize(
                    "The hag magically polymorphs into a Small or Medium female humanoid, "
                    "or back into her true form. Her statistics are the same in each form. "
                    "Any equipment she is wearing or carrying isn't transformed. "
                    "She reverts to her true form if she dies."
                ),
                "oni": normalize(
                    "The oni magically polymorphs into a Small or Medium humanoid, into a Large giant, "
                    "or back into its true form. Other than its size, its statistics are the same in each form. "
                    "The only equipment that is transformed is its glaive, which shrinks so that it can be wielded "
                    "in humanoid form. If the oni dies, it reverts to its true form, and its glaive reverts to its normal size."
                ),
            }.get(monster.id)
            return expected is not None and printed_n == expected
        if action_name == "Etherealness":
            expected = {
                "ghost": normalize(
                    "The ghost enters the Ethereal Plane from the Material Plane, or vice versa. "
                    "It is visible on the Material Plane while it is in the Border Ethereal, and vice versa, "
                    "yet it can't affect or be affected by anything on the other plane."
                ),
                "night-hag": normalize(
                    "The hag magically enters the Ethereal Plane from the Material Plane, or vice versa. "
                    "To do so, the hag must have a heartstone in her possession."
                ),
                "succubus-incubus": normalize(
                    "The fiend magically enters the Ethereal Plane from the Material Plane, or vice versa."
                ),
            }.get(monster.id)
            return expected is not None and printed_n == expected
        expected = _NONCOMBAT_ACTION_CLAUSES_2014.get(action_name)
        if expected is None or expected is None:
            return False
        return printed_n == normalize(expected)
    except Exception:
        logger.exception(
            "2014 noncombat action proof failed for %s / %s",
            monster.id, action_name,
        )
        raise
