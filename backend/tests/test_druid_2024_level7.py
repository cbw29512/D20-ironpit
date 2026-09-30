from __future__ import annotations

from app.combat.state import build_combatant_state
from app.content.audited_druid import build_thalen_greenbough_level
from app.content.audited_druid_profile import build_thalen_greenbough_profile
from app.content.canonical_spell_policy import canonical_spell_package
from app.content.certified_heroes import build_certified_hero_registry
from app.content.character_resource_audit import assert_character_resources_raw_ready
from app.content.pregen_combat_profiles import build_pregen_combat_profiles


def test_2024_druid_level_seven_progression_and_potent_spellcasting() -> None:
    profile = build_thalen_greenbough_profile(7)
    hero = build_thalen_greenbough_level(7)
    package = canonical_spell_package("druid", 7, "2024", 4)

    assert profile.level == 7
    assert hero.level == 7
    assert hero.max_hp == 38
    assert hero.ability_scores.wisdom == 19
    assert hero.saving_throw_bonuses["wisdom"] == 7

    assert {item.id: item.max_uses for item in hero.resources} == {
        "spell-slot-1": 4,
        "spell-slot-2": 3,
        "spell-slot-3": 3,
        "spell-slot-4": 1,
        "wild-shape": 3,
        "wild-resurgence-slot-restore": 1,
        "natural-recovery-free-cast": 1,
    }

    assert package is not None
    assert len(package.spells) == 11
    assert package.spells[-1].id == "divination"

    cantrips = {item.id: item for item in hero.spell_attack_actions}
    assert cantrips["poison-spray"].damage_bonus == 4
    assert cantrips["fire-bolt"].damage_bonus == 4
    assert cantrips["starry-wisp"].damage_bonus == 4
    assert cantrips["poison-spray"].damage_dice_count == 2
    assert cantrips["fire-bolt"].damage_dice_count == 2
    assert cantrips["starry-wisp"].damage_dice_count == 2

    audit = next(
        item for item in profile.feature_audits
        if item.feature_id == "elemental-fury-potent-spellcasting"
    )
    assert audit.combat_relevant is True
    assert audit.automated is True

    combat = build_pregen_combat_profiles()[hero.id]
    assert_character_resources_raw_ready(hero, profile, combat)


def test_2024_druid_level_seven_arid_blight_is_exact_and_natural_recovery_eligible() -> None:
    hero = build_thalen_greenbough_level(7)
    blight = next(item for item in hero.spell_save_actions if item.id == "blight")

    assert (
        blight.level,
        blight.action_cost,
        blight.range_ft,
        blight.save_ability,
        blight.damage_dice_count,
        blight.damage_dice_size,
        blight.damage_type,
        blight.success_damage,
        blight.upcast_dice_per_level,
    ) == (4, "action", 30, "constitution", 8, 8, "necrotic", "half", 1)
    assert blight.automatic_failure_creature_types == ["Plant"]
    assert blight.requires_target_sight is True

    state = build_combatant_state(hero)
    grants = state.template.progression_features.alternate_spell_cast_grants
    assert ("blight", 4) in {(item.spell_id, item.cast_level) for item in grants}


def test_certified_registry_exposes_2024_druid_level_seven() -> None:
    registry = build_certified_hero_registry()
    assert registry[("druid", 7, "canonical")] == (
        "Thalen Greenbough",
        "thalen-greenbough-l7",
    )
