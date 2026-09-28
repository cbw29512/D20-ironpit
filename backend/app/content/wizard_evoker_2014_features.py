from __future__ import annotations

import logging

from app.domain.area_spell_protection import AreaSpellAllyProtectionGrant
from app.domain.progression import ProgressionCombatFeatures
from app.domain.spell_features import SpellDamageMaximizerGrant, SpellSpecificCastGrant

logger = logging.getLogger(__name__)

_EVOCATION_AREA_SPELL_IDS = [
    "burning-hands", "shatter", "fireball", "lightning-bolt", "cone-of-cold",
]


def build_wizard_evoker_2014_features(level: int) -> ProgressionCombatFeatures:
    try:
        grants: list[SpellSpecificCastGrant] = []
        if level >= 18:
            grants.extend([
                SpellSpecificCastGrant(
                    source_id="spell-mastery-burning-hands", source_name="Spell Mastery",
                    spell_id="burning-hands", slot_level=1, unlimited=True,
                ),
                SpellSpecificCastGrant(
                    source_id="spell-mastery-shatter", source_name="Spell Mastery",
                    spell_id="shatter", slot_level=2, unlimited=True,
                ),
            ])
        if level >= 20:
            grants.extend([
                SpellSpecificCastGrant(
                    source_id="signature-spell-fireball", source_name="Signature Spells",
                    spell_id="fireball", slot_level=3, resource_id="signature-spell-fireball",
                ),
                SpellSpecificCastGrant(
                    source_id="signature-spell-lightning-bolt", source_name="Signature Spells",
                    spell_id="lightning-bolt", slot_level=3,
                    resource_id="signature-spell-lightning-bolt",
                ),
            ])
        return ProgressionCombatFeatures(
            area_spell_ally_protection=(
                AreaSpellAllyProtectionGrant(
                    source_id="sculpt-spells", source_name="Sculpt Spells",
                    eligible_spell_ids=list(_EVOCATION_AREA_SPELL_IDS),
                    base_protected_allies=1, protected_allies_per_slot_level=1,
                    requires_source_sight=True, auto_success_save=True, no_damage_on_success=True,
                ) if level >= 2 else None
            ),
            spell_specific_cast_grants=grants,
            spell_damage_maximizer=(
                SpellDamageMaximizerGrant(
                    source_id="overchannel", source_name="Overchannel",
                    minimum_spell_level=1, maximum_spell_level=5, free_uses=1,
                    self_damage_die_size=12, repeat_base_dice_per_spell_level=2,
                    repeat_increment_dice_per_spell_level=1, self_damage_type="necrotic",
                    bypasses_resistance_and_immunity=True,
                ) if level >= 14 else None
            ),
        )
    except Exception:
        logger.exception("Failed to build 2014 Evoker features at level %s.", level)
        raise
