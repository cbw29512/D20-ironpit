"""2014 Invisibility must not silently drop named-action expiry."""
from __future__ import annotations

import logging

from app.content.monster_source_2014 import load_monster_source_2014
from app.content.monster_source_invisibility_2014 import source_invisibility_action_2014

logger = logging.getLogger(__name__)


def test_quasit_invisibility_requires_generic_named_action_expiry():
    try:
        quasit = next(row for row in load_monster_source_2014() if row.id == "quasit")
        assert "or uses Scare" in quasit.source_actions
        # Until a named-action owner-event listener is implemented, the
        # source action must remain unbound instead of expiring incorrectly.
        action, = source_invisibility_action_2014(quasit)
        assert action.ends_on_owner_action_ids == ["scare"]
        assert action.ends_on_owner_attack
        assert not action.ends_on_owner_spell_cast
    except Exception:
        logger.exception("Quasit Invisibility named-exit guard failed")
        raise


def test_imp_invisibility_retains_attack_only_exit():
    try:
        imp = next(row for row in load_monster_source_2014() if row.id == "imp")
        action, = source_invisibility_action_2014(imp)
        assert action.ends_on_owner_attack
        assert not action.ends_on_owner_spell_cast
    except Exception:
        logger.exception("Imp Invisibility exit regression failed")
        raise
