from __future__ import annotations

from app.combat.attack_damage_type_choice import choose_attack_damage_type
from app.combat.dice import FixedDiceProvider
from app.combat.healing import resolve_healing
from app.combat.state import build_combatant_state
from app.content.demo import build_goblin_warrior
from app.content.monk_open_hand_2024_combat_profile import build_kael_2024_combat_profiles
from app.content.monk_open_hand_2024_profile import build_kael_stillwater_2024_profile
from app.content.monk_open_hand_2024_runtime import build_kael_stillwater_2024
from app.domain.encounters import EncounterCombatant
from app.domain.models import DamageType


def test_2024_monk_level_six_snapshot_and_empowered_strikes() -> None:
    try:
        profile = build_kael_stillwater_2024_profile(6)
        monk = build_kael_stillwater_2024(6)
        row = build_kael_2024_combat_profiles(6)[-1]
        resources = {item.id: item.max_uses for item in monk.resources}

        assert profile.final_ability_scores is not None
        assert profile.final_ability_scores.dexterity == 19
        assert monk.max_hp == 45
        assert monk.armor_class == 14
        assert monk.speed_ft == 45
        assert monk.initiative_bonus == 7
        assert monk.weapon_attack.weapon.dice_size == 8
        assert monk.weapon_attack.weapon.damage_type == DamageType.BLUDGEONING
        assert monk.weapon_attack.weapon.damage_type_choices == [DamageType.FORCE]
        assert resources == {
            "focus-points": 6,
            "uncanny-metabolism": 1,
            "wholeness-of-body": 1,
        }
        assert row.level == 6
        assert row.speed_ft == 45
        assert row.resources == (
            ("focus-points", 6),
            ("uncanny-metabolism", 1),
            ("wholeness-of-body", 1),
        )
    except Exception as exc:
        raise RuntimeError("2024 Monk level 6 snapshot certification failed.") from exc


def test_empowered_strikes_chooses_effective_legal_damage_type() -> None:
    try:
        monk = build_kael_stillwater_2024(6)
        target = build_goblin_warrior().model_copy(
            update={"damage_immunities": [DamageType.BLUDGEONING]}
        )
        target_state = build_combatant_state(target)
        chosen = choose_attack_damage_type(monk.weapon_attack, target_state)
        assert chosen == DamageType.FORCE

        force_immune = target.model_copy(
            update={
                "damage_immunities": [DamageType.FORCE],
                "damage_resistances": [],
            }
        )
        chosen_normal = choose_attack_damage_type(
            monk.weapon_attack,
            build_combatant_state(force_immune),
        )
        assert chosen_normal == DamageType.BLUDGEONING
    except Exception as exc:
        raise RuntimeError("Universal attack damage type choice regression failed.") from exc


def test_wholeness_of_body_uses_shared_bonus_action_healing_and_resource() -> None:
    try:
        template = build_kael_stillwater_2024(6)
        member = EncounterCombatant(
            combatant_id="hero-1:kael-stillwater-l6",
            side="heroes",
            position_ft=5,
            state=build_combatant_state(template),
        )
        member.state.current_hp = 20
        action = next(item for item in template.healing_actions if item.id == "wholeness-of-body")
        event = resolve_healing(
            1,
            1,
            member,
            member,
            action,
            FixedDiceProvider([8]),
            "1:hero-1:kael-stillwater-l6",
        )

        resource = next(item for item in member.state.resources if item.id == "wholeness-of-body")
        assert event.feature_id == "wholeness-of-body"
        assert event.healing_roll is not None
        assert event.healing_roll.total == 8
        assert member.state.current_hp == 28
        assert member.state.bonus_action_available is False
        assert resource.current_uses == 0
    except Exception as exc:
        raise RuntimeError("2024 Wholeness of Body healing regression failed.") from exc
