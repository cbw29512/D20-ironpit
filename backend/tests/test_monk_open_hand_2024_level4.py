from __future__ import annotations

from app.combat.attack_damage_reduction import apply_attack_damage_reduction
from app.combat.dice import FixedDiceProvider
from app.combat.state import build_combatant_state
from app.content.monk_open_hand_2024_combat_profile import build_kael_2024_combat_profiles
from app.content.monk_open_hand_2024_profile import build_kael_stillwater_2024_profile
from app.content.monk_open_hand_2024_runtime import build_kael_stillwater_2024
from app.domain.models import DamageRollComponent, DamageType


def test_2024_monk_level_four_asi_and_arena_neutral_slow_fall() -> None:
    try:
        profile = build_kael_stillwater_2024_profile(4)
        monk = build_kael_stillwater_2024(4)
        audits = {item.feature_id: item for item in profile.feature_audits}

        assert profile.final_ability_scores is not None
        assert profile.final_ability_scores.dexterity == 19
        assert [(item.ability, item.amount) for item in profile.advancement_increases] == [("dexterity", 2)]
        assert audits["ability-score-improvement-l4"].combat_relevant is True
        assert audits["ability-score-improvement-l4"].automated is True
        assert audits["slow-fall"].combat_relevant is False
        assert audits["slow-fall"].automated is False
        assert "no falling hazard" in (audits["slow-fall"].notes or "")

        assert monk.max_hp == 31
        assert monk.armor_class == 14
        assert monk.speed_ft == 40
        assert monk.initiative_bonus == 6
        assert monk.weapon_attack is not None
        assert monk.weapon_attack.attack_bonus == 6
        assert monk.weapon_attack.damage_bonus == 4
        assert monk.saving_throw_bonuses["dexterity"] == 6
        assert monk.skill_bonuses["acrobatics"] == 6
        assert {item.id: item.max_uses for item in monk.resources} == {
            "focus-points": 4,
            "uncanny-metabolism": 1,
        }
    except Exception as exc:
        raise RuntimeError("2024 Monk level 4 profile/runtime certification failed.") from exc


def test_2024_monk_level_four_derived_dexterity_reaches_shared_deflect_and_fingerprint() -> None:
    try:
        monk = build_combatant_state(build_kael_stillwater_2024(4))
        component = DamageRollComponent(
            source="test-hit",
            notation="20",
            rolls=[],
            modifier=20,
            damage_type=DamageType.BLUDGEONING,
            total=20,
        )
        result = apply_attack_damage_reduction(
            monk,
            monk.template.weapon_attack,
            [component],
            FixedDiceProvider([4]),
        )
        assert result.used is True
        assert result.reduction == 12  # d10 roll 4 + Dexterity 4 + Monk level 4.

        row = build_kael_2024_combat_profiles(4)[-1]
        assert row.level == 4
        assert row.abilities.dexterity == 19
        assert row.armor_class == 14
        assert row.max_hp == 31
        assert row.initiative_bonus == 6
        assert row.resources == (("focus-points", 4), ("uncanny-metabolism", 1))
    except Exception as exc:
        raise RuntimeError("2024 Monk level 4 derived-stat fingerprint regression failed.") from exc
