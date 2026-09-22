from __future__ import annotations

from app.combat.action_economy import spend
from app.combat.defensive_modifier_rules import healing_is_maximized
from app.combat.healing import _resource_available, _slot_heal, _target_allowed
from app.combat.hit_points import effective_max_hp
from app.combat.spellcasting import mark_slot_spell_cast
from app.combat.zero_hp import restore_hit_points
from app.domain.encounters import EncounterCombatant, EncounterSetup
from app.domain.models import BattleEvent, DiceRoll, HealingAction


def choose_group_healing_targets(
    healer: EncounterCombatant,
    setup: EncounterSetup,
    action: HealingAction,
    turn_key: str | None = None,
) -> list[EncounterCombatant]:
    if action.max_targets <= 1 or not _resource_available(healer, action, turn_key):
        return []
    allies = setup.heroes if healer.side == "heroes" else setup.monsters
    legal = [target for target in allies if _target_allowed(healer, target, action)]
    legal.sort(key=lambda target: (
        target.state.current_hp > 0,
        target.state.current_hp / max(1, effective_max_hp(target.state)),
        target.combatant_id,
    ))
    worthwhile = [
        target for target in legal
        if target.state.current_hp == 0
        or target.state.current_hp * 2 <= effective_max_hp(target.state)
    ]
    return worthwhile[:action.max_targets]


def resolve_group_healing(
    sequence: int,
    round_number: int,
    healer: EncounterCombatant,
    targets: list[EncounterCombatant],
    action: HealingAction,
    dice,
    turn_key: str | None = None,
) -> tuple[list[BattleEvent], int]:
    if action.max_targets <= 1 or not targets or len(targets) > action.max_targets:
        raise ValueError("Group healing requires one or more legal targets within max_targets.")
    if any(not _target_allowed(healer, target, action) for target in targets):
        raise ValueError("Group healing contains an illegal target.")
    if not _resource_available(healer, action, turn_key):
        raise ValueError("Group healing resource is unavailable.")
    if _slot_heal(action):
        if turn_key is None:
            raise ValueError("Spell-slot group healing requires an active turn key.")
        mark_slot_spell_cast(healer.state, turn_key)
    spend(healer.state, action.action_cost)
    remaining = None
    if action.resource_id is not None:
        resource = next(item for item in healer.state.resources if item.id == action.resource_id)
        resource.current_uses -= action.resource_cost
        remaining = resource.current_uses
    events: list[BattleEvent] = []
    notation = f"{action.dice_count}d{action.dice_size}+{action.healing_bonus}"
    for target in targets:
        rolls = [action.dice_size for _ in range(action.dice_count)] if healing_is_maximized(target.state) else [
            dice.roll(action.dice_size) for _ in range(action.dice_count)
        ]
        total = sum(rolls) + action.healing_bonus
        before = target.state.current_hp
        healed = restore_hit_points(target.state, total)
        events.append(BattleEvent(
            sequence=sequence, round_number=round_number, event_type="healing",
            actor_id=healer.combatant_id, actor_name=healer.state.template.name,
            target_id=target.combatant_id, target_name=target.state.template.name,
            healing_roll=DiceRoll(notation=notation, rolls=rolls, modifier=action.healing_bonus, total=total),
            hp_before=before, hp_after=target.state.current_hp,
            death_save_successes=target.state.death_save_successes,
            death_save_failures=target.state.death_save_failures,
            is_stable=target.state.is_stable, is_dead=target.state.is_dead,
            feature_id=action.id, resource_remaining=remaining, animation=action.animation,
            description=f"{healer.state.template.name} uses {action.name} on {target.state.template.name} and restores {healed} HP.",
        ))
        sequence += 1
    return events, sequence
