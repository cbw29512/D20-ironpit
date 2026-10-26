"""Universal equipment corrosion: item threshold, reset and magic exclusion."""
from __future__ import annotations

from app.combat.armor_corrosion import corrode_armor_on_hit
from app.combat.state import build_combatant_state
from app.content.demo import build_demo_fighter


def test_nonmagical_metal_armor_item_corrosion_is_encounter_local():
    card = build_demo_fighter()
    snapshot = card.model_dump_json()
    state = build_combatant_state(card)
    kwargs = {"item_base_ac": 16}
    assert corrode_armor_on_hit(state, "chain", hit=False,
                               nonmagical_metal_armor=True, **kwargs).penalty == 0
    assert corrode_armor_on_hit(state, "chain", hit=True,
                               nonmagical_metal_armor=False, **kwargs).penalty == 0
    for n in range(1, 7):
        result = corrode_armor_on_hit(state, "chain", hit=True,
                                      nonmagical_metal_armor=True, **kwargs)
        assert result.penalty == -n
        assert result.destroyed == (n == 6)
    assert not corrode_armor_on_hit(state, "chain", hit=True,
                                    nonmagical_metal_armor=True, **kwargs).applied
    assert corrode_armor_on_hit(state, "plate", hit=True,
                                nonmagical_metal_armor=True,
                                item_base_ac=18).penalty == -1
    assert build_combatant_state(card).armor_corrosion_penalties == {}
    assert build_combatant_state(card).destroyed_armor_ids == []
    assert card.model_dump_json() == snapshot
