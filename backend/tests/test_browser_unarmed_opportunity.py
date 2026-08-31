from __future__ import annotations

import json
from pathlib import Path

from app.content.certified_heroes import build_certified_hero_templates
from app.content.roster import build_arena_roster
from app.domain.models import CombatantTemplate, WeaponAttackKind

_REGISTRY = Path(__file__).resolve().parents[2] / "frontend" / "browser-unarmed-opportunity.js"
_MARKER = "window.IRON_PIT_UNARMED_OPPORTUNITY = "


def _has_five_foot_melee(template: CombatantTemplate) -> bool:
    attacks = [template.weapon_attack, *template.alternate_weapon_attacks]
    return any(
        attack.weapon.attack_kind is WeaponAttackKind.MELEE and attack.weapon.reach_ft == 5
        for attack in attacks
    )


def _browser_profiles() -> dict[str, dict[str, int]]:
    text = _REGISTRY.read_text(encoding="utf-8")
    payload = text.split(_MARKER, 1)[1].split(";\n", 1)[0]
    return json.loads(payload)


def test_browser_unarmed_fallbacks_match_canonical_runtime_profiles() -> None:
    expected: dict[str, dict[str, int]] = {}
    for template in build_arena_roster().monsters:
        if _has_five_foot_melee(template):
            continue
        profile = template.unarmed_opportunity_attack
        assert profile is not None, f"Missing canonical Unarmed Strike profile for {template.name}."
        expected[template.id] = {"attack_bonus": profile.attack_bonus, "damage": profile.damage}

    assert _browser_profiles() == expected


def test_browser_certified_heroes_keep_a_five_foot_melee_option() -> None:
    missing = [template.name for template in build_certified_hero_templates() if not _has_five_foot_melee(template)]
    assert missing == [], f"Browser heroes need an exported Unarmed Strike fallback: {missing}"
