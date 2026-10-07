import json
from pathlib import Path
import sys

import pytest

from app.content.capability_attack_compiler import compile_attack
from app.content.monster_basic_candidates_2014 import basic_blockers_2014, unsupported_traits_2014
from app.content.monster_definition_adapter_2014 import _attack, adapt_basic_monster_2014
from app.content.monster_included_weapon_traits_2014 import (
    included_weapon_trait_names_2014, weapon_damage_source_qualifiers_2014,
)
from app.content.monster_source_2014 import load_monster_source_2014
from app.domain.weapons import DamageSourceQualifier

FAMILY = {
    'azer': 'Heated Weapons', 'salamander': 'Heated Weapons',
    'bugbear': 'Brute', 'gladiator': 'Brute',
    'deva': 'Angelic Weapons', 'planetar': 'Angelic Weapons', 'solar': 'Angelic Weapons',
}


def source(monster_id):
    return next(m for m in load_monster_source_2014() if m.id == monster_id)


@pytest.mark.parametrize('monster_id,trait', FAMILY.items())
def test_included_damage_family_binds_without_certifying_other_mechanics(monster_id, trait):
    monster = source(monster_id)
    before = monster.model_dump_json()
    assert included_weapon_trait_names_2014(monster) == {trait}
    assert trait not in unsupported_traits_2014(monster)
    if monster_id == 'gladiator':
        # Its final independent blocker is now source-proven complete Multiattack.
        assert basic_blockers_2014(monster) == ()
        action = adapt_basic_monster_2014(monster).attack_action
        assert [(v.attack_kind.value, len(v.slots)) for v in action.variants] == [('melee', 3), ('ranged', 2)]
    else:
        assert basic_blockers_2014(monster)
        with pytest.raises(ValueError, match='not a basic 2014 candidate'):
            adapt_basic_monster_2014(monster)
    assert monster.model_dump_json() == before


@pytest.mark.parametrize('monster_id', ['azer', 'gladiator', 'deva', 'planetar', 'solar'])
def test_source_compilation_preserves_base_and_rider_dice_exactly_once(monster_id):
    monster = source(monster_id)
    for raw in monster.attacks:
        if not raw.source_complete:
            continue
        attack = compile_attack(_attack(monster, raw))
        assert (attack.weapon.dice_count, attack.weapon.dice_size, attack.damage_bonus) == (
            raw.damage.dice_count, raw.damage.dice_size, raw.damage.bonus,
        )
        assert [(r.dice_count, r.dice_size, r.damage_type.value) for r in attack.on_hit_damage] == [
            (r['dice_count'], r['dice_size'], r['type']) for r in raw.on_hit_damage
        ]
        assert not attack.conditional_damage
        assert attack.damage_source_qualifiers == (
            [DamageSourceQualifier.MAGICAL] if FAMILY[monster_id] == 'Angelic Weapons' else []
        )


@pytest.mark.parametrize('monster_id', FAMILY)
@pytest.mark.parametrize('mutation', ['missing_traits', 'missing_actions', 'not_included', 'wrong_base'])
def test_source_validation_fails_closed(monster_id, mutation):
    monster = source(monster_id).model_copy(deep=True)
    if mutation == 'missing_traits':
        monster.source_traits = None
    elif mutation == 'missing_actions':
        monster.source_actions = None
    elif mutation == 'not_included':
        monster.source_traits = monster.source_traits.replace('included in the attack', 'added later')
    else:
        monster.attacks[0].damage.dice_count += 1
    assert not included_weapon_trait_names_2014(monster)
    if FAMILY[monster_id] == 'Angelic Weapons':
        assert not weapon_damage_source_qualifiers_2014(monster)


@pytest.mark.parametrize('monster_id', ['azer', 'salamander', 'deva', 'planetar', 'solar'])
@pytest.mark.parametrize('mutation', ['missing', 'duplicate', 'wrong_type', 'extra_damage'])
def test_included_rider_must_match_printed_payload_once(monster_id, mutation):
    monster = source(monster_id).model_copy(deep=True)
    rows = monster.attacks[0].on_hit_damage
    if mutation == 'missing':
        rows.clear()
    elif mutation == 'duplicate':
        rows.append(dict(rows[0]))
    elif mutation == 'wrong_type':
        rows[0]['type'] = 'necrotic'
    else:
        rows.append({**rows[0], 'dice_count': 12})
    assert not included_weapon_trait_names_2014(monster)


def test_thrown_and_two_handed_variants_preserve_printed_dice():
    assert [a.damage.dice_count for a in source('bugbear').attacks] == [2, 2, 1]
    gladiator = source('gladiator')
    assert [(a.damage.dice_count, a.damage.dice_size) for a in gladiator.attacks] == [
        (2, 6), (2, 6), (2, 8), (2, 4),
    ]
    salamander = source('salamander')
    assert [a.on_hit_damage[0]['dice_count'] for a in salamander.attacks] == [1, 1, 1, 2]
    assert salamander.attacks[-1].grapple_target_policy == 'auto_hit_own_grapple'


def test_2024_native_source_has_no_included_weapon_traits_to_copy():
    rows = json.loads((Path(__file__).parents[1] / 'app/content/data/srd_5_2_1_monsters.json').read_text())
    for row in rows:
        assert not any(name in row['traits'] for name in set(FAMILY.values()))


def test_source_derived_browser_parity_fixture_is_current():
    root = Path(__file__).parents[2]
    sys.path.insert(0, str(root / 'scripts'))
    from included_weapon_damage_parity_fixture import fixture
    saved = json.loads((root / 'frontend/test-fixtures/included-weapon-damage.json').read_text())
    assert fixture() == saved
