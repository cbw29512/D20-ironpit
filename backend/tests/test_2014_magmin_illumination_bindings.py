"""Source-backed Magmin illumination proof; never hide missing Touch mechanics."""
from app.content.monster_source_2014 import load_monster_source_2014
from app.content.monster_basic_candidates_2014 import basic_blockers_2014, unsupported_traits_2014
from app.content.monster_arena_neutral_traits_2014 import verified_arena_inert_trait_2014

def test_magmin_printed_illumination_is_inert_but_attack_remains_blocked():
    source = next(m for m in load_monster_source_2014() if m.id == "magmin")
    before = source.model_dump_json()
    assert verified_arena_inert_trait_2014(source, "Ignited Illumination")
    assert "Ignited Illumination" not in unsupported_traits_2014(source)
    assert "attack:incomplete" in basic_blockers_2014(source)
    assert source.model_dump_json() == before

def test_magmin_illumination_requires_unchanged_printed_source():
    source = next(m for m in load_monster_source_2014() if m.id == "magmin")
    altered = source.model_copy(update={"source_traits": (source.source_traits or "").replace(
        "<strong>Ignited Illumination.</strong>", "<strong>Missing Illumination.</strong>")})
    assert not verified_arena_inert_trait_2014(altered, "Ignited Illumination")


def test_generic_end_turn_burn_ticks_once_without_expiring_or_stacking():
    from app.combat.end_of_turn_timed_damage import resolve_end_of_turn_timed_damage
    from app.combat.state import build_combatant_state
    from app.content.demo import build_demo_fighter
    from app.domain.encounters import EncounterCombatant, EncounterSetup
    from app.domain.timed_effects import TimedEffect
    from app.domain.combatants import DamageType

    class Dice:
        def roll(self, size):
            assert size == 6
            return 4

    fighter = build_demo_fighter()
    target = EncounterCombatant(combatant_id="target", side="heroes", position_ft=0,
                                 state=build_combatant_state(fighter))
    enemy = EncounterCombatant(combatant_id="enemy", side="monsters", position_ft=5,
                                state=build_combatant_state(fighter))
    setup = EncounterSetup(heroes=[target], monsters=[enemy],
                           hero_total_levels=1, monster_total_cr="1", ruleset="2014")
    burn = TimedEffect(effect_id="burning", source_id="enemy",
                       source_effect_id="touch", expires_at_start_of_source_turn=False,
                       end_of_turn_dice_count=1, end_of_turn_dice_size=6,
                       end_of_turn_damage_type=DamageType.FIRE)
    target.state.timed_effects.append(burn)
    initial_hp = target.state.current_hp
    events, seq = resolve_end_of_turn_timed_damage(1, 1, target, setup, Dice())
    assert (len(events), seq, target.state.current_hp) == (1, 2, initial_hp - 4)
    assert target.state.timed_effects == [burn]
    events, seq = resolve_end_of_turn_timed_damage(seq, 2, target, setup, Dice())
    assert (len(events), seq, target.state.current_hp) == (1, 3, initial_hp - 8)
    assert len(target.state.timed_effects) == 1
