from __future__ import annotations

from app.combat.encounter_targeting import combatant_distance
from app.combat.hit_points import effective_max_hp
from app.combat.pooled_healing import pooled_healing_capacity, resolve_pooled_healing
from app.content.monster_creature_types import is_creature_type
from app.domain.encounters import EncounterCombatant, EncounterSetup
from app.domain.models import BattleEvent

PRESERVE_LIFE = "preserve-life"


def healing_capacity(target: EncounterCombatant) -> int:
    try:
        return pooled_healing_capacity(target, 1, 2)
    except Exception:
        raise


def _legal_preserve_life_target(cleric: EncounterCombatant, target: EncounterCombatant) -> bool:
    try:
        if cleric.state.template.ruleset != "2014":
            return True
        return not (
            is_creature_type(target.state.template, "undead")
            or is_creature_type(target.state.template, "construct")
        )
    except Exception:
        raise


def preserve_life_targets(cleric: EncounterCombatant, setup: EncounterSetup) -> tuple[EncounterCombatant, ...]:
    allies = setup.heroes if cleric.side == "heroes" else setup.monsters
    legal = [
        target for target in allies
        if target.state.is_alive and not target.state.is_dead
        and combatant_distance(cleric, target) <= 30
        and _legal_preserve_life_target(cleric, target)
        and healing_capacity(target) > 0
    ]
    legal.sort(key=lambda target: (
        target.state.current_hp > 0,
        target.combatant_id == cleric.combatant_id,
        target.state.current_hp / effective_max_hp(target.state),
        combatant_distance(cleric, target),
        target.combatant_id,
    ))
    return tuple(legal)


def resolve_preserve_life(
    sequence: int,
    round_number: int,
    cleric: EncounterCombatant,
    targets: tuple[EncounterCombatant, ...],
    resource_remaining: int,
) -> BattleEvent:
    pool = 5 * (cleric.state.template.level or 0)
    if pool <= 0 or not targets:
        raise ValueError("Preserve Life requires a Cleric level and at least one worthwhile Bloodied target.")
    resolved, _ = resolve_pooled_healing(
        targets,
        pool,
        cap_numerator=1,
        cap_denominator=2,
    )
    allocations = [
        f"{target.state.template.name} +{restored} HP"
        for target, restored in resolved
    ]
    if not allocations:
        raise ValueError("Preserve Life had no legal healing allocation.")
    return BattleEvent(
        sequence=sequence, round_number=round_number, event_type="healing",
        actor_id=cleric.combatant_id, actor_name=cleric.state.template.name,
        feature_id=PRESERVE_LIFE, resource_remaining=resource_remaining,
        animation=PRESERVE_LIFE,
        description=f"{cleric.state.template.name} uses Preserve Life: {'; '.join(allocations)}.",
    )
