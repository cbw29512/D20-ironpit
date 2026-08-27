from app.combat.damage import resolve_weapon_damage
from app.combat.dice import FixedDiceProvider
from app.combat.multiattack import resolve_multiattack_action
from app.combat.state import build_combatant_state
from app.content.gladiators import build_vera_ash
from app.content.srd_monsters import build_tough_boss
from app.domain.models import BattlefieldState, RollMode


def test_tough_boss_core_stat_block_and_multiattack() -> None:
    boss = build_combatant_state(build_tough_boss())
    fighter = build_combatant_state(build_vera_ash())
    battlefield = BattlefieldState(distance_ft=5)

    events = resolve_multiattack_action(
        1,
        1,
        boss,
        fighter,
        battlefield,
        FixedDiceProvider([14, 4, 5, 15, 4, 5]),
    )
    attacks = [event for event in events if event.event_type == "attack"]

    assert boss.template.challenge_rating == "4"
    assert boss.template.armor_class == 16
    assert boss.template.max_hp == 82
    assert boss.template.attacks_per_action == 1
    assert boss.template.multiattack is not None
    assert boss.template.multiattack.attack_count == 2
    assert [event.weapon_id for event in attacks] == ["warhammer", "heavy-crossbow"]
    assert [event.damage_applied for event in attacks] == [12, 11]
    assert battlefield.distance_ft == 15


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
