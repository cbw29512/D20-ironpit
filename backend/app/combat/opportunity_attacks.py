from __future__ import annotations

from app.combat.action_economy import spend
from app.combat.ally_context import pack_tactics_active
from app.combat.dice import DiceProvider
from app.combat.encounter_attacks import resolve_encounter_attack
from app.combat.opportunity_attack_rules import MovementSource, opportunity_attack_weapon
from app.domain.encounters import EncounterCombatant, EncounterSetup
from app.domain.models import BattleEvent


def resolve_opportunity_attack(
    sequence: int,
    round_number: int,
    reactor: EncounterCombatant,
    mover: EncounterCombatant,
    setup: EncounterSetup,
    distance_before_ft: int,
    distance_after_ft: int,
    movement_source: MovementSource,
    dice: DiceProvider,
    *,
    disengaged: bool = False,
    can_see: bool = True,
) -> BattleEvent | None:
    """Resolve the universal 2024 Opportunity Attack Reaction immediately before reach is left."""
    attack = opportunity_attack_weapon(
        reactor, mover, distance_before_ft, distance_after_ft, movement_source,
        disengaged=disengaged, can_see=can_see,
    )
    if attack is None:
        return None
    spend(reactor.state, "reaction")
    pack = pack_tactics_active(reactor, mover, setup)
    return resolve_encounter_attack(
        sequence, round_number, reactor, mover, attack, distance_before_ft, dice, setup,
        spend_action=False, advantage_sources=1 if pack else 0,
        feature_id="opportunity-attack", close_enemy_active=True,
    )
