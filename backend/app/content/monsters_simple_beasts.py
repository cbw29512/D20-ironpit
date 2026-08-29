from __future__ import annotations

from app.content.monster_equipment import build_monster_visual
from app.content.monster_simple_beast_attacks import (
    build_camel_bite,
    build_deer_ram,
    build_draft_horse_hooves,
    build_giant_badger_bite,
)
from app.domain.models import CombatantTemplate, DamageType
from app.domain.size import CreatureSize


def _beast(**kwargs) -> CombatantTemplate:
    return CombatantTemplate(kind="monster", **kwargs)


def build_camel() -> CombatantTemplate:
    return _beast(
        id="srd-camel", name="Camel", archetype="Camel", challenge_rating="1/8",
        size=CreatureSize.LARGE, armor_class=10, max_hp=17, speed_ft=50, initiative_bonus=-1,
        weapon_attack=build_camel_bite(),
        visual=build_monster_visual("fur", "bite", "camel"),
        source="SRD 5.2.1 / 2024 Basic Rules Camel",
    )


def build_deer() -> CombatantTemplate:
    return _beast(
        id="srd-deer", name="Deer", archetype="Deer", challenge_rating="0",
        size=CreatureSize.MEDIUM, armor_class=13, max_hp=4, speed_ft=50, initiative_bonus=3,
        weapon_attack=build_deer_ram(),
        visual=build_monster_visual("fur", "horns", "deer"),
        source="SRD 5.2.1 / 2024 Basic Rules Deer",
    )


def build_draft_horse() -> CombatantTemplate:
    return _beast(
        id="srd-draft-horse", name="Draft Horse", archetype="Draft Horse", challenge_rating="1/4",
        size=CreatureSize.LARGE, armor_class=10, max_hp=15, speed_ft=40, initiative_bonus=0,
        weapon_attack=build_draft_horse_hooves(),
        visual=build_monster_visual("fur", "hooves", "horse"),
        source="SRD 5.2.1 / 2024 Basic Rules Draft Horse",
    )


def build_giant_badger() -> CombatantTemplate:
    return _beast(
        id="srd-giant-badger", name="Giant Badger", archetype="Giant Badger", challenge_rating="1/4",
        size=CreatureSize.MEDIUM, armor_class=13, max_hp=15, speed_ft=30, initiative_bonus=0,
        weapon_attack=build_giant_badger_bite(),
        damage_resistances=[DamageType.POISON],
        visual=build_monster_visual("fur", "bite", "badger"),
        source="SRD 5.2.1 / 2024 Basic Rules Giant Badger",
    )
