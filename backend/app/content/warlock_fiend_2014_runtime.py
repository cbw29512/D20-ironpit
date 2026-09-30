from __future__ import annotations

from app.content.character_math import fixed_hit_points, proficiency_bonus, saving_throw_bonuses
from app.content.monster_equipment import build_light_crossbow
from app.content.sorcerer_draconic_2014_spells import burning_hands_2014, fireball_2014, poison_spray_2014, shatter_2014
from app.content.shared_effect_removal_spells_2014 import dispel_magic_2014
from app.content.shared_damage_spells_2014 import flame_strike_2014
from app.content.warlock_2014_progression import warlock_2014_level
from app.content.warlock_2014_spells import (
    circle_of_death_2014,
    eldritch_blast_2014,
    finger_of_death_2014,
    hex_2014,
    scorching_ray_2014,
)
from app.content.warlock_fiend_2014_profile import build_varek_ashenmark_2014_profile
from app.content.warlock_fiend_2014_features import build_warlock_fiend_2014_features
from app.domain.actions import HpThresholdConditionAction, HpThresholdInstantDeathAction
from app.domain.models import CombatantTemplate, ResourceDefinition, VisualLoadout, WeaponAttack

def build_varek_ashenmark_2014(level: int) -> CombatantTemplate:
    if level not in range(1, 21): raise ValueError("2014 Varek runtime currently certifies levels 1 through 20.")
    profile = build_varek_ashenmark_2014_profile(level)
    scores = profile.final_ability_scores
    pb = proficiency_bonus(level)
    dex = scores.modifier("dexterity")
    cha = scores.modifier("charisma")
    crossbow = build_light_crossbow()
    row = warlock_2014_level(level)
    return CombatantTemplate(
        id=profile.template_id,
        name=profile.character_name,
        archetype="Warlock",
        level=level,
        kind="character",
        ruleset="2014",
        ability_scores=scores,
        armor_class=11 + dex,
        max_hp=fixed_hit_points(level, 8, scores.modifier("constitution")),
        speed_ft=30,
        movement_modes={"walk_ft": 30},
        initiative_bonus=dex,
        weapon_attack=WeaponAttack(
            id="varek-2014-light-crossbow",
            weapon=crossbow,
            attack_bonus=pb + dex,
            damage_bonus=dex,
            attack_ability="dexterity",
            attack_ability_modifier=dex,
        ),
        spell_attack_actions=[
            eldritch_blast_2014(
                pb + cha, level,
                damage_bonus=cha if level >= 2 else 0,
                range_ft=300 if level >= 2 else 120,
            ),
            *([scorching_ray_2014(pb + cha)] if level >= 3 else []),
        ],
        spell_save_actions=[
            poison_spray_2014(8 + pb + cha, level),
            burning_hands_2014(8 + pb + cha),
            *([shatter_2014(8 + pb + cha)] if level >= 3 else []),
            *([fireball_2014(8 + pb + cha)] if level >= 5 else []),
            *([flame_strike_2014(8 + pb + cha)] if level >= 9 else []),
        ],
        targeted_concentration_damage_actions=[hex_2014()],
        progression_features=build_warlock_fiend_2014_features(level, row.pact_slot_level),
        saving_throw_actions=[
            *([circle_of_death_2014(8 + pb + cha)] if level >= 11 else []),
            *([finger_of_death_2014(8 + pb + cha)] if level >= 13 else []),
        ],
        hp_threshold_instant_death_actions=(
            [HpThresholdInstantDeathAction(
                id="power-word-kill",
                name="Power Word Kill",
                action_cost="action",
                range_ft=60,
                requires_target_sight=True, max_current_hp=100,
                resource_id="mystic-arcanum-9",
                resource_cost=1,
                magical_effect=True,
                animation="instant-death",
            )] if level >= 17 else []
        ),
        hp_threshold_condition_actions=(
            [HpThresholdConditionAction(
                id="power-word-stun",
                name="Power Word Stun",
                action_cost="action",
                range_ft=60,
                requires_target_sight=True, max_current_hp=150,
                condition_id="stunned",
                repeat_save_ability="constitution",
                repeat_save_dc=8 + pb + cha,
                repeat_save_timing="target_turn_end",
                resource_id="mystic-arcanum-8",
                resource_cost=1,
                magical_effect=True,
                animation="spell-condition",
            )] if level >= 15 else []
        ),
        saving_throw_bonuses=saving_throw_bonuses(scores, level, ("wisdom", "charisma")),
        skill_bonuses={"arcana": scores.modifier("intelligence") + pb, "history": scores.modifier("intelligence") + pb,
                       **({"deception": cha + pb, "persuasion": cha + pb} if level >= 18 else {})},
        resources=[
            ResourceDefinition(
                id=f"spell-slot-{row.pact_slot_level}",
                name=f"Pact Magic Slot {row.pact_slot_level}",
                max_uses=row.pact_slots,
            ),
            *([ResourceDefinition(
                id="dark-ones-own-luck",
                name="Dark One's Own Luck",
                max_uses=1,
            )] if level >= 6 else []),
            *([ResourceDefinition(
                id="mystic-arcanum-6",
                name="Mystic Arcanum (6th Level)",
                max_uses=1,
            )] if level >= 11 else []),
            *([ResourceDefinition(
                id="mystic-arcanum-7",
                name="Mystic Arcanum (7th Level)",
                max_uses=1,
            )] if level >= 13 else []),
            *([ResourceDefinition(
                id="hurl-through-hell",
                name="Hurl Through Hell",
                max_uses=1,
            )] if level >= 14 else []),
            *([ResourceDefinition(
                id="mystic-arcanum-8",
                name="Mystic Arcanum (8th Level)",
                max_uses=1,
            )] if level >= 15 else []),
            *([ResourceDefinition(
                id="mystic-arcanum-9",
                name="Mystic Arcanum (9th Level)",
                max_uses=1,
            )] if level >= 17 else []),
            *([ResourceDefinition(
                id="eldritch-master",
                name="Eldritch Master",
                max_uses=1,
            )] if level >= 20 else []),
        ],
        effect_removal_actions=([dispel_magic_2014("charisma")] if level >= 6 else []),
        visual=VisualLoadout(armor="leather-armor", main_hand="arcane-focus", body_style="humanoid"),
        source="D&D Basic Rules 2014: Human; Sage; Warlock; Fiend Patron; Equipment",
    )
