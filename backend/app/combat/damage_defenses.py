from __future__ import annotations

import logging

from app.combat.condition_rules import has_condition
from app.domain.models import CombatantState, DamageRollComponent, DamageType, WeaponAttack

logger = logging.getLogger(__name__)


def _active_timed_resistances(target: CombatantState) -> set[DamageType]:
    """Return typed resistances owned by currently active timed effects."""
    try:
        return {
            damage_type
            for effect in target.timed_effects
            for damage_type in effect.owned_damage_resistances
        }
    except Exception as exc:
        logger.exception("Timed resistance lookup failed for %s.", target.template.name)
        raise RuntimeError("Timed resistances could not be resolved.") from exc


def _qualified_defense_kinds(
    target: CombatantState,
    damage_type: DamageType,
    attack: WeaponAttack | None,
) -> set[str]:
    """Return qualified defense kinds whose declarative source predicates match."""
    try:
        kinds: set[str] = set()
        for rule in target.template.qualified_damage_defenses:
            if damage_type not in rule.damage_types:
                continue
            if rule.attack_only and attack is None:
                continue
            if rule.magical is not None:
                if attack is None or attack.weapon.magical is not rule.magical:
                    continue
            if attack is not None and rule.bypass_materials:
                material = (attack.weapon.material or "").lower()
                if material in {item.lower() for item in rule.bypass_materials}:
                    continue
            kinds.add(rule.kind)
        return kinds
    except Exception as exc:
        logger.exception("Qualified damage defense lookup failed for %s.", target.template.name)
        raise RuntimeError("Qualified damage defenses could not be resolved.") from exc


def adjusted_damage_amount(
    amount: int,
    damage_type: DamageType,
    target: CombatantState,
    *,
    allow_vulnerability: bool = True,
    attack: WeaponAttack | None = None,
) -> int:
    """Apply immunity/resistance and, when allowed, vulnerability to one damage type."""
    try:
        if amount < 0:
            raise ValueError("Damage cannot be negative.")
        template = target.template
        qualified = _qualified_defense_kinds(target, damage_type, attack)
        if damage_type in template.damage_immunities or "immunity" in qualified:
            return 0

        adjusted = amount
        resistances = {
            *template.damage_resistances,
            *target.temporary_damage_resistances,
            *_active_timed_resistances(target),
        }
        if damage_type in resistances or "resistance" in qualified or has_condition(target, "petrified"):
            adjusted //= 2
        if allow_vulnerability and (
            damage_type in template.damage_vulnerabilities or "vulnerability" in qualified
        ):
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
    """Apply defenses per typed component and return the total damage actually taken."""
    try:
        adjusted_components: list[DamageRollComponent] = []
        applied_total = 0
        for component in components:
            applied = adjusted_damage_amount(
                component.total,
                component.damage_type,
                target,
                attack=attack,
            )
            adjusted_components.append(component.model_copy(update={"applied_total": applied}))
            applied_total += applied
        return applied_total, adjusted_components
    except Exception as exc:
        logger.exception("Typed damage defenses failed for %s.", target.template.name)
        raise RuntimeError("Typed damage defenses could not be applied.") from exc