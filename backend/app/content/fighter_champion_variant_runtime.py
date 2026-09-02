from __future__ import annotations

from app.content.armor_catalog import get_armor
from app.content.armor_class_rules import compile_worn_armor_class
from app.content.attack_bonus_rules import compile_weapon_attack_bonus
from app.content.character_math import fixed_hit_points, proficiency_bonus, saving_throw_bonuses, skill_bonus
from app.content.fighter_champion_variant_profiles import build_fighter_champion_variant_profile
from app.content.fighter_champion_variant_specs import FIGHTER_CHAMPION_VARIANT_SPECS
from app.content.fighting_style_rules import has_fighting_style
from app.content.weapon_catalog import build_weapon
from app.domain.actions import AttackActionDefinition, AttackActionSlot
from app.domain.models import CombatantTemplate, ResourceDefinition, VisualLoadout, WeaponAttack, WeaponAttackKind
from app.domain.progression import ProgressionCombatFeatures
from app.domain.traits import CombatTrait

_TACTICAL_MASTER_SAP_WEAPONS = {
    "great-weapon": ("greatsword",),
    "sword-shield": (),
    "archer": ("longbow",),
    "dual-wield": ("longbow",),
}


def _attack_count(level: int) -> int:
    return 1 if level < 5 else 2 if level < 11 else 3 if level < 20 else 4


def _resource_uses(level: int) -> tuple[int, int, int]:
    second_wind = 2 if level < 4 else 3 if level < 10 else 4
    action_surge = 0 if level < 2 else 1 if level < 17 else 2
    indomitable = 0 if level < 9 else 1 if level < 13 else 2 if level < 17 else 3
    return second_wind, action_surge, indomitable


def _resources(level: int) -> list[ResourceDefinition]:
    second_wind, action_surge, indomitable = _resource_uses(level)
    rows = [
        ("second-wind", "Second Wind", second_wind),
        ("action-surge", "Action Surge", action_surge),
        ("indomitable", "Indomitable", indomitable),
        ("adrenaline-rush", "Adrenaline Rush", proficiency_bonus(level)),
        ("relentless-endurance", "Relentless Endurance", 1),
    ]
    return [ResourceDefinition(id=resource_id, name=name, max_uses=uses)
            for resource_id, name, uses in rows if uses]


def _weapon_ability(weapon, primary_ability: str) -> str:
    if weapon.attack_kind is WeaponAttackKind.RANGED:
        return "dexterity"
    if weapon.finesse and primary_ability == "dexterity":
        return "dexterity"
    return "strength"


def _attack(profile, spec, weapon_id: str) -> WeaponAttack:
    weapon = build_weapon(weapon_id)
    ability = _weapon_ability(weapon, spec.primary_ability)
    modifier = profile.final_ability_scores.modifier(ability)
    attack_bonus = compile_weapon_attack_bonus(
        proficiency_bonus(profile.level) + modifier,
        profile.fighting_styles,
        weapon.attack_kind,
    )
    great_weapon = (
        has_fighting_style(profile.fighting_styles, "Great Weapon Fighting")
        and weapon.attack_kind is WeaponAttackKind.MELEE
        and (weapon.two_handed or weapon.versatile)
    )
    return WeaponAttack(
        id=f"{profile.build_id}-{weapon.id}", weapon=weapon,
        attack_bonus=attack_bonus, damage_bonus=modifier,
        damage_die_minimum=3 if great_weapon else None,
        attack_ability=ability, attack_ability_modifier=modifier,
    )


def _progression(level: int, styles: list[str], build_id: str) -> ProgressionCombatFeatures:
    return ProgressionCombatFeatures(
        critical_hit_minimum=18 if level >= 15 else 19,
        initiative_advantage=True,
        athletics_advantage=True,
        great_weapon_fighting=has_fighting_style(styles, "Great Weapon Fighting"),
        indomitable_bonus=level if level >= 9 else 0,
        tactical_master_sap_weapon_ids=(
            list(_TACTICAL_MASTER_SAP_WEAPONS[build_id]) if level >= 9 else []
        ),
        critical_move_fraction=0.5,
        tactical_shift_fraction=0.5 if level >= 5 else 0.0,
    )


def compile_fighter_champion_variant(build_id: str, level: int) -> CombatantTemplate:
    profile = build_fighter_champion_variant_profile(build_id, level)
    spec = FIGHTER_CHAMPION_VARIANT_SPECS[build_id]
    armor = get_armor(spec.armor)
    scores = profile.final_ability_scores
    armor_class = compile_worn_armor_class(
        armor.base_ac, armor.category, scores.modifier("dexterity"), profile.fighting_styles,
        wielding_shield=spec.shield, shield_trained=True,
    )
    weapon_ids = (spec.primary_weapon, *spec.secondary_weapons)
    attacks = [_attack(profile, spec, weapon_id) for weapon_id in weapon_ids]
    attack_ids = [attack.id for attack in attacks]
    action = AttackActionDefinition(
        id="attack", name="Attack", is_attack_action=True,
        slots=[AttackActionSlot(attack_ids=attack_ids) for _ in range(_attack_count(level))],
    )
    athletics = skill_bonus(scores, level, "strength", proficient="Athletics" in profile.skill_proficiencies)
    acrobatics = skill_bonus(scores, level, "dexterity", proficient="Acrobatics" in profile.skill_proficiencies)
    return CombatantTemplate(
        id=profile.template_id, name=profile.character_name, archetype=profile.class_name,
        level=level, kind="character", armor_class=armor_class,
        max_hp=fixed_hit_points(level, 10, scores.modifier("constitution")), speed_ft=30,
        initiative_bonus=scores.modifier("dexterity"), ability_scores=scores,
        weapon_attack=attacks[0], alternate_weapon_attacks=attacks[1:], attack_action=action,
        saving_throw_bonuses=saving_throw_bonuses(scores, level, ("strength", "constitution")),
        skill_bonuses={"athletics": athletics, "acrobatics": acrobatics},
        combat_traits=[CombatTrait.SAVAGE_ATTACKER, CombatTrait.ADRENALINE_RUSH, CombatTrait.RELENTLESS_ENDURANCE],
        fighting_style=profile.fighting_style, fighting_styles=profile.fighting_styles,
        weapon_masteries=profile.weapon_masteries,
        visual=VisualLoadout(
            armor=spec.armor, main_hand=spec.primary_weapon,
            off_hand="shield" if spec.shield else (spec.secondary_weapons[0] if build_id == "dual-wield" else None),
            body_style="humanoid",
        ),
        resources=_resources(level), progression_features=_progression(level, profile.fighting_styles, build_id),
        source="; ".join(profile.source_references),
    )
