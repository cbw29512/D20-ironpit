from app.combat.persistent_spell_attacks import resolve_persistent_spell_attack
from app.combat.state import begin_turn, build_combatant_state
from app.content.arena_map import build_standard_iron_pit_map
from app.content.build_audit import assert_character_build_raw_ready
from app.content.roster import build_arena_roster
from app.content.character_resource_audit import assert_character_resources_raw_ready
from app.content.cleric_2014_spell_package import build_cleric_2014_spell_package
from app.content.cleric_life_2014_combat_profile import build_seraphine_2014_combat_profile
from app.content.cleric_life_2014_profile import build_seraphine_dawnshield_2014_profile
from app.content.cleric_life_2014_runtime import build_seraphine_dawnshield_2014
from app.content.pregen_combat_audit import assert_pregen_combat_stats
from app.combat.dice import FixedDiceProvider
from app.domain.encounters import EncounterCombatant, EncounterSetup
from app.domain.grid import GridPosition


def _monster_template(template_id: str):
    try:
        return next(
            item for item in build_arena_roster("2014").monsters
            if item.id == template_id
        )
    except StopIteration as exc:
        raise ValueError(f"Missing certified 2014 monster template: {template_id}") from exc


def _member(template, combatant_id: str, side: str, x: int, y: int) -> EncounterCombatant:
    member = EncounterCombatant(
        combatant_id=combatant_id,
        side=side,
        position_ft=x * 5,
        state=build_combatant_state(template),
    )
    member.state.position = GridPosition(x=x, y=y)
    return member


def _resource(member: EncounterCombatant, resource_id: str) -> int:
    return next(
        item.current_uses for item in member.state.resources
        if item.id == resource_id
    )


def test_level_three_advances_the_same_seraphine_foundation() -> None:
    level_one = build_seraphine_dawnshield_2014_profile(1)
    level_two = build_seraphine_dawnshield_2014_profile(2)
    level_three = build_seraphine_dawnshield_2014_profile(3)

    assert [level_one.character_name, level_two.character_name, level_three.character_name] == [
        "Seraphine Dawnshield",
        "Seraphine Dawnshield",
        "Seraphine Dawnshield",
    ]
    assert level_three.base_ability_scores == level_one.base_ability_scores
    assert level_three.species_increases == level_one.species_increases
    assert level_three.advancement_increases == level_two.advancement_increases == []
    assert level_three.species_id == level_two.species_id == level_one.species_id == "hill-dwarf"
    assert level_three.background_id == level_two.background_id == level_one.background_id == "acolyte"
    assert level_three.subclass_id == level_two.subclass_id == level_one.subclass_id == "life-domain"
    assert level_three.class_equipment == level_two.class_equipment == level_one.class_equipment
    assert level_three.feature_audits == level_two.feature_audits
    assert level_three.source_references[:-1] == level_two.source_references
    assert level_three.source_references[-1] == "D&D Basic Rules 2014: Cleric level 3"


def test_level_three_spell_package_preserves_prior_choices_and_adds_legal_delta() -> None:
    package = build_cleric_2014_spell_package(3, 3)

    assert [spell.id for spell in package.spells] == [
        "healing-word",
        "guiding-bolt",
        "shield-of-faith",
        "inflict-wounds",
        "sanctuary",
        "aid",
    ]
    assert [spell.id for spell in package.always_prepared_spells] == [
        "bless",
        "cure-wounds",
        "lesser-restoration",
        "spiritual-weapon",
    ]


def test_level_three_runtime_and_fingerprint_match_persistent_progression() -> None:
    hero = build_seraphine_dawnshield_2014(3)
    profile = build_seraphine_dawnshield_2014_profile(3)
    combat = build_seraphine_2014_combat_profile(3)

    assert hero.max_hp == 30
    assert hero.armor_class == 16
    assert {item.id: item.max_uses for item in hero.resources} == {
        "spell-slot-1": 4,
        "spell-slot-2": 2,
        "channel-divinity": 1,
    }
    assert [item.id for item in hero.condition_removal_actions] == ["lesser-restoration"]
    assert [item.id for item in hero.persistent_spell_attack_actions] == ["spiritual-weapon"]
    spiritual = hero.persistent_spell_attack_actions[0]
    assert spiritual.duration_rounds == 10
    assert spiritual.move_ft == 20
    assert spiritual.attack_reach_ft == 5
    assert spiritual.attack.damage_dice_count == 1
    assert spiritual.attack.damage_dice_size == 8
    assert spiritual.attack.damage_bonus == 3
    assert spiritual.attack.damage_type == "force"

    assert_character_build_raw_ready(profile, hero)
    assert_pregen_combat_stats(hero, combat)
    assert_character_resources_raw_ready(hero, profile, combat)


def test_spiritual_weapon_cast_repeat_move_and_expiry_use_shared_runtime() -> None:
    cleric = _member(build_seraphine_dawnshield_2014(3), "cleric", "heroes", 0, 6)
    goblin = _member(_monster_template("2014-skeleton"), "goblin", "monsters", 8, 6)
    setup = EncounterSetup(
        heroes=[cleric],
        monsters=[goblin],
        hero_total_levels=3,
        monster_total_cr="1/4",
        ruleset="2014",
        map_definition=build_standard_iron_pit_map(),
    )

    begin_turn(cleric.state)
    cast = resolve_persistent_spell_attack(
        1, 1, cleric, setup, "1:cleric", FixedDiceProvider([10, 4]),
    )
    assert cast is not None
    assert cast.feature_id == "spiritual-weapon"
    assert cast.hit is True
    assert cast.damage_roll is not None and cast.damage_roll.total == 7
    assert cast.movement_ft is not None and cast.movement_ft <= 60
    assert cleric.state.action_available is True
    assert cleric.state.bonus_action_available is False
    assert _resource(cleric, "spell-slot-2") == 1
    assert cleric.state.spell_slot_expended_turn_key == "1:cleric"
    assert len(cleric.state.persistent_spell_attacks) == 1
    active = cleric.state.persistent_spell_attacks[0]
    assert active.slot_level == 2
    assert active.expires_round == 11

    goblin.state.position = GridPosition(x=12, y=6)
    goblin.position_ft = 60
    begin_turn(cleric.state)
    slot_before = _resource(cleric, "spell-slot-2")
    repeated = resolve_persistent_spell_attack(
        2, 2, cleric, setup, "2:cleric", FixedDiceProvider([10, 5]),
    )
    assert repeated is not None
    assert repeated.feature_id == "spiritual-weapon"
    assert repeated.movement_ft is not None and repeated.movement_ft <= 20
    assert cleric.state.action_available is True
    assert cleric.state.bonus_action_available is False
    assert _resource(cleric, "spell-slot-2") == slot_before
    assert cleric.state.spell_slot_expended_turn_key == "1:cleric"

    next(item for item in cleric.state.resources if item.id == "spell-slot-2").current_uses = 0
    begin_turn(cleric.state)
    expired = resolve_persistent_spell_attack(
        3, 11, cleric, setup, "11:cleric", FixedDiceProvider([]),
    )
    assert expired is None
    assert cleric.state.persistent_spell_attacks == []
