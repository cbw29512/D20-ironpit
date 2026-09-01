from app.content.legacy_monster_roster import build_legacy_monster_templates
from app.content.monster_catalog import load_monster_rows
from app.content.monster_source_audit import audit_monster_source
from app.domain.models import DamageType
from app.domain.traits import CombatTrait


def _template(name: str):
    matches = [item for item in build_legacy_monster_templates() if item.name == name]
    assert len(matches) == 1
    return matches[0]


def _row(name: str) -> dict[str, object]:
    matches = [row for row in load_monster_rows() if row["name"] == name]
    assert len(matches) == 1
    return matches[0]


def test_zombie_candidate_is_source_complete() -> None:
    zombie = _template("Zombie")
    assert (zombie.armor_class, zombie.max_hp, zombie.speed_ft, zombie.initiative_bonus) == (8, 15, 20, -2)
    assert zombie.challenge_rating == "1/4"
    assert (zombie.weapon_attack.attack_bonus, zombie.weapon_attack.weapon.dice_count,
            zombie.weapon_attack.weapon.dice_size, zombie.weapon_attack.damage_bonus) == (3, 1, 8, 1)
    assert zombie.weapon_attack.weapon.damage_type is DamageType.BLUDGEONING
    assert CombatTrait.UNDEAD_FORTITUDE in zombie.combat_traits
    assert zombie.damage_immunities == [DamageType.POISON]
    assert set(zombie.condition_immunities) == {"exhaustion", "poisoned"}
    assert audit_monster_source(zombie, _row("Zombie")) == []


def test_ogre_zombie_candidate_is_source_complete() -> None:
    zombie = _template("Ogre Zombie")
    assert (zombie.armor_class, zombie.max_hp, zombie.speed_ft, zombie.initiative_bonus) == (8, 85, 30, -2)
    assert zombie.challenge_rating == "2"
    assert (zombie.weapon_attack.attack_bonus, zombie.weapon_attack.weapon.dice_count,
            zombie.weapon_attack.weapon.dice_size, zombie.weapon_attack.damage_bonus) == (6, 2, 8, 4)
    assert zombie.weapon_attack.weapon.damage_type is DamageType.BLUDGEONING
    assert CombatTrait.UNDEAD_FORTITUDE in zombie.combat_traits
    assert zombie.damage_immunities == [DamageType.POISON]
    assert set(zombie.condition_immunities) == {"exhaustion", "poisoned"}
    assert audit_monster_source(zombie, _row("Ogre Zombie")) == []
