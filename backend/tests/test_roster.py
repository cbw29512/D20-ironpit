from app.main import get_demo_roster


def test_demo_roster_exposes_render_metadata() -> None:
    roster = get_demo_roster()

    assert roster.fighter.id == "aldric-vane-l1"
    assert roster.fighter.archetype == "Fighter"
    assert roster.fighter.level == 1
    assert roster.fighter.max_hp == 12
    assert roster.fighter.weapon_attack.weapon.name == "Longsword"
    assert roster.fighter.visual.off_hand == "shield"

    assert roster.monster.id == "srd-goblin-warrior"
    assert roster.monster.archetype == "Goblin Warrior"
    assert roster.monster.challenge_rating == "1/4"
    assert roster.monster.max_hp == 10
    assert roster.monster.weapon_attack.weapon.name == "Scimitar"
    assert roster.monster.visual.off_hand == "shield"
