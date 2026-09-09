from __future__ import annotations

from app.domain.combat_ir import AutomaticResolutionIR, CombatActionIR, TargetingIR
from app.domain.combat_ir_effects import ArmorClassModifierEffectIR, AttackRedirectEffectIR
from app.domain.combat_ir_triggers import HitByAttackTriggerIR, TargetedByAttackTriggerIR
from app.domain.reactions import ParryReaction, RedirectAttackReaction
from app.domain.weapons import WeaponAttackKind


def parry_reaction_to_ir(reaction: ParryReaction) -> CombatActionIR:
    return CombatActionIR(
        id="parry",
        name="Parry",
        action_cost="reaction",
        trigger="reaction",
        reaction_trigger=HitByAttackTriggerIR(
            attack_kind=WeaponAttackKind.MELEE,
            requires_weapon_held=True,
        ),
        targeting=TargetingIR(range_ft=0, target_mode="self"),
        resolution=AutomaticResolutionIR(),
        effects=[ArmorClassModifierEffectIR(
            amount=reaction.ac_bonus,
            applies_to_triggering_attack=True,
        )],
        animation="parry",
    )


def parry_ir_to_reaction(action: CombatActionIR) -> ParryReaction:
    trigger = action.reaction_trigger
    if not isinstance(trigger, HitByAttackTriggerIR):
        raise ValueError("Parry IR requires a hit-by-attack trigger.")
    if trigger.attack_kind is not WeaponAttackKind.MELEE or not trigger.requires_weapon_held:
        raise ValueError("Parry IR must preserve melee-hit and weapon-held trigger restrictions.")
    if len(action.effects) != 1 or not isinstance(action.effects[0], ArmorClassModifierEffectIR):
        raise ValueError("Parry IR requires exactly one armor-class modifier effect.")
    effect = action.effects[0]
    if not effect.applies_to_triggering_attack:
        raise ValueError("Parry AC modifier must apply to the triggering attack.")
    return ParryReaction(ac_bonus=effect.amount)


def redirect_attack_reaction_to_ir(reaction: RedirectAttackReaction) -> CombatActionIR:
    return CombatActionIR(
        id="redirect-attack",
        name="Redirect Attack",
        action_cost="reaction",
        trigger="reaction",
        reaction_trigger=TargetedByAttackTriggerIR(requires_vision=True),
        targeting=TargetingIR(range_ft=0, target_mode="self"),
        resolution=AutomaticResolutionIR(),
        effects=[AttackRedirectEffectIR(
            ally_range_ft=reaction.ally_range_ft,
            ally_max_size=reaction.ally_max_size,
            swap_positions=True,
            ally_becomes_target=True,
        )],
        animation="redirect-attack",
    )


def redirect_attack_ir_to_reaction(action: CombatActionIR) -> RedirectAttackReaction:
    trigger = action.reaction_trigger
    if not isinstance(trigger, TargetedByAttackTriggerIR) or not trigger.requires_vision:
        raise ValueError("Redirect Attack IR must preserve the visible-attacker targeting trigger.")
    if len(action.effects) != 1 or not isinstance(action.effects[0], AttackRedirectEffectIR):
        raise ValueError("Redirect Attack IR requires exactly one redirect effect.")
    effect = action.effects[0]
    if not effect.swap_positions or not effect.ally_becomes_target:
        raise ValueError("Redirect Attack IR must preserve swap-and-retarget semantics.")
    return RedirectAttackReaction(
        ally_range_ft=effect.ally_range_ft,
        ally_max_size=effect.ally_max_size,
    )
