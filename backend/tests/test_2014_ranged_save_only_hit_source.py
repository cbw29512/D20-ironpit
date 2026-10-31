"""327-card source proof and shared attack/save serialization for ranged hits."""
from __future__ import annotations

import logging

from app.combat.attacks import resolve_attack
from app.combat.dice import FixedDiceProvider
from app.combat.state import build_combatant_state
from app.content.capability_compiler import compile_combatant
from app.content.demo import build_demo_fighter
from app.content.monster_basic_candidates_2014 import basic_blockers_2014
from app.content.monster_definition_adapter_2014 import adapt_monster_mechanics_2014
from app.content.monster_source_2014 import load_monster_source_2014
from app.content.monster_source_ranged_save_only_hit_2014 import (
    source_ranged_save_only_hit_attacks_2014,
)
from scripts.browser_template_serializer import template_row

logger = logging.getLogger(__name__)


def test_complete_source_grammar_scans_all_327_2014_cards() -> None:
    try:
        cards = load_monster_source_2014()
        assert len(cards) == 327
        found = [
            (card, attack)
            for card in cards
            for attack in source_ranged_save_only_hit_attacks_2014(card)
        ]
        assert [(card.id, attack.name) for card, attack in found] == [
            ("guardian-naga", "Spit Poison"),
        ]
        card, action = found[0]
        assert action.fixed_damage == 0
        assert action.damage is None
        assert action.attack_bonus == 8
        assert (action.normal_range_ft, action.long_range_ft) == (15, 30)
        effect = action.effects[0]
        assert (effect.dc, effect.save_ability) == (15, "constitution")
        assert (effect.dice.count, effect.dice.size) == (10, 8)
        assert effect.damage_type.value == "poison" and effect.success_damage == "half"
        assert "source:extra-action" not in basic_blockers_2014(card)
        assert "mechanic:spellcasting" in basic_blockers_2014(card)
    except Exception:
        logger.exception("Ranged save-only source scan failed.")
        raise


def test_genuine_card_compiles_to_generic_zero_base_damage_attack() -> None:
    try:
        card = next(x for x in load_monster_source_2014() if x.id == "guardian-naga")
        snapshot = card.model_dump_json()
        template = compile_combatant(adapt_monster_mechanics_2014(card))
        extra = next(x for x in template.alternate_weapon_attacks
                     if x.weapon.name == "Spit Poison")
        assert extra.fixed_damage == 0 and extra.weapon.dice_count == 0
        assert extra.on_hit_save_damage is not None
        assert extra.on_hit_save_damage.dc == 15
        row = template_row(template)
        attack = next(x for x in row["attacks"] if x["name"] == "Spit Poison")
        assert attack["fixedDamage"] == 0
        assert attack["onHitSaveDamage"]["dc"] == 15
        assert attack["onHitSaveDamage"]["damageType"] == "poison"
        # The printed Naga card is never changed to force browser binding.
        assert card.model_dump_json() == snapshot
    except Exception:
        logger.exception("Guardian Naga ranged-save source adapter failed.")
        raise


def test_shared_attack_roll_precedes_poison_save_and_target_damage() -> None:
    try:
        card = next(x for x in load_monster_source_2014() if x.id == "guardian-naga")
        template = compile_combatant(adapt_monster_mechanics_2014(card))
        attack = next(x for x in template.alternate_weapon_attacks
                      if x.weapon.name == "Spit Poison")
        actor = build_combatant_state(template)
        target = build_combatant_state(build_demo_fighter())
        before = target.current_hp
        # Hit d20, defender save d20, then 10 poison dice.
        event = resolve_attack(1, 1, actor, target, attack, 15,
                               FixedDiceProvider([15, 1, *([4] * 12)]),
                               affected_states=[actor, target])
        assert event.event_type == "attack" and event.hit
        assert target.current_hp < before
        assert actor.action_available is False
    except Exception:
        logger.exception("Shared ranged on-hit-save combat regression failed.")
        raise


def test_unknown_rider_and_source_identity_changes_fail_closed() -> None:
    try:
        card = next(x for x in load_monster_source_2014() if x.id == "guardian-naga")
        for before, after in [
            ("half as much damage on a successful one.", "no damage on success."),
            ("Ranged Weapon Attack", "Ranged Spell Attack"),
            ("45 (10d8) poison", "45 (10d8) poison and blinded"),
        ]:
            changed = card.model_copy(update={
                "source_actions": card.source_actions.replace(before, after),
            })
            assert changed.source_actions != card.source_actions
            assert source_ranged_save_only_hit_attacks_2014(changed) == []
        # Changing valid source parameters changes the bound data, not runtime code.
        changed_type = card.model_copy(update={"source_actions":
            card.source_actions.replace(
                "45 (10d8) poison damage on a failed save",
                "45 (10d8) psychic damage on a failed save",
            )
        })
        bound = source_ranged_save_only_hit_attacks_2014(changed_type)
        assert len(bound) == 1
        assert bound[0].effects[0].damage_type.value == "psychic"
        renamed = card.model_copy(update={"id": "homebrew-naga", "name": "Other"})
        assert source_ranged_save_only_hit_attacks_2014(renamed)
    except Exception:
        logger.exception("Ranged save-only source fail-closed regression failed.")
        raise
