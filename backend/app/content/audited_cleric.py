from __future__ import annotations

from app.content.canonical_hero_policy import canonical_template_id
from app.content.healing_spell_effects import build_cure_wounds
from app.content.hero_progressions import HERO_BY_CLASS
from app.content.level_resources import orc_adrenaline_rush_uses
from app.content.offensive_spell_effects import build_guiding_bolt, build_sacred_flame
from app.content.spell_effects import BLESS, SHIELD_OF_FAITH
from app.content.spell_slot_progression import spell_slot_resources
from app.domain.models import (
    CombatantTemplate,
    DamageType,
    ResourceDefinition,
    VisualLoadout,
    Weapon,
    WeaponAttack,
    WeaponAttackKind,
)
from app.domain.traits import CombatTrait


def _mace_attack() -> WeaponAttack:
    return WeaponAttack(
        id="seraphine-mace",
        weapon=Weapon(
            id="mace",
            name="Mace",
            attack_kind=WeaponAttackKind.MELEE,
            dice_count=1,
            dice_size=6,
            damage_type=DamageType.BLUDGEONING,
            animation="blunt-strike",
            reach_ft=5,
        ),
        attack_bonus=3,
        damage_bonus=1,
    )


def _resources(level: int) -> list[ResourceDefinition]:
    slots = [
        ResourceDefinition(id=resource_id, name=f"Level {resource_id[-1]} Spell Slot", max_uses=uses)
        for resource_id, uses in spell_slot_resources("cleric", level).items()
    ]
    return [
        *slots,
        ResourceDefinition(
            id="adrenaline-rush",
            name="Adrenaline Rush",
            max_uses=orc_adrenaline_rush_uses(level),
        ),
        ResourceDefinition(id="relentless-endurance", name="Relentless Endurance", max_uses=1),
    ]


def build_seraphine_dawnshield() -> CombatantTemplate:
    """Level-1 canonical Cleric using only fully certified combat-facing choices."""
    level = 1
    hero = HERO_BY_CLASS["cleric"]
    return CombatantTemplate(
        id=canonical_template_id("cleric", level),
        name=hero.hero_name,
        archetype=hero.class_name,
        level=level,
        kind="character",
        armor_class=17,
        max_hp=10,
        speed_ft=30,
        initiative_bonus=2,
        weapon_attack=_mace_attack(),
        spell_save_actions=[build_sacred_flame(13, level)],
        spell_attack_actions=[build_guiding_bolt(5)],
        defensive_spell_actions=[BLESS.model_copy(deep=True), SHIELD_OF_FAITH.model_copy(deep=True)],
        healing_actions=[build_cure_wounds(3)],
        saving_throw_bonuses={
            "strength": 1, "dexterity": 2, "constitution": 2,
            "intelligence": -1, "wisdom": 5, "charisma": 2,
        },
        skill_bonuses={
            "athletics": 1, "acrobatics": 2,
            "arcana": 1, "history": 1, "medicine": 5, "persuasion": 2,
        },
        combat_traits=[CombatTrait.ADRENALINE_RUSH, CombatTrait.RELENTLESS_ENDURANCE],
        visual=VisualLoadout(
            armor="chain-shirt",
            main_hand="mace",
            off_hand="shield",
            body_style="humanoid",
        ),
        resources=_resources(level),
        source=(
            "D&D Beyond Basic Rules 2024: Cleric level 1, Orc, Sage, Protector, "
            "Sacred Flame, Bless, Cure Wounds, Guiding Bolt, Shield of Faith, Equipment"
        ),
    )
