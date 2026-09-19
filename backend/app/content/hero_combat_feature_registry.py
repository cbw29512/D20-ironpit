from __future__ import annotations

import logging

logger = logging.getLogger(__name__)


SUPPORTED_HERO_ENGINE_FEATURES = {
    "second-wind", "savage-attacker", "adrenaline-rush", "relentless-endurance",
    "action-surge", "tactical-mind", "extra-attack",
    "improved-critical", "remarkable-athlete", "tactical-shift", "great-weapon-fighting",
    "indomitable", "tactical-master", "heroic-warrior", "studied-attacks", "survivor",
    "rage", "danger-sense", "reckless-attack", "frenzy", "fast-movement", "mindless-rage",
    "relentless-rage", "feral-instinct", "instinctive-pounce", "brutal-strike", "brutal-strike-2d10",
    "brutal-critical", "brutal-critical-2", "brutal-critical-3", "intimidating-presence",
    "retaliation", "persistent-rage-2014", "indomitable-might", "primal-champion",
    "sneak-attack", "weapon-mastery", "cunning-action", "uncanny-dodge", "evasion",
    "fast-hands", "second-story-work", "superior-critical",
    "martial-arts", "unarmored-defense", "unarmored-movement", "ki", "stunning-strike",
    "open-hand-technique", "flurry-of-blows", "deflect-missiles",
    "lay-on-hands", "divine-sense", "divine-smite-2014", "fighting-style",
    "aura-of-protection-2014", "sacred-weapon-2014",
    "turn-unholy-2014", "aura-of-devotion-2014", "aura-of-courage-2014",
    "cleric-spellcasting", "divine-order-protector", "divine-spark", "turn-undead",
    "disciple-of-life", "preserve-life",
    "survivor-defy-death", "survivor-heroic-rally", "boon-combat-prowess",
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
    "danger-sense": {"danger_sense": True},
    "reckless-attack": {"reckless_attack": True},
    "frenzy": {"frenzy": True},
    "fast-movement": {"fast_movement_bonus_ft": 10},
    "mindless-rage": {"mindless_rage": True},
    "feral-instinct": {"initiative_advantage": True},
    "instinctive-pounce": {"instinctive_pounce_fraction": 0.5},
    "brutal-strike": {"brutal_strike_damage_dice": 1},
    "survivor-defy-death": {"death_save_advantage": True, "death_save_nat20_minimum": 18},
    "boon-combat-prowess": {"peerless_aim": True},
}


def unsupported_hero_engine_features(features: tuple[str, ...] | list[str]) -> tuple[str, ...]:
    return tuple(feature for feature in features if feature not in SUPPORTED_HERO_ENGINE_FEATURES)


def compile_progression_feature_fields(
    features: tuple[str, ...] | list[str],
    level: int,
    ruleset: str = "2024",
) -> dict[str, object]:
    try:
        fields: dict[str, object] = {}
        if ruleset == "2014":
            if "improved-critical" in features:
                fields["critical_hit_minimum"] = 19
            if "superior-critical" in features:
                fields["critical_hit_minimum"] = 18
            if "reckless-attack" in features:
                fields["reckless_attack"] = True
            if "danger-sense" in features:
                fields["danger_sense"] = True
            if "frenzy" in features:
                fields["frenzy_bonus_attack_2014"] = True
            if "fast-movement" in features:
                fields["fast_movement_bonus_ft"] = 10
            if "mindless-rage" in features:
                fields["mindless_rage"] = True
            if "feral-instinct" in features:
                fields["initiative_advantage"] = True
            if "cunning-action" in features:
                fields["cunning_action"] = True
            if "uncanny-dodge" in features:
                fields["uncanny_dodge"] = True
            if "evasion" in features:
                fields["evasion"] = True
            if "martial-arts" in features:
                fields["martial_arts_bonus_attack"] = True
            if "stunning-strike" in features:
                fields["stunning_strike"] = True
            if "open-hand-technique" in features:
                fields["open_hand_technique"] = True
            if "flurry-of-blows" in features:
                fields["flurry_of_blows"] = True
            if "deflect-missiles" in features:
                fields["deflect_missiles"] = True
            if "divine-smite-2014" in features:
                fields["divine_smite_2014"] = True
            if "turn-unholy-2014" in features:
                fields["turn_unholy_2014"] = True
            if "aura-of-devotion-2014" in features:
                fields["aura_of_devotion_2014"] = True
            if "aura-of-courage-2014" in features:
                fields["aura_of_courage_2014"] = True
            if "aura-of-protection-2014" in features:
                fields["aura_of_protection_2014_bonus"] = 1
            if "sacred-weapon-2014" in features:
                fields["sacred_weapon_2014_bonus"] = 1
            if "persistent-rage-2014" in features:
                fields["persistent_rage_2014"] = True
            if "indomitable-might" in features:
                fields["ability_check_minimums"] = [
                    {"source_id": "indomitable-might", "ability": "strength"},
                ]
        else:
            for feature in features:
                fields.update(_STATIC_PROGRESSION_FIELDS.get(feature, {}))
        if "indomitable" in features:
            if ruleset == "2014":
                fields["indomitable_reroll"] = True
            else:
                fields["indomitable_bonus"] = level
        if "sneak-attack" in features:
            fields["sneak_attack_d6"] = (level + 1) // 2
        if "brutal-strike-2d10" in features:
            fields["brutal_strike_damage_dice"] = 2
        if "brutal-critical-3" in features:
            fields["brutal_critical_dice"] = 3
        elif "brutal-critical-2" in features:
            fields["brutal_critical_dice"] = 2
        elif "brutal-critical" in features:
            fields["brutal_critical_dice"] = 1
        if "relentless-rage" in features:
            fields["effect_bound_survival_save"] = {
                "source_id": "relentless-rage", "required_effect_id": "rage",
                "save_ability": "constitution", "initial_dc": 10, "dc_increment": 5,
                "replacement_hp": 1 if ruleset == "2014" else 2 * level,
            }
        return fields
    except Exception:
        logger.exception("Failed to compile progression capabilities at level %s.", level)
        raise
