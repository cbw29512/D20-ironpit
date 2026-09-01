from __future__ import annotations


def apply_level_four(data: dict[str, object]) -> None:
    attack = data["weapon_attack"]; saves = data["saving_throw_bonuses"]
    skills = data["skill_bonuses"]; masteries = data["weapon_masteries"]
    if not isinstance(attack, dict) or not isinstance(saves, dict) or not isinstance(skills, dict) or not isinstance(masteries, list):
        raise ValueError("Karnok Fighter 4 base snapshot has an unexpected schema.")
    attack["attack_bonus"] = 6; attack["damage_bonus"] = 4
    saves["strength"] = 6; saves["constitution"] = 5; skills["athletics"] = 6
    masteries.append("longsword")


def apply_level_five(data: dict[str, object]) -> None:
    attack = data["weapon_attack"]; alternates = data["alternate_weapon_attacks"]
    saves = data["saving_throw_bonuses"]; skills = data["skill_bonuses"]
    if not isinstance(attack, dict) or not isinstance(alternates, list) or not isinstance(saves, dict) or not isinstance(skills, dict):
        raise ValueError("Karnok Fighter 5 base snapshot has an unexpected schema.")
    shortbow = next((item for item in alternates if isinstance(item, dict) and item.get("id") == "karnok-shortbow"), None)
    if shortbow is None:
        raise ValueError("Karnok Fighter 5 requires the audited Shortbow attack.")
    attack["attack_bonus"] = 7; shortbow["attack_bonus"] = 4
    saves["strength"] = 7; saves["constitution"] = 6; skills["athletics"] = 7
    ids = ["karnok-greatsword", "karnok-shortbow"]
    data["attack_action"] = {"id": "extra-attack", "name": "Extra Attack", "slots": [{"attack_ids": ids}, {"attack_ids": ids}]}


def apply_level_six(data: dict[str, object]) -> None:
    attack = data["weapon_attack"]; saves = data["saving_throw_bonuses"]; skills = data["skill_bonuses"]
    if not isinstance(attack, dict) or not isinstance(saves, dict) or not isinstance(skills, dict):
        raise ValueError("Karnok Fighter 6 base snapshot has an unexpected schema.")
    attack["attack_bonus"] = 8; attack["damage_bonus"] = 5
    saves["strength"] = 8; skills["athletics"] = 8


def apply_level_seven(data: dict[str, object]) -> None:
    attack = data["weapon_attack"]
    if not isinstance(attack, dict) or attack.get("id") != "karnok-greatsword":
        raise ValueError("Karnok Fighter 7 requires the audited Greatsword primary attack.")
    attack["damage_die_minimum"] = 3


def apply_level_eight(data: dict[str, object]) -> None:
    saves = data["saving_throw_bonuses"]
    if not isinstance(saves, dict):
        raise ValueError("Karnok Fighter 8 base snapshot has an unexpected schema.")
    saves["constitution"] = 7
