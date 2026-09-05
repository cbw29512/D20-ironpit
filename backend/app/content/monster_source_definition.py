from __future__ import annotations

from functools import lru_cache
import re

from app.content.monster_attack_advantage_source_audit import source_advantage_triggers
from app.content.monster_bonus_action_source_audit import parse_bonus_action_names
from app.content.monster_catalog import load_monster_rows
from app.content.monster_defense_source_audit import parse_defense_profile
from app.content.monster_legendary_source_audit import parse_legendary_action_names
from app.content.monster_limited_use_source_audit import parse_limited_use_names
from app.content.monster_reaction_source_audit import parse_reaction_names
from app.content.monster_saving_throws import parse_saving_throw_bonuses
from app.content.monster_spellcasting_source_audit import spellcasting_fingerprint
from app.content.monster_trait_source_audit import modeled_combat_traits, parse_trait_names
from app.content.movement_modes import parse_movement_profile, standard_arena_closing_speed

_SIZE_NAMES = ("tiny", "small", "medium", "large", "huge", "gargantuan")
_SKILL_END = "Vulnerabilities|Resistances|Immunities|Gear|Senses|Languages|CR"
_STR = re.compile(r"\bStr\s+(?P<score>\d+)\s+(?P<mod>[+-]\d+)\s+[+-]\d+\b")
_PB = re.compile(r"\bPB\s+(?P<pb>[+-]\d+)\b")


def slug(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")


@lru_cache(maxsize=1)
def _rows_by_name() -> dict[str, dict[str, object]]:
    return {str(row["name"]): row for row in load_monster_rows()}


def source_row(name: str) -> dict[str, object]:
    row = _rows_by_name().get(name)
    if row is None:
        raise ValueError(f"No SRD 5.2.1 source row for monster {name!r}.")
    return row


def _first_int(value: object) -> int:
    match = re.search(r"-?\d+", str(value))
    if match is None:
        raise ValueError(f"No integer found in SRD value: {value!r}")
    return int(match.group())


def _size(row: dict[str, object], override: str | None) -> str:
    if override:
        return override
    found = [name for name in _SIZE_NAMES if re.search(rf"\b{name}\b", str(row["size"]), re.I)]
    if len(found) != 1:
        raise ValueError(f"Monster {row['name']!r} needs an explicit runtime size override: {row['size']!r}")
    return found[0]


def _initiative(row: dict[str, object]) -> int:
    match = re.search(r"\bInitiative\s+([+-]?\d+)", str(row.get("rawText", "")), re.I)
    if match is None:
        raise ValueError(f"SRD initiative could not be parsed for {row['name']!r}.")
    return int(match.group(1))


def _skills(row: dict[str, object]) -> dict[str, int]:
    raw = str(row.get("rawText", ""))
    match = re.search(rf"\bSkills\s+(.+?)(?=\s+(?:{_SKILL_END})\b)", raw, re.I | re.S)
    if match is None:
        return {}
    entries = re.findall(r"([A-Za-z][A-Za-z ]*?)\s+([+-]\d+)(?=,|$)", match.group(1).strip())
    if not entries:
        raise ValueError(f"SRD Skills section could not be parsed for {row['name']!r}.")
    return {re.sub(r"\s+", "_", name.strip().lower()): int(value) for name, value in entries}


def _unarmed(row: dict[str, object]) -> dict[str, int]:
    raw = str(row.get("rawText", ""))
    strength = _STR.search(raw)
    pb = _PB.search(str(row.get("challenge", ""))) or _PB.search(raw)
    if strength is None or pb is None:
        raise ValueError(f"Could not derive Unarmed Strike profile for {row['name']!r}.")
    score = int(strength.group("score")); modifier = (score - 10) // 2
    if int(strength.group("mod")) != modifier:
        raise ValueError(f"Strength modifier drift for {row['name']!r}.")
    return {"attack_bonus": modifier + int(pb.group("pb")), "damage": max(0, 1 + modifier)}


def source_definition_fields(name: str, *, size_override: str | None = None) -> dict[str, object]:
    """Derive objective monster fields directly from the canonical SRD row."""
    row = source_row(name)
    movement = parse_movement_profile(row["speed"])
    defenses = parse_defense_profile(row)
    traits = parse_trait_names(row.get("traits", ""))
    attack_advantage, save_advantage = source_advantage_triggers(row)
    return {
        "schema_version": 1, "id": f"srd-{slug(name)}", "name": name,
        "archetype": "source-certified native monster", "challenge_rating": str(row["challenge"]).split()[0],
        "kind": "monster", "size": _size(row, size_override), "armor_class": _first_int(row["armorClass"]),
        "max_hp": _first_int(row["hitPoints"]), "speed_ft": standard_arena_closing_speed(row["speed"]),
        "movement_modes": movement.model_dump(), "initiative_bonus": _initiative(row),
        "attack_roll_advantage_triggers": attack_advantage, "saving_throw_advantage_triggers": save_advantage,
        "unarmed_opportunity_attack": _unarmed(row), "saving_throw_bonuses": parse_saving_throw_bonuses(row),
        "skill_bonuses": _skills(row), "combat_traits": [trait.value for trait in modeled_combat_traits(row.get("traits", ""))],
        "source_trait_names": traits, "source_reaction_names": parse_reaction_names(row.get("reactions", "")),
        "source_bonus_action_names": parse_bonus_action_names(row.get("bonusActions", "")),
        "source_limited_use_names": parse_limited_use_names(row),
        "source_legendary_action_names": parse_legendary_action_names(row.get("legendaryActions", "")),
        "source_spellcasting_fingerprint": spellcasting_fingerprint(row),
        **{key: sorted(value) for key, value in defenses.items()}, "source": str(row["sourceReference"]),
    }
