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
        "poison-spray",
        "starry-wisp",
        "thunderclap",
        "longstrider",
        "faerie-fire",
        "fire-bolt",
        "burning-hands",
        "blur",
        "blight",
        "inflict-wounds",
        "inflict-wounds-l5",
        "inflict-wounds-l6",
        "inflict-wounds-l7",
        "inflict-wounds-l8",
        "inflict-wounds-l9",
        "bless",
        "shield-of-faith",
        "aid",
        "shatter",
        "thunderwave",
        "fireball",
        "disintegrate",
        "finger-of-death",
        "sunburst",
        "cone-of-cold",
        "circle-of-death",
        "power-word-kill",
        "power-word-heal",
        "cure-wounds",
        "healing-word",
        "mass-healing-word",
        "mass-cure-wounds",
        "mass-cure-wounds-l6",
        "mass-cure-wounds-l7",
        "mass-cure-wounds-l8",
        "mass-cure-wounds-l9",
        "heal",
        "heal-l7",
        "heal-l8",
        "heal-l9",
        "greater-invisibility",
        "foresight",
        "freedom-of-movement",
        "lesser-restoration",
        "dispel-magic",
        "divine-intervention-inflict-wounds",
        "divine-intervention-mass-cure-wounds",
        "greater-divine-intervention-wish-fireball",
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
            or item.id.startswith("greater-divine-intervention-")
        ),
    }
    unknown = sorted(surfaced - known_spell_ids)
    assert unknown == [], (
        f"{progression.class_id} level {level} exposes 2024 spell mechanics without "
        f"an edition fingerprint: {unknown}"
    )

    if "poison-spray" in spell_attacks:
        spell = spell_attacks["poison-spray"]
        expected_dice = 1 + int(level >= 5) + int(level >= 11) + int(level >= 17)
        assert (
            spell.level,
            spell.action_cost,
            spell.attack_kind,
            spell.range_ft,
            spell.damage_dice_count,
            spell.damage_dice_size,
            spell.damage_type,
        ) == (
            0, "action", "ranged",
            30 + (300 if progression.class_id == "druid" and level >= 15 else 0),
            expected_dice, 12, "poison",
        )

    if "starry-wisp" in spell_attacks:
        spell = spell_attacks["starry-wisp"]
        expected_dice = 1 + int(level >= 5) + int(level >= 11) + int(level >= 17)
        assert (
            spell.level,
            spell.action_cost,
            spell.attack_kind,
            spell.range_ft,
            spell.damage_dice_count,
            spell.damage_dice_size,
            spell.damage_type,
        ) == (
            0, "action", "ranged",
            60 + (300 if progression.class_id == "druid" and level >= 15 else 0),
            expected_dice, 8, "radiant",
        )
        assert len(spell.on_hit_modifier_effects) == 1
        rider = spell.on_hit_modifier_effects[0]
        assert rider.kind == "invisibility-benefits-suppressed"
        assert rider.expires_after_source_turns == 1

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


    if "thunderclap" in spell_saves:
        spell = spell_saves["thunderclap"]
        expected_dice = 1 + int(level >= 5) + int(level >= 11) + int(level >= 17)
        expected_bonus = (
            template.ability_scores.modifier("wisdom")
            if progression.class_id == "druid" and level >= 7
            else 0
        )
        assert (
            spell.level,
            spell.action_cost,
            spell.range_ft,
            spell.area.shape if spell.area else None,
            spell.area.origin if spell.area else None,
            spell.area.radius_ft if spell.area else None,
            spell.save_ability,
            spell.damage_dice_count,
            spell.damage_dice_size,
            spell.damage_bonus,
            spell.damage_type,
            spell.success_damage,
        ) == (
            0,
            "action",
            0,
            "emanation",
            "self",
            5,
            "constitution",
            expected_dice,
            6,
            expected_bonus,
            "thunder",
            "none",
        )

    if "thunderwave" in spell_saves:
        spell = spell_saves["thunderwave"]
        assert (
            spell.level,
            spell.action_cost,
            spell.range_ft,
            spell.area.shape if spell.area else None,
            spell.area.origin if spell.area else None,
            spell.area.length_ft if spell.area else None,
            spell.save_ability,
            spell.damage_dice_count,
            spell.damage_dice_size,
            spell.damage_type,
            spell.success_damage,
            spell.upcast_dice_per_level,
            spell.failed_save_push_ft,
        ) == (
            1,
            "action",
            15,
            "cube",
            "self",
            15,
            "constitution",
            2,
            8,
            "thunder",
            "half",
            1,
            10,
        )

    if "shatter" in spell_saves:
        spell = spell_saves["shatter"]
        assert (
            spell.level,
            spell.action_cost,
            spell.range_ft,
            spell.area.shape if spell.area else None,
            spell.area.origin if spell.area else None,
            spell.area.radius_ft if spell.area else None,
            spell.save_ability,
            spell.damage_dice_count,
            spell.damage_dice_size,
            spell.damage_type,
            spell.success_damage,
            spell.upcast_dice_per_level,
        ) == (
            2,
            "action",
            60,
            "radius",
            "point",
            10,
            "constitution",
            3,
            8,
            "thunder",
            "half",
            1,
        )

    if "fireball" in spell_saves:
        spell = spell_saves["fireball"]
        assert (
            spell.level,
            spell.action_cost,
            spell.range_ft,
            spell.area.shape if spell.area else None,
            spell.area.origin if spell.area else None,
            spell.area.radius_ft if spell.area else None,
            spell.save_ability,
            spell.damage_dice_count,
            spell.damage_dice_size,
            spell.damage_type,
            spell.success_damage,
            spell.upcast_dice_per_level,
        ) == (
            3,
            "action",
            150,
            "radius",
            "point",
            20,
            "dexterity",
            8,
            6,
            "fire",
            "half",
            1,
        )

    if "disintegrate" in spell_saves:
        spell = spell_saves["disintegrate"]
        assert (
            spell.level,
            spell.action_cost,
            spell.range_ft,
            spell.save_ability,
            spell.damage_dice_count,
            spell.damage_dice_size,
            spell.damage_bonus,
            spell.damage_type,
            spell.success_damage,
            spell.upcast_dice_per_level,
        ) == (
            6,
            "action",
            60,
            "dexterity",
            10,
            6,
            40,
            "force",
            "none",
            3,
        )

    if "finger-of-death" in spell_saves:
        spell = spell_saves["finger-of-death"]
        assert (
            spell.level,
            spell.action_cost,
            spell.range_ft,
            spell.save_ability,
            spell.damage_dice_count,
            spell.damage_dice_size,
            spell.damage_bonus,
            spell.damage_type,
            spell.success_damage,
        ) == (
            7,
            "action",
            60,
            "constitution",
            7,
            8,
            30,
            "necrotic",
            "half",
        )

    if "cone-of-cold" in spell_saves:
        spell = spell_saves["cone-of-cold"]
        assert (
            spell.level,
            spell.action_cost,
            spell.range_ft,
            spell.area.shape if spell.area else None,
            spell.area.origin if spell.area else None,
            spell.area.length_ft if spell.area else None,
            spell.save_ability,
            spell.damage_dice_count,
            spell.damage_dice_size,
            spell.damage_type,
            spell.success_damage,
            spell.upcast_dice_per_level,
        ) == (5, "action", 60, "cone", "self", 60, "constitution", 8, 8, "cold", "half", 1)

    if "circle-of-death" in spell_saves:
        spell = spell_saves["circle-of-death"]
        assert (
            spell.level,
            spell.action_cost,
            spell.range_ft,
            spell.area.shape if spell.area else None,
            spell.area.origin if spell.area else None,
            spell.area.radius_ft if spell.area else None,
            spell.save_ability,
            spell.damage_dice_count,
            spell.damage_dice_size,
            spell.damage_type,
            spell.success_damage,
            spell.upcast_dice_per_level,
        ) == (6, "action", 150, "radius", "point", 60, "constitution", 8, 8, "necrotic", "half", 2)

    if "sunburst" in spell_saves:
        spell = spell_saves["sunburst"]
        assert (
            spell.level,
            spell.action_cost,
            spell.range_ft,
            spell.area.shape if spell.area else None,
            spell.area.origin if spell.area else None,
            spell.area.radius_ft if spell.area else None,
            spell.save_ability,
            spell.damage_dice_count,
            spell.damage_dice_size,
            spell.damage_type,
            spell.success_damage,
        ) == (8, "action", 150, "radius", "point", 60, "constitution", 12, 6, "radiant", "half")
        rider = spell.failed_save_timed_effect
        assert rider is not None
        assert (
            rider.effect_id,
            rider.duration_rounds,
            rider.repeat_save_ability,
            rider.repeat_save_dc,
            rider.repeat_save_timing,
        ) == ("blinded", 10, "constitution", spell.dc, "target_turn_end")

    threshold_actions = {item.id: item for item in template.hp_threshold_instant_death_actions}
    if "power-word-kill" in threshold_actions:
        spell = threshold_actions["power-word-kill"]
        assert (
            spell.range_ft,
            spell.max_current_hp,
            spell.fallback_damage_dice_count,
            spell.fallback_damage_dice_size,
            spell.fallback_damage_bonus,
            spell.fallback_damage_type,
            spell.resource_id,
        ) == (60, 100, 12, 12, 0, "psychic", "spell-slot-9")
        assert spell.max_targets == (2 if level >= 20 and progression.class_id == "bard" else 1)
        assert spell.secondary_target_within_ft == (
            10 if level >= 20 and progression.class_id == "bard" else None
        )

    if "heal" in healing:
        spell = healing["heal"]
        assert (
            spell.action_cost,
            spell.range_ft,
            spell.target_mode,
            spell.dice_count,
            spell.healing_bonus,
            spell.resource_id,
            spell.removable_conditions,
        ) == (
            "action",
            60,
            "self_or_ally",
            0,
            70,
            "spell-slot-6",
            ["blinded", "deafened", "poisoned"],
        )

    if "power-word-heal" in healing:
        spell = healing["power-word-heal"]
        assert (
            spell.action_cost,
            spell.range_ft,
            spell.target_mode,
            spell.restore_to_effective_max,
            spell.resource_id,
            spell.max_targets,
            spell.secondary_target_within_ft,
            spell.prone_reaction_stand,
        ) == ("action", 60, "any", True, "spell-slot-9", 2, 10, True)
        assert spell.removable_conditions == [
            "charmed", "frightened", "paralyzed", "poisoned", "stunned",
        ]

    if "faerie-fire" in spell_saves:
        spell = spell_saves["faerie-fire"]
        assert (
            spell.level,
            spell.action_cost,
            spell.range_ft,
            spell.area.shape if spell.area else None,
            spell.area.origin if spell.area else None,
            spell.area.length_ft if spell.area else None,
            spell.save_ability,
            spell.concentration,
            spell.duration_minutes,
        ) == (1, "action", 60, "cube", "point", 20, "dexterity", True, 1)
        assert {item.kind for item in spell.failed_save_modifier_effects} == {
            "attacks-against-advantage", "invisibility-benefits-suppressed",
        }

    if "longstrider" in defenses:
        spell = defenses["longstrider"]
        assert (
            spell.level,
            spell.action_cost,
            spell.range_ft,
            spell.duration_minutes,
            spell.target_count,
            spell.target_count_per_slot_above,
            spell.concentration,
        ) == (1, "action", 5, 60, 1, 1, False)
        assert len(spell.modifier_effects) == 1
        assert spell.modifier_effects[0].kind == "speed"
        assert spell.modifier_effects[0].flat_bonus == 10


    if "fire-bolt" in spell_attacks:
        spell = spell_attacks["fire-bolt"]
        expected_dice = 1 + int(level >= 5) + int(level >= 11) + int(level >= 17)
        assert (
            spell.level, spell.action_cost, spell.attack_kind, spell.range_ft,
            spell.damage_dice_count, spell.damage_dice_size, spell.damage_type,
        ) == (
            0, "action", "ranged",
            120 + (300 if progression.class_id == "druid" and level >= 15 else 0),
            expected_dice, 10, "fire",
        )

    if "burning-hands" in spell_saves:
        spell = spell_saves["burning-hands"]
        assert (
            spell.level, spell.action_cost, spell.range_ft,
            spell.area.shape if spell.area else None,
            spell.area.origin if spell.area else None,
            spell.area.length_ft if spell.area else None,
            spell.save_ability, spell.damage_dice_count, spell.damage_dice_size,
            spell.damage_type, spell.success_damage, spell.upcast_dice_per_level,
        ) == (1, "action", 15, "cone", "self", 15, "dexterity", 3, 6, "fire", "half", 1)

    if "blur" in defenses:
        spell = defenses["blur"]
        assert (
            spell.level, spell.action_cost, spell.range_ft, spell.duration_minutes,
            spell.target_policy, spell.concentration,
        ) == (2, "action", 0, 1, "self", True)
        assert len(spell.modifier_effects) == 1
        modifier = spell.modifier_effects[0]
        assert modifier.kind == "attacks-against-disadvantage"
        assert modifier.bypass_attacker_senses == ["blindsight", "truesight"]

    if "blight" in spell_saves:
        spell = spell_saves["blight"]
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
            spell.automatic_failure_creature_types,
            spell.requires_target_sight,
        ) == (4, "action", 30, "constitution", 8, 8, "necrotic", "half", 1, ["Plant"], True)

    if "greater-invisibility" in defenses:
        spell = defenses["greater-invisibility"]
        assert (
            spell.level,
            spell.action_cost,
            spell.range_ft,
            spell.duration_minutes,
            spell.target_count,
            spell.condition_ids,
            spell.concentration,
        ) == (4, "action", 5, 1, 1, ["invisible"], True)

    if "foresight" in defenses:
        spell = defenses["foresight"]
        assert (
            spell.level,
            spell.action_cost,
            spell.range_ft,
            spell.duration_minutes,
            spell.target_policy,
            spell.concentration,
            spell.free_opening_cast,
        ) == (9, "action", 5, 480, "self", False, True)
        assert {item.kind for item in spell.modifier_effects} == {
            "d20-test-advantage",
            "attacks-against-disadvantage",
        }

    if "freedom-of-movement" in defenses:
        spell = defenses["freedom-of-movement"]
        assert (
            spell.level, spell.action_cost, spell.range_ft, spell.duration_minutes,
            spell.target_policy, spell.target_count, spell.target_count_per_slot_above,
            spell.concentration,
        ) == (4, "action", 5, 60, "friendly", 1, 1, False)
        signatures = {
            (
                item.debuff_counter.debuff_id,
                item.debuff_counter.source_scope,
                item.debuff_counter.mode,
                item.debuff_counter.movement_cost_ft,
            )
            for item in spell.modifier_effects
            if item.debuff_counter is not None
        }
        assert ("difficult-terrain", "any", "prevent", 0) in signatures
        assert ("speed-reduction", "magical", "prevent", 0) in signatures
        assert ("paralyzed", "magical", "prevent", 0) in signatures
        assert ("restrained", "magical", "prevent", 0) in signatures
        assert ("grappled", "nonmagical", "remove-with-movement", 5) in signatures
        assert ("restrained", "nonmagical", "remove-with-movement", 5) in signatures
        assert len(spell.movement_mode_grants) == 1
        swim = spell.movement_mode_grants[0]
        assert (swim.mode, swim.fixed_speed_ft, swim.match_current_speed) == ("swim", None, True)

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
        expected_casting_abilities = {
            "bard": "charisma",
            "cleric": "wisdom",
            "druid": "wisdom",
        }
        assert progression.class_id in expected_casting_abilities
        spell = effect_removals["dispel-magic"]
        assert (
            spell.level,
            spell.action_cost,
            spell.range_ft,
            spell.casting_ability,
            spell.auto_remove_max_level,
            spell.resource_id,
        ) == (
            3,
            "action",
            120,
            expected_casting_abilities[progression.class_id],
            3,
            "spell-slot-3",
        )

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



def test_2024_greater_divine_intervention_wish_uses_2024_fireball_fingerprint() -> None:
    from app.content.audited_cleric import build_seraphine_dawnshield_level

    hero = build_seraphine_dawnshield_level(20)
    spell = next(
        item for item in hero.saving_throw_actions
        if item.id == "greater-divine-intervention-wish-fireball"
    )

    assert spell.action_cost == "action"
    assert spell.range_ft == 150
    assert spell.area is not None
    assert (spell.area.shape, spell.area.origin, spell.area.radius_ft) == ("radius", "point", 20)
    assert spell.save_ability == "dexterity"
    assert (spell.damage_dice_count, spell.damage_dice_size) == (8, 6)
    assert spell.damage_type == "fire"
    assert spell.success_damage == "half"
    assert spell.resource_id == "divine-intervention"
