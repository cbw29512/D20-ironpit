import json
import sys
from pathlib import Path
import pytest
from pydantic import ValidationError
from app.content.monster_source_2014 import load_monster_source_2014
from app.content.monster_basic_candidates_2014 import basic_blockers_2014
from app.content.monster_multiattack_2014 import multiattack_2014
from app.content.monster_definition_adapter_2014 import adapt_basic_monster_2014
from app.domain.attack_action_definitions import AttackActionDefinition, AttackActionSlot, AttackActionVariant, AttackSequenceRepetition
ROOT = Path(__file__).parents[2]
sys.path.insert(0, str(ROOT / 'scripts'))
from fungus_sequence_parity_fixture import fixture


def source():
    return next(m for m in load_monster_source_2014() if m.id == 'violet-fungus')


def test_source_random_count_roundtrip_and_browser_fixture():
    monster = source()
    before = monster.model_dump()
    assert basic_blockers_2014(monster) == ()
    variant, = multiattack_2014(monster).variants
    assert variant.repetitions.model_dump() == {'dice_count': 1, 'dice_size': 4}
    assert [s.attack_ids for s in variant.slots] == [['2014-violet-fungus-rotting-touch']]
    assert fixture() == json.loads((ROOT / 'frontend/test-fixtures/fungus-sequence.json').read_text())
    assert monster.model_dump() == before


@pytest.mark.parametrize('mutation', ['wording', 'dice', 'count', 'unknown', 'empty', 'policy', 'name'])
def test_invalid_random_source_fails_whole_card(mutation):
    monster = source().model_copy(deep=True)
    if mutation == 'wording':
        monster.source_actions = monster.source_actions.replace('Multiattack.', 'Missing.')
    elif mutation == 'dice':
        monster.source_actions = monster.source_actions.replace('1d4 Rotting', '1d6 Rotting')
    elif mutation == 'count':
        monster.multiattack_slots.append(['rotting-touch'])
    elif mutation == 'unknown':
        monster.multiattack_slots[0] = ['unbound']
    elif mutation == 'empty':
        monster.multiattack_slots[0] = []
    elif mutation == 'policy':
        monster.multiattack_policy['repeat_slot_index'] = 1
    else:
        monster.attacks[0].name = 'Unrelated Weapon'
    assert 'multiattack:complex' in basic_blockers_2014(monster)
    with pytest.raises(ValueError):
        multiattack_2014(monster)
    with pytest.raises(ValueError):
        adapt_basic_monster_2014(monster)


@pytest.mark.parametrize('r', [{'dice_count': True, 'dice_size': 4}, {'dice_count': 1, 'dice_size': 9},
                             {'dice_count': 1, 'dice_size': 4, 'unknown': True}])
def test_invalid_repetition_metadata_rejected(r):
    with pytest.raises(ValidationError):
        AttackSequenceRepetition.model_validate(r)


def test_maximum_expanded_sequence_is_bounded_before_resolution():
    repeat = AttackSequenceRepetition(dice_count=3, dice_size=4)
    with pytest.raises(ValidationError, match='maximum exceeds eight slots'):
        AttackActionDefinition(id='generic', name='Generic', variants=[AttackActionVariant(id='generic-variant',
            slots=[AttackActionSlot(attack_ids=['renamed-profile'])], repetitions=repeat)])
