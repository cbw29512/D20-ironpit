"""Full-source proof for conditional grapple Multiattack slot sequences.

Only source adapter validates printed order and eligibility; generic Python
and browser Multiattack executors decide legality from current grapple state.
"""
from __future__ import annotations

import logging
import re

from app.content.monster_source_2014 import SourceMonster2014
from app.content.monster_source_sections_2014 import source_sections_2014

logger = logging.getLogger(__name__)
_NUMBERS = {"one": 1, "two": 2, "three": 3}
_CONDITIONAL = re.compile(
    r"The (?P<owner>[a-z][a-z '\-]*) makes (?P<count>one|two|three) "
    r"(?P<attack>[a-z][a-z '\-]*) attacks\. "
    r"If the (?P=owner) is grappling a creature, the (?P=owner) "
    r"can also use its (?P<save>[a-z][a-z '\-]*) once\.",
    flags=re.IGNORECASE,
)


def source_proves_grapple_followup_multiattack_2014(
    monster: SourceMonster2014, save_ids: set[str],
) -> bool:
    """Reject altered counts, action names, order, and hidden source riders."""
    try:
        binding = monster.multiattack_binding
        if not isinstance(binding, dict) or set(binding) != {"slots"}:
            return False
        slots = binding["slots"]
        if not isinstance(slots, list):
            return False
        body = source_sections_2014(
            monster.source_actions, include_continuations=True,
        ).get("Multiattack", "")
        match = _CONDITIONAL.fullmatch(" ".join(body.replace("’", "'").split()))
        if match is None or match["owner"].casefold() != monster.name.casefold():
            return False
        count = _NUMBERS[match["count"].casefold()]
        if len(slots) != count + 1:
            return False
        base_ids = [
            attack.id for attack in monster.attacks
            if attack.name.casefold() == match["attack"].casefold()
        ]
        followup_ids = [
            name for name in save_ids if name == re.sub(
                r"[^a-z0-9]+", "-", match["save"].casefold(),
            ).strip("-")
        ]
        if len(base_ids) != 1 or len(followup_ids) != 1:
            return False
        for raw in slots[:count]:
            if not isinstance(raw, dict) or raw != {"action_ids": base_ids}:
                return False
        return slots[-1] == {
            "action_ids": followup_ids,
            "optional": True,
            "requirement": "source_has_grappled_target",
        }
    except Exception:
        logger.exception("Failed strict source proof for conditional grapple Multiattack.")
        raise
