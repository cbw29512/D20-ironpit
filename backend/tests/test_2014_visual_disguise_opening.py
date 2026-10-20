"""2014 Sea Hag tactical opening: source-bound precombat illusion, printed Bonus Action dismissal."""
from __future__ import annotations

from app.combat.precombat_buffs import choose_opening_buff, prepare_opening_buffs
from app.combat.visual_disguise import resolve_visual_disguise_first_turn_dismissal
from app.combat.visual_true_form import observer_sees_true_form
from app.combat.state import build_combatant_state, begin_turn
from app.combat.turn_start_visual_effects import resolve_visual_turn_start_events
from app.combat.dice import FixedDiceProvider
from app.content.capability_compiler import compile_combatant
from app.content.monster_definition_adapter_2014 import adapt_basic_monster_2014
from app.content.monster_source_2014 import load_monster_source_2014
from app.content.monster_visual_disguise_2014 import visual_disguise_action_2014
from app.content.monster_visual_turn_start_2014 import visual_turn_start_rule_2014
from app.domain.encounters import EncounterCombatant, EncounterSetup


def _setup():
    rows = {m.id: m for m in load_monster_source_2014()}
    hag = rows["sea-hag"]
    card_before = hag.model_dump_json()
    action = visual_disguise_action_2014(hag)
    assert action is not None and action.inspection_dc == 16
    assert action.activation_cost == "action" and action.dismissal_cost == "bonus_action"
    assert action.investigation_reveals_true_form is False
    source_template = compile_combatant(adapt_basic_monster_2014(rows["commoner"]))
    source_template = source_template.model_copy(update={
        "visual_turn_start_rule": visual_turn_start_rule_2014(hag),
        "visual_disguise_action": action,
    })
    source = EncounterCombatant(combatant_id="source", side="monsters",
        position_ft=10, state=build_combatant_state(source_template))
    hero_template = compile_combatant(adapt_basic_monster_2014(rows["commoner"]))
    hero = EncounterCombatant(combatant_id="target", side="heroes",
        position_ft=0, state=build_combatant_state(hero_template))
    setup = EncounterSetup(heroes=[hero], monsters=[source],
        ruleset="2014", hero_total_levels=0, monster_total_cr="0")
    assert hag.model_dump_json() == card_before
    return setup, source, hero


def test_one_free_buff_then_real_bonus_action_reveal_before_later_turns():
    setup, source, target = _setup()
    opening = choose_opening_buff(source, setup)
    assert opening is not None and opening.kind == "visual-disguise"
    events, _ = prepare_opening_buffs(setup)
    assert len(events) == 1 and events[0].round_number == 0
    assert source.state.magical_visual_disguise_active
    assert not observer_sees_true_form(source.state, target.state, 10)
    assert source.state.opening_buff_id == source.state.template.visual_disguise_action.id
    assert source.state.action_available and source.state.bonus_action_available
    # A victim beginning a turn while disguise is active cannot see true form.
    target.state.turns_started = 1
    hidden, _ = resolve_visual_turn_start_events(
        1, 1, target, setup, FixedDiceProvider([1]), ["source", "target"])
    assert hidden == []
    begin_turn(source.state)
    revealed = resolve_visual_disguise_first_turn_dismissal(2, 1, source)
    assert revealed is not None and "Bonus Action" in revealed.description
    assert source.state.action_available and not source.state.bonus_action_available
    assert not source.state.magical_visual_disguise_active
    assert observer_sees_true_form(source.state, target.state, 10)
    assert resolve_visual_disguise_first_turn_dismissal(3, 1, source) is None
    # The actual gaze save occurs only at the next target TURN START.
    after, _ = resolve_visual_turn_start_events(
        4, 1, target, setup, FixedDiceProvider([1]), ["source", "target"])
    assert len(after) == 1 and after[0].applied_condition_ids == ["frightened"]
    assert source.state.template.visual_disguise_action.inspection_dc == 16
    assert not build_combatant_state(source.state.template).magical_visual_disguise_active


def test_target_first_avoids_gaze_despite_owner_first_turn_reveal():
    setup, source, target = _setup()
    prepare_opening_buffs(setup)
    target.state.turns_started = 1
    before, _ = resolve_visual_turn_start_events(
        1, 1, target, setup, FixedDiceProvider([1]), ["target", "source"])
    assert before == []
    begin_turn(source.state)
    assert resolve_visual_disguise_first_turn_dismissal(1, 1, source)
    # House-rule ordering continues to control later starts: early target averts.
    target.state.turns_started = 2
    after, _ = resolve_visual_turn_start_events(
        2, 2, target, setup, FixedDiceProvider([1]), ["target", "source"])
    assert len(after) == 1 and after[0].event_type == "feature"


def test_cannot_get_extra_bonus_action_or_reveal_while_incapacitated():
    setup, source, _ = _setup()
    prepare_opening_buffs(setup)
    begin_turn(source.state)
    source.state.bonus_action_available = False
    assert resolve_visual_disguise_first_turn_dismissal(1, 1, source) is None
    assert source.state.magical_visual_disguise_active
    source.state.bonus_action_available = True
    source.state.is_unconscious = True
    assert resolve_visual_disguise_first_turn_dismissal(1, 1, source) is None
    assert source.state.magical_visual_disguise_active
    source.state.is_unconscious = False
    assert resolve_visual_disguise_first_turn_dismissal(1, 1, source)
    assert not source.state.bonus_action_available


def test_monster_and_pregen_forms_share_source_owned_disguise_mechanics():
    """The same printed declaration runs on either card kind without a new resolver."""
    from pydantic import ValidationError
    from app.domain.visual_disguise import VisualDisguiseAction
    from app.combat.visual_disguise import resolve_visual_disguise_opening

    source_fields = [
        "activation_cost", "dismissal_cost", "conceals_true_form",
        "magical_illusion", "ends_if_owner_dead", "physical_inspection_inconsistent",
        "inspection_cost", "inspection_ability", "inspection_skill", "inspection_dc",
        "investigation_reveals_true_form", "opening_priority", "opening_eligible",
        "dismiss_on_first_turn",
    ]
    assert all(VisualDisguiseAction.model_fields[x].is_required() for x in source_fields)

    setup, source, target = _setup()
    original_card = source.state.template.visual_disguise_action
    assert original_card.physical_inspection_inconsistent
    synthetic = original_card.model_dump() | {
        "name": "Unrelated Pregen Visual Mask",
        "dismissal_cost": "action",
        "inspection_dc": 19,
    }
    alternate = VisualDisguiseAction.model_validate(synthetic)
    template = target.state.template.model_copy(update={
        "kind": "character", "visual_disguise_action": alternate,
    })
    actor = EncounterCombatant(combatant_id="pregen", side="heroes",
        position_ft=0, state=build_combatant_state(template))
    event = resolve_visual_disguise_opening(1, actor)
    assert event.feature_id == alternate.id
    assert actor.state.magical_visual_disguise_active
    begin_turn(actor.state)
    dismissal = resolve_visual_disguise_first_turn_dismissal(2, 1, actor)
    assert dismissal is not None and "using an Action" in dismissal.description
    assert actor.state.action_available is False
    assert actor.state.bonus_action_available is True
    assert alternate.inspection_dc == 19
    assert original_card.inspection_dc == 16
    assert source.state.template.visual_disguise_action is original_card

    with __import__("pytest").raises(ValidationError):
        VisualDisguiseAction.model_validate({k: v for k, v in synthetic.items() if k != "inspection_dc"})
    with __import__("pytest").raises(ValidationError):
        VisualDisguiseAction.model_validate(synthetic | {"dismissal_cost": "free"})
