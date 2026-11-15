"""2014 Shield: source, slots, reaction, AC, immunity and start-turn expiry."""
from __future__ import annotations

import logging
import pytest

from app.combat.hit_modifiers import expire_source_turn_start_modifiers
from app.combat.modifier_stack import effective_armor_class
from app.combat.reaction_defense_spells import (
    active_reaction_defense, reaction_defense_blocks_auto_hit,
    trigger_reaction_defense,
)
from app.combat.state import build_combatant_state
from app.content.demo import build_demo_fighter
from app.content.monster_shield_reaction_2014 import source_shield_reaction_2014
from app.content.monster_source_2014 import load_monster_source_2014
from app.domain.combatants import ResourceDefinition
from app.domain.reaction_defense_spells import ReactionDefenseSpell

logger = logging.getLogger(__name__)
CASTERS = ("Couatl", "Flameskull", "Gynosphinx", "Lich", "Mage")


def _state(slots=1):
    try:
        template = build_demo_fighter().model_copy(update={
            "reaction_defense_spell": ReactionDefenseSpell(
                id="shield", name="Shield", minimum_slot_level=1,
                ac_bonus=5, blocked_auto_hit_spell_ids=["magic-missile"],
            ),
            "resources": [ResourceDefinition(
                id="spell-slot-1", name="Spell Slot 1", max_uses=slots,
            )],
        })
        return build_combatant_state(template)
    except Exception:
        logger.exception("Shield fixture construction failed")
        raise


@pytest.mark.parametrize("name", CASTERS)
def test_printed_shield_source_is_bound_for_all_five_casters(name):
    try:
        card = next(x for x in load_monster_source_2014() if x.name == name)
        original = card.model_dump_json()
        action = source_shield_reaction_2014(card)
        assert action is not None and action.id == "shield"
        assert action.ac_bonus == 5
        assert action.blocked_auto_hit_spell_ids == ["magic-missile"]
        assert card.model_dump_json() == original
    except Exception:
        logger.exception("Shield source proof failed for %s", name)
        raise


@pytest.mark.parametrize("change", ["id", "name", "level", "missing"])
def test_prepared_shield_source_changes_fail_closed(change):
    try:
        card = next(x for x in load_monster_source_2014() if x.name == "Mage")
        source = dict(card.spellcasting)
        spells = [dict(entry) for entry in source["spells"]]
        target = next(row for row in spells if row["id"] == "shield")
        if change == "id":
            target["id"] = "shield-x"
        elif change == "name":
            target["name"] = "shield plus"
        elif change == "level":
            target["level"] = 9
        else:
            spells.remove(target)
        source["spells"] = spells
        changed = card.model_copy(update={"spellcasting": source})
        assert source_shield_reaction_2014(changed) is None
    except Exception:
        logger.exception("Changed prepared Shield source unexpectedly accepted")
        raise


def test_shield_stops_hit_and_expires_at_source_next_turn():
    try:
        state = _state()
        initial_ac = effective_armor_class(state)
        assert trigger_reaction_defense(
            state, incoming_attack_total=initial_ac + 3,
            natural_roll=12, source_id="monster-1",
        )
        assert effective_armor_class(state) == initial_ac + 5
        assert state.reaction_available is False
        assert state.resources[0].current_uses == 0
        assert active_reaction_defense(state)
        assert not trigger_reaction_defense(
            state, incoming_attack_total=initial_ac + 3, natural_roll=12,
        )
        assert expire_source_turn_start_modifiers([state], "monster-1") == 1
        assert effective_armor_class(state) == initial_ac
    except Exception:
        logger.exception("Shield timing and armor class failed")
        raise


@pytest.mark.parametrize("total_offset,natural", [(-1, 12), (5, 12), (2, 20)])
def test_shield_does_not_spend_reaction_when_unhelpful(total_offset, natural):
    try:
        state = _state()
        assert not trigger_reaction_defense(
            state, incoming_attack_total=effective_armor_class(state) + total_offset,
            natural_roll=natural, source_id="defender",
        )
        assert state.reaction_available and state.resources[0].current_uses == 1
    except Exception:
        logger.exception("Shield unhelpful attack should not spend resources")
        raise


def test_shield_blocks_magic_missile_but_not_other_auto_hit_spells():
    try:
        state = _state()
        assert not reaction_defense_blocks_auto_hit(state, "different", source_id="target")
        assert reaction_defense_blocks_auto_hit(state, "magic-missile", source_id="target")
        assert active_reaction_defense(state)
        assert state.resources[0].current_uses == 0
        assert reaction_defense_blocks_auto_hit(state, "magic-missile", source_id="target")
        assert not reaction_defense_blocks_auto_hit(state, "different", source_id="target")
    except Exception:
        logger.exception("Shield Magic Missile immunity failed")
        raise


def test_weapon_attack_outcome_triggers_shield_and_logs_reaction_status():
    try:
        from app.combat.attack_d20_outcome import resolve_attack_d20_outcome
        from app.content.demo import build_goblin_warrior
        from app.domain.event_support import DiceRoll

        defender = _state()
        attacker = build_combatant_state(build_goblin_warrior())
        incoming = effective_armor_class(defender) + 2
        roll = DiceRoll(
            notation="1d20", rolls=[12], modifier=incoming - 12,
            selected_roll=12, total=incoming,
        )
        outcome = resolve_attack_d20_outcome(
            attacker, defender, build_goblin_warrior().weapon_attack,
            roll, effective_armor_class(defender),
        )
        assert not outcome.hit
        assert outcome.reaction_defense_used
        assert outcome.target_ac == effective_armor_class(defender)
        assert defender.resources[0].current_uses == 0
    except Exception:
        logger.exception("Shield weapon D20 outcome integration failed")
        raise
