from __future__ import annotations

import logging

from app.combat.condition_rules import has_condition
from app.combat.zero_hp import restore_hit_points
from app.domain.damage_defense_rules import ConditionalDamageResistance, DamageAbsorption
from app.domain.models import CombatantState, DamageRollComponent, DamageType, WeaponAttack

logger = logging.getLogger(__name__)


def _conditional_resistance_applies(
    rule: ConditionalDamageResistance,
    damage_type: DamageType,
    attack: WeaponAttack | None,
) -> bool:
    if damage_type not in rule.damage_types:
        return False
    if rule.nonmagical_attack_only:
        if attack is None or attack.weapon.magical:
            return False
    if attack is not None and rule.bypass_if_silvered and attack.weapon.silvered:
        return False
    if attack is not None and rule.bypass_if_adamantine and attack.weapon.adamantine:
        return False
    return True


def _absorption_rule(target: CombatantState, damage_type: DamageType) -> DamageAbsorption | None:
    return next((rule for rule in target.template.damage_absorptions if rule.damage_type == damage_type), None)


def adjusted_damage_amount(
    amount: int,
    damage_type: DamageType,
    target: CombatantState,
    *,
    allow_vulnerability: bool = True,
    attack: WeaponAttack | None = None,
) -> int:
    """Apply typed defenses without mutating target state; absorbed damage previews as zero."""
    try:
        if amount < 0:
            raise ValueError("Damage cannot be negative.")
        template = target.template
        if _absorption_rule(target, damage_type) is not None or damage_type in template.damage_immunities:
            return 0

        adjusted = amount
        resistances = {
            *template.damage_resistances,
            *target.temporary_damage_resistances,
        }
        conditional = any(
            _conditional_resistance_applies(rule, damage_type, attack)
            for rule in template.conditional_damage_resistances
        )
        if damage_type in resistances or conditional or has_condition(target, "petrified"):
            adjusted //= 2
        if allow_vulnerability and damage_type in template.damage_vulnerabilities:
            adjusted *= 2
        return adjusted
    except ValueError:
        raise
    except Exception as exc:
        logger.exception("Damage defense resolution failed for %s.", target.template.name)
        raise RuntimeError("Damage defenses could not be resolved.") from exc


def apply_damage_defenses(
    target: CombatantState,
    components: list[DamageRollComponent],
    *,
    attack: WeaponAttack | None = None,
) -> tuple[int, list[DamageRollComponent]]:
    """Apply defenses per typed component; absorption converts raw typed damage into healing."""
    try:
        adjusted_components: list[DamageRollComponent] = []
        applied_total = 0
        for component in components:
            absorption = _absorption_rule(target, component.damage_type)
            if absorption is not None:
                restore_hit_points(target, component.total * absorption.healing_multiplier)
                applied = 0
            else:
                applied = adjusted_damage_amount(component.total, component.damage_type, target, attack=attack)
            adjusted_components.append(component.model_copy(update={"applied_total": applied}))
            applied_total += applied
        return applied_total, adjusted_components
    except Exception as exc:
        logger.exception("Typed damage defenses failed for %s.", target.template.name)
        raise RuntimeError("Typed damage defenses could not be applied.") from exc
