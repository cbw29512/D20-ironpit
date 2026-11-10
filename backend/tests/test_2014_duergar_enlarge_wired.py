"""Duergar's exact 2014 source is composed from universal buff and weapon rules."""
from __future__ import annotations

import logging

from app.combat.ability_checks import ability_check_roll_mode
from app.combat.damage import resolve_weapon_damage
from app.combat.dice import FixedDiceProvider
from app.combat.saving_throw_rolls import resolve_saving_throw
from app.combat.state import build_combatant_state
from app.combat.timed_condition_lifecycle import remove_effect_group
from app.combat.timed_self_buffs import resolve_timed_self_buff
from app.content.capability_compiler import compile_combatant
from app.content.monster_basic_candidates_2014 import basic_blockers_2014
from app.content.monster_definition_adapter_2014 import adapt_basic_monster_2014
from app.content.monster_source_2014 import load_monster_source_2014
from app.content.monster_source_enlarge_2014 import (
    source_enlarge_action_2014, source_enlarge_ranged_weapon_2014,
    source_enlarge_weapon_2014,
)
from app.domain.encounters import EncounterCombatant
from app.domain.models import RollMode
from app.domain.size import CreatureSize
from scripts.browser_template_serializer import template_row

logger = logging.getLogger(__name__)


def _source():
    try:
        return next(card for card in load_monster_source_2014() if card.id == "duergar")
    except Exception:
        logger.exception("Pinned 2014 Duergar was not found")
        raise


def _build():
    template = compile_combatant(adapt_basic_monster_2014(_source()))
    state = build_combatant_state(template)
    actor = EncounterCombatant(
        combatant_id="duergar-1", side="monsters", position_ft=0, state=state,
    )
    return template, state, actor


def test_exact_source_admits_full_monster_and_both_weapon_modes():
    try:
        original = _source()
        before = original.model_dump_json()
        assert source_enlarge_action_2014(original)[0].duration_rounds == 10
        assert source_enlarge_ranged_weapon_2014(original, original.attacks[1])
        assert not basic_blockers_2014(original)
        template, _, _ = _build()
        attacks = [template.weapon_attack, *template.alternate_weapon_attacks]
        assert [(a.id, a.weapon.attack_kind.value) for a in attacks] == [
            ("2014-duergar-war-pick", "melee"),
            ("2014-duergar-javelin", "melee"),
            ("2014-duergar-javelin-ranged", "ranged"),
        ]
        assert all(
            len(a.conditional_damage) == 1
            and a.conditional_damage[0].required_effect_id == "enlarge"
            for a in attacks
        )
        assert attacks[2].weapon.normal_range_ft == 30
        assert attacks[2].weapon.long_range_ft == 120
        assert {r.id for r in template.resources} == {"enlarge", "invisibility"}
        row = template_row(template)
        assert len(row["attacks"]) == 3
        assert any(a["conditionalDamage"]["requiredEffectId"] == "enlarge"
                   for a in row["attacks"])
        assert original.model_dump_json() == before
    except Exception:
        logger.exception("Full 2014 Duergar source/attack admission regression")
        raise


def test_enlarge_buff_doubles_weapon_dice_but_not_fixed_bonus_then_resets():
    try:
        template, state, member = _build()
        attacks = [template.weapon_attack, *template.alternate_weapon_attacks]
        for attack, base, enlarged in zip(attacks, [6, 5, 5], [11, 9, 9]):
            before, _ = resolve_weapon_damage(
                state, attack, FixedDiceProvider([4]), False, RollMode.NORMAL,
            )
            assert before.notation == f"1d{8 if base == 6 else 6}+2"
        action = next(a for a in template.timed_self_buff_actions if a.id == "enlarge")
        event = resolve_timed_self_buff(
            1, 1, member, action, spend_action_cost=False,
        )
        assert event.feature_id == "enlarge"
        assert state.template.size == CreatureSize.LARGE
        assert template.size == CreatureSize.MEDIUM
        assert "enlarge" in state.active_effect_ids
        assert ability_check_roll_mode(state, ability="strength") == RollMode.ADVANTAGE
        assert ability_check_roll_mode(state, ability="dexterity") == RollMode.NORMAL
        save, _ = resolve_saving_throw(
            state, "strength", 99, FixedDiceProvider([4, 15]),
        )
        assert save.mode == "advantage" and save.rolls == [4, 15]
        for attack, die in zip(attacks, [8, 6, 6]):
            result, parts = resolve_weapon_damage(
                state, attack, FixedDiceProvider([3, 5]), False, RollMode.NORMAL,
            )
            assert result.notation == f"2d{die}+2"
            assert result.total == 10
            assert len(parts) == 1
        critical, parts = resolve_weapon_damage(
            state, attacks[0], FixedDiceProvider([1, 2, 3, 4]),
            True, RollMode.NORMAL,
        )
        assert critical.notation == "4d8+2"
        assert critical.total == 12
        effect = next(e for e in state.timed_effects if e.source_effect_id == "enlarge")
        assert remove_effect_group(state, effect) == ["enlarge"]
        assert state.template.size == CreatureSize.MEDIUM
        assert ability_check_roll_mode(state, ability="strength") == RollMode.NORMAL
        restored, _ = resolve_weapon_damage(
            state, attacks[0], FixedDiceProvider([5]), False, RollMode.NORMAL,
        )
        assert restored.notation == "1d8+2"
    except Exception:
        logger.exception("2014 Duergar printed Enlarge lifecycle/dice failed")
        raise


def test_unverified_rewritten_action_or_weapon_never_gets_admitted():
    try:
        original = _source()
        rewritten = original.model_copy(update={
            "source_actions": original.source_actions.replace("For 1 minute", "For 2 minutes"),
        })
        assert source_enlarge_action_2014(rewritten) == []
        assert "source:extra-action" in basic_blockers_2014(rewritten)
        weapon_edit = original.model_copy(update={
            "source_actions": original.source_actions.replace(
                "11 (2d8 + 2)", "20 (4d8 + 2)",
            ),
        })
        assert not source_enlarge_weapon_2014(
            weapon_edit, weapon_edit.attacks[0],
        ).source_complete
        assert "attack:incomplete" in basic_blockers_2014(weapon_edit)
        rename = original.model_copy(update={"id": "another-card", "name": "Other"})
        assert source_enlarge_action_2014(rename) == source_enlarge_action_2014(original)
    except Exception:
        logger.exception("2014 source proof mutation or identity regression")
        raise
