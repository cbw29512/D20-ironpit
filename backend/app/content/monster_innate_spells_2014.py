from __future__ import annotations

import logging

from app.content.monster_source_2014 import SourceMonster2014
from app.domain.debuffs import DebuffCounter
from app.domain.save_effects import FailedSaveTimedEffect
from app.domain.spell_modifiers import SpellModifierEffect
from app.domain.spells import SpellSaveAction
from app.domain.targeting import AreaTargeting

logger = logging.getLogger(__name__)

# These printed innate spells do not change Iron Pit combat state.
ARENA_NEUTRAL_INNATE_SPELLS_2014 = frozenset({
    "detect-evil-and-good",
    "druidcraft",
    "pass-without-trace",
})
_PIT_BANNED_INNATE_SPELLS_2014 = frozenset({
    "teleport",
    "plane-shift",
    "dimension-door",
    "misty-step",
})
_DISPEL_ATTACKER_TYPES_2014 = ("celestial", "elemental", "fey", "fiend", "undead")


def _innate(monster: SourceMonster2014) -> dict[str, object] | None:
    raw = monster.innate_spellcasting
    return raw if isinstance(raw, dict) else None


def _spells(monster: SourceMonster2014) -> list[dict[str, object]]:
    data = _innate(monster)
    if data is None:
        return []
    spells = data.get("spells") or []
    if not isinstance(spells, list):
        raise ValueError(f"{monster.name} innate spell list is not structured.")
    return [item for item in spells if isinstance(item, dict)]


def _dc(monster: SourceMonster2014) -> int | None:
    data = _innate(monster)
    if data is None:
        return None
    raw = data.get("save_dc")
    return int(raw) if raw is not None else None


def innate_spell_save_actions_2014(monster: SourceMonster2014) -> list[SpellSaveAction]:
    """Bind printed combat innate save spells. Arena-neutral spells stay source-only."""
    try:
        actions: list[SpellSaveAction] = []
        dc = _dc(monster)
        for spell in _spells(monster):
            spell_id = str(spell.get("id") or "")
            if dc is None:
                continue
            if spell_id == "entangle":
                actions.append(SpellSaveAction(
                    id="entangle",
                    name="Entangle",
                    level=1,
                    range_ft=90,
                    area=AreaTargeting(shape="cube", origin="point", length_ft=20),
                    save_ability="strength",
                    dc=dc,
                    failed_save_timed_effect=FailedSaveTimedEffect(
                        effect_id="restrained",
                        duration_rounds=10,
                        expiry_timing="source_turn_end",
                        escape_check_ability="strength",
                        escape_check_dc=dc,
                    ),
                    concentration=True,
                    duration_minutes=1,
                    creates_difficult_terrain=True,
                    difficult_terrain_duration_rounds=10,
                    animation="entangle",
                ))
            elif spell_id == "calm-emotions":
                actions.append(SpellSaveAction(
                    id="calm-emotions",
                    name="Calm Emotions",
                    level=2,
                    range_ft=60,
                    area=AreaTargeting(shape="radius", origin="point", radius_ft=20),
                    save_ability="charisma",
                    dc=dc,
                    required_target_creature_types=["humanoid"],
                    failed_save_modifier_effects=[
                        SpellModifierEffect(kind="condition-immunity", condition_id="charmed"),
                        SpellModifierEffect(kind="condition-immunity", condition_id="frightened"),
                        SpellModifierEffect(
                            kind="debuff-counter",
                            debuff_counter=DebuffCounter(debuff_id="charmed", source_scope="any"),
                        ),
                        SpellModifierEffect(
                            kind="debuff-counter",
                            debuff_counter=DebuffCounter(debuff_id="frightened", source_scope="any"),
                        ),
                    ],
                    concentration=True,
                    duration_minutes=1,
                    animation="calm-emotions",
                ))
        return actions
    except Exception:
        logger.exception("Failed to compile 2014 innate save spells for %s.", monster.name)
        raise
