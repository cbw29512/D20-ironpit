from __future__ import annotations

from dataclasses import dataclass

from app.content.armor_class_rules import ArmorCategory


@dataclass(frozen=True)
class ArmorRecord:
    id: str
    name: str
    category: ArmorCategory
    base_ac: int


ARMOR_CATALOG = {
    "chain-mail": ArmorRecord("chain-mail", "Chain Mail", "heavy", 16),
    "studded-leather": ArmorRecord("studded-leather", "Studded Leather Armor", "light", 12),
}


def get_armor(armor_id: str) -> ArmorRecord:
    try:
        return ARMOR_CATALOG[armor_id]
    except KeyError as exc:
        raise ValueError(f"Unknown audited armor: {armor_id}.") from exc
