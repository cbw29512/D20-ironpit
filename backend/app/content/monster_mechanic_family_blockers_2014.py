"""Source-side mechanical blocker-family classification for 2014 monsters.

No combat-state changes or printed-name runtime dispatch. The call site owns
its already-verified recharge eligibility so one monster is not checked twice.
"""
from __future__ import annotations

import logging

from app.content.monster_conditional_damage_defenses_2014 import remaining_unsupported_defense_text_2014
from app.content.monster_healing_2014 import healing_actions_2014, supports_healing_2014
from app.content.monster_innate_support_2014 import innate_spell_resources_2014, supports_innate_spellcasting_2014
from app.content.monster_legendary_bindings_2014 import supports_legendary_actions_2014
from app.content.monster_regeneration_2014 import supports_regeneration_2014
from app.content.monster_save_capabilities_2014 import unsupported_save_actions_2014
from app.content.monster_source_2014 import SourceMonster2014
from app.content.monster_zero_hp_prevention_2014 import supports_zero_hp_prevention_2014

logger = logging.getLogger(__name__)


def mechanic_family_blockers_2014(
    monster: SourceMonster2014, *, recharge_supported: bool,
) -> list[str]:
    """Compose the existing source blockers without adding engine behavior."""
    try:
        bound_limited = set()
        if supports_healing_2014(monster):
            # Reuse the source's existing healing resource binding
            bound_limited.update(action.resource_id for action in healing_actions_2014(monster) if action.resource_id)
        if supports_innate_spellcasting_2014(monster):
            # Reuse the source's existing innate resource binding
            bound_limited.update(item.id for item in innate_spell_resources_2014(monster))
        unbound_limited = {
            key: value for key, value in monster.limited_action_uses.items()
            if key not in bound_limited
        }
        families = {
            "defense": remaining_unsupported_defense_text_2014(monster),
            "save-action": unsupported_save_actions_2014(monster),
            "swallow": monster.swallow_actions,
            "death-trigger": monster.death_trigger_actions,
            "healing": monster.healing_actions if not supports_healing_2014(monster) else None,
            "limited-use": unbound_limited,
            "spellcasting": (
                None if (
                    supports_innate_spellcasting_2014(monster) and not monster.spellcasting
                ) else (monster.innate_spellcasting or monster.spellcasting)
            ),
            "zero-hp": monster.zero_hp_prevention if not supports_zero_hp_prevention_2014(monster) else None,
            "regeneration": monster.regeneration if not supports_regeneration_2014(monster) else None,
            "legendary": (
                None if supports_legendary_actions_2014(monster)
                else (
                    monster.legendary_actions or monster.legendary_action_uses
                    or monster.unsupported_legendary_action_names
                )
            ),
            "recharge": (
                monster.action_recharges or monster.rest_recharge_action_ids
            ) if not recharge_supported else {},
        }
        return [f"mechanic:{name}" for name, value in families.items() if value]
    except Exception:
        logger.exception("Failed mechanic-family classification for %s.", monster.name)
        raise
