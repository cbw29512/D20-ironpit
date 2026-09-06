from app.content.monster_catalog import build_monster_catalog
from app.content.simple_monster_source_attacks import parse_simple_attacks
from app.content.simple_monster_source_definitions import build_simple_source_definitions
from app.domain.catalog import CoverageStatus


_EXPECTED_SIMPLE_SOURCE = {
    "Azer Sentinel", "Berserker", "Blink Dog", "Bone Devil", "Bugbear Warrior", "Ettin", "Fire Giant", "Hezrou",
    "Hill Giant", "Hobgoblin Captain", "Magmin", "Merrow", "Mimic", "Nightmare", "Sahuagin Warrior", "Satyr",
    "Specter", "Spy", "Tough Boss", "Troll Limb", "Wraith", "Xorn",
}


def test_simple_source_family_compiles_without_bespoke_monster_builders() -> None:
    definitions = build_simple_source_definitions()
    assert {item.name for item in definitions.values()} == _EXPECTED_SIMPLE_SOURCE

    spy = definitions["srd-spy"]
    poison = [effect for attack in spy.attacks for effect in attack.effects if effect.kind == "damage"]
    assert any(effect.damage_type.value == "poison" for effect in poison)

    fire_giant = definitions["srd-fire-giant"]
    hammer = next(attack for attack in fire_giant.attacks if attack.name == "Hammer Throw")
    disadvantage = [effect for effect in hammer.effects if effect.kind == "next-attack-disadvantage"]
    assert len(disadvantage) == 1
    assert disadvantage[0].expires_at_end_of_target_turn is True

    ettin = definitions["srd-ettin"]
    morningstar = next(attack for attack in ettin.attacks if attack.name == "Morningstar")
    assert any(effect.kind == "next-attack-disadvantage" for effect in morningstar.effects)
    battleaxe = next(attack for attack in ettin.attacks if attack.name == "Battleaxe")
    assert any(effect.kind == "prone" for effect in battleaxe.effects)

    boss = definitions["srd-tough-boss"]
    assert boss.attack_action is not None
    assert len(boss.attack_action.slots) == 2
    assert all(len(slot.attack_ids) == 2 for slot in boss.attack_action.slots)

    xorn = definitions["srd-xorn"]
    assert xorn.attack_action is not None
    xorn_names = {attack.id: attack.name for attack in xorn.attacks}
    assert [xorn_names[slot.attack_ids[0]] for slot in xorn.attack_action.slots] == ["Bite", "Claw", "Claw", "Claw"]

    for name in ("Specter", "Wraith"):
        drainer = definitions[f"srd-{name.lower()}"]
        life_drain = next(attack for attack in drainer.attacks if attack.name == "Life Drain")
        assert any(effect.kind == "max-hp-reduction" for effect in life_drain.effects)


def test_simple_source_parser_compiles_generic_grapple_and_prone_riders() -> None:
    grapple_row = {
        "name": "Homebrew Grappler",
        "actions": (
            "Grab. Melee Attack Roll: +5, reach 10 ft. "
            "Hit: 8 (1d10 + 3) Bludgeoning damage. "
            "If the target is a Medium or smaller creature, it has the Grappled condition (escape DC 13)."
        ),
    }
    attacks, _ = parse_simple_attacks(grapple_row)
    assert attacks[0]["effects"] == [{"kind": "grapple", "escape_dc": 13, "max_target_size": "medium"}]

    prone_row = {
        "name": "Homebrew Charger",
        "actions": (
            "Ram. Melee Attack Roll: +6, reach 5 ft. "
            "Hit: 10 (1d12 + 4) Bludgeoning damage. "
            "If the target is a Large or smaller creature, it has the Prone condition."
        ),
    }
    attacks, _ = parse_simple_attacks(prone_row)
    assert attacks[0]["effects"] == [{"kind": "prone", "max_target_size": "large"}]


def test_simple_source_parser_compiles_maximum_hp_drain_by_damage_outcome() -> None:
    untyped = {
        "name": "Homebrew Drainer",
        "actions": (
            "Life Drain. Melee Attack Roll: +4, reach 5 ft. Hit: 7 (2d6) Necrotic damage. "
            "If the target is a creature, its Hit Point maximum decreases by an amount equal to the damage taken."
        ),
    }
    attacks, _ = parse_simple_attacks(untyped)
    assert {"kind": "max-hp-reduction"} in attacks[0]["effects"]

    typed = {
        "name": "Homebrew Acid Drainer",
        "actions": (
            "Slam. Melee Attack Roll: +8, reach 5 ft. Hit: 12 (2d6 + 5) Bludgeoning damage plus 3 (1d6) Acid damage. "
            "The target's Hit Point maximum is reduced by an amount equal to the Acid damage taken."
        ),
    }
    attacks, _ = parse_simple_attacks(typed)
    assert {"kind": "max-hp-reduction", "damage_type": "acid"} in attacks[0]["effects"]


def test_simple_source_family_is_promoted_only_through_full_catalog_audit() -> None:
    cards = {card.name: card for card in build_monster_catalog()}
    for name in _EXPECTED_SIMPLE_SOURCE:
        assert cards[name].coverage_status is CoverageStatus.RAW_READY
        assert cards[name].blockers == []
    assert cards["Roper"].coverage_status is CoverageStatus.BLOCKED
