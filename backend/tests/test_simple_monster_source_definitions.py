from app.content.monster_catalog import build_monster_catalog
from app.content.simple_monster_source_attacks import parse_simple_attacks
from app.content.simple_monster_source_definitions import build_simple_source_definitions
from app.domain.catalog import CoverageStatus


_EXPECTED_SIMPLE_SOURCE = {
    "Ankheg", "Azer Sentinel", "Berserker", "Black Dragon Wyrmling", "Blink Dog", "Blue Dragon Wyrmling", "Bone Devil", "Bugbear Stalker", "Bugbear Warrior",
    "Ettin", "Fire Giant", "Ghoul", "Giant Shark", "Green Dragon Wyrmling", "Hell Hound", "Hezrou", "Hill Giant", "Hobgoblin Captain", "Hunter Shark",
    "Lion", "Magmin", "Merrow", "Nightmare", "Piranha", "Pirate", "Red Dragon Wyrmling", "Sahuagin Warrior", "Satyr", "Specter", "Spy", "Tough Boss",
    "Troll Limb", "Werebear", "Wereboar", "Wererat", "Weretiger", "Werewolf", "White Dragon Wyrmling", "Winter Wolf", "Wraith", "Xorn",
}
_EXPECTED_READY_SOURCE = _EXPECTED_SIMPLE_SOURCE


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

    ghoul = definitions["srd-ghoul"]
    claw = next(effect for attack in definitions["srd-ghoul"].attacks for effect in attack.effects if attack.name == "Claw" and effect.kind == "condition")
    assert claw.condition == "paralyzed" and claw.initial_save_ability == "constitution" and claw.initial_save_dc == 10
    assert claw.expiry_timing == "target_turn_end" and claw.excluded_creature_types == ["undead"] and claw.excluded_species_ids == ["elf"]

    boss = definitions["srd-tough-boss"]
    assert boss.attack_action is not None and len(boss.attack_action.slots) == 2
    assert all(len(slot.attack_ids) == 2 for slot in boss.attack_action.slots)

    xorn = definitions["srd-xorn"]
    assert xorn.attack_action is not None
    xorn_names = {attack.id: attack.name for attack in xorn.attacks}
    assert [xorn_names[slot.attack_ids[0]] for slot in xorn.attack_action.slots] == ["Bite", "Claw", "Claw", "Claw"]

    for name in ("Specter", "Wraith"):
        drainer = definitions[f"srd-{name.lower()}"]
        life_drain = next(attack for attack in drainer.attacks if attack.name == "Life Drain")
        assert any(effect.kind == "max-hp-reduction" for effect in life_drain.effects)


def test_lycanthropes_enter_in_battle_ready_hybrid_form_without_curse_runtime() -> None:
    definitions = build_simple_source_definitions()
    expected_sizes = {"Werebear": "large", "Wereboar": "medium", "Wererat": "medium", "Weretiger": "large", "Werewolf": "large"}
    for name, size in expected_sizes.items():
        definition = definitions[f"srd-{name.lower()}"]
        assert definition.size.value == size
        assert definition.save_actions == []
        assert definition.attack_action is not None


def test_wereboar_uses_source_derived_universal_charge_data() -> None:
    definition = build_simple_source_definitions()["srd-wereboar"]
    tusk = next(attack for attack in definition.attacks if attack.name.startswith("Tusk"))
    profile = tusk.charge
    assert profile is not None and profile.minimum_move_ft == 20
    assert profile.max_target_size.value == "medium" and profile.prone_max_target_size.value == "medium"
    assert profile.bonus_damage is not None and (profile.bonus_damage.dice_count, profile.bonus_damage.dice_size) == (2, 6)
    assert profile.bonus_damage.damage_type.value == "piercing"
    assert "charge" not in definition.combat_traits


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
    assert attacks[0]["effects"] == [{
        "kind": "grapple", "escape_dc": 13, "max_target_size": "medium", "escape_check_disadvantage": False,
    }]

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
    for name in _EXPECTED_READY_SOURCE:
        assert cards[name].coverage_status is CoverageStatus.RAW_READY
        assert cards[name].blockers == []
    for name in ("Mimic", "Roper"):
        assert cards[name].coverage_status is CoverageStatus.BLOCKED
