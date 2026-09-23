from app.combat.action_economy import is_available
from app.combat.state import build_combatant_state
from app.combat.turn_creature_effects import apply_turned_creature_effects
from app.content.capability_registry import build_combatant_from_capabilities
from app.content.cleric_life_2014_runtime import build_seraphine_dawnshield_2014
from app.domain.encounters import EncounterCombatant, EncounterSetup


def _member(template, combatant_id: str, side: str) -> EncounterCombatant:
    return EncounterCombatant(
        combatant_id=combatant_id,
        side=side,
        position_ft=0,
        state=build_combatant_state(template),
    )


def test_2014_turned_state_suppresses_reactions_without_false_conditions() -> None:
    cleric = _member(build_seraphine_dawnshield_2014(1), "cleric", "heroes")
    skeleton = _member(build_combatant_from_capabilities("2014-skeleton"), "skeleton", "monsters")
    setup = EncounterSetup(
        heroes=[cleric], monsters=[skeleton],
        hero_total_levels=1, monster_total_cr="1/4", ruleset="2014",
    )

    applied = apply_turned_creature_effects(
        cleric, skeleton, setup, 1,
        source_effect_id="turn-undead",
        turned_effect_id="turned-undead",
        include_frightened=False,
        include_incapacitated=False,
        suppress_reactions=True,
        ends_if_source_incapacitated=False,
        ends_if_source_dead=False,
    )

    assert applied == ["turned-undead"]
    assert "frightened" not in skeleton.state.active_effect_ids
    assert "incapacitated" not in skeleton.state.active_effect_ids
    assert is_available(skeleton.state, "reaction") is False
    assert is_available(skeleton.state, "action") is True
    effect = next(item for item in skeleton.state.timed_effects if item.effect_id == "turned-undead")
    assert effect.turn_behavior == "forced_retreat"
    assert effect.ends_on_damage is True
    assert effect.ends_if_source_incapacitated is False
    assert effect.ends_if_source_dead is False
