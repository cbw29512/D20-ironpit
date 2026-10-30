from __future__ import annotations

import logging
from dataclasses import dataclass, field

from app.combat.dice import DiceProvider
from app.combat.save_failure_effects import apply_save_failure_effects
from app.combat.saving_throw_rolls import resolve_saving_throw
from app.combat.source_effect_immunity import grant_source_effect_immunity, has_source_effect_immunity
from app.domain.models import CombatantState, DiceRoll, WeaponAttack

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class AttackSaveRiderOutcome:
    save_roll: DiceRoll | None = None
    save_ability: str | None = None
    save_dc: int | None = None
    save_succeeded: bool | None = None
    target_eligible: bool | None = None
    severe_failure: bool = False
    applied_effect_ids: list[str] = field(default_factory=list)


def _severe_failure(rider, roll: DiceRoll | None, succeeded: bool) -> bool:
    try:
        return bool(
            not succeeded
            and rider.severe_failure_margin is not None
            and roll is not None
            and roll.total <= rider.dc - rider.severe_failure_margin
        )
    except Exception:
        logger.exception("Failed to evaluate severe save failure for DC %s.", rider.dc)
        raise


def resolve_attack_save_rider(
    attacker: CombatantState,
    defender: CombatantState,
    attack: WeaponAttack,
    dice: DiceProvider,
    *,
    round_number: int,
    attacker_event_id: str,
    distance_ft: int,
    affected_states: list[CombatantState] | None = None,
    advantage_sources: int = 0,
) -> AttackSaveRiderOutcome:
    """Resolve one source-neutral saving throw caused by a successful attack hit."""
    try:
        rider = attack.on_hit_saving_throw
        if rider is None or defender.is_dead or not defender.is_alive:
            return AttackSaveRiderOutcome()
        eligible = rider.target_filter.allows(defender.template.creature_type, defender.template.creature_tags)
        if rider.source_effect_immunity_on_success and has_source_effect_immunity(
            defender, attacker_event_id, attack.id,
        ):
            eligible = False
        if rider.forbid_target_ongoing_hp_loss_id is not None:
            eligible = eligible and not any(
                effect.effect_id == rider.forbid_target_ongoing_hp_loss_id
                for effect in defender.ongoing_hp_loss_effects
            )
        if not eligible:
            return AttackSaveRiderOutcome(
                save_ability=rider.save_ability, save_dc=rider.dc, target_eligible=False,
            )
        roll, succeeded = resolve_saving_throw(
            defender,
            rider.save_ability,
            rider.dc,
            dice,
            magical_effect=rider.magical_effect,
            advantage_sources=advantage_sources,
        )
        severe = _severe_failure(rider, roll, succeeded)
        applied: list[str] = []
        if succeeded and rider.source_effect_immunity_on_success:
            grant_source_effect_immunity(defender, attacker_event_id, attack.id)
        if not succeeded:
            effects = rider.severe_failure_effects if severe else rider.failure_effects
            applied = apply_save_failure_effects(
                defender,
                attacker_event_id,
                attack.id,
                effects,
                round_number=round_number,
                range_ft=distance_ft,
                affected_states=affected_states,
            )
        return AttackSaveRiderOutcome(
            save_roll=roll,
            save_ability=rider.save_ability,
            save_dc=rider.dc,
            save_succeeded=succeeded,
            target_eligible=True,
            severe_failure=severe,
            applied_effect_ids=applied,
        )
    except ValueError:
        raise
    except Exception as exc:
        logger.exception("On-hit saving throw rider failed for %s.", attack.id)
        raise RuntimeError("On-hit saving throw rider could not be resolved.") from exc
