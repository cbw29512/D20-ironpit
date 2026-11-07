"""Independent printed Engulf Action reuses the shared grapple promotion lifecycle."""
from __future__ import annotations

from app.combat.dice import FixedDiceProvider
from app.combat.encounter_grapple_upgrade_action import resolve_grapple_upgrade_action
from app.combat.grapple import apply_grapple, release_grapple
from app.combat.source_turn_relation_damage import resolve_source_turn_relation_damage
from app.combat.state import build_combatant_state
from app.content.capability_compiler import compile_combatant
from app.content.demo import build_demo_fighter
from app.content.monster_definition_adapter_2014 import adapt_monster_mechanics_2014
from app.content.monster_source_2014 import load_monster_source_2014
from app.domain.encounters import EncounterCombatant, EncounterSetup


def test_existing_grapple_upgrades_with_action_without_early_damage():
    source = next(m for m in load_monster_source_2014() if m.id == "shambling-mound")
    owner = EncounterCombatant(
        combatant_id="owner", side="monsters", position_ft=0,
        state=build_combatant_state(compile_combatant(adapt_monster_mechanics_2014(source))),
    )
    target = EncounterCombatant(
        combatant_id="hero", side="heroes", position_ft=5,
        state=build_combatant_state(build_demo_fighter()),
    )
    setup = EncounterSetup(
        heroes=[target], monsters=[owner], hero_total_levels=1,
        monster_total_cr="5", ruleset="2014",
    )
    assert resolve_grapple_upgrade_action(1, 1, owner, setup) is None
    assert apply_grapple(target.state, "owner", 14, 5) == ["grappled"]
    # Before the separate Action, an ordinary grapple MUST NOT deal Engulf ticks.
    assert resolve_source_turn_relation_damage(
        1, 1, owner, setup, FixedDiceProvider([1]),
    ) == ([], 1)
    events, sequence = resolve_grapple_upgrade_action(1, 1, owner, setup)
    assert sequence == 2 and events[0].feature_id == "Engulf"
    assert owner.state.action_available is False
    assert target.state.grapple_sources[0].linked_effect_id == "engulf"
    assert target.state.grapple_sources[0].prevents_breathing is True
    assert "restrained" in target.state.active_effect_ids
    assert "blinded" in target.state.active_effect_ids
    assert resolve_grapple_upgrade_action(2, 1, owner, setup) is None
    saved, _ = resolve_source_turn_relation_damage(
        2, 2, owner, setup, FixedDiceProvider([20]),
    )
    assert len(saved) == 1 and saved[0].save_succeeded is True
    release_grapple(target.state, "owner")
    assert resolve_source_turn_relation_damage(
        3, 3, owner, setup, FixedDiceProvider([1]),
    ) == ([], 3)
    assert "blinded" not in target.state.active_effect_ids
