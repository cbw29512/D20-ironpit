from app.combat.attack_actions import resolve_attack_action
from app.combat.dice import FixedDiceProvider
from app.combat.state import build_combatant_state
from app.content.gladiators import build_mara_stone
from app.content.srd_monsters import build_ogre, build_tough_boss
from app.domain.models import BattlefieldState, RollMode, SizeCategory


def test_tough_boss_push_changes_distance_then_reselects_crossbow() -> None:
    boss = build_combatant_state(build_tough_boss())
    mara = build_combatant_state(build_mara_stone())
    battlefield = BattlefieldState(distance_ft=5)

    events = resolve_attack_action(
        1,
        1,
        boss,
        mara,
        battlefield,
        FixedDiceProvider([14, 1, 1, 15, 1, 1]),
    )

    assert [event.event_type for event in events] == ["attack", "forced_movement", "attack"]
    assert [event.sequence for event in events] == [1, 2, 3]
    assert events[0].weapon_id == "warhammer"
    assert events[1].feature_id == "tough-boss-warhammer-push"
    assert events[1].distance_before_ft == 5
    assert events[1].distance_after_ft == 15
    assert events[2].weapon_id == "heavy-crossbow"
    assert events[2].attack_roll is not None
    assert events[2].attack_roll.mode is RollMode.NORMAL
    assert battlefield.distance_ft == 15


def test_tough_boss_miss_does_not_push_target() -> None:
    boss = build_combatant_state(build_tough_boss())
    boss.template.attacks_per_action = 1
    mara = build_combatant_state(build_mara_stone())
    battlefield = BattlefieldState(distance_ft=5)

    events = resolve_attack_action(
        1,
        1,
        boss,
        mara,
        battlefield,
        FixedDiceProvider([1]),
    )

    assert [event.event_type for event in events] == ["attack"]
    assert battlefield.distance_ft == 5


def test_tough_boss_does_not_push_huge_target() -> None:
    boss = build_combatant_state(build_tough_boss())
    boss.template.attacks_per_action = 1
    mara = build_combatant_state(build_mara_stone())
    mara.template.size = SizeCategory.HUGE
    battlefield = BattlefieldState(distance_ft=5)

    events = resolve_attack_action(
        1,
        1,
        boss,
        mara,
        battlefield,
        FixedDiceProvider([14, 1, 1]),
    )

    assert [event.event_type for event in events] == ["attack"]
    assert battlefield.distance_ft == 5


def test_weapon_mastery_metadata_does_not_create_monster_push() -> None:
    ogre = build_combatant_state(build_ogre())
    ogre.template.attacks_per_action = 1
    mara = build_combatant_state(build_mara_stone())
    battlefield = BattlefieldState(distance_ft=5)

    events = resolve_attack_action(
        1,
        1,
        ogre,
        mara,
        battlefield,
        FixedDiceProvider([13, 1, 1]),
    )

    assert ogre.template.weapon_attack.weapon.mastery_property == "push"
    assert ogre.template.weapon_attack.on_hit_effects == []
    assert [event.event_type for event in events] == ["attack"]
    assert battlefield.distance_ft == 5
