"""Source-proven Archmage arena loadout substitution regressions."""
from __future__ import annotations

from app.content.capability_compiler import compile_combatant
from app.content.monster_archmage_arena_loadout_2014 import (
    source_proven_archmage_arena_finger_of_death_2014,
)
from app.content.monster_definition_adapter_2014 import adapt_monster_mechanics_2014
from app.content.monster_source_2014 import load_monster_source_2014
from scripts.browser_template_serializer import template_row


def test_2014_archmage_arena_finger_of_death_scans_all_source_cards() -> None:
    cards = load_monster_source_2014()
    assert len(cards) == 327
    matching = [
        card for card in cards
        if source_proven_archmage_arena_finger_of_death_2014(card) is not None
    ]
    assert len(matching) == 1
    card = matching[0]
    initial = card.model_dump_json()
    action = source_proven_archmage_arena_finger_of_death_2014(card)
    assert action is not None
    assert (
        action.id,
        action.name,
        action.dc,
        action.save_ability,
        action.range_ft,
        action.damage_dice_count,
        action.damage_dice_size,
        action.damage_bonus,
        action.damage_type,
        action.success_damage,
        action.level,
        action.action_cost,
    ) == (
        "finger-of-death", "Finger of Death", 17, "constitution", 60,
        7, 8, 30, "necrotic", "half", 7, "action",
    )
    assert card.model_dump_json() == initial

    renamed = card.model_copy(update={"id": "renamed-source", "name": "Renamed Source"})
    assert source_proven_archmage_arena_finger_of_death_2014(renamed) == action


def test_2014_archmage_arena_finger_of_death_fails_closed_on_source_changes() -> None:
    card = next(card for card in load_monster_source_2014() if card.id == "archmage")
    for update in (
        {"source_complete": False},
        {"save_dc": 16},
        {"slots": {**card.spellcasting["slots"], "7": 2}},
        {"spells": [spell for spell in card.spellcasting["spells"] if spell["id"] != "teleport"]},
    ):
        changed = card.model_copy(deep=True)
        changed.spellcasting.update(update)
        assert source_proven_archmage_arena_finger_of_death_2014(changed) is None


def test_2014_archmage_template_exports_arena_finger_to_browser_schema() -> None:
    card = next(card for card in load_monster_source_2014() if card.id == "archmage")
    definition = adapt_monster_mechanics_2014(card)
    action = next(item for item in definition.spell_save_actions if item.id == "finger-of-death")
    assert action.dc == 17
    assert action.level == 7
    slot = next(item for item in definition.resources if item.id == "spell-slot-7")
    assert slot.max_uses == 1
    template = compile_combatant(definition)
    row = template_row(template)
    browser = next(item for item in row["spell_save_actions"] if item["id"] == "finger-of-death")
    assert browser["dc"] == 17
    assert browser["level"] == 7
    assert browser["range"] == 60
    assert browser["damageDiceCount"] == 7
    assert browser["damageDiceSize"] == 8
    assert browser["damageBonus"] == 30
    assert browser["damageType"] == "necrotic"
    assert row["resources"]["spell-slot-7"] == 1

