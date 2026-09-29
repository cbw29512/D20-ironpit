from __future__ import annotations

import pytest

from app.content.certified_hero_progressions import iter_certified_progression_levels


def _by_id(items):
    return {item.id: item for item in items}


@pytest.mark.parametrize(
    ("progression", "level"),
    iter_certified_progression_levels("2024"),
)
def test_certified_2024_spell_surfaces_use_registered_2024_fingerprints(
    progression,
    level: int,
) -> None:
    template = progression.template_builder(level)

    spell_attacks = _by_id(template.spell_attack_actions)
    spell_saves = _by_id(template.spell_save_actions)
    defenses = _by_id(template.defensive_spell_actions)
    healing = _by_id([
        item for item in template.healing_actions
        if (item.resource_id or "").startswith("spell-slot-")
        or item.id.startswith("divine-intervention-")
    ])
    condition_removals = _by_id([
        item for item in template.condition_removal_actions
        if item.expends_spell_slot
    ])
    effect_removals = _by_id([
        item for item in template.effect_removal_actions
        if item.expends_spell_slot
    ])

    known_spell_ids = {
        "guiding-bolt",
        "sacred-flame",
        "inflict-wounds",
        "inflict-wounds-l5",
        "inflict-wounds-l6",
        "inflict-wounds-l7",
        "inflict-wounds-l8",
        "inflict-wounds-l9",
        "bless",
        "shield-of-faith",
        "aid",
        "cure-wounds",
        "healing-word",
        "mass-healing-word",
        "mass-cure-wounds",
        "mass-cure-wounds-l6",
        "mass-cure-wounds-l7",
        "mass-cure-wounds-l8",
        "mass-cure-wounds-l9",
        "lesser-restoration",
        "dispel-magic",
        "divine-intervention-inflict-wounds",
        "divine-intervention-mass-cure-wounds",
        "greater-divine-intervention-wish-power-word-stun",
    }
    surfaced = {
        *spell_attacks,
        *spell_saves,
        *defenses,
        *healing,
        *condition_removals,
        *effect_removals,
        *(
            item.id
            for item in template.saving_throw_actions
            if item.id.startswith("divine-intervention-")
        ),
        *(
            item.id
            for item in template.hp_threshold_condition_actions
            if item.id.startswith("greater-divine-intervention-")
        ),
    }
    unknown = sorted(surfaced - known_spell_ids)
    assert unknown == [], (
        f"{progression.class_id} level {level} exposes 2024 spell mechanics without "
        f"an edition fingerprint: {unknown}"
    )

    if "guiding-bolt" in spell_attacks:
        spell = spell_attacks["guiding-bolt"]
        assert (
            spell.action_cost,
            spell.attack_kind,
            spell.range_ft,
            spell.damage_dice_count,
            spell.damage_dice_size,
            spell.damage_type,
        ) == ("action", "ranged", 120, 4, 6, "radiant")
        assert len(spell.on_hit_modifier_effects) == 1
        rider = spell.on_hit_modifier_effects[0]
        assert rider.kind == "attacks-against-advantage"
        assert rider.consume_on_attack_against is True
        assert rider.expires_after_source_turns == 1

    if "sacred-flame" in spell_saves:
        spell = spell_saves["sacred-flame"]
        expected_dice = 1 + int(level >= 5) + int(level >= 11) + int(level >= 17)
        assert (
            spell.action_cost,
            spell.range_ft,
            spell.save_ability,
            spell.damage_dice_count,
            spell.damage_dice_size,
            spell.damage_type,
            spell.success_damage,
        ) == ("action", 60, "dexterity", expected_dice, 8, "radiant", "none")

    for spell_id, spell in spell_saves.items():
        if not spell_id.startswith("inflict-wounds"):
            continue
        slot_level = 1 if spell_id == "inflict-wounds" else int(spell_id.rsplit("-l", 1)[1])
        assert (
            spell.level,
            spell.action_cost,
            spell.range_ft,
            spell.save_ability,
            spell.damage_dice_count,
            spell.damage_dice_size,
            spell.damage_type,
            spell.success_damage,
            spell.upcast_dice_per_level,
        ) == (
            slot_level,
            "action",
            5,
            "constitution",
            2 + (slot_level - 1),
            10,
            "necrotic",
            "half",
            1,
        )

    if "bless" in defenses:
        spell = defenses["bless"]
        assert (
            spell.level,
            spell.action_cost,
            spell.range_ft,
            spell.duration_minutes,
            spell.target_count,
            spell.target_count_per_slot_above,
            spell.concentration,
        ) == (1, "action", 30, 1, 3, 1, True)
        modifiers = {(item.kind, item.dice_count, item.dice_size) for item in spell.modifier_effects}
        assert modifiers == {
            ("attack-roll-bonus-die", 1, 4),
            ("saving-throw-bonus-die", 1, 4),
        }

    if "shield-of-faith" in defenses:
        spell = defenses["shield-of-faith"]
        assert (
            spell.level,
            spell.action_cost,
            spell.range_ft,
            spell.duration_minutes,
            spell.concentration,
        ) == (1, "bonus_action", 60, 10, True)
        assert len(spell.modifier_effects) == 1
        assert spell.modifier_effects[0].kind == "armor-class"
        assert spell.modifier_effects[0].flat_bonus == 2

    if "aid" in defenses:
        spell = defenses["aid"]
        assert (
            spell.level,
            spell.action_cost,
            spell.range_ft,
            spell.duration_minutes,
            spell.target_count,
            spell.max_hp_increase,
            spell.current_hp_increase,
        ) == (2, "action", 30, 480, 3, 5, 5)

    if "cure-wounds" in healing:
        spell = healing["cure-wounds"]
        assert (
            spell.action_cost,
            spell.range_ft,
            spell.dice_count,
            spell.dice_size,
            spell.resource_id,
        ) == ("action", 5, 2, 8, "spell-slot-1")

    if "healing-word" in healing:
        spell = healing["healing-word"]
        assert (
            spell.action_cost,
            spell.range_ft,
            spell.dice_count,
            spell.dice_size,
            spell.resource_id,
        ) == ("bonus_action", 60, 2, 4, "spell-slot-1")

    if "mass-healing-word" in healing:
        spell = healing["mass-healing-word"]
        assert (
            spell.action_cost,
            spell.range_ft,
            spell.max_targets,
            spell.dice_count,
            spell.dice_size,
            spell.resource_id,
        ) == ("bonus_action", 60, 6, 2, 4, "spell-slot-3")

    for spell_id, spell in healing.items():
        if not spell_id.startswith("mass-cure-wounds"):
            continue
        if spell_id == "divine-intervention-mass-cure-wounds":
            expected_slot = 5
            expected_resource = "divine-intervention"
        else:
            expected_slot = 5 if spell_id == "mass-cure-wounds" else int(spell_id.rsplit("-l", 1)[1])
            expected_resource = f"spell-slot-{expected_slot}"
        assert (
            spell.action_cost,
            spell.range_ft,
            spell.max_targets,
            spell.area_radius_ft,
            spell.dice_count,
            spell.dice_size,
            spell.resource_id,
        ) == (
            "action",
            60,
            6,
            30,
            5 + (expected_slot - 5),
            8,
            expected_resource,
        )

    if "lesser-restoration" in condition_removals:
        spell = condition_removals["lesser-restoration"]
        assert (
            spell.action_cost,
            spell.range_ft,
            spell.max_conditions_per_use,
            spell.resource_costs,
        ) == ("bonus_action", 5, 1, {"spell-slot-2": 1})
        assert set(spell.removable_conditions) == {
            "blinded",
            "deafened",
            "paralyzed",
            "poisoned",
        }

    if "dispel-magic" in effect_removals:
        spell = effect_removals["dispel-magic"]
        assert (
            spell.level,
            spell.action_cost,
            spell.range_ft,
            spell.casting_ability,
            spell.auto_remove_max_level,
            spell.resource_id,
        ) == (3, "action", 120, "wisdom", 3, "spell-slot-3")

    divine_healing = healing.get("divine-intervention-mass-cure-wounds")
    if divine_healing is not None:
        assert (
            divine_healing.action_cost,
            divine_healing.range_ft,
            divine_healing.max_targets,
            divine_healing.area_radius_ft,
            divine_healing.dice_count,
            divine_healing.dice_size,
            divine_healing.resource_id,
        ) == ("action", 60, 6, 30, 5, 8, "divine-intervention")

    intervention = next(
        (
            item for item in template.saving_throw_actions
            if item.id == "divine-intervention-inflict-wounds"
        ),
        None,
    )
    if intervention is not None:
        assert (
            intervention.action_cost,
            intervention.range_ft,
            intervention.save_ability,
            intervention.damage_dice_count,
            intervention.damage_dice_size,
            intervention.damage_type,
            intervention.success_damage,
            intervention.resource_id,
        ) == (
            "action",
            5,
            "constitution",
            6,
            10,
            "necrotic",
            "half",
            "divine-intervention",
        )


    greater_intervention = next(
        (
            item for item in template.hp_threshold_condition_actions
            if item.id == "greater-divine-intervention-wish-power-word-stun"
        ),
        None,
    )
    if greater_intervention is not None:
        assert (
            greater_intervention.action_cost,
            greater_intervention.range_ft,
            greater_intervention.max_current_hp,
            greater_intervention.condition_id,
            greater_intervention.repeat_save_ability,
            greater_intervention.repeat_save_timing,
            greater_intervention.resource_id,
            greater_intervention.resource_cost,
            greater_intervention.magical_effect,
        ) == (
            "action",
            60,
            150,
            "stunned",
            "constitution",
            "target_turn_end",
            "divine-intervention",
            1,
            True,
        )
        assert greater_intervention.repeat_save_dc == (
            8 + 6 + 5
        )
