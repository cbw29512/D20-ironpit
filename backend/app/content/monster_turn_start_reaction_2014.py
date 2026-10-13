from __future__ import annotations

from app.content.monster_source_2014 import SourceMonster2014
from app.domain.turn_start_save_reaction import TurnStartSaveReaction


def source_turn_start_reaction_2014(monster: SourceMonster2014) -> TurnStartSaveReaction | None:
    text = monster.source_reactions or ""
    if (monster.reaction_names != ["Unnerving Mask"]
            or "DC 14" not in text or "Wisdom" not in text or "30 feet" not in text):
        return None
    return TurnStartSaveReaction(
        source_id="unnerving-mask", source_name="Unnerving Mask",
        range_ft=30, source_must_see_target=True, target_must_see_source=True,
        save_ability="wisdom", save_dc=14,
    )


def supports_turn_start_reaction_2014(monster: SourceMonster2014) -> bool:
    return source_turn_start_reaction_2014(monster) is not None
