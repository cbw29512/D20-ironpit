import re

from app.content.monster_source_attack_rider_text import attack_rider_text
from app.content.monster_source_attack_riders import parse_attack_riders


def test_charge_conditioned_prone_is_not_promoted_to_unconditional_hit_rider() -> None:
    text = (
        "If the target is Medium or smaller and the boar moved 20+ feet straight toward "
        "it immediately before the hit, the target has the Prone condition."
    )

    effects = parse_attack_riders(text)

    assert all(effect.kind != "prone" for effect in effects)


def test_unconditional_prone_still_compiles_as_hit_rider() -> None:
    effects = parse_attack_riders("The target has the Prone condition.")

    assert [effect.kind for effect in effects] == ["prone"]


def test_out_of_match_repeat_save_keeps_initial_combat_condition() -> None:
    text = (
        "Constitution Saving Throw: DC 12. First Failure: The target has the Poisoned condition. "
        "While Poisoned, the target's Hit Point maximum doesn't return to normal when finishing a Long Rest, "
        "and it repeats the save every 24 hours that elapse, ending the effect on itself on a success."
    )

    effects = parse_attack_riders(text)

    assert len(effects) == 1
    save = effects[0]
    assert save.kind == "saving-throw"
    assert save.save_ability == "constitution"
    assert save.dc == 12
    assert len(save.failure_effects) == 1
    condition = save.failure_effects[0]
    assert condition.kind == "condition"
    assert condition.condition == "poisoned"
    assert condition.expiry_timing is None
    assert condition.repeat_save_timing is None


def test_in_combat_staged_save_does_not_use_out_of_match_fallback() -> None:
    text = (
        "Wisdom Saving Throw: DC 13. First Failure: The target has the Frightened condition. "
        "The target repeats the save at the end of its next turn, ending the effect on a success. "
        "Second Failure: The target has the Stunned condition."
    )

    effects = parse_attack_riders(text)

    assert len(effects) == 1
    save = effects[0]
    condition = save.failure_effects[0]
    assert condition.repeat_save_timing == "target_turn_end"
    assert condition.repeat_save_failure_condition == "stunned"

def test_self_next_attack_advantage_compiles_with_source_turn_end_expiry() -> None:
    try:
        effects = parse_attack_riders(
            "Hit: 13 (2d8 + 4) Piercing damage, and the pirate has Advantage "
            "on the next attack roll it makes before the end of this turn."
        )

        modifier = next(effect for effect in effects if effect.kind == "next-attack-advantage")
        assert modifier.recipient == "source"
        assert modifier.expires_at_end_of_current_turn is True
        assert modifier.expires_at_end_of_source_turn is False
        assert modifier.expires_at_start_of_source_turn is False
        assert modifier.expires_at_end_of_target_turn is False
    except Exception:
        raise


def test_grapple_escape_disadvantage_continuation_is_preserved() -> None:
    try:
        actions = (
            "Pseudopod. Melee Attack Roll: +5, reach 5 ft. Hit: 7 (1d8 + 3) Bludgeoning damage. "
            "If the target is a Large or smaller creature, it has the Grappled condition (escape DC 13). "
            "Ability checks made to escape this grapple have Disadvantage."
        )
        match = re.search(
            r"Pseudopod\.\s+Melee Attack Roll:.*?Hit:\s*7\s*\(1d8 \+ 3\)\s*Bludgeoning damage(?P<tail>[^.]*)\.",
            actions,
            re.IGNORECASE,
        )
        assert match is not None

        rider_text = attack_rider_text(actions, match)
        effects = parse_attack_riders(rider_text)
        grapple = next(effect for effect in effects if effect.kind == "grapple")

        assert grapple.escape_dc == 13
        assert grapple.escape_check_disadvantage is True
    except Exception:
        raise
