from app.combat.dice import FixedDiceProvider
from app.combat.encounter_combat_turn import resolve_combat_turn
from app.combat.encounter_setup import build_encounter_setup
from app.combat.resources import resource_state
from app.content.capability_registry import build_combatant_from_capabilities
from app.content.monster_catalog import load_monster_rows
from app.content.monster_source_audit import audit_monster_source
from app.domain.grid import GridPosition
from app.domain.models import EncounterSelection


def _fixture():
    setup = build_encounter_setup(EncounterSelection(
        hero_ids=["karnok-stoneward-l1"], monster_ids=["srd-hell-hound"],
    ))
    hero, hound = setup.heroes[0], setup.monsters[0]
    hero.state.position = GridPosition(x=0, y=6)
    hound.state.position = GridPosition(x=1, y=6)
    hero.state.initiative_total = 10
    hound.state.initiative_total = 20
    return setup, hero, hound


def test_hell_hound_binding_matches_srd_and_area_semantics() -> None:
    hound = build_combatant_from_capabilities("srd-hell-hound")
    row = next(row for row in load_monster_rows() if row["name"] == "Hell Hound")
    assert audit_monster_source(hound, row) == []
    assert hound.attack_action is not None
    assert [slot.attack_ids for slot in hound.attack_action.slots] == [
        ["hell-hound-bite"], ["hell-hound-bite"],
    ]
    breath = hound.saving_throw_actions[0]
    assert (breath.save_ability, breath.dc, breath.success_damage) == ("dexterity", 12, "half")
    assert breath.area is not None
    assert (breath.area.shape, breath.area.origin, breath.area.length_ft) == ("cone", "self", 15)
    assert (breath.damage_dice_count, breath.damage_dice_size, breath.damage_type) == (5, 6, "fire")
    assert breath.resource_id == "hell-hound-fire-breath-recharge"


def test_hell_hound_uses_breath_then_failed_recharge_falls_back_to_two_bites() -> None:
    setup, hero, hound = _fixture()
    resource = resource_state(hound.state, "hell-hound-fire-breath-recharge")
    assert resource.current_uses == 1

    first_turn, sequence = resolve_combat_turn(
        1, 1, hound, hero, setup, FixedDiceProvider([20, 1, 1, 1, 1, 1]),
    )
    saves = [event for event in first_turn if event.event_type == "saving_throw"]
    assert len(saves) == 1
    assert saves[0].feature_id == "hell-hound-fire-breath"
    assert saves[0].save_succeeded is True
    assert resource.current_uses == 0

    second_turn, _ = resolve_combat_turn(
        sequence, 2, hound, hero, setup,
        # Noncritical hits keep this fixture focused on Recharge fallback, not crit dice expansion.
        FixedDiceProvider([4, 19, 1, 1, 19, 1, 1]),
    )
    recharge = [event for event in second_turn if event.resource_roll is not None]
    assert len(recharge) == 1
    assert recharge[0].resource_roll.selected_roll == 4
    assert resource.current_uses == 0
    attacks = [event for event in second_turn if event.event_type == "attack"]
    assert [event.weapon_id for event in attacks] == ["hell-hound-bite", "hell-hound-bite"]
