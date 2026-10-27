"""Source-verified 2014 lycanthrope Shapechanger opening-form policy.

Locked Iron Pit rule: 2014 lycanthropes always begin combat in their printed
beast (animal) form. This module proves the printed Shapechanger clause and
extracts the beast form without monster-name dispatch.

True form is humanoid; the action polymorphs into hybrid or into the beast.
Fail closed on mutated, missing, or extra clauses.
"""
from __future__ import annotations

import re
from html import unescape

from app.content.monster_source_2014 import SourceMonster2014

_SHAPECHANGER_HEADING = "<strong>Shapechanger.</strong>"
_BEAST_PATTERN = re.compile(
    r"polymorph into a .+? hybrid or into a(?:n)? (.+?), or back into its true form, which is humanoid",
    re.IGNORECASE | re.DOTALL,
)


def verified_lycanthrope_beast_opening_form_2014(monster: SourceMonster2014) -> str | None:
    """Return the printed beast form ID if the Shapechanger clause is exact, else None.

    No name dispatch. Returns a normalized form key only after full-clause match.
    """
    try:
        source = unescape(monster.source_traits or "")
        if _SHAPECHANGER_HEADING not in source:
            return None
        # Isolate the first Shapechanger paragraph.
        start = source.find(_SHAPECHANGER_HEADING)
        end = source.find("</p>", start)
        paragraph = source[start:end] if end > start else source[start:start + 800]
        match = _BEAST_PATTERN.search(paragraph)
        if not match:
            return None
        beast = match.group(1).strip().lower()
        # Normalize common printed variants to a stable form key.
        beast = re.sub(r"\s+", "-", beast)
        if not beast or "hybrid" in beast or "humanoid" in beast:
            return None
        return beast
    except Exception:
        return None
