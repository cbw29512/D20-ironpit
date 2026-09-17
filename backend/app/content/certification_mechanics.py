from __future__ import annotations

from typing import Any


def template_mechanics(template: Any) -> list[str]:
    """Return deterministic combat-mechanic labels for a certified runtime template."""
    mechanics = {
        *(f"attack:{item.id}" for item in [template.weapon_attack, *template.alternate_weapon_attacks]),
        *(f"resource:{item.id}" for item in template.resources),
        *(f"trait:{item.value}" for item in template.combat_traits),
        *(f"saving-throw-action:{item.id}" for item in template.saving_throw_actions),
        *(f"spell-save-action:{item.id}" for item in template.spell_save_actions),
        *(f"spell-attack-action:{item.id}" for item in template.spell_attack_actions),
        *(f"defensive-spell-action:{item.id}" for item in template.defensive_spell_actions),
        *(f"healing-action:{item.id}" for item in template.healing_actions),
        *(f"condition-removal-action:{item.id}" for item in template.condition_removal_actions),
    }
    if template.attack_action is not None:
        mechanics.add("multiattack-or-extra-attack")
    features = template.progression_features
    feature_flags = (
        (features.critical_hit_minimum < 20, "expanded-critical-range"),
        (features.initiative_advantage, "initiative-advantage"),
        (features.athletics_advantage, "athletics-advantage"),
        (features.danger_sense, "danger-sense"),
        (features.reckless_attack, "reckless-attack"),
        (features.frenzy, "frenzy"),
        (features.fast_movement_bonus_ft, "fast-movement"),
        (features.mindless_rage, "mindless-rage"),
        (features.instinctive_pounce_fraction, "instinctive-pounce"),
        (features.great_weapon_fighting, "great-weapon-fighting"),
        (features.indomitable_reroll or features.indomitable_bonus, "indomitable"),
        (features.tactical_master_sap_weapon_ids, "tactical-master"),
        (features.heroic_warrior, "heroic-warrior"),
        (features.studied_attacks, "studied-attacks"),
        (features.sneak_attack_d6, "sneak-attack"),
        (features.critical_move_fraction, "post-critical-movement"),
        (features.tactical_shift_fraction, "tactical-shift"),
    )
    mechanics.update(label for enabled, label in feature_flags if enabled)
    return sorted(mechanics)
