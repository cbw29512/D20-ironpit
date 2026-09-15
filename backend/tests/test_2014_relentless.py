from app.combat.state import build_combatant_state
from app.combat.zero_hp import apply_damage
from app.content.demo import build_goblin_warrior
from app.domain.combatants import ResourceDefinition
from app.domain.zero_hp_prevention import ZeroHpPrevention


def _state(threshold: int):
    template = build_goblin_warrior().model_copy(deep=True, update={
        "zero_hp_prevention": ZeroHpPrevention(
            resource_id="relentless", max_trigger_damage=threshold, resulting_hp=1,
        ),
        "resources": [ResourceDefinition(id="relentless", name="Relentless", max_uses=1)],
    })
    state = build_combatant_state(template)
    state.current_hp = 5
    return state


def test_relentless_prevents_only_qualifying_damage_once():
    state = _state(7)
    assert apply_damage(state, 7) == "zero_hp_prevention"
    assert state.current_hp == 1
    assert state.is_alive and not state.is_dead
    assert next(item for item in state.resources if item.id == "relentless").current_uses == 0
    assert apply_damage(state, 7) == "dead"
    assert state.is_dead


def test_relentless_damage_ceiling_is_exact():
    boar = _state(7)
    assert apply_damage(boar, 8) == "dead"
    giant_boar = _state(10)
    assert apply_damage(giant_boar, 10) == "zero_hp_prevention"
    too_much = _state(10)
    assert apply_damage(too_much, 11) == "dead"
