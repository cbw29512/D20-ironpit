"""Water Elemental held-target damage is card data, not a Whelm resolver."""
from __future__ import annotations

from app.combat.dice import FixedDiceProvider
from app.combat.grapple import apply_grapple, release_grapple
from app.combat.source_turn_relation_damage import resolve_source_turn_relation_damage
from app.combat.state import build_combatant_state
from app.content.capability_compiler import compile_combatant
from app.content.demo import build_demo_fighter
from app.content.monster_basic_candidates_2014 import basic_blockers_2014
from app.content.monster_definition_adapter_2014 import adapt_monster_mechanics_2014
from app.content.monster_source_2014 import load_monster_source_2014
from app.content.monster_source_held_turn_damage_2014 import source_held_turn_damage_2014
from app.domain.encounters import EncounterCombatant, EncounterSetup
from app.domain.weapons_base import DamageType
from scripts.browser_template_serializer import template_row


def _cards():
    cards = load_monster_source_2014()
    assert len(cards) == 327
    return {card.id: card for card in cards}


def _fight():
    card = _cards()["water-elemental"]
    template = compile_combatant(adapt_monster_mechanics_2014(card))
    owner = EncounterCombatant(
        combatant_id="water-owner", side="monsters", position_ft=0,
        state=build_combatant_state(template),
    )
    hero = build_demo_fighter().model_copy(update={"max_hp": 75})
    target = EncounterCombatant(
        combatant_id="held-hero", side="heroes", position_ft=0,
        state=build_combatant_state(hero),
    )
    setup = EncounterSetup(
        heroes=[target], monsters=[owner], hero_total_levels=1,
        monster_total_cr="5", ruleset="2014",
    )
    return owner, target, setup


def test_full_roster_strict_source_and_browser_export():
    cards = _cards()
    found = {
        key: rules
        for key, card in cards.items()
        if (rules := source_held_turn_damage_2014(card))
    }
    assert list(found) == ["water-elemental"]
    source = cards["water-elemental"]
    unchanged = source.model_dump_json()
    (rule,) = found["water-elemental"]
    assert (rule.source_name, rule.target_relation) == (
        "Whelm", "creatures_grappled_by_source",
    )
    assert (rule.dice_count, rule.dice_size, rule.damage_bonus) == (2, 8, 4)
    assert rule.damage_type == DamageType.BLUDGEONING
    assert rule.save_ability is None and rule.save_dc is None
    template = compile_combatant(adapt_monster_mechanics_2014(source))
    assert rule in template.source_turn_relation_damages
    browser = template_row(template)
    assert rule.model_dump(mode="json") in browser["source_turn_relation_damages"]
    assert "mechanic:recharge" in basic_blockers_2014(source)
    assert "source:extra-action" in basic_blockers_2014(source)
    assert source.model_dump_json() == unchanged


def test_source_mutation_rejects_unknown_outcome_and_action_rename_works():
    source = _cards()["water-elemental"]
    for before, after in (
        ("At the start of each of the elemental's turns", "At the end of each of the elemental's turns"),
        ("unless it can breathe water", "unless it can breathe air"),
        ("one Large creature or up to two Medium", "two Large creatures or up to two Medium"),
        ("each target grappled by it", "each creature adjacent to it"),
        ("escape DC 14", "escape DC 17"),
    ):
        assert before in source.source_actions
        altered = source.model_copy(update={
            "source_actions": source.source_actions.replace(before, after),
        })
        assert source_held_turn_damage_2014(altered) == []
    renamed = source.model_copy(update={
        "id": "renamed-flowing-source", "name": "Renamed Flowing Source",
        "source_actions": source.source_actions.replace(
            "Whelm (Recharge 4–6)", "Torrent (Recharge 4–6)",
        ),
        "action_names": [
            name.replace("Whelm (Recharge 4–6)", "Torrent (Recharge 4–6)")
            for name in source.action_names
        ],
        "action_recharges": {"torrent": 4},
    })
    (rule,) = source_held_turn_damage_2014(renamed)
    assert rule.source_name == "Torrent"
    assert (rule.dice_count, rule.dice_size, rule.damage_bonus) == (2, 8, 4)


def test_existing_relationship_damage_takes_typed_damage_only_while_held():
    owner, target, setup = _fight()
    hp = target.state.current_hp
    assert resolve_source_turn_relation_damage(
        1, 1, owner, setup, FixedDiceProvider([1]),
    ) == ([], 1)
    apply_grapple(target.state, owner.combatant_id, 14, 0, restrains=True)
    events, sequence = resolve_source_turn_relation_damage(
        1, 2, owner, setup, FixedDiceProvider([3, 5]),
    )
    assert sequence == 2 and len(events) == 1
    assert events[0].feature_id == "Whelm"
    assert target.state.current_hp == hp - 12
    assert events[0].hp_after == hp - 12
    release_grapple(target.state, owner.combatant_id)
    assert resolve_source_turn_relation_damage(
        2, 3, owner, setup, FixedDiceProvider([3, 5]),
    ) == ([], 2)
