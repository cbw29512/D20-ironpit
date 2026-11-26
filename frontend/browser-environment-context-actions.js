(() => {
  "use strict";

  const E = () => window.IRON_PIT_ACTION_ECONOMY;
  const distance = (source, target) => window.IRON_PIT_BROWSER_STATE.distance(source, target);

  function choose(member, setup) {
    const enemies = member.side === "heroes" ? setup.monsters : setup.heroes;
    for (const action of member.state.template.environment_context_control_actions || []) {
      if (!E().available(member.state, action.action_cost)) continue;
      const current = member.state.environment_context_modes?.[action.id] || action.initial_mode_id;
      if (current === action.ai_mode_id) continue;
      const mode = (action.modes || []).find((item) => item.id === action.ai_mode_id);
      if (!mode) throw new Error(`Missing AI mode ${action.ai_mode_id} for ${action.name}.`);
      const relevant = (mode.emitted_contexts || []).some((emitted) => enemies.some((enemy) =>
        enemy.state.is_alive && !enemy.state.is_dead
        && distance(member, enemy) <= emitted.radius_ft
        && (enemy.state.template.environment_context_reactions || []).some((reaction) =>
          reaction.context_id === emitted.context_id)));
      if (relevant) return { action, mode };
    }
    return null;
  }

  function resolve(sequence, round, member, action, mode, affectedStates = [], setup = null) {
    if (!(action.modes || []).some((item) => item.id === mode.id)) {
      throw new Error(`${mode.id} is not a declared mode for ${action.name}.`);
    }
    if (!E().available(member.state, action.action_cost)) {
      throw new Error(`${action.action_cost} is unavailable for ${action.name}.`);
    }
    const current = member.state.environment_context_modes?.[action.id] || action.initial_mode_id;
    if (current === mode.id) throw new Error(`${action.name} is already in mode ${mode.id}.`);
    E().spend(member.state, action.action_cost);
    window.IRON_PIT_BROWSER_OWNER_ACTION_EXPIRY?.expire?.(
      member.state, "action", affectedStates.length ? affectedStates : [member.state], action.id,
    );
    member.state.environment_context_modes ||= {};
    member.state.environment_context_modes[action.id] = mode.id;
    const expired = setup
      ? window.IRON_PIT_BROWSER_ENVIRONMENT_CONTEXTS?.expireProhibitedBuffs?.(setup) || []
      : [];
    return {
      sequence, round_number: round, event_type: "feature",
      actor_id: member.combatant_id, actor_name: member.state.template.name,
      feature_id: action.name, animation: "buff",
      description: `${member.state.template.name} uses ${action.name} and selects ${mode.id}.`
        + (expired.length ? ` ${expired.join(", ")} ends.` : ""),
    };
  }

  window.IRON_PIT_BROWSER_ENVIRONMENT_CONTEXT_ACTIONS = { choose, resolve };
})();
