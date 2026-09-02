from __future__ import annotations

from dataclasses import dataclass

from app.domain.character_builds import AbilityIncrease, AbilityScores
from app.domain.class_loadouts import MeleeLoadoutKind


@dataclass(frozen=True)
class FighterChampionVariantSpec:
    build_id: str
    primary_ability: str
    base_scores: AbilityScores
    background_increases: tuple[AbilityIncrease, ...]
    fighting_styles: tuple[str, str]
    armor: str
    shield: bool
    primary_weapon: str
    secondary_weapons: tuple[str, ...]
    mastery_priority: tuple[str, ...]
    class_equipment_option: str
    class_equipment: tuple[str, ...]
    loadout_kind: MeleeLoadoutKind | None
    asi_plan: dict[int, tuple[AbilityIncrease, ...]]
    boon_ability: str


_STR_BASE = AbilityScores(
    strength=15, dexterity=13, constitution=14,
    intelligence=10, wisdom=10, charisma=10,
)
_DEX_BASE = AbilityScores(
    strength=10, dexterity=15, constitution=14,
    intelligence=10, wisdom=13, charisma=10,
)
_STR_BG = (AbilityIncrease(ability="strength", amount=2), AbilityIncrease(ability="constitution", amount=1))
_DEX_BG = (AbilityIncrease(ability="dexterity", amount=2), AbilityIncrease(ability="constitution", amount=1))
_STR_ASI = {
    4: (AbilityIncrease(ability="strength", amount=1), AbilityIncrease(ability="constitution", amount=1)),
    6: (AbilityIncrease(ability="strength", amount=2),),
    8: (AbilityIncrease(ability="constitution", amount=2),),
    12: (AbilityIncrease(ability="constitution", amount=2),),
    14: (AbilityIncrease(ability="dexterity", amount=2),),
    16: (AbilityIncrease(ability="dexterity", amount=2),),
}
_DEX_ASI = {
    4: (AbilityIncrease(ability="dexterity", amount=1), AbilityIncrease(ability="constitution", amount=1)),
    6: (AbilityIncrease(ability="dexterity", amount=2),),
    8: (AbilityIncrease(ability="constitution", amount=2),),
    12: (AbilityIncrease(ability="constitution", amount=2),),
    14: (AbilityIncrease(ability="wisdom", amount=2),),
    16: (AbilityIncrease(ability="wisdom", amount=2),),
}


def _spec(**kwargs) -> FighterChampionVariantSpec:
    return FighterChampionVariantSpec(**kwargs)


FIGHTER_CHAMPION_VARIANT_SPECS = {
    "great-weapon": _spec(
        build_id="great-weapon", primary_ability="strength", base_scores=_STR_BASE,
        background_increases=_STR_BG, fighting_styles=("Great Weapon Fighting", "Defense"),
        armor="chain-mail", shield=False, primary_weapon="greatsword",
        secondary_weapons=("shortbow",),
        mastery_priority=("greatsword", "javelin", "flail", "longsword", "shortbow", "scimitar"),
        class_equipment_option="package",
        class_equipment=("Chain Mail", "Greatsword", "Flail", "8 Javelins", "Dungeoneer's Pack", "4 GP"),
        loadout_kind="two-handed", asi_plan=_STR_ASI, boon_ability="dexterity",
    ),
    "sword-shield": _spec(
        build_id="sword-shield", primary_ability="strength", base_scores=_STR_BASE,
        background_increases=_STR_BG, fighting_styles=("Defense", "Archery"),
        armor="chain-mail", shield=True, primary_weapon="longsword",
        secondary_weapons=("shortbow",),
        mastery_priority=("longsword", "javelin", "flail", "shortbow", "scimitar", "greatsword"),
        class_equipment_option="gold",
        class_equipment=("Chain Mail", "Shield", "Longsword", "4 Javelins", "Dungeoneer's Pack"),
        loadout_kind="one-hander-shield", asi_plan=_STR_ASI, boon_ability="dexterity",
    ),
    "archer": _spec(
        build_id="archer", primary_ability="dexterity", base_scores=_DEX_BASE,
        background_increases=_DEX_BG, fighting_styles=("Archery", "Defense"),
        armor="studded-leather", shield=False, primary_weapon="longbow",
        secondary_weapons=("shortsword", "scimitar"),
        mastery_priority=("longbow", "shortsword", "scimitar", "shortbow", "javelin", "longsword"),
        class_equipment_option="package",
        class_equipment=("Studded Leather Armor", "Scimitar", "Shortsword", "Longbow", "20 Arrows", "Quiver", "Dungeoneer's Pack", "11 GP"),
        loadout_kind=None, asi_plan=_DEX_ASI, boon_ability="wisdom",
    ),
    "dual-wield": _spec(
        build_id="dual-wield", primary_ability="dexterity", base_scores=_DEX_BASE,
        background_increases=_DEX_BG, fighting_styles=("Two-Weapon Fighting", "Defense"),
        armor="studded-leather", shield=False, primary_weapon="scimitar",
        secondary_weapons=("shortsword", "longbow"),
        mastery_priority=("scimitar", "shortsword", "longbow", "javelin", "longsword", "greatsword"),
        class_equipment_option="package",
        class_equipment=("Studded Leather Armor", "Scimitar", "Shortsword", "Longbow", "20 Arrows", "Quiver", "Dungeoneer's Pack", "11 GP"),
        loadout_kind="dual-wield", asi_plan=_DEX_ASI, boon_ability="wisdom",
    ),
}
