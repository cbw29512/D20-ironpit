from __future__ import annotations

import logging

from app.content.canonical_hero_policy import canonical_template_id
from app.content.character_math import fixed_hit_points, proficiency_bonus, saving_throw_bonuses
from app.content.cleric_life_domain import AID, LESSER_RESTORATION
from app.content.healing_spell_effects import build_cure_wounds
from app.content.hero_progressions import HERO_BY_CLASS
from app.content.paladin_devotion_2024_profile import build_aurelia_brightshield_2024_profile
from app.content.paladin_devotion_2024_level9 import abjure_foes_2024, beacon_of_hope_2024, dispel_magic_2024_paladin
from app.content.offensive_spell_effects import build_flame_strike_2024
from app.content.paladin_devotion_2024_resources import build_paladin_2024_resources
from app.content.paladin_devotion_2024_runtime_support import (
    build_paladin_2024_attack,
    build_paladin_2024_attack_action,
    build_paladin_2024_progression,
    build_paladin_2024_timed_self_buffs,
)
from app.content.paladin_devotion_2024_support import (
    divine_favor_2024,
    protection_from_evil_and_good_2024,
    sacred_weapon_2024,
    shield_of_faith_2024,
)
from app.content.shared_movement_spells_2024 import freedom_of_movement_2024
from app.content.spell_effects import BLESS
from app.domain.actions import ConditionRemovalAction, HealingAction
from app.domain.models import CombatantTemplate, VisualLoadout
from app.domain.traits import CombatTrait

logger = logging.getLogger(__name__)

def build_aurelia_brightshield_2024(level: int = 1) -> CombatantTemplate:
    """Build certified 2024 Aurelia through Paladin level 18."""
    try:
        if level not in range(1, 19):
            raise ValueError("The current 2024 Paladin runtime tranche supports levels 1-18 only.")
        profile = build_aurelia_brightshield_2024_profile(level)
        scores = profile.final_ability_scores
        if scores is None:
            raise ValueError("2024 Aurelia profile is missing final ability scores.")
        strength = scores.modifier("strength")
        charisma = scores.modifier("charisma")
        pb = proficiency_bonus(level)
        return CombatantTemplate(
            id=canonical_template_id("paladin", level),
            name=HERO_BY_CLASS["paladin"].hero_name, archetype="Paladin",
            level=level, kind="character", ruleset="2024", creature_type="humanoid",
            ability_scores=scores, armor_class=18 + int(level >= 2),
            max_hp=fixed_hit_points(level, 10, scores.modifier("constitution")),
            speed_ft=30, initiative_bonus=scores.modifier("dexterity"),
            starts_with_heroic_inspiration=True,
            weapon_attack=build_paladin_2024_attack("longsword", strength, level),
            alternate_weapon_attacks=[build_paladin_2024_attack("javelin", strength, level)],
            attack_action=build_paladin_2024_attack_action(level),
            saving_throw_actions=[abjure_foes_2024(8 + pb + charisma, charisma)] if level >= 9 else [],
            spell_save_actions=[build_flame_strike_2024(8 + pb + charisma)] if level >= 17 else [],
            healing_actions=[
                HealingAction(
                    id="lay-on-hands-heal", name="Lay On Hands", action_cost="bonus_action",
                    range_ft=5, target_mode="self_or_ally", dice_count=0,
                    healing_bonus=5 * level, resource_id="lay-on-hands",
                    resource_cost=5 * level, healing_from_resource_pool=True, animation="healing",
                ),
                build_cure_wounds(charisma),
            ],
            condition_removal_actions=[
                ConditionRemovalAction(
                    id="lay-on-hands-poison", name="Lay On Hands (Restoring Touch)" if level >= 14 else "Lay On Hands",
                    action_cost="bonus_action", range_ft=5, target_mode="self_or_ally",
                    removable_conditions=["poisoned", *(["blinded", "charmed", "deafened",
                        "frightened", "paralyzed", "stunned"] if level >= 14 else [])],
                    max_conditions_per_use=7 if level >= 14 else 1, resource_costs_per_condition={"lay-on-hands": 5},
                ),
                *([LESSER_RESTORATION.model_copy(deep=True)] if level >= 7 else []),
            ],
            defensive_spell_actions=[
                divine_favor_2024(),
                *([BLESS.model_copy(deep=True)] if level >= 2 else []),
                *(
                    [protection_from_evil_and_good_2024(), shield_of_faith_2024()]
                    if level >= 3 else []
                ),
                *([AID.model_copy(deep=True)] if level >= 5 else []),
                *([beacon_of_hope_2024()] if level >= 9 else []),
                *([freedom_of_movement_2024()] if level >= 13 else []),
            ],
            effect_removal_actions=[dispel_magic_2024_paladin()] if level >= 9 else [],
            attack_action_weapon_buffs=[
                sacred_weapon_2024(charisma)
            ] if level >= 3 else [],
            saving_throw_bonuses=saving_throw_bonuses(scores, level, ("wisdom", "charisma")),
            skill_bonuses={
                "athletics": strength + pb, "intimidation": charisma + pb,
                "insight": scores.modifier("wisdom") + pb, "persuasion": charisma + pb,
                "perception": scores.modifier("wisdom") + pb,
                "acrobatics": scores.modifier("dexterity") + pb,
                "medicine": scores.modifier("wisdom") + pb,
                "religion": scores.modifier("intelligence") + pb,
            },
            combat_traits=[CombatTrait.SAVAGE_ATTACKER],
            progression_features=build_paladin_2024_progression(level, charisma),
            timed_self_buff_actions=build_paladin_2024_timed_self_buffs(level),
            weapon_masteries=["longsword", "javelin"],
            fighting_style="Defense" if level >= 2 else None,
            fighting_styles=["Defense"] if level >= 2 else [],
            wearing_heavy_armor=True, wearing_metal_armor=True,
            visual=VisualLoadout(armor="chain-mail", main_hand="longsword", off_hand="shield"),
            resources=build_paladin_2024_resources(level),
            source=(
                f"D&D Beyond Basic Rules 2024: Paladin {level}, Human, Soldier, "
                "Cure Wounds, Divine Favor, "
                + ("Bless, Divine Smite, " if level >= 2 else "")
                + (
                    "Sacred Weapon, Protection from Evil and Good, Shield of Faith, "
                    if level >= 3 else ""
                )
                + ("Thunderous Smite (fail-closed pending shared atomic post-hit save/push primitive), " if level >= 4 else "")
                + (
                    "Shining Smite (fail-closed pending shared persistent post-hit target-effect primitive), "
                    "Aid, Zone of Truth, Find Steed (arena-unavailable summon), "
                    if level >= 5 else ""
                )
                + ("Lesser Restoration, Aura of Devotion, " if level >= 7 else "")
                + ("Abjure Foes, Aura of Vitality, Blinding Smite, Beacon of Hope, Dispel Magic, " if level >= 9 else "")
                + ("Aura of Courage, " if level >= 10 else "")
                + ("Radiant Strikes, Crusader\'s Mantle, " if level >= 11 else "")
                + ("Freedom of Movement, Guardian of Faith (arena-unavailable summon), "
                   "Staggering Smite (fail-closed pending shared atomic post-hit save/condition choice), "
                   if level >= 13 else "")
                + ("Restoring Touch, " if level >= 14 else "")
                + ("Smite of Protection, Aura of Life (fail-closed pending shared recovery aura), " if level >= 15 else "")
                + ("Commune (arena-neutral), Flame Strike, Destructive Wave (fail-closed), Greater Restoration (fail-closed), " if level >= 17 else "")
                + ("Aura Expansion, " if level >= 18 else "")
                + "Longsword, Javelin"
            ),
        )
    except Exception:
        logger.exception("Failed to build 2024 Aurelia Brightshield at level %s.", level)
        raise
