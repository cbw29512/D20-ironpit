from app.content.capability_registry import build_combatant_from_capabilities
from app.content.monster_catalog import build_monster_catalog
from app.domain.catalog import CoverageStatus
from app.domain.traits import CombatTrait


def test_winter_wolf_composes_existing_shared_primitives() -> None:
    wolf = build_combatant_from_capabilities("srd-winter-wolf")
    bite = wolf.weapon_attack
    breath = wolf.saving_throw_actions[0]
    resource = wolf.resources[0]

    assert wolf.combat_traits == [CombatTrait.PACK_TACTICS]
    assert bite.knocks_prone_max_size.value == "large"
    assert (breath.area.shape, breath.area.size_ft) == ("cone", 15)
    assert (breath.save_ability, breath.dc) == ("constitution", 12)
    assert (breath.damage_dice_count, breath.damage_dice_size, breath.damage_type) == (4, 8, "cold")
    assert breath.success_damage == "half"
    assert breath.resource_id == resource.id
    assert (resource.recharge.minimum, resource.recharge.maximum) == (5, 6)


def test_winter_wolf_is_raw_ready_after_shared_composition() -> None:
    card = next(card for card in build_monster_catalog() if card.name == "Winter Wolf")
    assert card.coverage_status == CoverageStatus.RAW_READY
    assert card.runnable_template_id == "srd-winter-wolf"
    assert card.blockers == []
