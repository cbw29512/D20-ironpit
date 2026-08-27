from app.combat.attack_actions import resolve_attack_action
from app.combat.damage import resolve_weapon_damage
from app.combat.dice import FixedDiceProvider
from app.combat.state import build_combatant_state
from app.content.gladiators import build_vera_ash
from app.content.srd_monsters import build_tough_boss
from app.domain.models import RollMode


def test_tough_boss_core_stat_block_and_multiattack() -> None:
    boss = build_combatant_state(build_tough_boss())
    fighter = build_combatant_state(build_vera_ash())

    events = resolve_attack_action(
        1,
        1,
        boss,
        fighter,
        boss.template.weapon_attack,
        5,
        FixedDiceProvider([14, 4, 5, 14, 4, 5]),
    )

    assert boss.template.challenge_rating == "4"
    assert boss.template.armor_class == 16
    assert boss.template.max_hp == 82
    assert boss.template.attacks_per_action == 2
    assert len(events) == 2
    assert [event.damage_applied for event in events] == [12, 12]


def test_tough_boss_crossbow_uses_monster_damage_override() -> None:
    boss = build_combatant_state(build_tough_boss())
    crossbow = boss.template.alternate_weapon_attacks[0]

    total, components = resolve_weapon_damage(
        boss,
        crossbow,
        FixedDiceProvider([10, 1]),
        critical=False,
        attack_mode=RollMode.NORMAL,
    )

    assert crossbow.weapon.name == "Heavy Crossbow"
    assert crossbow.attack_bonus == 4
    assert total.total == 13
    assert components[0].notation == "2d10+2"
