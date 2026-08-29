from __future__ import annotations

from app.content.monster_charge_attacks import build_boar_gore, build_elk_ram, build_giant_boar_gore
from app.content.monster_equipment import build_monster_visual
from app.domain.models import CombatantTemplate
from app.domain.size import CreatureSize
from app.domain.traits import CombatTrait


def _beast(**kwargs) -> CombatantTemplate:
    return CombatantTemplate(kind="monster", **kwargs)


def build_boar() -> CombatantTemplate:
    return _beast(
        id="srd-boar", name="Boar", archetype="Boar", challenge_rating="1/4",
        size=CreatureSize.MEDIUM, armor_class=11, max_hp=13, speed_ft=40, initiative_bonus=0,
        weapon_attack=build_boar_gore(),
        combat_traits=[CombatTrait.CHARGE, CombatTrait.BLOODIED_FURY],
        visual=build_monster_visual("hide", "tusks", "boar"),
        source="SRD 5.2.1 Boar",
    )


def build_elk() -> CombatantTemplate:
    return _beast(
        id="srd-elk", name="Elk", archetype="Elk", challenge_rating="1/4",
        size=CreatureSize.LARGE, armor_class=10, max_hp=11, speed_ft=50, initiative_bonus=0,
        weapon_attack=build_elk_ram(),
        combat_traits=[CombatTrait.CHARGE],
        visual=build_monster_visual("hide", "antlers", "elk"),
        source="SRD 5.2.1 Elk",
    )


def build_giant_boar() -> CombatantTemplate:
    return _beast(
        id="srd-giant-boar", name="Giant Boar", archetype="Giant Boar", challenge_rating="2",
        size=CreatureSize.LARGE, armor_class=13, max_hp=42, speed_ft=40, initiative_bonus=0,
        weapon_attack=build_giant_boar_gore(),
        combat_traits=[CombatTrait.CHARGE, CombatTrait.BLOODIED_FURY],
        visual=build_monster_visual("hide", "tusks", "giant-boar"),
        source="SRD 5.2.1 Giant Boar",
    )
