import json
import sys
from pathlib import Path
import pytest
from pydantic import ValidationError
from app.content.monster_source_2014 import load_monster_source_2014
from app.content.monster_basic_candidates_2014 import basic_blockers_2014
from app.content.monster_definition_adapter_2014 import adapt_basic_monster_2014
from app.content.monster_multiattack_2014 import multiattack_2014
from app.domain.attack_action_definitions import AttackActionDefinition, AttackActionSlot, PreviousAttackRequirement
from app.combat.attack_action_choices import followup_target
ROOT = Path(__file__).parents[2]
sys.path.insert(0, str(ROOT / 'scripts'))
from grick_sequence_parity_fixture import fixture


def source():
    return next(m for m in load_monster_source_2014() if m.id == 'grick')


def test_printed_followup_survives_source_compiler_serializer_and_browser_oracle():
    monster = source()
    before = monster.model_dump()
    assert basic_blockers_2014(monster) == ()
    variant, = multiattack_2014(monster).variants
    assert [s.attack_ids for s in variant.slots] == [['2014-grick-tentacles'], ['2014-grick-beak']]
    assert variant.slots[0].previous_attack is None
    assert variant.slots[1].previous_attack.model_dump() == {'hit': True, 'same_target': True}
    assert fixture() == json.loads((ROOT / 'frontend/test-fixtures/grick-sequence.json').read_text())
    assert monster.model_dump() == before


@pytest.mark.parametrize('mutation', ['wording', 'miss_wording', 'target_wording', 'unknown', 'count', 'empty', 'policy', 'weapon_name'])
def test_mutated_followup_source_blocks_whole_card(mutation):
    monster = source().model_copy(deep=True)
    if mutation == 'wording':
        monster.source_actions = monster.source_actions.replace('Multiattack.', 'Missing.')
    elif mutation == 'miss_wording':
        monster.source_actions = monster.source_actions.replace('If that attack hits', 'If that attack misses')
    elif mutation == 'target_wording':
        monster.source_actions = monster.source_actions.replace('the same target', 'a different target')
    elif mutation == 'unknown':
        monster.multiattack_slots[1] = ['unbound']
    elif mutation == 'count':
        monster.multiattack_slots.append(['beak'])
    elif mutation == 'empty':
        monster.multiattack_slots[0] = []
    elif mutation == 'policy':
        monster.multiattack_policy['same_target_as_previous_slots'] = []
    else:
        monster.attacks[1].name = 'Unrelated Weapon'
    assert 'multiattack:complex' in basic_blockers_2014(monster)
    with pytest.raises(ValueError):
        multiattack_2014(monster)
    with pytest.raises(ValueError):
        adapt_basic_monster_2014(monster)


@pytest.mark.parametrize('rule', [{}, {'hit': 'true'}, {'hit': True, 'unknown': True}])
def test_invalid_conditional_metadata_fails_before_resolution(rule):
    with pytest.raises(ValidationError):
        PreviousAttackRequirement.model_validate(rule)


def test_conditional_slot_cannot_be_first_or_follow_a_save_choice():
    dependent = AttackActionSlot(attack_ids=['b'], previous_attack=PreviousAttackRequirement(hit=True, same_target=True))
    for slots in [[dependent], [AttackActionSlot(save_action_ids=['s']), dependent]]:
        with pytest.raises(ValidationError, match='immediately preceding attack-only'):
            AttackActionDefinition(id='generic', name='Generic', slots=slots)


def test_shared_condition_is_independent_of_creature_and_weapon_names():
    slot = AttackActionSlot(attack_ids=['renamed-profile'], previous_attack=PreviousAttackRequirement(hit=True, same_target=True))
    assert followup_target(slot, True, 'actual-redirected-target') == (True, 'actual-redirected-target')
    assert followup_target(slot, False, 'actual-redirected-target') == (False, None)
    assert followup_target(slot, None, None) == (False, None)
    assert followup_target(slot, True, None) == (False, None)
