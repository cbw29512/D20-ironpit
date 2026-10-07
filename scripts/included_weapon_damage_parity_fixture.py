"""Source-derived attacks through real compiler, serializer, and Python resolver."""
from __future__ import annotations

import json
import logging

from app.combat.attacks import resolve_attack
from app.combat.dice import FixedDiceProvider
from app.combat.state import build_combatant_state
from app.content.capability_attack_compiler import compile_attack
from app.content.capability_compiler import compile_combatant
from app.content.monster_definition_adapter_2014 import _attack, adapt_basic_monster_2014
from app.content.monster_source_2014 import load_monster_source_2014
from app.domain.weapons import DamageType
from browser_template_serializer import attack_row, template_row

logger = logging.getLogger(__name__)
_EXPECTED = {'azer': [2, 3], 'gladiator': [4, 6], 'deva': [10, 16],
             'planetar': [20, 33], 'solar': [22, 36]}


def fixture() -> list[dict]:
    try:
        source = {m.id: m for m in load_monster_source_2014()}
        before = {key: source[key].model_dump_json() for key in _EXPECTED}
        base = compile_combatant(adapt_basic_monster_2014(source['commoner']))
        gargoyle = compile_combatant(adapt_basic_monster_2014(source['gargoyle']))
        target = gargoyle.model_copy(update={
            'max_hp': 200, 'damage_immunities': [DamageType.FIRE],
            'damage_resistances': [DamageType.RADIANT],
        }, deep=True)
        cases = []
        for monster_id, expected in _EXPECTED.items():
            attack = compile_attack(_attack(source[monster_id], source[monster_id].attacks[0]))
            for critical in (False, True):
                count = attack.weapon.dice_count + sum(r.dice_count for r in attack.on_hit_damage)
                rolls = [20 if critical else 15] + [2] * count * (2 if critical else 1)
                attacker, defender = build_combatant_state(base), build_combatant_state(target)
                event = resolve_attack(1, 1, attacker, defender, attack, 5, FixedDiceProvider(rolls))
                assert event.hit and event.critical == critical
                assert event.damage_roll.total == expected[critical], (monster_id, critical, event)
                cases.append({
                    'id': f'{monster_id}-{critical}', 'attack': attack_row(attack, set()),
                    'attacker': template_row(base), 'target': template_row(target), 'rolls': rolls,
                    'critical': critical, 'total': event.damage_roll.total,
                    'remainingHp': defender.current_hp,
                    'components': [{'type': p.damage_type.value, 'total': p.total,
                                    'applied': p.applied_total, 'notation': p.notation}
                                   for p in event.damage_components],
                })
        assert before == {key: source[key].model_dump_json() for key in _EXPECTED}
        return cases
    except Exception:
        logger.exception('Included weapon damage parity fixture failed.')
        raise


if __name__ == '__main__':
    print(json.dumps(fixture()))
