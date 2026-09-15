from __future__ import annotations

from typing import TYPE_CHECKING, TypeVar

from app.domain.damage_defense_rules import ConditionalDamageImmunity, ConditionalDamageResistance
from app.domain.weapons import DamageType

if TYPE_CHECKING:
    from app.content.monster_catalog_2014_models import CatalogMonster2014

_PHYSICAL = [DamageType.BLUDGEONING, DamageType.PIERCING, DamageType.SLASHING]
_NONMAGICAL = "bludgeoning, piercing, and slashing from nonmagical attacks"
_RuleT = TypeVar("_RuleT", ConditionalDamageResistance, ConditionalDamageImmunity)


def _normalized(value: str) -> str:
    return value.lower().replace("’", "'").strip().rstrip(".")


def _clauses(text: str | None) -> list[str]:
    return [item.strip().rstrip(".") for item in (text or "").split(";") if item.strip()]


def _rule(clause: str, rule_type: type[_RuleT]) -> _RuleT | None:
    value = _normalized(clause)
    if value == _NONMAGICAL:
        return rule_type(damage_types=_PHYSICAL, nonmagical_attack_only=True)
    if value == f"{_NONMAGICAL} that aren't silvered":
        return rule_type(
            damage_types=_PHYSICAL,
            nonmagical_attack_only=True,
            bypass_if_silvered=True,
        )
    if value == f"{_NONMAGICAL} that aren't adamantine":
        return rule_type(
            damage_types=_PHYSICAL,
            nonmagical_attack_only=True,
            bypass_if_adamantine=True,
        )
    return None


def conditional_resistances_2014(text: str | None) -> list[ConditionalDamageResistance]:
    return [
        rule for clause in _clauses(text)
        if (rule := _rule(clause, ConditionalDamageResistance)) is not None
    ]


def conditional_immunities_2014(text: str | None) -> list[ConditionalDamageImmunity]:
    return [
        rule for clause in _clauses(text)
        if (rule := _rule(clause, ConditionalDamageImmunity)) is not None
    ]


def unresolved_defenses_2014(source: "CatalogMonster2014") -> list[str]:
    recognized = {
        _normalized(clause)
        for text, rule_type in (
            (source.damage_resistances_text, ConditionalDamageResistance),
            (source.damage_immunities_text, ConditionalDamageImmunity),
        )
        for clause in _clauses(text)
        if _rule(clause, rule_type) is not None
    }
    return [
        clause for clause in source.unsupported_defense_text
        if _normalized(clause) not in recognized
    ]