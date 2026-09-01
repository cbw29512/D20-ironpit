from app.combat.dice import FixedDiceProvider
from app.combat.spell_offense import resolve_best_spell_offense
from app.combat.state import build_combatant_state
from app.content.audited_cleric import build_seraphine_dawnshield_level_four
from app.content.audited_cleric_life_profile import build_seraphine_dawnshield_level4_profile
from app.content.audited_fighter import build_karnok_stoneward
from app.content.build_audit import assert_character_build_raw_ready
from app.content.canonical_hero_policy import assert_canonical_profile_policy, canonical_spell_package
from app.content.character_resource_audit import assert_character_resources_raw_ready
from app.content.certified_heroes import build_certified_hero_registry
from app.content.pregen_combat_audit import assert_pregen_combat_stats
from app.content.pregen_combat_profiles import build_pregen_combat_profiles
from app.domain.encounters import EncounterCombatant, EncounterSetup


def _member(template, combatant_id: str, side: str, position: int) -> EncounterCombatant:
    return EncounterCombatant(
        combatant_id=combatant_id,
        side=side,
        position_ft=position,
        state=build_combatant_state(template),
    )


def test_seraphine_level_four_build_and_spell_package_are_raw_audited() -> None:
    template = build_seraphine_dawnshield_level_four()
    profile = build_seraphine_dawnshield_level4_profile()
    combat = build_pregen_combat_profiles()[template.id]
    spells = canonical_spell_package("cleric", 4)

    assert_canonical_profile_policy(profile)
    assert_character_build_raw_ready(profile, template)
    assert_pregen_combat_stats(template, combat)
    assert_character_resources_raw_ready(template, profile, combat)

    assert template.level == 4
    assert template.max_hp == 23
    assert template.saving_throw_bonuses["wisdom"] == 6
    assert template.skill_bonuses["medicine"] == 6
    assert {item.id: item.max_uses for item in template.resources} == {
        "spell-slot-1": 4,
        "spell-slot-2": 3,
        "channel-divinity": 2,
        "adrenaline-rush": 2,
        "relentless-endurance": 1,
    }
    assert [spell.id for spell in spells.cantrips] == ["sacred-flame", "light", "thaumaturgy", "mending"]
    assert [spell.id for spell in spells.spells] == [
        "guiding-bolt", "shield-of-faith", "healing-word", "detect-magic",
        "create-or-destroy-water", "augury", "inflict-wounds",
    ]
    assert [spell.id for spell in spells.always_prepared_spells] == [
        "bless", "cure-wounds", "aid", "lesser-restoration",
    ]
    assert [spell.id for spell in template.spell_save_actions] == ["sacred-flame", "inflict-wounds"]
    inflict = template.spell_save_actions[1]
    assert (inflict.level, inflict.range_ft, inflict.save_ability, inflict.dc) == (1, 5, "constitution", 14)
    assert (inflict.damage_dice_count, inflict.damage_dice_size, inflict.damage_type) == (2, 10, "necrotic")
    assert inflict.success_damage == "half"
    assert template.spell_attack_actions[0].attack_bonus == 6
    assert all(action.healing_bonus == 7 for action in template.healing_actions)


def test_cleric_four_expected_value_uses_inflict_wounds_in_close_combat() -> None:
    caster = _member(build_seraphine_dawnshield_level_four(), "cleric", "heroes", 5)
    target = _member(build_karnok_stoneward(), "fighter", "monsters", 10)
    setup = EncounterSetup(heroes=[caster], monsters=[target], hero_total_levels=4, monster_total_cr="1")

    events, sequence = resolve_best_spell_offense(
        1, 1, caster, setup, "1:cleric", FixedDiceProvider([1, 10, 9]),
    )

    assert sequence == 3
    assert events[0].feature_id == "inflict-wounds"
    assert events[1].feature_id == "inflict-wounds"
    assert events[1].save_succeeded is False
    assert events[1].damage_roll is not None and events[1].damage_roll.total == 19
    slots = {item.id: item.current_uses for item in caster.state.resources}
    assert slots["spell-slot-1"] == 3
    assert slots["spell-slot-2"] == 3


def test_seraphine_certified_registry_exposes_level_four() -> None:
    registry = build_certified_hero_registry()
    assert registry[("cleric", 4, "canonical")] == ("Seraphine Dawnshield", "seraphine-dawnshield-l4")
