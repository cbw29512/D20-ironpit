from __future__ import annotations

from app.content.canonical_hero_policy import canonical_template_id
from app.content.cleric_combat_levels import CLERIC_COMBAT_LEVELS, cleric_combat_features
from app.content.cleric_life_domain import AID, LESSER_RESTORATION, disciple_of_life_bonus
from app.content.healing_spell_effects import build_cure_wounds, build_healing_word
from app.content.hero_combat_feature_registry import unsupported_hero_engine_features
from app.content.hero_progressions import HERO_BY_CLASS
from app.content.offensive_spell_effects import build_guiding_bolt, build_inflict_wounds, build_sacred_flame
from app.content.spell_effects import BLESS, SHIELD_OF_FAITH
from app.domain.models import (
    CombatantTemplate, DamageType, ResourceDefinition, VisualLoadout,
    Weapon, WeaponAttack, WeaponAttackKind,
)
from app.domain.traits import CombatTrait


def _modifier(score: int) -> int:
    return (score - 10) // 2


def _mace_attack(attack_bonus: int) -> WeaponAttack:
    return WeaponAttack(
        id="seraphine-mace",
        weapon=Weapon(
            id="mace", name="Mace", attack_kind=WeaponAttackKind.MELEE,
            dice_count=1, dice_size=6, damage_type=DamageType.BLUDGEONING,
            animation="blunt-strike", reach_ft=5,
        ),
        attack_bonus=attack_bonus, damage_bonus=0,
    )


def _resources(level: int) -> list[ResourceDefinition]:
    row = CLERIC_COMBAT_LEVELS[level]
    slots = [
        ResourceDefinition(id=f"spell-slot-{spell_level}", name=f"Level {spell_level} Spell Slot", max_uses=uses)
        for spell_level, uses in enumerate(row.spell_slots, start=1) if uses
    ]
    channel = [ResourceDefinition(id="channel-divinity", name="Channel Divinity", max_uses=row.channel_divinity_uses)] if row.channel_divinity_uses else []
    return [
        *slots, *channel,
        ResourceDefinition(id="adrenaline-rush", name="Adrenaline Rush", max_uses=row.proficiency_bonus),
        ResourceDefinition(id="relentless-endurance", name="Relentless Endurance", max_uses=1),
    ]


def _source(level: int) -> str:
    return (
        f"D&D Beyond Basic Rules 2024: Cleric level {level}, Orc, Sage, Protector, "
        "Sacred Flame, Bless, Cure Wounds, Guiding Bolt, Shield of Faith, "
        + ("Healing Word, Channel Divinity, " if level >= 2 else "")
        + ("Life Domain, Aid, Lesser Restoration, Disciple of Life, " if level >= 3 else "")
        + ("Ability Score Improvement, Mending, Inflict Wounds, " if level >= 4 else "")
        + "Equipment"
    )


def _build_seraphine(level: int) -> CombatantTemplate:
    if level not in CLERIC_COMBAT_LEVELS:
        raise ValueError(f"Seraphine Cleric level {level} must be between 1 and 20.")
    unsupported = unsupported_hero_engine_features(cleric_combat_features(level))
    if unsupported:
        raise ValueError(f"Seraphine Cleric level {level} awaits combat support for: {', '.join(unsupported)}")
    row = CLERIC_COMBAT_LEVELS[level]
    hero = HERO_BY_CLASS["cleric"]
    wisdom_modifier = _modifier(row.wisdom)
    intelligence_modifier = 2
    charisma_modifier = _modifier(row.charisma)
    save_dc = 8 + row.proficiency_bonus + wisdom_modifier
    spell_attack_bonus = row.proficiency_bonus + wisdom_modifier
    life_bonus = disciple_of_life_bonus(1) if level >= 3 else 0
    healing = [build_cure_wounds(wisdom_modifier, life_bonus)]
    if level >= 2:
        healing.append(build_healing_word(wisdom_modifier, life_bonus))
    defenses = [BLESS.model_copy(deep=True), SHIELD_OF_FAITH.model_copy(deep=True)]
    if level >= 3:
        defenses.insert(0, AID.model_copy(deep=True))
    save_spells = [build_sacred_flame(save_dc, level)]
    if level >= 4:
        save_spells.append(build_inflict_wounds(save_dc))
    traits = [CombatTrait.ADRENALINE_RUSH, CombatTrait.RELENTLESS_ENDURANCE]
    if level >= 3:
        traits.append(CombatTrait.LIFE_DOMAIN)
    return CombatantTemplate(
        id=canonical_template_id("cleric", level), name=hero.hero_name, archetype=hero.class_name,
        level=level, kind="character", armor_class=row.armor_class, max_hp=row.max_hp,
        speed_ft=30, initiative_bonus=0, weapon_attack=_mace_attack(row.proficiency_bonus),
        spell_save_actions=save_spells, spell_attack_actions=[build_guiding_bolt(spell_attack_bonus)],
        defensive_spell_actions=defenses, healing_actions=healing,
        condition_removal_actions=[LESSER_RESTORATION.model_copy(deep=True)] if level >= 3 else [],
        saving_throw_bonuses={
            "strength": 0, "dexterity": 0, "constitution": 0, "intelligence": intelligence_modifier,
            "wisdom": row.proficiency_bonus + wisdom_modifier,
            "charisma": row.proficiency_bonus + charisma_modifier,
        },
        skill_bonuses={
            "athletics": 0, "acrobatics": 0,
            "arcana": row.proficiency_bonus + intelligence_modifier,
            "history": row.proficiency_bonus + intelligence_modifier,
            "medicine": row.proficiency_bonus + wisdom_modifier,
            "persuasion": row.proficiency_bonus + charisma_modifier,
        },
        combat_traits=traits,
        visual=VisualLoadout(armor="chain-shirt", main_hand="mace", off_hand="shield", body_style="humanoid"),
        resources=_resources(level), source=_source(level),
    )


def build_seraphine_dawnshield_level(level: int) -> CombatantTemplate:
    """Compile Seraphine from the complete 1-20 Cleric table; missing combat content fails closed."""
    return _build_seraphine(level)


def build_seraphine_dawnshield() -> CombatantTemplate:
    return build_seraphine_dawnshield_level(1)


def build_seraphine_dawnshield_level_two() -> CombatantTemplate:
    return build_seraphine_dawnshield_level(2)


def build_seraphine_dawnshield_level_three() -> CombatantTemplate:
    return build_seraphine_dawnshield_level(3)


def build_seraphine_dawnshield_level_four() -> CombatantTemplate:
    return build_seraphine_dawnshield_level(4)
