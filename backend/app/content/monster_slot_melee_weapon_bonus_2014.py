"""Source-proof slot-funded melee weapon damage bonuses for 2014 monsters.

State schema: TimedSelfBuffAction owns action/slot/duration; SpellModifierEffect
limits bonus dice to genuine melee weapon attacks. Combat code never
dispatches on the printed monster or trait name.
"""
from __future__ import annotations

import logging
import re

from app.content.monster_source_2014 import SourceMonster2014
from app.content.monster_source_sections_2014 import source_sections_2014
from app.content.monster_spell_slot_resources_2014 import monster_spell_slot_resources_2014
from app.domain.spell_modifiers import SpellModifierEffect
from app.domain.timed_self_buffs import TimedSelfBuffAction

logger = logging.getLogger(__name__)

# The WHOLE trait must describe one slot-funded, end-of-turn, melee-only bonus.
_SLOT_MELEE_BONUS = re.compile(
    r"As a bonus action, the (?P<subject>[^.]+?) can expend a spell slot to cause its "
    r"melee weapon attacks to magically deal an extra (?P<average>\d+) "
    r"\((?P<dice>\d+)d6\) (?P<type>\w+) damage to a target on a hit\. "
    r"This benefit lasts until the end of the turn\. If the (?P=subject) "
    r"expends a spell slot of 2nd level or higher, the extra damage increases "
    r"by 1d6 for each level above 1st\.",
    flags=re.IGNORECASE,
)


def slot_melee_weapon_bonus_actions_2014(
    monster: SourceMonster2014,
) -> list[TimedSelfBuffAction]:
    """Bind every whole-source matching trait without name-based mechanics."""
    try:
        source = monster.spellcasting
        if not isinstance(source, dict) or source.get("source_complete") is not True:
            return []

        paragraphs = source_sections_2014(
            monster.source_traits, include_continuations=True,
        )
        actions: list[TimedSelfBuffAction] = []
        for heading, body in paragraphs.items():
            match = _SLOT_MELEE_BONUS.fullmatch(body)
            if match is None or heading not in monster.trait_names:
                continue
            dice = int(match["dice"])
            if not 1 <= dice <= 11 or int(match["average"]) != dice * 7 // 2:
                continue
            damage_type = match["type"].lower()
            slug = re.sub(r"[^a-z0-9]+", "-", heading.lower()).strip("-")
            for slot in monster_spell_slot_resources_2014(monster):
                level = int(slot.id.removeprefix("spell-slot-"))
                count = dice + level - 1
                if count > 20:
                    continue
                actions.append(TimedSelfBuffAction(
                    id=f"{slug}-slot-{level}",
                    name=f"{heading} (Level {level})",
                    action_cost="bonus_action",
                    resource_id=slot.id,
                    resource_cost=1,
                    expend_slot_without_cast=True,
                    duration_rounds=1,
                    expiry_timing="source_turn_end",
                    magical_effect=True,
                    modifier_effects=[SpellModifierEffect(
                        kind="bonus-damage",
                        dice_count=count,
                        dice_size=6,
                        damage_type=damage_type,
                        required_weapon_attack_kind="melee",
                    )],
                    animation="radiant-buff",
                ))
        return actions
    except Exception:
        logger.exception("2014 source slot/melee bonus binding failed for %s", monster.id)
        raise


def bound_slot_melee_weapon_bonus_traits_2014(monster: SourceMonster2014) -> set[str]:
    """Read source trait labels from successfully compiled generic actions."""
    try:
        return {
            action.name.rsplit(" (Level ", 1)[0]
            for action in slot_melee_weapon_bonus_actions_2014(monster)
        }
    except Exception:
        logger.exception("2014 slot/melee trait classification failed for %s", monster.id)
        raise
