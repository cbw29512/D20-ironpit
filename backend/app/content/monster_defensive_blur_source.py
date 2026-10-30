from __future__ import annotations

import logging
import re

from app.domain.models import CombatantTemplate
from app.domain.traits import CombatTrait

logger = logging.getLogger(__name__)
_TRAIT = CombatTrait.ATTACKS_AGAINST_DISADVANTAGE_UNLESS_INCAPACITATED
_PATTERN = re.compile(
    r"(?P<name>[A-Z][A-Za-z0-9’' -]*?)\.\s+"
    r"Attack rolls against the [^.]+ are made with Disadvantage unless the [^.]+ "
    r"has the Incapacitated condition\.",
    re.IGNORECASE,
)


def defensive_disadvantage_trait_name(source_traits: object) -> str | None:
    """Return the printed trait name when it declares the generic defensive rule."""
    try:
        match = _PATTERN.search(str(source_traits or ""))
        return match.group("name").strip() if match else None
    except Exception as exc:
        logger.exception("Failed to parse defensive attack-Disadvantage trait.")
        raise RuntimeError("Defensive attack-Disadvantage trait could not be parsed.") from exc


def defensive_disadvantage_trait_issues(
    template: CombatantTemplate,
    row: dict[str, object],
) -> tuple[list[str], set[str]]:
    """Audit source behavior against the generic runtime trait."""
    try:
        name = defensive_disadvantage_trait_name(row.get("traits", ""))
        runtime_has = _TRAIT in template.combat_traits
        if name is None:
            return (["trait-source-missing:attacks-against-disadvantage"] if runtime_has else []), set()
        if not runtime_has:
            return ["trait-runtime-missing:attacks-against-disadvantage"], set()
        return [], {name}
    except Exception as exc:
        logger.exception("Failed defensive attack-Disadvantage audit for %s.", template.id)
        raise RuntimeError("Defensive attack-Disadvantage audit failed.") from exc
