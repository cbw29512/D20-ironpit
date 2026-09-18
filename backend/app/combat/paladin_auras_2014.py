from __future__ import annotations

import logging

from app.combat.condition_rules import is_incapacitated
from app.combat.encounter_targeting import combatant_distance
from app.combat.modifier_stack import add_modifier
from app.domain.encounters import EncounterCombatant, EncounterSetup
from app.domain.modifiers import CombatModifier, ModifierKind

logger = logging.getLogger(__name__)
_AURA_EFFECTS = {
    "aura-of-protection-2014",
    "aura-of-devotion-2014",
    "aura-of-courage-2014",
}


def _members(setup: EncounterSetup) -> list[EncounterCombatant]:
    return [*setup.heroes, *setup.monsters]


def _active_source(member: EncounterCombatant) -> bool:
    state = member.state
    return state.is_alive and not state.is_dead and state.current_hp > 0 and not is_incapacitated(state)


def _clear_aura_modifiers(setup: EncounterSetup) -> None:
    for member in _members(setup):
        member.state.active_modifiers = [
            item for item in member.state.active_modifiers
            if item.source_effect_id not in _AURA_EFFECTS
        ]


def _nearby_sources(target: EncounterCombatant, setup: EncounterSetup) -> list[EncounterCombatant]:
    side_members = setup.heroes if target.side == "heroes" else setup.monsters
    return [
        source for source in side_members
        if source.combatant_id != target.combatant_id
        and _active_source(source)
        and combatant_distance(source, target) <= 10
    ]


def _apply_save_aura(target: EncounterCombatant, sources: list[EncounterCombatant]) -> None:
    own = target.state.template.progression_features.aura_of_protection_2014_bonus
    candidates = [
        (source.state.template.progression_features.aura_of_protection_2014_bonus, source)
        for source in sources
        if source.state.template.progression_features.aura_of_protection_2014_bonus > 0
    ]
    if not candidates:
        return
    best_bonus, source = max(candidates, key=lambda item: (item[0], item[1].combatant_id))
    extra = max(0, best_bonus - own)
    if extra <= 0:
        return
    add_modifier(target.state, CombatModifier(
        id=f"{source.combatant_id}:aura-of-protection-2014:{target.combatant_id}",
        source_id=source.combatant_id,
        source_effect_id="aura-of-protection-2014",
        kind=ModifierKind.SAVING_THROW_FLAT,
        flat_bonus=extra,
    ))


def _apply_condition_aura(
    target: EncounterCombatant,
    sources: list[EncounterCombatant],
    feature_name: str,
    effect_id: str,
    condition_id: str,
) -> None:
    if condition_id in target.state.template.condition_immunities:
        return
    source = next((
        member for member in sources
        if bool(getattr(member.state.template.progression_features, feature_name))
    ), None)
    if source is None:
        return
    add_modifier(target.state, CombatModifier(
        id=f"{source.combatant_id}:{effect_id}:{target.combatant_id}",
        source_id=source.combatant_id,
        source_effect_id=effect_id,
        kind=ModifierKind.CONDITION_IMMUNITY,
        condition_id=condition_id,
    ))


def sync_paladin_auras_2014(setup: EncounterSetup) -> None:
    """Refresh non-stacking 10-foot 2014 Paladin aura effects from current encounter positions."""
    try:
        _clear_aura_modifiers(setup)
        for target in _members(setup):
            sources = _nearby_sources(target, setup)
            _apply_save_aura(target, sources)
            _apply_condition_aura(
                target, sources, "aura_of_devotion_2014", "aura-of-devotion-2014", "charmed",
            )
            _apply_condition_aura(
                target, sources, "aura_of_courage_2014", "aura-of-courage-2014", "frightened",
            )
    except Exception:
        logger.exception("Failed to synchronize 2014 Paladin auras.")
        raise
