from __future__ import annotations

import logging

from app.content.monster_source_capability_candidates import _ATTACK, _attack

logger = logging.getLogger(__name__)

ANKHEG_BITE = (
    "Bite. Melee Attack Roll: +5 (with Advantage if the target is Grappled by the ankheg), reach 5 ft. "
    "Hit: 10 (2d6 + 3) Slashing damage plus 3 (1d6) Acid damage. "
    "If the target is a Large or smaller creature, it has the Grappled condition (escape DC 13)."
)


def test_source_attack_header_grapple_advantage_compiles_declaratively() -> None:
    try:
        match = _ATTACK.search(ANKHEG_BITE)
        assert match is not None
        attack = _attack({"name": "Ankheg"}, ANKHEG_BITE, match)
        assert [item.trigger for item in attack.conditional_attack_advantage] == ["target_grappled_by_source"]
        assert any(effect.kind == "grapple" for effect in attack.effects)
    except Exception:
        logger.exception("Source attack-header Advantage regression failed.")
        raise


def test_unknown_attack_header_parenthetical_still_fails_closed() -> None:
    try:
        unsupported = ANKHEG_BITE.replace(
            "with Advantage if the target is Grappled by the ankheg",
            "with Advantage on Tuesdays",
        )
        assert _ATTACK.search(unsupported) is None
    except Exception:
        logger.exception("Unsupported attack-header parenthetical regression failed.")
        raise
