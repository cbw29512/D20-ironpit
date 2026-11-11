from __future__ import annotations

import logging

from collections.abc import Iterable

from app.domain.models import CombatantState, WeaponAttack
from app.domain.size import size_at_most
from app.combat.condition_rules import is_incapacitated

logger = logging.getLogger(__name__)


def attack_allowed_against(
    attack: WeaponAttack,
    attacker_event_id: str,
    defender: CombatantState,
    encounter_states: Iterable[CombatantState] | None = None,
) -> bool:
    try:
        if attack.unavailable_reason is not None or defender.swallowed is not None:
            return False
        if defender.is_dead or (defender.template.kind == "monster" and defender.current_hp <= 0):
            return False
        if attack.target_max_size is not None and not size_at_most(defender.template.size, attack.target_max_size):
            return False
        defender_owned = any(source.source_id == attacker_event_id for source in defender.grapple_sources)
        if attack.forbid_target_grappled_by_self and defender_owned:
            return False
        if attack.target_qualification is not None:
            allowed = set(attack.target_qualification.any_of)
            if not (
                ("source_grappled" in allowed and defender_owned)
                or ("incapacitated" in allowed and is_incapacitated(defender))
                or ("restrained" in allowed and "restrained" in defender.active_effect_ids)
                or ("willing" in allowed and attacker_event_id in defender.willing_attack_source_ids)
            ):
                return False
        if attack.grapple_target_policy == "normal":
            return True
        if attack.grapple_target_policy not in {"own_grapple_only", "auto_hit_own_grapple"}:
            raise ValueError(f"Unsupported grapple target policy: {attack.grapple_target_policy}")
        if defender_owned:
            return True
        if encounter_states is None:
            return True
        return not any(
            any(source.source_id == attacker_event_id for source in state.grapple_sources)
            for state in encounter_states
        )
    except Exception as exc:
        logger.exception("Failed to evaluate target legality for attack %s.", attack.id)
        raise RuntimeError("Attack target legality could not be evaluated.") from exc
