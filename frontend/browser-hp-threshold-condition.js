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
    try {
      // Visibility is source data, not a spell-name branch.
      const distance = F().saveDistance(member, target, action.range || 0);
      if (action.requiresTargetSight && !window.IRON_PIT_BROWSER_CONDITION_RULES.canSee(member.state, target.state, distance)) return false;
      if (!E().available(member.state, action.actionCost || "action")) return false;
      if (!target.state.is_alive || target.state.is_dead || target.state.current_hp <= 0) return false;
      if (target.state.current_hp > action.maxCurrentHp) return false;
      if (distance > (action.range || 0)) return false;
      return resourceAvailable(member, action);
    } catch (error) {
      console.error("HP-threshold target legality failed.", member.combatant_id, action.id, error);
      throw error;
    }
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

  function installProvider() {
    const selection = window.IRON_PIT_BROWSER_MAIN_ACTION_SELECTION;
    if (!selection) throw new Error("HP-threshold provider requires main-action selection.");
    const category = selection.CATEGORIES.HP_THRESHOLD_CONDITION;
    selection.registerProvider({
      id: "hp-threshold-condition", category, rulesets: ["2014", "2024"],
      discover: ({ member, setup }) => {
        const selected = choose(member, setup);
        return selected ? { payload: { targetId: selected.target.combatant_id, actionId: selected.action.id } } : null;
      },
      resolve: ({ sequence, round, member, setup }, candidate) => {
        const target = [...setup.heroes, ...setup.monsters]
          .find((item) => item.combatant_id === candidate.payload.targetId) || null;
        const action = (member.state.template.hp_threshold_condition_actions || [])
          .find((item) => item.id === candidate.payload.actionId) || null;
        if (!target || !action) throw new Error("HP-threshold condition candidate became unavailable.");
        return { events: [resolve(sequence, round, member, target, action, setup)], sequence: sequence + 1 };
      },
    });
  }

  window.IRON_PIT_BROWSER_HP_THRESHOLD_CONDITION = { choose, installProvider, legal, resolve };
})();