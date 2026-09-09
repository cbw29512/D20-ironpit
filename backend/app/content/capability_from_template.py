from __future__ import annotations

from app.content.capability_compiler import UnsupportedCapabilityError
from app.domain.capabilities import CombatantDefinition
from app.domain.effect_gates import EffectGate
from app.domain.models import CombatantTemplate, WeaponAttack


def _dice(count: int, size: int, bonus: int = 0) -> dict[str, int]:
    return {"count": count, "size": size, "bonus": bonus}


def _gate(control) -> dict[str, object] | None:
    return None if control.gate == EffectGate() else control.gate.model_dump(mode="json")


def _control_effect(control) -> dict[str, object]:
    has_grapple = control.grapple_escape_dc is not None
    has_condition = control.condition_id is not None
    if has_grapple and has_condition:
        raise UnsupportedCapabilityError("Runtime control rider combines grapple and condition.")
    common: dict[str, object] = {"max_target_size": control.max_target_size}
    gate = _gate(control)
    if gate is not None:
        common["gate"] = gate
    if has_grapple:
        return {
            "kind": "grapple", "escape_dc": control.grapple_escape_dc,
            "restrains": control.restrains_while_grappled, **common,
        }
    if has_condition:
        return {
            "kind": "condition", "condition": control.condition_id,
            "expires_at_start_of_source_turn": control.expires_at_start_of_source_turn,
            "expiry_timing": control.expiry_timing,
            "repeat_save_ability": control.repeat_save_ability,
            "repeat_save_dc": control.repeat_save_dc,
            "repeat_save_timing": control.repeat_save_timing,
            "allowed_removal_action_ids": control.allowed_removal_action_ids,
            **common,
        }
    raise UnsupportedCapabilityError("Runtime control rider has no supported grapple or condition effect.")


def _resource_binding(result: dict[str, object], action) -> None:
    if action.resource_id is not None:
        result["resource_id"] = action.resource_id
        result["resource_cost"] = action.resource_cost


def _attack(attack: WeaponAttack) -> dict[str, object]:
    weapon = attack.weapon
    effects: list[dict[str, object]] = [
        {"kind": "damage", "source": extra.source, "dice": _dice(extra.dice_count, extra.dice_size, extra.damage_bonus), "damage_type": extra.damage_type}
        for extra in attack.on_hit_damage
    ]
    effects.extend({
        "kind": "damage", "source": f"conditional:{extra.trigger}",
        "dice": _dice(extra.dice_count, extra.dice_size, extra.damage_bonus),
        "damage_type": extra.damage_type, "trigger": extra.trigger, "mode": extra.mode,
    } for extra in attack.conditional_damage)
    effects.extend(effect.model_dump(mode="json") for effect in attack.on_hit_modifier_effects)
    if attack.knocks_prone_max_size is not None:
        effects.append({"kind": "prone", "max_target_size": attack.knocks_prone_max_size})
    if attack.control_effect is not None:
        effects.append(_control_effect(attack.control_effect))
    elif attack.persistent_effects:
        effects.extend(_control_effect(effect) for effect in attack.persistent_effects)
    result: dict[str, object] = {
        "id": attack.id, "weapon_id": weapon.id, "name": weapon.name,
        "attack_kind": weapon.attack_kind, "attack_bonus": attack.attack_bonus,
        "damage_type": weapon.damage_type, "animation": weapon.animation,
        "reach_ft": weapon.reach_ft, "normal_range_ft": weapon.normal_range_ft,
        "long_range_ft": weapon.long_range_ft, "projectile": weapon.projectile,
        "mastery_property": weapon.mastery_property,
        "light": weapon.light, "finesse": weapon.finesse, "heavy": weapon.heavy,
        "two_handed": weapon.two_handed, "versatile": weapon.versatile,
        "attack_ability": attack.attack_ability, "attack_ability_modifier": attack.attack_ability_modifier,
        "rage_eligible": attack.rage_eligible, "effects": effects,
        "forbid_target_grappled_by_self": attack.forbid_target_grappled_by_self,
    }
    _resource_binding(result, attack)
    if attack.fixed_damage is None:
        result["damage"] = _dice(weapon.dice_count, weapon.dice_size, attack.damage_bonus)
    else:
        result["fixed_damage"] = attack.fixed_damage
    return result


def _save(action) -> dict[str, object]:
    result: dict[str, object] = {
        "id": action.id, "name": action.name, "save_ability": action.save_ability,
        "dc": action.dc, "range_ft": action.range_ft, "target_max_size": action.target_max_size,
        "success_damage": action.success_damage, "animation": action.animation,
    }
    _resource_binding(result, action)
    if action.damage_dice_count:
        result["damage"] = _dice(action.damage_dice_count, action.damage_dice_size, action.damage_bonus)
        result["damage_type"] = action.damage_type
    persistent = [_control_effect(effect) for effect in action.persistent_effects]
    if len(persistent) == 1 and persistent[0]["kind"] == "grapple" and "gate" not in persistent[0] and not action.on_failure_modifier_effects:
        result["grapple"] = persistent[0]
    elif persistent or action.on_failure_modifier_effects:
        result["effects"] = [*persistent, *(effect.model_dump(mode="json") for effect in action.on_failure_modifier_effects)]
    elif action.grapple_escape_dc is not None:
        result["grapple"] = {
            "kind": "grapple", "escape_dc": action.grapple_escape_dc,
            "max_target_size": action.target_max_size, "restrains": action.restrains_while_grappled,
        }
    return result


def definition_from_template(template: CombatantTemplate) -> CombatantDefinition:
    attacks = [template.weapon_attack, *template.alternate_weapon_attacks]
    data = template.model_dump(mode="json", exclude={"weapon_attack", "alternate_weapon_attacks", "attack_action", "saving_throw_actions"})
    data["attacks"] = [_attack(attack) for attack in attacks]
    data["primary_attack_id"] = template.weapon_attack.id
    data["save_actions"] = [_save(action) for action in template.saving_throw_actions]
    if template.attack_action is not None:
        data["attack_action"] = {
            "id": template.attack_action.id, "name": template.attack_action.name,
            "is_attack_action": template.attack_action.is_attack_action,
            "slots": [slot.model_dump(mode="json") for slot in template.attack_action.slots],
        }
    return CombatantDefinition.model_validate(data)
