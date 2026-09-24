from app.combat.effect_removal import resolve_effect_removal
from app.combat.effect_removal_targets import tracked_spell_effects
from app.combat.modifier_stack import add_modifier
from app.combat.state import build_combatant_state
from app.content.paladin_devotion_2014_profile import build_aurelia_brightshield_2014_profile
from app.content.paladin_devotion_2014_runtime import build_aurelia_brightshield_2014
from app.domain.encounters import EncounterCombatant, EncounterSetup
from app.domain.modifiers import CombatModifier, ModifierKind


class _NoDice:
    def d20(self):
        raise AssertionError("Cleansing Touch must not roll an ability check.")


def _member(combatant_id: str, level: int, position: int) -> EncounterCombatant:
    return EncounterCombatant(
        combatant_id=combatant_id,
        side="heroes",
        position_ft=position,
        state=build_combatant_state(build_aurelia_brightshield_2014(level)),
    )


def test_level_14_adds_three_cleansing_touch_uses_and_no_other_progression_change() -> None:
    level13 = build_aurelia_brightshield_2014(13)
    hero = build_aurelia_brightshield_2014(14)
    profile = build_aurelia_brightshield_2014_profile(14)

    resources = {item.id: item.max_uses for item in hero.resources}
    assert resources["cleansing-touch"] == 3
    assert {key: resources[key] for key in ("spell-slot-1", "spell-slot-2", "spell-slot-3", "spell-slot-4")} == {
        "spell-slot-1": 4,
        "spell-slot-2": 3,
        "spell-slot-3": 3,
        "spell-slot-4": 1,
    }
    assert hero.max_hp > level13.max_hp
    assert hero.ability_scores == level13.ability_scores

    cleansing = next(item for item in hero.effect_removal_actions if item.id == "cleansing-touch")
    assert cleansing.action_cost == "action"
    assert cleansing.range_ft == 5
    assert cleansing.target_mode == "self_or_ally"
    assert cleansing.auto_remove_max_level == 9
    assert cleansing.resource_id == "cleansing-touch"
    assert cleansing.resource_cost == 1
    assert cleansing.expends_spell_slot is False

    audits = {item.feature_id: item for item in profile.feature_audits}
    assert audits["cleansing-touch"].combat_relevant is True
    assert audits["cleansing-touch"].automated is True


def test_cleansing_touch_reuses_effect_removal_without_check_or_spell_slot() -> None:
    source = _member("source-paladin", 13, 0)
    remover = _member("aurelia", 14, 0)
    setup = EncounterSetup(heroes=[source, remover], monsters=[])

    remover.state.active_buff_effect_ids.append("death-ward")
    add_modifier(remover.state, CombatModifier(
        id="source-paladin:death-ward:aurelia:0",
        source_id=source.combatant_id,
        source_effect_id="death-ward",
        source_name="Death Ward",
        source_is_magical=True,
        kind=ModifierKind.ZERO_HP_REPLACEMENT,
        replacement_hp=1,
        prevents_instant_death=True,
    ))

    action = next(item for item in remover.state.template.effect_removal_actions if item.id == "cleansing-touch")
    candidates = tracked_spell_effects(remover, setup, action)
    assert len(candidates) == 1
    assert candidates[0].effect_id == "death-ward"

    slots_before = {
        item.id: item.current_uses
        for item in remover.state.resources
        if item.id.startswith("spell-slot-")
    }
    event = resolve_effect_removal(
        1, 1, remover, setup, action, candidates[0], _NoDice(), "1:aurelia",
    )

    cleansing = next(item for item in remover.state.resources if item.id == "cleansing-touch")
    assert cleansing.current_uses == 2
    assert remover.state.action_available is False
    assert not any(item.source_effect_id == "death-ward" for item in remover.state.active_modifiers)
    assert "death-ward" not in remover.state.active_buff_effect_ids
    assert event.ability_check_roll is None
    assert event.check_dc is None
    assert event.resource_remaining == 2
    assert {
        item.id: item.current_uses
        for item in remover.state.resources
        if item.id.startswith("spell-slot-")
    } == slots_before
