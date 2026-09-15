from __future__ import annotations

import logging

from app.domain.models import CombatantState, WeaponAttack

logger = logging.getLogger(__name__)


def attack_available_for_source(attack: WeaponAttack, attacker: CombatantState) -> bool:
    try:
        relation = attacker.attachment
        return relation is None or attack.id not in relation.forbids_source_attack_ids
    except Exception as exc:
        logger.exception("Failed to evaluate source legality for attack %s.", attack.id)
        raise RuntimeError("Attack source legality could not be evaluated.") from exc


def attack_allowed_against(
    attack: WeaponAttack,
    attacker_event_id: str,
    defender: CombatantState,
) -> bool:
    try:
        if not attack.forbid_target_grappled_by_self:
            return True
        return not any(source.source_id == attacker_event_id for source in defender.grapple_sources)
    except Exception as exc:
        logger.exception("Failed to evaluate target legality for attack %s.", attack.id)
        raise RuntimeError("Attack target legality could not be evaluated.") from exc
