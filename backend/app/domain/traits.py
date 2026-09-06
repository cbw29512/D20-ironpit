from enum import StrEnum


class CombatTrait(StrEnum):
    PACK_TACTICS = "pack-tactics"
    SAVAGE_ATTACKER = "savager-attacker"
    ADRENALINE_RUSH = "adrenaline-rush"
    RELENTLESS_ENDURANCE = "relentless-endurance"
    CHARGE = "charge"
    BLOODIED_FURY = "bloodied-fury"
    BLOODIED_ATTACK_SAVE_ADVANTAGE = "bloodied-attack-save-advantage"
    TARGET_MISSING_HP_ATTACK_ADVANTAGE = "target-missing-hp-attack-advantage"
    SWARM = "swarm"
    UNDEAD_FORTITUDE = "undead-fortitude"
    REGENERATION = "regeneration"
    END_TURN_DAMAGE_AURA = "end-turn-damage-aura"
    DEATH_TRIGGER_SAVE = "death-trigger-save"
    ALLY_ROLL_AURA = "ally-roll-aura"
    LIFE_DOMAIN = "life-domain"
    MAGIC_RESISTANCE = "magic-resistance"
