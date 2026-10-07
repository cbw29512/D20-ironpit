"""Keep optional sequence constraints in browser data without altering plain slots."""
import logging
logger = logging.getLogger(__name__)


def attack_slot_row(slot):
    try:
        row = {"attackIds": slot.attack_ids, "saveActionIds": slot.save_action_ids}
        if slot.previous_attack is not None:
            row["previousAttack"] = {"hit": slot.previous_attack.hit, "sameTarget": slot.previous_attack.same_target}
        return row
    except Exception:
        logger.exception("Failed browser attack-slot serialization for %s.", slot.attack_ids)
        raise
