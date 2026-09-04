import logging

from app.combat.attacks import resolve_attack
from app.combat.conditions import attack_roll_condition_sources
from app.combat.dice import FixedDiceProvider
from app.combat.encounter_setup import build_encounter_setup
from app.domain.models import EncounterSelection, RollMode

logger = logging.getLogger(__name__)


def _setup():
    try:
        return build_encounter_setup(EncounterSelection(
            hero_ids=["karnok-stoneward-l1"],
            monster_ids=["srd-wolf"],
        ))
    except Exception:
        logger.exception("Failed to build missing-HP Advantage test encounter.")
        raise


def _enable_missing_hp_advantage(state) -> None:
    try:
        state.template.attack_roll_advantage_triggers.append("target_missing_hit_points")
    except Exception:
        logger.exception("Failed to enable target-missing-HP Advantage trigger.")
        raise


def test_missing_hp_trigger_only_applies_after_target_loses_hp() -> None:
    setup = _setup()
    hero, wolf = setup.heroes[0], setup.monsters[0]
    _enable_missing_hp_advantage(wolf.state)

    advantage, disadvantage = attack_roll_condition_sources(
        wolf.state, hero.state, 5, hero.combatant_id,
    )
    assert (advantage, disadvantage) == (0, 0)

    hero.state.current_hp -= 1
    advantage, disadvantage = attack_roll_condition_sources(
        wolf.state, hero.state, 5, hero.combatant_id,
    )
    assert (advantage, disadvantage) == (1, 0)


def test_missing_hp_advantage_cancels_attack_disadvantage_normally() -> None:
    setup = _setup()
    hero, wolf = setup.heroes[0], setup.monsters[0]
    _enable_missing_hp_advantage(wolf.state)
    hero.state.current_hp -= 1
    wolf.state.active_effect_ids.append("poisoned")

    advantage, disadvantage = attack_roll_condition_sources(
        wolf.state, hero.state, 5, hero.combatant_id,
    )
    assert (advantage, disadvantage) == (1, 1)

    event = resolve_attack(
        1, 1, wolf.state, hero.state, wolf.state.template.weapon_attack, 5,
        FixedDiceProvider([1]),
        actor_event_id=wolf.combatant_id,
        target_event_id=hero.combatant_id,
    )
    assert event.attack_roll is not None
    assert event.attack_roll.mode is RollMode.NORMAL
