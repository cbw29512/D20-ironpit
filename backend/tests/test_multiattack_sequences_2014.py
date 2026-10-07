import json
import sys
from pathlib import Path
import pytest
from app.combat.attack_actions import resolve_attack_action
from app.combat.attacks import resolve_attack
from app.combat.attack_action_sequences import attack_action_damage
from app.combat.pit_policy import choose_standard_attack
from app.combat.state import build_combatant_state
from app.content.capability_compiler import compile_combatant
from app.content.monster_definition_adapter_2014 import adapt_basic_monster_2014
from app.content.monster_multiattack_2014 import multiattack_2014
from app.content.monster_basic_candidates_2014 import basic_blockers_2014
from app.content.monster_source_2014 import load_monster_source_2014
from app.domain.attack_action_definitions import AttackActionDefinition, AttackActionSlot, AttackActionVariant
from app.domain.encounters import EncounterCombatant, EncounterSetup
from app.domain.grid import GridPosition
from app.domain.weapons import DamageType, OnHitDamage
ROOT = Path(__file__).parents[2]
sys.path.insert(0, str(ROOT / 'scripts'))
from multiattack_sequence_parity_fixture import fixture, RecordingDice


def source(key):
    return next(m for m in load_monster_source_2014() if m.id == key)


def setup_for(key='gladiator', distance=5):
    card = compile_combatant(adapt_basic_monster_2014(source(key)))
    target_card = compile_combatant(adapt_basic_monster_2014(source('commoner'))).model_copy(update={'max_hp': 200})
    actor = EncounterCombatant(combatant_id='actor', side='monsters', position_ft=0, state=build_combatant_state(card))
    target = EncounterCombatant(combatant_id='target', side='heroes', position_ft=0, state=build_combatant_state(target_card))
    actor.state.position = GridPosition(x=6, y=6)
    target.state.position = GridPosition(x=6-distance//5, y=6)
    setup = EncounterSetup(heroes=[target], monsters=[actor], hero_total_levels=1, monster_total_cr='0', ruleset='2014')
    return actor, target, setup


def test_source_derived_browser_fixture_is_current():
    assert fixture() == json.loads((ROOT / 'frontend/test-fixtures/multiattack-sequences.json').read_text())


@pytest.mark.parametrize('key', ['bandit-captain', 'gladiator', 'medusa'])
def test_whole_alternatives_preserve_source_counts_and_mandatory_combinations(key):
    monster = source(key)
    before = monster.model_dump()
    action = multiattack_2014(monster)
    assert not action.slots
    assert [(v.attack_kind.value, len(v.slots)) for v in action.variants] == [('melee', 3), ('ranged', 2)]
    assert not action.is_attack_action
    if key == 'bandit-captain':
        assert [slot.attack_ids for slot in action.variants[0].slots] == [[f'2014-{key}-scimitar']] * 2 + [[f'2014-{key}-dagger-melee']]
    if key == 'medusa':
        assert [slot.attack_ids for slot in action.variants[0].slots] == [[f'2014-{key}-snake-hair']] + [[f'2014-{key}-shortsword']] * 2
        assert basic_blockers_2014(monster) == ('source:trait',)
    assert monster.model_dump() == before


def test_distinct_weapons_are_complete_pairs_never_two_copies_of_best_weapon():
    variants = multiattack_2014(source('lizardfolk')).variants
    assert len(variants) == 12
    assert all(len(v.slots) == 2 and v.slots[0].attack_ids != v.slots[1].attack_ids for v in variants)
    assert len({tuple(s.attack_ids[0] for s in v.slots) for v in variants}) == 12
    actor, _, setup = setup_for('lizardfolk', 20)
    assert attack_action_damage(actor, setup) == 0
    assert choose_standard_attack(actor, setup)[1].id == '2014-lizardfolk-javelin-ranged'


@pytest.mark.parametrize('key', ['bandit-captain', 'gladiator', 'medusa', 'lizardfolk', 'grick'])
@pytest.mark.parametrize('mutation', ['wording', 'count', 'empty', 'unknown'])
def test_source_mutations_fail_closed(key, mutation):
    monster = source(key).model_copy(deep=True)
    if mutation == 'wording':
        monster.source_actions = monster.source_actions.replace('Multiattack.', 'Missing.')
    elif mutation == 'count':
        monster.multiattack_slots.append(monster.multiattack_slots[0])
    elif mutation == 'empty':
        monster.multiattack_slots[0] = []
    else:
        monster.multiattack_slots[0].append('unbound')
    assert 'multiattack:complex' in basic_blockers_2014(monster)
    with pytest.raises(ValueError):
        multiattack_2014(monster)



def test_grick_hit_follow_up_binds_generic_slot_policy():
    monster = source('grick')
    before = monster.model_dump()
    action = multiattack_2014(monster)
    assert basic_blockers_2014(monster) == ()
    assert len(action.variants) == 1
    slots = action.variants[0].slots
    assert [slot.attack_ids for slot in slots] == [
        ['2014-grick-tentacles'], ['2014-grick-beak'],
    ]
    assert not slots[0].requires_previous_hit and not slots[0].same_target_as_previous
    assert slots[1].requires_previous_hit and slots[1].same_target_as_previous
    actor, _, setup = setup_for('grick', 5)
    assert attack_action_damage(actor, setup) == 14
    assert monster.model_dump() == before


def test_grick_tentacles_miss_skips_beak_without_ending_turn():
    class MissDice(RecordingDice):
        def roll(self, sides):
            self.calls.append(sides)
            return 2 if sides == 20 else 1

    actor, _, setup = setup_for('grick', 5)
    events, _ = resolve_attack_action(1, 1, actor, setup, MissDice())
    attacks = [event for event in events if event.event_type == 'attack']
    assert [event.weapon_id for event in attacks] == ['2014-grick-tentacles']
    assert attacks[0].hit is False
    assert not actor.state.turn_terminated


def test_grick_beak_does_not_retarget_after_tentacles_kills_target():
    actor, target, setup = setup_for('grick', 5)
    target.state.current_hp = 1
    other = EncounterCombatant(
        combatant_id='other', side='heroes', position_ft=0,
        state=build_combatant_state(target.state.template),
    )
    other.state.position = GridPosition(x=5, y=6)
    setup.heroes.append(other)
    before_other_hp = other.state.current_hp
    events, _ = resolve_attack_action(1, 1, actor, setup, RecordingDice())
    assert [event.weapon_id for event in events if event.event_type == 'attack'] == [
        '2014-grick-tentacles',
    ]
    assert target.state.current_hp == 0
    assert other.state.current_hp == before_other_hp

def test_fixed_shield_blocks_direct_two_handed_attack_without_mutation_or_dice():
    actor, target, _ = setup_for()
    attack = next(a for a in actor.state.template.alternate_weapon_attacks if a.id.endswith('spear-two-handed'))
    assert attack.weapon.dice_size == 8 and attack.unavailable_reason
    assert actor.state.template.armor_class == 16
    before = [actor.state.model_dump(), target.state.model_dump()]
    dice = RecordingDice()
    with pytest.raises(RuntimeError, match="Attack resolution failed") as caught:
        resolve_attack(1, 1, actor.state, target.state, attack, 5, dice)
    assert isinstance(caught.value.__cause__, ValueError)
    assert not dice.calls
    assert [actor.state.model_dump(), target.state.model_dump()] == before


def test_unselected_unknown_branch_is_validated_before_action_dice_or_damage():
    actor, target, setup = setup_for()
    action = actor.state.template.attack_action.model_copy(deep=True)
    action.variants[1].slots[0].attack_ids = ['unbound']
    actor.state.template = actor.state.template.model_copy(update={'attack_action': action})
    before = [actor.state.model_dump(), target.state.model_dump()]
    dice = RecordingDice()
    with pytest.raises(ValueError, match='Unknown Multiattack IDs'):
        resolve_attack_action(1, 1, actor, setup, dice)
    assert not dice.calls
    assert [actor.state.model_dump(), target.state.model_dump()] == before


def test_damage_riders_can_make_lower_base_damage_the_best_legal_choice():
    actor, _, setup = setup_for()
    card = actor.state.template.model_copy(deep=True)
    bash = next(a for a in card.alternate_weapon_attacks if a.id.endswith('shield-bash'))
    bash.on_hit_damage = [OnHitDamage(source='renamed-rider', dice_count=4, dice_size=6, damage_type=DamageType.POISON)]
    actor.state.template = card
    assert choose_standard_attack(actor, setup)[1].id == bash.id
    assert attack_action_damage(actor, setup) == 69
    events, _ = resolve_attack_action(1, 1, actor, setup, RecordingDice())
    assert [e.weapon_id for e in events if e.event_type == 'attack'] == [bash.id] * 3


@pytest.mark.parametrize('payload', [{}, {'slots': [AttackActionSlot(attack_ids=['a'])], 'variants': [AttackActionVariant(id='b', slots=[AttackActionSlot(attack_ids=['a'])])]}])
def test_definition_has_exactly_one_sequence_representation(payload):
    with pytest.raises(ValueError, match='either slots or complete variants'):
        AttackActionDefinition(id='invalid', name='Invalid', **payload)


@pytest.mark.parametrize('mutation', ['missing_id', 'wrong_kind'])
def test_unselected_branch_schema_and_kind_fail_before_mutation(mutation):
    actor, target, setup = setup_for()
    action = actor.state.template.attack_action.model_copy(deep=True)
    if mutation == 'missing_id':
        action.variants[1].id = None
    else:
        action.variants[1].attack_kind = action.variants[0].attack_kind
    actor.state.template = actor.state.template.model_copy(update={'attack_action': action})
    before = [actor.state.model_dump(), target.state.model_dump()]
    dice = RecordingDice()
    with pytest.raises(ValueError):
        resolve_attack_action(1, 1, actor, setup, dice)
    assert not dice.calls
    assert [actor.state.model_dump(), target.state.model_dump()] == before
