from __future__ import annotations

from dataclasses import dataclass

from app.combat.encounter_targeting import combatant_distance
from app.domain.effect_removal import EffectRemovalAction
from app.domain.encounters import EncounterCombatant, EncounterSetup


@dataclass(frozen=True)
class TrackedSpellEffect:
    target: EncounterCombatant
    source: EncounterCombatant
    effect_id: str
    spell_level: int


def _spell_level(source: EncounterCombatant, effect_id: str) -> int | None:
    template = source.state.template
    spells = [
        *template.defensive_spell_actions,
        *template.spell_save_actions,
        *template.spell_attack_actions,
    ]
    spell = next((item for item in spells if item.id == effect_id), None)
    return spell.level if spell is not None else None


def _target_allowed(
    remover: EncounterCombatant,
    target: EncounterCombatant,
    action: EffectRemovalAction,
) -> bool:
    if target.state.is_dead or not target.state.is_alive:
        return False
    same_side = target.side == remover.side
    if action.target_mode == "enemy" and same_side:
        return False
    if action.target_mode == "ally" and (not same_side or target.combatant_id == remover.combatant_id):
        return False
    if action.target_mode == "self_or_ally" and not same_side:
        return False
    return combatant_distance(remover, target) <= action.range_ft


def tracked_spell_effects(
    remover: EncounterCombatant,
    setup: EncounterSetup,
    action: EffectRemovalAction,
) -> list[TrackedSpellEffect]:
    members = [*setup.heroes, *setup.monsters]
    by_id = {member.combatant_id: member for member in members}
    found: dict[tuple[str, str, str], TrackedSpellEffect] = {}
    for target in members:
        if not _target_allowed(remover, target, action):
            continue
        for modifier in target.state.active_modifiers:
            source = by_id.get(modifier.source_id)
            if source is None:
                continue
            level = _spell_level(source, modifier.source_effect_id)
            if level is None:
                continue
            key = (target.combatant_id, source.combatant_id, modifier.source_effect_id)
            found[key] = TrackedSpellEffect(target, source, modifier.source_effect_id, level)
    return sorted(
        found.values(),
        key=lambda item: (-item.spell_level, combatant_distance(remover, item.target), item.effect_id),
    )
