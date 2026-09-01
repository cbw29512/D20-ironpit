from __future__ import annotations

from app.domain.spells import DefensiveSpellAction, SpellModifierEffect


SHIELD_OF_FAITH = DefensiveSpellAction(
    id="shield-of-faith",
    name="Shield of Faith",
    level=1,
    action_cost="bonus_action",
    range_ft=60,
    duration_minutes=10,
    modifier_effects=[SpellModifierEffect(kind="armor-class", flat_bonus=2)],
    concentration=True,
    priority=20,
    animation="shield-of-faith",
    source="SRD 5.2.1 p.162",
)


def defensive_spell_by_id(spell_id: str) -> DefensiveSpellAction:
    spells = {SHIELD_OF_FAITH.id: SHIELD_OF_FAITH}
    try:
        return spells[spell_id]
    except KeyError as exc:
        raise ValueError(f"Unsupported certified defensive spell: {spell_id}") from exc
