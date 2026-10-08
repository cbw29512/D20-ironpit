"""Bind 2014 traits onto existing save-advantage and Bonus Action Dash grants."""
from __future__ import annotations

import logging

from app.content.monster_source_2014 import SourceMonster2014
from app.content.monster_contextual_save_defenses import contextual_save_defenses_2014
from app.domain.progression import SavingThrowAdvantageGrant
from app.domain.tactical_actions import BonusActionTacticalGrant

logger = logging.getLogger(__name__)
_ALL_SAVE_ABILITIES = (
    "strength", "dexterity", "constitution", "intelligence", "wisdom", "charisma",
)
_MAGIC_RESISTANCE = "Magic Resistance"
_DARK_DEVOTION = "Dark Devotion"
_BRAVE = "Brave"
_GNOME_CUNNING = "Gnome Cunning"
_FEY_ANCESTRY = "Fey Ancestry"
_AGGRESSIVE = "Aggressive"
_TWO_HEAD_TRAITS = frozenset({"Two-Headed", "Two Heads"})
_TWO_HEAD_SAVE_TAGS = (
    "blinded", "charm", "charmed", "deafened", "frightened", "stunned", "unconscious",
)


def _condition_save_advantage(source_id: str, source_name: str, tags: tuple[str, ...]) -> list[SavingThrowAdvantageGrant]:
    """Compose one printed trait from the shared per-tag save-Advantage grant."""
    try:
        return [
            SavingThrowAdvantageGrant(
                source_id=f"{source_id}-{tag}",
                source_name=source_name,
                abilities=list(_ALL_SAVE_ABILITIES),
                required_effect_tags=[tag],
            )
            for tag in tags
        ]
    except Exception:
        logger.exception("Failed to compose %s save-Advantage grants.", source_name)
        raise


def saving_throw_advantage_grants_2014(monster: SourceMonster2014) -> list[SavingThrowAdvantageGrant]:
    """Map printed 2014 traits onto the shared saving-throw Advantage grant."""
    try:
        grants: list[SavingThrowAdvantageGrant] = []
        if _MAGIC_RESISTANCE in monster.trait_names:
            grants.append(SavingThrowAdvantageGrant(
                source_id="magic-resistance",
                source_name=_MAGIC_RESISTANCE,
                abilities=list(_ALL_SAVE_ABILITIES),
                requires_magical_effect=True,
            ))
        if _DARK_DEVOTION in monster.trait_names:
            grants.extend(_condition_save_advantage("dark-devotion", _DARK_DEVOTION, ("charm", "frightened")))
        if _BRAVE in monster.trait_names:
            grants.extend(_condition_save_advantage("brave", _BRAVE, ("frightened",)))
        if _GNOME_CUNNING in monster.trait_names:
            grants.append(SavingThrowAdvantageGrant(
                source_id="gnome-cunning", source_name=_GNOME_CUNNING,
                abilities=["intelligence", "wisdom", "charisma"],
                requires_magical_effect=True,
            ))
        if _FEY_ANCESTRY in monster.trait_names:
            grants.extend(_condition_save_advantage("fey-ancestry", _FEY_ANCESTRY, ("charm",)))
        for trait_name in monster.trait_names:
            if trait_name not in _TWO_HEAD_TRAITS:
                continue
            grants.extend(_condition_save_advantage(
                trait_name.casefold().replace(" ", "-"),
                trait_name,
                _TWO_HEAD_SAVE_TAGS,
            ))
        grants.extend(contextual_save_defenses_2014(monster)[1])
        return grants
    except Exception:
        logger.exception("Failed to bind 2014 save-Advantage traits for %s.", monster.name)
        raise


def aggressive_tactical_grants_2014(monster: SourceMonster2014) -> list[BonusActionTacticalGrant]:
    """Bind printed Aggressive to the shared enable-offense Bonus Action Dash grant."""
    try:
        if _AGGRESSIVE not in monster.trait_names:
            return []
        return [BonusActionTacticalGrant(
            id="aggressive-dash",
            name=_AGGRESSIVE,
            effects=["dash"],
            priority=50,
            use_policy="enable-offense",
        )]
    except Exception:
        logger.exception("Failed to bind 2014 Aggressive for %s.", monster.name)
        raise


def bound_passive_trait_names_2014(monster: SourceMonster2014) -> frozenset[str]:
    """Return printed traits fully represented by the shared grant primitives above."""
    try:
        bound: set[str] = set()
        actions, grants = contextual_save_defenses_2014(monster)
        bound.update(item.name for item in actions)
        bound.update(item.source_name for item in grants)
        if _MAGIC_RESISTANCE in monster.trait_names:
            bound.add(_MAGIC_RESISTANCE)
        if _DARK_DEVOTION in monster.trait_names:
            bound.add(_DARK_DEVOTION)
        if _BRAVE in monster.trait_names:
            bound.add(_BRAVE)
        if _GNOME_CUNNING in monster.trait_names:
            bound.add(_GNOME_CUNNING)
        if _FEY_ANCESTRY in monster.trait_names:
            bound.add(_FEY_ANCESTRY)
        if _AGGRESSIVE in monster.trait_names:
            bound.add(_AGGRESSIVE)
        bound.update(name for name in monster.trait_names if name in _TWO_HEAD_TRAITS)
        return frozenset(bound)
    except Exception:
        logger.exception("Failed to classify 2014 passive grant traits for %s.", monster.name)
        raise
