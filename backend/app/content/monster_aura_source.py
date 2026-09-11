from __future__ import annotations

import logging
import re
from functools import lru_cache

from app.content.monster_catalog import load_monster_rows
from app.domain.auras import EndTurnDamageAura, RollAdvantageAura, StartTurnSaveConditionAura
from app.domain.models import CombatantTemplate, DamageType

logger = logging.getLogger(__name__)
_FIRE_AURA = re.compile(
    r"Fire Aura\.\s+At the end of each of the [^.]+ turns, each creature(?: of the [^.]+ choice)? "
    r"in a (?P<radius>\d+)-foot Emanation originating from the [^.]+ takes "
    r"(?P<average>\d+) \((?P<count>\d+)d(?P<size>\d+)(?:\s*(?P<sign>[+-])\s*(?P<bonus>\d+))?\) "
    r"(?P<dtype>[A-Za-z]+) damage(?P<tail>[^.]*)\.",
    re.IGNORECASE,
)
_START_TURN_CONDITION_AURA = re.compile(
    r"(?P<name>[A-Z][A-Za-z '\-]+)\.\s+(?P<ability>Strength|Dexterity|Constitution|Intelligence|Wisdom|Charisma) "
    r"Saving Throw: DC (?P<dc>\d+), any creature that starts its turn in a (?P<radius>\d+)-foot Emanation "
    r"originating from the [^.]+\. Failure: The target has the (?P<condition>Poisoned|Frightened) condition "
    r"until the start of its next turn\.", re.IGNORECASE,
)
_ROLL_ADVANTAGE_AURA = re.compile(
    r"(?P<name>[A-Z][A-Za-z '\-]+)\.\s+While in a (?P<radius>\d+)-foot Emanation originating from the [^,]+, "
    r"the [^ ]+ and its allies have Advantage on attack rolls and saving throws, provided the [^ ]+ doesn’t have "
    r"the Incapacitated condition\.", re.IGNORECASE,
)


@lru_cache(maxsize=1)
def _rows_by_name() -> dict[str, dict[str, object]]:
    return {str(row["name"]): row for row in load_monster_rows()}


def _traits(name: str) -> str:
    row = _rows_by_name().get(name)
    if row is None:
        raise ValueError(f"No SRD 5.2.1 source row for monster {name!r}.")
    return str(row.get("traits", ""))


def source_end_turn_damage_auras(name: str) -> list[EndTurnDamageAura]:
    text = _traits(name)
    match = _FIRE_AURA.search(text)
    if not match:
        return []
    bonus = int(match.group("bonus") or 0)
    if match.group("sign") == "-":
        bonus = -bonus
    return [EndTurnDamageAura(
        id="fire-aura", name="Fire Aura", radius_ft=int(match.group("radius")),
        damage_dice_count=int(match.group("count")), damage_dice_size=int(match.group("size")),
        damage_bonus=bonus, damage_type=DamageType(match.group("dtype").lower()),
        disabled_while_incapacitated="incapacitated condition" in match.group("tail").lower(),
    )]


def source_start_turn_condition_auras(name: str) -> list[StartTurnSaveConditionAura]:
    text = _traits(name)
    match = _START_TURN_CONDITION_AURA.search(text)
    if not match:
        return []
    heading = match.group("name").strip()
    return [StartTurnSaveConditionAura(
        id=re.sub(r"[^a-z0-9]+", "-", heading.lower()).strip("-"), name=heading,
        radius_ft=int(match.group("radius")), save_ability=match.group("ability").lower(),
        dc=int(match.group("dc")), condition=match.group("condition").lower(),
        expiry_timing="target_turn_start",
    )]


def source_roll_advantage_auras(name: str) -> list[RollAdvantageAura]:
    match = _ROLL_ADVANTAGE_AURA.search(_traits(name))
    if not match:
        return []
    heading = match.group("name").strip()
    return [RollAdvantageAura(
        id=re.sub(r"[^a-z0-9]+", "-", heading.lower()).strip("-"), name=heading,
        radius_ft=int(match.group("radius")), target_scope="self-and-allies",
        attack_roll_advantage=True, saving_throw_advantage=True,
        disabled_while_incapacitated=True,
    )]


def complete_monster_auras(templates: list[CombatantTemplate]) -> list[CombatantTemplate]:
    try:
        return [
            template.model_copy(update={
                "end_turn_damage_auras": source_end_turn_damage_auras(template.name),
                "start_turn_save_condition_auras": source_start_turn_condition_auras(template.name),
                "roll_advantage_auras": source_roll_advantage_auras(template.name),
            }) if template.kind == "monster" else template
            for template in templates
        ]
    except Exception as exc:
        logger.exception("Failed to derive monster auras from SRD source.")
        raise RuntimeError("Monster aura source compilation failed.") from exc


def complete_monster_end_turn_damage_auras(templates: list[CombatantTemplate]) -> list[CombatantTemplate]:
    return complete_monster_auras(templates)


def fire_aura_source_is_fully_modeled(row: dict[str, object]) -> bool:
    text = str(row.get("traits", ""))
    if not _FIRE_AURA.search(text):
        return False
    lowered = text.lower()
    return not any(term in lowered for term in ("burning", "ignite", "ignites", "catches fire"))
