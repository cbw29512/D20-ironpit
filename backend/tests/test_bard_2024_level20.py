from __future__ import annotations

from app.combat.dice import FixedDiceProvider
from app.combat.group_healing import resolve_group_healing
from app.combat.hp_threshold_instant_death import resolve_group_hp_threshold_instant_death
from app.combat.state import build_combatant_state
from app.content.audited_bard import build_lyra_silverstring_level
from app.content.audited_bard_profile import build_lyra_silverstring_profile
from app.content.canonical_spell_policy import canonical_spell_package
from app.domain.encounters import EncounterCombatant, EncounterSetup


def _member(level: int, combatant_id: str, side: str, position_ft: int) -> EncounterCombatant:
    return EncounterCombatant(
        combatant_id=combatant_id,
        side=side,
        position_ft=position_ft,
        state=build_combatant_state(build_lyra_silverstring_level(level)),
    )


def test_2024_bard_level_twenty_raw_progression_and_spell_package() -> None:
    profile = build_lyra_silverstring_profile(20)
    hero = build_lyra_silverstring_level(20)

    assert hero.max_hp == 103
    resources = {item.id: item.max_uses for item in hero.resources}
    assert resources["spell-slot-6"] == 2
    assert resources["spell-slot-7"] == 2
    assert resources["spell-slot-8"] == 1
    assert resources["spell-slot-9"] == 1

    audit = next(item for item in profile.feature_audits if item.feature_id == "words-of-creation")
    assert audit.automated is True

    package = canonical_spell_package("bard", 20, "2024", 5)
    assert package is not None
    assert len(package.spells) == 22
    assert [item.id for item in package.spells[-2:]] == ["circle-of-death", "legend-lore"]
    assert [item.id for item in package.always_prepared_spells] == [
        "bless",
        "guiding-bolt",
        "power-word-kill",
        "power-word-heal",
    ]

    circle = next(item for item in hero.spell_save_actions if item.id == "circle-of-death")
    assert circle.dc == 19
    assert circle.area is not None
    assert (circle.area.shape, circle.area.origin, circle.area.radius_ft) == ("radius", "point", 60)
    assert (
        circle.damage_dice_count,
        circle.damage_dice_size,
        circle.damage_type,
        circle.success_damage,
        circle.upcast_dice_per_level,
    ) == (8, 8, "necrotic", "half", 2)


def test_words_of_creation_power_word_heal_is_one_spell_for_two_linked_targets() -> None:
    source = _member(20, "lyra", "heroes", 0)
    first = _member(1, "ally-one", "heroes", 10)
    second = _member(1, "ally-two", "heroes", 20)
    enemy = _member(1, "enemy", "monsters", 50)
    setup = EncounterSetup(
        heroes=[source, first, second],
        monsters=[enemy],
        hero_total_levels=22,
        monster_total_cr="1",
    )
    first.state.current_hp = 1
    second.state.current_hp = 2
    first.state.active_effect_ids.extend(["charmed", "prone"])
    second.state.active_effect_ids.append("poisoned")

    action = next(item for item in source.state.template.healing_actions if item.id == "power-word-heal")
    assert (action.max_targets, action.secondary_target_within_ft) == (2, 10)

    events, sequence = resolve_group_healing(
        1, 1, source, [first, second], action, FixedDiceProvider([1]), "lyra-turn", setup=setup,
    )

    assert sequence == 3
    assert source.state.action_available is False
    assert next(item for item in source.state.resources if item.id == "spell-slot-9").current_uses == 0
    assert first.state.current_hp == first.state.template.max_hp
    assert second.state.current_hp == second.state.template.max_hp
    assert "charmed" not in first.state.active_effect_ids
    assert "poisoned" not in second.state.active_effect_ids
    assert "prone" not in first.state.active_effect_ids
    assert first.state.reaction_available is False
    assert events[0].removed_condition_ids == ["charmed", "prone"]
    assert events[1].removed_condition_ids == ["poisoned"]


def test_words_of_creation_power_word_kill_spends_one_slot_for_two_linked_targets() -> None:
    source = _member(20, "lyra", "heroes", 0)
    first = _member(20, "enemy-one", "monsters", 30)
    second = _member(20, "enemy-two", "monsters", 40)
    setup = EncounterSetup(
        heroes=[source],
        monsters=[first, second],
        hero_total_levels=20,
        monster_total_cr="40",
    )
    first.state.current_hp = 100
    second.state.current_hp = 150

    action = source.state.template.hp_threshold_instant_death_actions[0]
    assert action.id == "power-word-kill"
    assert (action.max_targets, action.secondary_target_within_ft) == (2, 10)

    events = resolve_group_hp_threshold_instant_death(
        1, 1, source, [first, second], action, setup, dice=FixedDiceProvider([1] * 12),
    )

    assert len(events) == 2
    assert source.state.action_available is False
    assert next(item for item in source.state.resources if item.id == "spell-slot-9").current_uses == 0
    assert first.state.is_dead is True
    assert second.state.current_hp == 138


def test_words_of_creation_rejects_second_target_outside_ten_feet() -> None:
    source = _member(20, "lyra", "heroes", 0)
    first = _member(1, "ally-one", "heroes", 10)
    second = _member(1, "ally-two", "heroes", 25)
    enemy = _member(1, "enemy", "monsters", 50)
    setup = EncounterSetup(
        heroes=[source, first, second],
        monsters=[enemy],
        hero_total_levels=22,
        monster_total_cr="1",
    )
    first.state.current_hp = 1
    second.state.current_hp = 1
    action = next(item for item in source.state.template.healing_actions if item.id == "power-word-heal")

    try:
        resolve_group_healing(
            1, 1, source, [first, second], action, FixedDiceProvider([]), "lyra-turn", setup=setup,
        )
    except ValueError as exc:
        assert "linked-target distance" in str(exc)
    else:
        raise AssertionError("Words of Creation accepted a second target more than 10 feet from the first.")
