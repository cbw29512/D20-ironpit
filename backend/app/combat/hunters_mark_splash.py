from __future__ import annotations

import logging

from app.combat.damage_defenses import apply_damage_defenses
from app.combat.encounter_targeting import combatant_distance
from app.combat.zero_hp import apply_damage
from app.domain.encounters import EncounterSetup
from app.domain.models import CombatantState, DamageRollComponent

logger = logging.getLogger(__name__)
_MARK_SOURCES = frozenset({"hunter's mark", "hunters-mark"})
_SPLASH_KEY = "superior-hunters-prey"


def _mark_component(components: list[DamageRollComponent]) -> DamageRollComponent | None:
    return next(
        (
            item for item in components
            if item.source.casefold() in _MARK_SOURCES and (item.applied_total or item.total) > 0
        ),
        None,
    )


def resolve_hunters_mark_splash(
    attacker: CombatantState,
    attacker_id: str,
    primary_id: str,
    components: list[DamageRollComponent],
    turn_key: str | None,
    setup: EncounterSetup | None,
    dice,
    affected_states: list[CombatantState] | None,
) -> DamageRollComponent | None:
    """Once per turn, copy Hunter's Mark extra damage to a second creature within range."""
    try:
        range_ft = attacker.template.progression_features.hunters_mark_splash_range_ft
        if range_ft <= 0 or setup is None or not turn_key:
            return None
        if attacker.feature_last_turn_keys.get(_SPLASH_KEY) == turn_key:
            return None
        mark = _mark_component(components)
        if mark is None:
            return None
        members = [*setup.heroes, *setup.monsters]
        source = next((item for item in members if item.combatant_id == attacker_id), None)
        primary = next((item for item in members if item.combatant_id == primary_id), None)
        if source is None or primary is None:
            return None
        splash_target = next(
            (
                item for item in members
                if item.combatant_id not in {attacker_id, primary_id}
                and item.side != source.side
                and item.state.current_hp > 0
                and not item.state.is_dead
                and combatant_distance(source, item) <= range_ft
            ),
            None,
        )
        if splash_target is None:
            return None
        attacker.feature_last_turn_keys[_SPLASH_KEY] = turn_key
        splash = mark.model_copy(update={"source": "Superior Hunter's Prey", "applied_total": None})
        applied, adjusted = apply_damage_defenses(splash_target.state, [splash])
        apply_damage(
            splash_target.state, applied, critical=False,
            damage_types={splash.damage_type}, dice=dice,
            affected_states=affected_states, setup=setup,
        )
        return adjusted[0] if adjusted else splash.model_copy(update={"applied_total": applied})
    except Exception:
        logger.exception("Hunter's Mark splash failed for %s.", attacker.template.name)
        raise
