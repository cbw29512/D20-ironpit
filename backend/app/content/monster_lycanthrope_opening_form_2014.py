"""Source-verified 2014 lycanthrope opening-form policy.

Uses the locked Iron Pit rule: lycanthropes begin combat in their printed
beast (animal) form at no action cost. True form remains humanoid. Mid-fight
Shapechanger Action remains available for later binding. No name dispatch in
resolvers; this module only classifies source cards.
"""
from __future__ import annotations

import logging
import re
from html import unescape

from app.content.monster_source_2014 import SourceMonster2014

logger = logging.getLogger(__name__)

_LYCANTHROPE_IDS = frozenset({
    "werebear",
    "wereboar",
    "wererat",
    "weretiger",
    "werewolf",
})

_REQUIRED_CLAUSES = (
    "use its action to polymorph",
    "or back into its true form, which is humanoid",
    "it reverts to its true form if it dies",
)

_BEAST_FORMS = {
    "werebear": "large bear",
    "wereboar": "boar",
    "wererat": "giant rat",
    "weretiger": "tiger",
    "werewolf": "wolf",
}


def verified_lycanthrope_shapechanger_2014(monster: SourceMonster2014) -> bool:
    """True only when the printed Shapechanger matches the approved lycanthrope family."""
    try:
        if monster.id not in _LYCANTHROPE_IDS:
            return False
        if "Shapechanger" not in (monster.trait_names or ()):
            return False
        source = monster.source_traits or ""
        heading = "<strong>Shapechanger.</strong>"
        if heading not in source:
            return False
        continuation = source.split(heading, 1)[1].split("<strong>", 1)[0]
        section = " ".join(unescape(re.sub(r"<[^>]+>", " ", continuation)).split()).casefold()
        if not all(clause in section for clause in _REQUIRED_CLAUSES):
            return False
        expected_beast = _BEAST_FORMS.get(monster.id)
        return expected_beast is not None and expected_beast in section
    except Exception:
        logger.exception("Could not validate 2014 lycanthrope Shapechanger for %s", monster.id)
        raise


def opening_beast_form_id_2014(monster: SourceMonster2014) -> str:
    """Return the locked opening form ID after source proof. Fail closed otherwise."""
    if not verified_lycanthrope_shapechanger_2014(monster):
        raise ValueError(f"{monster.id} is not a verified 2014 lycanthrope Shapechanger source.")
    return "beast"
