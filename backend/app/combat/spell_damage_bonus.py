from __future__ import annotations

import logging

from app.domain.runtime import CombatantState

logger = logging.getLogger(__name__)


def matching_spell_damage_bonuses(
    state: CombatantState,
    spell_id: str,
    damage_type: str | None,
    *,
    excluded_source_ids: set[str] | None = None,
) -> list[tuple[str, str, int]]:
    """Return source-id/name/ability-modifier bonuses matching one spell damage component."""
    try:
        excluded = excluded_source_ids or set()
        scores = state.template.ability_scores
        grants = state.template.progression_features.spell_damage_bonus_grants
        if grants and scores is None:
            raise ValueError("Spell damage bonus requires character ability scores.")
        matches: list[tuple[str, str, int]] = []
        for grant in grants:
            if grant.source_id in excluded:
                continue
            spell_match = spell_id in grant.eligible_spell_ids
            type_match = damage_type is not None and damage_type in grant.eligible_damage_types
            if not spell_match and not type_match:
                continue
            matches.append((grant.source_id, grant.source_name, scores.modifier(grant.ability)))
        return matches
    except ValueError:
        raise
    except Exception as exc:
        logger.exception(
            "Failed spell damage bonus lookup for %s spell=%s type=%s.",
            state.template.name, spell_id, damage_type,
        )
        raise RuntimeError("Spell damage bonus could not be resolved.") from exc
