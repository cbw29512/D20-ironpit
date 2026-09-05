from app.content.monster_catalog import build_monster_catalog
from app.content.simple_monster_source_definitions import build_simple_source_definitions
from app.domain.catalog import CoverageStatus


def test_simple_source_family_compiles_without_bespoke_monster_builders() -> None:
    definitions = build_simple_source_definitions()
    assert {item.name for item in definitions.values()} == {"Blink Dog", "Spy", "Tough Boss", "Xorn"}

    spy = definitions["srd-spy"]
    poison = [effect for attack in spy.attacks for effect in attack.effects if effect.kind == "damage"]
    assert any(effect.damage_type.value == "poison" for effect in poison)

    boss = definitions["srd-tough-boss"]
    assert boss.attack_action is not None
    assert len(boss.attack_action.slots) == 2
    assert all(len(slot.attack_ids) == 2 for slot in boss.attack_action.slots)

    xorn = definitions["srd-xorn"]
    assert xorn.attack_action is not None
    xorn_names = {attack.id: attack.name for attack in xorn.attacks}
    assert [xorn_names[slot.attack_ids[0]] for slot in xorn.attack_action.slots] == ["Bite", "Claw", "Claw", "Claw"]


def test_simple_source_family_is_promoted_only_through_full_catalog_audit() -> None:
    cards = {card.name: card for card in build_monster_catalog()}
    for name in ("Blink Dog", "Spy", "Tough Boss", "Xorn"):
        assert cards[name].coverage_status is CoverageStatus.RAW_READY
        assert cards[name].blockers == []
