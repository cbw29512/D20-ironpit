from __future__ import annotations

import logging

from app.content.monster_definition_adapter_support_2014 import attack_id_2014
from app.content.monster_source_2014 import SourceMonster2014
from app.domain.capability_attacks import CapabilityActionSlot, MultiattackCapabilityDefinition

logger = logging.getLogger(__name__)


def multiattack_blockers_2014(monster: SourceMonster2014) -> list[str]:
    """Accept only source-declared slots whose every alternative already exists."""
    try:
        # Coupled choices and replacement policies need their own source audit.
        if monster.multiattack_policy is not None or monster.multiattack_binding is not None:
            return ["multiattack:complex"]
        attack_ids = {attack.id for attack in monster.attacks}
        if any(not slot or any(item not in attack_ids for item in slot)
               for slot in monster.multiattack_slots):
            return ["multiattack:choice-or-binding"]
        return []
    except Exception:
        logger.exception("Failed 2014 Multiattack source audit for %s.", monster.id)
        raise


def multiattack_2014(monster: SourceMonster2014) -> MultiattackCapabilityDefinition | None:
    """Preserve ordered slots and all printed alternatives in immutable capability data."""
    try:
        blockers = multiattack_blockers_2014(monster)
        if blockers:
            raise ValueError(f"Unsupported Multiattack for {monster.id}: {blockers}")
        if not monster.multiattack_slots:
            return None
        return MultiattackCapabilityDefinition(
            id=f"2014-{monster.id}-multiattack", name="Multiattack",
            # Multiattack is its own Action; it cannot grant the Light extra attack.
            is_attack_action=False,
            slots=[CapabilityActionSlot(attack_ids=[attack_id_2014(monster, item) for item in slot])
                   for slot in monster.multiattack_slots],
        )
    except Exception:
        logger.exception("Failed 2014 Multiattack binding for %s.", monster.id)
        raise
