from __future__ import annotations

import json
import logging
from pathlib import Path

from app.content.monster_catalog import build_monster_catalog
from app.content.roster import build_arena_roster
from app.domain.catalog import CoverageStatus
from browser_template_serializer import template_row

logger = logging.getLogger(__name__)
ROOT = Path(__file__).resolve().parents[1]
DESTINATION = ROOT / "frontend" / "browser-monsters-generated.js"


def _certified_monsters():
    catalog = build_monster_catalog()
    ready_ids = {card.runnable_template_id for card in catalog if card.coverage_status is CoverageStatus.RAW_READY and card.runnable_template_id is not None}
    monsters = [template for template in build_arena_roster().monsters if template.id in ready_ids]
    if {template.id for template in monsters} != ready_ids:
        raise RuntimeError("RAW-ready catalog and canonical monster roster disagree.")
    return monsters


def _aura_row(template):
    aura = template.end_turn_damage_aura
    if aura is None: return None
    return {"name": aura.name, "radius": aura.radius_ft, "diceCount": aura.dice_count, "diceSize": aura.dice_size,
            "damageBonus": aura.damage_bonus, "damageType": aura.damage_type.value, "targetMode": aura.target_mode,
            "disabledWhileIncapacitated": aura.disabled_while_incapacitated}


def _roll_aura_row(template):
    aura = template.roll_advantage_aura
    if aura is None: return None
    return {"name": aura.name, "radius": aura.radius_ft, "grantsAttackRollAdvantage": aura.grants_attack_roll_advantage,
            "grantsSavingThrowAdvantage": aura.grants_saving_throw_advantage,
            "disabledWhileIncapacitated": aura.disabled_while_incapacitated}


def render() -> str:
    try:
        rows = []
        for template in _certified_monsters():
            row = template_row(template); row["creature_type"] = template.creature_type
            aura = _aura_row(template)
            if aura: row["endTurnDamageAura"] = aura
            roll_aura = _roll_aura_row(template)
            if roll_aura: row["rollAdvantageAura"] = roll_aura
            rows.append(row)
        ids = {row["id"] for row in rows}
        if len(rows) != len(ids): raise RuntimeError("Certified browser monster export contains duplicate template IDs.")
        payload = json.dumps(rows, separators=(",", ":"), sort_keys=True)
        return ("/* GENERATED from canonical Python RAW-ready monster templates. Do not hand-edit. */\n" "(() => {\n  \"use strict\";\n"
                f"  const monsters = {payload};\n" "  window.IRON_PIT_BROWSER_MONSTERS = Object.fromEntries(monsters.map((item) => [item.id, item]));\n"
                "  window.IRON_PIT_CANONICAL_MONSTERS_READY = true;\n" "})();\n")
    except Exception:
        logger.exception("Certified browser monster rendering failed."); raise


def main() -> None:
    try:
        content = render(); DESTINATION.write_text(content, encoding="utf-8"); logger.info("Exported canonical browser monsters to %s.", DESTINATION)
    except Exception:
        logger.exception("Certified browser monster export failed."); raise


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO); main()
