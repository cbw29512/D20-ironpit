from __future__ import annotations

from dataclasses import dataclass
import logging

from app.combat.failed_d20_test_override import apply_failed_d20_test_override
from app.combat.miss_to_hit_override import apply_miss_to_hit_override
from app.combat.parry import resolve_parry_hit
from app.domain.models import CombatantState, DiceRoll, WeaponAttack

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class AttackD20Outcome:
    roll: DiceRoll
    target_ac: int
    hit: bool
    natural: int
    parry_used: bool
    d20_override_feature_id: str | None = None
    d20_override_source_name: str | None = None
    miss_override_feature_id: str | None = None
    miss_override_source_name: str | None = None


def resolve_attack_d20_outcome(
    attacker: CombatantState,
    defender: CombatantState,
    attack: WeaponAttack,
    attack_roll: DiceRoll,
    target_ac: int,
) -> AttackD20Outcome:
    """Resolve post-roll defensive and resource-backed attack outcome revisions."""
    try:
        original_natural = attack_roll.selected_roll or 0
        hit = original_natural != 1 and (
            original_natural == 20 or attack_roll.total >= target_ac
        )
        hit, parry_used = resolve_parry_hit(
            defender, attack, attack_roll.total, original_natural, hit,
        )
        if parry_used:
            target_ac += defender.template.parry_reaction.ac_bonus

        revised_roll, d20_id, d20_name = apply_failed_d20_test_override(
            attacker, attack_roll, failed=not hit, test_kind="attack",
        )
        if revised_roll is None:
            raise ValueError("Attack D20 override unexpectedly removed the attack roll.")
        natural = revised_roll.selected_roll or 0
        if d20_id is not None:
            hit = natural == 20 or revised_roll.total >= target_ac

        hit, miss_id, miss_name = apply_miss_to_hit_override(attacker, hit=hit)
        return AttackD20Outcome(
            roll=revised_roll,
            target_ac=target_ac,
            hit=hit,
            natural=natural,
            parry_used=parry_used,
            d20_override_feature_id=d20_id,
            d20_override_source_name=d20_name,
            miss_override_feature_id=miss_id,
            miss_override_source_name=miss_name,
        )
    except ValueError:
        raise
    except Exception as exc:
        logger.exception("Failed to resolve attack D20 outcome for %s.", attacker.template.name)
        raise RuntimeError("Attack D20 outcome could not be resolved.") from exc
