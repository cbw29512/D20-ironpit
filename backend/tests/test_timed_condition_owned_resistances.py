from app.combat.damage_defenses import adjusted_damage_amount
from app.combat.state import build_combatant_state
from app.combat.timed_conditions import apply_timed_condition, remove_effect_group
from app.content.demo import build_demo_fighter
from app.domain.models import DamageType


def test_apply_timed_condition_carries_source_owned_resistances() -> None:
    state = build_combatant_state(build_demo_fighter())

    applied = apply_timed_condition(
        state,
        "invisible",
        "hero",
        source_effect_id="test-composite-buff",
        applied_round=1,
        expires_round=11,
        owned_damage_resistances=[DamageType.FIRE, DamageType.COLD],
    )

    assert applied == "invisible"
    assert state.active_effect_ids == ["invisible"]
    assert state.temporary_damage_resistances == []
    assert state.timed_effects[0].owned_damage_resistances == [DamageType.FIRE, DamageType.COLD]
    assert adjusted_damage_amount(9, DamageType.FIRE, state) == 4
    assert adjusted_damage_amount(9, DamageType.FORCE, state) == 9


def test_group_cleanup_removes_only_resistances_owned_by_expired_source() -> None:
    state = build_combatant_state(build_demo_fighter())
    apply_timed_condition(
        state,
        "invisible",
        "hero",
        source_effect_id="first-source",
        owned_damage_resistances=[DamageType.FIRE],
    )
    apply_timed_condition(
        state,
        "blurred",
        "hero",
        source_effect_id="second-source",
        owned_damage_resistances=[DamageType.COLD],
    )

    first = next(effect for effect in state.timed_effects if effect.source_effect_id == "first-source")
    removed = remove_effect_group(state, first)

    assert removed == ["invisible"]
    assert adjusted_damage_amount(8, DamageType.FIRE, state) == 8
    assert adjusted_damage_amount(8, DamageType.COLD, state) == 4
    assert any(effect.source_effect_id == "second-source" for effect in state.timed_effects)
