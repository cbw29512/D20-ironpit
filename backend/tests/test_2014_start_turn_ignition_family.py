"""2014 on-hit start-of-target-turn fire: source proof and universal fight parity."""
from __future__ import annotations

import logging

from app.combat.attacks import resolve_attack
from app.combat.dice import FixedDiceProvider
from app.combat.douse_burning import choose_douse_target, resolve_douse_action
from app.combat.end_of_turn_recurring_damage import resolve_end_turn_recurring_damage
from app.combat.start_of_turn_save_condition_events import (
    resolve_start_of_turn_save_condition_damage_events,
)
from app.combat.state import build_combatant_state
from app.content.capability_compiler import compile_combatant
from app.content.demo import build_demo_fighter
from app.content.monster_basic_candidates_2014 import basic_blockers_2014
from app.content.monster_definition_adapter_2014 import adapt_monster_mechanics_2014
from app.content.monster_source_2014 import load_monster_source_2014
from app.content.monster_source_start_turn_recurring_2014 import (
    source_start_turn_recurring_damage_2014,
)
from app.domain.encounters import EncounterCombatant, EncounterSetup
import sys
from pathlib import Path

_scripts = Path(__file__).resolve().parents[2] / "scripts"
if str(_scripts) not in sys.path:
    sys.path.insert(0, str(_scripts))
from browser_template_serializer import template_row

logger = logging.getLogger(__name__)


def _source():
    try:
        return next(card for card in load_monster_source_2014() if card.id == "fire-elemental")
    except Exception:
        logger.exception("Pinned 2014 start-turn burn source is unavailable.")
        raise


def _combat():
    try:
        card = _source()
        template = compile_combatant(adapt_monster_mechanics_2014(card))
        attack = next(a for a in [template.weapon_attack, *template.alternate_weapon_attacks]
                      if a is not None and a.weapon.name == "Touch")
        fire = EncounterCombatant(
            combatant_id="fire-source", side="monsters", position_ft=0,
            state=build_combatant_state(template),
        )
        target_template = build_demo_fighter().model_copy(update={"max_hp": 100})
        hero = EncounterCombatant(
            combatant_id="hero-target", side="heroes", position_ft=5,
            state=build_combatant_state(target_template),
        )
        scene = EncounterSetup(
            heroes=[hero], monsters=[fire], ruleset="2014",
            hero_total_levels=2, monster_total_cr="5",
        )
        return card, template, attack, fire, hero, scene
    except Exception:
        logger.exception("Start-turn source monster combat setup failed.")
        raise


def test_full_source_proof_compiles_generic_attack_and_keeps_other_blockers():
    try:
        cards = load_monster_source_2014()
        found = [
            (card.id, row.name) for card in cards for row in card.attacks
            if source_start_turn_recurring_damage_2014(card, row) is not None
        ]
        assert found == [("fire-elemental", "Touch")]
        card, template, attack, *_ = _combat()
        original = card.model_dump_json()
        source_attack = next(a for a in card.attacks if a.name == "Touch")
        proof = source_start_turn_recurring_damage_2014(card, source_attack)
        assert proof and proof.effect_id == "burning"
        assert (proof.dice_count, proof.dice_size, proof.damage_type.value) == (1, 10, "fire")
        assert proof.tick_timing == "target_turn_start"
        assert proof.removal_action_ids == ["douse-fire"] and not proof.ends_if_source_dead
        assert attack.on_hit_recurring_damage == proof
        row = template_row(template)
        printed = next(x for x in row["attacks"] if x["name"] == "Touch")
        assert printed["onHitRecurringDamage"] == {
            "effectId": "burning", "diceCount": 1, "diceSize": 10,
            "damageType": "fire", "tickTiming": "target_turn_start",
            "stacking": "nonstacking", "endsIfSourceDead": False,
            "removalActionIds": ["douse-fire"],
        }
        # Source is still *not* admitted: compound Fire Form and water exposure
        # remain independently unimplemented, as does unspecified helper dousing.
        assert "source:trait" in basic_blockers_2014(card)
        assert card.model_dump_json() == original
    except Exception:
        logger.exception("2014 Fire Elemental Touch source and serializer parity failed.")
        raise


def test_start_turn_source_proof_is_identity_neutral_and_mutation_safe():
    try:
        card = _source()
        attack = next(a for a in card.attacks if a.id == "touch")
        assert source_start_turn_recurring_damage_2014(
            card.model_copy(update={"id": "renamed-form", "name": "Renamed Form"}), attack,
        )
        for before, after in (
            ("at the start of each of its turns", "at the end of each of its turns"),
            ("5 (1d10) fire damage", "5 (1d8) fire damage"),
            ("action to douse the fire", "free action to douse the fire"),
            ("If the target is a creature", "If the target is a metal object"),
            ("2d6 + 3", "2d6 + 4"),
        ):
            changed = card.model_copy(update={
                "source_actions": card.source_actions.replace(before, after),
            })
            assert changed.source_actions != card.source_actions
            assert source_start_turn_recurring_damage_2014(changed, attack) is None
        bad_data = attack.model_copy(update={
            "ongoing_damage_effect": {
                **attack.ongoing_damage_effect, "dice_size": 6,
            },
        })
        assert source_start_turn_recurring_damage_2014(card, bad_data) is None
    except Exception:
        logger.exception("Start-turn recurring source mutation guard failed.")
        raise


def test_hit_start_turn_tick_typed_damage_self_douse_and_fight_reset():
    try:
        _, template, attack, fire, hero, scene = _combat()
        hit = resolve_attack(
            1, 1, fire.state, hero.state, attack, 5,
            FixedDiceProvider([18, 3, 4]),
            actor_event_id=fire.combatant_id, target_event_id=hero.combatant_id,
        )
        assert hit.hit is True
        effects = [x for x in hero.state.timed_effects if x.effect_id == "burning"]
        assert len(effects) == 1
        effect = effects[0]
        assert (effect.start_of_turn_dice_count, effect.start_of_turn_dice_size,
                effect.start_of_turn_damage_type.value) == (1, 10, "fire")
        assert effect.end_of_turn_dice_count == 0
        assert effect.source_name == "Touch"
        before = hero.state.current_hp
        end, _ = resolve_end_turn_recurring_damage(2, 1, hero, scene, FixedDiceProvider([7]))
        assert end == [] and hero.state.current_hp == before
        # The printed effect persists if the hit's owner dies.
        fire.state.current_hp = 0
        fire.state.is_alive = False
        fire.state.is_dead = True
        started, _ = resolve_start_of_turn_save_condition_damage_events(
            3, 2, hero, scene, FixedDiceProvider([7]),
        )
        assert any("fire damage" in x.description and "start of the turn" in x.description for x in started)
        assert hero.state.current_hp == before - 7
        assert choose_douse_target(hero, scene) is hero
        action = resolve_douse_action(4, 2, hero, hero)
        assert "burning" in action.removed_condition_ids
        assert not hero.state.action_available
        assert not [x for x in hero.state.timed_effects if x.effect_id == "burning"]
        repeated, _ = resolve_start_of_turn_save_condition_damage_events(
            5, 3, hero, scene, FixedDiceProvider([9]),
        )
        assert not any("burning" in x.feature_id for x in repeated)
        assert hero.state.current_hp == before - 7
        assert build_combatant_state(template).timed_effects == []
    except Exception:
        logger.exception("Live Python start-turn burning and douse lifecycle failed.")
        raise
