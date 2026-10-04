from __future__ import annotations

import logging

from app.domain.alternate_spell_casts import AlternateSpellCastGrant
from app.domain.area_spell_protection import AreaSpellAllyProtectionGrant
from app.domain.d20_outcome_adjustments import ResourceBackedD20OutcomeAdjustment
from app.domain.progression import ProgressionCombatFeatures
from app.domain.spell_damage_maximizers import SpellDamageMaximizerGrant

logger = logging.getLogger(__name__)

_EVOCATION_AREA_SPELL_IDS = [
    "burning-hands", "thunderwave", "shatter", "thunderclap",
    "fireball", "lightning-bolt", "cone-of-cold", "sunburst",
]


def build_wizard_evoker_2024_features(level: int) -> ProgressionCombatFeatures:
    try:
        alternate: list[AlternateSpellCastGrant] = []
        if level >= 18:
            alternate.extend([
                AlternateSpellCastGrant(
                    source_id="spell-mastery-burning-hands",
                    source_name="Spell Mastery",
                    spell_id="burning-hands",
                    cast_level=1,
                    priority=100,
                ),
                AlternateSpellCastGrant(
                    source_id="spell-mastery-shatter",
                    source_name="Spell Mastery",
                    spell_id="shatter",
                    cast_level=2,
                    priority=100,
                ),
            ])
        if level >= 20:
            alternate.extend([
                AlternateSpellCastGrant(
                    source_id="signature-spells-fireball",
                    source_name="Signature Spells",
                    spell_id="fireball",
                    cast_level=3,
                    resource_id="signature-spell-fireball",
                    priority=90,
                ),
                AlternateSpellCastGrant(
                    source_id="signature-spells-lightning-bolt",
                    source_name="Signature Spells",
                    spell_id="lightning-bolt",
                    cast_level=3,
                    resource_id="signature-spell-lightning-bolt",
                    priority=90,
                ),
            ])
        return ProgressionCombatFeatures(
            area_spell_ally_protection=(
                AreaSpellAllyProtectionGrant(
                    source_id="sculpt-spells",
                    source_name="Sculpt Spells",
                    eligible_spell_ids=list(_EVOCATION_AREA_SPELL_IDS),
                    base_protected_allies=1,
                    protected_allies_per_slot_level=1,
                    requires_source_sight=True,
                )
                if level >= 6 else None
            ),
            alternate_spell_cast_grants=alternate,
            spell_damage_maximizer=(
                SpellDamageMaximizerGrant(
                    source_id="overchannel",
                    source_name="Overchannel",
                    eligible_spell_ids=[
                        "magic-missile", "burning-hands", "thunderwave", "shatter",
                        "fireball", "lightning-bolt", "blight", "cone-of-cold",
                    ],
                    minimum_spell_level=1,
                    maximum_spell_level=5,
                    safe_uses=1,
                    self_damage_dice_size=12,
                    initial_self_damage_dice_per_spell_level=2,
                    self_damage_increment_per_spell_level=1,
                    self_damage_type="necrotic",
                    ignores_resistance_and_immunity=True,
                )
                if level >= 14 else None
            ),
            resource_backed_d20_outcome_adjustments=(
                [ResourceBackedD20OutcomeAdjustment(
                    source_id="boon-of-fate",
                    source_name="Boon of Fate",
                    resource_id="boon-of-fate",
                    dice_count=2,
                    dice_size=4,
                    range_ft=60,
                    test_kinds=["attack", "saving_throw", "ability_check"],
                    can_add=True,
                    can_subtract=True,
                )] if level >= 19 else []
            ),
        )
    except Exception:
        logger.exception("Failed to build Elian's 2024 progression features at level %s.", level)
        raise
