from __future__ import annotations

from app.content.canonical_class_combat_spines import canonical_combat_features
from app.content.canonical_hero_policy import canonical_template_id
from app.content.hero_combat_feature_registry import unsupported_hero_engine_features
from app.content.hero_progressions import HERO_BY_CLASS
from app.content.offensive_spell_effects import build_eldritch_blast
from app.content.warlock_combat_levels import WARLOCK_COMBAT_LEVELS
from app.domain.models import (
    CombatantTemplate, DamageType, ResourceDefinition, VisualLoadout,
    Weapon, WeaponAttack, WeaponAttackKind,
)
from app.domain.traits import CombatTrait


def _pact_longsword() -> WeaponAttack:
    return WeaponAttack(
        id="varek-pact-longsword",
        weapon=Weapon(
            id="longsword", name="Pact Longsword", attack_kind=WeaponAttackKind.MELEE,
            dice_count=1, dice_size=8, damage_type=DamageType.SLASHING,
            animation="eldritch-slash", reach_ft=5,
        ),
        attack_bonus=5, damage_bonus=3,
        attack_ability="charisma", attack_ability_modifier=3,
    )


def build_varek_ashenmark_level(level: int) -> CombatantTemplate:
    if level != 1:
        raise ValueError("Varek Warlock progression beyond level 1 is not yet certified.")
    row = WARLOCK_COMBAT_LEVELS[level]
    unsupported = unsupported_hero_engine_features(canonical_combat_features("warlock", level))
    if unsupported:
        raise ValueError(f"Varek Warlock level {level} awaits combat support for: {', '.join(unsupported)}")
    hero = HERO_BY_CLASS["warlock"]
    return CombatantTemplate(
        id=canonical_template_id("warlock", level), name=hero.hero_name,
        archetype=hero.class_name, level=level, kind="character",
        armor_class=11, max_hp=8, speed_ft=30, initiative_bonus=0,
        weapon_attack=_pact_longsword(),
        spell_attack_actions=[build_eldritch_blast(5, level)],
        saving_throw_bonuses={
            "strength": 0, "dexterity": 0, "constitution": 0,
            "intelligence": 1, "wisdom": 4, "charisma": 5,
        },
        skill_bonuses={
            "athletics": 0, "acrobatics": 0, "arcana": 3,
            "intimidation": 5, "insight": 4, "religion": 3,
        },
        combat_traits=[CombatTrait.ADRENALINE_RUSH, CombatTrait.RELENTLESS_ENDURANCE],
        visual=VisualLoadout(
            armor="leather-armor", main_hand="pact-longsword",
            off_hand="arcane-focus-orb", body_style="humanoid",
        ),
        resources=[
            ResourceDefinition(
                id=f"pact-slot-{row.pact_slot_level}",
                name=f"Level {row.pact_slot_level} Pact Magic Slot", max_uses=row.pact_slots,
            ),
            ResourceDefinition(id="adrenaline-rush", name="Adrenaline Rush", max_uses=row.proficiency_bonus),
            ResourceDefinition(id="relentless-endurance", name="Relentless Endurance", max_uses=1),
        ],
        source=(
            "D&D Beyond Basic Rules 2024 / SRD 5.2.1: Warlock 1, Pact of the Blade, "
            "Eldritch Blast, Orc, Acolyte, Leather Armor"
        ),
    )


def build_varek_ashenmark() -> CombatantTemplate:
    return build_varek_ashenmark_level(1)
