"""Source-backed 2014 Command selection using only shared combat effects.

Data schema: a complete prepared spell entry with exact id/name/level plus
source-owned save DC and printed Spellcasting evidence.
Fight state: ordinary spell slot, language-aware target eligibility and the
existing one-target-turn Prone/end-turn marker. No Command-specific resolver.
"""
from __future__ import annotations

import logging
import re

from app.content.monster_source_2014 import SourceMonster2014
from app.domain.save_effects import FailedSaveTimedEffect
from app.domain.spells import SpellSaveAction

logger = logging.getLogger(__name__)
_COMMAND_SOURCE = {"id": "command", "name": "command", "level": 1}


def command_grovel_2014(save_dc: int) -> SpellSaveAction:
    """Build the printed 2014 spell with the Pit's locked Grovel choice."""
    try:
        if type(save_dc) is not int or not 1 <= save_dc <= 40:
            raise ValueError("2014 Command requires a source-owned Wisdom save DC.")
        return SpellSaveAction(
            id="command",
            name="Command",
            level=1,
            action_cost="action",
            range_ft=60,
            save_ability="wisdom",
            dc=save_dc,
            requires_target_sight=True,
            requires_shared_spoken_language=True,
            excluded_target_creature_types=["undead"],
            # The existing turn-entry resolver applies Prone on the NEXT turn.
            # The marker expires at the END of that turn; Prone does not.
            failed_save_timed_effect=FailedSaveTimedEffect(
                effect_id="commanded",
                duration_target_turns=1,
                expiry_timing="target_turn_end",
                turn_behavior="fall_prone_end_turn",
            ),
            # Each slot above first level commands one additional legal target.
            allows_higher_slots=True,
            target_count=1,
            target_count_per_slot_above=1,
            max_target_pair_distance_ft=30,
            animation="spell-save",
        )
    except Exception:
        logger.exception("Unable to bind source-accurate 2014 Command.")
        raise


def prepared_command_spell_actions_2014(
    monster: SourceMonster2014,
) -> tuple[SpellSaveAction, ...]:
    """Bind Command only when printed and structured source evidence agrees."""
    try:
        source = monster.spellcasting
        if not isinstance(source, dict) or source.get("source_complete") is not True:
            return ()
        spells = source.get("spells")
        if not isinstance(spells, list):
            raise ValueError("Complete prepared spell source lacks a spell list.")
        commands = [
            item for item in spells
            if isinstance(item, dict) and item.get("id") == "command"
        ]
        if not commands:
            return ()
        if len(commands) != 1 or commands[0] != _COMMAND_SOURCE:
            raise ValueError("2014 Command source entry must match its printed level/name.")
        if "Spellcasting" not in monster.trait_names or not re.search(
            r"\bcommand\b", monster.source_traits or "", re.IGNORECASE,
        ):
            raise ValueError("2014 Command is missing printed Spellcasting evidence.")
        if type(source.get("save_dc")) is not int:
            raise ValueError("2014 Command is missing its printed spell save DC.")
        return (command_grovel_2014(source["save_dc"]),)
    except Exception:
        logger.exception("2014 prepared Command source proof failed for %s.", monster.id)
        raise
