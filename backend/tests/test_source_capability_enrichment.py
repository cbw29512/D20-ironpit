from app.content.source_capability_enrichment import (
    _merge_resources,
    _merge_save_actions,
    _resource_rebinds,
)
from app.domain.capability_attacks import SaveCapabilityDefinition
from app.domain.combatants import ResourceDefinition


def _resource(resource_id: str) -> ResourceDefinition:
    return ResourceDefinition(
        id=resource_id,
        name="Fire Breath",
        max_uses=1,
        recharge={"minimum_roll": 5},
    )


def _save(action_id: str, resource_id: str | None, *, area: bool = False) -> SaveCapabilityDefinition:
    return SaveCapabilityDefinition(
        id=action_id,
        name="Fire Breath",
        save_ability="dexterity",
        dc=12,
        range_ft=0,
        area={"shape": "cone", "origin": "self", "length_ft": 15} if area else None,
        damage={"count": 4, "size": 6, "bonus": 0},
        damage_type="fire",
        success_damage="half",
        resource_id=resource_id,
    )


def test_source_recharge_save_reuses_canonical_action_and_resource_ids() -> None:
    existing_resources = [_resource("hell-hound-fire-breath-recharge")]
    source_resources = [_resource("srd-hell-hound-fire-breath")]
    existing_actions = [_save("hell-hound-fire-breath", "hell-hound-fire-breath-recharge")]
    source_actions = [_save("srd-hell-hound-fire-breath", "srd-hell-hound-fire-breath", area=True)]

    rebinds = _resource_rebinds(existing_resources, source_resources)
    actions = _merge_save_actions(existing_actions, source_actions, rebinds)
    resources = _merge_resources(existing_resources, source_resources)

    assert len(actions) == 1
    assert actions[0].id == "hell-hound-fire-breath"
    assert actions[0].resource_id == "hell-hound-fire-breath-recharge"
    assert actions[0].area is not None
    assert actions[0].area.length_ft == 15
    assert [resource.id for resource in resources] == ["hell-hound-fire-breath-recharge"]


def test_source_only_save_rebinds_to_existing_semantic_resource() -> None:
    existing_resources = [_resource("young-dragon-fire-breath-recharge")]
    source_resources = [_resource("srd-young-dragon-fire-breath")]
    source_actions = [_save("srd-young-dragon-fire-breath", "srd-young-dragon-fire-breath", area=True)]

    rebinds = _resource_rebinds(existing_resources, source_resources)
    actions = _merge_save_actions([], source_actions, rebinds)

    assert len(actions) == 1
    assert actions[0].id == "srd-young-dragon-fire-breath"
    assert actions[0].resource_id == "young-dragon-fire-breath-recharge"


def test_resource_free_semantic_save_duplicate_keeps_canonical_action() -> None:
    existing_actions = [_save("legacy-fire-breath", None)]
    source_actions = [_save("srd-fire-breath", None)]

    actions = _merge_save_actions(existing_actions, source_actions, {})

    assert len(actions) == 1
    assert actions[0].id == "legacy-fire-breath"
