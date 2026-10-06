from __future__ import annotations

from dataclasses import dataclass
import logging

from app.combat.condition_immunity import condition_is_immune
from app.combat.dice import DiceProvider
from app.combat.forced_movement import push_straight_away
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
        if condition_is_immune(defender, effect.condition_id, source_template):
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
        if not succeeded:
            timed = effect.duration_rounds is not None or effect.repeat_save_timing is not None
            if timed:
                applied = apply_timed_condition(
                    defender,
                    effect.condition_id,
                    source_id or (source_template.id if source_template is not None else "on-hit-save"),
                    source_effect_id=attack.weapon.name,
                    source_template=source_template,
                    applied_round=round_number,
                    expires_round=(
                        None if round_number is None or effect.duration_rounds is None
                        else round_number + effect.duration_rounds
                    ),
                    expiry_timing="target_turn_end" if effect.duration_rounds is not None else None,
                    repeat_save_ability=effect.save_ability if effect.repeat_save_timing else None,
                    repeat_save_dc=effect.dc if effect.repeat_save_timing else None,
                    repeat_save_timing=effect.repeat_save_timing,
                    repeat_save_failure_condition_id=effect.repeat_save_failure_condition_id,
                    expires_at_start_of_source_turn=False,
                    affected_states=affected_states,
                    use_default_poison_recovery=False,
                )
            elif effect.condition_id not in defender.active_effect_ids:
                defender.active_effect_ids.append(effect.condition_id)
                apply_terminal_condition_outcome(
                    defender, effect.condition_id, affected_states=affected_states
                )
                applied = effect.condition_id
        moved = 0
        if not succeeded and effect.failure_push_ft:
            if setup is None or target_id is None or source_id is None:
                raise ValueError("Failed-save forced movement requires encounter identities and setup.")
            members = {item.combatant_id: item for item in [*setup.heroes, *setup.monsters]}
            source_member = members.get(source_id)
            target_member = members.get(target_id)
            if source_member is None or target_member is None:
                raise ValueError("Failed-save forced movement combatants are missing from encounter setup.")
            moved = push_straight_away(
                target_member, source_member, setup, effect.failure_push_ft,
                round_number=round_number or 1,
            )
        return OnHitConditionSaveResolution(
            save_roll, effect.save_ability, effect.dc, succeeded, applied, moved
        )
    except Exception:
        logger.exception("Failed to resolve on-hit condition save for %s.", defender.template.name)
        raise
