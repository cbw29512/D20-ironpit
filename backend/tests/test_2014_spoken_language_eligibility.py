"""Pinned SRD language proof and shared save-spell target eligibility."""
from __future__ import annotations

import logging

import pytest

from app.combat.spell_policy_targeting import legal_single_spell_targets
from app.combat.spoken_language_eligibility import spoken_language_understood
from app.combat.state import build_combatant_state
from app.content.audited_fighter import build_karnok_stoneward
from app.content.monster_languages_2014 import monster_languages_2014
from app.content.monster_source_2014 import load_monster_source_2014
from app.domain.encounters import EncounterCombatant, EncounterSetup
from app.domain.languages import LanguageProfile
from app.domain.spells import SpellSaveAction

logger = logging.getLogger(__name__)


def test_pinned_2014_languages_are_preserved_without_guessing_undecided_choices() -> None:
    try:
        rows = load_monster_source_2014()
        assert len(rows) == 327
        assert all(isinstance(row.languages, str) and row.languages for row in rows)
        cards = {row.id: row for row in rows}
        originals = {key: cards[key].model_dump_json() for key in (
            "androsphinx", "guardian-naga", "cult-fanatic", "mummy-lord",
        )}
        assert monster_languages_2014(cards["androsphinx"].languages).spoken == ("common", "sphinx")
        assert monster_languages_2014(cards["guardian-naga"].languages).spoken == ("celestial", "common")
        for key in ("cult-fanatic", "mummy-lord"):
            profile = monster_languages_2014(cards[key].languages)
            assert profile.unspecified and not profile.spoken
            assert not profile.understood
        for key, before in originals.items():
            assert cards[key].model_dump_json() == before
        assert monster_languages_2014("--") == LanguageProfile(unspecified=False)
        shield = monster_languages_2014(cards["shield-guardian"].languages)
        assert shield.understands_all and not shield.speaks_all
        stalker = monster_languages_2014(cards["invisible-stalker"].languages)
        assert "auran" in stalker.spoken
        assert "common" in stalker.understood and "common" not in stalker.spoken
        assert all(isinstance(monster_languages_2014(row.languages), LanguageProfile) for row in rows)
    except Exception:
        logger.exception("Pinned 2014 language source proof failed.")
        raise


@pytest.mark.parametrize("speak,understand,expected", [
    (["common"], ["common"], True),
    (["common"], ["draconic"], False),
    (["aquan"], ["ignan"], True),
    (["auran"], ["primordial"], True),
    ([], ["common"], False),
    (["sphinx"], [], False),
])
def test_spoken_language_matches_only_confirmed_comprehension(speak, understand, expected) -> None:
    try:
        caster = LanguageProfile(spoken=tuple(speak), understood=tuple(speak), unspecified=False)
        listener = LanguageProfile(understood=tuple(understand), unspecified=False)
        assert spoken_language_understood(caster, listener) is expected
        assert not spoken_language_understood(LanguageProfile(), listener)
        assert not spoken_language_understood(caster, LanguageProfile())
    except Exception:
        logger.exception("Shared source-backed language equivalence failed.")
        raise


def test_spell_eligibility_filters_targets_before_resource_or_save_roll() -> None:
    try:
        template = build_karnok_stoneward()
        speaker = LanguageProfile(spoken=("common",), understood=("common",), unspecified=False)
        listener = LanguageProfile(understood=("common",), unspecified=False)
        caster = EncounterCombatant(
            combatant_id="caster", side="monsters", position_ft=10,
            state=build_combatant_state(template.model_copy(update={"language_profile": speaker})),
        )
        victim = EncounterCombatant(
            combatant_id="target", side="heroes", position_ft=5,
            state=build_combatant_state(template.model_copy(update={"language_profile": listener})),
        )
        setup = EncounterSetup(
            heroes=[victim], monsters=[caster], hero_total_levels=1, monster_total_cr="1",
        )
        command_like = SpellSaveAction(
            id="renamed-compulsion", name="Renamed Compulsion", level=1,
            range_ft=60, save_ability="wisdom", dc=11,
            requires_shared_spoken_language=True,
            excluded_target_creature_types=["undead"],
            requires_target_sight=True,
        )
        assert legal_single_spell_targets(caster, setup, command_like) == [victim]
        victim.state.template = template.model_copy(update={
            "language_profile": LanguageProfile(understood=("draconic",), unspecified=False),
        })
        assert legal_single_spell_targets(caster, setup, command_like) == []
        victim.state.template = template.model_copy(update={"language_profile": LanguageProfile()})
        assert legal_single_spell_targets(caster, setup, command_like) == []
        victim.state.template = template.model_copy(update={
            "language_profile": listener, "creature_type": "undead",
        })
        assert legal_single_spell_targets(caster, setup, command_like) == []
    except Exception:
        logger.exception("Generic spoken-language spell target legality regressed.")
        raise
