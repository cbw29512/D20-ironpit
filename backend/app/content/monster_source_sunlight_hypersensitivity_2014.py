"""Full printed 2014 environmental flaw proof; runtime uses typed contexts."""
from __future__ import annotations

import logging

from app.content.monster_source_2014 import SourceMonster2014
from app.content.monster_source_sections_2014 import source_sections_2014
from app.domain.environment_contexts import EnvironmentContextReaction
from app.domain.weapons_base import DamageType

logger = logging.getLogger(__name__)

_SHARED = (
    "the vampire has the following flaws: forbiddance. "
    "the vampire can't enter a residence without an invitation from one of the occupants. "
    "harmed by running water. the vampire takes 20 acid damage "
)
_SUN = (
    " sunlight hypersensitivity. the vampire takes 20 radiant damage "
    "when it starts its turn in sunlight. while in sunlight, "
    "it has disadvantage on attack rolls and ability checks."
)
_RESTING = (
    "stake to the heart. if a piercing weapon made of wood is driven into the "
    "vampire's heart while the vampire is incapacitated in its resting place, "
    "the vampire is paralyzed until the stake is removed."
)
_DESTROYED = (
    "stake to the heart. the vampire is destroyed if a piercing weapon made "
    "of wood is driven into its heart while it is incapacitated in its resting place."
)
_PINNED = frozenset({
    _SHARED + "if it ends its turn in running water. " + _RESTING + _SUN,
    _SHARED + "when it ends its turn in running water. " + _DESTROYED + _SUN,
})


def source_proven_sunlight_hypersensitivity_2014(
    monster: SourceMonster2014,
) -> EnvironmentContextReaction | None:
    """Return shared context effect only when every printed clause is accounted for."""
    try:
        if "Vampire Weaknesses" not in monster.trait_names:
            return None
        source = source_sections_2014(
            monster.source_traits, include_continuations=True,
        ).get("Vampire Weaknesses", "")
        normalized = " ".join(source.casefold().replace("’", "'").split())
        if normalized not in _PINNED:
            return None
        # Residence, running water and a vulnerable sleeping body lack legal
        # standard-arena triggers. A source-owned sunlight emitter does not.
        return EnvironmentContextReaction(
            source_id="vampire-weaknesses",
            source_name="Vampire Weaknesses",
            context_id="sunlight",
            disadvantage_on=["attack_rolls", "ability_checks"],
            start_turn_damage_amount=20,
            start_turn_damage_type=DamageType.RADIANT,
        )
    except Exception:
        logger.exception("Failed source sunlight weakness proof for %s.", monster.id)
        raise
