from __future__ import annotations

from typing import TYPE_CHECKING, TypeVar

from app.domain.damage_defense_rules import ConditionalDamageImmunity, ConditionalDamageResistance
from app.domain.weapons import DamageType

if TYPE_CHECKING:
    from app.content.monster_catalog_2014_models import CatalogMonster2014

_PHYSICAL_BY_NAME = {
    "bludgeoning": DamageType.BLUDGEONING,
    "piercing": DamageType.PIERCING,
    "slashing": DamageType.SLASHING,
}
_NONMAGICAL_MARKER = " from nonmagical attacks"
_RuleT = TypeVar("_RuleT", ConditionalDamageResistance, ConditionalDamageImmunity)


def _normalized(value: str) -> str:
    return value.lower().replace("’", "'").strip().rstrip(".")


def _clauses(text: str | None) -> list[str]:
    return [item.strip().rstrip(".") for item in (text or "").split(";") if item.strip()]


def _physical_damage_types(text: str) -> list[DamageType] | None:
    names = text.replace(", and ", ", ").replace(" and ", ", ").split(",")
    types: list[DamageType] = []
    for name in (item.strip() for item in names if item.strip()):
        damage_type = _PHYSICAL_BY_NAME.get(name)
        if damage_type is None:
            return None
        if damage_type not in types:
            types.append(damage_type)
    return types or None


def _rule(clause: str, rule_type: type[_RuleT]) -> _RuleT | None:
    value = _normalized(clause)
    if _NONMAGICAL_MARKER not in value:
        return None
    damage_text, qualifier = value.split(_NONMAGICAL_MARKER, 1)
    damage_types = _physical_damage_types(damage_text)
    if damage_types is None:
        return None
    kwargs = {"damage_types": damage_types, "nonmagical_attack_only": True}
    if qualifier == "":
        return rule_type(**kwargs)
    if qualifier == " that aren't silvered":
        return rule_type(**kwargs, bypass_if_silvered=True)
    if qualifier == " that aren't adamantine":
        return rule_type(**kwargs, bypass_if_adamantine=True)
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
