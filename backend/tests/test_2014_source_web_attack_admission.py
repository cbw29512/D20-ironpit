"""2014 Ettercap and Giant Spider: the same generic ranged breakable restraint."""
from __future__ import annotations

import logging
import pytest

from app.combat.breakable_condition_object import damage_breakable_condition_object
from app.combat.state import build_combatant_state
from app.combat.timed_conditions import apply_timed_condition
from app.content.capability_compiler import compile_combatant
from app.content.monster_basic_candidates_2014 import basic_blockers_2014
from app.content.monster_definition_adapter_2014 import adapt_basic_monster_2014
from app.content.monster_source_2014 import load_monster_source_2014
from app.content.monster_source_breakable_restraint_2014 import source_recharge_breakable_restraint_2014

logger = logging.getLogger(__name__)


def _card(monster_id: str):
    try:
        return next(card for card in load_monster_source_2014() if card.id == monster_id)
    except Exception:
        logger.exception("Missing 2014 source monster: %s", monster_id)
        raise


@pytest.mark.parametrize("monster_id,bonus,dc,max_size", [
    ("giant-spider", 5, 12, None),
    ("ettercap", 4, 11, "large"),
])
def test_source_complete_ranged_web_compiles_without_special_resolver(monster_id, bonus, dc, max_size):
    try:
        card = _card(monster_id)
        original = card.model_dump_json()
        web = next(attack for attack in card.attacks if attack.id == "web")
        proof = source_recharge_breakable_restraint_2014(card, web)
        assert proof is not None
        assert (proof.resource_id, proof.recharge_minimum, proof.escape_dc) == ("web", 5, dc)
        assert (proof.max_target_size.value if proof.max_target_size else None) == max_size
        assert (proof.object_ac, proof.object_hp) == (10, 5)
        assert proof.damage_vulnerabilities == ("fire",)
        assert proof.damage_immunities == ("bludgeoning", "poison", "psychic")
        assert basic_blockers_2014(card) == ()
        template = compile_combatant(adapt_basic_monster_2014(card))
        attack = next(attack for attack in [
            template.weapon_attack, *template.alternate_weapon_attacks
        ] if attack is not None and attack.weapon.name == "Web")
        assert (attack.weapon.attack_kind.value, attack.attack_bonus, attack.fixed_damage) == (
            "ranged", bonus, 0,
        )
        assert (attack.weapon.normal_range_ft, attack.weapon.long_range_ft) == (30, 60)
        assert attack.resource_id == "web"
        assert attack.control_effect.condition_id == "restrained"
        assert attack.control_effect.escape_check_dc == dc
        assert attack.control_effect.breakable_object.hit_points == 5
        assert next(r for r in template.recharge_rules if r.resource_id == "web").minimum_roll == 5
        assert next(r for r in template.resources if r.id == "web").max_uses == 1
        assert card.model_dump_json() == original
    except Exception:
        logger.exception("Shared 2014 Web binding failed for %s.", monster_id)
        raise


@pytest.mark.parametrize("monster_id", ["giant-spider", "ettercap"])
def test_web_mutations_fail_closed_but_renamed_source_is_equivalent(monster_id):
    try:
        card = _card(monster_id)
        web = next(row for row in card.attacks if row.id == "web")
        assert source_recharge_breakable_restraint_2014(card, web)
        renamed = card.model_copy(update={"id": "unrelated-creature", "name": "Other Creature"})
        assert source_recharge_breakable_restraint_2014(renamed, web)
        damaged = card.model_copy(update={
            "source_actions": card.source_actions.replace("vulnerability to fire damage", "vulnerability to acid damage")
        })
        assert source_recharge_breakable_restraint_2014(damaged, web) is None
        assert "attack:complex" in basic_blockers_2014(damaged)
        changed = web.model_copy(update={"breakable_restraint": {
            **web.breakable_restraint, "object_hp": 50,
        }})
        assert source_recharge_breakable_restraint_2014(card, changed) is None
        assert "attack:complex" in basic_blockers_2014(card.model_copy(update={
            "attacks": [changed if attack.id == "web" else attack for attack in card.attacks]
        }))
    except Exception:
        logger.exception("Shared Web fail-closed/identity-neutral proof failed.")
        raise


def test_breakable_web_condition_uses_fresh_state_and_existing_condition_cleanup():
    try:
        card = _card("ettercap")
        template = compile_combatant(adapt_basic_monster_2014(card))
        web = next(row for row in [template.weapon_attack, *template.alternate_weapon_attacks]
                   if row and row.weapon.name == "Web")
        target = build_combatant_state(template)
        control = web.control_effect
        assert apply_timed_condition(
            target, "restrained", "attacker",
            source_effect_id=web.id, source_template=template,
            applied_round=1, expires_at_start_of_source_turn=False,
            escape_check_ability=control.escape_check_ability,
            escape_check_dc=control.escape_check_dc,
            breakable_object=control.breakable_object,
        ) == "restrained"
        effect = target.timed_effects[-1]
        assert effect.breakable_object.current_hp == 5
        assert effect.escape_check_dc == 11 and effect.expiry_timing is None
        assert damage_breakable_condition_object(target, effect, 9, 8, "fire") == (0, False)
        assert damage_breakable_condition_object(target, effect, 20, 8, "poison") == (0, False)
        assert damage_breakable_condition_object(target, effect, 20, 2, "fire") == (4, False)
        assert effect.breakable_object.current_hp == 1
        assert damage_breakable_condition_object(target, effect, 20, 1, "piercing") == (1, True)
        assert "restrained" not in target.active_effect_ids
        # A separate hit can be escaped by spending a normal Action.
        from app.combat.ability_check_escape import resolve_escape_check, should_escape_check
        from app.combat.dice import FixedDiceProvider
        from app.domain.encounters import EncounterCombatant
        trapped = build_combatant_state(template)
        assert apply_timed_condition(
            trapped, "restrained", "attacker", source_effect_id=web.id,
            applied_round=1, expires_at_start_of_source_turn=False,
            escape_check_ability="strength", escape_check_dc=control.escape_check_dc,
            breakable_object=control.breakable_object,
        ) == "restrained"
        actor = EncounterCombatant(
            combatant_id="trapped", side="heroes", position_ft=5, state=trapped,
        )
        assert should_escape_check(actor.state)
        escape = resolve_escape_check(1, 1, actor, FixedDiceProvider([20]))
        assert escape.check_succeeded
        assert not trapped.action_available
        assert "restrained" not in trapped.active_effect_ids
        fresh = build_combatant_state(template)
        assert not fresh.timed_effects and "restrained" not in fresh.active_effect_ids
    except Exception:
        logger.exception("Shared breakable condition lifecycle failed.")
        raise
