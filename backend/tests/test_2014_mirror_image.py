from __future__ import annotations

from app.combat.attacks import resolve_attack
from app.combat.dice import FixedDiceProvider
from app.combat.state import build_combatant_state
from app.combat.timed_self_buffs import resolve_timed_self_buff
from app.content.monster_innate_support_2014 import innate_timed_self_buffs_2014
from app.content.monster_prepared_spells_2014 import prepared_timed_self_buffs_2014
from app.content.monster_source_2014 import load_monster_source_2014
from app.content.monsters import build_commoner
from app.content.shared_mirror_image_2014 import mirror_image_2014
from app.domain.encounters import EncounterCombatant
from app.domain.character_builds import AbilityScores


def _cards():
    cards = load_monster_source_2014()
    assert len(cards) == 327
    return cards


def test_semantic_327_card_scan_binds_all_printed_2014_mirror_image_spells():
    cards = _cards()
    applicable = []
    for card in cards:
        prepared = (card.spellcasting or {}).get("spells", []) if card.spellcasting else []
        innate = (card.innate_spellcasting or {}).get("spells", []) if card.innate_spellcasting else []
        if any(row.get("id") == "mirror-image" for row in [*prepared, *innate]):
            applicable.append(card)
    assert [(card.id, card.name) for card in applicable] == [
        ("archmage", "Archmage"), ("lamia", "Lamia"), ("lich", "Lich"),
    ]

    archmage, lamia, lich = applicable
    assert prepared_timed_self_buffs_2014(archmage) == [mirror_image_2014("spell-slot-2")]
    assert innate_timed_self_buffs_2014(lamia) == [mirror_image_2014("mirror-image")]
    assert prepared_timed_self_buffs_2014(lich) == [mirror_image_2014("spell-slot-2")]
    assert not any(
        action.id == "mirror-image"
        for card in cards if card not in applicable
        for action in [*prepared_timed_self_buffs_2014(card), *innate_timed_self_buffs_2014(card)]
    )

    # Identity is never part of the semantic binding proof.
    renamed = lamia.model_copy(update={"id": "renamed-source", "name": "Unrelated Caster"})
    assert innate_timed_self_buffs_2014(renamed) == [mirror_image_2014("mirror-image")]

    # Cloaker Phantasms is deliberately distinct: it also affects saves and
    # harmful spells and therefore cannot silently reuse Mirror Image.
    cloaker = next(card for card in cards if card.id == "cloaker")
    assert "Phantasms" in cloaker.source_actions
    assert innate_timed_self_buffs_2014(cloaker) == []
    assert prepared_timed_self_buffs_2014(cloaker) == []


def _member(combatant_id: str, *, mirror: bool = False, dexterity: int = 10):
    template = build_commoner().model_copy(deep=True)
    update = {
        "id": combatant_id,
        "name": combatant_id.title(),
        "ability_scores": AbilityScores(
            strength=10, dexterity=dexterity, constitution=10,
            intelligence=10, wisdom=10, charisma=10,
        ),
    }
    if mirror:
        update["timed_self_buff_actions"] = [mirror_image_2014(None)]
    template = template.model_copy(update=update)
    return EncounterCombatant(
        combatant_id=combatant_id, side="monsters" if mirror else "heroes",
        position_ft=0 if mirror else 5, state=build_combatant_state(template),
    )


def test_shared_attack_runtime_redirects_destroys_and_resets_fight_state():
    attacker = _member("attacker")
    defender = _member("defender", mirror=True, dexterity=14)
    action = defender.state.template.timed_self_buff_actions[0]
    resolve_timed_self_buff(1, 1, defender, action, affected_states=[defender.state])
    effect, = defender.state.timed_effects
    assert effect.illusory_duplicates_remaining == 3
    assert defender.state.template.ability_scores.dexterity == 14

    event = resolve_attack(
        2, 1, attacker.state, defender.state, attacker.state.template.weapon_attack,
        5, FixedDiceProvider([6, 10]),
        actor_event_id=attacker.combatant_id, target_event_id=defender.combatant_id,
        affected_states=[attacker.state, defender.state],
    )
    assert event.feature_id == "mirror-image"
    assert event.feature_roll.total == 6
    assert event.target_ac == 12
    assert event.hit is True
    assert event.hp_before == event.hp_after == defender.state.current_hp
    assert effect.illusory_duplicates_remaining == 2

    attacker.state.action_available = True
    miss = resolve_attack(
        3, 1, attacker.state, defender.state, attacker.state.template.weapon_attack,
        5, FixedDiceProvider([8, 1]),
        actor_event_id=attacker.combatant_id, target_event_id=defender.combatant_id,
        affected_states=[attacker.state, defender.state],
    )
    assert miss.feature_id == "mirror-image"
    assert miss.hit is False
    assert effect.illusory_duplicates_remaining == 2

    fresh = _member("defender-next-fight", mirror=True, dexterity=14)
    assert fresh.state.timed_effects == []
    assert fresh.state.template.ability_scores.dexterity == 14


def test_duplicate_defense_is_bypassed_by_blindsight_and_nonvisual_attacks_are_untouched():
    attacker = _member("attacker")
    defender = _member("defender", mirror=True, dexterity=14)
    resolve_timed_self_buff(
        1, 1, defender, defender.state.template.timed_self_buff_actions[0],
        affected_states=[defender.state],
    )
    attacker.state.template = attacker.state.template.model_copy(update={"blindsight_ft": 10})
    before = defender.state.current_hp
    event = resolve_attack(
        2, 1, attacker.state, defender.state, attacker.state.template.weapon_attack,
        5, FixedDiceProvider([15, 4]),
        actor_event_id=attacker.combatant_id, target_event_id=defender.combatant_id,
        affected_states=[attacker.state, defender.state],
    )
    assert event.feature_id != "mirror-image"
    assert event.hp_after < before
    assert defender.state.timed_effects[0].illusory_duplicates_remaining == 3
