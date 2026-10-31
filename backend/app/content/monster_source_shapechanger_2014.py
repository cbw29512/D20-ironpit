"""Source-proven 2014 Shapechanger family contract.

Common printed pattern (verified against immutable cards):
- Action to polymorph into a listed form or back to true form.
- Statistics other than size are identical in each form.
- Equipment worn/carried is not transformed.
- Reverts to true form on death.

Differences (size, available attacks, form-only traits) remain source data.
This module only proves the shared contract for reuse of existing
ReplacementFormAction / enter_replacement_form primitives.
No monster-name dispatch. No admission claimed.
"""
from __future__ import annotations

import re
from typing import Final

from app.content.monster_source_2014 import SourceMonster2014

_SHAPECHANGER = re.compile(
    r"(?P<name>\w[\w\s/'-]*?) can use its action to polymorph into "
    r"(?P<form>.+?) or back into its true form\. "
    r"Its statistics, other than its size, are the same in each form\. "
    r"Any equipment it is wearing or carrying isn't transformed\. "
    r"It reverts to its true form if it dies\.",
    re.IGNORECASE | re.DOTALL,
)

# Source-proven consumers of the common contract (2014 SRD). Not a runtime key.
SHAPECHANGER_FAMILY_2014: Final[frozenset[str]] = frozenset({
    "doppelganger", "imp", "mimic", "quasit", "succubus/incubus",
    "vampire", "werebear", "wereboar", "wererat", "weretiger", "werewolf",
})


def source_proven_shapechanger_2014(monster: SourceMonster2014) -> dict | None:
    """Return immutable contract parameters when the common pattern matches.

    Fail closed on any deviation. Size, form list, and form-specific mechanics
    stay on the source card; this only certifies the shared lifecycle.
    """
    if monster.id not in SHAPECHANGER_FAMILY_2014:
        return None
    section = (monster.source_traits or "") + " " + (monster.source_actions or "")
    match = _SHAPECHANGER.search(section)
    if match is None:
        return None
    return {
        "source_id": "shapechanger",
        "source_name": "Shapechanger",
        "action_cost": "action",
        "hp_mode": "retain_owner",
        "ends_on_death": True,
        "equipment_preserved": True,
        "stats_identical_except_size": True,
        "printed_name": match.group("name").strip(),
        "form_description": match.group("form").strip(),
    }
