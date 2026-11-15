"""Read-only 2014 monster spell-family coverage audit.

Immutable schema: SourceMonster2014 spellcasting/innate_spellcasting and source spells.
Runtime state: none; the audit invokes only existing action builders and classifiers.
"""
from __future__ import annotations

import logging
from pathlib import Path

from app.content.monster_source_2014 import load_monster_source_2014
from app.content.monster_prepared_spells_2014 import (
    _prepared_spells, prepared_spell_save_actions_2014,
    prepared_spell_attack_actions_2014, prepared_auto_hit_spell_actions_2014,
    prepared_persistent_save_zone_actions_2014, supports_prepared_spellcasting_2014,
)
from app.content.monster_prepared_cleric_spells_2014 import prepared_cleric_spell_actions_2014
from app.content.monster_prepared_nature_spells_2014 import prepared_nature_spells_2014
from app.content.monster_source_tier1_cleric_2014 import source_proves_tier1_cleric_spells_2014
from app.content.monster_source_priest_spellcasting_2014 import priest_proven_spell_ids_2014
from app.content.monster_command_spell_2014 import prepared_command_spell_actions_2014
from app.content.monster_innate_support_2014 import (
    supports_innate_spellcasting_2014, innate_timed_self_buffs_2014,
)
from app.content.monster_innate_spells_2014 import (
    _spells, _innate, ARENA_NEUTRAL_INNATE_SPELLS_2014,
    _PIT_BANNED_INNATE_SPELLS_2014, innate_spell_save_actions_2014,
    innate_auto_hit_spell_actions_2014, innate_spell_attack_actions_2014,
    innate_persistent_save_zone_actions_2014,
)
from app.content.monster_hp_pool_spell_bindings_2014 import innate_hp_pool_spells_2014
from app.content.monster_environmental_spell_proofs_2014 import source_proven_arena_inert_innate_spells_2014
from app.content.monster_source_angelic_innate_2014 import source_proven_angelic_arena_exclusions_2014
from app.content.monster_innate_darkness_2014 import source_proven_innate_darkness_2014
from app.content.monster_innate_fog_cloud_2014 import source_proven_innate_fog_cloud_2014
from app.content.monster_innate_misty_step_2014 import source_proven_innate_misty_step_2014
from app.content.monster_innate_ai_exclusions_2014 import source_proven_arena_ai_excluded_innate_spells_2014

logger = logging.getLogger(__name__)


def blocked_caster_names(report: Path) -> tuple[str, ...]:
    """The generated blocker report, not an editable name list, chooses the cohort."""
    try:
        rows = []
        for line in report.read_text(encoding="utf-8").splitlines():
            if not line.startswith("| ") or "mechanic:spellcasting" not in line:
                continue
            name, family = [part.strip() for part in line.split("|")[1:3]]
            if name != "`mechanic:spellcasting`" and family.startswith(("mechanic:", "source:", "attack:", "multiattack:")):
                rows.append(name)
        if len(rows) != 17 or len(set(rows)) != 17:
            raise ValueError(f"Expected 17 unique blocked 2014 casters, found {len(rows)}")
        return tuple(rows)
    except Exception:
        logger.exception("Failed to select 2014 spellcasting blockers from %s", report)
        raise


def _ids(*collections) -> set[str]:
    return {action.id for collection in collections for action in collection}


def prepared_spell_gap(card) -> dict:
    try:
        source = card.spellcasting
        entries = _prepared_spells(card)
        known = {str(item.get("id") or "") for item in entries}
        bound = _ids(
            prepared_spell_save_actions_2014(card),
            prepared_spell_attack_actions_2014(card),
            prepared_auto_hit_spell_actions_2014(card),
            prepared_persistent_save_zone_actions_2014(card),
            prepared_command_spell_actions_2014(card),
        )
        if source_proves_tier1_cleric_spells_2014(card):
            bound |= {"light", "thaumaturgy", "bless", "cure-wounds", "sanctuary"}
        bound |= priest_proven_spell_ids_2014(card)
        bound |= prepared_cleric_spell_actions_2014(card).implemented_ids()
        bound |= prepared_nature_spells_2014(card).implemented_ids()
        return {
            "kind": "prepared", "complete_source": bool(isinstance(source, dict) and source.get("source_complete")),
            "known": sorted(known), "unbound": sorted(known - bound),
            "classifier_supported": supports_prepared_spellcasting_2014(card),
            "spell_count": len(known),
        }
    except Exception:
        logger.exception("Failed prepared-spell audit for %s", card.name)
        raise


def innate_spell_gap(card) -> dict:
    try:
        source = _innate(card)
        known = {str(item.get("id") or "") for item in _spells(card)}
        bound = set(ARENA_NEUTRAL_INNATE_SPELLS_2014) | set(_PIT_BANNED_INNATE_SPELLS_2014)
        bound |= set(source_proven_arena_inert_innate_spells_2014(card))
        bound |= set(source_proven_angelic_arena_exclusions_2014(card))
        bound |= set(source_proven_arena_ai_excluded_innate_spells_2014(card))
        bound |= _ids(
            innate_spell_save_actions_2014(card), innate_auto_hit_spell_actions_2014(card),
            innate_hp_pool_spells_2014(card), innate_spell_attack_actions_2014(card),
            innate_timed_self_buffs_2014(card), innate_persistent_save_zone_actions_2014(card),
            source_proven_innate_darkness_2014(card), source_proven_innate_fog_cloud_2014(card),
            source_proven_innate_misty_step_2014(card),
        )
        return {
            "kind": "innate", "complete_source": bool(isinstance(source, dict) and source.get("source_complete")),
            "known": sorted(known), "unbound": sorted(known - bound),
            "classifier_supported": supports_innate_spellcasting_2014(card),
            "spell_count": len(known),
        }
    except Exception:
        logger.exception("Failed innate-spell audit for %s", card.name)
        raise
