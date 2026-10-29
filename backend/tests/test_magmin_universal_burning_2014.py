"""Magmin's hit-ignited Burning runs through the shared effect engine."""
from app.content.monster_source_2014 import load_monster_source_2014
from app.content.monster_ignite_on_hit_source_2014 import source_ignite_on_hit_2014
from app.content.monster_definition_adapter_2014 import adapt_monster_mechanics_2014
from app.content.capability_compiler import compile_combatant
from scripts.browser_template_serializer import template_row


def test_magmin_touch_burns_with_exact_printed_card_numbers():
    card = next(m for m in load_monster_source_2014() if m.id == "magmin")
    touch = next(a for a in card.attacks if a.name.casefold() == "touch")
    proof = source_ignite_on_hit_2014(card, touch)
    assert proof is not None
    assert (proof.damage_dice_count, proof.damage_dice_size, proof.damage_type) == (1, 6, "fire")
    compiled = compile_combatant(adapt_monster_mechanics_2014(card))
    attack = next(a for a in compiled.attacks if a.id.endswith("-touch"))
    assert attack.on_hit_end_turn_dice_count == 1
    assert attack.on_hit_end_turn_dice_size == 6
    assert attack.on_hit_end_turn_damage_type.value == "fire"
    browser = template_row(compiled)
    touch_row = next(a for a in browser["attacks"] if a["id"] == attack.id)
    assert touch_row["onHitEndTurnDamage"]["effectId"] == "burning"
    assert touch_row["onHitEndTurnDamage"]["diceCount"] == 1
