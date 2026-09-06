import pytest
from fastapi import HTTPException
from pydantic import ValidationError

from app.content.readiness import assert_public_selection_runnable
from app.domain.models import EncounterSelection
from app.main import create_encounter_setup


def _selection(hero_id: str, monster_id: str = "srd-goblin-warrior") -> EncounterSelection:
    return EncounterSelection(hero_ids=[hero_id], monster_ids=[monster_id])


def test_starting_distance_is_not_a_public_selection_option() -> None:
    with pytest.raises(ValidationError):
        EncounterSelection(
            hero_ids=["karnok-stoneward-l1"],
            monster_ids=["srd-goblin-warrior"],
            starting_distance_ft=30,
        )


@pytest.mark.parametrize(
    "hero_id",
    ["karnok-stoneward-l1", "karnok-stoneward-l2", "karnok-stoneward-l3", "karnok-stoneward-l4", "karnok-stoneward-l5"],
)
def test_audited_karnok_levels_and_certified_monster_pass_public_readiness(hero_id: str) -> None:
    assert_public_selection_runnable(_selection(hero_id))


def test_goblin_boss_passes_public_readiness() -> None:
    assert_public_selection_runnable(_selection("karnok-stoneward-l1", "srd-goblin-boss"))


def test_blood_hawk_passes_public_readiness() -> None:
    assert_public_selection_runnable(_selection("karnok-stoneward-l1", "srd-blood-hawk"))


@pytest.mark.parametrize("monster_id", ["srd-swarm-of-bats", "srd-swarm-of-rats", "srd-swarm-of-crawling-claws"])
def test_certified_swarms_pass_public_readiness(monster_id: str) -> None:
    assert_public_selection_runnable(_selection("karnok-stoneward-l1", monster_id))


@pytest.mark.parametrize(
    "monster_id",
    ["srd-bandit-captain", "srd-knight", "srd-noble", "srd-warrior-veteran"],
)
def test_certified_parry_monsters_pass_public_readiness(monster_id: str) -> None:
    assert_public_selection_runnable(_selection("karnok-stoneward-l1", monster_id))


@pytest.mark.parametrize("monster_id", ["srd-zombie", "srd-ogre-zombie"])
def test_certified_zombies_pass_public_readiness(monster_id: str) -> None:
    assert_public_selection_runnable(_selection("karnok-stoneward-l1", monster_id))


def test_legacy_uncertified_hero_cannot_bypass_catalog_through_api_id() -> None:
    with pytest.raises(ValueError, match="aldric-vane-l1"):
        assert_public_selection_runnable(_selection("aldric-vane-l1"))


def test_uncertified_monster_id_is_rejected_before_engine_setup() -> None:
    with pytest.raises(ValueError, match="srd-mimic"):
        assert_public_selection_runnable(_selection("karnok-stoneward-l1", "srd-mimic"))


def test_public_setup_endpoint_returns_400_for_uncertified_hero() -> None:
    with pytest.raises(HTTPException) as caught:
        create_encounter_setup(_selection("brom-ironmark-l1"))

    assert caught.value.status_code == 400
    assert "brom-ironmark-l1" in str(caught.value.detail)
