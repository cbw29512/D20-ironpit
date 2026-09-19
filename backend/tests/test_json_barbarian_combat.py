from app.combat.attacks import resolve_attack
from app.combat.barbarian import enter_rage
from app.combat.dice import FixedDiceProvider
from app.combat.state import build_combatant_state
from app.content.json_hero_runtime import compile_json_hero_template
from app.content.monsters import build_commoner


def _rokhan(edition: str, slug: str, level: int):
    return build_combatant_state(compile_json_hero_template(edition, slug, level))


def test_2014_json_level_20_rages_without_a_use_counter_and_logs_a_hit() -> None:
    attacker = _rokhan("2014", "rokhan-stonefury-2014", 20)
    defender = build_combatant_state(build_commoner().model_copy(update={"armor_class": 10, "max_hp": 20}))
    assert attacker.template.unlimited_resource_ids == ["rage"]
    assert enter_rage(1, 1, attacker, attacker.template.id) is not None
    event = resolve_attack(
        1, 1, attacker, defender, attacker.template.weapon_attack,
        5, FixedDiceProvider([15, 8]), turn_key="1:rokhan",
    )
    assert event.hit is True
    assert event.hp_after is not None and event.hp_before is not None
    assert event.hp_after < event.hp_before
    assert "Greataxe" in event.description


def test_2024_json_level_10_retaliation_is_on_the_compiled_template() -> None:
    hero = compile_json_hero_template("2024", "rokhan-stonefury", 10)
    assert hero.damage_reaction_attack is not None
    assert hero.damage_reaction_attack.source_feature == "retaliation"
    assert hero.damage_reaction_attack.source_range_ft == 5
