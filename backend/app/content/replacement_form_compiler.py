from __future__ import annotations

import logging
from fractions import Fraction

from app.domain.character_builds import AbilityScores
from app.domain.models import CombatantTemplate

logger = logging.getLogger(__name__)


def compile_replacement_form_template(
    original: CombatantTemplate,
    form: CombatantTemplate,
    *,
    retain_spellcasting: bool = False,
    retained_spell_action_ids: list[str] | None = None,
    retain_creature_type: bool = False,
    retain_hit_points: bool = False,
) -> CombatantTemplate:
    """Compose an active replacement-form template without mutating either source template."""
    try:
        if original.kind != "character":
            raise ValueError("Replacement-form owners must be character combatants.")
        if form.kind != "monster":
            raise ValueError("Replacement-form source data must come from a monster/beast template.")
        if original.ability_scores is None or form.ability_scores is None:
            raise ValueError("Replacement-form compilation requires ability scores on both templates.")

        active_scores = AbilityScores(
            strength=form.ability_scores.strength,
            dexterity=form.ability_scores.dexterity,
            constitution=form.ability_scores.constitution,
            intelligence=original.ability_scores.intelligence,
            wisdom=original.ability_scores.wisdom,
            charisma=original.ability_scores.charisma,
        )
        saves = {
            ability: max(
                original.saving_throw_bonuses.get(ability, -99),
                form.saving_throw_bonuses.get(ability, -99),
            )
            for ability in set(original.saving_throw_bonuses) | set(form.saving_throw_bonuses)
        }
        skills = {
            skill: max(
                original.skill_bonuses.get(skill, -99),
                form.skill_bonuses.get(skill, -99),
            )
            for skill in set(original.skill_bonuses) | set(form.skill_bonuses)
        }

        update = {
            "id": f"{original.id}--form-{form.id}",
            "name": original.name,
            "archetype": original.archetype,
            "level": original.level,
            "kind": "character",
            "ruleset": original.ruleset,
            "creature_type": original.creature_type if retain_creature_type else form.creature_type,
            "max_hp": original.max_hp if retain_hit_points else form.max_hp,
            "ability_scores": active_scores,
            "saving_throw_bonuses": saves,
            "skill_bonuses": skills,
            "progression_features": original.progression_features,
            "resources": original.resources,
            "unlimited_resource_ids": original.unlimited_resource_ids,
            "source": f"{original.source}; replacement form: {form.source}",
        }
        if retain_spellcasting:
            allowed = set(retained_spell_action_ids or [])
            keep = lambda actions: [action for action in actions if action.id in allowed]
            update.update({
                "spell_save_actions": keep(original.spell_save_actions),
                "spell_attack_actions": keep(original.spell_attack_actions),
                "auto_hit_spell_actions": keep(original.auto_hit_spell_actions),
                "persistent_spell_attack_actions": keep(original.persistent_spell_attack_actions),
                "persistent_barrier_actions": keep(original.persistent_barrier_actions),
                "defensive_spell_actions": keep(original.defensive_spell_actions),
                "healing_actions": keep(original.healing_actions),
                "condition_removal_actions": keep(original.condition_removal_actions),
                "effect_removal_actions": keep(original.effect_removal_actions),
            })
        else:
            update.update({
                "spell_save_actions": [],
                "spell_attack_actions": [],
                "persistent_spell_attack_actions": [],
                "persistent_barrier_actions": [],
                "defensive_spell_actions": [],
                "healing_actions": [],
                "condition_removal_actions": [],
                "effect_removal_actions": [],
            })
        return form.model_copy(update=update, deep=True)
    except Exception:
        logger.exception(
            "Failed to compile replacement form %s for %s.",
            form.name,
            original.name,
        )
        raise


def compile_monster_change_shape_physical_overlay(
    original: CombatantTemplate,
    form: CombatantTemplate,
) -> CombatantTemplate:
    """Build the *physical-stat layer* of a source-retaining monster transformation.

    This is deliberately not a complete Change Shape action: forms can grant
    additional attacks/capabilities, which require separate source-proof and
    binding before the transformed monster may enter production combat.
    """
    if original.kind != "monster" or form.kind != "monster":
        raise ValueError("Monster Change Shape requires two monster templates.")
    if original.ruleset != form.ruleset:
        raise ValueError("A Change Shape form must use the owner's ruleset.")
    if not (form.creature_type or "").lower().startswith(("beast", "humanoid")):
        raise ValueError("Change Shape form must be a humanoid or beast.")
    if original.challenge_rating is None or form.challenge_rating is None:
        raise ValueError("Change Shape requires source challenge ratings.")
    if Fraction(form.challenge_rating) > Fraction(original.challenge_rating):
        raise ValueError("Change Shape form exceeds its source's challenge rating.")
    if original.ability_scores is None or form.ability_scores is None:
        raise ValueError("Change Shape requires source ability scores.")

    # 2014 Deva-style source: keep the owner's other statistics and identity.
    # Wild Shape intentionally remains in compile_replacement_form_template.
    scores = original.ability_scores.model_copy(update={
        "strength": form.ability_scores.strength,
        "dexterity": form.ability_scores.dexterity,
    })
    return original.model_copy(update={
        "id": f"{original.id}--form-{form.id}",
        "armor_class": form.armor_class,
        "speed_ft": form.speed_ft,
        "movement_modes": form.movement_modes.model_copy(deep=True),
        "blindsight_ft": form.blindsight_ft,
        "truesight_ft": form.truesight_ft,
        "ability_scores": scores,
        # The source says the owner retains defenses AND gains new ones
        # its form has that it lacks. These are real source qualifiers, not
        # an inferred full set of immunities based on the form name or CR.
        "damage_resistances": list(dict.fromkeys([
            *original.damage_resistances, *form.damage_resistances,
        ])),
        "damage_immunities": list(dict.fromkeys([
            *original.damage_immunities, *form.damage_immunities,
        ])),
        "condition_immunities": list(dict.fromkeys([
            *original.condition_immunities, *form.condition_immunities,
        ])),
        "conditional_damage_defenses": [
            *original.conditional_damage_defenses,
            *(rule for rule in form.conditional_damage_defenses
              if rule not in original.conditional_damage_defenses),
        ],
        "source": f"{original.source}; physical Change Shape overlay: {form.source}",
    }, deep=True)
