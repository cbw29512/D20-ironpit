from __future__ import annotations

from app.content.monster_source_2014 import SourceMonster2014

# Combat cannot use these actions. Printed abilities remain unchanged on the source card.
# Excluded actions do not acquire resources, recharge rolls, or subordinate attacks.
PIT_BANNED_ACTION_LABELS_2014 = frozenset({"teleport", "plane shift"})


def action_label_2014(name: str) -> str:
    return name.split(" (Recharge", 1)[0].strip().casefold()


def arena_unavailable_recharge_ids_2014(monster: SourceMonster2014) -> frozenset[str]:
    """Exclude recharge only for a matching printed, already-banned action.

    An unknown recharge id remains blocked rather than silently discarded.
    """
    printed = {action_label_2014(name) for name in monster.action_names}
    return frozenset(
        action_id for action_id in monster.action_recharges
        if action_id in PIT_BANNED_ACTION_LABELS_2014 and action_id in printed
    )

def source_proven_ethereal_shift_action_2014(
    monster: SourceMonster2014, action_name: str,
) -> bool:
    """Recognize the complete printed plane-shift effect, not its label alone."""
    if action_name not in monster.action_names:
        return False
    from app.content.monster_source_sections_2014 import source_sections_2014
    printed = source_sections_2014(monster.source_actions).get(action_name, "")
    normalized = " ".join(printed.casefold().replace("’", "'").split())
    return normalized == (
        "the nightmare and up to three willing creatures within 5 feet of it "
        "magically enter the ethereal plane from the material plane, or vice versa."
    )

