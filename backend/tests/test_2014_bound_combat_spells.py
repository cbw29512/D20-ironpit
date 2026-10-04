from app.content.cleric_life_2014_runtime import build_seraphine_dawnshield_2014
from app.content.paladin_devotion_2014_runtime import build_aurelia_brightshield_2014
from app.content.pregen_2014_roster_audit import runtime_binding_ids
from app.content.shared_healing_spells_2014 import heal_2014, mass_healing_word_2014
from app.content.shared_restoration_spells_2014 import greater_restoration_2014
from app.content.warlock_2014_spell_package import build_warlock_2014_spell_package
from app.content.warlock_fiend_2014_runtime import build_varek_ashenmark_2014


def test_2014_mass_healing_word_uses_printed_1d4_and_excludes_undead() -> None:
    spell = mass_healing_word_2014(5, additional_healing_bonus=5)

    assert (
        spell.id,
        spell.action_cost,
        spell.range_ft,
        spell.max_targets,
        spell.dice_count,
        spell.dice_size,
        spell.healing_bonus,
        spell.resource_id,
        spell.excluded_creature_types,
    ) == (
        "mass-healing-word",
        "bonus_action",
        60,
        6,
        1,
        4,
        10,
        "spell-slot-3",
        ["undead", "construct"],
    )


def test_2014_heal_is_touch_70_hp_and_does_not_end_poisoned() -> None:
    spell = heal_2014(additional_healing_bonus=8)

    assert (
        spell.id,
        spell.action_cost,
        spell.range_ft,
        spell.healing_bonus,
        spell.resource_id,
        spell.removable_conditions,
        spell.excluded_creature_types,
    ) == (
        "heal",
        "action",
        5,
        78,
        "spell-slot-6",
        ["blinded", "deafened"],
        ["undead", "construct"],
    )
    assert "poisoned" not in spell.removable_conditions


def test_2014_greater_restoration_removes_charm_or_petrify_only() -> None:
    spell = greater_restoration_2014()

    assert spell.id == "greater-restoration"
    assert spell.action_cost == "action"
    assert spell.range_ft == 5
    assert spell.removable_conditions == ["charmed", "petrified"]
    assert spell.max_conditions_per_use == 1
    assert spell.resource_costs == {"spell-slot-5": 1}
    assert spell.expends_spell_slot is True
    assert "exhaustion" not in spell.removable_conditions


def test_2014_life_cleric_binds_prepared_supported_spells_at_slice_entry() -> None:
    before = runtime_binding_ids(build_seraphine_dawnshield_2014(7))
    level_eight = runtime_binding_ids(build_seraphine_dawnshield_2014(8))
    level_ten = runtime_binding_ids(build_seraphine_dawnshield_2014(10))
    level_thirteen = runtime_binding_ids(build_seraphine_dawnshield_2014(13))
    level_fifteen = runtime_binding_ids(build_seraphine_dawnshield_2014(15))
    level_sixteen = runtime_binding_ids(build_seraphine_dawnshield_2014(16))
    level_nineteen = runtime_binding_ids(build_seraphine_dawnshield_2014(19))

    assert "mass-healing-word" not in before
    assert "mass-healing-word" in level_eight
    assert "dispel-magic" in level_ten
    assert "freedom-of-movement" in level_thirteen
    assert "flame-strike" in level_fifteen
    assert "greater-restoration" in level_sixteen
    assert "heal" in level_nineteen


def test_2014_life_cleric_does_not_bind_unsupported_named_spells() -> None:
    ids = runtime_binding_ids(build_seraphine_dawnshield_2014(20))

    assert "warding-bond" not in ids
    assert "hold-person" not in ids
    assert "silence" not in ids
    assert "spirit-guardians" not in ids
    assert "protection-from-energy" not in ids
    assert "remove-curse" not in ids
    assert "harm" not in ids


def test_2014_paladin_magic_weapon_stays_unbound() -> None:
    assert "magic-weapon" not in runtime_binding_ids(build_aurelia_brightshield_2014(20))


def test_2014_warlock_utilities_are_source_backed_arena_out_of_scope() -> None:
    package = build_warlock_2014_spell_package(10)
    by_id = {item.id: item for item in (*package.cantrips, *package.spells)}

    assert by_id["comprehend-languages"].required_capabilities == ["arena-out-of-scope"]
    assert by_id["mage-hand"].required_capabilities == ["arena-out-of-scope"]
    assert by_id["hallucinatory-terrain"].required_capabilities == ["arena-out-of-scope"]
    assert by_id["prestidigitation"].required_capabilities == ["arena-out-of-scope"]
    assert by_id["dimension-door"].required_capabilities == ["teleport"]
    assert "dimension-door" not in runtime_binding_ids(build_varek_ashenmark_2014(20))
