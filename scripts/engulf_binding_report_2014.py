"""Audit source-verified linked Engulf using the generic browser capability schema."""
from __future__ import annotations

import logging
from app.content.demo import build_demo_fighter
from browser_template_serializer import template_row

logger = logging.getLogger(__name__)


def report_linked_grapple(monster, binding):
    """Return report parameters and strict Python/browser source agreement."""
    try:
        grapple, tick = binding
        card = build_demo_fighter().model_copy(update={
            "multi_hit_grapple_effects": [grapple],
            "source_turn_relation_damages": [tick],
        })
        browser = template_row(card)
        attack = browser.get("multiHitGrappleEffects", [])
        damage = browser.get("source_turn_relation_damages", [])
        expected = {
            "sourceName": grapple.source_name,
            "effectId": grapple.effect_id,
            "standaloneAction": grapple.standalone_action,
            "attackId": grapple.attack_id,
            "hitsRequired": grapple.hits_required,
            "maxTargetSize": grapple.max_target_size.value,
            "escapeDc": grapple.escape_dc,
            "rangeFt": grapple.range_ft,
            "maxActiveGrapples": grapple.max_active_grapples,
            "restrains": grapple.restrains,
            "blinds": grapple.blinds,
            "preventsBreathing": grapple.prevents_breathing,
        }
        parameters = {
            "delivery_mode": "two_hits_or_held_action",
            "attack_id": grapple.attack_id,
            "hits_required": grapple.hits_required,
            "max_target_size": grapple.max_target_size.value,
            "grapple_escape_dc": grapple.escape_dc,
            "damage_dice": f"{tick.dice_count}d{tick.dice_size}+{tick.damage_bonus}",
            "damage_type": tick.damage_type.value,
            "owner_turn_save_ability": tick.save_ability,
            "owner_turn_save_dc": tick.save_dc,
            "max_engulfed": grapple.max_active_grapples,
            "total_external_cover": False,
        }
        return parameters, (len(attack) == len(damage) == 1
                            and attack[0] == expected
                            and damage[0] == tick.model_dump(mode="json"))
    except Exception:
        logger.exception("Source-neutral linked grapple audit failed for %s.", monster.id)
        raise
