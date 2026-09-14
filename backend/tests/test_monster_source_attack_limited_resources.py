from __future__ import annotations

from app.content.monster_source_capability_candidates import source_candidate_definitions
from app.content.source_capability_enrichment import enrich_definition


def _ape_source_definition():
    return source_candidate_definitions(set())["srd-ape"]


def test_source_attack_compiler_binds_recharge_marker_to_shared_resource() -> None:
    source = _ape_source_definition()
    rock = next(attack for attack in source.attacks if attack.name == "Rock")
    resource = next(item for item in source.resources if item.id == rock.resource_id)

    assert rock.resource_id == "srd-ape-rock"
    assert rock.resource_cost == 1
    assert resource.name == "Rock"
    assert resource.max_uses == 1
    assert resource.recharge is not None
    assert resource.recharge.minimum_roll == 6


def test_enrichment_propagates_source_attack_resource_binding() -> None:
    source = _ape_source_definition()
    stripped = source.model_copy(update={
        "resources": [],
        "attacks": [attack.model_copy(update={"resource_id": None}) for attack in source.attacks],
    })

    enriched = enrich_definition(stripped, source)
    rock = next(attack for attack in enriched.attacks if attack.name == "Rock")

    assert rock.resource_id == "srd-ape-rock"
    assert any(item.id == rock.resource_id for item in enriched.resources)
