from __future__ import annotations

from app.combat.hit_points import effective_max_hp
from app.combat.zero_hp import restore_hit_points
from app.domain.encounters import EncounterCombatant, EncounterSetup
from app.domain.models import BattleEvent
from app.domain.traits import CombatTrait

PRESERVE_LIFE = "preserve-life"


def healing_capacity(target: EncounterCombatant) -> int:
    return max(0, effective_max_hp(target.state) // 2 - target.state.current_hp)


def preserve_life_targets(cleric: EncounterCombatant, setup: EncounterSetup) -> tuple[EncounterCombatant, ...]:
    allies = setup.heroes if cleric.side == "heroes" else setup.monsters
    legal = [
        target for target in allies
        if target.state.is_alive and not target.state.is_dead
        and abs(cleric.position_ft - target.position_ft) <= 30
        and CombatTrait.SWARM not in target.state.template.combat_traits
        and healing_capacity(target) > 0
    ]
    legal.sort(key=lambda target: (
        target.state.current_hp > 0,
        target.combatant_id == cleric.combatant_id,
        target.state.current_hp / effective_max_hp(target.state),
        abs(cleric.position_ft - target.position_ft),
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
    allocations: list[str] = []
    for target in targets:
        if pool <= 0:
            break
        amount = min(pool, healing_capacity(target))
        if amount <= 0:
            continue
        restored = restore_hit_points(target.state, amount)
        if restored:
            allocations.append(f"{target.state.template.name} +{restored} HP")
            pool -= restored
    if not allocations:
        raise ValueError("Preserve Life had no legal healing allocation.")
    return BattleEvent(
        sequence=sequence, round_number=round_number, event_type="healing",
        actor_id=cleric.combatant_id, actor_name=cleric.state.template.name,
        feature_id=PRESERVE_LIFE, resource_remaining=resource_remaining,
        animation=PRESERVE_LIFE,
        description=f"{cleric.state.template.name} uses Preserve Life: {'; '.join(allocations)}.",
    )
