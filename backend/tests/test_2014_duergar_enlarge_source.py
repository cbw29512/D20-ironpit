"""2014 Duergar source Enlarge reuses shared timed effects, dice and size gates."""
from __future__ import annotations

import logging

from app.combat.ability_checks import ability_check_roll_mode
from app.combat.damage import resolve_weapon_damage
from app.combat.dice import FixedDiceProvider
from app.combat.saving_throw_rolls import resolve_saving_throw
from app.combat.state import build_combatant_state
from app.combat.timed_condition_lifecycle import remove_effect_group
from app.combat.timed_self_buff_facts import effective_creature_size
from app.combat.timed_self_buffs import resolve_timed_self_buff
from app.content.capability_compiler import compile_combatant
from app.content.monster_definition_adapter_2014 import adapt_monster_mechanics_2014
from app.content.monster_source_2014 import load_monster_source_2014
from app.content.monster_source_enlarge_2014 import (
    source_enlarge_actions_2014, source_enlarge_resources_2014,
)
from app.content.monster_source_enlarged_attacks_2014 import (
    source_completed_enlarged_attack_2014,
    source_enlarged_dual_range_attacks_2014,
)
from app.domain.encounters import EncounterCombatant
from app.domain.saving_throw_context import SavingThrowContext
from app.domain.size import CreatureSize
from app.domain.models import RollMode

logger = logging.getLogger(__name__)


def _source():
    try:
        return next(row for row in load_monster_source_2014() if row.id == "duergar")
    except Exception:
        logger.exception("2014 Duergar card missing")
        raise


def _state():
    try:
        template = compile_combatant(adapt_monster_mechanics_2014(_source()))
        state = build_combatant_state(template)
        actor = EncounterCombatant(
            combatant_id="source-1", side="monsters", position_ft=0, state=state,
        )
        return state, actor
    except Exception:
        logger.exception("Failed to compile Duergar's universal fight template")
        raise


def test_pinned_327_source_enlarge_family_is_complete_and_named():
    try:
        cards = load_monster_source_2014()
        assert len(cards) == 327
        assert {m.id for m in cards if source_enlarge_actions_2014(m)} == {"duergar"}
        action, = source_enlarge_actions_2014(_source())
        assert action.name == "Enlarge"
        assert action.resource_id == "enlarge"
        assert action.size_override == CreatureSize.LARGE
        assert action.duration_rounds == 10
        assert action.ability_check_advantage_abilities == ["strength"]
        assert len(action.saving_throw_advantage_grants) == 1
        assert action.saving_throw_advantage_grants[0].abilities == ["strength"]
        assert action.opening_eligible is False
        assert action.concentration is False
        resource, = source_enlarge_resources_2014(_source())
        assert resource.max_uses == 1
    except Exception:
        logger.exception("2014 source Enlarge corpus audit failed")
        raise


def test_source_attack_dice_and_dual_melee_ranged_binding():
    try:
        card = _source()
        assert len(card.attacks) == 2
        for attack in card.attacks:
            assert attack.source_complete is False
            bound = source_completed_enlarged_attack_2014(card, attack)
            assert bound.source_complete is True
            rider, = bound.conditional_damage
            assert rider["trigger"] == "attacker_effect_active"
            assert rider["required_effect_id"] == "enlarge"
            assert rider["mode"] == "replace_weapon"
            assert rider["dice_count"] == 2
            assert rider["dice_size"] == attack.damage.dice_size
            assert rider["damage_bonus"] == 2
            assert rider["damage_type"] == "piercing"
        ranged, = source_enlarged_dual_range_attacks_2014(card)
        assert ranged.id == "javelin-ranged" and ranged.kind == "ranged"
        assert (ranged.normal_range_ft, ranged.long_range_ft) == (30, 120)
        state, _ = _state()
        ids = [
            state.template.weapon_attack.id,
            *[a.id for a in state.template.alternate_weapon_attacks],
        ]
        assert len(ids) == len(set(ids))
        assert "2014-duergar-javelin-ranged" in ids
    except Exception:
        logger.exception("2014 printed enlargement weapon profiles failed")
        raise


def test_active_enlarge_doubles_only_weapon_dice_and_reverts():
    try:
        state, actor = _state()
        attacks = {
            attack.id: attack for attack in [
                state.template.weapon_attack,
                *state.template.alternate_weapon_attacks,
            ]
        }
        war = attacks["2014-duergar-war-pick"]
        javelin = attacks["2014-duergar-javelin-ranged"]
        normal, _ = resolve_weapon_damage(
            state, war, FixedDiceProvider([4]), False, RollMode.NORMAL,
        )
        assert normal.total == 6 and normal.notation.startswith("1d8+2")
        normal_javelin, _ = resolve_weapon_damage(
            state, javelin, FixedDiceProvider([4]), False, RollMode.NORMAL,
        )
        assert normal_javelin.total == 6 and normal_javelin.notation.startswith("1d6+2")
        action = next(a for a in state.template.timed_self_buff_actions if a.id == "enlarge")
        resolve_timed_self_buff(1, 1, actor, action, spend_action_cost=False)
        assert effective_creature_size(state) == CreatureSize.LARGE
        assert "enlarge" in state.active_effect_ids
        assert next(r for r in state.resources if r.id == "enlarge").current_uses == 0
        enlarged, _ = resolve_weapon_damage(
            state, war, FixedDiceProvider([4, 5]), False, RollMode.NORMAL,
        )
        assert enlarged.total == 11 and enlarged.notation.startswith("2d8+2")
        ranged_enlarged, _ = resolve_weapon_damage(
            state, javelin, FixedDiceProvider([4, 5]), False, RollMode.NORMAL,
        )
        assert ranged_enlarged.total == 11 and ranged_enlarged.notation.startswith("2d6+2")
        assert ability_check_roll_mode(state, ability="strength") == RollMode.ADVANTAGE
        assert ability_check_roll_mode(state, ability="dexterity") == RollMode.NORMAL
        save, _ = resolve_saving_throw(
            state, "strength", 99, FixedDiceProvider([3, 17]), SavingThrowContext(),
        )
        assert save.mode == "advantage" and save.rolls == [3, 17]
        group = next(x for x in state.timed_effects if x.source_effect_id == "enlarge")
        remove_effect_group(state, group)
        assert effective_creature_size(state) == CreatureSize.MEDIUM
        assert ability_check_roll_mode(state, ability="strength") == RollMode.NORMAL
        restored, _ = resolve_weapon_damage(
            state, war, FixedDiceProvider([4]), False, RollMode.NORMAL,
        )
        assert restored.total == 6
    except Exception:
        logger.exception("Compiled Duergar Enlarge dice/Strength/expiry regression failed")
        raise


def test_enlarge_source_changes_fail_closed_and_identity_is_irrelevant():
    try:
        source = _source()
        old = source.model_dump_json()
        renamed = source.model_copy(update={"id": "other", "name": "Other"})
        assert source_enlarge_actions_2014(renamed) == source_enlarge_actions_2014(source)
        changed = source.source_actions.replace(
            "Strength checks and Strength saving throws",
            "Strength saving throws",
        )
        assert changed != source.source_actions
        mutated = source.model_copy(update={"source_actions": changed})
        assert source_enlarge_actions_2014(mutated) == []
        assert all(not source_completed_enlarged_attack_2014(mutated, a).source_complete
                   for a in mutated.attacks)
        assert source.model_dump_json() == old
    except Exception:
        logger.exception("Enlarge full-clause source integrity failed")
        raise
