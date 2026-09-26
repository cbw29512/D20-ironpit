from __future__ import annotations

import logging

from app.domain.character_builds import AbilityScores
from app.domain.models import CombatantTemplate

logger = logging.getLogger(__name__)


def compile_replacement_form_template(
    original: CombatantTemplate,
    form: CombatantTemplate,
    *,
    retain_spellcasting: bool = False,
    retained_spell_action_ids: list[str] | None = None,
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
            "creature_type": form.creature_type,
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
                "persistent_spell_attack_actions": keep(original.persistent_spell_attack_actions),
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
