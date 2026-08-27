from app.combat.attacks import resolve_attack
from app.combat.condition_timing import expire_turn_conditions
from app.combat.conditions import has_condition
from app.combat.dice import FixedDiceProvider
from app.combat.effects import resolve_on_hit_effects
from app.combat.multiattack import resolve_multiattack_action
from app.combat.state import build_combatant_state
from app.content.demo import build_demo_fighter
from app.content.gladiators import build_mara_stone
from app.content.srd_monsters import build_skeleton
from app.content.srd_undead import build_ghoul
from app.domain.models import BattlefieldState, ConditionExpiry, ConditionType


def _resolve_claw(ghoul, target, dice):
    claw = ghoul.template.alternate_weapon_attacks[0]
    battlefield = BattlefieldState(distance_ft=5)
    attack = resolve_attack(1, 1, ghoul, target, claw, 5, dice)
    effects = resolve_on_hit_effects(
        2, 1, ghoul, target, claw, battlefield, attack, dice
    )
    return attack, effects


def test_ghoul_multiattack_is_two_bites_not_claws() -> None:
    ghoul = build_combatant_state(build_ghoul())
    fighter = build_combatant_state(build_mara_stone())

    events = resolve_multiattack_action(
        1,
        1,
        ghoul,
        fighter,
        BattlefieldState(distance_ft=5),
        FixedDiceProvider([15, 3, 2, 15, 3, 2]),
    )

    attacks = [event for event in events if event.event_type == "attack"]
    assert [event.weapon_id for event in attacks] == ["bite", "bite"]
    assert [event.damage_applied for event in attacks] == [7, 7]


def test_ghoul_claw_failed_save_paralyzes_until_target_turn_end() -> None:
    ghoul = build_combatant_state(build_ghoul(), "ghoul-1")
    fighter = build_combatant_state(build_demo_fighter(), "fighter-1")
    dice = FixedDiceProvider([14, 2, 5])

    attack, effects = _resolve_claw(ghoul, fighter, dice)

    assert attack.hit is True
    assert [event.event_type for event in effects] == ["saving_throw", "condition"]
    assert effects[0].test_dc == 10
    assert effects[0].test_success is False
    paralysis = next(
        item for item in fighter.conditions if item.condition is ConditionType.PARALYZED
    )
    assert paralysis.expires_on is ConditionExpiry.TARGET_TURN_END

    end_events = expire_turn_conditions(4, 2, fighter, [ghoul, fighter], "end")
    assert [event.condition for event in end_events] == [ConditionType.PARALYZED]
    assert not has_condition(fighter, ConditionType.PARALYZED)


def test_ghoul_claw_successful_save_does_not_paralyze() -> None:
    ghoul = build_combatant_state(build_ghoul())
    fighter = build_combatant_state(build_demo_fighter())

    _, effects = _resolve_claw(ghoul, fighter, FixedDiceProvider([14, 2, 6]))

    assert [event.event_type for event in effects] == ["saving_throw"]
    assert effects[0].test_success is True
    assert not has_condition(fighter, ConditionType.PARALYZED)


def test_ghoul_claw_paralysis_excludes_undead() -> None:
    ghoul = build_combatant_state(build_ghoul())
    skeleton = build_combatant_state(build_skeleton())

    _, effects = _resolve_claw(ghoul, skeleton, FixedDiceProvider([10, 2]))

    assert effects == []
    assert not has_condition(skeleton, ConditionType.PARALYZED)


def test_ghoul_claw_paralysis_excludes_elf_tag() -> None:
    ghoul = build_combatant_state(build_ghoul())
    template = build_demo_fighter().model_copy(update={"creature_tags": ["elf"]})
    elf = build_combatant_state(template)

    _, effects = _resolve_claw(ghoul, elf, FixedDiceProvider([14, 2]))

    assert effects == []
    assert not has_condition(elf, ConditionType.PARALYZED)
