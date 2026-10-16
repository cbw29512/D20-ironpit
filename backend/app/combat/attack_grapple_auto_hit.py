"""Typed auto-hit predicate for weapon attacks against owner-grappled targets."""
from __future__ import annotations
from app.combat.attack_d20_outcome import AttackD20Outcome
from app.combat.attack_roll_resolution import AttackRollResolution
from app.domain.models import RollMode

def owned_grapple_auto_hit(attack, owner_id: str, defender) -> bool:
    return attack.grapple_target_policy == "auto_hit_own_grapple" and any(
        grapple.source_id == owner_id for grapple in defender.grapple_sources
    )

def automatic_hit_roll() -> AttackRollResolution:
    return AttackRollResolution(
        roll=None, mode=RollMode.NORMAL, heroic_reroll=False,
        brutal_strike_disadvantage=0,
    )

def automatic_hit_outcome(target_ac: int) -> AttackD20Outcome:
    return AttackD20Outcome(
        roll=None, target_ac=target_ac, hit=True, natural=0, parry_used=False,
    )
