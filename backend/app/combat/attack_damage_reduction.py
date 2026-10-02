from __future__ import annotations

from dataclasses import dataclass
import logging

from app.combat.action_economy import is_available, spend
from app.combat.dice import DiceProvider
from app.domain.models import CombatantState, DamageRollComponent, WeaponAttack

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class AttackDamageReductionResolution:
    components: list[DamageRollComponent]
    used: bool = False
    reduction: int = 0
    source_id: str | None = None
    source_name: str | None = None
    zeroed_attack: bool = False


def _value(item: object) -> str:
    try:
        return str(getattr(item, "value", item)).casefold()
    except Exception as exc:
        logger.exception("Failed to normalize attack damage reduction value %r.", item)
        raise RuntimeError("Attack damage reduction value could not be normalized.") from exc


def can_reduce_attack_damage(
    defender: CombatantState,
    attack: WeaponAttack,
    components: list[DamageRollComponent],
) -> bool:
    """Return whether the defender can spend its Reaction on this attack's rolled damage."""
    try:
        rule = defender.template.attack_damage_reduction_reaction
        if rule is None or not components or defender.current_hp <= 0:
            return False
        if not is_available(defender, "reaction"):
            return False
        if _value(attack.weapon.attack_kind) not in set(rule.attack_kinds):
            return False
        required = {_value(item) for item in rule.required_damage_types}
        if required and not any(_value(part.damage_type) in required and part.total > 0 for part in components):
            return False
        return True
    except Exception as exc:
        logger.exception("Failed attack damage reduction eligibility for %s.", defender.template.name)
        raise RuntimeError("Attack damage reduction eligibility could not be resolved.") from exc


def apply_attack_damage_reduction(
    defender: CombatantState,
    attack: WeaponAttack,
    components: list[DamageRollComponent],
    dice: DiceProvider,
) -> AttackDamageReductionResolution:
    """Apply one source-declared Reaction reduction before damage defenses and HP mutation."""
    try:
        rule = defender.template.attack_damage_reduction_reaction
        if rule is None or not can_reduce_attack_damage(defender, attack, components):
            return AttackDamageReductionResolution(components=list(components))

        original_total = sum(max(0, component.total) for component in components)
        reduction = sum(dice.roll(rule.reduction_dice_size) for _ in range(rule.reduction_dice_count))
        if rule.reduction_ability is not None:
            scores = defender.template.ability_scores
            if scores is None:
                raise ValueError(f"{rule.source_name} requires certified ability scores.")
            reduction += scores.modifier(rule.reduction_ability)
        if rule.add_level:
            if defender.template.level is None:
                raise ValueError(f"{rule.source_name} requires a certified character level.")
            reduction += defender.template.level

        spend(defender, "reaction")
        remaining = max(0, reduction)
        reduced: list[DamageRollComponent] = []
        for component in components:
            applied = min(component.total, remaining)
            reduced.append(component.model_copy(update={"total": component.total - applied}))
            remaining -= applied

        return AttackDamageReductionResolution(
            components=reduced,
            used=True,
            reduction=reduction,
            source_id=rule.source_id,
            source_name=rule.source_name,
            zeroed_attack=original_total > 0 and sum(max(0, item.total) for item in reduced) == 0,
        )
    except ValueError:
        raise
    except Exception as exc:
        logger.exception("Failed attack damage reduction for %s.", defender.template.name)
        raise RuntimeError("Attack damage reduction could not be resolved.") from exc
