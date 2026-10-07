import json
import pytest
from test_multiattack_sequences_2014 import source, setup_for, ROOT, RecordingDice
from veteran_multiattack_parity_fixture import EXPECTED
from multiattack_sequence_parity_fixture import fixture
from app.combat.attack_actions import resolve_attack_action
from app.combat.attacks import resolve_attack
from app.combat.encounter_attacks import resolve_encounter_attack
from app.combat.pit_policy import choose_standard_attack
from app.content.monster_basic_candidates_2014 import basic_blockers_2014
from app.content.monster_multiattack_2014 import multiattack_2014
from app.content.monster_definition_adapter_2014 import adapt_basic_monster_2014


def test_veteran_browser_fixture_is_current():
    assert fixture(EXPECTED) == json.loads((ROOT / 'frontend/test-fixtures/veteran-multiattack.json').read_text())


@pytest.mark.parametrize('key,ac', [('veteran', 17), ('half-red-dragon-veteran', 18)])
def test_fixed_printed_loadout_and_single_crossbow_fallback(key, ac):
    monster = source(key)
    before = monster.model_dump()
    assert basic_blockers_2014(monster) == ()
    actor, target, setup = setup_for(key, 20)
    card = actor.state.template
    assert card.armor_class == ac
    variant, = card.attack_action.variants
    assert variant.attack_kind.value == 'melee' and not card.attack_action.is_attack_action
    assert [s.attack_ids for s in variant.slots] == [[f'2014-{key}-{i}'] for i in ['longsword', 'longsword', 'shortsword']]
    attacks = [card.weapon_attack, *card.alternate_weapon_attacks]
    two = next(a for a in attacks if a.id.endswith('longsword-two-handed'))
    assert (two.weapon.dice_count, two.weapon.dice_size, two.damage_bonus) == (1, 10, 3)
    assert two.unavailable_reason
    prior = [actor.state.model_dump(), target.state.model_dump()]
    dice = RecordingDice()
    with pytest.raises(RuntimeError):
        resolve_attack(1, 1, actor.state, target.state, two, 5, dice)
    assert [actor.state.model_dump(), target.state.model_dump()] == prior and not dice.calls
    assert resolve_attack_action(1, 1, actor, setup, dice) == ([], 1)
    assert actor.state.action_available and not dice.calls
    chosen_target, crossbow, distance = choose_standard_attack(actor, setup)
    assert crossbow.id == f'2014-{key}-heavy-crossbow'
    assert (crossbow.weapon.normal_range_ft, crossbow.weapon.long_range_ft) == (100, 400)
    event = resolve_encounter_attack(1, 1, actor, chosen_target, crossbow, distance, dice, setup)
    assert event.weapon_id == crossbow.id and event.damage_roll.total == 2
    assert dice.calls == [20, 10] and not actor.state.action_available
    assert actor.state.bonus_action_available and source(key).model_dump() == before


@pytest.mark.parametrize('key', ['veteran', 'half-red-dragon-veteran'])
@pytest.mark.parametrize('mutation', ['wording', 'count', 'empty', 'unknown', 'policy', 'two_hand_proof'])
def test_invalid_offhand_source_fails_whole_card(key, mutation):
    monster = source(key).model_copy(deep=True)
    if mutation == 'wording':
        monster.source_actions = monster.source_actions.replace('Multiattack.', 'Missing.')
    elif mutation == 'count':
        monster.multiattack_slots.append(['shortsword'])
    elif mutation == 'empty':
        monster.multiattack_slots[0] = []
    elif mutation == 'unknown':
        monster.multiattack_slots[0].append('unbound')
    elif mutation == 'policy':
        monster.multiattack_policy['incompatible_attack_ids'] = []
    else:
        monster.source_actions = monster.source_actions.replace('if used with two hands', 'if used with three hands')
    assert 'multiattack:complex' in basic_blockers_2014(monster)
    with pytest.raises(ValueError):
        multiattack_2014(monster)
    with pytest.raises(ValueError):
        adapt_basic_monster_2014(monster)


def test_half_red_dragon_breath_retains_independent_printed_profile():
    actor, _, _ = setup_for('half-red-dragon-veteran')
    breath, = actor.state.template.saving_throw_actions
    assert (breath.id, breath.save_ability, breath.dc) == ('fire-breath', 'dexterity', 15)
    assert (breath.damage_dice_count, breath.damage_dice_size, breath.success_damage) == (7, 6, 'half')
    assert breath.area.shape == 'cone' and breath.area.length_ft == 15
    recharge, = actor.state.template.recharge_rules
    assert (recharge.minimum_roll, recharge.die_size) == (5, 6)
