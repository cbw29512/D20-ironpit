(() => {
  "use strict";

  const E = () => window.IRON_PIT_ACTION_ECONOMY;
  const F = () => window.IRON_PIT_BROWSER_FORMATION;
  const Z = () => window.IRON_PIT_BROWSER_ZERO_HP;

  function legal(member, target, action) {
    if (!E().available(member.state, action.actionCost || "action")) return false;
    if (!target.state.is_alive || target.state.is_dead || target.state.current_hp <= 0) return false;
    if (target.state.current_hp > action.maxCurrentHp) return false;
    if (F().saveDistance(member, target, action.range || 0) > (action.range || 0)) return false;
    if (action.resourceId && (member.state.resources?.[action.resourceId] || 0) < (action.resourceCost || 1)) return false;
    return true;
  }

  function choose(member, setup) {
    for (const action of member.state.template.hp_threshold_instant_death_actions || []) {
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
    const hpBefore = target.state.current_hp;
    const states = [...setup.heroes, ...setup.monsters].map((item) => item.state);
    const outcome = Z().applyInstantDeath(target.state, states);
    const prevented = outcome === "zero_hp_replacement";
    const wardLog = window.IRON_PIT_BROWSER_ZERO_HP_REPLACEMENT?.consumeLog(target.state) || "";
    return {
      sequence, round_number: round, event_type: "feature",
      actor_id: member.combatant_id, actor_name: member.state.template.name,
      target_id: target.combatant_id, target_name: target.state.template.name,
      hp_before: hpBefore, hp_after: target.state.current_hp, is_dead: target.state.is_dead,
      feature_id: action.id,
      resource_remaining: action.resourceId ? member.state.resources[action.resourceId] : null,
      animation: action.animation || "instant-death",
      description: member.state.template.name + " uses " + action.name + " on " + target.state.template.name + "; "
        + (prevented ? target.state.template.name + "'s ward negates the instant-death effect." : target.state.template.name + " dies.")
        + wardLog,
    };
  }

  function installProvider() {
    const selection = window.IRON_PIT_BROWSER_MAIN_ACTION_SELECTION;
    if (!selection) throw new Error("HP-threshold instant-death provider requires main-action selection.");
    selection.registerProvider({
      id: "hp-threshold-instant-death",
      category: selection.CATEGORIES.HP_THRESHOLD_INSTANT_DEATH,
      rulesets: ["2014", "2024"],
      discover: ({ member, setup }) => {
        const selected = choose(member, setup);
        return selected ? { payload: { targetId: selected.target.combatant_id, actionId: selected.action.id } } : null;
      },
      resolve: ({ sequence, round, member, setup }, candidate) => {
        const target = [...setup.heroes, ...setup.monsters].find((item) => item.combatant_id === candidate.payload.targetId) || null;
        const action = (member.state.template.hp_threshold_instant_death_actions || [])
          .find((item) => item.id === candidate.payload.actionId) || null;
        if (!target || !action) throw new Error("HP-threshold instant-death candidate became unavailable.");
        return { events: [resolve(sequence, round, member, target, action, setup)], sequence: sequence + 1 };
      },
    });
  }

  window.IRON_PIT_BROWSER_HP_THRESHOLD_INSTANT_DEATH = { choose, installProvider, legal, resolve };
})();