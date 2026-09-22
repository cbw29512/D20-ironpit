from __future__ import annotations

import logging

logger = logging.getLogger(__name__)


SUPPORTED_HERO_ENGINE_FEATURES = {
    "second-wind", "savage-attacker", "adrenaline-rush", "relentless-endurance",
    "action-surge", "tactical-mind", "extra-attack",
    "improved-critical", "superior-critical", "remarkable-athlete", "tactical-shift", "great-weapon-fighting",
    "indomitable", "tactical-master", "heroic-warrior", "studied-attacks",
    "survivor-defy-death", "survivor-heroic-rally",
    "rage", "danger-sense", "reckless-attack", "frenzy", "fast-movement", "mindless-rage",
    "relentless-rage", "feral-instinct", "instinctive-pounce", "brutal-strike", "brutal-strike-2d10",
    "sneak-attack", "weapon-mastery", "cunning-action", "steady-aim", "cunning-strike", "improved-cunning-strike", "devious-strikes", "slippery-mind", "thiefs-reflexes", "uncanny-dodge", "evasion",
    "cleric-spellcasting", "divine-order-protector", "divine-spark", "turn-undead",
    "disciple-of-life", "preserve-life", "sear-undead", "cleric-combat-spells-3", "blessed-healer",
    "blessed-strikes", "cleric-combat-spells-5", "divine-intervention", "cleric-combat-spells-6",
}

_STATIC_PROGRESSION_FIELDS: dict[str, dict[str, object]] = {
    "improved-critical": {"critical_hit_minimum": 19},
    "superior-critical": {"critical_hit_minimum": 18},
    "remarkable-athlete": {
        "initiative_advantage": True,
        "athletics_advantage": True,
        "critical_move_fraction": 0.5,
    },
    "tactical-shift": {"tactical_shift_fraction": 0.5},
    "great-weapon-fighting": {"great_weapon_fighting": True},
    "heroic-warrior": {"heroic_warrior": True},
    "studied-attacks": {"studied_attacks": True},
    "survivor-defy-death": {"death_save_advantage": True, "death_save_recovery_minimum": 18},
    "danger-sense": {"danger_sense": True},
    "reckless-attack": {"reckless_attack": True},
    "frenzy": {"frenzy": True},
    "fast-movement": {"fast_movement_bonus_ft": 10},
    "mindless-rage": {"mindless_rage": True},
    "feral-instinct": {"initiative_advantage": True},
    "instinctive-pounce": {"instinctive_pounce_fraction": 0.5},
    "brutal-strike": {"brutal_strike_damage_dice": 1},
    "cunning-action": {"cunning_action": True},
    "steady-aim": {"stationary_bonus_action_next_attack_advantage": True},
    "cunning-strike": {"cunning_strike_trip_die_cost": 1, "cunning_strike_max_effects": 1},
    "improved-cunning-strike": {"cunning_strike_max_effects": 2},
    "devious-strikes": {"cunning_strike_obscure_die_cost": 3},
    "slippery-mind": {
        "saving_throw_proficiency_grants": [
            {"source_id": "slippery-mind", "abilities": ["wisdom", "charisma"]},
        ],
    },
    "thiefs-reflexes": {
        "first_round_extra_turn_grants": [
            {"source_id": "thiefs-reflexes", "initiative_offset": -10},
        ],
    },
    "uncanny-dodge": {"uncanny_dodge": True},
    "evasion": {"evasion": True},
}


def unsupported_hero_engine_features(features: tuple[str, ...] | list[str]) -> tuple[str, ...]:
    return tuple(feature for feature in features if feature not in SUPPORTED_HERO_ENGINE_FEATURES)


def compile_progression_feature_fields(features: tuple[str, ...] | list[str], level: int) -> dict[str, object]:
    try:
        fields: dict[str, object] = {}
        for feature in features:
            fields.update(_STATIC_PROGRESSION_FIELDS.get(feature, {}))
        if "indomitable" in features:
            fields["indomitable_bonus"] = level
        if "sneak-attack" in features:
            fields["sneak_attack_d6"] = (level + 1) // 2
        if "brutal-strike-2d10" in features:
            fields["brutal_strike_damage_dice"] = 2
        if "relentless-rage" in features:
            fields["effect_bound_survival_save"] = {
                "source_id": "relentless-rage", "required_effect_id": "rage",
                "save_ability": "constitution", "initial_dc": 10, "dc_increment": 5,
                "replacement_hp": 2 * level,
            }
        return fields
    except Exception:
        logger.exception("Failed to compile progression capabilities at level %s.", level)
        raise
