from app.content.monster_catalog import load_monster_rows
from app.content.monster_simple_source_compiler import compile_simple_monster
from app.content.monster_source_audit import audit_monster_source
from app.content.monster_source_classifier import source_blockers


def _fire_giant_row() -> dict[str, object]:
    return next(row for row in load_monster_rows() if row["name"] == "Fire Giant")


def test_fire_giant_uses_existing_universal_push_and_attack_modifier_primitives() -> None:
    row = _fire_giant_row()
    names = {str(item["name"]) for item in load_monster_rows()}

    assert source_blockers(row, names) == []
    giant = compile_simple_monster(row, names)

    attacks = {attack.weapon.name: attack for attack in [giant.weapon_attack, *giant.alternate_weapon_attacks]}
    hammer = attacks["Hammer Throw"]
    assert hammer.control_effect is not None
    assert hammer.control_effect.forced_movement is not None
    assert hammer.control_effect.forced_movement.direction == "push"
    assert hammer.control_effect.forced_movement.max_distance_ft == 15
    assert hammer.control_effect.forced_movement.distance_mode == "up_to"
    assert [effect.kind for effect in hammer.on_hit_modifier_effects] == ["next-attack-made-disadvantage"]
    assert hammer.on_hit_modifier_effects[0].consume_on_attack_made is True
    assert hammer.on_hit_modifier_effects[0].expires_at_end_of_target_turn is True

    assert giant.attack_action is not None
    assert len(giant.attack_action.slots) == 2
    allowed = {attack_id for slot in giant.attack_action.slots for attack_id in slot.attack_ids}
    assert giant.weapon_attack.id in allowed
    assert hammer.id in allowed

    assert audit_monster_source(giant, row) == []
