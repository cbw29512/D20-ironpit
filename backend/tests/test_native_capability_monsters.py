import pytest

from app.content.capability_registry import (
    build_combatant_from_capabilities,
    get_capability_definition,
    merge_capability_definitions,
)
from app.content.legacy_monster_roster import build_legacy_monster_templates
from app.content.monster_catalog import load_monster_rows
from app.content.monster_source_audit import audit_monster_source
from app.content.roster import build_arena_roster
from app.domain.traits import CombatTrait

NATIVE = {
    "srd-swarm-of-insects": "Swarm of Insects",
    "srd-swarm-of-venomous-snakes": "Swarm of Venomous Snakes",
    "srd-ape": "Ape",
    "srd-lion": "Lion",
    "srd-hill-giant": "Hill Giant",
    "srd-sahuagin-warrior": "Sahuagin Warrior",
    "srd-xorn": "Xorn",
}

# Native capability definitions can exist before their complete source semantics are
# certified. Keep this list limited to definitions whose full SRD audit is currently
# clean; unresolved source choices must fail closed instead of being silently guessed.
SOURCE_AUDIT_CLEAN = {
    template_id: source_name
    for template_id, source_name in NATIVE.items()
    if template_id != "srd-swarm-of-insects"
}


def test_native_monsters_are_not_legacy_builder_outputs() -> None:
    legacy_ids = {monster.id for monster in build_legacy_monster_templates()}
    assert set(NATIVE).isdisjoint(legacy_ids)


def test_native_definitions_are_present_once_in_production_roster() -> None:
    production = build_arena_roster().monsters
    production_ids = [monster.id for monster in production]
    assert len(production_ids) == len(set(production_ids))
    assert set(NATIVE) <= set(production_ids)


def test_native_registry_rejects_cross_layer_duplicate_ids() -> None:
    definition = get_capability_definition("srd-swarm-of-insects")
    with pytest.raises(ValueError, match="ids overlap"):
        merge_capability_definitions({definition.id: definition}, {definition.id: definition})


def test_source_audit_clean_native_monsters_pass_full_srd_source_audit() -> None:
    rows = {str(row["name"]): row for row in load_monster_rows()}
    runtime = {monster.id: monster for monster in build_arena_roster().monsters}
    for template_id, source_name in SOURCE_AUDIT_CLEAN.items():
        assert get_capability_definition(template_id).kind == "monster"
        assert audit_monster_source(runtime[template_id], rows[source_name]) == []


def test_swarm_of_insects_fails_closed_on_unresolved_gm_movement_choice() -> None:
    rows = {str(row["name"]): row for row in load_monster_rows()}
    runtime = {monster.id: monster for monster in build_arena_roster().monsters}
    issues = audit_monster_source(runtime["srd-swarm-of-insects"], rows["Swarm of Insects"])
    assert "movement-choice-source-unmodeled" in issues
    assert "movement-fly-mismatch" in issues


def test_swarm_of_insects_uses_existing_swarm_and_bloodied_capabilities() -> None:
    swarm = build_combatant_from_capabilities("srd-swarm-of-insects")
    attack = swarm.weapon_attack
    assert swarm.combat_traits == [CombatTrait.SWARM]
    assert swarm.speed_ft == 20
    assert swarm.movement_modes.fly_ft == 20
    assert swarm.source_trait_names == ["Spider Climb", "Swarm"]
    assert (attack.weapon.dice_count, attack.weapon.dice_size, attack.damage_bonus) == (2, 4, 1)
    assert len(attack.conditional_damage) == 1
    bloodied = attack.conditional_damage[0]
    assert (bloodied.trigger, bloodied.mode) == ("attacker_bloodied", "replace_weapon")
    assert (bloodied.dice_count, bloodied.dice_size, bloodied.damage_bonus) == (1, 4, 1)


def test_swarm_of_venomous_snakes_preserves_poison_when_bloodied() -> None:
    swarm = build_combatant_from_capabilities("srd-swarm-of-venomous-snakes")
    attack = swarm.weapon_attack
    assert swarm.combat_traits == [CombatTrait.SWARM]
    assert swarm.movement_modes.swim_ft == 30
    assert (attack.weapon.dice_count, attack.weapon.dice_size, attack.damage_bonus) == (1, 8, 4)
    assert len(attack.on_hit_damage) == 1
    poison = attack.on_hit_damage[0]
    assert (poison.dice_count, poison.dice_size, poison.damage_bonus, poison.damage_type.value) == (3, 6, 0, "poison")
    assert len(attack.conditional_damage) == 1
    bloodied = attack.conditional_damage[0]
    assert (bloodied.trigger, bloodied.mode) == ("attacker_bloodied", "replace_weapon")
    assert (bloodied.dice_count, bloodied.dice_size, bloodied.damage_bonus) == (1, 4, 4)
