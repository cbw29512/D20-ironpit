from __future__ import annotations

from app.combat.timed_conditions import remove_effect_group
from app.domain.actions import ConditionTiming
from app.domain.encounters import EncounterCombatant
from app.domain.models import BattleEvent


def automatic_success_due(effect, round_number: int, timing: ConditionTiming) -> bool:
    return bool(
        effect.automatic_success_round is not None
        and round_number >= effect.automatic_success_round
        and effect.repeat_save_timing == timing
    )


def resolve_automatic_success(
    sequence: int,
    round_number: int,
    target: EncounterCombatant,
    effect,
) -> BattleEvent:
    removed = remove_effect_group(target.state, effect)
    return BattleEvent(
        sequence=sequence,
        round_number=round_number,
        event_type="saving_throw",
        actor_id=target.combatant_id,
        actor_name=target.state.template.name,
        target_id=target.combatant_id,
        target_name=target.state.template.name,
        saving_throw_roll=None,
        save_ability=effect.repeat_save_ability,
        save_dc=effect.repeat_save_dc,
        save_succeeded=True,
        removed_condition_ids=removed,
        feature_id=effect.source_effect_id or "timed-effect-auto-success",
        animation="condition-save",
        description=(
            f"{target.state.template.name} automatically succeeds against "
            f"{effect.source_effect_id or effect.effect_id} when its maximum duration ends."
        ),
    )
