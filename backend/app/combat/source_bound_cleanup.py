from __future__ import annotations

import logging

from app.combat.condition_rules import is_incapacitated
from app.combat.timed_conditions import remove_effect_group
from app.domain.encounters import EncounterSetup

logger = logging.getLogger(__name__)


def cleanup_disabled_source_effects(setup: EncounterSetup) -> None:
    """End source-owned effects whose declared source-state exit is satisfied."""
    try:
        members = [*setup.heroes, *setup.monsters]
        by_id = {member.combatant_id: member for member in members}
        for source in members:
            rule = source.state.template.visual_disguise_action
            dead = (
                source.state.is_dead
                or not source.state.is_alive
                or source.state.current_hp <= 0
            )
            if (
                rule is not None
                and rule.ends_if_owner_dead
                and dead
                and source.state.magical_visual_disguise_active
            ):
                source.state.magical_visual_disguise_active = False

        for target in members:
            handled: set[tuple[str, str | None]] = set()
            for effect in list(target.state.timed_effects):
                key = (effect.source_id, effect.source_effect_id)
                if key in handled:
                    continue
                source = by_id.get(effect.source_id)
                if source is None:
                    continue
                dead = (
                    source.state.is_dead
                    or not source.state.is_alive
                    or source.state.current_hp <= 0
                )
                incapacitated = is_incapacitated(source.state)
                if (
                    (effect.ends_if_source_dead and dead)
                    or (
                        effect.ends_if_source_incapacitated
                        and incapacitated
                    )
                ):
                    handled.add(key)
                    remove_effect_group(
                        target.state,
                        effect,
                        grant_source_immunity=False,
                    )
    except Exception as exc:
        logger.exception("Disabled source-effect cleanup failed.")
        raise RuntimeError("Disabled source effects could not be cleaned up.") from exc
