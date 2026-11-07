"""2014 ordinary Bite -> failed save -> generic Swallowed; same state as grapple."""
from __future__ import annotations

import logging

from app.combat.attacks import resolve_attack
from app.combat.dice import FixedDiceProvider
from app.combat.state import build_combatant_state
from app.combat.swallow_lifecycle import release_invalid_swallowed, source_turn_swallowed_damage
from app.content.capability_compiler import compile_combatant
from app.content.monster_basic_candidates_2014 import basic_blockers_2014
from app.content.monster_definition_adapter_2014 import adapt_basic_monster_2014
from app.content.monster_grapple_swallow_source_2014 import source_grapple_swallow_2014
from app.content.monster_source_2014 import load_monster_source_2014
from app.content.monsters import build_commoner
from app.domain.encounters import EncounterCombatant, EncounterSetup

logger = logging.getLogger(__name__)


def _source():
    try:
        return next(c for c in load_monster_source_2014() if c.id == "purple-worm")
    except Exception:
        logger.exception("2014 Bite-hit Swallow source was not found.")
        raise


def _scene():
    try:
        card = _source()
        template = compile_combatant(adapt_basic_monster_2014(card))
        bite = next(a for a in [template.weapon_attack, *template.alternate_weapon_attacks]
                    if a and a.weapon.name == "Bite")
        attacker = EncounterCombatant(
            combatant_id="source", side="monsters", position_ft=0,
            state=build_combatant_state(template),
        )
        hero = build_commoner().model_copy(update={"max_hp": 200, "armor_class": 5})
        target = EncounterCombatant(
            combatant_id="victim", side="heroes", position_ft=5,
            state=build_combatant_state(hero),
        )
        setup = EncounterSetup(
            heroes=[target], monsters=[attacker], ruleset="2014",
            hero_total_levels=1, monster_total_cr="15",
        )
        return card, template, bite, attacker, target, setup
    except Exception:
        logger.exception("Failed generic Bite-to-Swallow encounter setup.")
        raise


def test_printed_purple_worm_swallow_is_identity_neutral_and_compiles():
    try:
        card = _source()
        original = card.model_dump_json()
        proof = source_grapple_swallow_2014(card)
        assert proof is not None
        assert proof.delivery_mode == "attack_hit" and not proof.requires_existing_grapple
        assert (proof.on_hit_save_ability, proof.on_hit_save_dc) == ("dexterity", 19)
        assert (proof.max_target_size.value, proof.damage_dice_count, proof.damage_dice_size) == (
            "large", 6, 6,
        )
        assert (proof.regurgitation_damage_threshold, proof.regurgitation_save_dc,
                proof.exit_movement_ft) == (30, 21, 20)
        renamed = card.model_copy(update={
            "name": "Unknown Burrower", "id": "unrelated-homebrew",
        })
        assert source_grapple_swallow_2014(renamed) == proof
        assert basic_blockers_2014(card) == ()
        _, template, bite, *_ = _scene()
        assert bite.weapon.name == "Bite"
        assert any(s.delivery_mode == "attack_hit"
                   and not s.requires_existing_grapple
                   and s.on_hit_save_dc == 19 for s in template.swallow_actions)
        assert card.model_dump_json() == original
    except Exception:
        logger.exception("Purple Worm initial-save Swallow source proof failed.")
        raise


def test_swallow_source_mutations_fail_closed():
    try:
        card = _source()
        for old, new in (
            ("DC 19 Dexterity saving throw", "DC 20 Dexterity saving throw"),
            ("Large or smaller creature", "Huge or smaller creature"),
            ("6d6) acid damage", "8d6) acid damage"),
            ("regurgitate all swallowed creatures", "regurgitate one creature"),
        ):
            altered = card.model_copy(update={
                "source_actions": card.source_actions.replace(old, new),
            })
            assert altered.source_actions != card.source_actions
            assert source_grapple_swallow_2014(altered) is None
        raw = card.swallow_actions[0]
        corrupted = card.model_copy(update={
            "swallow_actions": [{**raw, "requires_existing_grapple": True}],
        })
        assert source_grapple_swallow_2014(corrupted) is None
    except Exception:
        logger.exception("Purple Worm Swallow mutation guard failed.")
        raise


def test_real_bite_hit_dex_save_then_canonical_swallow_turn_and_death_release():
    try:
        _, template, bite, attacker, target, setup = _scene()
        event = resolve_attack(
            1, 1, attacker.state, target.state, bite, 5,
            FixedDiceProvider([19, 5, 5, 5, 1]),
            actor_event_id="source", target_event_id="victim", reaction_setup=setup,
            reaction_roller=attacker,
        )
        assert event.hit is True and event.save_ability == "dexterity"
        assert event.save_dc == 19 and event.save_succeeded is False
        assert target.state.swallowed is not None
        assert target.state.swallowed.source_id == "source"
        assert {"blinded", "restrained"} <= set(target.state.active_effect_ids)
        assert {"blinded", "restrained"} <= set(event.applied_condition_ids)
        before = target.state.current_hp
        ticks, next_seq = source_turn_swallowed_damage(
            2, 2, attacker, setup, FixedDiceProvider([2, 2, 2, 2, 2, 2]),
        )
        assert next_seq == 3 and len(ticks) == 1
        assert target.state.current_hp == before - 12
        attacker.state.is_alive = False
        attacker.state.is_dead = True
        attacker.state.current_hp = 0
        assert "victim" in release_invalid_swallowed(setup)
        assert target.state.swallowed is None
        assert "prone" in target.state.active_effect_ids
        assert build_combatant_state(template).swallowed_target_ids == []
    except Exception:
        logger.exception("Actual 2014 Bite-hit-to-Swallow turn lifecycle failed.")
        raise


def test_successful_save_and_oversized_creature_are_not_swallowed():
    try:
        _, _, bite, attacker, target, setup = _scene()
        event = resolve_attack(
            1, 1, attacker.state, target.state, bite, 5,
            FixedDiceProvider([19, 5, 5, 5, 20]),
            actor_event_id="source", target_event_id="victim", reaction_setup=setup,
            reaction_roller=attacker,
        )
        assert event.hit and event.save_succeeded is True
        assert target.state.swallowed is None
        # On another encounter, a too-large creature takes Bite damage but
        # never rolls the conditional Swallow saving throw.
        from app.domain.size import CreatureSize
        _, template, bite, attacker, target, setup = _scene()
        target.state.template.size = CreatureSize.HUGE
        event = resolve_attack(
            1, 1, attacker.state, target.state, bite, 5,
            FixedDiceProvider([19, 5, 5, 5]),
            actor_event_id="source", target_event_id="victim", reaction_setup=setup,
            reaction_roller=attacker,
        )
        assert event.hit and event.saving_throw_roll is None
        assert target.state.swallowed is None
    except Exception:
        logger.exception("Generic on-hit Swallow success/size exclusions failed.")
        raise
