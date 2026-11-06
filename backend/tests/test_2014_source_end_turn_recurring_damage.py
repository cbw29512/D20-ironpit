"""2014 end-of-turn typed recurring damage, source proof and fight state."""
from __future__ import annotations

import logging
from types import SimpleNamespace

from app.combat.attacks import resolve_attack
from app.combat.dice import FixedDiceProvider
from app.combat.end_of_turn_recurring_damage import resolve_end_turn_recurring_damage
from app.combat.on_hit_recurring_damage import apply_on_hit_recurring_damage
from app.combat.state import build_combatant_state
from app.combat.timed_condition_lifecycle import remove_effect_instance
from app.content.capability_compiler import compile_combatant
from app.content.demo import build_demo_fighter
from app.content.monster_basic_candidates_2014 import basic_blockers_2014
from app.content.monster_definition_adapter_2014 import adapt_monster_mechanics_2014
from app.content.monster_source_2014 import load_monster_source_2014
from app.content.monster_source_end_turn_recurring_2014 import (
    source_end_turn_recurring_damage_2014,
)
from app.domain.encounters import EncounterCombatant
from scripts.browser_template_serializer import template_row

logger = logging.getLogger(__name__)


def magmin_source():
    try:
        return next(card for card in load_monster_source_2014() if card.id == "magmin")
    except Exception:
        logger.exception("2014 recurring-damage source fixture missing.")
        raise


def magmin_attack():
    try:
        card = magmin_source()
        template = compile_combatant(adapt_monster_mechanics_2014(card))
        choices = [template.weapon_attack, *template.alternate_weapon_attacks]
        action = next(
            attack for attack in choices
            if attack is not None and attack.weapon.name == "Touch"
        )
        return card, template, action
    except Exception:
        logger.exception("2014 Magmin Touch failed generic attack compilation.")
        raise


def test_327_card_source_proof_renames_and_unknown_clauses() -> None:
    try:
        rows = load_monster_source_2014()
        assert len(rows) == 327
        found = [
            (card.id, attack.name)
            for card in rows for attack in card.attacks
            if source_end_turn_recurring_damage_2014(card, attack) is not None
        ]
        assert found == [("magmin", "Touch")]
        card = magmin_source()
        source_attack = next(a for a in card.attacks if a.name == "Touch")
        original = card.model_dump_json()
        proof = source_end_turn_recurring_damage_2014(card, source_attack)
        assert proof is not None
        assert (proof.dice_count, proof.dice_size, proof.damage_type.value) == (
            1, 6, "fire",
        )
        renamed = card.model_copy(update={
            "id": "homebrew-elemental", "name": "Unrelated Elemental",
        })
        assert source_end_turn_recurring_damage_2014(renamed, source_attack) == proof
        for before, after in [
            ("at the end of each of its turns", "at the start of each turn"),
            ("1d6", "1d8"),
            ("takes an action to douse the fire", "takes no action to douse the fire"),
        ]:
            assert before in card.source_actions
            modified = card.model_copy(update={
                "source_actions": card.source_actions.replace(before, after),
            })
            assert source_end_turn_recurring_damage_2014(modified, source_attack) is None
        # The source lacks another-creature douse range. Do not falsely admit.
        assert "attack:incomplete" in basic_blockers_2014(card)
        assert card.model_dump_json() == original
    except Exception:
        logger.exception("2014 end-turn source scan or fail-closed test failed.")
        raise


def test_generic_magmin_attack_compiles_and_exports_typed_tick() -> None:
    try:
        card, template, attack = magmin_attack()
        assert attack.on_hit_recurring_damage is not None
        proof = attack.on_hit_recurring_damage
        assert proof.effect_id == "burning"
        assert proof.tick_timing == "target_turn_end"
        assert proof.stacking == "nonstacking"
        assert not proof.ends_if_source_dead
        row = template_row(template)
        attack_row = next(item for item in row["attacks"] if item["name"] == "Touch")
        assert attack_row["onHitRecurringDamage"] == {
            "effectId": "burning", "diceCount": 1, "diceSize": 6,
            "damageType": "fire", "tickTiming": "target_turn_end",
            "stacking": "nonstacking", "endsIfSourceDead": False,
        }
        assert card.source_actions == magmin_source().source_actions
    except Exception:
        logger.exception("2014 recurring-damage template serialization failed.")
        raise


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
