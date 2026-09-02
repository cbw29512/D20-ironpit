from __future__ import annotations


SUPPORTED_HERO_ENGINE_FEATURES = {
    "second-wind", "savage-attacker", "adrenaline-rush", "relentless-endurance",
    "action-surge", "tactical-mind", "extra-attack",
    "improved-critical", "remarkable-athlete", "tactical-shift", "great-weapon-fighting",
    "indomitable", "tactical-master-sap",
    "rage", "danger-sense", "reckless-attack", "frenzy", "fast-movement", "mindless-rage",
    "feral-instinct",
    "sneak-attack", "weapon-mastery",
    "cleric-spellcasting", "divine-order-protector", "divine-spark", "turn-undead",
    "disciple-of-life", "preserve-life",
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
    "tactical-master-sap": {"tactical_master_sap": True},
    "danger-sense": {"danger_sense": True},
    "reckless-attack": {"reckless_attack": True},
    "frenzy": {"frenzy": True},
    "fast-movement": {"fast_movement_bonus_ft": 10},
    "mindless-rage": {"mindless_rage": True},
    "feral-instinct": {"initiative_advantage": True},
    "instinctive-pounce": {"instinctive_pounce_fraction": 0.5},
}


def unsupported_hero_engine_features(features: tuple[str, ...] | list[str]) -> tuple[str, ...]:
    return tuple(feature for feature in features if feature not in SUPPORTED_HERO_ENGINE_FEATURES)


def compile_progression_feature_fields(features: tuple[str, ...] | list[str], level: int) -> dict[str, object]:
    fields: dict[str, object] = {}
    for feature in features:
        fields.update(_STATIC_PROGRESSION_FIELDS.get(feature, {}))
    if "indomitable" in features:
        fields["indomitable_bonus"] = level
    if "sneak-attack" in features:
        fields["sneak_attack_d6"] = (level + 1) // 2
    return fields
