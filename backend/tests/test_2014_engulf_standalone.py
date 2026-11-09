"""Independent printed Engulf Action reuses the shared grapple promotion lifecycle."""
from __future__ import annotations

import logging

from app.combat.dice import FixedDiceProvider
from app.combat.encounter_grapple_upgrade_action import resolve_grapple_upgrade_action
from app.combat.grapple import apply_grapple, release_grapple
from app.combat.multi_hit_grapple import apply_multi_hit_grapples
from app.domain.events import BattleEvent
from app.domain.size import CreatureSize
from app.combat.source_turn_relation_damage import resolve_source_turn_relation_damage
from app.combat.state import build_combatant_state
from app.content.capability_compiler import compile_combatant
from app.content.demo import build_demo_fighter
from app.content.monster_definition_adapter_2014 import adapt_monster_mechanics_2014
from app.content.monster_source_2014 import load_monster_source_2014
from app.domain.encounters import EncounterCombatant, EncounterSetup

logger = logging.getLogger(__name__)


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

def test_second_double_hit_grapples_at_engulf_capacity_then_upgrades_after_release():
    """Capacity limits linked Engulf, not the ordinary source-owned Grappled state."""
    source = next(m for m in load_monster_source_2014() if m.id == "shambling-mound")
    owner = EncounterCombatant(
        combatant_id="owner", side="monsters", position_ft=0,
        state=build_combatant_state(compile_combatant(adapt_monster_mechanics_2014(source))),
    )
    first = EncounterCombatant(
        combatant_id="target", side="heroes", position_ft=5,
        state=build_combatant_state(
            build_demo_fighter().model_copy(update={"size": CreatureSize.MEDIUM, "max_hp": 90})
        ),
    )
    second = EncounterCombatant(
        combatant_id="second", side="heroes", position_ft=5,
        state=build_combatant_state(
            build_demo_fighter().model_copy(update={"size": CreatureSize.MEDIUM, "max_hp": 90})
        ),
    )
    setup = EncounterSetup(
        heroes=[first, second], monsters=[owner], hero_total_levels=1,
        monster_total_cr="5", ruleset="2014",
    )
    attack_id = owner.state.template.multi_hit_grapple_effects[0].attack_id

    def double_hit(target_id: str) -> list[BattleEvent]:
        return [BattleEvent(
            sequence=index, round_number=1, event_type="attack",
            actor_id="owner", actor_name=owner.state.template.name,
            target_id=target_id, attack_id=attack_id, hit=True,
            description="Source-neutral landed Slam.", animation="attack",
        ) for index in (1, 2)]

    linked, _ = apply_multi_hit_grapples(3, 1, owner, setup, double_hit("target"))
    assert len(linked) == 1
    assert first.state.grapple_sources[0].linked_effect_id == "engulf"

    fallback, _ = apply_multi_hit_grapples(4, 1, owner, setup, double_hit("second"))
    assert len(fallback) == 1
    assert fallback[0].applied_condition_ids == ["grappled"]
    assert "capacity reached" in fallback[0].description
    held = second.state.grapple_sources[0]
    assert held.source_id == "owner" and held.escape_dc == 14
    assert held.linked_effect_id is None
    assert held.restrains is False and held.blinds is False
    assert held.prevents_breathing is False
    assert "restrained" not in second.state.active_effect_ids
    assert "blinded" not in second.state.active_effect_ids

    # Hitting the already engulfed target cannot erase its linked state.
    again, _ = apply_multi_hit_grapples(5, 1, owner, setup, double_hit("target"))
    assert again == []
    assert first.state.grapple_sources[0].linked_effect_id == "engulf"

    # Ordinary Grappled must never receive Engulf-only turn damage.
    saved, _ = resolve_source_turn_relation_damage(
        6, 2, owner, setup, FixedDiceProvider([20]),
    )
    assert len(saved) == 1 and saved[0].target_id == "target"

    release_grapple(first.state, "owner")
    upgraded = resolve_grapple_upgrade_action(7, 2, owner, setup)
    assert upgraded is not None and upgraded[0][0].target_id == "second"
    assert second.state.grapple_sources[0].linked_effect_id == "engulf"
    assert "blinded" in second.state.active_effect_ids
    assert "restrained" in second.state.active_effect_ids
