from __future__ import annotations

import json
import logging
from pathlib import Path

from app.content.monster_spell_actions_2014 import SPELL_TARGET_RULES_2014
from app.content.shared_spell_actions_2014 import build_faerie_fire
from app.content.spell_effects import BLESS, SHIELD_OF_FAITH
from browser_template_serializer import defense_row

logger = logging.getLogger(__name__)
ROOT = Path(__file__).resolve().parents[1]
DESTINATION = ROOT / "frontend" / "browser-spell-effects.js"


def _target_rules() -> dict[str, dict[str, list[str]]]:
    return {
        spell_id: {
            "excludedCreatureTypes": list(rule.get("excluded_creature_types", [])),
            "saveDisadvantageCreatureTypes": list(rule.get("save_disadvantage_creature_types", [])),
            "maximizeDamageCreatureTypes": list(rule.get("maximize_damage_creature_types", [])),
        }
        for spell_id, rule in SPELL_TARGET_RULES_2014.items()
    }


def _modifier(effect) -> dict[str, object]:
    row: dict[str, object] = {"kind": effect.kind}
    if effect.flat_bonus: row["flatBonus"] = effect.flat_bonus
    if effect.dice_count: row.update(diceCount=effect.dice_count, diceSize=effect.dice_size)
    if effect.damage_type: row["damageType"] = effect.damage_type
    if effect.consume_on_attack_against: row["consumeOnAttackAgainst"] = True
    if effect.expires_at_start_of_source_turn: row["expiresAtStartOfSourceTurn"] = True
    if effect.expires_after_source_turns is not None: row["expiresAfterSourceTurns"] = effect.expires_after_source_turns
    return row


def _faerie_fire_row() -> dict[str, object]:
    spell = build_faerie_fire(1)
    return {
        "id": spell.id,
        "durationMinutes": spell.duration_minutes,
        "failureModifierEffects": [_modifier(effect) for effect in spell.failure_modifier_effects],
    }


def render() -> str:
    rows = [defense_row(BLESS), defense_row(SHIELD_OF_FAITH), _faerie_fire_row()]
    payload = json.dumps(rows, separators=(",", ":"), sort_keys=True)
    rules = json.dumps(_target_rules(), separators=(",", ":"), sort_keys=True)
    return (
        "/* GENERATED from canonical Python certified spell effects. Do not hand-edit. */\n"
        "(() => {\n  \"use strict\";\n"
        f"  const spells = {payload};\n"
        "  window.IRON_PIT_BROWSER_SPELL_EFFECTS = Object.fromEntries(spells.map((item) => [item.id, item]));\n"
        f"  window.IRON_PIT_BROWSER_SPELL_TARGET_RULES = {rules};\n"
        "})();\n"
    )


def main() -> None:
    try:
        DESTINATION.write_text(render(), encoding="utf-8")
        logger.info("Exported certified browser spell effects to %s.", DESTINATION)
    except Exception:
        logger.exception("Certified browser spell-effect export failed.")
        raise


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    main()
