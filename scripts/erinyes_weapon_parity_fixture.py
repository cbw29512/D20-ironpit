"""Compile immutable 2014 source and Python-oracle hit results for browser parity."""
from __future__ import annotations

import json
import logging

from app.combat.attacks import resolve_attack
from app.combat.dice import FixedDiceProvider
from app.combat.state import build_combatant_state
from app.content.capability_compiler import compile_combatant
from app.content.certified_heroes import build_certified_hero_templates_for_ruleset
from app.content.monster_definition_adapter_2014 import adapt_basic_monster_2014
from app.content.monster_source_2014 import load_monster_source_2014
from app.content.monsters import build_commoner
from app.domain.models import CombatantTemplate
from app.domain.weapons import DamageType
from browser_template_serializer import template_row

logger = logging.getLogger(__name__)


def fixture():
    try:
        source = next(item for item in load_monster_source_2014() if item.id == "erinyes")
        original = compile_combatant(adapt_basic_monster_2014(source))
        cleric = next(item for item in build_certified_hero_templates_for_ruleset("2014")
            if item.id == "seraphine-dawnshield-2014-l3")
        cases = []
        for label, save, immune, resistant, renamed in [
            ("failed", 2, False, False, False), ("saved", 20, False, False, False),
            ("immune", 2, True, False, False), ("resistant", 2, False, True, False),
            ("renamed-character", 2, False, False, True),
        ]:
            payload = original.model_dump()
            if renamed:
                payload.update(id="prism-archer", name="Prism Archer", kind="character")
                for attack in [payload["weapon_attack"], *payload["alternate_weapon_attacks"]]:
                    if attack["weapon"]["name"] == "Longbow":
                        attack["id"] = attack["weapon"]["id"] = "prism-bolt"
                        attack["weapon"]["name"] = "Prism Bolt"
                for slot in payload["attack_action"]["slots"]:
                    slot["attack_ids"] = ["prism-bolt" if value == "2014-erinyes-longbow" else value
                                          for value in slot["attack_ids"]]
            actor = CombatantTemplate.model_validate(payload)
            bow = next(item for item in actor.alternate_weapon_attacks if item.on_hit_condition_save)
            target = build_commoner().model_copy(update={
                "max_hp": 200, "condition_immunities": ["poisoned"] if immune else [],
                "damage_resistances": [DamageType.POISON] if resistant else [],
            })
            rolls = [10, 1, 2, 3, 4] + ([] if immune else [save])
            victim = build_combatant_state(target)
            event = resolve_attack(1, 1, build_combatant_state(actor), victim, bow, 20,
                FixedDiceProvider(rolls), close_enemy_active=False)
            cases.append({"id": label, "actor": template_row(actor), "target": template_row(target),
                "attackId": bow.id, "rolls": rolls, "expected": {
                    "damage": event.damage_roll.total, "hp": victim.current_hp,
                    "conditions": victim.active_effect_ids, "saveSucceeded": event.save_succeeded,
                    "parts": [{"type": part.damage_type.value, "total": part.total,
                               "applied": part.applied_total} for part in event.damage_components],
                }})
        return {"cases": cases, "cleric": template_row(cleric)}
    except Exception:
        logger.exception("Failed canonical included-poison weapon Python/browser fixture.")
        raise


if __name__ == "__main__":
    try:
        print(json.dumps(fixture()))
    except Exception:
        logger.exception("Could not emit included-poison weapon parity evidence.")
        raise
