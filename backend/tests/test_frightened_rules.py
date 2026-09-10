import pytest

from app.combat.frightened import fear_source_ids, frightened_d20_disadvantage
from app.combat.grid_reaction_movement_support import approaches_fear_source
from app.combat.state import build_combatant_state
from app.combat.timed_conditions import apply_timed_condition
from app.combat.visibility import has_line_of_sight
from app.content.audited_fighter import build_karnok_stoneward
from app.domain.encounters import EncounterCombatant, EncounterSetup
from app.domain.grid import GridPosition


def _member(combatant_id: str, side: str, x: int) -> EncounterCombatant:
    template = build_karnok_stoneward().model_copy(deep=True)
    template.id = f"template-{combatant_id}"
    template.name = combatant_id
    state = build_combatant_state(template)
    state.position = GridPosition(x=x, y=6)
    return EncounterCombatant(
        combatant_id=combatant_id, side=side, position_ft=x * 5, state=state,
    )


def _fear(target: EncounterCombatant, source: EncounterCombatant) -> None:
    apply_timed_condition(
        target.state, "frightened", source.combatant_id,
        source_effect_id="test-fear", applied_round=1,
    )


def test_visibility_defaults_clear_and_explicit_impairments_block_it() -> None:
    observer = _member("observer", "heroes", 0)
    source = _member("source", "monsters", 6)
    assert has_line_of_sight(observer.state, source.state) is True
    observer.state.active_effect_ids.append("blinded")
    assert has_line_of_sight(observer.state, source.state) is False
    observer.state.active_effect_ids.remove("blinded")
    source.state.active_buff_effect_ids.append("invisibility")
    assert has_line_of_sight(observer.state, source.state) is False


def test_frightened_d20_penalty_requires_any_visible_fear_source() -> None:
    target = _member("target", "heroes", 0)
    visible = _member("visible", "monsters", 6)
    hidden = _member("hidden", "monsters", 7)
    setup = EncounterSetup(
        heroes=[target], monsters=[visible, hidden], hero_total_levels=1, monster_total_cr="1",
    )
    _fear(target, visible)
    _fear(target, hidden)
    hidden.state.active_buff_effect_ids.append("invisibility")
    assert set(fear_source_ids(target.state)) == {"visible", "hidden"}
    assert frightened_d20_disadvantage(target.state, setup) == 1
    visible.state.active_buff_effect_ids.append("invisibility")
    assert frightened_d20_disadvantage(target.state, setup) == 0
    target.state.active_effect_ids.append("blinded")
    visible.state.active_buff_effect_ids.clear()
    assert frightened_d20_disadvantage(target.state, setup) == 0


def test_frightened_missing_source_fails_closed() -> None:
    target = _member("target", "heroes", 0)
    source = _member("source", "monsters", 6)
    other = _member("other", "monsters", 7)
    _fear(target, source)
    setup = EncounterSetup(heroes=[target], monsters=[other], hero_total_levels=1, monster_total_cr="0")
    with pytest.raises(ValueError, match="missing from the encounter"):
        frightened_d20_disadvantage(target.state, setup)


def test_frightened_movement_restriction_does_not_require_visibility() -> None:
    target = _member("target", "heroes", 0)
    source = _member("source", "monsters", 6)
    setup = EncounterSetup(heroes=[target], monsters=[source], hero_total_levels=1, monster_total_cr="1")
    _fear(target, source)
    source.state.active_buff_effect_ids.append("invisibility")
    assert frightened_d20_disadvantage(target.state, setup) == 0
    assert approaches_fear_source(target, GridPosition(x=1, y=6), setup) is True
    assert approaches_fear_source(target, GridPosition(x=0, y=5), setup) is False


def test_frightened_itself_invents_no_recovery_save() -> None:
    target = _member("target", "heroes", 0)
    source = _member("source", "monsters", 6)
    _fear(target, source)
    effect = target.state.timed_effects[0]
    assert effect.repeat_save_ability is None
    assert effect.repeat_save_dc is None
    assert effect.repeat_save_timing is None
