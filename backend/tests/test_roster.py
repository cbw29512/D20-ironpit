from app.content.audited_fighter import build_karnok_stoneward
from app.content.demo import build_goblin_warrior


def test_demo_templates_use_canonical_fighter_identity() -> None:
    fighter = build_karnok_stoneward()
    monster = build_goblin_warrior()

    assert fighter.id == "karnok-stoneward-l1"
    assert fighter.name == "Karnok Stoneward"
    assert fighter.archetype == "Fighter"
    assert fighter.level == 1
    assert fighter.armor_class == 17
    assert fighter.max_hp == 12
    assert fighter.weapon_attack.weapon.name == "Greatsword"
    assert fighter.fighting_style == "Defense"
    assert len(fighter.weapon_masteries) == 3
    assert fighter.visual.off_hand is None

    assert monster.id == "srd-goblin-warrior"
    assert monster.archetype == "Goblin Warrior"
    assert monster.challenge_rating == "1/4"
    assert monster.max_hp == 10
    assert monster.weapon_attack.weapon.name == "Scimitar"
    assert monster.visual.off_hand == "shield"