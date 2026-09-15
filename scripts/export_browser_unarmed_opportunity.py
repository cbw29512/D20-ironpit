from __future__ import annotations

import json
import logging
from pathlib import Path

from app.content.roster import build_arena_roster
from app.domain.models import CombatantTemplate, WeaponAttackKind

logger = logging.getLogger(__name__)
ROOT = Path(__file__).resolve().parents[1]
DESTINATION = ROOT / "frontend" / "browser-unarmed-opportunity.js"


def _has_five_foot_melee(template: CombatantTemplate) -> bool:
    try:
        attacks = [template.weapon_attack, *template.alternate_weapon_attacks]
        return any(
            attack.weapon.attack_kind is WeaponAttackKind.MELEE and attack.weapon.reach_ft == 5
            for attack in attacks
        )
    except Exception:
        logger.exception("Failed to inspect melee reach for %s.", template.name)
        raise


def build_payload() -> dict[str, dict[str, int]]:
    try:
        payload: dict[str, dict[str, int]] = {}
        for template in build_arena_roster().monsters:
            if _has_five_foot_melee(template):
                continue
            profile = template.unarmed_opportunity_attack
            if profile is None:
                raise RuntimeError(f"Missing canonical Unarmed Strike profile for {template.name}.")
            payload[template.id] = {
                "attack_bonus": profile.attack_bonus,
                "damage": profile.damage,
            }
        return payload
    except Exception:
        logger.exception("Failed to build browser Unarmed Strike fallback payload.")
        raise


def render() -> str:
    try:
        payload = json.dumps(build_payload(), separators=(",", ":"), sort_keys=True)
        return (
            "/* GENERATED from canonical runtime Unarmed Strike fallbacks. Do not hand-edit. */\n"
            "(() => {\n  \"use strict\";\n"
            f"  window.IRON_PIT_UNARMED_OPPORTUNITY = {payload};\n"
            "})();\n"
        )
    except Exception:
        logger.exception("Failed to render browser Unarmed Strike fallback registry.")
        raise


def main() -> None:
    try:
        DESTINATION.write_text(render(), encoding="utf-8")
        logger.info("Exported canonical browser Unarmed Strike fallback registry.")
    except Exception:
        logger.exception("Browser Unarmed Strike fallback export failed.")
        raise


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    main()
