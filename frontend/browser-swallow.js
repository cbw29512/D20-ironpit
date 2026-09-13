(() => {
  "use strict";

  const S = () => window.IRON_PIT_BROWSER_STATE;
  const G = () => window.IRON_PIT_BROWSER_GRAPPLE;
  const E = () => window.IRON_PIT_ACTION_ECONOMY;
  const Z = () => window.IRON_PIT_BROWSER_ZERO_HP;
  const I = () => window.IRON_PIT_BROWSER_CONDITION_IMMUNITY || { immune: () => false };
  const D = () => window.IRON_PIT_DICE;

  function members(setup) { return [...setup.heroes, ...setup.monsters]; }
  function swallowedTargets(sourceId, setup) {
    return members(setup).filter((member) => member.state.swallowed?.source_id === sourceId);
  }
  function choose(source, setup) {
    const swallowedCount = swallowedTargets(source.combatant_id, setup).length;
    const opponents = source.side === "heroes" ? setup.monsters : setup.heroes;
    for (const target of opponents) {
      if (!target.state.is_alive || target.state.is_dead || target.state.swallowed) continue;
      const held = (target.state.grapple_sources || []).some((item) => item.source_id === source.combatant_id);
      for (const action of source.state.template.swallow_actions || []) {
        const cost = action.actionCost || "action";
        const capacity = action.maxSwallowedTargets || 1;
        const requiresGrapple = action.requiresGrappledTarget !== false;
        if (!E().available(source.state, cost)) continue;
        if (swallowedCount >= capacity) continue;
        if (requiresGrapple && !held) continue;
        if (S().sizeAtMost(target, action.maxTargetSize)) return { target, action };
      }
    }
    return null;
  }
  function resolve(sequence, round, source, setup) {
    const picked = choose(source, setup);
    if (!picked) return { handled: false, events: [], sequence };
    const { target, action } = picked;
    const applied = [];
    if (action.appliesBlinded && !I().immune(target.state, "blinded")) applied.push("blinded");
    if (action.appliesRestrained && !I().immune(target.state, "restrained")) applied.push("restrained");
    if ((target.state.grapple_sources || []).some((item) => item.source_id === source.combatant_id)) {
      G().release(target.state, source.combatant_id);
    }
    target.state.swallowed = {
      source_id: source.combatant_id,
      action_id: action.id,
      applied_round: round,
      first_tick_round: round + (action.firstTickDelayRounds || 0),
      applied_condition_ids: applied,
      total_cover_from_outside: action.totalCoverFromOutside !== false,
    };
    target.position_ft = source.position_ft;
    target.state.position = source.state.position;
    E().spend(source.state, action.actionCost || "action");
    return {
      handled: true,
      sequence: sequence + 1,
      events: [{
        sequence, round_number: round, event_type: "feature",
        actor_id: source.combatant_id, actor_name: source.state.template.name,
        target_id: target.combatant_id, target_name: target.state.template.name,
        feature_id: action.id, applied_condition_ids: applied, animation: "swallow",
        description: `${source.state.template.name} swallows ${target.state.template.name}.`,
      }],
    };
  }
  function forbiddenAttacks(source, setup) {
    const active = swallowedTargets(source.combatant_id, setup)
      .map((target) => target.state.swallowed)
      .filter(Boolean);
    if (!active.length) return new Set();
    const actions = new Map((source.state.template.swallow_actions || []).map((item) => [item.id, item]));
    const forbidden = new Set();
    for (const swallowed of active) {
      const action = actions.get(swallowed.action_id);
      if (!action) throw new Error(`Missing active Swallow action ${swallowed.action_id}.`);
      for (const attackId of action.forbiddenAttackIdsWhileActive || []) forbidden.add(attackId);
    }
    return forbidden;
  }
  function adjusted(state, amount, type) {
    if ((state.template.damage_immunities || []).includes(type)) return 0;
    return (state.template.damage_resistances || []).includes(type) ? Math.floor(amount / 2) : amount;
  }
  function release(source, target, prone) {
    const removed = [...(target.state.swallowed?.applied_condition_ids || [])];
    target.state.swallowed = null;
    target.position_ft = source.position_ft;
    target.state.position = source.state.position;
    if (prone && !I().immune(target.state, "prone") && !target.state.active_effect_ids.includes("prone")) target.state.active_effect_ids.push("prone");
    return removed;
  }
  function turnEnd(sequence, round, source, setup) {
    const events = [];
    const byId = new Map((source.state.template.swallow_actions || []).map((action) => [action.id, action]));
    for (const target of swallowedTargets(source.combatant_id, setup)) {
      const swallowed = target.state.swallowed;
      if (!swallowed || round < swallowed.first_tick_round) continue;
      const action = byId.get(swallowed.action_id);
      if (!action) throw new Error(`Missing Swallow action ${swallowed.action_id}.`);
      const rolls = Array.from({ length: action.damageDiceCount }, () => D().roll(action.damageDiceSize));
      const raw = rolls.reduce((sum, roll) => sum + roll, 0) + (action.damageBonus || 0);
      const total = adjusted(target.state, raw, action.damageType);
      const hpBefore = target.state.current_hp;
      Z().applyDamage(target.state, total, false, total > 0 ? [action.damageType] : [], members(setup).map((member) => member.state));
      const removed = action.disgorgeAfterFirstTick && !target.state.is_dead ? release(source, target, true) : [];
      events.push({
        sequence: sequence++, round_number: round, event_type: "feature",
        actor_id: source.combatant_id, actor_name: source.state.template.name,
        target_id: target.combatant_id, target_name: target.state.template.name,
        feature_id: action.id,
        damage_roll: { notation: `${action.damageDiceCount}d${action.damageDiceSize}+${action.damageBonus || 0}`, rolls, modifier: action.damageBonus || 0, mode: "normal", total },
        hp_before: hpBefore, hp_after: target.state.current_hp, removed_condition_ids: removed,
        animation: "swallow-damage", description: `${action.name} deals ${total} ${action.damageType} damage to ${target.state.template.name}.`,
      });
    }
    return { events, sequence };
  }

  window.IRON_PIT_BROWSER_SWALLOW = { choose, forbiddenAttacks, resolve, swallowedTargets, turnEnd };
})();