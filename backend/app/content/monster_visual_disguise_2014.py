"""Bind strict printed visual disguise facts into a name-neutral combat capability."""
from __future__ import annotations

from app.content.monster_source_2014 import SourceMonster2014
from app.content.monster_source_visual_disguise_2014 import source_proven_visual_disguise_2014
from app.domain.visual_disguise import VisualDisguiseAction


def visual_disguise_action_2014(monster: SourceMonster2014) -> VisualDisguiseAction | None:
    facts = source_proven_visual_disguise_2014(monster)
    if facts is None:
        return None
    return VisualDisguiseAction(
        id="visual-disguise", name=facts.source_name,
        activation_cost=facts.activation_cost,
        dismissal_cost="bonus_action" if facts.ends_on_owner_bonus_action else "action",
        conceals_true_form=facts.conceals_true_form,
        magical_illusion=facts.magical_illusion,
        ends_if_owner_dead=facts.ends_if_owner_dead,
        inspection_cost=facts.investigation_action_cost,
        inspection_ability=facts.investigation_ability,
        inspection_skill=facts.investigation_skill,
        inspection_dc=facts.investigation_dc,
        investigation_reveals_true_form=facts.investigation_reveals_true_form,
    )
