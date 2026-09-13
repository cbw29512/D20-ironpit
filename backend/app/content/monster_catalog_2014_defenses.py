from __future__ import annotations

from app.domain.damage_defense_rules import ConditionalDamageResistance
from app.domain.weapons import DamageType

_PHYSICAL = [DamageType.BLUDGEONING, DamageType.PIERCING, DamageType.SLASHING]
_NONMAGICAL = "bludgeoning, piercing, and slashing from nonmagical attacks"


def _normalized(value: str) -> str:
    return value.lower().replace("’", "'").strip().rstrip(".")


def _rule(clause: str) -> ConditionalDamageResistance | None:
    value = _normalized(clause)
    if value == _NONMAGICAL:
        return ConditionalDamageResistance(damage_types=_PHYSICAL, nonmagical_attack_only=True)
    if value == f"{_NONMAGICAL} that aren't silvered":
        return ConditionalDamageResistance(
            damage_types=_PHYSICAL,
            nonmagical_attack_only=True,
            bypass_if_silvered=True,
        )
    if value == f"{_NONMAGICAL} that aren't adamantine":
        return ConditionalDamageResistance(
            damage_types=_PHYSICAL,
            nonmagical_attack_only=True,
            bypass_if_adamantine=True,
        )
    return None


def conditional_resistances_2014(clauses: list[str]) -> list[ConditionalDamageResistance]:
    return [rule for clause in clauses if (rule := _rule(clause)) is not None]


def unresolved_defenses_2014(clauses: list[str]) -> list[str]:
    return [clause for clause in clauses if _rule(clause) is None]
