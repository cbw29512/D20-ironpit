from app.combat.attacks import resolve_attack
from app.combat.dice import FixedDiceProvider
from app.combat.modifier_stack import next_attack_against_advantage_sources
from app.content.fighter_progression import build_karnok_stoneward_level
from app.content.pregens import build_brom_ironmark, build_mara_quickstep
from app.domain.models import CombatantState


def _state(template):
    return CombatantState(template=template, current_hp=template.max_hp)


def test_python_miss_keeps_graze_before_studied_attacks() -> None:
    template = build_karnok_stoneward_level(12)
    features = template.progression_features.model_copy(update={
        "studied_attacks": True,
        "tactical_master_sap_weapon_ids": [],
    })
    attacker = _state(template.model_copy(update={"progression_features": features}))
    target = _state(build_brom_ironmark())

    event = resolve_attack(
        1, 1, attacker, target, attacker.template.weapon_attack, 5,
        FixedDiceProvider([2]), spend_action=False,
    )

    assert event.hit is False
    assert event.damage_roll is not None and event.damage_roll.total > 0
    assert "Graze deals" in event.description
    assert "Studied Attacks primes" in event.description
    assert next_attack_against_advantage_sources(attacker, target.template.id) == 1


def test_python_tactical_master_sap_replaces_native_mastery_on_hit() -> None:
    attacker = _state(build_karnok_stoneward_level(9))
    target = _state(build_brom_ironmark())

    event = resolve_attack(
        1, 1, attacker, target, attacker.template.weapon_attack, 5,
        FixedDiceProvider([15, 4, 4]), spend_action=False,
    )

    assert event.hit is True
    assert any(effect.effect_id == "tactical-master-sap" for effect in target.timed_effects)
    assert "Tactical Master applies Sap" in event.description
    assert "Vex primes" not in event.description


def test_python_vex_hit_still_primes_the_next_attack() -> None:
    template = build_mara_quickstep().model_copy(update={"weapon_masteries": ["shortsword", "shortbow"]})
    attacker = _state(template)
    target = _state(build_brom_ironmark())

    event = resolve_attack(
        1, 1, attacker, target, attacker.template.weapon_attack, 5,
        FixedDiceProvider([15, 4]), spend_action=False,
    )

    assert event.hit is True
    assert "Vex primes" in event.description
    assert next_attack_against_advantage_sources(attacker, target.template.id) == 1
