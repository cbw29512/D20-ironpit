"""Source-verified spoken language and generic eligibility, no caster-name dispatch."""
from __future__ import annotations

import logging
from types import SimpleNamespace

import pytest

from app.combat.language_eligibility import target_understands_caster_language
from app.content.monster_languages_2014 import source_languages_2014
from app.content.monster_source_2014 import load_monster_source_2014
from app.content.monster_definition_adapter_2014 import adapt_basic_monster_2014
from app.content.capability_compiler import compile_combatant
from app.domain.spells import SpellSaveAction

logger = logging.getLogger(__name__)


def _card(monster_id: str):
    return next(x for x in load_monster_source_2014() if x.id == monster_id)


def test_2014_language_source_preserves_known_unknown_and_speech_distinction() -> None:
    try:
        assert len(load_monster_source_2014()) == 327
        assert source_languages_2014(_card("cult-fanatic")) == (["common"], ["common"])
        assert source_languages_2014(_card("goblin")) == (
            ["common", "goblin"], ["common", "goblin"],
        )
        assert source_languages_2014(_card("giant-vulture")) == ([], ["common"])
        assert source_languages_2014(_card("mummy-lord")) == ([], [])
        assert source_languages_2014(_card("couatl")) == (["all"], ["all"])
        assert source_languages_2014(_card("animated-armor")) == ([], [])

        cult = _card("cult-fanatic")
        before = cult.model_dump_json()
        template = compile_combatant(adapt_basic_monster_2014(cult))
        assert template.spoken_languages == ["common"]
        assert template.understood_languages == ["common"]
        assert cult.model_dump_json() == before
    except Exception:
        logger.exception("2014 source language compatibility fixtures failed.")
        raise


@pytest.mark.parametrize(
    ("spoken", "understood", "result"),
    [
        (["common"], ["common"], True),
        (["common"], ["goblin"], False),
        ([], ["common"], False),
        (["goblin"], [], False),
        (["all"], ["draconic"], True),
        (["draconic"], ["all"], True),
        ([], ["all"], False),
        (["common"], [], False),
    ],
)
def test_shared_spoken_language_never_invents_eligibility(spoken, understood, result) -> None:
    try:
        caster = SimpleNamespace(id="renamed-caster", spoken_languages=spoken)
        target = SimpleNamespace(id="renamed-target", understood_languages=understood)
        assert target_understands_caster_language(caster, target) is result
    except Exception:
        logger.exception("Shared language target eligibility failed.")
        raise


def test_spoken_language_spell_option_is_source_data_not_name_logic() -> None:
    try:
        options = dict(
            level=1, action_cost="action", range_ft=60, save_ability="wisdom",
            dc=11, requires_shared_spoken_language=True,
            requires_target_hearing=True,
            requires_target_sight=True,
            excluded_target_creature_types=["undead"],
        )
        for label in ["Command", "Renamed Command"]:
            action = SpellSaveAction(
                id=label.casefold().replace(" ", "-"), name=label, **options,
            )
            assert action.requires_shared_spoken_language
            assert action.excluded_target_creature_types == ["undead"]
    except Exception:
        logger.exception("Spoken-language spell name should remain metadata.")
        raise
