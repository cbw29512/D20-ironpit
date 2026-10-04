from __future__ import annotations

import logging
import re
from functools import lru_cache

from app.content.monster_source_2014 import load_monster_source_2014
from app.domain.capabilities import CombatantDefinition

logger = logging.getLogger(__name__)
_MODE_VERBS = {
    "flies": "fly",
    "swims": "swim",
    "walks": "walk",
    "climbs": "climb",
    "burrows": "burrow",
}
_EXEMPTION_RE = re.compile(
    r"doesn['’]t provoke (?:an )?opportunity attacks? when it "
    r"(flies|swims|walks|climbs|burrows) out of an enemy['’]?s reach",
    re.IGNORECASE,
)


def exempt_movement_modes_from_trait_text(source_traits: object) -> tuple[str, ...]:
    """Bind OA-exempt modes from printed trait text, never from a trait heading."""
    try:
        text = str(source_traits or "")
        if not text.strip():
            return ()
        found: list[str] = []
        for match in _EXEMPTION_RE.finditer(text):
            mode = _MODE_VERBS[match.group(1).lower()]
            if mode not in found:
                found.append(mode)
        return tuple(found)
    except Exception:
        logger.exception("Failed to parse movement-mode opportunity-attack exemptions.")
        raise RuntimeError("Movement-mode opportunity-attack exemptions could not be parsed.") from None


@lru_cache(maxsize=1)
def _source_traits_by_id() -> dict[str, str]:
    try:
        return {
            monster.id: str(monster.source_traits or "")
            for monster in load_monster_source_2014()
        }
    except Exception:
        logger.exception("Failed to index 2014 source trait text for movement-mode OA exemptions.")
        raise RuntimeError("2014 source trait text could not be indexed.") from None


def compiled_opportunity_attack_exempt_movement_modes(
    definition: CombatantDefinition,
) -> tuple[str, ...]:
    """Prefer explicit definition data, otherwise compile from 2014 source trait bodies."""
    try:
        existing = tuple(definition.opportunity_attack_exempt_movement_modes or ())
        if existing:
            return existing
        if definition.kind != "monster" or definition.ruleset != "2014":
            return ()
        source_id = definition.id.removeprefix("2014-")
        return exempt_movement_modes_from_trait_text(_source_traits_by_id().get(source_id, ""))
    except Exception:
        logger.exception(
            "Failed to compile movement-mode opportunity-attack exemptions for %s.",
            definition.id,
        )
        raise RuntimeError(
            "Movement-mode opportunity-attack exemptions could not be compiled."
        ) from None
