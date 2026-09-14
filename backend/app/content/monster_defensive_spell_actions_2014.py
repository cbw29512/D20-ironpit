from __future__ import annotations

from app.content.monster_catalog_2014_models import CatalogMonster2014
from app.domain.spells import DefensiveSpellAction, SpellModifierEffect

SUPPORTED_DEFENSIVE_SPELLS_2014 = frozenset({"fire-shield"})


def _retaliation(damage_type: str) -> list[SpellModifierEffect]:
    return [SpellModifierEffect(
        kind="adjacent-melee-hit-reactive-damage",
        dice_count=2,
        dice_size=8,
        damage_type=damage_type,
    )]


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
            modifier_effects=_retaliation("fire"), **common,
        ),
        DefensiveSpellAction(
            id="fire-shield-chill", damage_resistances=["fire"], priority=0,
            modifier_effects=_retaliation("cold"), **common,
        ),
    ]
