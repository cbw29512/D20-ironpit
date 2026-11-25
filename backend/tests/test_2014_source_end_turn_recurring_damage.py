"""2014 end-of-turn typed recurring damage, source proof and fight state."""
from __future__ import annotations

import logging

from app.content.capability_compiler import compile_combatant
from app.content.monster_basic_candidates_2014 import basic_blockers_2014
from app.content.monster_definition_adapter_2014 import adapt_monster_mechanics_2014
from app.content.monster_source_2014 import load_monster_source_2014
from app.content.monster_source_end_turn_recurring_2014 import (
    source_end_turn_recurring_damage_2014,
    source_completed_end_turn_ignition_attack_2014,
)
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
        # Locked no-douse AI removes irrelevant helper-range requirement.
        completed = source_completed_end_turn_ignition_attack_2014(card, source_attack)
        assert completed.source_complete
        assert "attack:incomplete" not in basic_blockers_2014(card)
        assert basic_blockers_2014(card) == ()
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
        assert proof.removal_action_ids == ["douse-fire"]
        row = template_row(template)
        attack_row = next(item for item in row["attacks"] if item["name"] == "Touch")
        assert attack_row["onHitRecurringDamage"] == {
            "effectId": "burning", "diceCount": 1, "diceSize": 6,
            "damageType": "fire", "tickTiming": "target_turn_end",
            "stacking": "nonstacking", "endsIfSourceDead": False,
            "removalActionIds": ["douse-fire"],
        }
        assert "attack:incomplete" not in basic_blockers_2014(card)
        assert card.source_actions == magmin_source().source_actions
    except Exception:
        logger.exception("2014 recurring-damage template serialization failed.")
        raise

