"""Pinned source and canonical compiler helpers for included poison weapon tests."""
import logging

from app.content.capability_compiler import compile_combatant
from app.content.monster_definition_adapter_2014 import adapt_basic_monster_2014
from app.content.monster_source_2014 import load_monster_source_2014

logger = logging.getLogger(__name__)


def source():
    try:
        return next(monster for monster in load_monster_source_2014() if monster.id == "erinyes")
    except Exception:
        logger.exception("Failed to retrieve the pinned 2014 Erinyes test source.")
        raise


def card():
    try:
        return compile_combatant(adapt_basic_monster_2014(source()))
    except Exception:
        logger.exception("Failed to compile the source-complete 2014 Erinyes test card.")
        raise
