import pytest

from app.combat.dice import FixedDiceProvider
from app.content.catalog import (
    CatalogEntryNotFoundError,
    get_catalog_entry,
    list_character_catalog,
    list_monster_catalog,
)
from app.domain.models import BattleRequest, RulesCoverage
from app.services.catalog_battles import CatalogBattleValidationError, run_catalog_battle


def test_catalog_lists_current_battle_ready_combatants() -> None:
    characters = list_character_catalog()
    monsters = list_monster_catalog()

    assert [entry.combatant.id for entry in characters] == [
        "aldric-vane-l1",
        "mara-stone-l5",
        "darius-flint-l11",
        "vera-ash-l20",
    ]
    assert [entry.combatant.id for entry in monsters] == [
        "srd-wolf",
        "srd-giant-crab",
        "srd-lion",
        "srd-giant-spider",
        "srd-ghoul",
        "srd-goblin-warrior",
        "srd-skeleton",
        "srd-ogre",
        "srd-knight",
        "srd-tough-boss",
    ]
    assert all(entry.battle_ready for entry in [*characters, *monsters])


def test_catalog_exposes_rules_coverage_without_hiding_gaps() -> None:
    fighter = get_catalog_entry("aldric-vane-l1")
    mara = get_catalog_entry("mara-stone-l5")
    wolf = get_catalog_entry("srd-wolf")
    crab = get_catalog_entry("srd-giant-crab")
    lion = get_catalog_entry("srd-lion")
    spider = get_catalog_entry("srd-giant-spider")
    ghoul = get_catalog_entry("srd-ghoul")
    knight = get_catalog_entry("srd-knight")
    ogre = get_catalog_entry("srd-ogre")
    tough_boss = get_catalog_entry("srd-tough-boss")

    fighter_coverage = {item.feature_id: item.coverage for item in fighter.rules_coverage}
    mara_coverage = {item.feature_id: item.coverage for item in mara.rules_coverage}
    wolf_coverage = {item.feature_id: item.coverage for item in wolf.rules_coverage}
    crab_coverage = {item.feature_id: item.coverage for item in crab.rules_coverage}
    lion_coverage = {item.feature_id: item.coverage for item in lion.rules_coverage}
    spider_coverage = {item.feature_id: item.coverage for item in spider.rules_coverage}
    ghoul_coverage = {item.feature_id: item.coverage for item in ghoul.rules_coverage}
    knight_coverage = {item.feature_id: item.coverage for item in knight.rules_coverage}
    ogre_coverage = {item.feature_id: item.coverage for item in ogre.rules_coverage}
    tough_coverage = {item.feature_id: item.coverage for item in tough_boss.rules_coverage}

    assert fighter_coverage["second-wind"] is RulesCoverage.FULLY_IMPLEMENTED
    assert fighter_coverage["weapon-mastery"] is RulesCoverage.UNSUPPORTED
    assert mara_coverage["extra-attack"] is RulesCoverage.FULLY_IMPLEMENTED
    assert mara_coverage["action-surge"] is RulesCoverage.FULLY_IMPLEMENTED
    assert mara_coverage["action-surge-policy"] is RulesCoverage.ARENA_ASSUMPTION
    assert wolf_coverage["bite-prone"] is RulesCoverage.FULLY_IMPLEMENTED
    assert wolf_coverage["pack-tactics"] is RulesCoverage.UNSUPPORTED
    assert crab_coverage["claw-grapple"] is RulesCoverage.FULLY_IMPLEMENTED
    assert crab_coverage["grapple-drag-carry"] is RulesCoverage.UNSUPPORTED
    assert lion_coverage["roar"] is RulesCoverage.FULLY_IMPLEMENTED
    assert lion_coverage["multiattack"] is RulesCoverage.FULLY_IMPLEMENTED
    assert lion_coverage["pack-tactics"] is RulesCoverage.UNSUPPORTED
    assert spider_coverage["web"] is RulesCoverage.FULLY_IMPLEMENTED
    assert spider_coverage["web-recharge"] is RulesCoverage.FULLY_IMPLEMENTED
    assert spider_coverage["web-object"] is RulesCoverage.FULLY_IMPLEMENTED
    assert spider_coverage["spider-climb"] is RulesCoverage.UNSUPPORTED
    assert ghoul_coverage["claw-paralysis-save"] is RulesCoverage.FULLY_IMPLEMENTED
    assert ghoul_coverage["claw-action-policy"] is RulesCoverage.ARENA_ASSUMPTION
    assert knight_coverage["radiant-rider"] is RulesCoverage.FULLY_IMPLEMENTED
    assert knight_coverage["parry"] is RulesCoverage.UNSUPPORTED
    assert ogre_coverage["thrown-weapon-range"] is RulesCoverage.FULLY_IMPLEMENTED
    assert ogre_coverage["javelin-inventory"] is RulesCoverage.ARENA_ASSUMPTION
    assert tough_coverage["warhammer"] is RulesCoverage.FULLY_IMPLEMENTED
    assert tough_coverage["warhammer-push"] is RulesCoverage.FULLY_IMPLEMENTED


def test_catalog_lookup_rejects_unknown_combatant() -> None:
    with pytest.raises(CatalogEntryNotFoundError):
        get_catalog_entry("not-a-real-combatant")


def test_id_driven_battle_preserves_locked_melee_regression() -> None:
    battle = run_catalog_battle(
        BattleRequest(character_id="aldric-vane-l1", monster_id="srd-goblin-warrior"),
        FixedDiceProvider([15, 10, 20, 7, 6]),
    )

    first_attack = next(event for event in battle.events if event.event_type == "attack")
    assert first_attack.actor_id == "aldric-vane-l1"
    assert first_attack.critical is True
    assert battle.winner_id == "aldric-vane-l1"
    assert battle.monster.current_hp == 0


def test_id_driven_battle_validates_catalog_roles() -> None:
    with pytest.raises(CatalogBattleValidationError):
        run_catalog_battle(
            BattleRequest(character_id="srd-goblin-warrior", monster_id="aldric-vane-l1"),
            FixedDiceProvider([10]),
        )
