"""Legal repeated hits accumulate source-owned HP loss past one-hit dice limits."""
from __future__ import annotations

import logging

from app.combat.dice import FixedDiceProvider
from app.combat.ongoing_hp_loss import apply_or_stack_hp_loss
from app.combat.start_of_turn_hp_loss import resolve_start_of_turn_hp_loss_events
from app.combat.state import build_combatant_state
from app.content.audited_fighter import build_karnok_stoneward
from app.domain.encounters import EncounterCombatant
from app.domain.timed_effects import TimedEffect

logger = logging.getLogger(__name__)


def test_legal_source_wounds_stack_past_40_and_deal_direct_hp_loss():
    """Test the universal mechanic with a 10,000-HP target and exact dice."""
    try:
        source_card = build_karnok_stoneward()
        template = source_card.model_copy(update={"max_hp": 10000})
        target = build_combatant_state(template)
        target.current_hp = 10000
        target.temporary_hp = 400
        for _ in range(75):
            count = apply_or_stack_hp_loss(
                target, "persistent-wound", "devil-one", "Printed Wound",
                dice_count=1, dice_size=10, ends_on_magical_healing=True,
            )
        assert count == 75
        assert len(target.timed_effects) == 1
        effect = target.timed_effects[0]
        assert effect.start_of_turn_hp_loss_dice_count == 75
        assert TimedEffect.model_validate(
            effect.model_dump()
        ).start_of_turn_hp_loss_dice_count == 75

        member = EncounterCombatant(
            combatant_id="bag", side="heroes", position_ft=0, state=target,
        )
        setup = type("Setup", (), {"heroes": [member], "monsters": []})()
        events, next_sequence = resolve_start_of_turn_hp_loss_events(
            1, 2, member, setup, FixedDiceProvider([1] * 75),
        )
        assert next_sequence == 2
        assert len(events) == 1
        assert target.current_hp == 9925
        assert target.temporary_hp == 400
        assert "not damage" in events[0].description
        assert source_card.max_hp != 10000
    except Exception:
        logger.exception("Ongoing HP-loss stack above 40 dice failed")
        raise


def test_multidie_hits_stack_by_source_without_merging_other_attackers():
    try:
        target = build_combatant_state(build_karnok_stoneward())
        for _ in range(25):
            apply_or_stack_hp_loss(
                target, "generic-wound", "attacker-one", "On Hit",
                dice_count=2, dice_size=6,
            )
        apply_or_stack_hp_loss(
            target, "generic-wound", "attacker-two", "On Hit",
            dice_count=2, dice_size=6,
        )
        assert len(target.timed_effects) == 2
        assert [item.start_of_turn_hp_loss_dice_count for item in
                target.timed_effects] == [50, 2]
    except Exception:
        logger.exception("Source-scoped multi-die wound stacking failed")
        raise
