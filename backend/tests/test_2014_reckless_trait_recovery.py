from app.combat.reckless_attack import (
    activate_reckless_attack,
    attacks_against_reckless_advantage,
    reckless_attack_advantage,
)
from app.combat.state import build_combatant_state
from app.content.capability_compiler import compile_combatant
from app.content.monster_basic_candidates_2014 import basic_blockers_2014, unsupported_traits_2014
from app.content.monster_definition_adapter_2014 import adapt_basic_monster_2014
from app.content.monster_source_2014 import load_monster_source_2014
from app.domain.traits import CombatTrait

_RECKLESS_IDS = ("berserker", "minotaur")


def _source():
    return {monster.id: monster for monster in load_monster_source_2014()}


def _template(monster_id: str):
    monster = _source()[monster_id]
    assert basic_blockers_2014(monster) == ()
    return compile_combatant(adapt_basic_monster_2014(monster))


def test_reckless_monsters_bind_to_shared_strength_melee_runtime() -> None:
    for monster_id in _RECKLESS_IDS:
        template = _template(monster_id)
        attacks = [template.weapon_attack, *template.alternate_weapon_attacks]
        assert CombatTrait.RECKLESS in template.combat_traits
        assert attacks
        assert all(attack.attack_ability == "strength" for attack in attacks)
        assert all(attack.weapon.attack_kind.value == "melee" for attack in attacks)

        state = build_combatant_state(template)
        assert activate_reckless_attack(state, template.weapon_attack, template.id, 1) is True
        assert reckless_attack_advantage(state, template.weapon_attack) == 1
        assert attacks_against_reckless_advantage(state) == 1


def test_minotaur_recall_and_winter_wolf_camouflage_are_flat_arena_neutral() -> None:
    source = _source()
    minotaur = source["minotaur"]
    winter_wolf = source["winter-wolf"]
    assert "Labyrinthine Recall" in minotaur.trait_names
    assert "Snow Camouflage" in winter_wolf.trait_names
    assert basic_blockers_2014(minotaur) == ()
    assert basic_blockers_2014(winter_wolf) == ()

    winter_template = compile_combatant(adapt_basic_monster_2014(winter_wolf))
    assert CombatTrait.PACK_TACTICS in winter_template.combat_traits
    assert CombatTrait.RECKLESS not in winter_template.combat_traits


def test_yeti_stays_blocked_by_fear_of_fire() -> None:
    yeti = _source()["yeti"]
    unsupported = set(unsupported_traits_2014(yeti))
    assert "Snow Camouflage" not in unsupported
    assert "Fear of Fire" in unsupported
    assert "source:trait" in basic_blockers_2014(yeti)
