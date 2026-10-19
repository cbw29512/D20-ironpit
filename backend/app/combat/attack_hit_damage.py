from __future__ import annotations

from dataclasses import dataclass
import logging

from app.combat.damage import BonusDamageSpec, aggregate_damage_components, resolve_weapon_damage
from app.combat.hunters_mark_splash import resolve_hunters_mark_splash
from app.combat.damage_defenses import apply_damage_defenses
from app.combat.cunning_strike import (
    CunningStrikeObscureResolution, CunningStrikeTripResolution,
    resolve_obscure, resolve_trip,
)
from app.combat.attack_damage_reduction import apply_attack_damage_reduction
from app.combat.ally_context import has_adjacent_active_ally_for_states
from app.combat.dice import DiceProvider
from app.combat.on_hit_save_damage import OnHitSaveDamageResolution, resolve_on_hit_save_damage
from app.combat.rogue_defenses import apply_uncanny_dodge
from app.combat.zero_hp import apply_damage
from app.combat.zero_hp_save_damage_rider import apply_zero_hp_save_damage_rider, save_damage_caused_zero
from app.domain.models import CombatantState, DamageRollComponent, DiceRoll, RollMode, WeaponAttack

logger = logging.getLogger(__name__)


def _ignored_resistance_types(attacker: CombatantState) -> set:
    try:
        return {
            damage_type
            for grant in attacker.template.progression_features.damage_resistance_bypass_grants
            for damage_type in grant.damage_types
        }
    except Exception as exc:
        logger.exception("Failed to resolve outgoing resistance bypass for %s.", attacker.template.name)
        raise RuntimeError("Outgoing resistance bypass could not be resolved.") from exc


def _natural_twenty_attack_damage(
    attacker: CombatantState,
    attack: WeaponAttack,
    natural_roll: int | None,
    existing_components: list[DamageRollComponent],
) -> list[DamageRollComponent]:
    try:
        if natural_roll != 20:
            return []
        scores = attacker.template.ability_scores
        grants = attacker.template.progression_features.natural_twenty_attack_damage_grants
        if not grants:
            return []
        if scores is None:
            raise ValueError(
                f"{attacker.template.name} has natural-20 attack damage without certified ability scores."
            )
        qualifiers = list(existing_components[0].source_qualifiers) if existing_components else []
        return [
            DamageRollComponent(
                source=grant.source_name,
                notation=str(scores.score(grant.ability)),
                rolls=[],
                modifier=scores.score(grant.ability),
                damage_type=attack.weapon.damage_type,
                total=scores.score(grant.ability),
                source_qualifiers=qualifiers,
            )
            for grant in grants
        ]
    except ValueError:
        raise
    except Exception as exc:
        logger.exception("Failed to resolve natural-20 attack damage for %s.", attacker.template.name)
        raise RuntimeError("Natural-20 attack damage could not be resolved.") from exc


@dataclass(frozen=True)
class AttackHitDamageResolution:
    damage_roll: DiceRoll
    damage_components: list[DamageRollComponent]
    damage_outcome: str | None
    applied_total: int
    save_damage: OnHitSaveDamageResolution
    cunning_strike_trip: CunningStrikeTripResolution
    cunning_strike_obscure: CunningStrikeObscureResolution
    uncanny_dodge_used: bool = False
    damage_reduction_reaction_used: bool = False
    damage_reduction_reaction_source_id: str | None = None
    damage_reduction_reaction_reduction: int = 0
    damage_reduction_zeroed_attack: bool = False
    deflect_missiles_used: bool = False
    deflect_missiles_reduction: int = 0


def resolve_attack_hit_damage(
    attacker: CombatantState,
    defender: CombatantState,
    attack: WeaponAttack,
    dice: DiceProvider,
    critical: bool,
    attack_mode: RollMode,
    turn_key: str,
    bonus_damage: BonusDamageSpec | None,
    affected_states: list[CombatantState] | None,
    sneak_attack_ally_available: bool,
    target_event_id: str | None = None,
    brutal_strike_disadvantage: bool = False,
    natural_roll: int | None = None,
    setup=None,
) -> AttackHitDamageResolution:
    hp_buffer_before = defender.current_hp + defender.temporary_hp
    adjacent_ally = bool(setup) and has_adjacent_active_ally_for_states(attacker, defender, setup)
    damage_roll, rolled_components = resolve_weapon_damage(
        attacker, attack, dice, critical, attack_mode, turn_key, bonus_damage=bonus_damage,
        target=defender, target_event_id=target_event_id,
        sneak_attack_ally_available=sneak_attack_ally_available,
        active_ally_adjacent_to_target=adjacent_ally,
        brutal_strike_disadvantage=brutal_strike_disadvantage,
    )
    rolled_components.extend(_natural_twenty_attack_damage(attacker, attack, natural_roll, rolled_components))
    save_damage = resolve_on_hit_save_damage(defender, attack, dice)
    save_component_present = save_damage.component is not None
    if save_component_present:
        rolled_components.append(save_damage.component)
    reduction = apply_attack_damage_reduction(defender, attack, rolled_components, dice)
    rolled_components = reduction.components
    rolled_components, uncanny_used = apply_uncanny_dodge(attacker, defender, rolled_components)
    damage_roll = aggregate_damage_components(rolled_components)
    applied_total, components = apply_damage_defenses(
        defender,
        rolled_components,
        ignored_resistance_types=_ignored_resistance_types(attacker),
    )
    damage_roll.total = applied_total
    applied_types = {part.damage_type for part in components if part.applied_total > 0}
    outcome = apply_damage(
        defender, applied_total, critical=critical, damage_types=applied_types,
        dice=dice, affected_states=affected_states, setup=setup, damage_components=components,
    )
    if setup is not None and target_event_id:
        source = next(
            (item for item in [*setup.heroes, *setup.monsters] if item.state is attacker),
            None,
        )
        if source is not None:
            resolve_hunters_mark_splash(
                attacker, source.combatant_id, target_event_id, components,
                turn_key, setup, dice, affected_states,
            )
    effect = attack.on_hit_save_damage
    if defender.current_hp == 0 and save_damage_caused_zero(
        hp_buffer_before, applied_total, components, effect, save_component_present=save_component_present,
    ):
        assert effect is not None
        apply_zero_hp_save_damage_rider(defender, effect, turn_key, affected_states)
        if not defender.is_dead:
            outcome = "unconscious"
    cunning_strike_trip = resolve_trip(attacker, defender, dice, turn_key)
    cunning_strike_obscure = resolve_obscure(attacker, defender, dice, turn_key)
    return AttackHitDamageResolution(
        damage_roll=damage_roll,
        damage_components=components,
        damage_outcome=outcome,
        applied_total=applied_total,
        save_damage=save_damage,
        cunning_strike_trip=cunning_strike_trip,
        cunning_strike_obscure=cunning_strike_obscure,
        uncanny_dodge_used=uncanny_used,
        damage_reduction_reaction_used=reduction.used,
        damage_reduction_reaction_source_id=reduction.source_id,
        damage_reduction_reaction_reduction=reduction.reduction,
        damage_reduction_zeroed_attack=reduction.zeroed_attack,
        deflect_missiles_used=reduction.used and reduction.source_id == "deflect-missiles",
        deflect_missiles_reduction=(
            reduction.reduction if reduction.used and reduction.source_id == "deflect-missiles" else 0
        ),
    )
