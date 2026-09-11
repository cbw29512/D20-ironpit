(() => {
  "use strict";
  const E = () => window.IRON_PIT_ACTION_ECONOMY;
  const O = () => window.IRON_PIT_BROWSER_ONGOING_DAMAGE;
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
    const all = members(setup);
    for (const source of all) {
      const relation = source.state.attachment;
      if (!relation) continue;
      const target = all.find((member) => member.combatant_id === relation.target_id);
      if (!target || target.side !== actor.side) continue;
      const targetDetach = actor.combatant_id === target.combatant_id && relation.detachable_by_target_action;
      const adjacentDetach = actor.combatant_id !== target.combatant_id && relation.detachable_by_adjacent_action && S().distance(actor, target) <= 5;
      if (!targetDetach && !adjacentDetach) continue;
      source.state.attachment = null; E().spend(actor.state, "action");
      return { sequence, round_number: round, event_type: "feature", actor_id: actor.combatant_id,
        actor_name: actor.state.template.name, target_id: source.combatant_id, target_name: source.state.template.name,
        feature_id: "detach-attachment", animation: "detach",
        description: `${actor.state.template.name} detaches ${source.state.template.name}.` };
    }
    return null;
  }

  function detachBySourceMovement(sequence, round, source) {
    const relation = source.state.attachment, cost = relation?.detachable_by_source_movement_ft || 0;
    if (!relation || !cost || source.state.movement_remaining_ft < cost) return null;
    source.state.movement_remaining_ft -= cost; source.state.attachment = null;
    return { sequence, round_number: round, event_type: "movement", actor_id: source.combatant_id,
      actor_name: source.state.template.name, feature_id: "detach-attachment", movement_ft: cost, animation: "detach",
      description: `${source.state.template.name} spends ${cost} ft. of movement to detach.` };
  }

  function startTurn(sequence, round, source, setup) {
    const relation = source.state.attachment;
    if (!relation) return { events: [], sequence };
    const target = members(setup).find((member) => member.combatant_id === relation.target_id);
    if (!target || source.state.is_dead || !source.state.is_alive || target.state.is_dead) {
      source.state.attachment = null; return { events: [], sequence };
    }
    const event = O().resolve(sequence, round, source, target, setup, {
      featureId: relation.source_effect_id, featureName: "attached effect",
      diceCount: relation.periodic_damage_count, diceSize: relation.periodic_damage_size,
      damageBonus: relation.periodic_damage_bonus, damageType: relation.periodic_damage_type,
      animation: "attachment-damage",
    });
    if (target.state.is_dead) source.state.attachment = null;
    return { events: [event], sequence: sequence + 1 };
  }

  window.IRON_PIT_BROWSER_ATTACHMENTS = { apply, attackAvailable, detachAction, detachBySourceMovement, sourceFor, startTurn };
})();