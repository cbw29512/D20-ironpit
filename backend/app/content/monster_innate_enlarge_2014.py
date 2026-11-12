"""2014 innate Enlarge, bound to the shared self-buff/weapon modifier system.

State: a timed, concentrating source-owned buff provides a one-category
size increase, Strength check/save Advantage, and extra weapon-hit damage.
The standard arena AI selects only the beneficial self-targeted Enlarge
mode; the source reference still retains the complete Enlarge/Reduce spell.
"""
from __future__ import annotations

import logging

from app.content.monster_innate_elemental_inert_2014 import (
    source_proven_elemental_inert_spells_2014,
)
from app.content.monster_innate_source_2014 import innate_spells_2014
from app.content.monster_source_2014 import SourceMonster2014
from app.content.monster_source_sections_2014 import source_sections_2014
from app.domain.progression import SavingThrowAdvantageGrant
from app.domain.size import CreatureSize
from app.domain.spell_modifiers import SpellModifierEffect
from app.domain.timed_self_buffs import TimedSelfBuffAction

logger = logging.getLogger(__name__)

_SIZE_AFTER_GROWTH = {
    CreatureSize.TINY: CreatureSize.SMALL,
    CreatureSize.SMALL: CreatureSize.MEDIUM,
    CreatureSize.MEDIUM: CreatureSize.LARGE,
    CreatureSize.LARGE: CreatureSize.HUGE,
    CreatureSize.HUGE: CreatureSize.GARGANTUAN,
}


def source_proven_innate_enlarge_2014(
    monster: SourceMonster2014,
) -> list[TimedSelfBuffAction]:
    """Compose complete source spell/weapon data; never use creature IDs."""
    try:
        # The existing full-source proof validates all nine innate spells,
        # their costs and exact printed spell paragraph before any action.
        if not source_proven_elemental_inert_spells_2014(monster):
            return []
        row, = [
            item for item in innate_spells_2014(monster)
            if item.get("id") == "enlarge-reduce"
        ]
        if (row.get("usage"), row.get("uses_per_day"),
                row.get("shared_pool")) != ("per_day", 3, True):
            return []

        original_size = CreatureSize(monster.size.casefold())
        new_size = _SIZE_AFTER_GROWTH.get(original_size)
        if new_size is None:
            return []

        # Only a single, source-complete melee weapon profile may use this
        # modifier. All other actions, including ranged spells, are untouched.
        melee = [
            attack for attack in monster.attacks if attack.kind == "melee"
        ]
        if len(melee) != 1:
            return []
        attack = melee[0]
        if (not attack.source_complete or attack.damage.type is None
                or attack.damage.dice_count < 1
                or attack.conditional_damage):
            return []
        printed = source_sections_2014(
            monster.source_actions, include_continuations=True,
        ).get(attack.name, "")
        damage = attack.damage
        expected_hit = (
            f"Hit: {damage.average} ({damage.dice_count}d"
            f"{damage.dice_size} + {damage.bonus}) "
            f"{damage.type} damage"
        )
        if ("Melee Weapon Attack:" not in printed
                or expected_hit not in printed):
            return []

        # No spell slot is fabricated: the native 3/day source resource
        # remains the action's cost. Tongues is excluded in this arena, so
        # its otherwise shared source pool is not independently spent.
        name = str(row["name"]).title()
        return [TimedSelfBuffAction(
            id="enlarge-reduce", name=name, action_cost="action",
            resource_id="enlarge-reduce", duration_rounds=10,
            expiry_timing="source_turn_start", concentration=True,
            magical_effect=True, size_override=new_size,
            ability_check_advantage_abilities=["strength"],
            saving_throw_advantage_grants=[SavingThrowAdvantageGrant(
                source_id="enlarge-reduce-strength-save",
                source_name=name, abilities=["strength"],
            )],
            modifier_effects=[SpellModifierEffect(
                kind="bonus-damage", dice_count=1, dice_size=4,
                damage_type=damage.type,
                required_weapon_attack_kind="melee",
            )],
            priority=75, animation="buff",
        )]
    except Exception:
        logger.exception("2014 source Enlarge binding failed for %s.", monster.id)
        raise
