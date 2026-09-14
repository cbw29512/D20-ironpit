from __future__ import annotations

from app.combat.damage_defenses import apply_damage_defenses
from app.combat.zero_hp import apply_damage, apply_hit_point_loss
from app.domain.event_support import DamageRollComponent, DiceRoll
from app.domain.models import BattleEvent, CombatantState, DamageType, WeaponAttack
from app.domain.ongoing_damage import OngoingDamageState


def _matching(state: CombatantState, source_id: str, attack_id: str) -> OngoingDamageState | None:
    return next((item for item in state.ongoing_damage_effects if item.source_id == source_id and item.source_effect_id == attack_id), None)


def should_skip_on_hit_save(state: CombatantState, attack: WeaponAttack, source_id: str) -> bool:
    effect = attack.ongoing_damage_effect
    return bool(effect and effect.apply_on == "failed_on_hit_save" and effect.stacks_on_reapply and _matching(state, source_id, attack.id))


def apply_on_hit_ongoing_damage(
    state: CombatantState, attack: WeaponAttack, source_id: str, save_succeeded: bool | None,
) -> bool:
    effect = attack.ongoing_damage_effect
    if effect is None or state.is_dead or not state.is_alive: return False
    existing = _matching(state, source_id, attack.id)
    if existing is not None:
        if effect.stacks_on_reapply: existing.stacks += 1; return True
        return False
    if effect.ends_when_grapple_source_ends and not any(
        item.source_id == source_id and item.source_effect_id == attack.id for item in state.grapple_sources
    ): return False
    if effect.apply_on == "failed_on_hit_save" and save_succeeded is not False: return False
    state.ongoing_damage_effects.append(OngoingDamageState(source_id=source_id, source_effect_id=attack.id, effect=effect))
    return True


def clear_magical_healing(state: CombatantState) -> list[str]:
    removed = [item.effect.id for item in state.ongoing_damage_effects if item.effect.ends_on_magical_healing]
    state.ongoing_damage_effects = [item for item in state.ongoing_damage_effects if not item.effect.ends_on_magical_healing]
    return removed


def _cleanup_ongoing(state: CombatantState) -> None:
    state.ongoing_damage_effects = [
        item for item in state.ongoing_damage_effects
        if not item.effect.ends_when_grapple_source_ends or any(
            source.source_id == item.source_id and source.source_effect_id == item.source_effect_id
            for source in state.grapple_sources
        )
    ]


def resolve_start_turn_ongoing_damage(sequence: int, round_number: int, member, setup, dice):
    _cleanup_ongoing(member.state); events: list[BattleEvent] = []
    affected = [item.state for item in [*setup.heroes, *setup.monsters]]
    for ongoing in list(member.state.ongoing_damage_effects):
        effect = ongoing.effect; count = effect.dice_count * ongoing.stacks
        rolls = [dice.roll(effect.dice_size) for _ in range(count)]
        modifier = effect.damage_bonus * ongoing.stacks; raw = max(0, sum(rolls) + modifier)
        hp_before = member.state.current_hp; components = []; applied = raw
        if effect.damage_type is None:
            apply_hit_point_loss(member.state, raw)
        else:
            dtype = DamageType(effect.damage_type)
            component = DamageRollComponent(
                source=effect.name, notation=f"{count}d{effect.dice_size}+{modifier}", rolls=rolls,
                modifier=modifier, damage_type=dtype, total=raw,
            )
            applied, components = apply_damage_defenses(member.state, [component])
            if applied: apply_damage(member.state, applied, damage_types={dtype}, dice=dice, affected_states=affected)
        wording = f"loses {applied} hit points" if effect.damage_type is None else f"takes {applied} {effect.damage_type} damage"
        events.append(BattleEvent(
            sequence=sequence, round_number=round_number, event_type="feature", actor_id=ongoing.source_id,
            actor_name=effect.name, target_id=member.combatant_id, target_name=member.state.template.name,
            feature_id=effect.id, damage_roll=DiceRoll(
                notation=f"{count}d{effect.dice_size}+{modifier}", rolls=rolls, modifier=modifier, total=applied,
            ), damage_components=components, hp_before=hp_before, hp_after=member.state.current_hp,
            is_dead=member.state.is_dead, animation="damage",
            description=f"{member.state.template.name} {wording} from {effect.name}.",
        )); sequence += 1
    return events, sequence


def resolve_start_turn_relationship_damage(sequence: int, round_number: int, source, setup, dice):
    events: list[BattleEvent] = []
    by_id = {member.combatant_id: member for member in [*setup.heroes, *setup.monsters]}
    affected_states = [member.state for member in by_id.values()]
    for profile in source.state.template.start_turn_relationship_damage:
        if profile.target_relationship != "grapplers": continue
        target_ids = list(dict.fromkeys(item.source_id for item in source.state.grapple_sources))
        for target_id in target_ids:
            target = by_id.get(target_id)
            if target is None or target.state.is_dead or not target.state.is_alive: continue
            rolls = [dice.roll(profile.dice_size) for _ in range(profile.dice_count)]
            raw = max(0, sum(rolls) + profile.damage_bonus)
            component = DamageRollComponent(
                source=profile.name, notation=f"{profile.dice_count}d{profile.dice_size}+{profile.damage_bonus}",
                rolls=rolls, modifier=profile.damage_bonus, damage_type=profile.damage_type, total=raw,
            )
            applied_total, components = apply_damage_defenses(target.state, [component])
            hp_before = target.state.current_hp
            if applied_total:
                apply_damage(target.state, applied_total, damage_types={profile.damage_type}, dice=dice, affected_states=affected_states)
            events.append(BattleEvent(
                sequence=sequence, round_number=round_number, event_type="feature", actor_id=source.combatant_id,
                actor_name=source.state.template.name, target_id=target.combatant_id, target_name=target.state.template.name,
                feature_id=profile.id, damage_roll=DiceRoll(notation=component.notation, rolls=rolls, modifier=profile.damage_bonus, total=applied_total),
                damage_components=components, hp_before=hp_before, hp_after=target.state.current_hp, animation="damage",
                description=f"{target.state.template.name} takes {applied_total} {profile.damage_type.value} damage from {source.state.template.name}'s {profile.name}.",
            )); sequence += 1
    return events, sequence
