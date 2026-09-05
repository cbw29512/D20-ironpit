from app.content.capability_registry import load_capability_definitions
from app.content.monster_recharge_batch import RECHARGE_MONSTER_NAMES, build_recharge_monster_definitions
from app.content.monster_source_audit import audit_monster_source
from app.content.monster_source_definition import source_row


def test_recharge_family_is_source_derived_from_names_only() -> None:
    definitions = build_recharge_monster_definitions()
    assert len(definitions) == len(RECHARGE_MONSTER_NAMES) == 11
    hell_hound = definitions["srd-hell-hound"]
    assert hell_hound.armor_class == 15
    assert hell_hound.max_hp == 58
    assert hell_hound.attack_action is not None
    assert len(hell_hound.attack_action.slots) == 2
    assert hell_hound.save_actions[0].name == "Fire Breath"
    assert hell_hound.save_actions[0].area_slots == 3
    assert hell_hound.resources[0].recharge_min_d6 == 5


def test_every_recharge_definition_passes_full_srd_source_audit() -> None:
    for definition in build_recharge_monster_definitions().values():
        from app.content.capability_compiler import compile_combatant
        from app.content.monster_creature_types import complete_monster_creature_types

        template = complete_monster_creature_types([compile_combatant(definition)])[0]
        assert audit_monster_source(template, source_row(definition.name)) == []


def test_native_definitions_no_longer_need_a_separate_ready_map() -> None:
    definitions = load_capability_definitions()
    for name in RECHARGE_MONSTER_NAMES:
        monster_id = f"srd-{name.lower().replace(' ', '-')}"
        assert monster_id in definitions
    assert "srd-spy" in definitions
    assert "srd-hill-giant" in definitions
