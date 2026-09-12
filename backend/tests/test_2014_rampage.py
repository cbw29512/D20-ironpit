from app.combat.dice import FixedDiceProvider
from app.combat.rampage import resolve_rampage
from app.combat.state import build_combatant_state
from app.content.demo import build_demo_fighter
from app.content.monster_catalog_2014 import monster_by_id_2014
from app.domain.encounters import EncounterCombatant, EncounterSetup
from app.domain.events import BattleEvent
from app.domain.traits import CombatTrait


def _member(combatant_id, side, position, template):
    return EncounterCombatant(
        combatant_id=combatant_id, side=side, position_ft=position,
        state=build_combatant_state(template),
    )


def test_rampage_compiles_for_both_2014_monsters() -> None:
    try:
        for monster_id in ("giant-hyena", "gnoll"):
            template = monster_by_id_2014(monster_id)
            assert CombatTrait.RAMPAGE in template.combat_traits
            assert any(attack.id == "bite" for attack in [template.weapon_attack, *template.alternate_weapon_attacks])
    except Exception as exc:
        raise AssertionError("2014 Rampage monsters must compile with a Bite attack.") from exc


def test_rampage_uses_bonus_action_and_shared_bite_resolver() -> None:
    try:
        attacker = _member("hyena", "monsters", 10, monster_by_id_2014("giant-hyena"))
        fallen = _member("fallen", "heroes", 10, build_demo_fighter())
        target = _member("target", "heroes", 15, build_demo_fighter())
        fallen.state.current_hp = 0
        fallen.state.is_unconscious = True
        prior = [BattleEvent(
            sequence=1, round_number=1, event_type="attack", actor_id="hyena",
            actor_name=attacker.state.template.name, target_id="fallen", target_name=fallen.state.template.name,
            weapon_id="bite", hp_before=1, hp_after=0, hit=True, animation="melee",
            description="The hyena drops its target.",
        )]
        setup = EncounterSetup(
            heroes=[fallen, target], monsters=[attacker], hero_total_levels=2, monster_total_cr="1",
        )
        events, sequence = resolve_rampage(
            2, 1, attacker, setup, FixedDiceProvider([20, 3, 3, 3, 3]), prior, "1:hyena",
        )
        assert sequence == 3
        assert attacker.state.bonus_action_available is False
        assert len(events) == 1
        assert events[0].feature_id == "rampage"
        assert events[0].attack_name == "Bite"
        assert events[0].target_id == "target"
    except Exception as exc:
        raise AssertionError("Rampage must spend its bonus action and resolve Bite through shared combat.") from exc
