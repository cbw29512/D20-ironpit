import pytest

from app.combat.public_readiness import assert_public_selection_runnable
from app.domain.encounters import EncounterSelection


def _selection(hero_id: str, monster_id: str = "srd-goblin-warrior") -> EncounterSelection:
    return EncounterSelection(hero_ids=[hero_id], monster_ids=[monster_id])


def test_certified_goblin_passes_public_readiness() -> None:
    assert_public_selection_runnable(_selection("karnok-stoneward-l1"))


@pytest.mark.parametrize("monster_id", ["srd-zombie", "srd-ogre-zombie"])
def test_certified_zombies_pass_public_readiness(monster_id: str) -> None:
    assert_public_selection_runnable(_selection("karnok-stoneward-l1", monster_id))


@pytest.mark.parametrize("monster_id", ["srd-specter", "srd-stirge"])
def test_certified_rider_monsters_pass_public_readiness(monster_id: str) -> None:
    assert_public_selection_runnable(_selection("karnok-stoneward-l1", monster_id))


def test_legacy_uncertified_hero_cannot_bypass_public_readiness() -> None:
    with pytest.raises(ValueError, match="aldric-vane-l1"):
        assert_public_selection_runnable(_selection("aldric-vane-l1"))


def test_uncertified_hero_is_rejected_before_engine_setup() -> None:
    with pytest.raises(ValueError, match="brom-ironmark-l1"):
        assert_public_selection_runnable(_selection("brom-ironmark-l1"))