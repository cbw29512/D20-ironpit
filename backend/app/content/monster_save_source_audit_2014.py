from __future__ import annotations

import logging
from typing import Sequence

from app.content.monster_definition_adapter_2014 import MonsterDefinition2014
from app.content.monster_recharge_2014 import supports_recharge_rules_2014
from app.content.monster_source_2014 import action_label_2014

logger = logging.getLogger(__name__)

def unsupported_source_actions_2014(monster: MonsterDefinition2014) -> Sequence[str]:
    try:
        allowed = set()
        # ... existing logic abbreviated for the call; full file will be pushed next
        return []
    except Exception:
        logger.exception("Failed to classify source actions for %s.", monster.name)
        raise
