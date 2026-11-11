"""Source-only, immutable contracts for taking control of another combatant.

No creature-name runtime dispatch or direct battle-state mutation. A separate
universal engine resolver must implement control transfer before admission.
"""
from __future__ import annotations

import logging
import re

from pydantic import BaseModel, Field

from app.content.monster_source_2014 import SourceMonster2014
from app.content.monster_source_sections_2014 import source_sections_2014

logger = logging.getLogger(__name__)


class SourceBodyControlDefinition(BaseModel):
    """Printed parameters that a future generic control resolver must honor."""

    source_action_id: str = Field(min_length=1)
    source_name: str = Field(min_length=1)
    recharge_minimum: int = Field(ge=1, le=6)
    range_ft: int = Field(ge=0)
    required_creature_type: str = Field(min_length=1)
    requires_sight: bool
    save_ability: str = Field(min_length=1)
    save_dc: int = Field(ge=1, le=40)
    release_bonus_action: bool
    ends_on_host_zero_hp: bool
    owner_untargetable_except_turning: bool
    host_uses_own_statistics: bool
    owner_retains_mental_scores: bool
    post_end_immunity_hours: int = Field(ge=1)


# This recognizes every printed control, targetability, statistics and exit
# clause. New outcomes fail closed rather than silently disappearing.
_BODY_CONTROL = re.compile(
    r"One (?P<creature>humanoid) that the (?P<owner>[a-z][a-z -]*) can see "
    r"within (?P<range>\d+) feet of it must succeed on a DC (?P<dc>\d+) "
    r"(?P<ability>Charisma) saving throw or be possessed by the (?P=owner); "
    r"the (?P=owner) then disappears, and the target is incapacitated and "
    r"loses control of its body\. The (?P=owner) now controls the body but "
    r"doesn't deprive the target of awareness\. The (?P=owner) can't be "
    r"targeted by any attack, spell, or other effect, except ones that "
    r"turn undead, and it retains its alignment, Intelligence, Wisdom, "
    r"Charisma, and immunity to being charmed and frightened\. It otherwise "
    r"uses the possessed target's statistics, but doesn't gain access to "
    r"the target's knowledge, class features, or proficiencies\. "
    r"The possession lasts until the body drops to 0 hit points, the "
    r"(?P=owner) ends it as a bonus action, or the (?P=owner) is turned "
    r"or forced out by an effect like the dispel evil and good spell\. "
    r"When the possession ends, the (?P=owner) reappears in an unoccupied "
    r"space within (?P<exit_range>\d+) feet of the body\. The target is "
    r"immune to this (?P=owner)'s Possession for (?P<immunity>\d+) hours "
    r"after succeeding on the saving throw or after the possession ends\.",
    re.IGNORECASE,
)


def source_proven_body_control_2014(
    monster: SourceMonster2014,
) -> list[SourceBodyControlDefinition]:
    """Return complete typed source parameters, never a runnable action."""
    try:
        headers = [
            name for name in monster.action_names
            if re.fullmatch(r"Possession \(Recharge 6\)", name)
        ]
        if len(headers) != 1 or monster.action_recharges.get("possession") != 6:
            return []
        section = source_sections_2014(
            monster.source_actions, include_continuations=True,
        ).get(headers[0])
        if section is None:
            return []
        match = _BODY_CONTROL.fullmatch(" ".join(section.replace("’", "'").split()))
        if match is None or int(match["exit_range"]) != 5 or int(match["immunity"]) != 24:
            return []
        return [SourceBodyControlDefinition(
            source_action_id="possession",
            source_name="Possession",
            recharge_minimum=6,
            range_ft=int(match["range"]),
            required_creature_type=match["creature"].lower(),
            requires_sight=True,
            save_ability=match["ability"].lower(),
            save_dc=int(match["dc"]),
            release_bonus_action=True,
            ends_on_host_zero_hp=True,
            owner_untargetable_except_turning=True,
            host_uses_own_statistics=True,
            owner_retains_mental_scores=True,
            post_end_immunity_hours=int(match["immunity"]),
        )]
    except Exception:
        logger.exception("Failed source-proven body-control contract for %s.", monster.id)
        raise
