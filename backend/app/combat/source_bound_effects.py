from __future__ import annotations

from app.combat.condition_rules import is_incapacitated
from app.combat.timed_conditions import remove_effect_group
from app.domain.encounters import EncounterSetup
from app.domain.models import CombatantState


def end_damage_sensitive_effects(state: CombatantState) -> list[str]:
    removed: list[str] = []
    handled: set[tuple[str, str | None]] = set()
    for effect in list(state.timed_effects):
        key = (effect.source_id, effect.source_effect_id)
        if not effect.ends_on_damage or key in handled:
            continue
        handled.add(key)
        removed.extend(remove_effect_group(state, effect))
    return removed


def cleanup_disabled_source_effects(setup: EncounterSetup) -> None:
    members = [*setup.heroes, *setup.monsters]
    by_id = {member.combatant_id: member for member in members}
    for target in members:
        handled: set[tuple[str, str | None]] = set()
        for effect in list(target.state.timed_effects):
            key = (effect.source_id, effect.source_effect_id)
            if key in handled:
                continue
            source = by_id.get(effect.source_id)
            if source is None:
                continue
            dead = source.state.is_dead or not source.state.is_alive
            incapacitated = is_incapacitated(source.state)
            if (effect.ends_if_source_dead and dead) or (effect.ends_if_source_incapacitated and incapacitated):
                handled.add(key)
                remove_effect_group(target.state, effect)
