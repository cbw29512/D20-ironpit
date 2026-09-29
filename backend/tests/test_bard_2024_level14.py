from __future__ import annotations

from app.combat.ability_checks import resolve_ability_check_outcome
from app.combat.attack_d20_outcome import resolve_attack_d20_outcome
from app.combat.dice import FixedDiceProvider
from app.combat.state import build_combatant_state
from app.content.audited_bard import build_lyra_silverstring_level
from app.content.audited_bard_profile import build_lyra_silverstring_profile
from app.domain.models import DiceRoll, RollMode


def _roll(natural: int, modifier: int) -> DiceRoll:
    try:
        return DiceRoll(
            notation=f"1d20+{modifier}",
            rolls=[natural],
            selected_roll=natural,
            modifier=modifier,
            total=natural + modifier,
            mode=RollMode.NORMAL,
        )
    except Exception:
        raise


def _inspiration(state) -> int:
    try:
        return next(
            item.current_uses for item in state.resources
            if item.id == "bardic-inspiration"
        )
    except Exception:
        raise


def test_2024_bard_level_fourteen_peerless_skill_profile() -> None:
    profile = build_lyra_silverstring_profile(14)
    hero = build_lyra_silverstring_level(14)

    assert hero.max_hp == 73
    audit = next(item for item in profile.feature_audits if item.feature_id == "peerless-skill")
    assert audit.automated is True

    rules = hero.progression_features.resource_backed_d20_bonus_dice
    assert len(rules) == 1
    rule = rules[0]
    assert rule.source_id == "peerless-skill"
    assert rule.resource_id == "bardic-inspiration"
    assert rule.dice_size == 10
    assert rule.test_kinds == ["attack", "ability_check"]
    assert rule.consume_only_on_success is True


def test_2024_peerless_skill_check_spends_only_when_bonus_succeeds() -> None:
    state = build_combatant_state(build_lyra_silverstring_level(14))

    revised, succeeded = resolve_ability_check_outcome(
        state,
        "dexterity",
        _roll(5, 5),
        16,
        dice=FixedDiceProvider([6]),
        round_number=1,
    )

    assert succeeded is True
    assert revised.total == 16
    assert "Peerless Skill" in revised.notation
    assert _inspiration(state) == 4


def test_2024_peerless_skill_check_keeps_inspiration_when_bonus_still_fails() -> None:
    state = build_combatant_state(build_lyra_silverstring_level(14))

    revised, succeeded = resolve_ability_check_outcome(
        state,
        "dexterity",
        _roll(5, 5),
        18,
        dice=FixedDiceProvider([2]),
        round_number=1,
    )

    assert succeeded is False
    assert revised.total == 12
    assert "Peerless Skill" in revised.notation
    assert _inspiration(state) == 5


def test_2024_peerless_skill_attack_spends_only_when_bonus_hits() -> None:
    attacker = build_combatant_state(build_lyra_silverstring_level(14))
    defender = build_combatant_state(build_lyra_silverstring_level(1))
    attack = attacker.template.weapon_attack
    assert attack is not None

    outcome = resolve_attack_d20_outcome(
        attacker,
        defender,
        attack,
        _roll(5, attack.attack_bonus),
        12,
        dice=FixedDiceProvider([2]),
    )

    assert outcome.hit is True
    assert outcome.roll.total == 12
    assert "Peerless Skill" in outcome.roll.notation
    assert _inspiration(attacker) == 4


def test_2024_peerless_skill_attack_keeps_inspiration_when_bonus_still_misses() -> None:
    attacker = build_combatant_state(build_lyra_silverstring_level(14))
    defender = build_combatant_state(build_lyra_silverstring_level(1))
    attack = attacker.template.weapon_attack
    assert attack is not None

    outcome = resolve_attack_d20_outcome(
        attacker,
        defender,
        attack,
        _roll(2, attack.attack_bonus),
        15,
        dice=FixedDiceProvider([3]),
    )

    assert outcome.hit is False
    assert outcome.roll.total == 10
    assert "Peerless Skill" in outcome.roll.notation
    assert _inspiration(attacker) == 5
