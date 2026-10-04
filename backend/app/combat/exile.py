from __future__ import annotations

import logging

from app.combat.damage_defenses import apply_damage_defenses
from app.combat.exile_hit_effects import apply_exile_hit_riders, exile_save_succeeded
from app.combat.resources import resource_state
from app.combat.timed_condition_lifecycle import remove_effect_group
from app.combat.timed_conditions import apply_timed_condition
from app.combat.zero_hp import apply_damage
from app.domain.encounters import EncounterCombatant, EncounterSetup
from app.domain.models import BattleEvent, CombatantState, DamageRollComponent, DiceRoll, WeaponAttack

logger = logging.getLogger(__name__)

EXILED_EFFECT_ID = "banished"


def removed_from_battlefield(state: CombatantState) -> bool:
    return any(effect.removed_from_battlefield for effect in state.timed_effects)


def apply_on_hit_exile(
    attacker: CombatantState,
    defender: CombatantState,
    attack: WeaponAttack,
    *,
    attacker_id: str,
    round_number: int,
    affected_states: list[CombatantState] | None = None,
    dice=None,
    turn_key: str | None = None,
) -> tuple[str, int] | None:
    """Spend a declarative resource after a hit and exile a living target."""
    rule = attacker.template.progression_features.resource_backed_on_hit_exile
    if rule is None or defender.is_dead or not defender.is_alive or defender.current_hp <= 0:
        return None
    if rule.once_per_turn:
        if not turn_key:
            raise ValueError(f"{rule.source_name} requires a turn key for its once-per-turn limit.")
        if attacker.feature_last_turn_keys.get(rule.source_id) == turn_key:
            return None
    resource = resource_state(attacker, rule.resource_id)
    if resource is None:
        raise ValueError(f"{rule.source_name} references missing resource {rule.resource_id}.")
    if resource.current_uses < rule.resource_cost:
        return None
    resource.current_uses -= rule.resource_cost
    if rule.once_per_turn:
        attacker.feature_last_turn_keys[rule.source_id] = turn_key
    if exile_save_succeeded(defender, rule, dice):
        return None
    apply_exile_hit_riders(
        attacker,
        defender,
        rule,
        attacker_id=attacker_id,
        round_number=round_number,
        dice=dice,
        affected_states=affected_states,
    )
    applied = apply_timed_condition(
        defender,
        EXILED_EFFECT_ID,
        attacker_id,
        source_effect_id=rule.source_id,
        source_template=attacker.template,
        source_is_magical=True,
        suppress_action=True,
        suppress_bonus_action=True,
        suppress_reactions=True,
        suppress_movement=True,
        applied_round=round_number,
        expires_round=round_number + rule.duration_rounds,
        expiry_timing=rule.expiry_timing,
        affected_states=affected_states,
        use_default_poison_recovery=False,
        removed_from_battlefield=True,
        return_damage_dice_count=rule.return_damage_dice_count,
        return_damage_dice_size=rule.return_damage_dice_size,
        return_damage_bonus=rule.return_damage_bonus,
        return_damage_type=rule.return_damage_type,
        return_damage_excluded_creature_types=rule.return_damage_excluded_creature_types,
    )
    return (applied, resource.current_uses) if applied else None


def resolve_source_exile_returns(
    sequence: int,
    round_number: int,
    source: EncounterCombatant,
    setup: EncounterSetup,
    dice,
) -> tuple[list[BattleEvent], int]:
    """Return source-owned exiles at source turn end and apply declared delayed damage."""
    events: list[BattleEvent] = []
    states = [member.state for member in [*setup.heroes, *setup.monsters]]
    for target in [*setup.heroes, *setup.monsters]:
        expiring = [
            effect for effect in list(target.state.timed_effects)
            if effect.source_id == source.combatant_id
            and effect.removed_from_battlefield
            and effect.expiry_timing == "source_turn_end"
            and (effect.expires_round is None or round_number >= effect.expires_round)
        ]
        for effect in expiring:
            hp_before = target.state.current_hp
            temp_before = target.state.temporary_hp
            removed = remove_effect_group(target.state, effect)
            if not removed:
                continue
            damage_roll = None
            components = []
            excluded = (target.state.template.creature_type or "").lower() in {
                item.lower() for item in effect.return_damage_excluded_creature_types
            }
            if effect.return_damage_type is not None and effect.return_damage_dice_count and not excluded:
                rolls = [dice.roll(effect.return_damage_dice_size) for _ in range(effect.return_damage_dice_count)]
                raw_total = sum(rolls) + effect.return_damage_bonus
                raw = DamageRollComponent(
                    source=effect.source_effect_id or effect.effect_id,
                    notation=f"{effect.return_damage_dice_count}d{effect.return_damage_dice_size}+{effect.return_damage_bonus}",
                    rolls=rolls,
                    modifier=effect.return_damage_bonus,
                    damage_type=effect.return_damage_type,
                    total=raw_total,
                )
                applied_total, components = apply_damage_defenses(target.state, [raw])
                damage_roll = DiceRoll(
                    notation=raw.notation,
                    rolls=rolls,
                    modifier=effect.return_damage_bonus,
                    total=applied_total,
                )
                if applied_total:
                    apply_damage(
                        target.state,
                        applied_total,
                        damage_types={effect.return_damage_type},
                        dice=dice,
                        affected_states=states,
                    )
            events.append(BattleEvent(
                sequence=sequence,
                round_number=round_number,
                event_type="feature",
                actor_id=source.combatant_id,
                actor_name=source.state.template.name,
                target_id=target.combatant_id,
                target_name=target.state.template.name,
                removed_condition_ids=removed,
                feature_id=effect.source_effect_id or "exile-return",
                animation="condition-ended",
                damage_roll=damage_roll,
                damage_components=components,
                hp_before=hp_before,
                hp_after=target.state.current_hp,
                temporary_hp_before=temp_before,
                temporary_hp_after=target.state.temporary_hp,
                description=(
                    f"{target.state.template.name} returns from {effect.source_effect_id or effect.effect_id}."
                    + (" The return damage is suppressed by creature type." if excluded else "")
                ),
            ))
            sequence += 1
    return events, sequence
