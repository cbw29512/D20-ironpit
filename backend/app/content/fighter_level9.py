from __future__ import annotations


def apply_fighter_level9(data: dict[str, object]) -> None:
    weapon_attack = data.get("weapon_attack")
    alternate_attacks = data.get("alternate_weapon_attacks")
    saving_throws = data.get("saving_throw_bonuses")
    skills = data.get("skill_bonuses")
    if not isinstance(weapon_attack, dict) or not isinstance(alternate_attacks, list):
        raise ValueError("Karnok Fighter 9 attack snapshot has an unexpected schema.")
    if not isinstance(saving_throws, dict) or not isinstance(skills, dict):
        raise ValueError("Karnok Fighter 9 save/skill snapshot has an unexpected schema.")
    shortbow = next((item for item in alternate_attacks if isinstance(item, dict) and item.get("id") == "karnok-shortbow"), None)
    if shortbow is None:
        raise ValueError("Karnok Fighter 9 requires the audited Shortbow attack.")
    weapon_attack["attack_bonus"] = 9
    shortbow["attack_bonus"] = 5
    saving_throws["strength"] = 9
    saving_throws["constitution"] = 8
    skills["athletics"] = 9
    data["weapon_masteries"] = ["greatsword", "shortbow", "javelin", "spear"]
