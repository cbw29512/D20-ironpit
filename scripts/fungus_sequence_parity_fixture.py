"""Printed random-count source through shared dice and ordinary slot resolution."""
import json
import logging
from app.combat.attack_actions import resolve_attack_action
from app.combat.attack_action_sequences import attack_action_damage
from app.combat.state import build_combatant_state
from app.content.capability_compiler import compile_combatant
from app.content.monster_definition_adapter_2014 import adapt_basic_monster_2014
from app.content.monster_source_2014 import load_monster_source_2014
from app.domain.encounters import EncounterCombatant, EncounterSetup
from app.domain.grid import GridPosition
from browser_template_serializer import template_row
logger = logging.getLogger(__name__)
CASES = [(f'count-{n}', n, 15, 200, 10) for n in range(1, 5)] + [
    ('natural-one', 4, 1, 200, 10), ('retarget', 4, 15, 1, 10), ('no-range', 4, 15, 200, 15)]


class ScenarioDice:
    def __init__(self, count, attack_roll):
        try:
            self.count, self.attack_roll, self.calls = count, attack_roll, []
        except Exception:
            logger.exception('Failed random sequence dice setup.')
            raise

    def roll(self, sides):
        try:
            self.calls.append(sides)
            return self.count if sides == 4 else self.attack_roll if sides == 20 else 1
        except Exception:
            logger.exception('Failed random sequence d%s.', sides)
            raise


def fixture():
    try:
        sources = {m.id: m for m in load_monster_source_2014()}
        before_source = sources['violet-fungus'].model_dump()
        card = compile_combatant(adapt_basic_monster_2014(sources['violet-fungus']))
        before_card = card.model_dump()
        base = compile_combatant(adapt_basic_monster_2014(sources['commoner'])).model_copy(update={'max_hp': 200})
        cases = []
        for key, count, attack_roll, hp, distance in CASES:
            actor = EncounterCombatant(combatant_id='actor', side='monsters', position_ft=0, state=build_combatant_state(card))
            targets = [EncounterCombatant(combatant_id=i, side='heroes', position_ft=0, state=build_combatant_state(base)) for i in ['target', 'other']]
            actor.state.position = GridPosition(x=6, y=6)
            for target in targets:
                target.state.position = GridPosition(x=6-distance//5, y=6)
            targets[0].state.current_hp = hp
            setup = EncounterSetup(heroes=targets, monsters=[actor], hero_total_levels=2, monster_total_cr='0', ruleset='2014')
            before = [m.state.model_dump() for m in [actor, *targets]]
            dice = ScenarioDice(count, attack_roll)
            score = attack_action_damage(actor, setup)
            assert score == (0 if distance > 10 else 11.25)
            assert not dice.calls and [m.state.model_dump() for m in [actor, *targets]] == before
            events, _ = resolve_attack_action(1, 1, actor, setup, dice)
            attacks = [e for e in events if e.event_type == 'attack']
            expected_count = 0 if distance > 10 else 1 if attack_roll == 1 else count
            assert len(attacks) == expected_count
            assert [e.weapon_id for e in attacks] == ['2014-violet-fungus-rotting-touch'] * expected_count
            repetitions = [e for e in events if e.feature_roll is not None]
            assert len(repetitions) == (0 if distance > 10 else 1)
            if repetitions:
                assert repetitions[0].feature_roll.total == count and repetitions[0].feature_roll.rolls == [count]
                assert repetitions[0].sequence < attacks[0].sequence
                assert repetitions[0].audit.steps[0].phase.value == 'roll'
            assert dice.calls.count(4) == (0 if distance > 10 else 1)
            assert actor.state.action_available == (distance > 10)
            assert card.model_dump() == before_card
            cases.append({'id': key, 'actor': template_row(card), 'target': template_row(base), 'initialHp': hp,
                'distance': distance, 'count': count, 'attackRoll': attack_roll, 'score': score,
                'weapons': [e.weapon_id for e in attacks], 'targetIds': [e.target_id for e in attacks],
                'repetitionRoll': repetitions[0].feature_roll.model_dump(mode='json') if repetitions else None,
                'diceCalls': dice.calls, 'remainingHp': [t.state.current_hp for t in targets],
                'actionAvailable': actor.state.action_available, 'bonusActionAvailable': actor.state.bonus_action_available,
                'turnTerminated': actor.state.turn_terminated})
        assert sources['violet-fungus'].model_dump() == before_source
        return cases
    except Exception:
        logger.exception('Violet Fungus source random-count parity fixture failed.')
        raise


if __name__ == '__main__':
    print(json.dumps(fixture()))
