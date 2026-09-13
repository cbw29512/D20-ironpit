from __future__ import annotations

from app.combat.damage_defenses import apply_damage_defenses
from app.combat.zero_hp import apply_damage
from app.domain.encounters import EncounterCombatant, EncounterSetup
from app.domain.models import BattleEvent, DamageRollComponent, DiceRoll


def _members(setup: EncounterSetup) -> list[EncounterCombatant]:
    return [*setup.heroes, *setup.monsters]


def _grapplers(source: EncounterCombatant, setup: EncounterSetup) -> list[EncounterCombatant]:
    by_id = {member.combatant_id: member for member in _members(setup)}
    ids = list(dict.fromkeys(item.source_id for item in source.state.grapple_sources))
    return [by_id[item] for item in ids if item in by_id and by_id[item].state.current_hp > 0 and not by_id[item].state.is_dead]


def resolve_start_turn_relationship_damage(
    sequence: int, round_number: int, source: EncounterCombatant, setup: EncounterSetup, dice,
) -> tuple[list[BattleEvent], int]:
    events: list[BattleEvent] = []
    affected = [member.state for member in _members(setup)]
    for profile in source.state.template.start_turn_relationship_damage:
        targets = _grapplers(source, setup) if profile.target_relationship == "grapplers" else []
        for target in targets:
            rolls = [dice.roll(profile.dice_size) for _ in range(profile.dice_count)]
            rolled = DamageRollComponent(
                source=profile.name, notation=f"{profile.dice_count}d{profile.dice_size}+{profile.damage_bonus}",
                rolls=rolls, modifier=profile.damage_bonus, damage_type=profile.damage_type,
                total=sum(rolls) + profile.damage_bonus,
            )
            applied, components = apply_damage_defenses(target.state, [rolled])
            hp_before = target.state.current_hp
            if applied:
                apply_damage(target.state, applied, damage_types={profile.damage_type}, dice=dice, affected_states=affected)
            events.append(BattleEvent(
                sequence=sequence, round_number=round_number, event_type="feature",
                actor_id=source.combatant_id, actor_name=source.state.template.name,
                target_id=target.combatant_id, target_name=target.state.template.name,
                feature_id=profile.id, damage_roll=DiceRoll(
                    notation=rolled.notation, rolls=rolls, modifier=profile.damage_bonus, total=applied,
                ), damage_components=components, hp_before=hp_before, hp_after=target.state.current_hp,
                animation="damage",
                description=f"{target.state.template.name} takes {applied} {profile.damage_type.value} damage from {source.state.template.name}'s {profile.name}.",
            ))
            sequence += 1
    return events, sequence
