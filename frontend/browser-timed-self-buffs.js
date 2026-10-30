(() => {
  "use strict";

  const E = () => window.IRON_PIT_ACTION_ECONOMY;
  const T = () => window.IRON_PIT_BROWSER_TIMED;
  const C = () => window.IRON_PIT_BROWSER_CONCENTRATION;

  function active(member, action) {
    return (member.state.timed_effects || []).some((effect) => effect.source_effect_id === action.id);
  }

  function choose(member, actionCost) {
    if (!E().available(member.state, actionCost)) return null;
    const actions = (member.state.template.timed_self_buff_actions || [])
      .filter((action) => (action.actionCost || "action") === actionCost)
      .sort((a, b) => (b.priority || 0) - (a.priority || 0));
    for (const action of actions) {
      if (active(member, action)) continue;
      if (action.concentration && member.state.concentration) continue;
      if (action.resourceId
        && (member.state.resources?.[action.resourceId] || 0) < (action.resourceCost || 1)) continue;
      return action;
    }
    return null;
  }

  function resolve(sequence, round, member, action, setup) {
    const cost = action.actionCost || "action";
    if (!E().available(member.state, cost)) throw new Error(`${cost} is unavailable for ${action.name}.`);
    if (active(member, action)) throw new Error(`${action.name} is already active.`);
    const resourceCost = action.resourceCost || 1;
    if (action.resourceId && (member.state.resources?.[action.resourceId] || 0) < resourceCost) {
      throw new Error(`Resource ${action.resourceId} is unavailable for ${action.name}.`);
    }
    E().spend(member.state, cost);
    if (action.resourceId) member.state.resources[action.resourceId] -= resourceCost;
    const states = [...setup.heroes, ...setup.monsters].map((item) => item.state);
    const expiresRound = action.durationRounds == null ? null : round + action.durationRounds;
    const applied = [];
    for (const conditionId of action.conditionIds || []) {
      const result = T().apply(member.state, conditionId, member.combatant_id, {
        sourceEffectId: action.id,
        appliedRound: round,
        expiresRound,
        expiresAtStartOfSourceTurn: false,
        endsOnOwnerAttack: Boolean(action.endsOnOwnerAttack),
        endsOnOwnerSpellCast: Boolean(action.endsOnOwnerSpellCast),
      });
      if (result) applied.push(result);
    }
    if (action.concentration) C().start(
      member.state, member.combatant_id, action.id, round, states, expiresRound,
    );
    return {
      sequence, round_number: round, event_type: "feature",
      actor_id: member.combatant_id, actor_name: member.state.template.name,
      target_id: member.combatant_id, target_name: member.state.template.name,
      applied_condition_ids: applied, feature_id: action.id,
      resource_remaining: action.resourceId ? member.state.resources[action.resourceId] : null,
      concentration_started_effect_id: action.concentration ? action.id : null,
      animation: action.animation || "buff",
      description: `${member.state.template.name} uses ${action.name}.`,
    };
  }

  window.IRON_PIT_BROWSER_TIMED_SELF_BUFFS = { active, choose, resolve };
})();
