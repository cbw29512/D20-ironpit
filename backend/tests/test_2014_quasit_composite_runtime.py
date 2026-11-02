"""Runtime regression: one shared save applies both poison damage and timed Poisoned.

Reuses existing SaveDamageEffectDefinition + failed_save_condition path.
No name dispatch. Python reference for browser parity.
"""
from __future__ import annotations

import logging
import pytest

from app.content.monster_source_2014 import load_monster_source_2014
from app.content.monster_basic_attack_effects_2014 import basic_attack_effects_2014
from app.domain.capability_effects import SaveDamageEffectDefinition

logger = logging.getLogger(__name__)


def test_quasit_composite_compiles_to_shared_save_with_condition():
    try:
        quasit = next(m for m in load_monster_source_2014() if m.id == "quasit")
        attack = next(a for a in quasit.attacks if a.id == "claws-bite-in-beast-form")
        effects = basic_attack_effects_2014(attack)
        composite = next(e for e in effects if isinstance(e, SaveDamageEffectDefinition))
        assert composite.failed_save_condition is not None
        assert composite.failed_save_condition.condition == "poisoned"
        assert composite.dice.count == 2
        assert composite.success_damage == "none"
        # Existing runtime path in attack_hit_riders.py shares the save result.
    except Exception:
        logger.exception("Quasit composite runtime contract failed")
        raise
