"""Source proof that lycanthrope form-gated Multiattack is the existing primitive.

Under locked Pit rules the Shapechanger trait is arena-inert (statistics
identical except AC or size). Therefore a Multiattack whose only form
qualifier is the same inert Shapechanger is the ordinary multiattack
already represented by multiattack_slots. This is source classification
only; combat resolution never dispatches on the form note or monster name.
Any mutation of the printed clause fails closed.
"""
from __future__ import annotations

import logging

from app.content.monster_arena_neutral_traits_2014 import verified_arena_inert_trait_2014
from app.content.monster_source_2014 import SourceMonster2014
from app.content.monster_source_sections_2014 import source_sections_2014

logger = logging.getLogger(__name__)

_WEREWOLF_MULTIATTACK = (
    "The werewolf makes two attacks: one with its bite and one with its claws or spear."
)


def verified_lycanthrope_form_gated_multiattack_2014(
    monster: SourceMonster2014, action_name: str,
) -> bool:
    """Accept only the exact pinned Werewolf Multiattack under proven inert Shapechanger."""
    try:
        if monster.id != "werewolf" or action_name not in monster.action_names:
            return False
        if not verified_arena_inert_trait_2014(monster, "Shapechanger"):
            return False
        printed = source_sections_2014(monster.source_actions).get(action_name, "")
        normalized = " ".join(printed.casefold().replace("’", "'").split())
        expected = " ".join(_WEREWOLF_MULTIATTACK.casefold().split())
        return normalized == expected
    except Exception:
        logger.exception(
            "2014 lycanthrope form-gated Multiattack proof failed for %s / %s",
            monster.id, action_name,
        )
        raise
