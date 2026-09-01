from app.combat.condition_immunity import apply_condition_if_allowed
from app.combat.conditions import apply_hit_conditions
from app.combat.state import build_combatant_state
from app.combat.timed_conditions import apply_timed_condition
from app.combat.zero_hp import apply_damage
from app.content.catalog import get_arena_roster


def _template(item_id: str):
    roster = get_arena_roster()
    return next(item for item in [*roster.characters, *roster.monsters] if item.id == item_id).model_copy(deep=True)


def test_poisoned_immunity_blocks_timed_condition_entirely() -> None:
    target = build_combatant_state(_template("karnok-stoneward-l1"))
    target.template.condition_immunities = ["poisoned"]
    assert apply_timed_condition(
        target, "poisoned", "test-poison", 1, expires_at="end_of_source_next_turn",
    ) is False
    assert "poisoned" not in target.active_effect_ids
    assert target.timed_conditions == []


def test_grappled_immunity_blocks_grapple_and_restrained_rider() -> None:
    target = build_combatant_state(_template("karnok-stoneward-l1"))
    target.template.condition_immunities = ["grappled"]
    assert apply_condition_if_allowed(target, "grappled") is False
    assert target.grapple_source_id is None
    assert "grappled" not in target.active_effect_ids
    assert apply_condition_if_allowed(target, "restrained") is True
    assert "restrained" in target.active_effect_ids


def test_restrained_immunity_keeps_legal_grapple_without_restrained() -> None:
    target = build_combatant_state(_template("karnok-stoneward-l1"))
    target.template.condition_immunities = ["restrained"]
    assert apply_condition_if_allowed(target, "grappled") is True
    target.grapple_source_id = "attacker"
    assert apply_condition_if_allowed(target, "restrained") is False
    assert "grappled" in target.active_effect_ids
    assert "restrained" not in target.active_effect_ids


def test_prone_immunity_blocks_on_hit_prone_rider() -> None:
    bear = build_combatant_state(_template("srd-brown-bear"))
    target = build_combatant_state(_template("karnok-stoneward-l1"))
    target.template.condition_immunities = ["prone"]
    attack = bear.template.weapon_attack
    attack.knocks_prone_max_size = "large"
    applied = apply_hit_conditions(attack, target, "bear", 1)
    assert applied == []
    assert "prone" not in target.active_effect_ids


def test_prone_immunity_is_respected_when_character_becomes_unconscious() -> None:
    target = build_combatant_state(_template("karnok-stoneward-l1"))
    target.template.condition_immunities = ["prone"]
    target.resources["relentless-endurance"] = 0
    apply_damage(target, target.current_hp)
    assert target.current_hp == 0
    assert target.is_unconscious is True
    assert "prone" not in target.active_effect_ids
