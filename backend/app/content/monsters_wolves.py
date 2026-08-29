from __future__ import annotations

from app.content.monster_equipment import build_monster_visual
from app.content.monster_wolf_attacks import build_dire_wolf_bite, build_wolf_bite
from app.domain.models import CombatantTemplate
from app.domain.size import CreatureSize
from app.domain.traits import CombatTrait


def build_wolf() -> CombatantTemplate:
    return CombatantTemplate(
        id="srd-wolf",
        name="Wolf",
        archetype="Wolf",
        challenge_rating="1/4",
        kind="monster",
        size=CreatureSize.MEDIUM,
        armor_class=12,
        max_hp=11,
        speed_ft=40,
        initiative_bonus=2,
        weapon_attack=build_wolf_bite(),
        combat_traits=[CombatTrait.PACK_TACTICS],
        visual=build_monster_visual("fur", "bite", "wolf"),
        source="SRD 5.2.1 Wolf p. 364",
    )


def build_dire_wolf() -> CombatantTemplate:
    return CombatantTemplate(
        id="srd-dire-wolf",
        name="Dire Wolf",
        archetype="Dire Wolf",
        challenge_rating="1",
        kind="monster",
        size=CreatureSize.LARGE,
        armor_class=14,
        max_hp=22,
        speed_ft=50,
        initiative_bonus=2,
        weapon_attack=build_dire_wolf_bite(),
        combat_traits=[CombatTrait.PACK_TACTICS],
        visual=build_monster_visual("fur", "bite", "dire-wolf"),
        source="SRD 5.2.1 Dire Wolf p. 347",
    )
