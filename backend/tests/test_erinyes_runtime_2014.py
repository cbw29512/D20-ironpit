"""The compiled poison weapon uses shared damage, save, cure and reset rules."""
import logging

import pytest

from app.combat.attacks import resolve_attack
from app.combat.condition_removal import resolve_condition_removal
from app.combat.dice import FixedDiceProvider
from app.combat.state import begin_turn, build_combatant_state
from app.content.certified_heroes import build_certified_hero_templates_for_ruleset
from app.content.monsters import build_commoner
from app.domain.encounters import EncounterCombatant
from app.domain.weapons import DamageType
from erinyes_test_support import card

logger = logging.getLogger(__name__)


@pytest.mark.parametrize("save_roll,immune,resistant,expected_poison,damage", [
    (2, False, False, True, 13),
    (20, False, False, False, 13),
    (2, True, False, False, 13),
    (2, False, True, True, 8),
])
def test_longbow_damage_and_poison_are_separate_shared_effects(save_roll, immune, resistant, expected_poison, damage):
    try:
        template = card()
        before = template.model_dump()
        bow = next(attack for attack in template.alternate_weapon_attacks if attack.weapon.name == "Longbow")
        attacker = build_combatant_state(template)
        target_card = build_commoner().model_copy(update={
            "max_hp": 200, "condition_immunities": ["poisoned"] if immune else [],
            "damage_resistances": [DamageType.POISON] if resistant else [],
        })
        target = build_combatant_state(target_card)
        event = resolve_attack(1, 1, attacker, target, bow, 20,
            FixedDiceProvider([10, 1, 2, 3, 4, save_roll]), close_enemy_active=False)
        assert event.hit and event.attack_name == "Longbow"
        assert event.damage_roll.total == damage
        assert ("poisoned" in target.active_effect_ids) is expected_poison
        assert [part.damage_type for part in event.damage_components] == [DamageType.PIERCING, DamageType.POISON]
        assert event.save_succeeded is (None if immune else save_roll == 20)
        begin_turn(target)
        assert ("poisoned" in target.active_effect_ids) is expected_poison
        assert not target.timed_effects  # No invented expiry or repeat saving throw.
        assert build_combatant_state(target_card).active_effect_ids == []
        assert template.model_dump() == before
    except Exception:
        logger.exception("Erinyes Longbow damage/save/condition parity failed: save=%s immune=%s resistant=%s.", save_roll, immune, resistant)
        raise


def test_real_2014_lesser_restoration_cures_the_persistent_poison_and_spends_its_slot():
    try:
        template = card()
        bow = next(attack for attack in template.alternate_weapon_attacks if attack.weapon.name == "Longbow")
        victim_card = build_commoner().model_copy(update={"max_hp": 200})
        victim = EncounterCombatant(combatant_id="victim", side="heroes", position_ft=0,
            state=build_combatant_state(victim_card))
        resolve_attack(1, 1, build_combatant_state(template), victim.state, bow, 20,
            FixedDiceProvider([10, 1, 2, 3, 4, 2]), close_enemy_active=False)
        cleric_card = next(item for item in build_certified_hero_templates_for_ruleset("2014")
            if item.id == "seraphine-dawnshield-2014-l3")
        cleric = EncounterCombatant(combatant_id="cleric", side="heroes", position_ft=0,
            state=build_combatant_state(cleric_card))
        action = next(item for item in cleric_card.condition_removal_actions if item.id == "lesser-restoration")
        slot = next(item for item in cleric.state.resources if item.id == "spell-slot-2")
        available = slot.current_uses
        result = resolve_condition_removal(2, 1, cleric, victim, action, ["poisoned"], "1:cleric")
        assert result.removed_condition_ids == ["poisoned"]
        assert "poisoned" not in victim.state.active_effect_ids
        assert slot.current_uses == available - 1
        assert not cleric.state.action_available
    except Exception:
        logger.exception("Canonical 2014 Lesser Restoration failed to cure source-bound poison.")
        raise
