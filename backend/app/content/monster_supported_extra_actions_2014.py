"""Source-verified auxiliary action labels permitted by the 2014 arena classifier.

Only already compiled mechanics or locked arena exceptions may clear blockers.
An unfamiliar source action stays blocked rather than being ignored.
"""
from __future__ import annotations

import logging

from app.content.monster_arena_action_policy_2014 import (
    PIT_BANNED_ACTION_LABELS_2014, action_label_2014,
    source_proven_ethereal_shift_action_2014,
)
from app.content.monster_animate_chains_2014 import supports_animate_chains_arena_unavailable_2014
from app.content.monster_change_shape_policy_2014 import approved_inert_change_shape_2014
from app.content.monster_fetid_cloud_2014 import fetid_cloud_zone_2014
from app.content.monster_healing_2014 import healing_action_names_2014
from app.content.monster_innate_support_2014 import innate_spell_names_2014
from app.content.monster_leadership_2014 import leadership_labels_2014
from app.content.monster_source_2014 import SourceMonster2014
from app.content.monster_source_etherealness_2014 import verified_unavailable_etherealness_2014
from app.content.monster_source_invisibility_2014 import source_invisibility_action_2014
from app.content.monster_source_scare_2014 import source_scare_2014
from app.content.monster_source_limited_audible_conditions_2014 import (
    source_proven_limited_audible_conditions_2014,
)
from app.content.monster_visual_disguise_2014 import visual_disguise_action_2014
from app.content.monster_grapple_swallow_source_2014 import source_grapple_swallow_2014

logger = logging.getLogger(__name__)

_ARENA_ABSENT_CONTEXT = frozenset({"ink cloud"})
_UNAVAILABLE_SUMMONS = frozenset({"animate trees", "children of the night", "create specter"})
_NEUTRAL_MIND_ACTIONS = frozenset({"weird insight"})


def _label(name: str) -> str:
    # Match the existing classifier's normalization of printed action headings.
    return action_label_2014(name).split(" (", 1)[0]


def source_supported_extra_action_labels_2014(monster: SourceMonster2014) -> set[str]:
    """Allow only verified existing capabilities or explicitly arena-inert actions."""
    try:
        allowed = (
            healing_action_names_2014(monster)
            | innate_spell_names_2014(monster)
            | {_label(action.name) for action in source_invisibility_action_2014(monster)}
            | {
                _label(action.name)
                for action in source_proven_limited_audible_conditions_2014(monster)
            }
            | {_label(action.name) for action in source_scare_2014(monster)}
            | PIT_BANNED_ACTION_LABELS_2014
            | {
                _label(name) for name in monster.action_names
                if verified_unavailable_etherealness_2014(monster, name)
            }
            | _ARENA_ABSENT_CONTEXT
            | _UNAVAILABLE_SUMMONS
            | _NEUTRAL_MIND_ACTIONS
            | {
                _label(name)
                for name in monster.action_names
                if source_proven_ethereal_shift_action_2014(monster, name)
            }
            | ({"animate chains"} if supports_animate_chains_arena_unavailable_2014(monster) else set())
            | ({"change shape"} if approved_inert_change_shape_2014(monster) else set())
            | leadership_labels_2014(monster)
            | {
                _label(zone.name)
                for zone in (fetid_cloud_zone_2014(monster),)
                if zone is not None
            }
        )
        # An illusion is NOT arena-neutral. Accept it only when the full printed
        # source compiles into the shared action/inspection/dismissal runtime.
        disguise = visual_disguise_action_2014(monster)
        if disguise is not None:
            allowed.add(_label(disguise.name))
        swallow = source_grapple_swallow_2014(monster)
        if swallow is not None:
            allowed.add(_label(swallow.source_name))
        return allowed
    except Exception:
        logger.exception("Could not classify verified extra actions for %s", monster.id)
        raise
