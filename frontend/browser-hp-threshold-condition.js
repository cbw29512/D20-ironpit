(() => {
  "use strict";

  const E = () => window.IRON_PIT_ACTION_ECONOMY;
  const F = () => window.IRON_PIT_BROWSER_FORMATION;
  const T = () => window.IRON_PIT_BROWSER_TIMED;

  function resourceAvailable(member, action) {
    if (!action.resourceId) return true;
    return (member.state.resources?.[action.resourceId] || 0) >= (action.resourceCost || 1);
  }

  function legal(member, target, action) {
    if (!E().available(member.state, action.actionCost || "action")) return false;
    if (!target.state.is_alive || target.state.is_dead || target.state.current_hp <= 0) return false;
    if (target.state.current_hp > action.maxCurrentHp) return false;
    if (F().saveDistance(member, target, action.range || 0) > (action.range || 0)) return false;
    return resourceAvailable(member, action);
  }

  function choose(member, setup) {
    for (const action of member.state.template.hp_threshold_condition_actions || []) {
      for (const target of F().targetOrder(member, setup)) {
        if (legal(member, target, action)) return { target, action };
      }
    }
    return null;
  }

  function resolve(sequence, round, member, target, action, setup) {
    if (!legal(member, target, action)) throw new Error(action.name + " is no longer legal.");
    if (action.resourceId) member.state.resources[action.resourceId] -= (action.resourceCost || 1);
    E().spend(member.state, action.actionCost || "action");
    const applied = T().apply(target.state, action.conditionId, member.combatant_id, {
      sourceEffectId: action.id,
      sourceTemplate: member.state.template,
      sourceIsMagical: action.magicalEffect !== false,
      appliedRound: round,
      repeatSaveAbility: action.repeatSaveAbility,
      repeatSaveDc: action.repeatSaveDc,
      repeatSaveTiming: action.repeatSaveTiming || "target_turn_end",
      useDefaultPoisonRecovery: false,
    });
    if (!applied) throw new Error(action.name + " could not apply " + action.conditionId + ".");
    return {
      sequence, round_number: round, event_type: "feature",
      actor_id: member.combatant_id, actor_name: member.state.template.name,
      target_id: target.combatant_id, target_name: target.state.template.name,
      applied_condition_ids: [applied], feature_id: action.id,
      resource_remaining: action.resourceId ? member.state.resources[action.resourceId] : null,
      animation: action.animation || "condition",
      description: member.state.template.name + " uses " + action.name + " on "
        + target.state.template.name + "; " + target.state.template.name + " is " + action.conditionId + ".",
    };
  }

  window.IRON_PIT_BROWSER_HP_THRESHOLD_CONDITION = { choose, legal, resolve };
})();