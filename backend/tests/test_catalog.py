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


def test_catalog_lists_current_mvp_combatants() -> None:
    characters = list_character_catalog()
    monsters = list_monster_catalog()

    assert [entry.combatant.id for entry in characters] == ["aldric-vane-l1"]
    assert [entry.combatant.id for entry in monsters] == ["srd-goblin-warrior"]
    assert characters[0].battle_ready is True
    assert monsters[0].battle_ready is True


def test_catalog_exposes_rules_coverage_without_hiding_gaps() -> None:
    fighter = get_catalog_entry("aldric-vane-l1")
    goblin = get_catalog_entry("srd-goblin-warrior")

    fighter_coverage = {item.feature_id: item.coverage for item in fighter.rules_coverage}
    goblin_coverage = {item.feature_id: item.coverage for item in goblin.rules_coverage}

    assert fighter_coverage["second-wind"] is RulesCoverage.FULLY_IMPLEMENTED
    assert fighter_coverage["weapon-mastery"] is RulesCoverage.UNSUPPORTED
    assert goblin_coverage["shortbow"] is RulesCoverage.FULLY_IMPLEMENTED
    assert goblin_coverage["nimble-escape"] is RulesCoverage.UNSUPPORTED


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
