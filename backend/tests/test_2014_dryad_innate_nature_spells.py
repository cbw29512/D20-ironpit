"""2014 Dryad's six printed innate spells retain identity and combat state."""
from __future__ import annotations

import logging

from app.combat.modifier_stack import effective_armor_class
from app.combat.state import build_combatant_state
from app.combat.timed_condition_lifecycle import remove_effect_group
from app.combat.timed_self_buffs import resolve_timed_self_buff
from app.content.capability_compiler import compile_combatant
from app.content.monster_basic_candidates_2014 import basic_blockers_2014
from app.content.monster_definition_adapter_2014 import adapt_monster_mechanics_2014
from app.content.monster_innate_ai_exclusions_2014 import (
    source_proven_arena_ai_excluded_innate_spells_2014,
)
from app.content.monster_innate_nature_spells_2014 import (
    innate_nature_barkskin_2014,
    source_proven_goodberry_ai_exclusion_2014,
    source_proves_innate_nature_2014,
)
from app.content.monster_innate_support_2014 import (
    innate_spell_resources_2014, innate_timed_self_buffs_2014,
    supports_innate_spellcasting_2014,
)
from app.content.monster_source_2014 import load_monster_source_2014
from app.domain.encounters import EncounterCombatant

logger = logging.getLogger(__name__)


def _source():
    try:
        return next(card for card in load_monster_source_2014() if card.id == "dryad")
    except Exception:
        logger.exception("2014 Dryad source catalog is missing.")
        raise


def test_six_innate_spells_bind_without_undocumented_actions() -> None:
    try:
        source = _source()
        original = source.model_dump_json()
        assert source_proves_innate_nature_2014(source)
        assert supports_innate_spellcasting_2014(source)
        assert source_proven_goodberry_ai_exclusion_2014(source) == {"goodberry"}
        assert "goodberry" in source_proven_arena_ai_excluded_innate_spells_2014(source)
        buffs = {action.id: action for action in innate_timed_self_buffs_2014(source)}
        assert {"shillelagh", "barkskin"} <= buffs.keys()
        assert buffs["barkskin"].duration_rounds == 600
        assert buffs["barkskin"].concentration
        assert buffs["barkskin"].action_cost == "action"
        assert buffs["barkskin"].modifier_effects[0].kind == "armor-class-minimum"
        assert buffs["barkskin"].modifier_effects[0].minimum_value == 16
        resources = {item.id: item.max_uses for item in innate_spell_resources_2014(source)}
        assert resources["barkskin"] == 1
        assert resources["shillelagh"] == 1
        assert resources["entangle"] == 3
        assert "goodberry" not in resources, "AI-excluded berries must not create a usable cast"
        assert source.model_dump_json() == original
        # Once the separately source-proven Fey Charm binding is present,
        # all six innate spells and its action must be admitted together.
        assert basic_blockers_2014(source) == ()
    except Exception:
        logger.exception("The six 2014 innate nature spell dispositions regressed.")
        raise


def test_source_renaming_and_mutation_fail_closed() -> None:
    try:
        source = _source()
        renamed = source.model_copy(update={"id": "renamed-fey", "name": "Renamed Fey"})
        assert source_proves_innate_nature_2014(renamed)
        assert innate_nature_barkskin_2014(renamed) == innate_nature_barkskin_2014(source)
        changed = source.model_copy(deep=True)
        changed.innate_spellcasting["spells"][3]["uses_per_day"] = 2
        assert not source_proves_innate_nature_2014(changed)
        assert innate_nature_barkskin_2014(changed) is None
        assert source_proven_goodberry_ai_exclusion_2014(changed) == frozenset()
    except Exception:
        logger.exception("Innate nature spell source proof did not fail closed.")
        raise


def test_barkskin_is_not_free_ac_and_expires_via_generic_timed_lifecycle() -> None:
    try:
        source = _source()
        template = compile_combatant(adapt_monster_mechanics_2014(source))
        state = build_combatant_state(template)
        caster = EncounterCombatant(
            combatant_id="dryad", side="monsters", position_ft=5, state=state,
        )
        action = next(a for a in template.timed_self_buff_actions if a.id == "barkskin")
        assert effective_armor_class(state) == 11
        event = resolve_timed_self_buff(1, 1, caster, action, spend_action_cost=True)
        assert event.feature_id == "barkskin"
        assert effective_armor_class(state) == 16
        assert state.concentration is not None
        assert next(item for item in state.resources if item.id == "barkskin").current_uses == 0
        effect = next(x for x in state.timed_effects if x.source_effect_id == "barkskin")
        remove_effect_group(state, effect)
        assert effective_armor_class(state) == 11
    except Exception:
        logger.exception("Universal timed Barkskin did not manage AC/resource/Concentration.")
        raise
