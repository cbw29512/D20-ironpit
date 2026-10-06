from __future__ import annotations

import logging

from app.combat.dice import FixedDiceProvider
from app.combat.melee_hit_retaliation import active_melee_hit_retaliation, apply_melee_hit_retaliation
from app.combat.state import build_combatant_state
from app.content.capability_compiler import compile_combatant
from app.content.monster_basic_candidates_2014 import basic_blockers_2014, unsupported_traits_2014
from app.content.monster_definition_adapter_2014 import adapt_basic_monster_2014
from app.content.monster_heat_traits_2014 import (
    heated_body_action_2014,
    supports_heated_weapons_2014,
)
from app.content.monster_source_2014 import load_monster_source_2014
from app.domain.encounters import EncounterCombatant

logger = logging.getLogger(__name__)


def _monster(name: str):
    try:
        return next(monster for monster in load_monster_source_2014() if monster.name == name)
    except Exception:
        logger.exception("Failed to load 2014 source monster %s.", name)
        raise


def _member(template, combatant_id: str, side: str, position: int) -> EncounterCombatant:
    try:
        return EncounterCombatant(
            combatant_id=combatant_id,
            side=side,
            position_ft=position,
            state=build_combatant_state(template),
        )
    except Exception:
        logger.exception("Failed to build heat-trait test member %s.", combatant_id)
        raise


def test_heated_body_uses_one_passive_shared_retaliation_shape() -> None:
    expected = {
        "Azer": (1, 10),
        "Salamander": (2, 6),
        "Remorhaz": (3, 6),
    }
    for name, dice in expected.items():
        action = heated_body_action_2014(_monster(name))
        assert action is not None
        assert action.name == "Heated Body"
        assert action.activation_timing == "passive"
        assert action.duration_rounds is None
        assert action.melee_hit_retaliation is not None
        assert (
            action.melee_hit_retaliation.dice_count,
            action.melee_hit_retaliation.dice_size,
            action.melee_hit_retaliation.range_ft,
            action.melee_hit_retaliation.damage_type.value,
        ) == (*dice, 5, "fire")


def test_heated_weapons_reuses_fire_damage_already_in_source_attack() -> None:
    for name in ("Azer", "Salamander"):
        monster = _monster(name)
        assert supports_heated_weapons_2014(monster)
        assert any(
            isinstance(row, dict)
            and row.get("type") == "fire"
            and row.get("dice_count") == 1
            and row.get("dice_size") == 6
            for attack in monster.attacks
            for row in attack.on_hit_damage
        )


def test_heat_traits_are_no_longer_source_trait_blockers() -> None:
    for name in ("Azer", "Salamander", "Remorhaz"):
        unsupported = set(unsupported_traits_2014(_monster(name)))
        assert "Heated Body" not in unsupported
        assert "Heated Weapons" not in unsupported


def test_azer_is_certifiable_without_double_adding_heated_weapon_damage() -> None:
    azer = _monster("Azer")
    assert basic_blockers_2014(azer) == ()
    runtime = compile_combatant(adapt_basic_monster_2014(azer))
    fire = [rider for rider in runtime.weapon_attack.on_hit_damage if rider.damage_type.value == "fire"]
    assert len(fire) == 1
    assert (fire[0].dice_count, fire[0].dice_size, fire[0].damage_bonus) == (1, 6, 0)

    heated = next(action for action in runtime.timed_self_buff_actions if action.name == "Heated Body")
    assert heated.activation_timing == "passive"


def test_passive_heated_body_retaliates_without_mutating_buff_state() -> None:
    defender_template = compile_combatant(adapt_basic_monster_2014(_monster("Azer")))
    attacker_template = compile_combatant(adapt_basic_monster_2014(_monster("Bandit")))
    defender = _member(defender_template, "azer", "monsters", 5)
    attacker = _member(attacker_template, "bandit", "heroes", 0)

    assert defender.state.timed_effects == []
    bound = active_melee_hit_retaliation(defender.state)
    assert bound is not None and bound[0].name == "Heated Body"

    before = attacker.state.current_hp
    applied = apply_melee_hit_retaliation(
        attacker,
        defender,
        melee=True,
        dice=FixedDiceProvider([10]),
        affected_states=[attacker.state, defender.state],
    )
    assert applied == 10
    assert attacker.state.current_hp == before - 10
    assert defender.state.timed_effects == []


def test_heated_body_does_not_retaliate_beyond_five_feet() -> None:
    defender_template = compile_combatant(adapt_basic_monster_2014(_monster("Azer")))
    attacker_template = compile_combatant(adapt_basic_monster_2014(_monster("Bandit")))
    defender = _member(defender_template, "azer", "monsters", 10)
    attacker = _member(attacker_template, "bandit", "heroes", 0)

    before = attacker.state.current_hp
    assert apply_melee_hit_retaliation(
        attacker,
        defender,
        melee=True,
        dice=FixedDiceProvider([10]),
    ) == 0
    assert attacker.state.current_hp == before
