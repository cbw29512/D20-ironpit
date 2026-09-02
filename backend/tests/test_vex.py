from app.combat.attacks import resolve_attack
from app.combat.dice import FixedDiceProvider
from app.combat.modifier_stack import expire_source_turn_modifiers, next_attack_against_advantage_sources
from app.combat.vex import apply_vex_mastery, vex_mastery_active
from app.content.pregens import build_brom_ironmark, build_mara_quickstep, build_selene_asharrow
from app.domain.models import CombatantState, DamageType, RollMode


def _state(template):
    return CombatantState(template=template, current_hp=template.max_hp)


def _mara():
    template = build_mara_quickstep().model_copy(update={"weapon_masteries": ["shortsword", "shortbow"]})
    return _state(template)


def test_vex_requires_the_weapon_to_be_mastered() -> None:
    plain = _state(build_mara_quickstep())
    mastered = _mara()
    assert vex_mastery_active(plain, plain.template.weapon_attack) is False
    assert vex_mastery_active(mastered, mastered.template.weapon_attack) is True
    assert vex_mastery_active(mastered, mastered.template.alternate_weapon_attacks[0]) is True


def test_vex_hit_primes_only_the_same_target_and_next_roll_consumes_it() -> None:
    mara = _mara(); brom = _state(build_brom_ironmark()); selene = _state(build_selene_asharrow())
    first = resolve_attack(1, 1, mara, brom, mara.template.weapon_attack, 5, FixedDiceProvider([15, 4]), spend_action=False)
    assert first.hit and "Vex primes" in first.description
    assert next_attack_against_advantage_sources(mara, brom.template.id) == 1
    assert next_attack_against_advantage_sources(mara, selene.template.id) == 0

    other = resolve_attack(2, 1, mara, selene, mara.template.weapon_attack, 5, FixedDiceProvider([15, 4]), spend_action=False)
    assert other.attack_roll.mode is RollMode.NORMAL
    assert next_attack_against_advantage_sources(mara, brom.template.id) == 1

    miss = resolve_attack(3, 1, mara, brom, mara.template.weapon_attack, 5, FixedDiceProvider([2, 3]), spend_action=False)
    assert miss.attack_roll.mode is RollMode.ADVANTAGE and miss.hit is False
    assert next_attack_against_advantage_sources(mara, brom.template.id) == 0


def test_vex_chains_when_the_advantaged_attack_hits_and_deals_damage() -> None:
    mara = _mara(); brom = _state(build_brom_ironmark())
    resolve_attack(1, 1, mara, brom, mara.template.weapon_attack, 5, FixedDiceProvider([15, 4]), spend_action=False)
    chained = resolve_attack(2, 1, mara, brom, mara.template.weapon_attack, 5, FixedDiceProvider([3, 18, 5]), spend_action=False)
    assert chained.hit and chained.attack_roll.mode is RollMode.ADVANTAGE
    assert next_attack_against_advantage_sources(mara, brom.template.id) == 1


def test_vex_does_not_trigger_when_defenses_reduce_damage_to_zero() -> None:
    mara = _mara()
    immune_template = build_brom_ironmark().model_copy(update={"damage_immunities": [DamageType.PIERCING]})
    immune = _state(immune_template)
    event = resolve_attack(1, 1, mara, immune, mara.template.weapon_attack, 5, FixedDiceProvider([15, 4]), spend_action=False)
    assert event.hit and event.damage_roll is not None and event.damage_roll.total == 0
    assert next_attack_against_advantage_sources(mara, immune.template.id) == 0


def test_vex_expires_at_end_of_attackers_next_turn() -> None:
    mara = _mara(); attack = mara.template.weapon_attack
    assert apply_vex_mastery(mara, "mara", "target", attack, 2, 1)
    assert next_attack_against_advantage_sources(mara, "target") == 1
    assert expire_source_turn_modifiers([mara], "mara", 2) == 0
    assert next_attack_against_advantage_sources(mara, "target") == 1
    assert expire_source_turn_modifiers([mara], "mara", 3) == 1
    assert next_attack_against_advantage_sources(mara, "target") == 0
