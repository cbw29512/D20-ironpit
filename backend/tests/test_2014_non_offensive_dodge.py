from app.combat.dice import FixedDiceProvider
from app.combat.encounter_combat_turn import resolve_combat_turn
from app.combat.engine import MAX_ROUNDS, run_duel
from app.combat.state import build_combatant_state
from app.content.capability_compiler import compile_combatant
from app.content.demo import build_demo_fighter
from app.content.monster_definition_adapter_2014 import adapt_basic_monster_2014
from app.content.monster_non_offensive_dodge_2014 import non_offensive_dodge_inventory_2014
from app.content.monster_source_2014 import load_monster_source_2014
from app.domain.encounters import EncounterCombatant, EncounterSetup
from scripts.browser_template_serializer import template_row


def _sea_horse():
    source = load_monster_source_2014()
    card = next(monster for monster in source if monster.id == "sea-horse")
    return card, compile_combatant(adapt_basic_monster_2014(card))


def test_327_card_non_offensive_inventory_is_complete() -> None:
    report = non_offensive_dodge_inventory_2014(load_monster_source_2014())
    assert report["source_card_count"] == 327
    assert report["applicable_card_count"] == 4
    assert report["wired_card_count"] == 1
    assert report["remaining_card_count"] == 3
    assert report["wired"] == [{"monster_id": "sea-horse", "monster_name": "Sea Horse"}]
    assert {item["monster_id"] for item in report["exceptions"]} == {
        "frog", "rug-of-smothering", "shrieker",
    }


def test_sea_horse_compiles_and_serializes_without_fabricated_attack() -> None:
    source, template = _sea_horse()
    source_before = source.model_dump_json()
    assert template.weapon_attack is None
    assert template.alternate_weapon_attacks == []
    row = template_row(template)
    assert row["attacks"] == []
    assert row["primary_attack_id"] is None
    assert source.model_dump_json() == source_before


def test_sea_horse_turn_uses_shared_dodge_fallback() -> None:
    source, template = _sea_horse()
    source_before = source.model_dump_json()
    sea_horse = EncounterCombatant(
        combatant_id="renamed-non-offensive-card", side="monsters", position_ft=10,
        state=build_combatant_state(template.model_copy(update={"name": "Renamed Card"})),
    )
    hero = EncounterCombatant(
        combatant_id="hero", side="heroes", position_ft=5,
        state=build_combatant_state(build_demo_fighter()),
    )
    setup = EncounterSetup(
        heroes=[hero], monsters=[sea_horse], hero_total_levels=1,
        monster_total_cr="0", ruleset="2014",
    )
    events, _ = resolve_combat_turn(
        1, 1, sea_horse, hero, setup, FixedDiceProvider([10]),
    )
    assert any(event.feature_id == "dodge" for event in events)
    assert not any(event.event_type == "attack" for event in events)
    assert source.model_dump_json() == source_before


def test_attack_free_duel_uses_existing_round_limit() -> None:
    _, template = _sea_horse()
    result = run_duel(template, template, FixedDiceProvider([10, 10]))
    assert result.winner_id is None
    assert result.rounds == MAX_ROUNDS
    assert result.events[-1].event_type == "draw"
