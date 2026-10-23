from __future__ import annotations

from dataclasses import dataclass
import logging

from app.combat.condition_immunity import condition_is_immune
from app.combat.dice import DiceProvider
from app.combat.failure_margin_runtime import escalation_duration
from app.combat.saving_throw_rolls import resolve_saving_throw
from app.combat.timed_conditions import apply_terminal_condition_outcome, apply_timed_condition
from app.content.monster_creature_types import creature_matches_kind
from app.domain.models import CombatantState, CombatantTemplate, DiceRoll, WeaponAttack
from app.domain.saving_throw_context import SavingThrowContext
from app.domain.size import size_at_most

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class OnHitConditionSaveResolution:
    save_roll: DiceRoll | None = None
    save_ability: str | None = None
    save_dc: int | None = None
    save_succeeded: bool | None = None
    applied_condition: str | None = None
    forced_movement_ft: int = 0
    additional_conditions: tuple[str, ...] = ()


def _excluded_target(defender: CombatantState, effect) -> bool:
    try:
        kinds = [*effect.excluded_creature_types, *effect.excluded_creature_subtypes]
        return any(creature_matches_kind(defender.template, kind) for kind in kinds)
    except Exception:
        logger.exception("Failed to evaluate on-hit condition-save exclusions for %s.", defender.template.name)
        raise


def resolve_on_hit_condition_save(
    defender: CombatantState,
    attack: WeaponAttack,
    dice: DiceProvider,
    source_template: CombatantTemplate | None = None,
    *,
    source_id: str | None = None,
    round_number: int | None = None,
    affected_states: list[CombatantState] | None = None,
    setup=None,
    target_id: str | None = None,
) -> OnHitConditionSaveResolution:
    try:
        effect = attack.on_hit_condition_save
        if effect is None or defender.is_dead or not defender.is_alive:
            return OnHitConditionSaveResolution()
        if effect.max_target_size is not None and not size_at_most(defender.template.size, effect.max_target_size):
            return OnHitConditionSaveResolution()
        if _excluded_target(defender, effect):
            return OnHitConditionSaveResolution()
        target_actor = next((item for item in [*setup.heroes, *setup.monsters] if item.state is defender), None) if setup else None
        if condition_is_immune(defender, effect.condition_id, source_template, actor=target_actor, setup=setup):
            return OnHitConditionSaveResolution()
        save_roll, succeeded = resolve_saving_throw(
            defender,
            effect.save_ability,
            effect.dc,
            dice,
            SavingThrowContext(
                condition_id=effect.condition_id,
                effect_tags=frozenset({"poison"}) if effect.condition_id == "poisoned" else frozenset(),
            ),
        )
        applied = None
        additional: list[str] = []
        escalation = effect.failure_margin_escalation
        escalated, duration = escalation_duration(effect, save_roll, succeeded, dice)
        if not succeeded:
            timed = duration is not None or effect.repeat_save_timing is not None
            if timed:
                applied = apply_timed_condition(
                    defender,
                    effect.condition_id,
                    source_id or (source_template.id if source_template is not None else "on-hit-save"),
                    source_effect_id=attack.weapon.name,
                    source_template=source_template,
                    target_actor=target_actor, setup=setup,
                    applied_round=round_number,
                    expires_round=(
                        None if round_number is None or duration is None
                        else round_number + duration
                    ),
                    expiry_timing="target_turn_end" if duration is not None else None,
                    repeat_save_ability=effect.save_ability if effect.repeat_save_timing else None,
                    repeat_save_dc=effect.dc if effect.repeat_save_timing else None,
                    repeat_save_timing=effect.repeat_save_timing,
                    repeat_save_failure_condition_id=effect.repeat_save_failure_condition_id,
                    expires_at_start_of_source_turn=False,
                    affected_states=affected_states,
                    use_default_poison_recovery=False,
                    cannot_regain_hit_points=effect.cannot_regain_hit_points,
                )
            elif effect.condition_id not in defender.active_effect_ids:
                defender.active_effect_ids.append(effect.condition_id)
                apply_terminal_condition_outcome(
                    defender, effect.condition_id, affected_states=affected_states
                )
                applied = effect.condition_id
            if escalated:
                for condition_id in escalation.additional_condition_ids:
                    added = apply_timed_condition(
                        defender, condition_id,
                        source_id or (source_template.id if source_template is not None else "on-hit-save"),
                        source_effect_id=(
                            f"{attack.weapon.name}:escalated"
                            if escalation.ends_on_damage or escalation.allowed_removal_action_ids
                            else attack.weapon.name
                        ),
                        source_template=source_template,
                        target_actor=target_actor, setup=setup,
                        applied_round=round_number,
                        expires_round=None if round_number is None else round_number + duration,
                        expiry_timing="target_turn_end",
                        ends_on_damage=escalation.ends_on_damage,
                        allowed_removal_action_ids=escalation.allowed_removal_action_ids,
                        use_default_poison_recovery=False,
                        affected_states=affected_states,
                    )
                    if added is not None:
                        additional.append(added)
        # Ignore printed displacement after resolving the save and conditions.
        moved = 0
        return OnHitConditionSaveResolution(
            save_roll, effect.save_ability, effect.dc, succeeded, applied, moved,
            tuple(additional),
        )
    except Exception:
        logger.exception("Failed to resolve on-hit condition save for %s.", defender.template.name)
        raise
