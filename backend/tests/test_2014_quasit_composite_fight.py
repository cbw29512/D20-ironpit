"""Python fight verification that Quasit Claws applies damage AND Poisoned on one failed save.

Reuses existing universal on-hit save damage + condition primitives.
No name dispatch. Source mutation fails closed.
"""
from __future__ import annotations

import logging

from app.combat.attack_effect_resolution import resolve_attack_effects
from app.combat.dice import FixedDiceProvider
from app.combat.state import build_combatant_state
from app.content.capability_compiler import compile_combatant
from app.content.demo import build_demo_fighter
from app.content.monster_definition_adapter_2014 import adapt_basic_monster_2014
from app.content.monster_source_2014 import load_monster_source_2014
from app.domain.models import RollMode

logger = logging.getLogger(__name__)


def _quasit_attack():
    try:
        source = next(m for m in load_monster_source_2014() if m.id == "quasit")
        template = compile_combatant(adapt_basic_monster_2014(source))
        attack = next(a for a in [template.weapon_attack, *template.alternate_weapon_attacks]
                      if "Claws" in (a.weapon.name or "") or "Bite" in (a.weapon.name or ""))
        return source, template, attack
    except Exception:
        logger.exception("Failed to load Quasit composite attack")
        raise


def test_failed_composite_save_applies_poison_damage_and_poisoned():
    try:
        source, template, attack = _quasit_attack()
        assert attack.on_hit_save_damage is not None
        assert attack.on_hit_save_damage.failed_save_condition is not None
        defender = build_combatant_state(build_demo_fighter())
        # Fixed: hit roll high, damage dice, save low (fail)
        dice = FixedDiceProvider([20, 3, 4, 1])  # attack, d4 damage, d4, save d20 low
        result = resolve_attack_effects(
            build_combatant_state(template),
            defender,
            attack,
            dice,
            hit=True,
            critical=False,
            mode=RollMode.NORMAL,
            round_number=1,
            attacker_event_id="quasit",
            defender_event_id="hero",
            actual_event_id="hero",
            turn_key="1:quasit",
            bonus_damage=None,
            affected_states=None,
            sneak_attack_ally_available=False,
            brutal_strike_disadvantage=0,
        )
        assert result.save_damage is not None
        assert result.save_damage.save_succeeded is False
        assert any(c.damage_type == "poison" for c in result.damage_components)
        assert "poisoned" in defender.active_effect_ids
        assert "poisoned" in result.applied_conditions
    except Exception:
        logger.exception("Quasit composite failed-save fight verification failed")
        raise


def test_successful_composite_save_applies_neither():
    try:
        source, template, attack = _quasit_attack()
        defender = build_combatant_state(build_demo_fighter())
        dice = FixedDiceProvider([20, 3, 4, 20])  # high save
        result = resolve_attack_effects(
            build_combatant_state(template),
            defender,
            attack,
            dice,
            hit=True,
            critical=False,
            mode=RollMode.NORMAL,
            round_number=1,
            attacker_event_id="quasit",
            defender_event_id="hero",
            actual_event_id="hero",
            turn_key="1:quasit",
            bonus_damage=None,
            affected_states=None,
            sneak_attack_ally_available=False,
            brutal_strike_disadvantage=0,
        )
        assert result.save_damage is not None
        assert result.save_damage.save_succeeded is True
        assert not any(c.damage_type == "poison" for c in result.damage_components)
        assert "poisoned" not in defender.active_effect_ids
    except Exception:
        logger.exception("Quasit composite success-save fight verification failed")
        raise
