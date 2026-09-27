from __future__ import annotations

from app.content.character_math import fixed_hit_points, proficiency_bonus, saving_throw_bonuses
from app.content.monster_equipment import build_light_crossbow
from app.content.sorcerer_draconic_2014_spells import burning_hands_2014, fireball_2014, poison_spray_2014, shatter_2014
from app.content.shared_effect_removal_spells_2014 import dispel_magic_2014
from app.content.warlock_2014_progression import warlock_2014_level
from app.content.warlock_2014_spells import eldritch_blast_2014, hex_2014, scorching_ray_2014
from app.content.warlock_fiend_2014_profile import build_varek_ashenmark_2014_profile
from app.domain.models import CombatantTemplate, ResourceDefinition, VisualLoadout, WeaponAttack
from app.domain.progression import ProgressionCombatFeatures
from app.domain.progression_primitives import ResourceBackedD20BonusDie, SourceReducesHostileToZeroHpTemporaryHp


def build_varek_ashenmark_2014(level: int) -> CombatantTemplate:
    if level not in range(1, 7):
        raise ValueError("2014 Varek runtime currently certifies levels 1 through 6.")
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
        ],
        targeted_concentration_damage_actions=[hex_2014()],
        progression_features=ProgressionCombatFeatures(
            source_reduces_hostile_to_zero_hp_temporary_hp=SourceReducesHostileToZeroHpTemporaryHp(
                source_id="dark-ones-blessing",
                source_name="Dark One's Blessing",
                ability="charisma",
                per_level=1,
                minimum=1,
            ),
            resource_backed_d20_bonus_dice=(
                [ResourceBackedD20BonusDie(
                    source_id="dark-ones-own-luck",
                    source_name="Dark One's Own Luck",
                    resource_id="dark-ones-own-luck",
                    resource_cost=1,
                    dice_count=1,
                    dice_size=10,
                    test_kinds=["saving_throw", "ability_check"],
                )] if level >= 6 else []
            ),
        ),
        saving_throw_bonuses=saving_throw_bonuses(scores, level, ("wisdom", "charisma")),
        skill_bonuses={
            "arcana": scores.modifier("intelligence") + pb,
            "history": scores.modifier("intelligence") + pb,
        },
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
        ],
        effect_removal_actions=([dispel_magic_2014("charisma")] if level >= 6 else []),
        visual=VisualLoadout(armor="leather-armor", main_hand="arcane-focus", body_style="humanoid"),
        source="D&D Basic Rules 2014: Human; Sage; Warlock; Fiend Patron; Equipment",
    )
