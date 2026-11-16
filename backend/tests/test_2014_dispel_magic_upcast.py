"""2014 Dispel Magic upcasting must spend the actual slot and use its level."""
from __future__ import annotations

import logging

from app.combat.dice import FixedDiceProvider
from app.combat.effect_removal import choose_effect_removal_action, resolve_effect_removal
from app.combat.effect_removal_slot_choice import choose_effect_removal_slot
from app.combat.modifier_stack import add_modifier
from app.combat.state import build_combatant_state
from app.content.monsters import build_commoner
from app.content.paladin_devotion_2014_runtime import build_aurelia_brightshield_2014
from app.content.shared_effect_removal_spells_2014 import dispel_magic_2014
from app.domain.encounters import EncounterCombatant, EncounterSetup
from app.domain.models import ResourceDefinition
from app.domain.modifiers import CombatModifier, ModifierKind
from app.domain.spells import DefensiveSpellAction, SpellModifierEffect

logger = logging.getLogger(__name__)


def _member(name, side, template):
    return EncounterCombatant(
        combatant_id=name, side=side, position_ft=0,
        state=build_combatant_state(template),
    )


def _fixture(slots):
    try:
        base = build_commoner()
        caster = base.model_copy(update={
            "name": "Dispel Caster",
            "effect_removal_actions": [dispel_magic_2014("wisdom")],
            "ability_scores": build_aurelia_brightshield_2014(9).ability_scores,
            "resources": [
                ResourceDefinition(id=f"spell-slot-{level}", name=f"Slot {level}", max_uses=uses)
                for level, uses in slots.items()
            ],
        })
        enemy = base.model_copy(update={
            "name": "Ward Caster",
            "defensive_spell_actions": [
                DefensiveSpellAction(
                    id="higher-ward", name="Higher Ward", level=4,
                    range_ft=5, duration_minutes=1,
                    modifier_effects=[SpellModifierEffect(kind="armor-class", flat_bonus=2)],
                ),
            ],
        })
        actor = _member("actor", "heroes", caster)
        target = _member("target", "monsters", enemy)
        add_modifier(target.state, CombatModifier(
            id="target:higher-ward", source_id="target",
            source_effect_id="higher-ward", kind=ModifierKind.ARMOR_CLASS,
            flat_bonus=2, target_id="target",
        ))
        setup = EncounterSetup(
            heroes=[actor], monsters=[target],
            hero_total_levels=1, monster_total_cr="0", ruleset="2014",
        )
        return actor, target, setup
    except Exception:
        logger.exception("Could not prepare Dispel Magic upcast fixture")
        raise


def test_higher_slot_automatically_dispels_level_four_spell():
    try:
        actor, target, setup = _fixture({3: 1, 4: 1})
        picked = choose_effect_removal_action(actor, setup, "1:actor")
        assert picked is not None
        event = resolve_effect_removal(
            1, 1, actor, setup, *picked, FixedDiceProvider([1]), "1:actor",
        )
        assert event.removed_condition_ids == ["higher-ward"]
        assert event.ability_check_roll is None
        assert not target.state.active_modifiers
        assert next(x.current_uses for x in actor.state.resources if x.id == "spell-slot-3") == 1
        assert next(x.current_uses for x in actor.state.resources if x.id == "spell-slot-4") == 0
    except Exception:
        logger.exception("Upcast Dispel Magic did not spend the fourth-level slot")
        raise


def test_available_higher_slot_when_third_level_exhausted():
    try:
        actor, _, setup = _fixture({3: 0, 4: 1})
        action = actor.state.template.effect_removal_actions[0]
        assert choose_effect_removal_slot(actor, action, "1:actor", [4]) == ("spell-slot-4", 4)
        assert choose_effect_removal_action(actor, setup, "1:actor") is not None
    except Exception:
        logger.exception("Higher slot fallback was incorrectly rejected")
        raise


def test_third_level_slot_still_requires_check_for_level_four_spell():
    try:
        actor, target, setup = _fixture({3: 1})
        picked = choose_effect_removal_action(actor, setup, "1:actor")
        assert picked is not None
        event = resolve_effect_removal(
            1, 1, actor, setup, *picked, FixedDiceProvider([1]), "1:actor",
        )
        assert event.check_dc == 14
        assert event.check_succeeded is False
        assert target.state.active_modifiers
        assert actor.state.resources[0].current_uses == 0
    except Exception:
        logger.exception("Third-level Dispel Magic bypassed a required check")
        raise
