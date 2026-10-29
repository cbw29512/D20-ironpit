"""End-of-turn regurgitation uses actual damage and source-defined saves."""
from types import SimpleNamespace

from app.combat.swallow_turn_resolution import resolve_swallowed_end_turn
from app.domain.models import BattleEvent
from app.domain.size import CreatureSize
from app.domain.swallowed_state import SwallowedState


def test_below_threshold_never_calls_saving_throw():
    swallowed = SwallowedState(
        source_id="owner", source_name="Swallow",
        damage_dice_count=6, damage_dice_size=6, damage_type="acid",
        exit_movement_ft=15, target_size=CreatureSize.MEDIUM,
        regurgitation_damage_threshold=30,
        regurgitation_save_ability="constitution", regurgitation_save_dc=14,
        regurgitation_range_ft=10,
    )
    victim = SimpleNamespace(
        combatant_id="victim", state=SimpleNamespace(swallowed=swallowed),
    )
    owner = SimpleNamespace(
        combatant_id="owner",
        state=SimpleNamespace(is_dead=False, is_alive=True),
    )
    setup = SimpleNamespace(heroes=[victim], monsters=[owner])
    # Incoming damage from other creatures must not count.
    events = [
        BattleEvent(sequence=1, round_number=1, event_type="attack",
                    actor_id="other", actor_name="Other", target_id="owner",
                    target_name="Owner", hp_before=50, hp_after=1),
        BattleEvent(sequence=2, round_number=1, event_type="attack",
                    actor_id="victim", actor_name="Victim", target_id="owner",
                    target_name="Owner", hp_before=40, hp_after=25),
    ]
    output, sequence = resolve_swallowed_end_turn(
        events, 3, 1, victim, setup, None, "1:victim",
    )
    assert output == [] and sequence == 3
    assert swallowed.damage_from_victim_this_turn == 15
