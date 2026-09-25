from app.combat.pooled_healing import pooled_healing_capacity, resolve_pooled_healing
from app.combat.state import build_combatant_state
from app.content.roster import build_arena_roster
from app.domain.encounters import EncounterCombatant


def _monster_template(template_id: str):
    try:
        return next(
            item for item in build_arena_roster("2014").monsters
            if item.id == template_id
        )
    except StopIteration as exc:
        raise ValueError(f"Missing certified 2014 monster template: {template_id}") from exc


def _member(combatant_id: str, current_hp: int) -> EncounterCombatant:
    template = _monster_template("2014-goblin")
    member = EncounterCombatant(
        combatant_id=combatant_id,
        side="heroes",
        position_ft=0,
        state=build_combatant_state(template),
    )
    member.state.current_hp = current_hp
    return member


def test_universal_pooled_healing_respects_shared_pool_and_target_ceiling() -> None:
    first = _member("first", 0)
    second = _member("second", 1)
    first_capacity = pooled_healing_capacity(first, 1, 2)
    second_capacity = pooled_healing_capacity(second, 1, 2)

    allocations, remaining = resolve_pooled_healing(
        (first, second),
        100,
        cap_numerator=1,
        cap_denominator=2,
    )

    assert [(target.combatant_id, healed) for target, healed in allocations] == [
        ("first", first_capacity),
        ("second", second_capacity),
    ]
    assert first.state.current_hp == first.state.template.max_hp // 2
    assert second.state.current_hp == second.state.template.max_hp // 2
    assert remaining == 100 - first_capacity - second_capacity
