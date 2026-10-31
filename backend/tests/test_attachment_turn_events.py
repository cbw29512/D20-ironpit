"""Universal attachment turn ticks consume the existing HP-loss/typed-damage paths."""
import pytest

from app.combat.attachment_turn_events import (
    cleanup_invalid_attachments, resolve_attachment_turn_start_events,
)
from app.combat.attachments import attach, linked_attachment_effects
from app.combat.dice import FixedDiceProvider
from app.combat.state import build_combatant_state
from app.content.audited_fighter import build_karnok_stoneward
from app.content.monsters_low_cr import build_giant_rat
from app.domain.attachments import Attachment
from app.domain.encounters import EncounterCombatant, EncounterSetup


def _setup():
    hero = EncounterCombatant(
        combatant_id="victim", side="heroes", position_ft=5,
        state=build_combatant_state(build_karnok_stoneward()),
    )
    hero.state.current_hp = 20
    hero.state.temporary_hp = 9
    source = EncounterCombatant(
        combatant_id="drainer", side="monsters", position_ft=0,
        state=build_combatant_state(build_giant_rat()),
    )
    setup = EncounterSetup(
        heroes=[hero], monsters=[source], hero_total_levels=1, monster_total_cr="1/8",
    )
    return setup, source, hero


def _link(kind="direct_hp_loss", damage_type=None, threshold=10):
    return Attachment(
        source_id="drainer", target_id="victim", effect_id="drain",
        source_name="Blood Drain" if kind == "direct_hp_loss" else "Synthetic Drain",
        damage_dice_count=1, damage_dice_size=4, damage_bonus=3,
        periodic_effect_kind=kind, damage_type=damage_type,
        detach_after_hp_lost=threshold,
    )


def test_source_turn_drain_uses_hp_loss_without_damage_or_grapple():
    setup, source, hero = _setup()
    setup.attachments = list(attach((), _link()))
    initial_conditions = list(hero.state.active_effect_ids)
    events, seq = resolve_attachment_turn_start_events(
        1, 1, source, setup, FixedDiceProvider([1]),
    )
    assert seq == 2
    assert len(events) == 1
    assert events[0].feature_id == "Blood Drain"
    assert events[0].damage_components == []
    assert "not damage" in events[0].description
    assert hero.state.current_hp == 16
    assert hero.state.temporary_hp == 9
    assert hero.state.active_effect_ids == initial_conditions
    assert setup.attachments[0].actual_hp_lost == 4


def test_actual_ten_hp_drained_detaches_linked_buff_and_debuff():
    setup, source, _hero = _setup()
    setup.attachments = list(attach((), _link()))
    _, seq = resolve_attachment_turn_start_events(1, 1, source, setup, FixedDiceProvider([1]))
    assert setup.attachments[0].actual_hp_lost == 4
    _, seq = resolve_attachment_turn_start_events(seq, 2, source, setup, FixedDiceProvider([4]))
    assert seq == 3
    assert setup.attachments == []
    assert linked_attachment_effects(tuple(setup.attachments)) == ()


def test_dead_source_cleans_link_and_cannot_drain():
    setup, source, _hero = _setup()
    setup.attachments = list(attach((), _link()))
    source.state.is_dead = True
    source.state.is_alive = False
    events, seq = resolve_attachment_turn_start_events(
        1, 2, source, setup, FixedDiceProvider([]),
    )
    assert (events, seq, setup.attachments) == ([], 1, [])


def test_typed_variant_uses_existing_damage_components():
    setup, source, hero = _setup()
    setup.attachments = list(attach((), _link("typed_damage", "necrotic", None)))
    events, seq = resolve_attachment_turn_start_events(
        1, 1, source, setup, FixedDiceProvider([2]),
    )
    assert seq == 2
    assert len(events[0].damage_components) == 1
    assert events[0].feature_id == "Synthetic Drain"
    assert "necrotic damage" in events[0].description
    assert hero.state.current_hp == 20
    assert hero.state.temporary_hp == 4
    assert setup.attachments[0].actual_hp_lost == 0


def test_new_encounter_never_inherits_previous_links():
    first, _, _ = _setup()
    second, _, _ = _setup()
    first.attachments.append(_link())
    assert second.attachments == []


def test_malformed_attachment_rejected_before_runtime():
    with pytest.raises(ValueError):
        _link("typed_damage", None)
