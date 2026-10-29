from __future__ import annotations

from app.combat.attacks import resolve_attack
from app.combat.dice import FixedDiceProvider
from app.combat.state import build_combatant_state
from app.content.capability_compiler import compile_combatant
from app.content.monster_basic_candidates_2014 import unsupported_traits_2014
from app.content.monster_definition_adapter_2014 import adapt_monster_mechanics_2014
from app.content.monster_opening_initiative_2014 import (
    opening_initiative_advantage_source_2014,
    opening_initiative_damage_source_2014,
)
from app.content.monster_source_2014 import load_monster_source_2014
from app.content.monsters import build_commoner
from app.domain.models import RollMode


def _source():
    return next(row for row in load_monster_source_2014() if row.id == "doppelganger")


def _combatants():
    source = _source()
    template = compile_combatant(adapt_monster_mechanics_2014(source))
    attacker = build_combatant_state(template)
    attacker.turns_started = 1
    victim = build_combatant_state(build_commoner().model_copy(update={"max_hp": 100}))
    return attacker, victim, template.weapon_attack


def test_source_semantics_bind_ambusher_and_surprise_attack_without_identity_routing() -> None:
    source = _source()
    before = source.model_dump_json()
    assert opening_initiative_advantage_source_2014(source) == "Ambusher"
    assert opening_initiative_damage_source_2014(source) == "Surprise Attack"
    assert unsupported_traits_2014(source) == ("Shapechanger",)
    template = compile_combatant(adapt_monster_mechanics_2014(source))
    slam = template.weapon_attack
    assert [(row.trigger, row.source_name, row.dice_count, row.dice_size)
            for row in slam.conditional_damage] == [
        ("round1_initiative_lead", "Surprise Attack", 3, 6),
    ]
    assert [row.trigger for row in slam.conditional_attack_advantage] == [
        "round1_initiative_lead",
    ]
    assert source.model_dump_json() == before

    renamed = source.model_copy(update={
        "trait_names": ["Shapechanger", "Opening Hunter", "Opening Strike"],
        "source_traits": (source.source_traits or "")
        .replace("Ambusher.", "Opening Hunter.")
        .replace("Surprise Attack.", "Opening Strike."),
    })
    assert opening_initiative_advantage_source_2014(renamed) == "Opening Hunter"
    assert opening_initiative_damage_source_2014(renamed) == "Opening Strike"


def test_opening_lead_grants_advantage_and_card_declared_damage_once() -> None:
    attacker, victim, attack = _combatants()
    hit = resolve_attack(
        1, 1, attacker, victim, attack, 5,
        FixedDiceProvider([3, 18, 2, 4, 5, 6]),
        spend_action=False, turn_key="1:doppelganger",
    )
    assert hit.hit
    assert hit.attack_roll.mode is RollMode.ADVANTAGE
    assert hit.attack_roll.selected_roll == 18
    surprise = next(row for row in hit.damage_components if row.source == "Surprise Attack")
    assert surprise.rolls == [4, 5, 6]

    later = resolve_attack(
        2, 1, attacker, victim, attack, 5,
        FixedDiceProvider([18, 17, 2]), spend_action=False, turn_key="1:doppelganger",
    )
    assert later.attack_roll.mode is RollMode.ADVANTAGE
    assert all(row.source != "Surprise Attack" for row in later.damage_components)


def test_opening_modifiers_do_not_apply_without_initiative_lead() -> None:
    attacker, victim, attack = _combatants()
    victim.turns_started = 1
    hit = resolve_attack(
        1, 1, attacker, victim, attack, 5,
        FixedDiceProvider([18, 2]), spend_action=False, turn_key="1:doppelganger",
    )
    assert hit.attack_roll.mode is RollMode.NORMAL
    assert all(row.source != "Surprise Attack" for row in hit.damage_components)
