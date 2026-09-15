from __future__ import annotations

from app.combat.action_economy import is_available, spend
from app.combat.encounter_targeting import combatant_distance
from app.domain.encounters import EncounterCombatant, EncounterSetup
from app.domain.models import BattleEvent
from app.domain.ongoing_damage import OngoingDamageState


def source_attacks_blocked(source_id: str, opponents) -> bool:
    return any(
        ongoing.source_id == source_id and ongoing.effect.blocks_source_attacks
        for state in opponents
        for ongoing in state.ongoing_damage_effects
    )


def choose_action_removal(
    member: EncounterCombatant, setup: EncounterSetup,
) -> tuple[EncounterCombatant, OngoingDamageState] | None:
    if not is_available(member.state, "action"):
        return None
    allies = setup.heroes if member.side == "heroes" else setup.monsters
    ordered = [member, *(ally for ally in allies if ally.combatant_id != member.combatant_id)]
    for target in ordered:
        if target.state.is_dead or not target.state.is_alive:
            continue
        for ongoing in target.state.ongoing_damage_effects:
            effect = ongoing.effect
            if effect.action_removable and combatant_distance(member, target) <= effect.action_removal_range_ft:
                return target, ongoing
    return None


def resolve_action_removal(
    sequence: int, round_number: int, member: EncounterCombatant,
    target: EncounterCombatant, ongoing: OngoingDamageState,
) -> BattleEvent:
    if not is_available(member.state, "action"):
        raise ValueError("Action is unavailable for attachment removal.")
    if ongoing not in target.state.ongoing_damage_effects:
        raise ValueError("Attachment is no longer active.")
    if combatant_distance(member, target) > ongoing.effect.action_removal_range_ft:
        raise ValueError("Attachment is out of removal range.")
    spend(member.state, "action")
    target.state.ongoing_damage_effects.remove(ongoing)
    return BattleEvent(
        sequence=sequence, round_number=round_number, event_type="feature",
        actor_id=member.combatant_id, actor_name=member.state.template.name,
        target_id=target.combatant_id, target_name=target.state.template.name,
        feature_id=f"remove-{ongoing.effect.id}", animation="condition-remove",
        description=f"{member.state.template.name} uses its action to remove {ongoing.effect.name} from {target.state.template.name}.",
    )


def detach_source_with_movement(
    source: EncounterCombatant, setup: EncounterSetup,
) -> bool:
    for target in [*setup.heroes, *setup.monsters]:
        for ongoing in list(target.state.ongoing_damage_effects):
            cost = ongoing.effect.source_detach_movement_ft
            if ongoing.source_id != source.combatant_id or cost is None:
                continue
            if source.state.movement_remaining_ft < cost:
                return False
            source.state.movement_remaining_ft -= cost
            target.state.ongoing_damage_effects.remove(ongoing)
            return True
    return False
