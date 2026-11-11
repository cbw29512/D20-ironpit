from __future__ import annotations

import logging

from app.domain.regeneration import RegenerationTrait
from app.content.monster_source_2014 import SourceMonster2014
from app.content.monster_source_sections_2014 import source_sections_2014

logger = logging.getLogger(__name__)


def regeneration_trait_2014(monster: SourceMonster2014) -> RegenerationTrait | None:
    """Compile a pinned 2014 Regeneration object into the shared trait."""
    try:
        raw = monster.regeneration
        if raw is None:
            return None
        if not isinstance(raw, dict):
            raise ValueError(f"{monster.id} Regeneration must be a declarative object.")
        trait = RegenerationTrait.model_validate(raw)
        printed = source_sections_2014(
            monster.source_traits, include_continuations=True,
        ).get("Regeneration", "")
        normal = " ".join(printed.casefold().replace("’", "'").split())
        if "sunlight" in normal or "running water" in normal:
            expected = (
                f"the vampire regains {trait.amount} hit points at the start of its "
                "turn if it has at least 1 hit point and isn't in sunlight or running water. "
                "if the vampire takes radiant damage or damage from holy water, "
                "this trait doesn't function at the start of the vampire's next turn."
            )
            if normal != expected:
                raise ValueError("Environmental Regeneration source clause changed; fail closed.")
            trait = trait.model_copy(update={
                "suppressed_by_environment_contexts": ["sunlight"],
            })
        return trait
    except Exception:
        logger.exception("Failed to compile 2014 Regeneration for %s.", monster.id)
        raise


def supports_regeneration_2014(monster: SourceMonster2014) -> bool:
    """Return whether printed Regeneration can bind to the shared primitive."""
    try:
        return regeneration_trait_2014(monster) is not None
    except Exception:
        logger.exception("Failed to classify 2014 Regeneration for %s.", monster.id)
        raise
