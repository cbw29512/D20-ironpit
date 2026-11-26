"""2014 conditional head attachments through the universal linked-state engine."""
from app.combat.attachment_attack_gate import source_attacks_blocked
from app.combat.attachment_decision import resolve_attachment_removal_action
from app.combat.attachment_on_hit import apply_attack_hit_attachment
from app.combat.attachments import (
    attachment_attack_advantage, move_attached_sources_with_target,
)
from app.combat.breathing import unable_to_breathe
from app.combat.dice import FixedDiceProvider
from app.combat.modifier_stack import effective_speed
from app.combat.state import build_combatant_state
from app.content.capability_compiler import compile_combatant
from app.content.monster_basic_candidates_2014 import basic_blockers_2014
from app.content.monster_definition_adapter_2014 import adapt_monster_mechanics_2014
from app.content.monster_source_2014 import load_monster_source_2014
from app.content.monsters import build_commoner
from app.domain.character_builds import AbilityScores
from app.domain.encounters import EncounterCombatant, EncounterSetup
from app.domain.models import RollMode


def _cards():
    cards = {card.id: card for card in load_monster_source_2014()}
    assert len(cards) == 327
    return cards


def _fight(card_id="darkmantle", *, target_size="medium"):
    card = _cards()[card_id]
    template = compile_combatant(adapt_monster_mechanics_2014(card))
    attack = template.weapon_attack
    assert attack is not None and attack.on_hit_attachment is not None
    owner = EncounterCombatant(
        combatant_id="owner", side="monsters", position_ft=0,
        state=build_combatant_state(template),
    )
    victim_template = build_commoner().model_copy(update={
        "size": target_size,
        "ability_scores": AbilityScores(
            strength=10, dexterity=10, constitution=10,
            intelligence=10, wisdom=10, charisma=10,
        ),
    })
    victim = EncounterCombatant(
        combatant_id="victim", side="heroes", position_ft=5,
        state=build_combatant_state(victim_template),
    )
    other = EncounterCombatant(
        combatant_id="other", side="heroes", position_ft=5,
        state=build_combatant_state(build_commoner()),
    )
    setup = EncounterSetup(
        heroes=[victim, other], monsters=[owner], ruleset="2014",
        hero_total_levels=2, monster_total_cr=card.challenge_rating or "0",
    )
    return attack, owner, victim, other, setup


def test_semantic_family_scans_all_cards_and_clears_attack_blockers():
    cards = _cards()
    assert "attack:incomplete" not in basic_blockers_2014(cards["darkmantle"])
    assert "attack:incomplete" not in basic_blockers_2014(cards["cloaker"])
    dark = compile_combatant(adapt_monster_mechanics_2014(cards["darkmantle"]))
    cloak = compile_combatant(adapt_monster_mechanics_2014(cards["cloaker"]))
    assert dark.weapon_attack.on_hit_attachment.action_removal_check_dc == 13
    assert cloak.weapon_attack.on_hit_attachment.action_removal_check_dc == 16
    assert cloak.weapon_attack.on_hit_attachment.attach_max_target_size.value == "large"


def test_advantaged_medium_hit_projects_control_without_grapple():
    attack, owner, victim, other, setup = _fight()
    assert apply_attack_hit_attachment(
        attack, owner.combatant_id, victim.combatant_id, victim.state, setup,
        RollMode.ADVANTAGE,
    )
    link = setup.attachments[0]
    assert link.blinds_target and link.prevents_breathing
    assert victim.state.grapple_sources == []
    assert "blinded" in victim.state.active_effect_ids
    assert unable_to_breathe(victim.state)
    assert effective_speed(owner.state) == 0
    assert source_attacks_blocked(setup, owner.combatant_id, other.combatant_id)
    assert not source_attacks_blocked(setup, owner.combatant_id, victim.combatant_id)
    assert attachment_attack_advantage(
        tuple(setup.attachments), owner.combatant_id, victim.combatant_id,
    ) == 1
    victim.position_ft = 25
    move_attached_sources_with_target(setup, victim.combatant_id)
    assert owner.position_ft == 25


def test_normal_hit_attaches_without_head_controls_and_checked_detach_can_fail_then_pass():
    attack, owner, victim, _, setup = _fight()
    assert apply_attack_hit_attachment(
        attack, owner.combatant_id, victim.combatant_id, victim.state, setup,
        RollMode.NORMAL,
    )
    assert not setup.attachments[0].blinds_target
    assert "blinded" not in victim.state.active_effect_ids
    failed = resolve_attachment_removal_action(
        1, 1, victim, setup, FixedDiceProvider([1]),
    )
    assert failed.check_succeeded is False and setup.attachments
    victim.state.action_available = True
    passed = resolve_attachment_removal_action(
        2, 1, victim, setup, FixedDiceProvider([20]),
    )
    assert passed.check_succeeded is True and setup.attachments == []
    assert victim.state.attachment_breathing_source_ids == []


def test_cloaker_large_limit_and_advantage_head_qualification_are_independent():
    attack, owner, victim, _, setup = _fight("cloaker", target_size="huge")
    assert not apply_attack_hit_attachment(
        attack, owner.combatant_id, victim.combatant_id, victim.state, setup,
        RollMode.ADVANTAGE,
    )
    attack, owner, victim, _, setup = _fight("cloaker", target_size="large")
    assert apply_attack_hit_attachment(
        attack, owner.combatant_id, victim.combatant_id, victim.state, setup,
        RollMode.ADVANTAGE,
    )
    assert setup.attachments[0].blinds_target
