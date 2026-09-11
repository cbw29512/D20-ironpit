(() => {
  "use strict";
  const E = () => window.IRON_PIT_ACTION_ECONOMY;
  const D = () => window.IRON_PIT_DICE;
  const Z = () => window.IRON_PIT_BROWSER_ZERO_HP;
  const S = () => window.IRON_PIT_BROWSER_STATE;
  const members = (setup) => [...setup.heroes, ...setup.monsters];

  function apply(source, sourceId, targetId, attack, round) {
    const rule = attack.attachmentOnHit;
    if (!rule) return false;
    source.attachment = {
      source_id: sourceId, target_id: targetId, source_effect_id: attack.id, applied_round: round,
      periodic_damage_count: rule.periodicDamageCount, periodic_damage_size: rule.periodicDamageSize,
      periodic_damage_bonus: rule.periodicDamageBonus || 0, periodic_damage_type: rule.periodicDamageType,
      forbids_source_attack_ids: [...(rule.forbidsSourceAttackIds || [])],
      detachable_by_source_movement_ft: rule.detachableBySourceMovementFt || 0,
      detachable_by_target_action: rule.detachableByTargetAction !== false,
      detachable_by_adjacent_action: rule.detachableByAdjacentAction !== false,
    };
    return true;
  }

  const attackAvailable = (state, attack) => !state.attachment || !state.attachment.forbids_source_attack_ids.includes(attack.id);
  const sourceFor = (targetId, setup) => members(setup).find((member) => member.state.attachment?.target_id === targetId) || null;

  function detachAction(sequence, round, actor, setup) {
    if (!E().available(actor.state, "action")) return null;
    const source = sourceFor(actor.combatant_id, setup), relation = source?.state.attachment;
    if (!relation || !relation.detachable_by_target_action) return null;
    source.state.attachment = null; E().spend(actor.state, "action");
    return { sequence, round_number: round, event_type: "feature", actor_id: actor.combatant_id,
      actor_name: actor.state.template.name, target_id: source.combatant_id, target_name: source.state.template.name,
      feature_id: "detach-attachment", animation: "detach",
      description: `${actor.state.template.name} detaches ${source.state.template.name}.` };
  }

  function detachBySourceMovement(sequence, round, source) {
    const relation = source.state.attachment, cost = relation?.detachable_by_source_movement_ft || 0;
    if (!relation || !cost || source.state.movement_remaining_ft < cost) return null;
    source.state.movement_remaining_ft -= cost; source.state.attachment = null;
    return { sequence, round_number: round, event_type: "movement", actor_id: source.combatant_id,
      actor_name: source.state.template.name, feature_id: "detach-attachment", movement_ft: cost, animation: "detach",
      description: `${source.state.template.name} spends ${cost} ft. of movement to detach.` };
  }

  function adjusted(state, amount, type) {
    if (state.template.damage_immunities?.includes(type)) return 0;
    let result = amount;
    if (state.template.damage_resistances?.includes(type) || state.temporary_damage_resistances?.includes(type)) result = Math.floor(result / 2);
    if (state.template.damage_vulnerabilities?.includes(type)) result *= 2;
    return result;
  }

  function startTurn(sequence, round, source, setup) {
    const relation = source.state.attachment;
    if (!relation) return { events: [], sequence };
    const target = members(setup).find((member) => member.combatant_id === relation.target_id);
    if (!target || source.state.is_dead || !source.state.is_alive || target.state.is_dead) {
      source.state.attachment = null; return { events: [], sequence };
    }
    const rolls = Array.from({ length: relation.periodic_damage_count }, () => D().roll(relation.periodic_damage_size));
    const raw = rolls.reduce((sum, value) => sum + value, 0) + relation.periodic_damage_bonus;
    const total = adjusted(target.state, raw, relation.periodic_damage_type), hpBefore = target.state.current_hp;
    Z().applyDamage(target.state, total, false, total > 0 ? [relation.periodic_damage_type] : [], members(setup).map((member) => member.state));
    const component = { source: source.state.template.name, notation: `${relation.periodic_damage_count}d${relation.periodic_damage_size}${relation.periodic_damage_bonus ? `+${relation.periodic_damage_bonus}` : ""}`,
      rolls, modifier: relation.periodic_damage_bonus, damage_type: relation.periodic_damage_type, total: raw, applied_total: total };
    const event = { sequence, round_number: round, event_type: "feature", actor_id: source.combatant_id,
      actor_name: source.state.template.name, target_id: target.combatant_id, target_name: target.state.template.name,
      feature_id: relation.source_effect_id, damage_roll: { notation: component.notation, rolls, modifier: relation.periodic_damage_bonus, total },
      damage_components: [component], hp_before: hpBefore, hp_after: target.state.current_hp, animation: "attachment-damage",
      description: `${source.state.template.name}'s attached effect deals ${total} ${relation.periodic_damage_type} damage to ${target.state.template.name}.` };
    return { events: [event], sequence: sequence + 1 };
  }

  window.IRON_PIT_BROWSER_ATTACHMENTS = { apply, attackAvailable, detachAction, detachBySourceMovement, sourceFor, startTurn };
})();