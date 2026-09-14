from __future__ import annotations

from app.content.monster_catalog_2014_models import CatalogMonster2014
from app.domain.reactive_damage import MeleeHitReactiveDamage
from app.domain.spells import DefensiveSpellAction

SUPPORTED_DEFENSIVE_SPELLS_2014 = frozenset({"fire-shield"})


def defensive_spell_actions_2014(source: CatalogMonster2014) -> list[DefensiveSpellAction]:
    profile = source.spellcasting
    if profile is None or not any(spell.id == "fire-shield" for spell in profile.spells):
        return []
    common = dict(
        name="Fire Shield", level=4, range_ft=0, duration_minutes=10,
        target_policy="self", animation="fire-shield",
        source="SRD 5.1 / 2014 monster spell",
    )
    return [
        DefensiveSpellAction(
            id="fire-shield-warm", damage_resistances=["cold"], priority=1,
            melee_hit_reactive_damage=[MeleeHitReactiveDamage(
                id="fire-shield-warm", range_ft=5, dice_count=2, dice_size=8,
                damage_type="fire",
            )],
            **common,
        ),
        DefensiveSpellAction(
            id="fire-shield-chill", damage_resistances=["fire"], priority=0,
            melee_hit_reactive_damage=[MeleeHitReactiveDamage(
                id="fire-shield-chill", range_ft=5, dice_count=2, dice_size=8,
                damage_type="cold",
            )],
            **common,
        ),
    ]
