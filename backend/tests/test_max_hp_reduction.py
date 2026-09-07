from app.combat.hit_points import effective_max_hp
from app.combat.max_hp import apply_attack_max_hp_reduction, apply_max_hp_reduction
from app.content.roster import build_arena_roster
from app.domain.models import CombatantState, DamageRollComponent, DamageType, MaxHpReductionRider


def _state() -> CombatantState:
    template = next(item for item in build_arena_roster().monsters if item.name == "Commoner")
    return CombatantState(template=template, current_hp=template.max_hp)


def _component(amount: int, applied: int, damage_type: DamageType) -> DamageRollComponent:
    return DamageRollComponent(
        source="test", notation=str(amount), rolls=[], modifier=0,
        damage_type=damage_type, total=amount, applied_total=applied,
    )


def test_max_hp_reduction_is_shared_runtime_survival_math() -> None:
    state = _state()
    before = effective_max_hp(state)
    reduced = apply_max_hp_reduction(state, 2)
    assert reduced == min(2, before)
    assert effective_max_hp(state) == before - reduced
    assert state.current_hp == effective_max_hp(state)


def test_max_hp_reduction_stacks_against_active_max_hp_bonus() -> None:
    state = _state()
    state.max_hp_bonus = 5
    state.current_hp = effective_max_hp(state)
    assert apply_max_hp_reduction(state, 3) == 3
    assert effective_max_hp(state) == state.template.max_hp + 2


def test_max_hp_reduction_to_zero_kills_without_negative_maximum() -> None:
    state = _state()
    apply_max_hp_reduction(state, state.template.max_hp + 100)
    assert effective_max_hp(state) == 0
    assert state.current_hp == 0
    assert state.is_dead is True
    assert state.is_alive is False


def test_attack_max_hp_reduction_uses_post_defense_damage_and_type_filter() -> None:
    state = _state()
    state.max_hp_bonus = 20
    state.current_hp = effective_max_hp(state)
    attack = state.template.weapon_attack.model_copy(update={
        "max_hp_reduction": MaxHpReductionRider(damage_type=DamageType.ACID),
    })
    reduced = apply_attack_max_hp_reduction(state, attack, [
        _component(10, 5, DamageType.BLUDGEONING),
        _component(8, 4, DamageType.ACID),
    ])
    assert reduced == 4
    assert state.max_hp_reduction == 4


def test_attack_max_hp_reduction_without_type_uses_all_applied_components() -> None:
    state = _state()
    state.max_hp_bonus = 20
    state.current_hp = effective_max_hp(state)
    attack = state.template.weapon_attack.model_copy(update={"max_hp_reduction": MaxHpReductionRider()})
    reduced = apply_attack_max_hp_reduction(state, attack, [
        _component(10, 5, DamageType.BLUDGEONING),
        _component(8, 4, DamageType.NECROTIC),
    ])
    assert reduced == 9
