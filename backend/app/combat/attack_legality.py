from __future__ import annotations

import logging

from app.domain.models import CombatantState, WeaponAttack
from app.domain.size import size_at_most

logger = logging.getLogger(__name__)


def attack_allowed_against(
    attack: WeaponAttack,
    attacker_event_id: str,
    defender: CombatantState,
) -> bool:
    try:
        restraint = attack.breakable_restraint
        if restraint is not None:
            if restraint.max_target_size is not None and not size_at_most(defender.template.size, restraint.max_target_size):
                return False
            if any(source.source_id == attacker_event_id and source.source_effect_id == attack.id for source in defender.restraint_sources):
                return False
        if not attack.forbid_target_grappled_by_self:
            return True
        return not any(source.source_id == attacker_event_id for source in defender.grapple_sources)
    except Exception as exc:
        logger.exception("Failed to evaluate target legality for attack %s.", attack.id)
        raise RuntimeError("Attack target legality could not be evaluated.") from exc
