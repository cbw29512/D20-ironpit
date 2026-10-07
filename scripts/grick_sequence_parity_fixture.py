"""Actual source Grick plus generic conditional-slot interruption/target evidence."""
import json
import logging
from unittest.mock import patch
from app.combat.attack_actions import resolve_attack_action
from app.combat.attack_action_sequences import attack_action_damage
from app.combat.encounter_attacks import resolve_encounter_attack
from app.combat.damage_reaction_events import resolve_damage_event_reactions
from app.combat.state import build_combatant_state
from app.content.capability_compiler import compile_combatant
from app.content.monster_definition_adapter_2014 import adapt_basic_monster_2014
from app.content.monster_source_2014 import load_monster_source_2014
from app.domain.encounters import EncounterCombatant, EncounterSetup
from app.domain.grid import GridPosition
from browser_template_serializer import template_row
logger = logging.getLogger(__name__)
CASES = {
    'hit': (15, 200, None, False, 5), 'miss': (2, 200, None, False, 5),
    'natural-one': (1, 200, None, False, 5), 'dead-target': (15, 4, None, False, 5),
    'reorder': (15, 200, 'reorder', False, 5), 'moved-target': (15, 200, 'move', False, 5),
    'redirect': (15, 200, None, True, 5), 'prerequisite-out-of-range': (15, 200, None, False, 20),
}


class ScenarioDice:
    def __init__(self, first_roll):
        try:
            self.first_roll, self.calls = first_roll, []
        except Exception:
            logger.exception('Failed conditional-slot dice setup.')
            raise

    def roll(self, sides):
        try:
            self.calls.append(sides)
            return (self.first_roll if self.calls.count(20) == 1 else 15) if sides == 20 else 1
        except Exception:
            logger.exception('Failed conditional-slot d%s.', sides)
            raise


def fixture():
    try:
        source = {m.id: m for m in load_monster_source_2014()}
        source_before = source['grick'].model_dump()
        base = compile_combatant(adapt_basic_monster_2014(source['commoner'])).model_copy(update={'max_hp': 200})
        cases = []
        for key, (roll, hp, after_first, redirect, distance) in CASES.items():
            card = compile_combatant(adapt_basic_monster_2014(source['grick']))
            if distance == 20:
                card = card.model_copy(deep=True)
                card.alternate_weapon_attacks[0].weapon.reach_ft = 25
            card_before = card.model_dump()
            actor = EncounterCombatant(combatant_id='actor', side='monsters', position_ft=0, state=build_combatant_state(card))
            targets = [EncounterCombatant(combatant_id=name, side='heroes', position_ft=0, state=build_combatant_state(base))
                       for name in ['target', 'other']]
            actor.state.position = GridPosition(x=6, y=6)
            for target in targets:
                target.state.position = GridPosition(x=6-distance//5, y=6)
                target.state.formation_row = 'front'
            targets[0].state.current_hp = hp
            setup = EncounterSetup(heroes=targets, monsters=[actor], hero_total_levels=2, monster_total_cr='0', ruleset='2014')
            before = [m.state.model_dump() for m in [actor, *targets]]
            score = attack_action_damage(actor, setup)
            assert score == (0 if distance == 20 else 14.5)
            assert [m.state.model_dump() for m in [actor, *targets]] == before
            dice = ScenarioDice(roll)

            def reactions(sequence, round_number, attacker, event, encounter, dice_provider, turn_key=None):
                try:
                    if event.weapon_id.endswith('tentacles'):
                        if after_first == 'reorder':
                            targets[0].state.formation_row = 'back'
                        if after_first == 'move':
                            targets[0].state.position = GridPosition(x=1, y=6)
                    return resolve_damage_event_reactions(sequence, round_number, attacker, event, encounter, dice_provider, turn_key=turn_key)
                except Exception:
                    logger.exception('Failed conditional-slot reaction scenario %s.', key)
                    raise

            def attack(sequence, round_number, attacker, target, weapon, attack_distance, dice_provider, encounter, **options):
                try:
                    actual = targets[1] if redirect and weapon.id.endswith('tentacles') else target
                    return resolve_encounter_attack(sequence, round_number, attacker, actual, weapon, attack_distance, dice_provider, encounter, **options)
                except Exception:
                    logger.exception('Failed conditional-slot redirected scenario %s.', key)
                    raise

            with patch('app.combat.attack_actions.resolve_damage_event_reactions', reactions), patch('app.combat.attack_actions.resolve_encounter_attack', attack):
                events, _ = resolve_attack_action(1, 1, actor, setup, dice)
            attacks = [e for e in events if e.event_type == 'attack']
            count = 0 if distance == 20 else 2 if key in {'hit', 'reorder', 'redirect'} else 1
            expected = ['2014-grick-tentacles', '2014-grick-beak'][:count]
            assert [e.weapon_id for e in attacks] == expected
            assert [e.target_id for e in attacks] == [('other' if redirect else 'target')] * count
            assert actor.state.action_available == (distance == 20)
            assert actor.state.bonus_action_available == (roll != 1), key
            assert card.model_dump() == card_before, key
            cases.append({'id': key, 'actor': template_row(card), 'target': template_row(base),
                'initialHp': hp, 'distance': distance, 'firstRoll': roll, 'afterFirst': after_first,
                'redirectFirst': redirect, 'score': score, 'weapons': expected,
                'targetIds': [e.target_id for e in attacks], 'diceCalls': dice.calls,
                'remainingHp': [t.state.current_hp for t in targets], 'actionAvailable': actor.state.action_available,
                'turnTerminated': actor.state.turn_terminated, 'bonusActionAvailable': actor.state.bonus_action_available})
        assert source['grick'].model_dump() == source_before
        return cases
    except Exception:
        logger.exception('Grick source and conditional-slot parity fixture failed.')
        raise


if __name__ == '__main__':
    print(json.dumps(fixture()))
