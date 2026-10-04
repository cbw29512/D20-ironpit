from __future__ import annotations

import logging
from typing import Literal

from app.combat.encounter_targeting import combatant_distance
from app.domain.encounters import EncounterCombatant, EncounterSetup

logger = logging.getLogger(__name__)

ContextRollKind = Literal["attack_roll", "ability_check"]


def _active_context_tags(member: EncounterCombatant, setup: EncounterSetup) -> set[str]:
    try:
        tags: set[str] = set()
        for source in [*setup.heroes, *setup.monsters]:
            active_effect_ids = {
                effect.source_effect_id
                for effect in source.state.timed_effects
                if effect.source_id == source.combatant_id and effect.source_effect_id is not None
            }
            for action in source.state.template.timed_self_buff_actions:
                aura = action.environment_context_aura
                if aura is None or action.id not in active_effect_ids:
                    continue
                if combatant_distance(source, member) <= aura.radius_ft:
                    tags.update(aura.context_tags)
        return tags
    except Exception as exc:
        logger.exception("Failed to resolve environment context for %s.", member.combatant_id)
        raise RuntimeError("Environment context could not be resolved.") from exc


def environment_context_disadvantage_sources(
    member: EncounterCombatant,
    setup: EncounterSetup | None,
    kind: ContextRollKind,
) -> int:
    """Return target-owned Disadvantage sources activated by universal context tags."""
    try:
        if setup is None:
            return 0
        active_tags = _active_context_tags(member, setup)
        total = 0
        for reaction in member.state.template.environment_context_reactions:
            if reaction.context_tag not in active_tags:
                continue
            if kind == "attack_roll" and reaction.attack_roll_disadvantage:
                total += 1
            elif kind == "ability_check" and reaction.ability_check_disadvantage:
                total += 1
        return total
    except Exception as exc:
        logger.exception(
            "Failed to resolve %s environment-context Disadvantage for %s.",
            kind,
            member.combatant_id,
        )
        raise RuntimeError("Environment-context Disadvantage could not be resolved.") from exc
