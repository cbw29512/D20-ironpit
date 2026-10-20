"""Live context drives immunity, existing fear suppression and fresh-fight reset."""
import logging

import pytest

from app.combat.ally_context import has_active_ally, has_visible_active_ally_within
from app.combat.attacks import resolve_attack
from app.combat.condition_immunity import condition_is_immune
from app.combat.condition_rules import has_condition
from app.combat.dice import FixedDiceProvider
from app.combat.grapple import _check_mode
from app.combat.grid_reaction_movement_support import approaches_fear_source
from app.combat.on_hit_contested_movement import _contest_disadvantage
from app.combat.saving_throws import resolve_save_action
from app.combat.state import build_combatant_state
from app.content.capability_compiler import compile_combatant
from app.content.monster_definition_adapter_2014 import adapt_basic_monster_2014
from app.domain.capabilities import CombatantDefinition
from app.domain.grid import GridPosition
from bearded_devil_test_support import setup_with_card, source

logger = logging.getLogger(__name__)


@pytest.mark.parametrize("change,expected", [
    ("boundary", True), ("stunned", False), ("paralyzed", False),
    ("unconscious", False), ("distant", False), ("dead", False),
    ("zero-hp", False), ("invisible", False), ("blind-owner", False),
    ("enemy-only", False), ("self-only", False),
])
def test_live_ally_gate_has_exact_range_sight_and_eligibility(change, expected):
    try:
        owner, ally, foe, setup = setup_with_card()
        before = owner.state.template.model_dump()
        if change in {"stunned", "paralyzed", "unconscious", "invisible"}:
            ally.state.active_effect_ids.append(change)
        elif change == "distant":
            ally.state.position = GridPosition(x=8, y=1)
        elif change == "dead":
            ally.state.is_dead = True
        elif change == "zero-hp":
            ally.state.current_hp = 0
        elif change == "blind-owner":
            owner.state.active_effect_ids.append("blinded")
        elif change == "enemy-only":
            setup.monsters.remove(ally)
        elif change == "self-only":
            setup.monsters.remove(ally)
            setup.heroes.clear()
        assert has_visible_active_ally_within(owner, setup, 30) is expected
        assert condition_is_immune(owner.state, "frightened", actor=owner, setup=setup) is expected
        assert not condition_is_immune(owner.state, "charmed", actor=owner, setup=setup)
        if change in {"stunned", "paralyzed", "unconscious"}:
            assert not has_active_ally(owner, setup), "Pack Tactics still needs a capable ally."
        assert owner.state.template.model_dump() == before
    except Exception:
        logger.exception("Visible-ally live eligibility failed: %s.", change)
        raise


@pytest.mark.parametrize("kind", ["monster", "character"])
def test_renamed_form_prevents_new_fear_and_suppresses_existing_fear_dynamically(kind):
    try:
        payload = adapt_basic_monster_2014(source()).model_dump()
        payload.update(id="crystal-warden", name="Crystal Warden", kind=kind)
        payload["source_trait_names"] = ["Crystal Resolve"]
        grant = payload["passive_modifier_grants"][0]
        grant.update(source_id="crystal-resolve", source_name="Crystal Resolve")
        card = compile_combatant(CombatantDefinition.model_validate(payload))
        before = card.model_dump()
        owner, ally, foe, setup = setup_with_card(card)
        action = next(item for item in foe.state.template.saving_throw_actions if item.id == "frightful-presence")
        blocked = resolve_save_action(1, 1, foe, owner, action, 5, FixedDiceProvider([1]),
                                      spend_action=False, setup=setup)
        assert not blocked.save_succeeded and blocked.applied_condition_ids == []
        assert "frightened" not in owner.state.active_effect_ids
        ally.state.position = GridPosition(x=8, y=1)
        landed = resolve_save_action(2, 1, foe, owner, action, 5, FixedDiceProvider([1]),
                                     spend_action=False, setup=setup)
        assert landed.applied_condition_ids == ["frightened"]
        assert has_condition(owner.state, "frightened", setup=setup)
        assert _check_mode(owner.state, True, setup) == "disadvantage"
        assert _contest_disadvantage(owner, "strength", setup) == 1
        assert approaches_fear_source(owner, GridPosition(x=2, y=1), setup)
        ally.state.position = GridPosition(x=7, y=1)
        assert not has_condition(owner.state, "frightened", setup=setup)
        assert "frightened" in owner.state.active_effect_ids, "Immunity suppresses; it does not erase a timed source."
        assert _check_mode(owner.state, True, setup) == "normal"
        assert _contest_disadvantage(owner, "strength", setup) == 0
        assert not approaches_fear_source(owner, GridPosition(x=2, y=1), setup)
        attack = owner.state.template.weapon_attack
        hit = resolve_attack(3, 1, owner.state, foe.state, attack, 5,
                             FixedDiceProvider([10, 1, 20]), spend_action=False,
                             actor_event_id=owner.combatant_id, target_event_id=foe.combatant_id,
                             reaction_setup=setup, reaction_roller=owner)
        assert hit.attack_roll.mode == "normal"
        ally.state.position = GridPosition(x=8, y=1)
        assert has_condition(owner.state, "frightened", setup=setup)
        assert card.model_dump() == before
        fresh = build_combatant_state(card)
        assert not fresh.timed_effects and not fresh.active_effect_ids
        assert not condition_is_immune(fresh, "frightened"), "A previous fight's allies cannot persist."
    except Exception:
        logger.exception("Renamed %s visible-ally immunity lifecycle failed.", kind)
        raise
