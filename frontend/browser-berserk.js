(() => {
  "use strict";
  const D = () => window.IRON_PIT_DICE;

  function active(state) {
    const profile = state.template.berserk;
    return Boolean(profile && state.active_effect_ids.includes(profile.effectId || "berserk"));
  }

  function startTurn(sequence, round, member) {
    const state = member.state, profile = state.template.berserk;
    if (!profile) return null;
    const effectId = profile.effectId || "berserk";
    if (active(state) && state.current_hp >= state.template.max_hp) {
      state.active_effect_ids = state.active_effect_ids.filter((id) => id !== effectId);
      return { sequence: sequence + 1, event: {
        sequence, round_number: round, event_type: "feature", actor_id: member.combatant_id,
        actor_name: state.template.name, feature_id: effectId, removed_condition_ids: [effectId],
        animation: "feature", description: `${state.template.name} is no longer berserk after regaining all its hit points.`,
      } };
    }
    if (active(state) || state.current_hp > profile.hpThreshold) return null;
    const roll = D().roll(profile.dieSize), triggered = roll === profile.triggerRoll;
    if (triggered) state.active_effect_ids.push(effectId);
    return { sequence: sequence + 1, event: {
      sequence, round_number: round, event_type: "feature", actor_id: member.combatant_id,
      actor_name: state.template.name, feature_id: triggered ? effectId : "berserk-check",
      resource_roll: { notation: `1d${profile.dieSize}`, rolls: [roll], selected_roll: roll, modifier: 0, mode: "normal", total: roll },
      applied_condition_ids: triggered ? [effectId] : [], animation: "feature",
      description: triggered
        ? `${state.template.name} rolls ${roll} on d${profile.dieSize} for Berserk and goes berserk.`
        : `${state.template.name} rolls ${roll} on d${profile.dieSize} for Berserk and remains controlled.`,
    } };
  }

  window.IRON_PIT_BROWSER_BERSERK = { active, startTurn };
})();
