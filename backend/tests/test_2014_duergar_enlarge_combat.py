"""Duergar Enlarge source-neutral fight-state / dice integration regression."""
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
from app.domain.encounters import EncounterCombatant
from app.domain.saving_throw_context import SavingThrowContext
from app.domain.size import CreatureSize
from app.domain.models import RollMode
logger = logging.getLogger(__name__)

def _state():
    try:
        card = next(c for c in load_monster_source_2014() if c.id == "duergar")
        template = compile_combatant(adapt_monster_mechanics_2014(card))
        state = build_combatant_state(template)
        actor = EncounterCombatant(
            combatant_id="source-1", side="monsters", position_ft=0, state=state,
        )
        return state, actor
    except Exception:
        logger.exception("Could not compile universal Duergar encounter state")
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


