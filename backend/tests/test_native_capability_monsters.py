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
    "srd-sahuagin-warrior": "Sahuagin Warrior",
}


def test_native_monsters_are_not_legacy_builder_outputs() -> None:
    legacy_ids = {monster.id for monster in build_legacy_monster_templates()}
    assert set(NATIVE).isdisjoint(legacy_ids)


def test_native_definitions_extend_production_roster_without_replacing_legacy_ids() -> None:
    legacy = build_legacy_monster_templates()
    production = build_arena_roster().monsters
    assert len(production) == len(legacy) + len(NATIVE)
    assert [monster.id for monster in production[-len(NATIVE):]] == list(NATIVE)


def test_native_registry_rejects_cross_layer_duplicate_ids() -> None:
    definition = get_capability_definition("srd-swarm-of-insects")
    with pytest.raises(ValueError, match="ids overlap"):
        merge_capability_definitions({definition.id: definition}, {definition.id: definition})


def test_native_monsters_compile_and_pass_full_srd_source_audit() -> None:
    rows = {str(row["name"]): row for row in load_monster_rows()}
    runtime = {monster.id: monster for monster in build_arena_roster().monsters}
    for template_id, source_name in NATIVE.items():
        assert get_capability_definition(template_id).kind == "monster"
        assert audit_monster_source(runtime[template_id], rows[source_name]) == []


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
