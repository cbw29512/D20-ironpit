from __future__ import annotations

from app.combat.dice import FixedDiceProvider
from app.combat.modifier_stack import attack_roll_flat_bonus
from app.combat.ongoing_spell_control import forced_retreat_active
from app.combat.paladin_channel_divinity_2014 import (
    legal_unholy_targets,
    resolve_paladin_channel_support,
)
from app.combat.state import build_combatant_state
from app.content.capability_registry import build_combatant_from_capabilities
from app.content.monsters import build_commoner
from app.content.paladin_devotion_2014_runtime import build_aurelia_brightshield_2014
from app.domain.encounters import EncounterCombatant, EncounterSetup


def _member(template, combatant_id: str, side: str, position: int) -> EncounterCombatant:
    return EncounterCombatant(
        combatant_id=combatant_id,
        side=side,
        position_ft=position,
        state=build_combatant_state(template),
    )


def _uses(member: EncounterCombatant) -> int:
    return next(item.current_uses for item in member.state.resources if item.id == "channel-divinity")


def test_turn_unholy_takes_priority_over_sacred_weapon() -> None:
    paladin = _member(build_aurelia_brightshield_2014(3), "aurelia", "heroes", 0)
    skeleton = _member(build_combatant_from_capabilities("srd-skeleton"), "skeleton", "monsters", 10)
    fiend = _member(
        build_commoner().model_copy(update={"creature_type": "Fiend"}),
        "fiend", "monsters", 20,
    )
    setup = EncounterSetup(
        heroes=[paladin], monsters=[skeleton, fiend], hero_total_levels=3,
        monster_total_cr="1/4", ruleset="2014",
    )
    assert legal_unholy_targets(paladin, setup) == (skeleton, fiend)

    events, sequence = resolve_paladin_channel_support(
        1, 1, paladin, setup, FixedDiceProvider([1, 20]),
    )

    assert sequence == 3
    assert [event.feature_id for event in events] == ["turn-the-unholy", "turn-the-unholy"]
    assert [event.save_succeeded for event in events] == [False, True]
    assert events[0].save_dc == 12
    assert _uses(paladin) == 0
    assert paladin.state.action_available is False
    assert forced_retreat_active(skeleton.state) is True
    assert {"turned-unholy", "frightened", "incapacitated"}.issubset(skeleton.state.active_effect_ids)
    assert fiend.state.active_effect_ids == []
    assert attack_roll_flat_bonus(paladin.state, "longsword") == 0


def test_sacred_weapon_is_fallback_when_no_unholy_target_is_legal() -> None:
    paladin = _member(build_aurelia_brightshield_2014(3), "aurelia", "heroes", 0)
    commoner = _member(build_commoner(), "commoner", "monsters", 5)
    setup = EncounterSetup(
        heroes=[paladin], monsters=[commoner], hero_total_levels=3,
        monster_total_cr="0", ruleset="2014",
    )

    events, sequence = resolve_paladin_channel_support(
        1, 1, paladin, setup, FixedDiceProvider([10]),
    )

    assert sequence == 2
    assert len(events) == 1
    assert events[0].feature_id == "sacred-weapon"
    assert _uses(paladin) == 0
    assert attack_roll_flat_bonus(paladin.state, "longsword") == 2


def test_unholy_target_outside_thirty_feet_does_not_consume_turn_policy() -> None:
    paladin = _member(build_aurelia_brightshield_2014(3), "aurelia", "heroes", 0)
    skeleton = _member(build_combatant_from_capabilities("srd-skeleton"), "skeleton", "monsters", 35)
    setup = EncounterSetup(
        heroes=[paladin], monsters=[skeleton], hero_total_levels=3,
        monster_total_cr="1/4", ruleset="2014",
    )

    assert legal_unholy_targets(paladin, setup) == ()
    events, _ = resolve_paladin_channel_support(1, 1, paladin, setup, FixedDiceProvider([10]))
    assert events[0].feature_id == "sacred-weapon"
