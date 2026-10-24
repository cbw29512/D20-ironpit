"""Classify fully supported 2014 source Actions without identity dispatch."""
from __future__ import annotations

import logging

from app.content.monster_animate_chains_2014 import supports_animate_chains_arena_unavailable_2014
from app.content.monster_arena_action_policy_2014 import (
    PIT_BANNED_ACTION_LABELS_2014,
    source_proven_ethereal_shift_action_2014,
)
from app.content.monster_arena_unavailable_reactions_2014 import arena_unavailable_reaction_names_2014
from app.content.monster_change_shape_policy_2014 import approved_inert_change_shape_2014
from app.content.monster_fetid_cloud_2014 import fetid_cloud_zone_2014
from app.content.monster_healing_2014 import healing_action_names_2014
from app.content.monster_informational_action_proofs_2014 import verified_nonactionable_action_2014
from app.content.monster_innate_support_2014 import innate_spell_names_2014
from app.content.monster_legendary_bindings_2014 import supports_legendary_actions_2014
from app.content.monster_rock_catching_2014 import supports_rock_catching_reaction_2014
from app.content.monster_save_capabilities_2014 import unsupported_source_actions_2014
from app.content.monster_source_2014 import SourceMonster2014
from app.content.monster_source_invisibility_2014 import source_invisibility_action_2014
from app.content.monster_unnerving_mask_2014 import supports_unnerving_mask_reaction_2014
from app.content.monster_visual_disguise_2014 import visual_disguise_action_2014

logger = logging.getLogger(__name__)

_ARENA_ABSENT_CONTEXT_ACTION_LABELS = frozenset({"ink cloud"})
_ARENA_UNAVAILABLE_SUMMON_ACTION_LABELS = frozenset({
    "animate trees", "children of the night", "create specter",
})
_ARENA_NEUTRAL_MIND_ACTION_LABELS = frozenset({"weird insight"})


def action_label_from_name(name: str) -> str:
    try:
        from app.content.monster_arena_action_policy_2014 import action_label_2014
        return action_label_2014(name).split(" (", 1)[0]
    except Exception:
        logger.exception("Failed to normalize 2014 source Action label %s.", name)
        raise


def _leadership_labels(monster: SourceMonster2014) -> set[str]:
    try:
        from app.content.monster_leadership_2014 import leadership_labels_2014
        return leadership_labels_2014(monster)
    except Exception:
        logger.exception("Failed to classify Leadership labels for %s.", monster.name)
        raise


def supports_parry_reaction_2014(monster: SourceMonster2014) -> bool:
    try:
        return monster.reaction_names == ["Parry"] and monster.parry_ac_bonus is not None
    except Exception:
        logger.exception("Failed to classify 2014 Parry support for %s.", monster.name)
        raise


def source_name_blockers_2014(
    monster: SourceMonster2014, *, recharge_supported: bool,
) -> list[str]:
    """Return source-shape blockers after all source-proven universal bindings."""
    try:
        extras = unsupported_source_actions_2014(
            monster, recharge_supported=recharge_supported,
        )
        disguise = visual_disguise_action_2014(monster)
        allowed_extras = (
            healing_action_names_2014(monster)
            | innate_spell_names_2014(monster)
            | {action.name.casefold() for action in source_invisibility_action_2014(monster)}
            | PIT_BANNED_ACTION_LABELS_2014
            | _ARENA_ABSENT_CONTEXT_ACTION_LABELS
            | _ARENA_UNAVAILABLE_SUMMON_ACTION_LABELS
            | _ARENA_NEUTRAL_MIND_ACTION_LABELS
            | {
                action_label_from_name(name)
                for name in monster.action_names
                if source_proven_ethereal_shift_action_2014(monster, name)
            }
            | ({"animate chains"} if supports_animate_chains_arena_unavailable_2014(monster) else set())
            | ({"change shape"} if approved_inert_change_shape_2014(monster) else set())
            | _leadership_labels(monster)
            | {
                action_label_from_name(zone.name)
                for zone in (fetid_cloud_zone_2014(monster),)
                if zone is not None
            }
            | ({action_label_from_name(disguise.name)} if disguise is not None else set())
        )
        extras = [
            name for name in extras
            if action_label_from_name(name) not in allowed_extras
            and not verified_nonactionable_action_2014(monster, name)
        ]
        blockers: list[str] = []
        if extras:
            blockers.append("source:extra-action")
        if monster.legendary_action_names and not supports_legendary_actions_2014(monster):
            blockers.append("source:legendary")
        if (
            set(monster.reaction_names) - arena_unavailable_reaction_names_2014(monster)
            or monster.parry_ac_bonus is not None
        ) and not (
            supports_parry_reaction_2014(monster)
            or supports_rock_catching_reaction_2014(monster)
            or supports_unnerving_mask_reaction_2014(monster)
        ):
            blockers.append("source:reaction")
        return blockers
    except Exception:
        logger.exception("Failed to classify 2014 source Actions for %s.", monster.name)
        raise
