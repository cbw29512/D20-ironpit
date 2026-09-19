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


def test_python_hit_keeps_tactical_sap_and_vex_in_same_attack_outcome() -> None:
    template = build_mara_quickstep()
    features = template.progression_features.model_copy(update={
        "tactical_master_sap_weapon_ids": ["shortsword"],
    })
    attacker = _state(template.model_copy(update={
        "weapon_masteries": ["shortsword"],
        "progression_features": features,
    }))
    target = _state(build_brom_ironmark())

    event = resolve_attack(
        1, 1, attacker, target, attacker.template.weapon_attack, 5,
        FixedDiceProvider([15, 4]), spend_action=False,
    )

    assert event.hit is True
    assert any(effect.effect_id == "tactical-master-sap" for effect in target.timed_effects)
    assert next_attack_against_advantage_sources(attacker, target.template.id) == 1
    assert "Tactical Master applies Sap" in event.description
    assert "Vex primes" in event.description
