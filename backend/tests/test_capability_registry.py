import pytest

from app.content.capability_registry import build_combatant_from_capabilities, get_capability_definition, parse_capability_definitions
from app.content.monster_catalog import load_monster_rows
from app.content.monster_source_audit import audit_monster_source
from app.content.roster import build_arena_roster
from app.domain.size import CreatureSize
from app.domain.traits import CombatTrait

MIGRATED = {
    "srd-wolf": "Wolf",
    "srd-dire-wolf": "Dire Wolf",
    "srd-giant-constrictor-snake": "Giant Constrictor Snake"
}


def test_data_registry_compiles_representative_capabilities() -> None:
    wolf = build_combatant_from_capabilities("srd-wolf")
    dire = build_combatant_from_capabilities("srd-dire-wolf")
    snake = build_combatant_from_capabilities("srd-giant-constrictor-snake")
    assert wolf.combat_traits == [CombatTrait.PACK_TACTICS]
    assert wolf.weapon_attack.knocks_prone_max_size == CreatureSize.MEDIUM
    assert dire.weapon_attack.knocks_prone_max_size == CreatureSize.LARGE
    assert snake.attack_action is not None and len(snake.attack_action.slots) == 2
    assert snake.saving_throw_actions[0].grapple_escape_dc == 14
    assert snake.saving_throw_actions[0].damage_dice_size == 8


def test_registry_rejects_duplicate_ids() -> None:
    row = get_capability_definition("srd-wolf").model_dump(mode="json")
    with pytest.raises(ValueError, match="ids must be unique"):
        parse_capability_definitions([row, row])


def test_migrated_data_definitions_still_pass_full_srd_source_audit() -> None:
    runtime = {template.id: template for template in build_arena_roster().monsters}
    rows = {str(row["name"]): row for row in load_monster_rows()}
    for template_id, source_name in MIGRATED.items():
        assert audit_monster_source(runtime[template_id], rows[source_name]) == []
