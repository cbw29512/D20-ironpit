"""Direct Python fight proof for source-declared recurring damage."""
from __future__ import annotations

import logging
from types import SimpleNamespace

from app.combat.attacks import resolve_attack
from app.combat.dice import FixedDiceProvider
from app.combat.end_of_turn_recurring_damage import resolve_end_turn_recurring_damage
from app.combat.on_hit_recurring_damage import apply_on_hit_recurring_damage
from app.combat.state import build_combatant_state
from app.combat.timed_condition_lifecycle import remove_effect_instance
from app.content.demo import build_demo_fighter
from app.domain.encounters import EncounterCombatant
from app.content.capability_compiler import compile_combatant
from app.content.monster_definition_adapter_2014 import adapt_monster_mechanics_2014
from app.content.monster_source_2014 import load_monster_source_2014


def magmin_attack():
    try:
        card = next(m for m in load_monster_source_2014() if m.id == "magmin")
        template = compile_combatant(adapt_monster_mechanics_2014(card))
        return card, template, next(
            attack for attack in [template.weapon_attack, *template.alternate_weapon_attacks]
            if attack is not None and attack.weapon.name == "Touch"
        )
    except Exception:
        logger.exception("Failed to compile Magmin's normal Touch weapon attack.")
        raise

logger = logging.getLogger(__name__)

def test_actual_attack_hit_burns_once_and_end_turn_takes_typed_damage() -> None:
    try:
        _, template, attack = magmin_attack()
        attacker = build_combatant_state(template)
        defender = build_combatant_state(build_demo_fighter())
        before = defender.current_hp
        # The attack uses its ordinary hit and damage rolls before applying
        # a fight-local recurring effect; extra dice cannot manufacture a hit.
        hit = resolve_attack(
            1, 1, attacker, defender, attack, 5,
            FixedDiceProvider([18, *([3] * 12)]),
            affected_states=[attacker, defender],
        )
        assert hit.hit and defender.current_hp < before
        assert len(defender.timed_effects) == 1
        effect = defender.timed_effects[0]
        assert effect.source_name == "Touch"
        assert (effect.end_of_turn_dice_count, effect.end_of_turn_damage_type.value) == (
            1, "fire",
        )
        assert apply_on_hit_recurring_damage(defender, attack, source_id="other") is None
        assert len(defender.timed_effects) == 1
        member = EncounterCombatant(
            combatant_id="defender", side="heroes", position_ft=5, state=defender,
        )
        owner = EncounterCombatant(
            combatant_id="attacker", side="monsters", position_ft=0, state=attacker,
        )
        setup = SimpleNamespace(heroes=[member], monsters=[owner])
        old_hp = defender.current_hp
        events, next_seq = resolve_end_turn_recurring_damage(
            2, 1, member, setup, FixedDiceProvider([4]),
        )
        assert next_seq == 3 and len(events) == 1
        assert defender.current_hp == old_hp - 4
        assert "Touch" in events[0].description
        remove_effect_instance(defender, effect)
        events, _ = resolve_end_turn_recurring_damage(
            3, 2, member, setup, FixedDiceProvider([]),
        )
        assert events == []
    except Exception:
        logger.exception("2014 recurring hit damage / end-turn fight failed.")
        raise


def test_attack_miss_creates_no_recurring_effect() -> None:
    try:
        _, template, attack = magmin_attack()
        actor = build_combatant_state(template)
        defender = build_combatant_state(build_demo_fighter())
        old_hp = defender.current_hp
        event = resolve_attack(
            1, 1, actor, defender, attack, 20, FixedDiceProvider([1]),
            affected_states=[actor, defender],
        )
        assert not event.hit and defender.current_hp == old_hp
        assert not defender.timed_effects
    except Exception:
        logger.exception("Missed weapon hit incorrectly ignited its target.")
        raise
