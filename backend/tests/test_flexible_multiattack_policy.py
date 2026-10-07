import logging

import pytest

from app.combat.attack_actions import resolve_attack_action
from app.combat.landing_offense_policy import decide_post_move_offense, attack_action_melee_legal
from app.combat.state import build_combatant_state
from app.content.monsters import build_commoner
from app.domain.actions import AttackActionDefinition, AttackActionSlot
from app.domain.encounters import EncounterCombatant, EncounterSetup
from app.domain.grid import GridPosition
from app.domain.models import DamageType, Weapon, WeaponAttack, WeaponAttackKind

logger = logging.getLogger(__name__)


class RecordingDice:
    def __init__(self):
        try:
            self.calls = []
        except Exception:
            logger.exception("Failed dice fixture initialization.")
            raise

    def roll(self, sides):
        try:
            self.calls.append(sides)
            return 10 if sides == 20 else 1
        except Exception:
            logger.exception("Failed fixed test roll for d%s.", sides)
            raise


def _setup(edition, row, protected, *, fixed=False):
    try:
        blade = WeaponAttack(id="blade", attack_bonus=20, damage_bonus=3, weapon=Weapon(
            id="blade", name="Renamed Blade", attack_kind=WeaponAttackKind.MELEE,
            dice_count=1, dice_size=6, damage_type=DamageType.SLASHING, animation="slash", light=True,
        ))
        bow = WeaponAttack(id="bow", attack_bonus=20, damage_bonus=5, weapon=Weapon(
            id="bow", name="Renamed Bow", attack_kind=WeaponAttackKind.RANGED,
            dice_count=2, dice_size=8, damage_type=DamageType.PIERCING, animation="projectile",
            normal_range_ft=80, long_range_ft=320,
        ))
        slots = [["bow"], ["blade"]] if fixed else [["blade", "bow"], ["blade", "bow"]]
        template = build_commoner().model_copy(update={
            "name": "Arbitrary Source", "ruleset": edition, "max_hp": 200,
            "weapon_attack": blade, "alternate_weapon_attacks": [bow],
            "attack_action": AttackActionDefinition(
                id="source-action", name="Multiattack", is_attack_action=False,
                slots=[AttackActionSlot(attack_ids=ids) for ids in slots],
            ),
        })
        attacker = EncounterCombatant(combatant_id="actor", side="monsters", position_ft=0,
                                      state=build_combatant_state(template))
        attacker.state.position = GridPosition(x=6, y=6)
        attacker.state.formation_row = row
        allies = [attacker]
        target_template = build_commoner().model_copy(update={"ruleset": edition, "max_hp": 200})
        target = EncounterCombatant(combatant_id="target", side="heroes", position_ft=0,
                                    state=build_combatant_state(target_template))
        target.state.position = GridPosition(x=5, y=6)
        if protected:
            guard = EncounterCombatant(combatant_id="guard", side="monsters", position_ft=0,
                                       state=build_combatant_state(target_template))
            guard.state.position = GridPosition(x=6, y=5)
            guard.state.formation_row = "front"
            allies.append(guard)
        setup = EncounterSetup(heroes=[target], monsters=allies, hero_total_levels=1,
                               monster_total_cr="0", ruleset=edition)
        return setup, attacker
    except Exception:
        logger.exception("Failed flexible Multiattack fixture for %s %s.", edition, row)
        raise


@pytest.mark.parametrize("edition", ["2014", "2024"])
@pytest.mark.parametrize("row,protected,distance,weapon,score", [
    ("front", True, 5, "blade", 13), ("back", True, 5, "blade", 13),
    ("back", False, 5, "blade", 13), ("front", False, 20, "bow", 28), ("back", True, 20, "bow", 28),
])
def test_range_choice_preview_and_resolution_agree_without_policy_dice(edition, row, protected, distance, weapon, score):
    try:
        setup, attacker = _setup(edition, row, protected)
        setup.heroes[0].state.position = GridPosition(x=6-distance//5, y=6)
        before = attacker.state.model_dump()
        pick = decide_post_move_offense(attacker, setup, "1:actor")
        assert pick.family == "attack-action"
        assert pick.expected_damage == score
        assert attack_action_melee_legal(attacker, setup) is (weapon == "blade")
        assert attacker.state.model_dump() == before
        dice = RecordingDice()
        events, _ = resolve_attack_action(1, 1, attacker, setup, dice)
        assert [event.weapon_id for event in events if event.event_type == "attack"] == [weapon, weapon]
        assert 100 not in dice.calls
        assert attacker.state.action_available is False
        assert attacker.state.bonus_action_available is True
        assert attacker.state.template.model_dump() == before["template"]
        assert build_combatant_state(attacker.state.template).action_available is True
    except Exception:
        logger.exception("Multiattack row parity failed for %s %s protected=%s.", edition, row, protected)
        raise


def test_fixed_slots_remain_fixed_even_when_the_other_kind_does_more_damage():
    try:
        setup, attacker = _setup("2014", "front", True, fixed=True)
        events, _ = resolve_attack_action(1, 1, attacker, setup, RecordingDice())
        assert [event.weapon_id for event in events if event.event_type == "attack"] == ["bow", "blade"]
    except Exception:
        logger.exception("Fixed printed slots were replaced by row policy.")
        raise


def test_unknown_slot_fails_before_any_action_or_damage_is_spent():
    try:
        setup, attacker = _setup("2014", "front", False)
        attacker.state.template = attacker.state.template.model_copy(update={
            "attack_action": AttackActionDefinition(id="invalid", name="Invalid", slots=[
                AttackActionSlot(attack_ids=["blade"]), AttackActionSlot(attack_ids=["unbound"]),
            ]),
        })
        before = [item.state.model_dump() for item in [*setup.heroes, *setup.monsters]]
        dice = RecordingDice()
        with pytest.raises(ValueError, match="Unknown Multiattack IDs"):
            resolve_attack_action(1, 1, attacker, setup, dice)
        assert not dice.calls
        assert [item.state.model_dump() for item in [*setup.heroes, *setup.monsters]] == before
    except Exception:
        logger.exception("Unknown slot did not fail before mutation.")
        raise


@pytest.mark.parametrize("edition", ["2014", "2024"])
def test_mode_stays_fixed_within_printed_sequence_when_target_moves_into_melee(monkeypatch, edition):
    try:
        from app.combat import attack_actions
        setup, attacker = _setup(edition, "back", True)
        setup.heroes[0].state.position = GridPosition(x=2, y=6)
        original = attack_actions.resolve_encounter_attack
        def after_attack(*args, **kwargs):
            event = original(*args, **kwargs)
            setup.heroes[0].state.position = GridPosition(x=5, y=6)
            return event
        monkeypatch.setattr(attack_actions, "resolve_encounter_attack", after_attack)
        events, _ = resolve_attack_action(1, 1, attacker, setup, RecordingDice())
        assert [event.weapon_id for event in events if event.event_type == "attack"] == ["bow", "bow"]
        from app.combat.attack_action_choices import flexible_attack_mode
        assert flexible_attack_mode(attacker, setup) is WeaponAttackKind.MELEE
    except Exception:
        logger.exception("Multiattack changed its selected source mode mid-Action.")
        raise
