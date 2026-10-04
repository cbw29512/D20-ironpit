from __future__ import annotations

from app.combat.condition_removal import resolve_condition_removal
from app.combat.condition_removal_policy import choose_condition_removal_action, removable
from app.combat.restoration_riders import apply_hit_point_maximum_reduction
from app.combat.state import begin_turn, build_combatant_state
from app.combat.timed_conditions import apply_timed_condition
from app.content.audited_cleric import build_seraphine_dawnshield_level
from app.content.paladin_devotion_2024_runtime import build_aurelia_brightshield_2024
from app.content.shared_restoration_spells_2024 import greater_restoration_2024
from app.domain.encounters import EncounterCombatant, EncounterSetup
from app.domain.grid import GridPosition


def _member(template, combatant_id: str) -> EncounterCombatant:
    member = EncounterCombatant(
        combatant_id=combatant_id,
        side="heroes",
        position_ft=0,
        state=build_combatant_state(template),
    )
    member.state.position = GridPosition(x=2, y=2)
    return member


def test_greater_restoration_2024_matches_printed_riders() -> None:
    spell = greater_restoration_2024()
    assert spell.id == "greater-restoration"
    assert spell.action_cost == "action"
    assert spell.range_ft == 5
    assert spell.removable_conditions == ["charmed", "petrified"]
    assert spell.max_conditions_per_use == 1
    assert spell.resource_costs == {"spell-slot-5": 1}
    assert spell.expends_spell_slot is True
    assert spell.reduces_exhaustion_levels == 1
    assert spell.removes_curses is True
    assert spell.removes_ability_score_reductions is True
    assert spell.removes_hit_point_maximum_reductions is True


def test_cleric_and_paladin_bind_greater_restoration_instead_of_a_label() -> None:
    cleric = build_seraphine_dawnshield_level(9)
    paladin = build_aurelia_brightshield_2024(17)
    assert any(item.id == "greater-restoration" for item in cleric.condition_removal_actions)
    assert any(item.id == "greater-restoration" for item in paladin.condition_removal_actions)


def test_greater_restoration_ends_one_printed_rider() -> None:
    cleric = _member(build_seraphine_dawnshield_level(9), "seraphine")
    begin_turn(cleric.state)
    apply_timed_condition(cleric.state, "charmed", "enemy", source_is_magical=True, applied_round=1)
    action = next(item for item in cleric.state.template.condition_removal_actions if item.id == "greater-restoration")
    assert removable(cleric, action)[0] == "charmed"
    event = resolve_condition_removal(1, 1, cleric, cleric, action, ["charmed"], "1:seraphine")
    assert event.removed_condition_ids == ["charmed"]
    assert "charmed" not in cleric.state.active_effect_ids
    slot = next(item for item in cleric.state.resources if item.id == "spell-slot-5")
    assert slot.current_uses == 0


def test_greater_restoration_reduces_exhaustion_and_clears_other_printed_riders() -> None:
    cleric = _member(build_seraphine_dawnshield_level(9), "seraphine")
    action = next(item for item in cleric.state.template.condition_removal_actions if item.id == "greater-restoration")
    setup = EncounterSetup(
        heroes=[cleric],
        monsters=[_member(build_seraphine_dawnshield_level(9), "dummy")],
        hero_total_levels=9,
        monster_total_cr="0",
        ruleset="2024",
    )
    setup.monsters[0].side = "monsters"

    cleric.state.exhaustion_level = 2
    begin_turn(cleric.state)
    chosen = choose_condition_removal_action(cleric, setup, "1:seraphine")
    assert chosen is not None
    assert chosen[0].id == "greater-restoration"
    assert chosen[2] == ["exhaustion"]
    resolve_condition_removal(1, 1, cleric, cleric, action, ["exhaustion"], "1:seraphine")
    assert cleric.state.exhaustion_level == 1

    begin_turn(cleric.state)
    next(item for item in cleric.state.resources if item.id == "spell-slot-5").current_uses = 1
    cleric.state.action_available = True
    cleric.state.active_curses = ["bestow-curse"]
    resolve_condition_removal(2, 2, cleric, cleric, action, ["curse"], "2:seraphine")
    assert cleric.state.active_curses == []

    begin_turn(cleric.state)
    next(item for item in cleric.state.resources if item.id == "spell-slot-5").current_uses = 1
    cleric.state.action_available = True
    cleric.state.ability_score_reductions = {"strength": 2}
    resolve_condition_removal(3, 3, cleric, cleric, action, ["ability-score-reduction"], "3:seraphine")
    assert cleric.state.ability_score_reductions == {}

    begin_turn(cleric.state)
    next(item for item in cleric.state.resources if item.id == "spell-slot-5").current_uses = 1
    cleric.state.action_available = True
    apply_hit_point_maximum_reduction(cleric, 10)
    resolve_condition_removal(4, 4, cleric, cleric, action, ["hit-point-maximum-reduction"], "4:seraphine")
    assert cleric.state.hit_point_maximum_reduction == 0
