from __future__ import annotations

from app.content.monster_equipment import build_monster_visual
from app.domain.models import (
    CombatantTemplate,
    DamageType,
    HitControlEffect,
    SavingThrowAction,
    Weapon,
    WeaponAttack,
    WeaponAttackKind,
)
from app.domain.size import CreatureSize


def _melee(
    attack_id: str,
    name: str,
    bonus: int,
    dice_count: int,
    dice_size: int,
    damage_bonus: int,
    damage_type: DamageType,
    *,
    control: HitControlEffect | None = None,
) -> WeaponAttack:
    return WeaponAttack(
        id=attack_id,
        weapon=Weapon(
            id=attack_id,
            name=name,
            attack_kind=WeaponAttackKind.MELEE,
            dice_count=dice_count,
            dice_size=dice_size,
            damage_type=damage_type,
            animation="bite" if name == "Bite" else "claw",
            reach_ft=5,
        ),
        attack_bonus=bonus,
        damage_bonus=damage_bonus,
        control_effect=control,
    )


def build_control_monsters() -> list[CombatantTemplate]:
    crocodile_bite = _melee(
        "crocodile-bite", "Bite", 4, 1, 8, 2, DamageType.PIERCING,
        control=HitControlEffect(
            max_target_size=CreatureSize.MEDIUM,
            grapple_escape_dc=12,
            restrains_while_grappled=True,
        ),
    )
    giant_crab_claw = _melee(
        "giant-crab-claw", "Claw", 3, 1, 6, 1, DamageType.BLUDGEONING,
        control=HitControlEffect(
            max_target_size=CreatureSize.MEDIUM,
            grapple_escape_dc=11,
        ),
    )
    constrictor_bite = _melee(
        "constrictor-snake-bite", "Bite", 4, 1, 8, 2, DamageType.PIERCING,
    )
    return [
        CombatantTemplate(
            id="srd-crocodile", name="Crocodile", archetype="Crocodile",
            challenge_rating="1/2", kind="monster", size=CreatureSize.LARGE,
            armor_class=12, max_hp=13, speed_ft=20, initiative_bonus=0,
            weapon_attack=crocodile_bite,
            saving_throw_bonuses={
                "strength": 2, "dexterity": 0, "constitution": 3,
                "intelligence": -4, "wisdom": 0, "charisma": -3,
            },
            skill_bonuses={"athletics": 2, "acrobatics": 0},
            visual=build_monster_visual("natural", "bite", "crocodile"),
            source="SRD 5.2.1 Crocodile p. 347",
        ),
        CombatantTemplate(
            id="srd-giant-crab", name="Giant Crab", archetype="Giant Crab",
            challenge_rating="1/8", kind="monster", size=CreatureSize.MEDIUM,
            armor_class=15, max_hp=13, speed_ft=30, initiative_bonus=1,
            weapon_attack=giant_crab_claw,
            saving_throw_bonuses={
                "strength": 1, "dexterity": 1, "constitution": 0,
                "intelligence": -5, "wisdom": -1, "charisma": -4,
            },
            skill_bonuses={"athletics": 1, "acrobatics": 1},
            visual=build_monster_visual("natural", "claw", "giant-crab"),
            source="SRD 5.2.1 Giant Crab p. 350",
        ),
        CombatantTemplate(
            id="srd-constrictor-snake", name="Constrictor Snake", archetype="Constrictor Snake",
            challenge_rating="1/4", kind="monster", size=CreatureSize.LARGE,
            armor_class=13, max_hp=13, speed_ft=30, initiative_bonus=2,
            weapon_attack=constrictor_bite,
            saving_throw_actions=[SavingThrowAction(
                id="constrictor-snake-constrict",
                name="Constrict",
                save_ability="strength",
                dc=12,
                range_ft=5,
                target_max_size=CreatureSize.MEDIUM,
                damage_dice_count=3,
                damage_dice_size=4,
                damage_type="bludgeoning",
                grapple_escape_dc=12,
                animation="constrict",
            )],
            saving_throw_bonuses={
                "strength": 2, "dexterity": 2, "constitution": 1,
                "intelligence": -5, "wisdom": 0, "charisma": -4,
            },
            skill_bonuses={"athletics": 2, "acrobatics": 2},
            visual=build_monster_visual("natural", "bite", "constrictor-snake"),
            source="SRD 5.2.1 Constrictor Snake p. 347",
        ),
    ]
