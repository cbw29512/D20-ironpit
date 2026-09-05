from __future__ import annotations

import re

from app.domain.capabilities import CombatantDefinition

# Compact family rows: all mechanics resolve through the shared attack/save/resource engine.
ROWS = [
    dict(name="Hell Hound", cr="3", size="medium", ac=15, hp=58, speed=50, movement=(50,0,0,0,0), init=1,
         saves=(3,1,2,-2,1,-2), skills={}, traits=["Pack Tactics"], immunities=["fire"], conditions=[],
         attack=("Bite",5,5,1,8,3,1,6,"fire"), breath=("Fire Breath","dexterity",12,15,3,5,6,"fire"), unarmed=(5,4), multi=2, body="quadruped"),
    dict(name="Black Dragon Wyrmling", cr="2", size="medium", ac=17, hp=33, speed=60, movement=(30,60,0,30,0), init=4,
         saves=(2,4,1,0,2,1), skills={"perception":4,"stealth":4}, traits=["Amphibious"], immunities=["acid"], conditions=[],
         attack=("Rend",4,5,1,6,2,1,4,"acid"), breath=("Acid Breath","dexterity",11,15,1,5,8,"acid"), unarmed=(4,3), multi=2, body="dragon"),
    dict(name="Young Black Dragon", cr="7", size="large", ac=18, hp=127, speed=80, movement=(40,80,0,40,0), init=5,
         saves=(4,5,3,1,3,2), skills={"perception":6,"stealth":5}, traits=["Amphibious"], immunities=["acid"], conditions=[],
         attack=("Rend",7,10,2,4,4,1,6,"acid"), breath=("Acid Breath","dexterity",14,30,1,14,6,"acid"), unarmed=(7,5), multi=3, body="dragon"),
    dict(name="Blue Dragon Wyrmling", cr="3", size="medium", ac=17, hp=65, speed=60, movement=(30,60,0,0,15), init=2,
         saves=(3,2,2,1,2,2), skills={"perception":4,"stealth":2}, traits=[], immunities=["lightning"], conditions=[],
         attack=("Rend",5,5,1,10,3,1,6,"lightning"), breath=("Lightning Breath","dexterity",12,30,1,6,6,"lightning"), unarmed=(5,4), multi=2, body="dragon"),
    dict(name="Young Blue Dragon", cr="9", size="large", ac=18, hp=152, speed=80, movement=(40,80,0,0,20), init=4,
         saves=(5,4,4,2,5,3), skills={"perception":9,"stealth":4}, traits=[], immunities=["lightning"], conditions=[],
         attack=("Rend",9,10,2,6,5,1,10,"lightning"), breath=("Lightning Breath","dexterity",16,60,1,10,10,"lightning"), unarmed=(9,6), multi=3, body="dragon"),
    dict(name="Green Dragon Wyrmling", cr="2", size="medium", ac=17, hp=38, speed=60, movement=(30,60,0,30,0), init=3,
         saves=(2,3,1,2,2,1), skills={"perception":4,"stealth":3}, traits=["Amphibious"], immunities=["poison"], conditions=["poisoned"],
         attack=("Rend",4,5,1,10,2,1,6,"poison"), breath=("Poison Breath","constitution",11,15,3,6,6,"poison"), unarmed=(4,3), multi=2, body="dragon"),
    dict(name="Young Green Dragon", cr="8", size="large", ac=18, hp=136, speed=80, movement=(40,80,0,40,0), init=4,
         saves=(4,4,3,3,4,2), skills={"deception":5,"perception":7,"stealth":4}, traits=["Amphibious"], immunities=["poison"], conditions=["poisoned"],
         attack=("Rend",7,10,2,6,4,2,6,"poison"), breath=("Poison Breath","constitution",14,30,6,12,6,"poison"), unarmed=(7,5), multi=3, body="dragon"),
    dict(name="Red Dragon Wyrmling", cr="4", size="medium", ac=17, hp=75, speed=60, movement=(30,60,30,0,0), init=2,
         saves=(4,2,3,1,2,2), skills={"perception":4,"stealth":2}, traits=[], immunities=["fire"], conditions=[],
         attack=("Rend",6,5,1,10,4,1,6,"fire"), breath=("Fire Breath","dexterity",13,15,3,7,6,"fire"), unarmed=(6,5), multi=2, body="dragon"),
    dict(name="Young Red Dragon", cr="10", size="large", ac=18, hp=178, speed=80, movement=(40,80,40,0,0), init=4,
         saves=(6,4,5,2,4,4), skills={"perception":8,"stealth":4}, traits=[], immunities=["fire"], conditions=[],
         attack=("Rend",10,10,2,6,6,1,6,"fire"), breath=("Fire Breath","dexterity",17,30,6,16,6,"fire"), unarmed=(10,7), multi=3, body="dragon"),
    dict(name="White Dragon Wyrmling", cr="2", size="medium", ac=16, hp=32, speed=60, movement=(30,60,0,30,15), init=2,
         saves=(2,2,2,-3,2,0), skills={"perception":4,"stealth":2}, traits=["Ice Walk"], immunities=["cold"], conditions=[],
         attack=("Rend",4,5,1,8,2,1,4,"cold"), breath=("Cold Breath","constitution",12,15,3,5,8,"cold"), unarmed=(4,3), multi=2, body="dragon"),
    dict(name="Young White Dragon", cr="6", size="large", ac=17, hp=123, speed=80, movement=(40,80,0,40,20), init=3,
         saves=(4,3,4,-2,3,1), skills={"perception":6,"stealth":3}, traits=["Ice Walk"], immunities=["cold"], conditions=[],
         attack=("Rend",7,10,2,4,4,1,4,"cold"), breath=("Cold Breath","constitution",15,30,6,9,8,"cold"), unarmed=(7,5), multi=3, body="dragon"),
]


def _slug(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")


def _definition(row: dict[str, object]) -> CombatantDefinition:
    slug = _slug(str(row["name"])); attack = row["attack"]; breath = row["breath"]
    attack_id = f"srd-{slug}-{_slug(attack[0])}"; save_id = f"srd-{slug}-{_slug(breath[0])}"
    resource_id = f"{save_id}-recharge"; walk, fly, climb, swim, burrow = row["movement"]
    strength, dexterity, constitution, intelligence, wisdom, charisma = row["saves"]
    return CombatantDefinition.model_validate({
        "schema_version": 1, "id": f"srd-{slug}", "name": row["name"], "archetype": "source-certified recharge monster",
        "challenge_rating": row["cr"], "kind": "monster", "size": row["size"], "armor_class": row["ac"],
        "max_hp": row["hp"], "speed_ft": row["speed"],
        "movement_modes": {"walk_ft": walk, "fly_ft": fly, "climb_ft": climb, "swim_ft": swim, "burrow_ft": burrow, "hover": False},
        "initiative_bonus": row["init"],
        "attacks": [{"id": attack_id, "name": attack[0], "weapon_id": f"{attack_id}-weapon", "attack_kind": "melee",
                     "attack_bonus": attack[1], "damage": {"count": attack[3], "size": attack[4], "bonus": attack[5]},
                     "damage_type": "piercing" if attack[0] == "Bite" else "slashing", "animation": "bite" if attack[0] == "Bite" else "slash",
                     "reach_ft": attack[2], "effects": [{"kind": "damage", "source": f"{row['name']} {attack[8].title()}",
                     "dice": {"count": attack[6], "size": attack[7], "bonus": 0}, "damage_type": attack[8]}]}],
        "primary_attack_id": attack_id, "unarmed_opportunity_attack": {"attack_bonus": row["unarmed"][0], "damage": row["unarmed"][1]},
        "attack_action": {"id": f"srd-{slug}-multiattack", "name": "Multiattack", "slots": [{"attack_ids": [attack_id]}] * row["multi"]},
        "save_actions": [{"id": save_id, "name": breath[0], "save_ability": breath[1], "dc": breath[2], "range_ft": breath[3],
                          "damage": {"count": breath[5], "size": breath[6], "bonus": 0}, "damage_type": breath[7],
                          "success_damage": "half", "resource_id": resource_id, "area_slots": breath[4], "priority": 100, "animation": "breath"}],
        "saving_throw_bonuses": {"strength": strength, "dexterity": dexterity, "constitution": constitution,
                                 "intelligence": intelligence, "wisdom": wisdom, "charisma": charisma},
        "skill_bonuses": row["skills"], "source_trait_names": row["traits"],
        "source_limited_use_names": [f"actions:{breath[0]} (Recharge 5-6)"],
        "damage_immunities": row["immunities"], "condition_immunities": row["conditions"],
        "resources": [{"id": resource_id, "name": breath[0], "max_uses": 1, "recharge_min_d6": 5}],
        "visual": {"armor": "natural", "main_hand": attack[0].lower(), "body_style": row["body"]}, "source": "SRD 5.2.1",
    })


def build_recharge_monster_definitions() -> dict[str, CombatantDefinition]:
    definitions = [_definition(row) for row in ROWS]
    return {item.id: item for item in definitions}
