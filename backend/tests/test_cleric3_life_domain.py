from app.combat.cleric_channel_divinity import resolve_channel_divinity
from app.combat.cleric_channel_policy import choose_channel_divinity
from app.combat.dice import FixedDiceProvider
from app.combat.hit_points import effective_max_hp
from app.combat.precombat_spells import prepare_defenses
from app.combat.state import build_combatant_state
from app.content.audited_cleric import build_seraphine_dawnshield_level_three
from app.content.audited_cleric_life_profile import build_seraphine_dawnshield_level3_profile
from app.content.audited_fighter import build_karnok_stoneward
from app.content.build_audit import assert_character_build_raw_ready
from app.content.canonical_spell_packages import build_class_spell_package
from app.content.character_resource_audit import assert_character_resources_raw_ready
from app.content.pregen_combat_audit import assert_pregen_combat_stats
from app.content.pregen_combat_profiles import build_pregen_combat_profiles
from app.domain.encounters import EncounterCombatant, EncounterSetup
from app.domain.traits import CombatTrait


def _member(template, combatant_id: str, side: str, position: int) -> EncounterCombatant:
    return EncounterCombatant(
        combatant_id=combatant_id, side=side, position_ft=position,
        state=build_combatant_state(template),
    )


def _resource(member: EncounterCombatant, resource_id: str) -> int:
    return next(item.current_uses for item in member.state.resources if item.id == resource_id)


def test_level_three_build_and_spell_package_are_complete_without_counting_domain_spells_against_prepared_slots() -> None:
    template = build_seraphine_dawnshield_level_three()
    profile = build_seraphine_dawnshield_level3_profile()
    combat = build_pregen_combat_profiles()[template.id]
    package = build_class_spell_package("cleric", 3)

    assert (template.level, template.max_hp, template.armor_class) == (3, 24, 17)
    assert {item.id: item.max_uses for item in template.resources} == {
        "spell-slot-1": 4, "spell-slot-2": 2, "channel-divinity": 2,
        "adrenaline-rush": 2, "relentless-endurance": 1,
    }
    assert [spell.id for spell in package.spells] == [
        "guiding-bolt", "shield-of-faith", "healing-word",
        "detect-magic", "create-or-destroy-water", "augury",
    ]
    assert [spell.id for spell in package.always_prepared_spells] == ["bless", "cure-wounds", "aid", "lesser-restoration"]
    assert CombatTrait.LIFE_DOMAIN in template.combat_traits
    assert [action.id for action in template.defensive_spell_actions] == ["aid", "bless", "shield-of-faith"]
    assert [action.id for action in template.condition_removal_actions] == ["lesser-restoration"]
    assert {action.id: action.healing_bonus for action in template.healing_actions} == {"cure-wounds": 6, "healing-word": 6}
    assert {"life-domain", "disciple-of-life", "aid", "lesser-restoration", "preserve-life"}.issubset(
        {feature.feature_id for feature in profile.feature_audits}
    )
    assert_character_build_raw_ready(profile, template)
    assert_pregen_combat_stats(template, combat)
    assert_character_resources_raw_ready(template, profile, combat)


def test_aid_raises_current_and_max_hp_for_three_legal_targets_and_spends_only_level_two_slot() -> None:
    cleric = _member(build_seraphine_dawnshield_level_three(), "cleric", "heroes", 0)
    fighter_a = _member(build_karnok_stoneward(), "fighter-a", "heroes", 5)
    fighter_b = _member(build_karnok_stoneward(), "fighter-b", "heroes", 5)
    enemy = _member(build_karnok_stoneward(), "enemy", "monsters", 10)
    setup = EncounterSetup(heroes=[cleric, fighter_a, fighter_b], monsters=[enemy], hero_total_levels=5, monster_total_cr="1")

    events, _ = prepare_defenses(setup)
    assert events[0].feature_id == "aid"
    assert _resource(cleric, "spell-slot-2") == 1
    assert _resource(cleric, "spell-slot-1") == 4
    for target in (cleric, fighter_a, fighter_b):
        assert target.state.max_hp_bonus == 5
        assert effective_max_hp(target.state) == target.state.template.max_hp + 5
        assert target.state.current_hp == effective_max_hp(target.state)


def test_preserve_life_uses_fifteen_point_pool_and_never_heals_above_half_effective_max() -> None:
    cleric = _member(build_seraphine_dawnshield_level_three(), "cleric", "heroes", 0)
    downed = _member(build_karnok_stoneward(), "downed", "heroes", 5)
    hurt = _member(build_karnok_stoneward(), "hurt", "heroes", 5)
    enemy = _member(build_karnok_stoneward(), "enemy", "monsters", 10)
    cleric.state.current_hp = 4
    downed.state.current_hp = 0
    downed.state.is_unconscious = True
    hurt.state.current_hp = 1
    setup = EncounterSetup(heroes=[cleric, downed, hurt], monsters=[enemy], hero_total_levels=5, monster_total_cr="1")

    choice = choose_channel_divinity(cleric, setup)
    assert choice is not None and choice.kind == "preserve-life"
    events, sequence = resolve_channel_divinity(1, 1, cleric, setup, choice, FixedDiceProvider([]))

    assert sequence == 2 and events[0].feature_id == "preserve-life"
    assert (downed.state.current_hp, hurt.state.current_hp, cleric.state.current_hp) == (6, 6, 8)
    assert all(member.state.current_hp <= effective_max_hp(member.state) // 2 for member in (downed, hurt, cleric))
    assert downed.state.is_unconscious is False
    assert _resource(cleric, "channel-divinity") == 1
    assert cleric.state.action_available is False


def test_aid_bonus_changes_bloodied_and_healing_ceiling_semantics() -> None:
    cleric = _member(build_seraphine_dawnshield_level_three(), "cleric", "heroes", 0)
    cleric.state.max_hp_bonus = 5
    cleric.state.current_hp = 14
    assert effective_max_hp(cleric.state) == 29
    from app.combat.bloodied import is_bloodied
    from app.combat.zero_hp import restore_hit_points
    assert is_bloodied(cleric.state) is True
    assert restore_hit_points(cleric.state, 99) == 15
    assert cleric.state.current_hp == 29


def test_lesser_restoration_is_printed_level_two_bonus_action_spell_removal() -> None:
    action = build_seraphine_dawnshield_level_three().condition_removal_actions[0]
    assert action.action_cost == "bonus_action"
    assert action.range_ft == 5
    assert action.max_conditions_per_use == 1
    assert action.removable_conditions == ["blinded", "deafened", "paralyzed", "poisoned"]
    assert action.resource_costs == {"spell-slot-2": 1}
    assert action.expends_spell_slot is True
