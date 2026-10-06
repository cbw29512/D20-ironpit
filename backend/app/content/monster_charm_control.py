"""Shared charm / possession / dominate control for Iron Pit.

Chris lock: the affected creature stands and does nothing until it is hit,
succeeds on a save, or the printed duration ends. Every such effect also
gets a repeat save vs the printed DC at the end of each of its turns.
Reuse FailedSaveTimedEffect + the existing incapacitated condition.
No monster-name dispatch.
"""
from __future__ import annotations

import logging
import re

from app.content.monster_source_2014 import SourceMonster2014
from app.domain.capability_attacks import SaveCapabilityDefinition
from app.domain.save_effects import FailedSaveTimedEffect
from app.domain.spells import SpellSaveAction

logger = logging.getLogger(__name__)

CHARM_CONTROL_ACTION_LABELS = frozenset({"charm", "possession"})
CHARM_CONTROL_SPELL_IDS = frozenset({
    "charm-person",
    "charm-monster",
    "dominate-person",
    "dominate-monster",
})
_SAVE = re.compile(
    r"DC\s+(\d+)\s+(Strength|Dexterity|Constitution|Intelligence|Wisdom|Charisma)",
    re.I,
)
_RANGE = re.compile(r"within\s+(\d+)\s+feet", re.I)
_ABILITIES = {
    "strength": "strength",
    "dexterity": "dexterity",
    "constitution": "constitution",
    "intelligence": "intelligence",
    "wisdom": "wisdom",
    "charisma": "charisma",
}


def charm_control_rider(dc: int, save_ability: str) -> FailedSaveTimedEffect:
    """Incapacitated until damage, a successful repeat save, or match end."""
    try:
        return FailedSaveTimedEffect(
            effect_id="incapacitated",
            duration_rounds=100,
            expiry_timing="target_turn_end",
            repeat_save_ability=save_ability,
            repeat_save_dc=dc,
            repeat_save_timing="target_turn_end",
            ends_on_damage=True,
            source_effect_immunity_on_end=True,
        )
    except Exception:
        logger.exception("Failed to build the shared charm/possession rider.")
        raise


def _paragraph_for(source_html: str, label: str) -> str:
    text = re.sub(r"<[^>]+>", " ", source_html or " ")
    text = re.sub(r"\s+", " ", text)
    pattern = re.compile(
        rf"{re.escape(label)}\.?\s*(.*?)(?=(?:[A-Z][A-Za-z'’\-]*(?:\s+[A-Z][A-Za-z'’\-]*){{0,4}}\s*\(|[A-Z][A-Za-z'’\-]*(?:\s+[A-Z][A-Za-z'’\-]*){{0,4}}\.|$))",
        re.S,
    )
    match = pattern.search(text)
    return match.group(1) if match else text


def _facts(blob: str, fallback_ability: str) -> tuple[int, str, int] | None:
    save = _SAVE.search(blob)
    if save is None:
        return None
    dc = int(save.group(1))
    ability = _ABILITIES[save.group(2).casefold()]
    ranged = _RANGE.search(blob)
    return dc, ability or fallback_ability, int(ranged.group(1)) if ranged else 30


def charm_control_save_actions_2014(monster: SourceMonster2014) -> list[SaveCapabilityDefinition]:
    """Bind printed Charm / Possession extra-actions to the shared control rider."""
    try:
        actions: list[SaveCapabilityDefinition] = []
        source = monster.source_actions or ""
        for name in monster.action_names:
            label = name.split(" (Recharge", 1)[0].strip().casefold()
            if label not in CHARM_CONTROL_ACTION_LABELS:
                continue
            facts = _facts(_paragraph_for(source, name.split(" (", 1)[0]), "wisdom")
            if facts is None:
                raise ValueError(f"{monster.name} {name} has no parseable save DC.")
            dc, ability, range_ft = facts
            resource_id = None
            for action_id in monster.action_recharges:
                if action_id.replace("-", " ") == label:
                    resource_id = action_id
                    break
            actions.append(SaveCapabilityDefinition(
                id=f"2014-{monster.id}-{label}".replace(" ", "-"),
                name=name.split(" (", 1)[0],
                save_ability=ability,
                dc=dc,
                range_ft=range_ft,
                resource_id=resource_id,
                magical_effect=True,
                effect_tags=["charm-control"],
                failed_save_timed_effect=charm_control_rider(dc, ability),
                source_effect_immunity_on_success=True,
                animation="charm-control",
            ))
        return actions
    except Exception:
        logger.exception("Failed to bind 2014 charm/possession actions for %s.", monster.name)
        raise


def charm_control_spell_actions_2014(monster: SourceMonster2014) -> list[SpellSaveAction]:
    """Bind printed charm/dominate spells to the shared incapacitated-until-hit rider."""
    try:
        actions: list[SpellSaveAction] = []
        for blob in (monster.spellcasting, monster.innate_spellcasting):
            if not isinstance(blob, dict):
                continue
            dc_raw = blob.get("save_dc")
            if dc_raw is None:
                continue
            dc = int(dc_raw)
            for spell in blob.get("spells") or []:
                if not isinstance(spell, dict):
                    continue
                spell_id = str(spell.get("id") or "")
                if spell_id not in CHARM_CONTROL_SPELL_IDS:
                    continue
                name = str(spell.get("name") or spell_id).replace("-", " ").title()
                dominate = spell_id.startswith("dominate-")
                actions.append(SpellSaveAction(
                    id=spell_id,
                    name=name,
                    level=max(1, int(spell.get("level") or (5 if dominate else 1))),
                    range_ft=60,
                    save_ability="wisdom",
                    dc=dc,
                    effect_tags=["charm-control"],
                    failed_save_timed_effect=charm_control_rider(dc, "wisdom"),
                    concentration=dominate,
                    duration_minutes=1 if dominate else None,
                    animation="charm-control",
                ))
        return actions
    except Exception:
        logger.exception("Failed to bind 2014 charm/dominate spells for %s.", monster.name)
        raise
