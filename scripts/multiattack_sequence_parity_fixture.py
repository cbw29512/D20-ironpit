"""Source/compiler/serializer/reference evidence for complete Multiattack choices."""
from __future__ import annotations
import json
import logging
from app.combat.attack_actions import resolve_attack_action
from app.combat.attack_action_sequences import attack_action_damage, select_sequence
from app.combat.state import build_combatant_state
from app.content.capability_compiler import compile_combatant
from app.content.monster_definition_adapter_2014 import adapt_basic_monster_2014
from app.content.monster_source_2014 import load_monster_source_2014
from app.domain.encounters import EncounterCombatant, EncounterSetup
from app.domain.grid import GridPosition
from browser_template_serializer import template_row
logger = logging.getLogger(__name__)
_EXPECTED = {
    'bandit-captain': {5: (['scimitar', 'scimitar', 'dagger-melee'], 18.5),
                      20: (['dagger-ranged', 'dagger-ranged'], 11)},
    'gladiator': {5: (['spear'] * 3, 33), 20: (['spear-ranged'] * 2, 22)},
    'lizardfolk': {5: (['bite', 'heavy-club'], 11), 20: ([], 0)},
}


class RecordingDice:
    def __init__(self):
        try:
            self.calls = []
        except Exception:
            logger.exception('Failed source-sequence dice setup.')
            raise

    def roll(self, sides):
        try:
            self.calls.append(sides)
            return 15 if sides == 20 else 1
        except Exception:
            logger.exception('Failed source-sequence roll d%s.', sides)
            raise


def fixture(expected=None):
    try:
        source = {m.id: m for m in load_monster_source_2014()}
        base = compile_combatant(adapt_basic_monster_2014(source['commoner'])).model_copy(update={'max_hp': 200})
        cases = []
        for source_id, distances in (_EXPECTED if expected is None else expected).items():
            card = compile_combatant(adapt_basic_monster_2014(source[source_id]))
            card_before = card.model_dump()
            for distance, (weapons, score) in distances.items():
                actor = EncounterCombatant(combatant_id='actor', side='monsters', position_ft=0,
                    state=build_combatant_state(card))
                target = EncounterCombatant(combatant_id='target', side='heroes', position_ft=0,
                    state=build_combatant_state(base))
                actor.state.position = GridPosition(x=6, y=6)
                actor.state.formation_row = 'back'
                target.state.position = GridPosition(x=6-distance//5, y=6)
                setup = EncounterSetup(heroes=[target], monsters=[actor], hero_total_levels=1,
                                       monster_total_cr='0', ruleset='2014')
                before = actor.state.model_dump()
                selected = select_sequence(actor, setup)
                assert attack_action_damage(actor, setup) == score
                assert actor.state.model_dump() == before
                dice = RecordingDice()
                events, _ = resolve_attack_action(1, 1, actor, setup, dice)
                expected = [f'2014-{source_id}-{i}' for i in weapons]
                assert [e.weapon_id for e in events if e.event_type == 'attack'] == expected
                assert card.model_dump() == card_before
                assert actor.state.bonus_action_available
                cases.append({'id': f'{source_id}-{distance}', 'actor': template_row(card),
                    'target': template_row(base), 'distance': distance, 'score': score,
                    'weapons': expected, 'variant': selected[0].id if selected else None,
                    'diceCalls': dice.calls, 'remainingHp': target.state.current_hp,
                    'actionAvailable': actor.state.action_available})
        return cases
    except Exception:
        logger.exception('Complete source Multiattack parity fixture failed.')
        raise


if __name__ == '__main__':
    print(json.dumps(fixture()))
