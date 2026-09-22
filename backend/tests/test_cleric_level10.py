from app.combat.dice import FixedDiceProvider
from app.combat.healing_riders import apply_slot_healing_self_rider
from app.combat.saving_throws import resolve_save_action
from app.combat.state import build_combatant_state
from app.content.audited_cleric import build_seraphine_dawnshield_level
from app.content.audited_cleric_life_high_profile import build_seraphine_dawnshield_level10_profile
from app.content.build_audit import assert_character_build_raw_ready
from app.content.canonical_hero_policy import assert_canonical_profile_policy, canonical_spell_package
from app.content.character_resource_audit import assert_character_resources_raw_ready
from app.content.capability_registry import build_combatant_from_capabilities
from app.content.certified_heroes import build_certified_hero_registry
from app.content.pregen_combat_audit import assert_pregen_combat_stats
from app.content.pregen_combat_profiles import build_pregen_combat_profiles
from app.domain.encounters import EncounterCombatant


def _member(template, combatant_id: str, side: str, position: int) -> EncounterCombatant:
    return EncounterCombatant(
        combatant_id=combatant_id,
        side=side,
        position_ft=position,
        state=build_combatant_state(template),
    )


def _resources(template) -> dict[str, int]:
    return {item.id: item.max_uses for item in template.resources}


def test_level_ten_adds_one_shared_divine_intervention_resource() -> None:
    level9 = build_seraphine_dawnshield_level(9)
    hero = build_seraphine_dawnshield_level(10)
    profile = build_seraphine_dawnshield_level10_profile()
    combat = build_pregen_combat_profiles()[hero.id]
    package = canonical_spell_package("cleric", 10)

    assert hero.max_hp == level9.max_hp + 5 == 53
    assert _resources(hero) == {
        "spell-slot-1": 4,
        "spell-slot-2": 3,
        "spell-slot-3": 3,
        "spell-slot-4": 3,
        "spell-slot-5": 2,
        "channel-divinity": 3,
        "divine-intervention": 1,
        "adrenaline-rush": 4,
        "relentless-endurance": 1,
    }

    damage = next(
        item for item in hero.saving_throw_actions
        if item.id == "divine-intervention-inflict-wounds"
    )
    healing = next(
        item for item in hero.healing_actions
        if item.id == "divine-intervention-mass-cure-wounds"
    )
    assert (damage.damage_dice_count, damage.damage_dice_size, damage.dc) == (6, 10, 17)
    assert damage.resource_id == "divine-intervention"
    assert healing.resource_id == "divine-intervention"
    assert (healing.dice_count, healing.dice_size, healing.healing_bonus) == (5, 8, 12)

    assert len(package.spells) == 15
    assert len(package.cantrips) == 5
    assert package.spells[-1].id == "contagion"
    assert package.cantrips[-1].id == "spare-the-dying"

    assert_canonical_profile_policy(profile)
    assert_character_build_raw_ready(profile, hero)
    assert_pregen_combat_stats(hero, combat)
    assert_character_resources_raw_ready(hero, profile, combat)


def test_divine_intervention_damage_spends_shared_resource_once() -> None:
    cleric = _member(build_seraphine_dawnshield_level(10), "cleric", "heroes", 0)
    enemy = _member(build_combatant_from_capabilities("srd-skeleton"), "enemy", "monsters", 5)
    action = cleric.state.template.saving_throw_actions[0]

    event = resolve_save_action(
        1,
        1,
        cleric,
        enemy,
        action,
        5,
        FixedDiceProvider([1, 1, 1, 1, 1, 1, 1]),
    )

    resource = next(item for item in cleric.state.resources if item.id == "divine-intervention")
    assert resource.current_uses == 0
    assert event.resource_remaining == 0


def test_divine_intervention_healing_does_not_trigger_blessed_healer() -> None:
    cleric = _member(build_seraphine_dawnshield_level(10), "cleric", "heroes", 0)
    action = next(
        item for item in cleric.state.template.healing_actions
        if item.id == "divine-intervention-mass-cure-wounds"
    )

    assert apply_slot_healing_self_rider(1, 1, cleric, True, action) is None


def test_certified_registry_exposes_cleric_level_ten_only() -> None:
    registry = build_certified_hero_registry()
    assert registry[("cleric", 10, "canonical")] == (
        "Seraphine Dawnshield", "seraphine-dawnshield-l10",
    )
    assert ("cleric", 11, "canonical") not in registry
