from __future__ import annotations

from app.content.monster_bear_attacks import (
    build_black_bear_rend,
    build_brown_bear_bite,
    build_brown_bear_claw,
)
from app.content.monster_equipment import build_monster_visual
from app.domain.actions import AttackActionDefinition, AttackActionSlot
from app.domain.models import CombatantTemplate
from app.domain.size import CreatureSize


def build_black_bear() -> CombatantTemplate:
    rend = build_black_bear_rend()
    return CombatantTemplate(
        id="srd-black-bear",
        name="Black Bear",
        archetype="Black Bear",
        challenge_rating="1/2",
        kind="monster",
        size=CreatureSize.MEDIUM,
        armor_class=11,
        max_hp=19,
        speed_ft=30,
        initiative_bonus=1,
        weapon_attack=rend,
        attack_action=AttackActionDefinition(
            id="black-bear-multiattack",
            name="Multiattack",
            slots=[
                AttackActionSlot(attack_ids=[rend.id]),
                AttackActionSlot(attack_ids=[rend.id]),
            ],
        ),
        visual=build_monster_visual("fur", "claw", "bear"),
        source="SRD 5.2.1 / 2024 Basic Rules Black Bear",
    )


def build_brown_bear() -> CombatantTemplate:
    bite = build_brown_bear_bite()
    claw = build_brown_bear_claw()
    return CombatantTemplate(
        id="srd-brown-bear",
        name="Brown Bear",
        archetype="Brown Bear",
        challenge_rating="1",
        kind="monster",
        size=CreatureSize.LARGE,
        armor_class=11,
        max_hp=22,
        speed_ft=40,
        initiative_bonus=1,
        weapon_attack=bite,
        alternate_weapon_attacks=[claw],
        attack_action=AttackActionDefinition(
            id="brown-bear-multiattack",
            name="Multiattack",
            slots=[
                AttackActionSlot(attack_ids=[bite.id]),
                AttackActionSlot(attack_ids=[claw.id]),
            ],
        ),
        visual=build_monster_visual("fur", "claw", "bear"),
        source="SRD 5.2.1 / 2024 Basic Rules Brown Bear",
    )
