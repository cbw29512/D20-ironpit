from app.combat.attack_actions import resolve_attack_action
from app.combat.dice import FixedDiceProvider
from app.combat.state import build_combatant_state
from app.content.gladiators import build_darius_flint, build_vera_ash
from app.content.srd_monsters import build_ogre
from app.domain.models import BattlefieldState


def test_level_eleven_fighter_progression_values() -> None:
    fighter = build_combatant_state(build_darius_flint())

    assert fighter.template.level == 11
    assert fighter.template.max_hp == 92
    assert fighter.template.attacks_per_action == 3
    assert fighter.template.weapon_attack.attack_bonus == 9
    assert fighter.template.weapon_attack.damage_bonus == 5
    assert fighter.resources[0].max_uses == 4


def test_level_twenty_fighter_progression_values_and_four_attacks() -> None:
    fighter = build_combatant_state(build_vera_ash())
    ogre = build_combatant_state(build_ogre())

    events = resolve_attack_action(
        1,
        1,
        fighter,
        ogre,
        BattlefieldState(distance_ft=5),
        FixedDiceProvider([2, 1, 2, 1, 2, 1, 2, 1]),
    )

    assert fighter.template.level == 20
    assert fighter.template.max_hp == 164
    assert fighter.template.weapon_attack.attack_bonus == 11
    assert fighter.resources[0].max_uses == 4
    assert len(events) == 4
    assert ogre.current_hp == 44
