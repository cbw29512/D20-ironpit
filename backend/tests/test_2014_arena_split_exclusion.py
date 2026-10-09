from __future__ import annotations

import pytest

from app.combat.damage_defenses import resolve_damage_amount
from app.combat.state import build_combatant_state
from app.content.capability_compiler import compile_combatant
from app.content.monster_arena_unavailable_reactions_2014 import arena_unavailable_reaction_names_2014
from app.content.monster_basic_candidates_2014 import basic_blockers_2014
from app.content.monster_definition_adapter_2014 import adapt_basic_monster_2014
from app.content.monster_source_2014 import load_monster_source_2014
from app.domain.models import DamageType
from scripts.browser_template_serializer import template_row


def source(monster_id):
    return next(monster for monster in load_monster_source_2014() if monster.id == monster_id)


def test_ochre_jelly_split_is_source_retained_not_executed_and_immunities_remain() -> None:
    monster = source("ochre-jelly")
    before = monster.model_dump_json()
    assert monster.reaction_names == ["Split"]
    assert "splits into two new jellies" in monster.source_reactions
    assert arena_unavailable_reaction_names_2014(monster) == {"Split"}
    assert set(monster.damage_immunities) == {"lightning", "slashing"}
    assert basic_blockers_2014(monster) == ()

    definition = adapt_basic_monster_2014(monster)
    template = compile_combatant(definition)
    state = build_combatant_state(template)
    assert set(template.damage_immunities) == {DamageType.LIGHTNING, DamageType.SLASHING}
    assert resolve_damage_amount(17, DamageType.LIGHTNING, state)[0] == 0
    assert resolve_damage_amount(17, DamageType.SLASHING, state)[0] == 0
    assert resolve_damage_amount(17, DamageType.FIRE, state)[0] == 17
    assert state.current_hp == monster.max_hp
    assert not template.damage_reaction_attack
    assert not template.recharge_rules
    browser = template_row(template)
    assert set(browser["damage_immunities"]) == {"lightning", "slashing"}
    assert not browser.get("damageReactionAttack")
    assert "Split" in browser["source_reaction_names"]
    assert monster.model_dump_json() == before


def test_split_applies_only_to_printed_creation_reactions() -> None:
    for name in ("ochre-jelly", "black-pudding"):
        monster = source(name)
        assert arena_unavailable_reaction_names_2014(monster) == {"Split"}

        without_text = monster.model_copy(update={"source_reactions": None})
        assert not arena_unavailable_reaction_names_2014(without_text)
        assert "source:reaction" in basic_blockers_2014(without_text)

        not_spawning = monster.model_copy(update={
            "source_reactions": monster.source_reactions.replace("splits into two new", "takes no damage"),
        })
        assert not arena_unavailable_reaction_names_2014(not_spawning)
        assert "source:reaction" in basic_blockers_2014(not_spawning)

        added = monster.model_copy(update={"reaction_names": ["Split", "Parry"]})
        assert arena_unavailable_reaction_names_2014(added) == {"Split"}
        assert "source:reaction" in basic_blockers_2014(added)


def test_ochre_jelly_does_not_unlock_unrelated_monsters() -> None:
    assert "source:reaction" not in basic_blockers_2014(source("ochre-jelly"))
    assert basic_blockers_2014(source("black-pudding"))
