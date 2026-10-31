"""Browser serialization must retain source-owned composite hit-save conditions."""
from __future__ import annotations

import logging

from app.content.monster_basic_attack_effects_2014 import basic_attack_effects_2014
from app.content.monster_source_2014 import load_monster_source_2014
from app.domain.capability_effects import SaveDamageEffectDefinition

logger = logging.getLogger(__name__)


def test_quasit_compiles_one_save_with_failed_condition():
    try:
        quasit = next(m for m in load_monster_source_2014() if m.id == "quasit")
        attack = next(a for a in quasit.attacks if a.id == "claws-bite-in-beast-form")
        effects = basic_attack_effects_2014(attack)
        composite = next(e for e in effects if isinstance(e, SaveDamageEffectDefinition))
        assert composite.dc == 10
        assert composite.dice.count == 2 and composite.dice.size == 4
        assert composite.failed_save_condition is not None
        assert composite.failed_save_condition.condition == "poisoned"
        assert composite.failed_save_condition.repeat_save_timing == "target_turn_end"
    except Exception:
        logger.exception("Quasit failed save compilation regression")
        raise
