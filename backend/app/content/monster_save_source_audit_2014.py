from __future__ import annotations

import logging

from app.content.monster_arena_action_policy_2014 import action_label_2014
from app.content.monster_recharge_self_buffs_2014 import recharge_self_buff_bindings_2014
from app.content.monster_save_capability_support_2014 import (
    supports_recharge_rules_2014,
    supports_save_action_2014,
)
from app.content.monster_source_2014 import SourceMonster2014
from app.content.monster_source_asymmetric_saves_2014 import source_proven_asymmetric_saves_2014
from app.content.monster_source_audible_maintained_control_2014 import (
    source_proven_audible_maintained_controls_2014,
)
from app.content.monster_source_conditioned_saves_2014 import source_proven_conditioned_saves_2014
from app.content.monster_source_dreadful_glare_2014 import source_proven_dreadful_glare_2014
from app.content.monster_source_opening_area_saves_2014 import source_proven_opening_area_saves_2014
from app.content.monster_source_recharge_line_damage_2014 import source_proven_recharge_line_damage_2014
from app.content.monster_source_recharge_timed_controls_2014 import (
    source_proven_recharge_timed_controls_2014,
)
from app.content.monster_source_visual_save_bindings_2014 import source_proven_visual_saves_2014

logger = logging.getLogger(__name__)


def unsupported_save_actions_2014(monster: SourceMonster2014) -> list[object]:
    try:
        return [
            action for action in monster.saving_throw_actions
            if not supports_save_action_2014(action)
        ]
    except Exception:
        logger.exception("Failed unsupported save-action audit for %s.", monster.name)
        raise


def unsupported_source_actions_2014(
    monster: SourceMonster2014, *, recharge_supported: bool | None = None,
) -> list[str]:
    try:
        allowed = {attack.name.casefold() for attack in monster.attacks}
        allowed.update(
            str(action.get("name", "")).casefold()
            for action in monster.saving_throw_actions if isinstance(action, dict)
        )
        allowed.update(item.name.casefold() for item in source_proven_asymmetric_saves_2014(monster))
        allowed.update(item.name.casefold() for item in source_proven_visual_saves_2014(monster))
        allowed.update(item.name.casefold() for item in source_proven_conditioned_saves_2014(monster))
        allowed.update(item.name.casefold() for item in source_proven_dreadful_glare_2014(monster))
        allowed.update(item.name.casefold() for item in source_proven_opening_area_saves_2014(monster))
        allowed.update(
            item.name.casefold() for item in source_proven_audible_maintained_controls_2014(monster)
        )
        allowed.update(item.action.name.casefold() for item in recharge_self_buff_bindings_2014(monster))
        allowed.update(item.name.casefold() for item in source_proven_recharge_line_damage_2014(monster))
        allowed.update(
            item.name.casefold() for item in source_proven_recharge_timed_controls_2014(monster)
        )
        if (
            monster.multiattack_slots
            or monster.multiattack_policy is not None
            or monster.multiattack_binding is not None
        ):
            allowed.add("multiattack")
        if recharge_supported is None:
            recharge_supported = supports_recharge_rules_2014(monster)
        if recharge_supported:
            allowed.add("breath weapons")
        return [
            name for name in monster.action_names
            if action_label_2014(name) not in allowed
        ]
    except Exception:
        logger.exception("Failed to classify source actions for %s.", monster.name)
        raise
