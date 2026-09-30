from __future__ import annotations

from app.combat.resource_conversion import (
    conversion_available,
    restoration_conversion,
    resolve_resource_conversion,
)
from app.combat.state import build_combatant_state
from app.content.audited_druid import build_thalen_greenbough_level
from app.content.audited_druid_profile import build_thalen_greenbough_profile
from app.content.canonical_spell_policy import canonical_spell_package


def _resource(state, resource_id: str):
    return next(item for item in state.resources if item.id == resource_id)


def test_2024_druid_level_five_progression_and_spells() -> None:
    profile = build_thalen_greenbough_profile(5)
    hero = build_thalen_greenbough_level(5)
    package = canonical_spell_package("druid", 5, "2024", 4)

    assert profile.final_ability_scores.wisdom == 19
    assert hero.max_hp == 28
    assert hero.saving_throw_bonuses["wisdom"] == 7
    assert hero.skill_bonuses["nature"] == 8
    assert hero.skill_bonuses["survival"] == 7
    assert hero.skill_bonuses["perception"] == 7

    assert {item.id: item.max_uses for item in hero.resources} == {
        "spell-slot-1": 4,
        "spell-slot-2": 3,
        "spell-slot-3": 2,
        "wild-shape": 2,
        "wild-resurgence-slot-restore": 1,
    }

    assert package is not None
    assert len(package.spells) == 9
    assert [item.id for item in package.spells][-2:] == ["dispel-magic", "water-breathing"]

    fireball = next(item for item in hero.spell_save_actions if item.id == "fireball")
    assert (
        fireball.level,
        fireball.action_cost,
        fireball.range_ft,
        fireball.area.radius_ft if fireball.area else None,
        fireball.save_ability,
        fireball.damage_dice_count,
        fireball.damage_dice_size,
        fireball.damage_type,
        fireball.success_damage,
    ) == (3, "action", 150, 20, "dexterity", 8, 6, "fire", "half")

    assert [item.id for item in hero.effect_removal_actions] == ["dispel-magic"]
    dispel = hero.effect_removal_actions[0]
    assert (
        dispel.action_cost,
        dispel.range_ft,
        dispel.casting_ability,
        dispel.auto_remove_max_level,
        dispel.resource_id,
    ) == ("action", 120, "wisdom", 3, "spell-slot-3")


def test_2024_druid_level_five_wild_resurgence_is_raw_gated() -> None:
    hero = build_thalen_greenbough_level(5)
    actions = {item.id: item for item in hero.resource_conversion_actions}

    regain_shape = actions["wild-resurgence-regain-wild-shape-slot-1"]
    assert regain_shape.action_cost == "none"
    assert regain_shape.source_resource_id == "spell-slot-1"
    assert regain_shape.target_resource_id == "wild-shape"
    assert regain_shape.requires_target_empty is True
    assert regain_shape.once_per_turn is True

    regain_slot = actions["wild-resurgence-regain-level-1-slot"]
    assert regain_slot.action_cost == "none"
    assert regain_slot.source_resource_id == "wild-shape"
    assert regain_slot.additional_source_costs == {"wild-resurgence-slot-restore": 1}
    assert regain_slot.target_resource_id == "spell-slot-1"

    state = build_combatant_state(hero)
    _resource(state, "wild-shape").current_uses = 0

    assert restoration_conversion(state, "wild-shape") is None
    restored = restoration_conversion(state, "wild-shape", "1:thalen")
    assert restored is not None
    assert restored.id == "wild-resurgence-regain-wild-shape-slot-1"
    assert conversion_available(state, regain_shape, "1:thalen") is True
    resolve_resource_conversion(
        state,
        regain_shape,
        sequence=1,
        round_number=1,
        actor_id="thalen",
        turn_key="1:thalen",
    )
    assert _resource(state, "wild-shape").current_uses == 1
    assert conversion_available(state, regain_shape, "1:thalen") is False

    _resource(state, "spell-slot-1").current_uses = 3
    _resource(state, "wild-shape").current_uses = 1
    assert conversion_available(state, regain_slot) is True
    resolve_resource_conversion(
        state,
        regain_slot,
        sequence=2,
        round_number=1,
        actor_id="thalen",
    )
    assert _resource(state, "spell-slot-1").current_uses == 4
    assert _resource(state, "wild-shape").current_uses == 0
    assert _resource(state, "wild-resurgence-slot-restore").current_uses == 0
    assert conversion_available(state, regain_slot) is False
