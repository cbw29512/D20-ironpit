from __future__ import annotations

import logging
import re
import unicodedata

from app.content.monster_catalog_2014_arena_policy import is_arena_disabled_action_2014
from app.content.monster_catalog_2014_auras import activated_start_turn_auras_2014
from app.content.monster_catalog_2014_models import CatalogMonster2014

logger = logging.getLogger(__name__)
NONBLOCKING_OPTIONAL_ACTIONS_2014 = frozenset({"change-shape", "weird-insight"})
ARENA_NEUTRAL_REACTIONS_2014 = frozenset({"Shriek", "Shield"})
_PER_DAY = re.compile(r"\((\d+)\s*/\s*Day\)", re.I)


def action_key_2014(value: str) -> str:
    clean = re.sub(r"\s*\(Recharge\s+[^)]+\)", "", value, flags=re.I).rstrip(".")
    clean = re.sub(r"\s*\(\d+\s*/\s*Day\)", "", clean, flags=re.I).rstrip(".")
    if re.fullmatch(r"Multiattack\.?\s*\([^)]*form only\)\.?", clean, re.I):
        clean = "Multiattack"
    text = unicodedata.normalize("NFKD", clean).encode("ascii", "ignore").decode().lower()
    return re.sub(r"[^a-z0-9]+", "-", text).strip("-")


def limited_action_uses_2014(source: CatalogMonster2014) -> dict[str, int]:
    """Return source-derived N/Day action pools without treating the action itself as supported."""
    try:
        uses = dict(source.limited_action_uses)
        for name in source.action_names:
            match = _PER_DAY.search(name)
            if match is not None:
                uses.setdefault(action_key_2014(name), int(match.group(1)))
        return uses
    except Exception as exc:
        logger.exception("Failed to derive limited action uses for %s.", source.id)
        raise ValueError(f"Could not derive limited action uses for {source.id}.") from exc


def _attack_action_ids(source: CatalogMonster2014) -> set[str]:
    supported = {attack.id for attack in source.attacks}
    split_bases: dict[str, set[str]] = {}
    for attack in source.attacks:
        for suffix in ("-melee", "-ranged"):
            if attack.id.endswith(suffix) and attack.source_complete:
                split_bases.setdefault(attack.id.removesuffix(suffix), set()).add(suffix)
    supported.update(base for base, variants in split_bases.items() if variants == {"-melee", "-ranged"})
    return supported


def supported_action_ids_2014(source: CatalogMonster2014) -> set[str]:
    supported = _attack_action_ids(source)
    supported.update(action.id for action in source.swallow_actions)
    supported.update(action.id for action in source.saving_throw_actions)
    supported.update(action.id for action in source.healing_actions)
    supported.update(action.id for action in activated_start_turn_auras_2014(source.source_actions))
    supported.update(action.resource_id for action in source.saving_throw_actions if action.resource_id)
    supported.update(action.resource_id for action in source.healing_actions if action.resource_id)
    supported.update(NONBLOCKING_OPTIONAL_ACTIONS_2014)
    action_keys = {action_key_2014(name) for name in source.action_names}
    if "invisibility" in action_keys:
        supported.add("invisibility")
    if source.multiattack_slots or source.multiattack_binding is not None:
        supported.add("multiattack")
    return supported


def unresolved_actions_2014(source: CatalogMonster2014) -> list[str]:
    try:
        supported = supported_action_ids_2014(source)
        return [
            name for name in source.action_names
            if action_key_2014(name) not in supported and not is_arena_disabled_action_2014(name)
        ]
    except Exception as exc:
        logger.exception("Failed to inventory arena-relevant actions for %s.", source.id)
        raise ValueError(f"Could not inventory arena-relevant actions for {source.id}.") from exc


def unresolved_reactions_2014(source: CatalogMonster2014, supported: set[str]) -> list[str]:
    try:
        supported_names = supported | ARENA_NEUTRAL_REACTIONS_2014
        return [
            name for name in source.reaction_names
            if name not in supported_names and not is_arena_disabled_action_2014(name)
        ]
    except Exception as exc:
        logger.exception("Failed to inventory arena-relevant reactions for %s.", source.id)
        raise ValueError(f"Could not inventory arena-relevant reactions for {source.id}.") from exc
