"""Source-semantic proof for arena-inert 2014 thought-reading Actions."""
from __future__ import annotations

from app.content.monster_source_2014 import SourceMonster2014
from app.content.monster_source_sections_2014 import source_sections_2014


def _normalized(value: str) -> str:
    return " ".join(value.casefold().replace("’", "'").split())


_READ_THOUGHTS_CLAUSE = _normalized(
    "The doppelganger magically reads the surface thoughts of one creature within 60 feet of it. "
    "The effect can penetrate barriers, but 3 feet of wood or dirt, 2 feet of stone, 2 inches of metal, "
    "or a thin sheet of lead blocks it. While the target is in range, the doppelganger can continue "
    "reading its thoughts, as long as the doppelganger's concentration isn't broken (as if concentrating "
    "on a spell). While reading the target's mind, the doppelganger has advantage on Wisdom (Insight) "
    "and Charisma (Deception, Intimidation, and Persuasion) checks against the target."
)


def semantic_read_thoughts_action_labels_2014(
    monster: SourceMonster2014,
) -> tuple[str, ...]:
    """Find thought-reading clauses by their outcome, not card or Action name."""
    labels: list[str] = []
    for label, printed in source_sections_2014(monster.source_actions).items():
        normalized = _normalized(printed)
        if (
            "reads the surface thoughts" in normalized
            and "wisdom (insight)" in normalized
            and "charisma (deception, intimidation, and persuasion) checks" in normalized
        ):
            labels.append(label)
    return tuple(labels)


def source_proven_noncombat_read_thoughts_2014(
    monster: SourceMonster2014, action_name: str,
) -> bool:
    """Prove the complete clause has no outcome used by standard Pit combat."""
    if action_name not in monster.action_names:
        return False
    printed = source_sections_2014(monster.source_actions).get(action_name)
    return printed is not None and _normalized(printed) == _READ_THOUGHTS_CLAUSE
