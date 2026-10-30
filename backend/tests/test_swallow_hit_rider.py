from __future__ import annotations

import logging

from app.combat.grapple import apply_grapple
from app.combat.state import build_combatant_state
from app.combat.swallow_hit_rider import apply_attack_hit_swallow
from app.content.monsters import build_commoner
from app.domain.size import CreatureSize
from app.domain.swallow_actions import GrappleSwallowAction

logger = logging.getLogger(__name__)


def test_attack_hit_swallow_requires_grapple_from_before_the_hit() -> None:
    try:
        base = build_commoner()
        attack = base.weapon_attack
        assert attack is not None
        action = GrappleSwallowAction(
            source_name="Swallow",
            attack_id=attack.id,
            delivery_mode="attack_hit",
            max_target_size=CreatureSize.MEDIUM,
            damage_dice_count=2,
            damage_dice_size=6,
            damage_type="acid",
            max_swallowed=1,
            exit_movement_ft=15,
        )
        owner = build_combatant_state(
            base.model_copy(update={"swallow_actions": [action]})
        )
        target = build_combatant_state(base)

        apply_grapple(target, "owner", 14, 5, restrains=True)

        assert apply_attack_hit_swallow(
            owner,
            target,
            attack,
            attacker_id="owner",
            defender_id="target",
            pre_hit_grappled_by_attacker=False,
        ) is False
        assert target.swallowed is None
        assert any(item.source_id == "owner" for item in target.grapple_sources)

        assert apply_attack_hit_swallow(
            owner,
            target,
            attack,
            attacker_id="owner",
            defender_id="target",
            pre_hit_grappled_by_attacker=True,
        ) is True
        assert target.swallowed is not None
        assert target.swallowed.source_id == "owner"
        assert target.grapple_sources == []
        assert {"blinded", "restrained"} <= set(target.active_effect_ids)
    except Exception:
        logger.exception("Attack-hit Swallow pre-hit grapple regression failed.")
        raise
