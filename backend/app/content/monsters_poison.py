from __future__ import annotations

from app.content.monster_equipment import build_monster_visual
from app.domain.models import (
    CombatantTemplate,
    DamageType,
    HitControlEffect,
    Weapon,
    WeaponAttack,
    WeaponAttackKind,
)
from app.domain.size import CreatureSize


def build_poison_monsters() -> list[CombatantTemplate]:
    bite = WeaponAttack(
        id="giant-centipede-bite",
        weapon=Weapon(
            id="giant-centipede-bite",
            name="Bite",
            attack_kind=WeaponAttackKind.MELEE,
            dice_count=1,
            dice_size=4,
            damage_type=DamageType.PIERCING,
            animation="bite",
            reach_ft=5,
        ),
        attack_bonus=4,
        damage_bonus=2,
        control_effect=HitControlEffect(
            condition_id="poisoned",
            expires_at_start_of_source_turn=True,
        ),
    )
    return [CombatantTemplate(
        id="srd-giant-centipede",
        name="Giant Centipede",
        archetype="Giant Centipede",
        challenge_rating="1/4",
        kind="monster",
        size=CreatureSize.SMALL,
        armor_class=14,
        max_hp=9,
        speed_ft=30,
        initiative_bonus=2,
        weapon_attack=bite,
        saving_throw_bonuses={
            "strength": -3, "dexterity": 2, "constitution": 1,
            "intelligence": -5, "wisdom": -2, "charisma": -4,
        },
        skill_bonuses={"athletics": -3, "acrobatics": 2},
        visual=build_monster_visual("natural", "bite", "giant-centipede"),
        source="SRD 5.2.1 Giant Centipede p. 349",
    )]
