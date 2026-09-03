from app.content.monster_catalog import load_monster_rows
from app.content.monster_saving_throws import complete_monster_saving_throws
from app.content.monster_source_audit import audit_monster_source
from app.content.monsters_grapple_expansion import build_grapple_expansion
from app.domain.size import CreatureSize


def _templates():
    return {template.name: template for template in complete_monster_saving_throws(build_grapple_expansion())}


def test_grapple_expansion_is_exactly_source_audited() -> None:
    rows = {row["name"]: row for row in load_monster_rows()}
    for name, template in _templates().items():
        assert audit_monster_source(template, rows[name]) == []


def test_giant_scorpion_uses_two_grappling_claws_then_sting() -> None:
    scorpion = _templates()["Giant Scorpion"]
    claw, sting = scorpion.weapon_attack, scorpion.alternate_weapon_attacks[0]
    assert claw.control_effect is not None
    assert claw.control_effect.max_target_size is CreatureSize.LARGE
    assert claw.control_effect.grapple_escape_dc == 13
    assert [(item.source, item.dice_count, item.dice_size, item.damage_type.value) for item in sting.on_hit_damage] == [
        ("Poison", 2, 10, "poison"),
    ]
    assert scorpion.attack_action is not None
    assert [slot.attack_ids for slot in scorpion.attack_action.slots] == [[claw.id], [claw.id], [sting.id]]


def test_grick_and_griffon_use_shared_grapple_schema() -> None:
    templates = _templates()
    grick = templates["Grick"]
    tentacles = grick.alternate_weapon_attacks[0]
    assert tentacles.control_effect is not None
    assert (tentacles.control_effect.max_target_size, tentacles.control_effect.grapple_escape_dc) == (CreatureSize.MEDIUM, 12)
    assert grick.attack_action is not None
    assert [slot.attack_ids for slot in grick.attack_action.slots] == [[grick.weapon_attack.id], [tentacles.id]]

    griffon = templates["Griffon"]
    rend = griffon.weapon_attack
    assert rend.control_effect is not None
    assert (rend.control_effect.max_target_size, rend.control_effect.grapple_escape_dc) == (CreatureSize.MEDIUM, 14)
    assert griffon.attack_action is not None
    assert [slot.attack_ids for slot in griffon.attack_action.slots] == [[rend.id], [rend.id]]
