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
    attacks = [template.weapon_attack, *template.alternate_weapon_attacks]
    return any(
        attack.weapon.attack_kind is WeaponAttackKind.MELEE and attack.weapon.reach_ft == 5
        for attack in attacks
    )


def build_profiles() -> dict[str, dict[str, int]]:
    try:
        profiles: dict[str, dict[str, int]] = {}
        for template in build_arena_roster().monsters:
            if _has_five_foot_melee(template):
                continue
            profile = template.unarmed_opportunity_attack
            if profile is None:
                raise ValueError(f"Missing canonical Unarmed Strike profile for {template.name}.")
            profiles[template.id] = {
                "attack_bonus": profile.attack_bonus,
                "damage": profile.damage,
            }
        return profiles
    except Exception:
        logger.exception("Failed to derive browser unarmed Opportunity Attack profiles.")
        raise


def main() -> None:
    try:
        payload = json.dumps(build_profiles(), separators=(",", ":"), sort_keys=True)
        content = f'(() => {{\n  "use strict";\n\n  window.IRON_PIT_UNARMED_OPPORTUNITY = {payload};\n}})();\n'
        DESTINATION.write_text(content, encoding="utf-8")
        logger.info("Exported browser unarmed Opportunity Attack profiles to %s.", DESTINATION)
    except Exception:
        logger.exception("Browser unarmed Opportunity Attack export failed.")
        raise


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    main()
