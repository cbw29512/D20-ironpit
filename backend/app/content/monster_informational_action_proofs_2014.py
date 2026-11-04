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
}


def verified_nonactionable_action_2014(monster: SourceMonster2014, action_name: str) -> bool:
    """Allow a source Action only if its *entire* effect is proven informational or arena-inert under locked Pit rules."""
    try:
        if action_name not in monster.action_names and action_name != "Shapechanger":
            return False
        if verified_arena_inert_equipment_action_2014(monster, action_name):
            return True
        # Lycanthrope Shapechanger action: polymorph with no combat-stat change
        # beyond already-printed AC/size under locked Pit rules. Exact source match.
        if action_name == "Shapechanger" and monster.id in (
            "werewolf", "werebear", "wererat", "wereboar", "weretiger",
        ):
            from app.content.monster_source_sections_2014 import source_sections_2014 as sections
            printed = sections(monster.source_traits or "", include_continuations=True).get("Shapechanger", "")
            expected = {
                "werewolf": (
                    "The werewolf can use its action to polymorph into a wolf-humanoid "
                    "hybrid or into a wolf, or back into its true form, which is humanoid. "
                    "Its statistics, other than its AC, are the same in each form. "
                    "Any equipment it is wearing or carrying isn't transformed. "
                    "It reverts to its true form if it dies."
                ),
                "werebear": (
                    "The werebear can use its action to polymorph into a Large bear-humanoid "
                    "hybrid or into a Large bear, or back into its true form, which is humanoid. "
                    "Its statistics, other than its size and AC, are the same in each form. "
                    "Any equipment it is wearing or carrying isn't transformed. "
                    "It reverts to its true form if it dies."
                ),
                "wererat": (
                    "The wererat can use its action to polymorph into a rat-humanoid "
                    "hybrid or into a giant rat, or back into its true form, which is humanoid. "
                    "Its statistics, other than its size, are the same in each form. "
                    "Any equipment it is wearing or carrying isn't transformed. "
                    "It reverts to its true form if it dies."
                ),
                "wereboar": (
                    "The wereboar can use its action to polymorph into a boar-humanoid "
                    "hybrid or into a boar, or back into its true form, which is humanoid. "
                    "Its statistics, other than its AC, are the same in each form. "
                    "Any equipment it is wearing or carrying isn't transformed. "
                    "It reverts to its true form if it dies."
                ),
                "weretiger": (
                    "The weretiger can use its action to polymorph into a tiger-humanoid "
                    "hybrid or into a tiger, or back into its true form, which is humanoid. "
                    "Its statistics, other than its size, are the same in each form. "
                    "Any equipment it is wearing or carrying isn't transformed. "
                    "It reverts to its true form if it dies."
                ),
            }
            return printed == expected.get(monster.id, "")
        expected = _NONCOMBAT_ACTION_CLAUSES_2014.get(action_name)
        if expected is None:
            return False
        printed = source_sections_2014(monster.source_actions).get(action_name)
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
