from app.combat.policy import preferred_approach_distance, select_weapon_attack
from app.combat.state import build_combatant_state
from app.content.demo import build_demo_fighter, build_goblin_warrior
from app.domain.models import DuelMode, WeaponAttackKind


def test_melee_mode_prefers_melee_profiles_at_engagement_range() -> None:
    fighter = build_combatant_state(build_demo_fighter())
    goblin = build_combatant_state(build_goblin_warrior())

    assert select_weapon_attack(fighter, 5, DuelMode.MELEE).weapon.id == "longsword"
    assert select_weapon_attack(goblin, 5, DuelMode.MELEE).weapon.id == "scimitar"


def test_ranged_mode_uses_available_ranged_profiles() -> None:
    fighter = build_combatant_state(build_demo_fighter())
    goblin = build_combatant_state(build_goblin_warrior())

    fighter_attack = select_weapon_attack(fighter, 20, DuelMode.RANGED)
    goblin_attack = select_weapon_attack(goblin, 20, DuelMode.RANGED)

    assert fighter_attack is not None
    assert fighter_attack.weapon.id == "handaxe"
    assert fighter_attack.weapon.attack_kind is WeaponAttackKind.RANGED
    assert goblin_attack is not None
    assert goblin_attack.weapon.id == "shortbow"


def test_ranged_mode_closes_when_no_ranged_profile_exists() -> None:
    template = build_demo_fighter().model_copy(update={"alternate_weapon_attacks": []})
    fighter = build_combatant_state(template)

    assert select_weapon_attack(fighter, 20, DuelMode.RANGED) is None
    assert preferred_approach_distance(fighter, DuelMode.RANGED) == 5


def test_ranged_mode_switches_to_melee_after_engagement() -> None:
    fighter = build_combatant_state(build_demo_fighter())
    goblin = build_combatant_state(build_goblin_warrior())

    assert select_weapon_attack(fighter, 5, DuelMode.RANGED).weapon.id == "longsword"
    assert select_weapon_attack(goblin, 5, DuelMode.RANGED).weapon.id == "scimitar"
