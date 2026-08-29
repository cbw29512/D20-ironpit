from app.combat.attacks import resolve_attack
from app.combat.dice import FixedDiceProvider
from app.combat.encounter_setup import build_encounter_setup
from app.domain.models import DamageType, EncounterSelection


def _setup(monster_id: str):
    return build_encounter_setup(EncounterSelection(
        hero_ids=["karnok-stoneward-l1"], monster_ids=[monster_id], starting_distance_ft=5,
    ))


def test_giant_venomous_snake_matches_srd_profile() -> None:
    snake = _setup("srd-giant-venomous-snake").monsters[0].state.template
    bite = snake.weapon_attack
    assert (snake.challenge_rating, snake.armor_class, snake.max_hp, snake.speed_ft, snake.initiative_bonus) == ("1/4", 14, 11, 40, 4)
    assert (bite.attack_bonus, bite.weapon.reach_ft, bite.weapon.dice_count, bite.weapon.dice_size, bite.damage_bonus) == (6, 10, 1, 4, 4)
    assert [(part.dice_count, part.dice_size, part.damage_type) for part in bite.on_hit_damage] == [(1, 8, DamageType.POISON)]


def test_giant_wasp_matches_srd_profile() -> None:
    wasp = _setup("srd-giant-wasp").monsters[0].state.template
    sting = wasp.weapon_attack
    assert (wasp.challenge_rating, wasp.armor_class, wasp.max_hp, wasp.speed_ft, wasp.initiative_bonus) == ("1/2", 13, 22, 50, 2)
    assert (sting.attack_bonus, sting.weapon.dice_size, sting.damage_bonus) == (4, 6, 2)
    assert [(part.dice_count, part.dice_size, part.damage_type) for part in sting.on_hit_damage] == [(2, 4, DamageType.POISON)]


def test_giant_wolf_spider_matches_srd_profile() -> None:
    spider = _setup("srd-giant-wolf-spider").monsters[0].state.template
    bite = spider.weapon_attack
    assert (spider.challenge_rating, spider.armor_class, spider.max_hp, spider.speed_ft, spider.initiative_bonus) == ("1/4", 13, 11, 40, 3)
    assert (bite.attack_bonus, bite.weapon.dice_size, bite.damage_bonus) == (5, 4, 3)
    assert [(part.dice_count, part.dice_size, part.damage_type) for part in bite.on_hit_damage] == [(2, 4, DamageType.POISON)]


def test_venom_damage_respects_poison_immunity_without_erasing_piercing() -> None:
    setup = _setup("srd-giant-wasp")
    hero, wasp = setup.heroes[0], setup.monsters[0]
    hero.state.template.damage_immunities = [DamageType.POISON]
    event = resolve_attack(
        1, 1, wasp.state, hero.state, wasp.state.template.weapon_attack, 5,
        FixedDiceProvider([15, 3, 4, 4]),
        actor_event_id=wasp.combatant_id, target_event_id=hero.combatant_id,
    )
    assert [part.total for part in event.damage_components] == [5, 8]
    assert [part.applied_total for part in event.damage_components] == [5, 0]
    assert event.damage_roll is not None and event.damage_roll.total == 5
