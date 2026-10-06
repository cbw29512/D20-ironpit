from __future__ import annotations

import logging

from app.combat.grid_geometry import footprint_distance_ft
from app.combat.temporary_hp import grant_temporary_hit_points
from app.domain.encounters import EncounterCombatant, EncounterSetup
from app.domain.models import BattleEvent

logger = logging.getLogger(__name__)


def _member_by_id(setup: EncounterSetup, combatant_id: str | None) -> EncounterCombatant | None:
    if combatant_id is None:
        return None
    return next(
        (
            member
            for member in [*setup.heroes, *setup.monsters]
            if member.combatant_id == combatant_id
        ),
        None,
    )


def _zero_hp_grant_amount(source: EncounterCombatant, rule) -> int:
    scores = source.state.template.ability_scores
    level = source.state.template.level
    if scores is None or level is None:
        raise ValueError("Zero-HP Temporary HP trigger requires certified ability scores and level.")
    return max(
        rule.minimum,
        rule.flat_bonus + rule.per_level * level + scores.modifier(rule.ability),
    )


def _grant_zero_hp_temporary_hp(
    sequence: int,
    round_number: int,
    source: EncounterCombatant,
    rule,
    *,
    ally_kill: bool,
) -> BattleEvent:
    amount = _zero_hp_grant_amount(source, rule)
    before = source.state.temporary_hp
    after = grant_temporary_hit_points(source.state, amount)
    trigger = (
        "after an ally reduced a nearby hostile creature to 0 HP"
        if ally_kill
        else "after reducing a hostile creature to 0 HP"
    )
    return BattleEvent(
        sequence=sequence,
        round_number=round_number,
        event_type="feature",
        actor_id=source.combatant_id,
        actor_name=source.state.template.name,
        target_id=source.combatant_id,
        target_name=source.state.template.name,
        hp_before=source.state.current_hp,
        hp_after=source.state.current_hp,
        temporary_hp_before=before,
        temporary_hp_after=after,
        feature_id=rule.source_id,
        animation="feature",
        description=(
            f"{source.state.template.name} gains {amount} Temporary HP from {rule.source_name} "
            f"{trigger}."
        ),
    )



def _mark_source_zero_hp_bonus_attack_triggers(
    source: EncounterCombatant,
    triggering_event: BattleEvent,
    *,
    round_number: int,
    turn_key: str | None,
) -> None:
    """Mark fight-state eligibility for source-owned Bonus Action attacks after a qualifying melee kill."""
    grants = [
        grant
        for grant in source.state.template.bonus_attack_grants
        if grant.trigger == "source_melee_zero_hp_this_turn"
    ]
    if not grants or turn_key != f"{round_number}:{source.combatant_id}":
        return
    if triggering_event.event_type != "attack" or not triggering_event.attack_id:
        return
    attacks = [source.state.template.weapon_attack, *source.state.template.alternate_weapon_attacks]
    attack = next((item for item in attacks if item.id == triggering_event.attack_id), None)
    if attack is None or attack.weapon.attack_kind.value != "melee":
        return
    for grant in grants:
        source.state.feature_last_turn_keys[f"bonus-attack-trigger:{grant.id}"] = turn_key

def resolve_source_zero_hp_triggers(
    sequence: int,
    round_number: int,
    source: EncounterCombatant,
    triggering_event: BattleEvent,
    setup: EncounterSetup,
    *,
    turn_key: str | None = None,
) -> tuple[list[BattleEvent], int]:
    """Resolve source-owned effects triggered by reducing a hostile creature to 0 HP."""
    try:
        rule = source.state.template.progression_features.source_reduces_hostile_to_zero_hp_temporary_hp
        has_bonus_trigger = any(
            grant.trigger == "source_melee_zero_hp_this_turn"
            for grant in source.state.template.bonus_attack_grants
        )
        if rule is None and not has_bonus_trigger:
            return [], sequence
        if triggering_event.actor_id != source.combatant_id:
            raise ValueError("Zero-HP trigger source must match the triggering event actor.")

        target = _member_by_id(setup, triggering_event.target_id)
        if target is None or target.combatant_id == source.combatant_id or target.side == source.side:
            return [], sequence
        if triggering_event.hp_before is None or triggering_event.hp_after is None:
            return [], sequence
        if triggering_event.hp_before <= 0 or triggering_event.hp_after != 0:
            return [], sequence

        _mark_source_zero_hp_bonus_attack_triggers(
            source, triggering_event, round_number=round_number, turn_key=turn_key,
        )
        if rule is None:
            return [], sequence

        event = _grant_zero_hp_temporary_hp(sequence, round_number, source, rule, ally_kill=False)
        return [event], sequence + 1
    except ValueError:
        raise
    except Exception as exc:
        logger.exception("Source zero-HP trigger dispatch failed after event %s.", triggering_event.sequence)
        raise RuntimeError("Source zero-HP trigger could not be resolved.") from exc


def resolve_witnessed_zero_hp_triggers(
    sequence: int,
    round_number: int,
    killer: EncounterCombatant,
    triggering_event: BattleEvent,
    setup: EncounterSetup,
) -> tuple[list[BattleEvent], int]:
    """Grant ally-range Temporary HP when someone else reduces a nearby hostile to 0 HP."""
    try:
        target = _member_by_id(setup, triggering_event.target_id)
        if target is None or triggering_event.hp_before is None or triggering_event.hp_after is None:
            return [], sequence
        if triggering_event.hp_before <= 0 or triggering_event.hp_after != 0:
            return [], sequence
        events: list[BattleEvent] = []
        for member in [*setup.heroes, *setup.monsters]:
            if member.combatant_id == killer.combatant_id:
                continue
            rule = member.state.template.progression_features.source_reduces_hostile_to_zero_hp_temporary_hp
            if rule is None or rule.ally_zero_hp_range_ft <= 0:
                continue
            if target.combatant_id == member.combatant_id or target.side == member.side:
                continue
            if member.state.position is None or target.state.position is None:
                continue
            distance = footprint_distance_ft(
                member.state.position,
                member.state.template.size,
                target.state.position,
                target.state.template.size,
            )
            if distance > rule.ally_zero_hp_range_ft:
                continue
            events.append(
                _grant_zero_hp_temporary_hp(sequence, round_number, member, rule, ally_kill=True)
            )
            sequence += 1
        return events, sequence
    except ValueError:
        raise
    except Exception as exc:
        logger.exception("Ally-range zero-HP trigger dispatch failed after event %s.", triggering_event.sequence)
        raise RuntimeError("Ally-range zero-HP trigger could not be resolved.") from exc
