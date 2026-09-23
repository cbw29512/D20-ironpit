from __future__ import annotations

from app.combat.condition_immunity import condition_is_immune
from app.combat.damage_defenses import apply_damage_defenses
from app.combat.dice import DiceProvider
from app.combat.saving_throw_rolls import resolve_saving_throw
from app.combat.timed_conditions import apply_timed_condition
from app.combat.turning_outcomes import destroy_on_failed_turn_save_if_eligible
from app.combat.zero_hp import apply_damage
from app.domain.encounters import EncounterCombatant, EncounterSetup
from app.domain.models import BattleEvent, DamageRollComponent, DamageType, DiceRoll


def apply_turned_creature_effects(
    source: EncounterCombatant,
    target: EncounterCombatant,
    setup: EncounterSetup,
    round_number: int,
    *,
    source_effect_id: str,
    turned_effect_id: str,
    include_frightened: bool = True,
    include_incapacitated: bool = True,
    suppress_action: bool = False,
    suppress_bonus_action: bool = False,
    suppress_reactions: bool = False,
    suppress_movement: bool = False,
    turn_behavior: str = "forced_retreat",
    repeat_save_ability: str | None = None,
    repeat_save_dc: int | None = None,
    repeat_save_timing: str | None = None,
    expires_rounds: int | None = 10,
    expiry_timing: str | None = "source_turn_start",
    ends_if_source_incapacitated: bool = True,
    ends_if_source_dead: bool = True,
) -> list[str]:
    """Apply the shared 1-minute forced-retreat turn package used by holy turning features."""
    states = [member.state for member in [*setup.heroes, *setup.monsters]]
    common = dict(
        source_effect_id=source_effect_id,
        applied_round=round_number,
        expires_round=(round_number + expires_rounds) if expires_rounds is not None else None,
        expiry_timing=expiry_timing,
        affected_states=states,
        ends_on_damage=True,
        ends_if_source_incapacitated=ends_if_source_incapacitated,
        ends_if_source_dead=ends_if_source_dead,
    )
    applied = [
        apply_timed_condition(
            target.state,
            turned_effect_id,
            source.combatant_id,
            turn_behavior=turn_behavior,
            suppress_action=suppress_action,
            suppress_bonus_action=suppress_bonus_action,
            suppress_reactions=suppress_reactions,
            suppress_movement=suppress_movement,
            repeat_save_ability=repeat_save_ability,
            repeat_save_dc=repeat_save_dc,
            repeat_save_timing=repeat_save_timing,
            **common,
        )
    ]
    conditions = []
    if include_frightened:
        conditions.append("frightened")
    if include_incapacitated:
        conditions.append("incapacitated")
    for condition in conditions:
        if not condition_is_immune(target.state, condition):
            applied.append(apply_timed_condition(
                target.state,
                condition,
                source.combatant_id,
                **common,
            ))
    return [effect for effect in applied if effect is not None]


def resolve_turning_saves(
    sequence: int,
    round_number: int,
    source: EncounterCombatant,
    setup: EncounterSetup,
    targets: tuple[EncounterCombatant, ...],
    dice: DiceProvider,
    *,
    save_dc: int,
    source_effect_id: str,
    turned_effect_id: str,
    resource_remaining: int,
    feature_name: str,
    include_frightened: bool = True,
    include_incapacitated: bool = True,
    suppress_action: bool = False,
    suppress_bonus_action: bool = False,
    suppress_reactions: bool = False,
    suppress_movement: bool = False,
    turn_behavior: str = "forced_retreat",
    repeat_save_timing: str | None = None,
    expires_rounds: int | None = 10,
    expiry_timing: str | None = "source_turn_start",
    ends_if_source_incapacitated: bool = True,
    ends_if_source_dead: bool = True,
) -> tuple[list[BattleEvent], int]:
    """Resolve the shared Wisdom-save/event loop for creature-turning features."""
    events: list[BattleEvent] = []
    features = source.state.template.progression_features
    rider = features.turning_failure_damage
    destroy_max_cr = features.turning_failure_destroy_max_cr
    shared_rolls: list[int] = []
    if rider is not None:
        scores = source.state.template.ability_scores
        if scores is None:
            raise ValueError("Ability-scaled turning damage requires ability scores.")
        dice_count = max(1, scores.modifier(rider.ability))
        shared_rolls = [dice.roll(rider.dice_size) for _ in range(dice_count)]
    affected_states = [member.state for member in [*setup.heroes, *setup.monsters]]
    for target in targets:
        hp_before = target.state.current_hp
        roll, succeeded = resolve_saving_throw(target.state, "wisdom", save_dc, dice)
        damage_roll = None
        damage_components = []
        if not succeeded and rider is not None:
            damage_type = DamageType(rider.damage_type)
            raw = DamageRollComponent(
                source=rider.source_id,
                notation=f"{len(shared_rolls)}d{rider.dice_size}",
                rolls=shared_rolls,
                modifier=0,
                damage_type=damage_type,
                total=sum(shared_rolls),
            )
            applied_total, damage_components = apply_damage_defenses(target.state, [raw])
            if applied_total:
                apply_damage(
                    target.state,
                    applied_total,
                    damage_types={damage_type},
                    dice=dice,
                    affected_states=affected_states,
                )
            damage_roll = DiceRoll(
                notation=raw.notation,
                rolls=shared_rolls,
                modifier=0,
                total=applied_total,
            )
        destroyed = destroy_on_failed_turn_save_if_eligible(
            target,
            succeeded=succeeded,
            maximum_cr=destroy_max_cr,
            dice=dice,
            affected_states=affected_states,
        )
        applied = [] if succeeded or target.state.is_dead or destroyed else apply_turned_creature_effects(
            source, target, setup, round_number,
            source_effect_id=source_effect_id,
            turned_effect_id=turned_effect_id,
            include_frightened=include_frightened,
            include_incapacitated=include_incapacitated,
            suppress_action=suppress_action,
            suppress_bonus_action=suppress_bonus_action,
            suppress_reactions=suppress_reactions,
            suppress_movement=suppress_movement,
            turn_behavior=turn_behavior,
            repeat_save_ability="wisdom" if repeat_save_timing is not None else None,
            repeat_save_dc=save_dc if repeat_save_timing is not None else None,
            repeat_save_timing=repeat_save_timing,
            expires_rounds=expires_rounds,
            expiry_timing=expiry_timing,
            ends_if_source_incapacitated=ends_if_source_incapacitated,
            ends_if_source_dead=ends_if_source_dead,
        )
        events.append(BattleEvent(
            sequence=sequence, round_number=round_number, event_type="saving_throw",
            actor_id=source.combatant_id, actor_name=source.state.template.name,
            target_id=target.combatant_id, target_name=target.state.template.name,
            saving_throw_roll=roll, save_ability="wisdom", save_dc=save_dc, save_succeeded=succeeded,
            damage_roll=damage_roll, damage_components=damage_components,
            applied_condition_ids=applied, feature_id=source_effect_id,
            resource_remaining=resource_remaining, animation="turn-undead",
            hp_before=hp_before, hp_after=target.state.current_hp, is_dead=target.state.is_dead,
            description=(
                f"{target.state.template.name} {'resists' if succeeded else 'fails'} "
                f"{source.state.template.name}'s {feature_name}"
                f"{' and is destroyed' if destroyed else ''}."
            ),
        ))
        sequence += 1
    return events, sequence
