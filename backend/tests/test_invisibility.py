from app.combat.conditions import attack_roll_condition_sources
from app.combat.invisibility import end_attack_invisibility, resolve_invisibility_action
from app.combat.state import begin_turn, build_combatant_state
from app.content.monster_catalog_2014 import load_catalog_2014, monster_by_id_2014, unsupported_mechanics_2014
from app.content.monster_catalog_2014_invisibility import invisibility_action_2014
from app.domain.encounters import EncounterCombatant, EncounterSetup


def _source(monster_id: str):
    try:
        return next(item for item in load_catalog_2014() if item.id == monster_id)
    except StopIteration as exc:
        raise AssertionError(f"Missing 2014 source monster {monster_id}.") from exc


def _member(combatant_id: str, side: str, template):
    return EncounterCombatant(
        combatant_id=combatant_id,
        side=side,
        position_ft=0,
        state=build_combatant_state(template),
    )


def test_permanent_invisibility_starts_active_and_changes_attack_modes() -> None:
    try:
        stalker = build_combatant_state(monster_by_id_2014("invisible-stalker"))
        goblin = build_combatant_state(monster_by_id_2014("goblin"))
        assert "invisible" in stalker.active_effect_ids
        assert attack_roll_condition_sources(stalker, goblin, 5) == (1, 0)
        assert attack_roll_condition_sources(goblin, stalker, 5) == (0, 1)
        assert not end_attack_invisibility(stalker, [stalker, goblin])
        assert "invisible" in stalker.active_effect_ids
    except Exception as exc:
        raise AssertionError("Permanent invisibility combat rules failed.") from exc


def test_action_invisibility_concentrates_and_ends_after_attack() -> None:
    try:
        profile = invisibility_action_2014(_source("imp"))
        assert profile is not None
        actor_template = monster_by_id_2014("goblin").model_copy(
            update={"invisibility_action": profile, "starts_invisible": False}
        )
        actor = _member("monster-1", "monsters", actor_template)
        target = _member("hero-1", "heroes", monster_by_id_2014("goblin"))
        setup = EncounterSetup(
            heroes=[target], monsters=[actor], hero_total_levels=1, monster_total_cr="1/4"
        )
        begin_turn(actor.state)
        event = resolve_invisibility_action(1, 1, actor, setup)
        assert event.applied_condition_ids == ["invisible"]
        assert actor.state.concentration is not None
        assert actor.state.concentration.effect_id == "invisibility"
        assert attack_roll_condition_sources(actor.state, target.state, 5) == (1, 0)
        assert end_attack_invisibility(actor.state, [actor.state, target.state])
        assert "invisible" not in actor.state.active_effect_ids
        assert actor.state.concentration is None
    except Exception as exc:
        raise AssertionError("Action invisibility lifecycle failed.") from exc


def test_2014_invisibility_names_are_no_longer_blockers() -> None:
    try:
        assert "trait:Invisibility" not in unsupported_mechanics_2014(_source("invisible-stalker"))
        for monster_id in ("imp", "quasit", "sprite", "will-o-wisp"):
            assert "action:Invisibility" not in unsupported_mechanics_2014(_source(monster_id))
    except Exception as exc:
        raise AssertionError("2014 invisibility blockers were not cleared universally.") from exc
