from __future__ import annotations

import logging

from app.combat.damage_defenses import apply_damage_defenses
from app.combat.saving_throw_rolls import resolve_saving_throw
from app.combat.timed_conditions import apply_timed_condition
from app.combat.zero_hp import apply_damage
from app.domain.models import CombatantState, DamageRollComponent
from app.domain.saving_throw_context import SavingThrowContext

logger = logging.getLogger(__name__)


def exile_save_succeeded(
    defender: CombatantState,
    rule,
    dice,
) -> bool:
    try:
        if rule.save_ability is None:
            return False
        if dice is None or rule.save_dc is None:
            raise ValueError(f"{rule.source_name} requires a save DC and dice when a save is declared.")
        _roll, succeeded = resolve_saving_throw(
            defender,
            rule.save_ability,
            rule.save_dc,
            dice,
            SavingThrowContext(condition_id="banished"),
        )
        return succeeded
    except ValueError:
        raise
    except Exception as exc:
        logger.exception("On-hit exile save failed for %s.", rule.source_id)
        raise RuntimeError("On-hit exile save could not be resolved.") from exc


def apply_exile_hit_riders(
    attacker: CombatantState,
    defender: CombatantState,
    rule,
    *,
    attacker_id: str,
    round_number: int,
    dice,
    affected_states: list[CombatantState] | None,
) -> None:
    try:
        creature_type = (defender.template.creature_type or "").lower()
        excluded = creature_type in {item.lower() for item in rule.hit_damage_excluded_creature_types}
        if (
            rule.hit_damage_type is not None
            and rule.hit_damage_dice_count
            and dice is not None
            and not excluded
        ):
            rolls = [dice.roll(rule.hit_damage_dice_size) for _ in range(rule.hit_damage_dice_count)]
            raw_total = sum(rolls)
            raw = DamageRollComponent(
                source=rule.source_id,
                notation=f"{rule.hit_damage_dice_count}d{rule.hit_damage_dice_size}",
                rolls=rolls,
                modifier=0,
                damage_type=rule.hit_damage_type,
                total=raw_total,
            )
            applied_total, _components = apply_damage_defenses(defender, [raw])
            if applied_total:
                apply_damage(
                    defender,
                    applied_total,
                    damage_types={rule.hit_damage_type},
                    dice=dice,
                    affected_states=affected_states,
                )
        for condition_id in rule.apply_condition_ids:
            apply_timed_condition(
                defender,
                condition_id,
                attacker_id,
                source_effect_id=rule.source_id,
                source_template=attacker.template,
                source_is_magical=True,
                applied_round=round_number,
                expires_round=round_number + rule.duration_rounds,
                expiry_timing=rule.expiry_timing,
                affected_states=affected_states,
                use_default_poison_recovery=False,
            )
    except ValueError:
        raise
    except Exception as exc:
        logger.exception("On-hit exile riders failed for %s.", rule.source_id)
        raise RuntimeError("On-hit exile riders could not be resolved.") from exc
