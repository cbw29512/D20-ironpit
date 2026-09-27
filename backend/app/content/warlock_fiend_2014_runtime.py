from __future__ import annotations

from app.content.character_math import fixed_hit_points, proficiency_bonus, saving_throw_bonuses
from app.content.monster_equipment import build_light_crossbow
from app.content.warlock_2014_spells import eldritch_blast_2014, hex_2014
from app.content.warlock_fiend_2014_profile import build_varek_ashenmark_2014_profile
from app.domain.models import CombatantTemplate, ResourceDefinition, VisualLoadout, WeaponAttack
from app.domain.progression import ProgressionCombatFeatures
from app.domain.progression_primitives import SourceReducesHostileToZeroHpTemporaryHp


def build_varek_ashenmark_2014(level: int) -> CombatantTemplate:
    if level != 1:
        raise ValueError("2014 Varek runtime currently certifies level 1 only.")
    profile = build_varek_ashenmark_2014_profile(level)
    scores = profile.final_ability_scores
    pb = proficiency_bonus(level)
    dex = scores.modifier("dexterity")
    cha = scores.modifier("charisma")
    crossbow = build_light_crossbow()
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
        spell_attack_actions=[eldritch_blast_2014(pb + cha, level)],
        targeted_concentration_damage_actions=[hex_2014()],
        progression_features=ProgressionCombatFeatures(
            source_reduces_hostile_to_zero_hp_temporary_hp=SourceReducesHostileToZeroHpTemporaryHp(
                source_id="dark-ones-blessing",
                source_name="Dark One's Blessing",
                ability="charisma",
                per_level=1,
                minimum=1,
            ),
        ),
        saving_throw_bonuses=saving_throw_bonuses(scores, level, ("wisdom", "charisma")),
        skill_bonuses={
            "arcana": scores.modifier("intelligence") + pb,
            "history": scores.modifier("intelligence") + pb,
        },
        resources=[ResourceDefinition(id="spell-slot-1", name="Pact Magic Slot 1", max_uses=1)],
        visual=VisualLoadout(armor="leather-armor", main_hand="arcane-focus", body_style="humanoid"),
        source="D&D Basic Rules 2014: Human; Sage; Warlock; Fiend Patron; Equipment",
    )
