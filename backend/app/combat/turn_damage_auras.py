from __future__ import annotations

from app.combat.barbarian import end_rage_if_incapacitated
from app.combat.condition_rules import is_incapacitated
from app.combat.damage_defenses import apply_damage_defenses
from app.combat.dice import DiceProvider
from app.combat.encounter_targeting import combatant_distance
from app.combat.zero_hp import apply_damage
from app.domain.encounters import EncounterCombatant, EncounterSetup
from app.domain.models import BattleEvent, DamageRollComponent, DiceRoll


def _targets(source: EncounterCombatant, setup: EncounterSetup, radius_ft: int, target_mode: str):
    if target_mode == "enemies":
        candidates = setup.monsters if source.side == "heroes" else setup.heroes
    elif target_mode == "all-creatures":
        candidates = [*setup.heroes, *setup.monsters]
    else:
        raise ValueError(f"Unsupported aura target mode {target_mode!r}.")
    return [
        member for member in candidates
        if member.combatant_id != source.combatant_id
        and member.state.is_alive and not member.state.is_dead
        and combatant_distance(source, member) <= radius_ft
    ]


def resolve_end_turn_damage_auras(
    sequence: int,
    round_number: int,
    source: EncounterCombatant,
    setup: EncounterSetup,
    dice: DiceProvider,
) -> tuple[list[BattleEvent], int]:
    events: list[BattleEvent] = []
    affected_states = [member.state for member in [*setup.heroes, *setup.monsters]]
    for aura in source.state.template.turn_damage_auras:
        if aura.suppressed_if_incapacitated and is_incapacitated(source.state):
            continue
        targets = _targets(source, setup, aura.radius_ft, aura.target_mode)
        if not targets:
            continue
        rolls = [dice.roll(aura.dice_size) for _ in range(aura.dice_count)]
        raw_total = max(0, sum(rolls) + aura.damage_bonus)
        notation = f"{aura.dice_count}d{aura.dice_size}"
        if aura.damage_bonus:
            notation += f"{aura.damage_bonus:+d}"
        for target in targets:
            hp_before = target.state.current_hp
            temporary_hp_before = target.state.temporary_hp
            component = DamageRollComponent(
                source=aura.name,
                notation=notation,
                rolls=rolls,
                modifier=aura.damage_bonus,
                damage_type=aura.damage_type,
                total=raw_total,
            )
            applied_total, components = apply_damage_defenses(target.state, [component])
            if applied_total:
                applied_types = {part.damage_type for part in components if (part.applied_total or 0) > 0}
                apply_damage(
                    target.state,
                    applied_total,
                    damage_types=applied_types,
                    dice=dice,
                    affected_states=affected_states,
                )
                end_rage_if_incapacitated(target.state)
            events.append(BattleEvent(
                sequence=sequence,
                round_number=round_number,
                event_type="feature",
                actor_id=source.combatant_id,
                actor_name=source.state.template.name,
                target_id=target.combatant_id,
                target_name=target.state.template.name,
                damage_roll=DiceRoll(
                    notation=notation,
                    rolls=rolls,
                    modifier=aura.damage_bonus,
                    total=applied_total,
                ),
                damage_components=components,
                hp_before=hp_before,
                hp_after=target.state.current_hp,
                temporary_hp_before=temporary_hp_before,
                temporary_hp_after=target.state.temporary_hp,
                is_dead=target.state.is_dead,
                feature_id=aura.id,
                animation="aura",
                description=f"{source.state.template.name}'s {aura.name} deals {applied_total} {aura.damage_type.value} damage to {target.state.template.name}.",
            ))
            sequence += 1
    return events, sequence
