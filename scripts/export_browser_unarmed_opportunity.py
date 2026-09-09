from __future__ import annotations

import json
from pathlib import Path

from app.content.roster import build_arena_roster
from app.domain.models import CombatantTemplate, WeaponAttackKind

ROOT = Path(__file__).resolve().parents[1]
DESTINATION = ROOT / "frontend" / "browser-unarmed-opportunity.js"


def _has_five_foot_melee(template: CombatantTemplate) -> bool:
    attacks = [template.weapon_attack, *template.alternate_weapon_attacks]
    return any(
        attack.weapon.attack_kind is WeaponAttackKind.MELEE and attack.weapon.reach_ft == 5
        for attack in attacks
    )


def main() -> None:
    profiles: dict[str, dict[str, int]] = {}
    for template in build_arena_roster().monsters:
        if _has_five_foot_melee(template):
            continue
        profile = template.unarmed_opportunity_attack
        if profile is None:
            raise RuntimeError(f"Missing Unarmed Strike profile for {template.name}.")
        profiles[template.id] = {"attack_bonus": profile.attack_bonus, "damage": profile.damage}
    payload = json.dumps(profiles, separators=(",", ":"), sort_keys=True)
    DESTINATION.write_text(
        '(() => {\n  "use strict";\n\n  window.IRON_PIT_UNARMED_OPPORTUNITY = ' + payload + ';\n})();\n',
        encoding="utf-8",
    )


if __name__ == "__main__":
    main()
