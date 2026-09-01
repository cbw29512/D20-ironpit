from app.combat.conditions import apply_hit_conditions
from app.combat.grapple import apply_grapple
from app.combat.state import build_combatant_state
from app.combat.timed_conditions import apply_timed_condition
from app.combat.zero_hp import apply_damage
from app.main import get_arena_roster


def _template(item_id: str):
    roster = get_arena_roster()
    return next(item for item in [*roster.characters, *roster.monsters] if item.id == item_id).model_copy(deep=True)


def test_poisoned_immunity_blocks_timed_condition_entirely() -> None:
    target = build_combatant_state(_template("karnok-stoneward-l1"))
    target.template.condition_immunities = ["poisoned"]

    applied = apply_timed_condition(target, "poisoned", "centipede")

    assert applied is None
    assert "poisoned" not in target.active_effect_ids
    assert target.timed_effects == []


def test_grappled_immunity_blocks_grapple_and_restrained_rider() -> None:
    target = build_combatant_state(_template("karnok-stoneward-l1"))
    target.template.condition_immunities = ["grappled"]

    applied = apply_grapple(target, "crocodile", 12, 5, restrains=True)

    assert applied == []
    assert target.grapple_sources == []
    assert "grappled" not in target.active_effect_ids
    assert "restrained" not in target.active_effect_ids


def test_restrained_immunity_keeps_legal_grapple_without_restrained() -> None:
    target = build_combatant_state(_template("karnok-stoneward-l1"))
    target.template.condition_immunities = ["restrained"]

    applied = apply_grapple(target, "crocodile", 12, 5, restrains=True)

    assert applied == ["grappled"]
    assert len(target.grapple_sources) == 1
    assert target.grapple_sources[0].restrains is False
    assert "grappled" in target.active_effect_ids
    assert "restrained" not in target.active_effect_ids


def test_prone_immunity_blocks_on_hit_prone_rider() -> None:
    bear = build_combatant_state(_template("srd-brown-bear"))
    target = build_combatant_state(_template("karnok-stoneward-l1"))
    target.template.condition_immunities = ["prone"]
    claw = bear.template.alternate_weapon_attacks[0]

    applied = apply_hit_conditions(claw, target, "brown-bear")

    assert "prone" not in applied
    assert "prone" not in target.active_effect_ids


def test_prone_immunity_is_respected_when_character_becomes_unconscious() -> None:
    target = build_combatant_state(_template("karnok-stoneward-l1"))
    target.template.condition_immunities = ["prone"]
    relentless = next(item for item in target.resources if item.id == "relentless-endurance")
    relentless.current_uses = 0

    outcome = apply_damage(target, target.current_hp)

    assert outcome == "unconscious"
    assert target.is_unconscious is True
    assert "prone" not in target.active_effect_ids
