"""Efreeti's source Enlarge is a real universal buff, not an AI exemption."""
from __future__ import annotations

import logging

import pytest

from app.combat.ability_checks import ability_check_roll_mode
from app.combat.modifier_stack import bonus_damage_modifiers
from app.combat.saving_throw_rolls import resolve_saving_throw
from app.combat.dice import FixedDiceProvider
from app.combat.state import build_combatant_state
from app.combat.timed_condition_lifecycle import remove_effect_group
from app.combat.timed_self_buffs import resolve_timed_self_buff
from app.content.capability_compiler import compile_combatant
from app.content.monster_basic_candidates_2014 import basic_blockers_2014
from app.content.monster_definition_adapter_2014 import adapt_monster_mechanics_2014
from app.content.monster_innate_enlarge_2014 import source_proven_innate_enlarge_2014
from app.content.monster_source_2014 import load_monster_source_2014
from app.domain.encounters import EncounterCombatant
from app.domain.models import RollMode
from app.domain.size import CreatureSize
from scripts.browser_template_serializer import template_row

logger = logging.getLogger(__name__)


def _source():
    try:
        return next(card for card in load_monster_source_2014()
                    if card.id == "efreeti")
    except Exception:
        logger.exception("2014 Efreeti source was not found.")
        raise


def test_exact_printed_source_weapon_and_327_scan_are_required():
    try:
        cards = load_monster_source_2014()
        assert len(cards) == 327
        assert [row.id for row in cards
                if source_proven_innate_enlarge_2014(row)] == ["efreeti"]
        card = _source()
        before = card.model_dump_json()
        action, = source_proven_innate_enlarge_2014(card)
        assert (action.id, action.name) == ("enlarge-reduce", "Enlarge/Reduce")
        assert action.resource_id == "enlarge-reduce"
        assert action.action_cost == "action"
        assert action.duration_rounds == 10 and action.concentration
        assert action.size_override == CreatureSize.HUGE
        assert action.ability_check_advantage_abilities == ["strength"]
        assert action.saving_throw_advantage_grants[0].abilities == ["strength"]
        effect, = action.modifier_effects
        assert (effect.kind, effect.dice_count, effect.dice_size) == (
            "bonus-damage", 1, 4,
        )
        assert effect.required_weapon_attack_kind == "melee"
        assert effect.damage_type == "slashing"
        assert action.opening_eligible

        renamed = card.model_copy(update={
            "name": "Unrelated Caster", "id": "renamed-source",
        })
        assert len(source_proven_innate_enlarge_2014(renamed)) == 1
        assert card.model_dump_json() == before
    except Exception:
        logger.exception("Source-proven Enlarge definition failed.")
        raise


def test_compiled_real_buff_resource_size_strength_and_weapon_only_damage():
    try:
        source = _source()
        before = source.model_dump_json()
        template = compile_combatant(adapt_monster_mechanics_2014(source))
        action, = [x for x in template.timed_self_buff_actions
                   if x.id == "enlarge-reduce"]
        row = template_row(template)
        exported, = [x for x in row["timed_self_buff_actions"]
                     if x["id"] == action.id]
        assert exported["sizeOverride"] == "huge"
        assert exported["concentration"]
        assert exported["modifierEffects"][0]["diceCount"] == 1
        assert exported["modifierEffects"][0]["diceSize"] == 4
        assert exported["modifierEffects"][0]["damageType"] == "slashing"
        assert exported["modifierEffects"][0]["requiredWeaponAttackKind"] == "melee"

        state = build_combatant_state(template)
        member = EncounterCombatant(
            combatant_id="new-caster", side="monsters", position_ft=0,
            state=state,
        )
        resource = next(x for x in state.resources if x.id == action.resource_id)
        assert resource.current_uses == 3
        assert ability_check_roll_mode(state, ability="strength") == RollMode.NORMAL
        event = resolve_timed_self_buff(
            1, 1, member, action, spend_action_cost=False,
        )
        assert event.feature_id == "enlarge-reduce"
        assert resource.current_uses == 2
        assert state.template.size == CreatureSize.HUGE
        assert template.size == CreatureSize.LARGE
        assert state.concentration is not None
        assert ability_check_roll_mode(state, ability="strength") == RollMode.ADVANTAGE
        saving, _ = resolve_saving_throw(
            state, "strength", 99, FixedDiceProvider([4, 15]),
        )
        assert saving.mode == "advantage"
        melee = template.weapon_attack
        assert melee is not None and melee.weapon.attack_kind.value == "melee"
        matching = bonus_damage_modifiers(state, None, melee)
        assert len(matching) == 1
        assert matching[0].dice_count == 1 and matching[0].dice_size == 4
        assert bonus_damage_modifiers(state, None) == []

        effect = next(x for x in state.timed_effects
                      if x.source_effect_id == action.id)
        assert remove_effect_group(state, effect) == ["enlarge-reduce"]
        assert state.template.size == CreatureSize.LARGE
        assert ability_check_roll_mode(state, ability="strength") == RollMode.NORMAL
        assert bonus_damage_modifiers(state, None, melee) == []
        assert source.model_dump_json() == before
    except Exception:
        logger.exception("2014 Enlarge activation, modifier or expiry failed.")
        raise


@pytest.mark.parametrize("changes", [
    {"source_traits": ("At will: detect magic", "At will: detect magic, fly")},
    {"source_traits": ("3/day: enlarge/reduce", "2/day: enlarge/reduce")},
    {"source_actions": ("2d6 + 6", "2d8 + 6")},
    {"size": ("Large", "Gargantuan")},
])
def test_mutations_fail_closed(changes):
    try:
        card = _source()
        updated = {}
        for key, (old, new) in changes.items():
            value = getattr(card, key)
            assert old in value
            updated[key] = value.replace(old, new)
        altered = card.model_copy(update=updated)
        assert source_proven_innate_enlarge_2014(altered) == []
    except Exception:
        logger.exception("Source mutation unexpectedly kept Enlarge available.")
        raise


def test_other_spells_still_block_entire_efreeti_admission():
    try:
        card = _source()
        assert "mechanic:spellcasting" in basic_blockers_2014(card)
        # No fabricated Major Image spell effects or premature roster admission.
        assert "major-image" in {
            x["id"] for x in card.innate_spellcasting["spells"]
        }
    except Exception:
        logger.exception("Efreeti admission was incorrectly forced.")
        raise
