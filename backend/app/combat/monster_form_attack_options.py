"""Source-neutral composition of *alternative* printed attack sequences.

A transforming creature keeps its own legal Attack Action choices and gains
those printed by its legal form.  Complete source sequences must stay
alternatives: concatenating their slots would invent extra attacks.

This pure helper does not authorize a form, grant class/legendary abilities,
recalculate ability-dependent hit bonuses, register acquired attack profiles or
activate Change Shape.  Those are distinct source-validated runtime gates.
"""
from __future__ import annotations

from app.domain.attack_action_definitions import (
    AttackActionDefinition,
    AttackActionVariant,
)
from app.domain.models import CombatantTemplate


def _source_variants(template: CombatantTemplate) -> list[AttackActionVariant]:
    action = template.attack_action
    if action is None:
        return []
    if action.variants:
        return [
            variant.model_copy(update={"id": f"{template.id}:{variant.id}"}, deep=True)
            for variant in action.variants
        ]
    return [AttackActionVariant(
        id=f"{template.id}:{action.id}",
        slots=[slot.model_copy(deep=True) for slot in action.slots],
    )]


def compose_monster_form_attack_sequences(
    owner: CombatantTemplate,
    form: CombatantTemplate,
) -> AttackActionDefinition | None:
    """Retain both complete actions as choices, never one extra-long Action.

    Caller must independently source-validate the form's edition, creature
    type, CR and eligibility and bind all referenced attack/save IDs. This
    result is not a live transformation or an added extra Action.
    """
    if owner.kind != "monster" or form.kind != "monster":
        raise ValueError("Only monster sources can compose monster form attacks.")
    if owner.ruleset != form.ruleset:
        raise ValueError("Cannot combine different edition attack sequences.")
    before, gained = owner.attack_action, form.attack_action
    if before is None and gained is None:
        return None
    if before is None:
        return gained.model_copy(deep=True)
    if gained is None:
        return before.model_copy(deep=True)
    if before == gained:
        return before.model_copy(deep=True)
    if before.name != gained.name:
        raise ValueError("Distinctly named Actions require separately authorized action binding.")

    variants = [*_source_variants(owner), *_source_variants(form)]
    if len(variants) > 16 or len({row.id for row in variants}) != len(variants):
        raise ValueError("Source form Attack Action alternatives exceed the universal limits.")
    return AttackActionDefinition(
        id=f"{owner.id}--form-{form.id}--attack-options",
        name=before.name,
        variants=variants,
        # An Attack Action-specific bonus is safe only when both choices are
        # independently qualified. Never promote a non-Attack source Action.
        is_attack_action=before.is_attack_action and gained.is_attack_action,
    )
