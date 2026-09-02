from app.combat.attacks import resolve_attack
from app.combat.dice import FixedDiceProvider
from app.combat.modifier_stack import expire_source_turn_modifiers, next_attack_against_advantage_sources
from app.combat.studied_attacks import apply_studied_attack_miss, studied_attacks_active
from app.content.fighter_progression import build_karnok_stoneward_level
from app.content.pregens import build_brom_ironmark, build_selene_asharrow
from app.domain.models import CombatantState, RollMode


def _state(template):
    return CombatantState(template=template, current_hp=template.max_hp)


def _studied_karnok():
    template = build_karnok_stoneward_level(12)
    features = template.progression_features.model_copy(update={"studied_attacks": True})
    return _state(template.model_copy(update={"progression_features": features}))


def test_studied_attacks_requires_feature_and_expires_after_next_turn() -> None:
    plain = _state(build_karnok_stoneward_level(12)); studied = _studied_karnok()
    assert studied_attacks_active(plain) is False
    assert apply_studied_attack_miss(plain, "plain", "target", 2) is False
    assert studied_attacks_active(studied) is True
    assert apply_studied_attack_miss(studied, "karnok", "target", 2) is True
    assert next_attack_against_advantage_sources(studied, "target") == 1
    assert expire_source_turn_modifiers([studied], "karnok", 2) == 0
    assert expire_source_turn_modifiers([studied], "karnok", 3) == 1


def test_studied_attacks_graze_miss_primes_and_next_same_target_attack_consumes() -> None:
    karnok = _studied_karnok(); brom = _state(build_brom_ironmark())
    first = resolve_attack(1, 1, karnok, brom, karnok.template.weapon_attack, 5, FixedDiceProvider([2]), spend_action=False)
    assert first.hit is False and first.damage_roll is not None
    assert "Graze deals" in first.description and "Studied Attacks primes" in first.description
    assert next_attack_against_advantage_sources(karnok, brom.template.id) == 1

    second = resolve_attack(2, 1, karnok, brom, karnok.template.weapon_attack, 5, FixedDiceProvider([3, 18, 4, 4]), spend_action=False)
    assert second.attack_roll.mode is RollMode.ADVANTAGE and second.hit is True
    assert next_attack_against_advantage_sources(karnok, brom.template.id) == 0


def test_studied_attacks_other_target_does_not_consume_study() -> None:
    karnok = _studied_karnok(); brom = _state(build_brom_ironmark()); selene = _state(build_selene_asharrow())
    resolve_attack(1, 1, karnok, brom, karnok.template.weapon_attack, 5, FixedDiceProvider([2]), spend_action=False)
    other = resolve_attack(2, 1, karnok, selene, karnok.template.weapon_attack, 5, FixedDiceProvider([15, 4, 4]), spend_action=False)
    assert other.attack_roll.mode is RollMode.NORMAL
    assert next_attack_against_advantage_sources(karnok, brom.template.id) == 1


def test_heroic_inspiration_recovery_to_hit_does_not_prime_studied_attacks() -> None:
    karnok = _studied_karnok(); brom = _state(build_brom_ironmark()); karnok.heroic_inspiration = True
    event = resolve_attack(1, 1, karnok, brom, karnok.template.weapon_attack, 5, FixedDiceProvider([2, 20, 4, 4]), spend_action=False)
    assert event.hit is True and "Heroic Inspiration rerolls" in event.description
    assert "Studied Attacks primes" not in event.description
    assert next_attack_against_advantage_sources(karnok, brom.template.id) == 0
