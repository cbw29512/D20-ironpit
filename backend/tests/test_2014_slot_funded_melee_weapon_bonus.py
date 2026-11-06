"""Priest source proof and generic slot-funded melee weapon bonus regressions."""
from __future__ import annotations

import logging

from app.combat.modifier_stack import add_modifier, bonus_damage_modifiers
from app.combat.spell_modifiers import build_spell_modifier
from app.combat.state import build_combatant_state
from app.combat.timed_self_buffs import resolve_timed_self_buff
from app.content.capability_compiler import compile_combatant
from app.content.demo import build_demo_fighter
from app.content.monster_definition_adapter_2014 import adapt_monster_mechanics_2014
from app.content.monster_slot_melee_weapon_bonus_2014 import (
    slot_melee_weapon_bonus_actions_2014,
)
from app.content.monster_source_2014 import load_monster_source_2014
from app.content.monster_trait_bindings_2014 import bound_trait_names_2014
from app.domain.encounters import EncounterCombatant
from app.domain.weapons import WeaponAttackKind
from scripts.browser_template_serializer import template_row

logger = logging.getLogger(__name__)


def priest():
    try:
        return next(card for card in load_monster_source_2014() if card.id == "priest")
    except Exception:
        logger.exception("2014 Priest source fixture unavailable.")
        raise


def test_complete_327_card_semantic_scan_and_parameters() -> None:
    try:
        cards = load_monster_source_2014()
        assert len(cards) == 327
        matches = [
            card.id for card in cards if slot_melee_weapon_bonus_actions_2014(card)
        ]
        assert matches == ["priest"]
        card = priest()
        actions = slot_melee_weapon_bonus_actions_2014(card)
        assert [a.resource_id for a in actions] == [
            "spell-slot-1", "spell-slot-2", "spell-slot-3",
        ]
        assert [a.modifier_effects[0].dice_count for a in actions] == [3, 4, 5]
        for action in actions:
            assert action.action_cost == "bonus_action"
            assert action.resource_cost == 1
            assert action.duration_rounds == 1
            assert action.expiry_timing == "source_turn_end"
            assert not action.opening_eligible
            assert action.expend_slot_without_cast
            effect, = action.modifier_effects
            assert effect.required_weapon_attack_kind == "melee"
            assert effect.damage_type == "radiant"
        assert "Divine Eminence" in bound_trait_names_2014(card)
        altered = card.model_copy(update={"id": "synthetic-cleric", "name": "Other"})
        assert [a.name for a in slot_melee_weapon_bonus_actions_2014(altered)] == [
            a.name for a in actions
        ]
        source = card.source_traits
        assert isinstance(source, str)
        changed = card.model_copy(update={
            "source_traits": source.replace(
                "melee weapon attacks", "ranged weapon attacks",
            ),
        })
        assert changed.source_traits != source
        assert slot_melee_weapon_bonus_actions_2014(changed) == []
    except Exception:
        logger.exception("2014 slot-funded melee source scan failed.")
        raise


def test_compiled_priest_activation_consumes_one_slot_but_does_not_cast() -> None:
    try:
        template = compile_combatant(adapt_monster_mechanics_2014(priest()))
        row = template_row(template)
        slot = next(a for a in template.timed_self_buff_actions
                    if a.id == "divine-eminence-slot-1")
        exported = next(a for a in row["timed_self_buff_actions"]
                        if a["id"] == slot.id)
        assert exported["expendSlotWithoutCast"] is True
        assert exported["openingEligible"] is False
        assert exported["modifierEffects"][0]["requiredWeaponAttackKind"] == "melee"
        state = build_combatant_state(template)
        member = EncounterCombatant(
            combatant_id="priest", side="monsters", position_ft=0, state=state,
        )
        resources = {resource.id: resource for resource in state.resources}
        before = resources[slot.resource_id].current_uses
        state.spell_slot_expended_turn_key = "1:priest"
        event = resolve_timed_self_buff(
            1, 1, member, slot, turn_key="1:priest", affected_states=[state],
        )
        assert event.feature_id == slot.id
        assert resources[slot.resource_id].current_uses == before - 1
        assert state.spell_slot_expended_turn_key == "1:priest"
        assert state.action_available
        assert not state.bonus_action_available
        assert len(state.active_modifiers) == 1
        assert state.active_modifiers[0].required_weapon_attack_kind == "melee"
    except Exception:
        logger.exception("2014 Priest slot-funded Bonus Action activation failed.")
        raise


def test_generic_melee_weapon_bonus_rejects_ranged_and_spell_damage() -> None:
    try:
        template = build_demo_fighter()
        state = build_combatant_state(template)
        melee = template.weapon_attack
        assert melee is not None
        ranged = melee.model_copy(update={
            "weapon": melee.weapon.model_copy(update={
                "attack_kind": WeaponAttackKind.RANGED,
            }),
        })
        effect = slot_melee_weapon_bonus_actions_2014(priest())[0].modifier_effects[0]
        modifier = build_spell_modifier(
            "source", "source", "slot-funded-radiance", effect, 0,
        )
        add_modifier(state, modifier)
        assert bonus_damage_modifiers(state, None, melee) == [modifier]
        assert bonus_damage_modifiers(state, None, ranged) == []
        # Spell attacks do not have a WeaponAttack argument.
        assert bonus_damage_modifiers(state, None) == []
    except Exception:
        logger.exception("Universal melee-weapon-only damage gating failed.")
        raise
