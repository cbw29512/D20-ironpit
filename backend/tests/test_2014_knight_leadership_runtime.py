"""Knight Leadership (SRD 5.1 2014) through the universal TimedFriendlyRollBonusAura.

Printed source: "For 1 minute, the knight can utter a special command or warning
whenever a nonhostile creature that it can see within 30 feet of it makes an attack
roll or a saving throw. The creature can add a d4 to its roll provided it can hear
and understand the knight. A creature can benefit from only one Leadership die at a
time. This effect ends if the knight is incapacitated." (Recharges after a Short or
Long Rest -> one use per Iron Pit fight; no rest occurs mid-fight.)
"""
from __future__ import annotations

import pytest

from app.combat.friendly_roll_bonus_auras import roll_bonus_aura_relevant, sync_friendly_roll_bonus_auras
from app.combat.modifier_stack import apply_d20_bonus_dice
from app.combat.source_bound_effects import cleanup_disabled_source_effects
from app.combat.state import begin_turn, build_combatant_state
from app.combat.timed_self_buffs import resolve_timed_self_buff
from app.content.arena_map import build_standard_iron_pit_map
from app.content.capability_compiler import compile_combatant
from app.content.monster_basic_candidates_2014 import basic_blockers_2014
from app.content.monster_definition_adapter_2014 import adapt_basic_monster_2014
from app.content.monster_leadership_2014 import leadership_actions_2014
from app.content.monster_source_2014 import load_monster_source_2014
from app.content.monsters import build_commoner
from app.domain.events import DiceRoll
from app.domain.encounters import EncounterCombatant, EncounterSetup
from app.domain.grid import GridPosition
from app.domain.modifiers import ModifierKind


def _knight_source():
    return next(m for m in load_monster_source_2014() if m.id == "knight")


def _member(cid, side, template, x):
    member = EncounterCombatant(combatant_id=cid, side=side, position_ft=x * 5,
                                state=build_combatant_state(template))
    member.state.position = GridPosition(x=x, y=7)
    return member


def _setup(heroes, monsters):
    return EncounterSetup(heroes=heroes, monsters=monsters, hero_total_levels=1,
                          monster_total_cr="3", ruleset="2014",
                          map_definition=build_standard_iron_pit_map())


def _knight_template():
    return compile_combatant(adapt_basic_monster_2014(_knight_source()))


class _FixedDice:
    def roll(self, size):
        return 3


def test_source_binding_preserves_printed_terms_and_clears_only_blocker():
    source = _knight_source()
    original = source.model_dump_json()
    assert basic_blockers_2014(source) == ()
    [action] = leadership_actions_2014(source)
    aura = action.friendly_roll_bonus_aura
    assert (action.name, action.duration_rounds, action.concentration) == ("Leadership", 10, False)
    assert action.action_cost == "action" and action.resource_cost == 1
    assert action.ends_if_source_incapacitated and action.ends_if_source_dead
    assert (aura.radius_ft, aura.requires_hearing, aura.requires_source_sight) == (30, True, True)
    assert (aura.attack_dice_count, aura.attack_dice_size, aura.save_dice_count, aura.save_dice_size) == (1, 4, 1, 4)
    assert aura.stack_group == "leadership" and not aura.includes_source
    assert source.model_dump_json() == original
    template = _knight_template()
    assert next(r for r in template.resources if r.id == "leadership").max_uses == 1


def test_drifted_source_text_does_not_bind():
    source = _knight_source()
    drifted = source.model_copy(update={"source_actions": source.source_actions.replace("a d4", "a d6")})
    assert leadership_actions_2014(drifted) == []
    assert "source:extra-action" in basic_blockers_2014(drifted)


def test_leadership_live_lifecycle_range_sight_hearing_nonstack_and_incapacitation():
    knight = _member("knight", "monsters", _knight_template(), 1)
    knight2 = _member("knight2", "monsters", _knight_template(), 2)
    ally = _member("ally", "monsters", build_commoner(), 4)        # 15 ft
    far = _member("far", "monsters", build_commoner(), 10)        # 45 ft
    foe = _member("foe", "heroes", build_commoner(), 3)
    setup = _setup([foe], [knight, knight2, ally, far])
    [action] = knight.state.template.timed_self_buff_actions
    assert roll_bonus_aura_relevant(knight, action.friendly_roll_bonus_aura, setup)

    begin_turn(knight.state)
    resolve_timed_self_buff(1, 1, knight, action, setup=setup, turn_key="1:knight")
    begin_turn(knight2.state)
    resolve_timed_self_buff(2, 1, knight2, action, setup=setup, turn_key="1:knight2")
    sync_friendly_roll_bonus_auras(setup)
    kinds = lambda m: sorted(x.kind.value for x in m.state.active_modifiers if x.id.startswith("friendly-roll-bonus-aura:"))
    assert kinds(ally) == ["attack-roll-bonus-die", "saving-throw-bonus-die"]  # one die, not two
    assert kinds(far) == [] and kinds(foe) == []
    assert kinds(knight) == ["attack-roll-bonus-die", "saving-throw-bonus-die"]  # from the other Knight only
    boosted = apply_d20_bonus_dice(ally.state, ModifierKind.ATTACK_ROLL_BONUS_DIE,
                                   DiceRoll(notation="1d20", rolls=[10], modifier=0, total=10), _FixedDice())
    assert boosted.total == 13 and boosted.notation.endswith("1d4")
    assert next(r for r in knight.state.resources if r.id == "leadership").current_uses == 0
    begin_turn(knight.state)
    with pytest.raises(ValueError):
        resolve_timed_self_buff(3, 2, knight, action, setup=setup, turn_key="2:knight")

    ally.state.active_effect_ids.append("deafened")
    sync_friendly_roll_bonus_auras(setup)
    assert kinds(ally) == []
    ally.state.active_effect_ids.remove("deafened")
    for k in (knight, knight2):
        k.state.active_effect_ids.append("blinded")
    sync_friendly_roll_bonus_auras(setup)
    assert kinds(ally) == []  # source must see the recipient
    for k in (knight, knight2):
        k.state.active_effect_ids.remove("blinded")
        k.state.active_effect_ids.append("incapacitated")
    cleanup_disabled_source_effects(setup)
    sync_friendly_roll_bonus_auras(setup)
    assert kinds(ally) == [] and not any(e.source_effect_id == "leadership" for e in knight.state.timed_effects)
