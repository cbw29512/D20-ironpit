from app.combat.attacks import resolve_attack
from app.combat.dice import FixedDiceProvider
from app.combat.hit_modifiers import apply_hit_modifier_effects, expire_source_turn_start_modifiers
from app.combat.state import build_combatant_state
from app.content.audited_fighter import build_karnok_stoneward
from app.content.monster_catalog import load_monster_rows
from app.content.monster_saving_throws import with_source_saving_throws
from app.content.monster_source_audit import audit_monster_source
from app.content.monster_worg import build_worg
from app.domain.modifiers import ModifierKind


def _worg():
    return with_source_saving_throws(build_worg())


def test_worg_bite_and_advantage_rider_match_srd() -> None:
    worg = _worg()
    bite = worg.weapon_attack
    assert (bite.id, bite.attack_bonus, bite.weapon.dice_count, bite.weapon.dice_size, bite.damage_bonus) == (
        "srd-worg-bite", 5, 1, 8, 3,
    )
    assert len(bite.on_hit_modifier_effects) == 1
    rider = bite.on_hit_modifier_effects[0]
    assert rider.kind == "attacks-against-advantage"
    assert rider.consume_on_attack_against is True
    assert rider.expires_at_start_of_source_turn is True
    row = next(row for row in load_monster_rows() if row["name"] == "Worg")
    assert audit_monster_source(worg, row) == []


def test_worg_hit_primes_exactly_one_attack_against_target() -> None:
    worg = build_combatant_state(_worg())
    target = build_combatant_state(build_karnok_stoneward().model_copy(deep=True))
    event = resolve_attack(
        1, 1, worg, target, worg.template.weapon_attack, 5,
        FixedDiceProvider([15, 1]), actor_event_id="worg", target_event_id="target", spend_action=False,
    )
    assert event.hit is True
    assert len(target.active_modifiers) == 1
    modifier = target.active_modifiers[0]
    assert modifier.kind is ModifierKind.ATTACKS_AGAINST_ADVANTAGE
    assert modifier.source_id == "worg"
    assert modifier.consume_on_attack_against is True
    assert modifier.expires_at_start_of_source_turn is True

    target.template.armor_class = 30
    attacker = build_combatant_state(build_karnok_stoneward().model_copy(deep=True))
    follow_up = resolve_attack(
        2, 1, attacker, target, attacker.template.weapon_attack, 5,
        FixedDiceProvider([5, 15]), actor_event_id="ally", target_event_id="target", spend_action=False,
    )
    assert follow_up.attack_roll is not None and follow_up.attack_roll.mode.value == "advantage"
    assert target.active_modifiers == []


def test_unused_worg_rider_expires_at_worg_turn_start() -> None:
    worg = _worg()
    target = build_combatant_state(build_karnok_stoneward().model_copy(deep=True))
    apply_hit_modifier_effects(target, "worg", worg.weapon_attack)
    assert len(target.active_modifiers) == 1
    assert expire_source_turn_start_modifiers([target], "other") == 0
    assert expire_source_turn_start_modifiers([target], "worg") == 1
    assert target.active_modifiers == []
