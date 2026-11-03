from __future__ import annotations

import logging
import re

from app.content.monster_source_2014 import SourceMonster2014
from app.domain.spell_modifiers import SpellModifierEffect
from app.domain.timed_self_buffs import TimedSelfBuffAction

logger = logging.getLogger(__name__)

_DIVINE_EMINENCE = re.compile(
    r"As a bonus action, the (?P<subject>[^.]+?) can expend a spell slot to cause its "
    r"melee weapon attacks to magically deal an extra \d+ \((?P<base_dice>\d+)d6\) "
    r"(?P<damage_type>\w+) damage to a target on a hit\. This benefit lasts until the "
    r"end of the turn\. If the (?P=subject) expends a spell slot of 2nd level or higher, "
    r"the extra damage increases by 1d6 for each level above 1st\.",
    flags=re.IGNORECASE | re.DOTALL,
)


def divine_eminence_actions_2014(monster: SourceMonster2014) -> list[TimedSelfBuffAction]:
    """Bind source-proven Divine Eminence as Bonus Action slot-scaled on-hit radiant damage.

    Parses the printed trait. Creates one TimedSelfBuffAction per available spell-slot
    level using existing universal primitives. No name dispatch at resolution time.
    """
    try:
        if "Divine Eminence" not in monster.trait_names:
            return []
        plain = re.sub(r"<[^>]+>", " ", monster.source_traits or "")
        plain = re.sub(r"\s+", " ", plain)
        match = _DIVINE_EMINENCE.search(plain)
        if match is None:
            return []
        source = monster.spellcasting
        if not isinstance(source, dict) or source.get("source_complete") is not True:
            return []
        raw_slots = source.get("slots") or {}
        if not isinstance(raw_slots, dict):
            return []

        base_dice = int(match["base_dice"])
        damage_type = match["damage_type"].strip().lower()
        actions: list[TimedSelfBuffAction] = []
        for raw_level, count in sorted(raw_slots.items(), key=lambda item: int(item[0])):
            level = int(raw_level)
            if not 1 <= level <= 9 or not isinstance(count, int) or count < 1:
                continue
            dice = base_dice + max(0, level - 1)
            actions.append(
                TimedSelfBuffAction(
                    id=f"divine-eminence-slot-{level}",
                    name=f"Divine Eminence (Level {level})",
                    action_cost="bonus_action",
                    resource_id=f"spell-slot-{level}",
                    resource_cost=1,
                    duration_rounds=1,
                    expiry_timing="source_turn_end",
                    magical_effect=True,
                    modifier_effects=[
                        SpellModifierEffect(
                            kind="bonus-damage",
                            dice_count=dice,
                            dice_size=6,
                            damage_type=damage_type,
                        )
                    ],
                    animation="divine-eminence",
                )
            )
        return actions
    except Exception:
        logger.exception("Failed to bind 2014 Divine Eminence for %s.", monster.name)
        raise


def supports_divine_eminence_2014(monster: SourceMonster2014) -> bool:
    return bool(divine_eminence_actions_2014(monster))
